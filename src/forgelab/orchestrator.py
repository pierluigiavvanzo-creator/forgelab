from __future__ import annotations

import json
import os
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .artifacts import ArtifactStore
from .domain import AgentResult, AgentTask, ResourceLimits, ResultStatus, Role, RunStatus, Scope
from .quality import review_patch, security_review_patch
from .state_machine import RunStateMachine
from .workspace import IsolatedWorkspace
from .model_router import ModelRouter, TaskClass, UsageLedger, load_routes
from .ollama_provider import OllamaProvider
from .memory import ProjectMemory
from .governance import PolicyEngine, ToolGateway


@dataclass(frozen=True)
class MultiAgentRequest:
    repository: Path
    objective: str
    target_path: str
    old_text: str
    new_text: str
    test_command: list[str]
    timeout_seconds: int = 60
    initial_new_text: str | None = None
    risk: str = "normal"
    max_repair_attempts: int = 1
    ai_mode: bool = False
    operation: str = "replace_text"
    allowed_paths: tuple[str, ...] = ()

    @property
    def target_paths(self) -> tuple[str, ...]:
        return self.allowed_paths or (self.target_path,)

    @classmethod
    def from_json(cls, path: Path) -> "MultiAgentRequest":
        payload = json.loads(
            path.read_text(encoding="utf-8-sig")
        )

        change = payload["change"]
        operation = change.get(
            "operation",
            "replace_text",
        )

        if operation not in {
            "replace_text",
            "ai_generate",
        }:
            raise ValueError(
                "change.operation must be "
                "replace_text or ai_generate"
            )

        attempts = int(
            payload.get(
                "max_repair_attempts",
                1,
            )
        )

        if attempts < 0 or attempts > 3:
            raise ValueError(
                "max_repair_attempts must be "
                "between 0 and 3"
            )

        ai_mode = payload.get(
            "ai_mode",
            False,
        )

        if not isinstance(ai_mode, bool):
            raise ValueError(
                "ai_mode must be boolean"
            )

        if operation == "replace_text":
            target_path = change["path"]
            allowed_paths = (target_path,)
            old_text = change["old"]
            new_text = change["new"]
            initial_new = change.get(
                "initial_new"
            )
        else:
            if "paths" in change:
                raw_paths = change["paths"]

                if (
                    not isinstance(raw_paths, list)
                    or not 1 <= len(raw_paths) <= 3
                    or not all(
                        isinstance(item, str)
                        and item.strip()
                        for item in raw_paths
                    )
                ):
                    raise ValueError(
                        "ai_generate paths must contain "
                        "1 to 3 non-empty strings"
                    )

                allowed_paths = tuple(
                    item.strip()
                    for item in raw_paths
                )

                if len(set(allowed_paths)) != len(allowed_paths):
                    raise ValueError(
                        "ai_generate paths must be unique"
                    )

                target_path = allowed_paths[0]
            else:
                target_path = change["path"]
                allowed_paths = (target_path,)

            old_text = ""
            new_text = ""
            initial_new = None

            # ai_generate itself is explicit
            # authorization to use local AI.
            ai_mode = True

        return cls(
            repository=Path(
                payload["repository"]
            ),
            objective=payload["objective"],
            target_path=target_path,
            old_text=old_text,
            new_text=new_text,
            initial_new_text=initial_new,
            test_command=list(
                payload["test_command"]
            ),
            timeout_seconds=int(
                payload.get(
                    "timeout_seconds",
                    60,
                )
            ),
            risk=payload.get(
                "risk",
                "normal",
            ),
            max_repair_attempts=attempts,
            ai_mode=ai_mode,
            operation=operation,
            allowed_paths=allowed_paths,
        )



def _build_local_ai_router() -> tuple[ModelRouter, UsageLedger]:
    configured = os.environ.get(
        "FORGELAB_ROUTING_CONFIG"
    )

    routing_path = (
        Path(configured)
        if configured
        else Path.cwd() / ".forgelab" / "routing.yaml"
    )

    if not routing_path.is_file():
        raise FileNotFoundError(
            f"ForgeLab routing config not found: {routing_path}"
        )

    endpoint = os.environ.get(
        "FORGELAB_OLLAMA_URL",
        "http://127.0.0.1:11434",
    )

    routes = load_routes(routing_path)

    # Hard zero-spend budget for the local provider.
    ledger = UsageLedger(
        Decimal("0")
    )

    router = ModelRouter(
        routes,
        {
            "ollama": OllamaProvider(
                endpoint
            ),
        },
        ledger,
    )

    return router, ledger


def _read_ai_developer_target(
    workspace: Path,
    relative_path: str,
) -> str:

    relative = Path(relative_path)

    if (
        relative.is_absolute()
        or ".." in relative.parts
        or ".git" in relative.parts
    ):
        raise ValueError(
            "AI Developer target path "
            "escapes authorized workspace scope"
        )

    root = workspace.resolve()
    target = (root / relative).resolve()

    try:
        target.relative_to(root)
    except ValueError as error:
        raise ValueError(
            "AI Developer target path "
            "escapes workspace"
        ) from error

    if not target.is_file():
        raise ValueError(
            "AI Developer target file "
            "does not exist"
        )

    source = target.read_text(
        encoding="utf-8"
    )

    if len(source) > 12_000:
        raise ValueError(
            "AI Developer target exceeds "
            "12000 character per-file context cap"
        )

    return source


def _read_ai_developer_targets(
    workspace: Path,
    relative_paths: tuple[str, ...],
) -> dict[str, str]:

    if not 1 <= len(relative_paths) <= 3:
        raise ValueError(
            "AI Developer requires 1 to 3 "
            "authorized target paths"
        )

    if len(set(relative_paths)) != len(relative_paths):
        raise ValueError(
            "AI Developer target paths must be unique"
        )

    sources = {
        path: _read_ai_developer_target(
            workspace,
            path,
        )
        for path in relative_paths
    }

    if sum(len(value) for value in sources.values()) > 24_000:
        raise ValueError(
            "AI Developer authorized file context "
            "exceeds 24000 character total cap"
        )

    return sources



def _extract_ai_developer_json(
    text: str,
) -> dict[str, Any]:

    candidate = text.strip()

    if candidate.startswith("```"):
        lines = candidate.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        candidate = "\n".join(
            lines
        ).strip()

    try:
        payload = json.loads(candidate)

        if isinstance(payload, dict):
            return payload

    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()

    for index, char in enumerate(candidate):

        if char != "{":
            continue

        try:
            payload, _ = decoder.raw_decode(
                candidate[index:]
            )
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict):
            return payload

    raise ValueError(
        "AI Developer did not return "
        "a valid JSON object"
    )


def _validate_ai_developer_change(
    payload: dict[str, Any],
    expected_paths: tuple[str, ...],
    source_texts: dict[str, str],
) -> dict[str, str]:

    required = {
        "path",
        "old_text",
        "new_text",
        "summary",
    }

    missing = required - set(payload)

    if missing:
        raise ValueError(
            "AI Developer change missing fields: "
            + ", ".join(sorted(missing))
        )

    path = payload["path"]

    if path not in expected_paths:
        raise ValueError(
            "AI Developer attempted "
            "path expansion"
        )

    old_text = payload["old_text"]
    new_text = payload["new_text"]
    summary = payload["summary"]

    if (
        not isinstance(old_text, str)
        or not old_text
    ):
        raise ValueError(
            "AI Developer old_text must "
            "be non-empty"
        )

    if not isinstance(new_text, str):
        raise ValueError(
            "AI Developer new_text must "
            "be a string"
        )

    if (
        not isinstance(summary, str)
        or not summary.strip()
    ):
        raise ValueError(
            "AI Developer summary must "
            "be non-empty"
        )

    if (
        len(old_text) > 100_000
        or len(new_text) > 100_000
    ):
        raise ValueError(
            "AI Developer replacement "
            "exceeds size limit"
        )

    if old_text == new_text:
        raise ValueError(
            "AI Developer proposed "
            "a no-op replacement"
        )

    match_count = source_texts[path].count(
        old_text
    )

    if match_count != 1:
        raise ValueError(
            "AI Developer old_text must occur "
            f"exactly once in {path}; found {match_count}"
        )

    return {
        "path": path,
        "old_text": old_text,
        "new_text": new_text,
        "summary": summary.strip(),
    }


def _validate_ai_developer_patch(
    response_text: str,
    expected_paths: tuple[str, ...],
    source_texts: dict[str, str],
    *,
    require_all_paths: bool = True,
) -> dict[str, Any]:

    payload = _extract_ai_developer_json(
        response_text
    )

    if len(expected_paths) == 1:
        required = {
            "schema_version",
            "path",
            "old_text",
            "new_text",
            "summary",
        }

        missing = required - set(payload)

        if missing:
            raise ValueError(
                "AI Developer patch missing fields: "
                + ", ".join(sorted(missing))
            )

        if payload["schema_version"] != "1.0":
            raise ValueError(
                "AI Developer single-file schema_version "
                "must be 1.0"
            )

        change = _validate_ai_developer_change(
            payload,
            expected_paths,
            source_texts,
        )

        return {
            "schema_version": "1.0",
            **change,
        }

    required = {
        "schema_version",
        "changes",
        "summary",
    }

    missing = required - set(payload)

    if missing:
        raise ValueError(
            "AI Developer multi-file patch missing fields: "
            + ", ".join(sorted(missing))
        )

    if payload["schema_version"] != "2.0":
        raise ValueError(
            "AI Developer multi-file schema_version "
            "must be 2.0"
        )

    raw_changes = payload["changes"]
    summary = payload["summary"]

    if (
        not isinstance(raw_changes, list)
        or not all(
            isinstance(item, dict)
            for item in raw_changes
        )
    ):
        raise ValueError(
            "AI Developer multi-file changes must be "
            "a structured change list"
        )

    if require_all_paths:
        if len(raw_changes) != len(expected_paths):
            raise ValueError(
                "AI Developer multi-file changes must contain "
                "exactly one structured change per authorized path"
            )
    elif not 1 <= len(raw_changes) <= len(expected_paths):
        raise ValueError(
            "AI Developer repair must change one or more "
            "already-authorized paths"
        )

    if (
        not isinstance(summary, str)
        or not summary.strip()
    ):
        raise ValueError(
            "AI Developer multi-file summary "
            "must be non-empty"
        )

    validated = [
        _validate_ai_developer_change(
            item,
            expected_paths,
            source_texts,
        )
        for item in raw_changes
    ]

    changed_paths = [
        item["path"]
        for item in validated
    ]

    if len(set(changed_paths)) != len(changed_paths):
        raise ValueError(
            "AI Developer multi-file patch "
            "contains duplicate paths"
        )

    if (
        require_all_paths
        and set(changed_paths) != set(expected_paths)
    ):
        raise ValueError(
            "AI Developer multi-file patch must "
            "change every authorized path exactly once"
        )

    by_path = {
        item["path"]: item
        for item in validated
    }

    return {
        "schema_version": "2.0",
        "summary": summary.strip(),
        "changes": [
            by_path[path]
            for path in expected_paths
            if path in by_path
        ],
    }


def _ai_patch_changes(
    payload: dict[str, Any],
) -> list[dict[str, str]]:

    if payload.get("schema_version") == "2.0":
        return list(payload["changes"])

    return [{
        "path": payload["path"],
        "old_text": payload["old_text"],
        "new_text": payload["new_text"],
        "summary": payload["summary"],
    }]


class TaskGraphError(ValueError):
    pass


def validate_task_graph(tasks: list[dict[str, Any]]) -> None:
    ids = [task["task_id"] for task in tasks]
    if len(ids) != len(set(ids)):
        raise TaskGraphError("task ids must be unique")
    known = set(ids)
    dependencies = {task["task_id"]: set(task.get("dependencies", [])) for task in tasks}
    missing = {dep for values in dependencies.values() for dep in values if dep not in known}
    if missing:
        raise TaskGraphError(f"unknown task dependencies: {sorted(missing)}")
    remaining = {task_id: set(values) for task_id, values in dependencies.items()}
    resolved: set[str] = set()
    while remaining:
        ready = {task_id for task_id, values in remaining.items() if values <= resolved}
        if not ready:
            raise TaskGraphError("task graph contains a cycle")
        resolved |= ready
        for task_id in ready:
            del remaining[task_id]


def select_roles(request: MultiAgentRequest) -> list[Role]:
    roles = [Role.PROJECT_MANAGER, Role.DEVELOPER, Role.TESTER, Role.REVIEWER]
    sensitive = ("auth", "security", "secret", "payment", "permission")
    lowered_paths = [
        path.lower()
        for path in request.target_paths
    ]

    if (
        request.risk == "high"
        or any(
            term in path
            for path in lowered_paths
            for term in sensitive
        )
    ):
        roles.append(Role.SECURITY)

    if any(
        path.endswith((".md", ".rst", ".txt"))
        for path in lowered_paths
    ):
        roles.append(Role.DOCUMENTATION)

    return roles


def _task(
    run_id: str,
    task_id: str,
    role: Role,
    objective: str,
    paths: str | tuple[str, ...] | list[str],
    tools: list[str],
    dependencies: list[str],
) -> dict[str, Any]:
    allowed_paths = (
        [paths]
        if isinstance(paths, str)
        else list(paths)
    )

    inputs: dict[str, Any] = {"dependencies": dependencies}
    if role in {Role.PROJECT_MANAGER, Role.DEVELOPER, Role.SUPPORT}:
        inputs["relevant_context"] = {
            "artifact_ref": "ContextBundle.json",
            "mode": "read_only",
            "write_scope_expansion": False,
        }

    contract = AgentTask(
        task_id=task_id,
        run_id=run_id,
        role=role,
        objective=objective,
        scope=Scope(allowed_paths, [".git", "main"]),
        inputs=inputs,
        acceptance_criteria=[
            "Return structured result with evidence"
        ],
        allowed_tools=tools,
        resource_limits=ResourceLimits(20, 120, 0.0),
        escalation_conditions=[
            "Scope expansion",
            "Repeated failure",
            "Gate required",
        ],
    )
    payload = contract.to_dict()
    payload["dependencies"] = dependencies
    return payload


def _result(store: ArtifactStore, task_id: str, status: ResultStatus, summary: str,
            evidence: list[str], next_action: str, findings: list[dict[str, Any]] | None = None,
            changed: list[str] | None = None) -> dict[str, Any]:
    result = AgentResult(status, summary, changed or [], evidence, findings or [], [], next_action).to_dict()
    store.write_task_result(task_id, result)
    return result


def _render_governed_context(context_bundle: dict[str, object]) -> str:
    documents = context_bundle.get("documents", [])
    sections = [
        "Context contract: READ-ONLY. Context paths never expand authorized write scope."
    ]
    if isinstance(documents, list):
        for item in documents:
            if not isinstance(item, dict):
                continue
            path = item.get("path", "")
            source = item.get("source", "")
            sha256 = item.get("sha256", "")
            content = item.get("content", "")
            sections.append(
                f"--- BEGIN READ-ONLY CONTEXT {path} [{source}] sha256={sha256} ---\n"
                f"{content}\n"
                f"--- END READ-ONLY CONTEXT {path} ---"
            )
    return "\n\n".join(sections)


def run_multi_agent(request: MultiAgentRequest, output_root: Path) -> Path:
    run_id = f"run-{uuid4().hex[:12]}"
    run_dir = output_root.resolve() / run_id
    store = ArtifactStore(run_dir)
    machine = RunStateMachine()
    roles = select_roles(request)
    target_paths = request.target_paths
    project_memory = ProjectMemory(request.repository)
    memory_snapshot = project_memory.snapshot()
    context_bundle = project_memory.select(
        request.objective,
        max_chars=16_000,
        max_repository_files=8,
        max_repository_file_chars=12_000,
        max_repository_candidates=2_000,
        exclude_paths=target_paths,
    )
    governed_context = _render_governed_context(context_bundle)
    store.write_optional_json("MemorySnapshot.json", memory_snapshot)
    store.write_optional_json("ContextBundle.json", context_bundle)
    if request.operation not in {
        "replace_text",
        "ai_generate",
    }:
        raise ValueError(
            "unsupported change operation"
        )

    if (
        request.operation == "replace_text"
        and not request.old_text
    ):
        raise ValueError(
            "replace_text requires old_text"
        )

    if (
        request.operation == "ai_generate"
        and request.initial_new_text is not None
    ):
        raise ValueError(
            "ai_generate does not accept "
            "initial_new_text"
        )

    if (
        request.operation == "replace_text"
        and target_paths != (request.target_path,)
    ):
        raise ValueError(
            "replace_text supports exactly one target path"
        )

    if (
        request.operation == "ai_generate"
        and not 1 <= len(target_paths) <= 3
    ):
        raise ValueError(
            "ai_generate supports 1 to 3 "
            "authorized target paths"
        )

    if len(set(target_paths)) != len(target_paths):
        raise ValueError(
            "authorized target paths must be unique"
        )

    if request.target_path != target_paths[0]:
        raise ValueError(
            "target_path must equal the first "
            "authorized target path"
        )

    use_ai = (
        request.ai_mode
        or request.operation == "ai_generate"
    )

    ai_router: ModelRouter | None = None
    ai_ledger = UsageLedger(Decimal("0"))

    if use_ai:
        ai_router, ai_ledger = _build_local_ai_router()

        plan_targets = "\n".join(
            f"- {path}"
            for path in target_paths
        )

        plan_prompt = f"""
You are the PROJECT_MANAGER agent in ForgeLab.

Create a concise bounded implementation plan.

Objective:
{request.objective}

Authorized target paths:
{plan_targets}

Governed read-only project/repository context:
{governed_context}

Return:
1. intended outcome
2. execution steps
3. acceptance criteria
4. principal risks

Do not claim that tools or tests have already run.
"""

        plan_response = ai_router.execute(
            TaskClass.S1,
            plan_prompt,
            "plan",
            Role.PROJECT_MANAGER.value,
            "AI-assisted bounded planning",
            request.timeout_seconds,
        )

        plan_route = ai_router.route(
            TaskClass.S1
        )

        store.write_optional_json(
            "AIPlan.json",
            {
                "role": Role.PROJECT_MANAGER.value,
                "provider": plan_route.provider,
                "model": plan_route.model,
                "text": plan_response.text,
                "context_bundle_ref": "ContextBundle.json",
                "context_selection_sha256": context_bundle["selection_sha256"],
            },
        )
    policy_dir = request.repository / ".forgelab"
    if (policy_dir / "agents.yaml").is_file() and (policy_dir / "policy.yaml").is_file():
        policy_engine = PolicyEngine.from_directory(policy_dir)
    else:
        policy_engine = PolicyEngine()
    gateway = ToolGateway(policy_engine)
    task_defs = [
        _task(run_id, "plan", Role.PROJECT_MANAGER, "Create bounded execution plan", target_paths, ["repo_read"], []),
        _task(run_id, "implement", Role.DEVELOPER, request.objective, target_paths, ["repo_edit"], ["plan"]),
        _task(run_id, "test", Role.TESTER, "Run acceptance tests", target_paths, ["test_runner"], ["implement"]),
        _task(run_id, "review", Role.REVIEWER, "Review scope and correctness", target_paths, ["git_diff"], ["test"]),
    ]
    if Role.SECURITY in roles:
        task_defs.append(_task(run_id, "security", Role.SECURITY, "Review security risk", target_paths, ["policy_check"], ["review"]))
    if Role.DOCUMENTATION in roles:
        task_defs.append(_task(run_id, "documentation", Role.DOCUMENTATION, "Confirm documentation consistency", target_paths, ["docs_read"], ["review"]))
    validate_task_graph(task_defs)

    store.write("ExecutionPlan.json", {
        "run_id": run_id, "objective": request.objective, "repository": str(request.repository.resolve()),
        "tasks": task_defs, "selected_roles": [role.value for role in roles],
        "selection_reason": "Minimum roles for plan, implementation, test, and independent review; conditional roles by risk and path",
        "max_repair_attempts": request.max_repair_attempts, "test_command": request.test_command,
        "change_operation": request.operation,
        "allowed_paths": list(target_paths),
        "timeout_seconds": request.timeout_seconds, "requires_human_gate": True,
        "memory_snapshot_ref": "MemorySnapshot.json", "context_bundle_ref": "ContextBundle.json",
        "memory_manifest_sha256": memory_snapshot["manifest_sha256"],
        "context_selection": {
            "mode": context_bundle["mode"],
            "write_scope_expansion": context_bundle["write_scope_expansion"],
            "selection_sha256": context_bundle["selection_sha256"],
            "selected_paths": context_bundle["selected_paths"],
            "used_chars": context_bundle["used_chars"],
        },
    })
    machine.transition(RunStatus.PRECHECK)
    machine.transition(RunStatus.PLANNED)
    _result(store, "plan", ResultStatus.PASS, "Bounded plan created", ["ExecutionPlan.json"], "Create isolated workspace")
    machine.transition(RunStatus.ISOLATED)
    workspace = IsolatedWorkspace(request.repository, run_id)
    evidence: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    diff = ""
    repair_attempts = 0
    diagnostic_history: list[dict[str, Any]] = []
    seen_hypotheses: set[str] = set()
    seen_repair_payloads: set[str] = set()
    ai_developer_artifact: dict[str, Any] | None = None
    source_unchanged = False
    final_test_passed = False
    review_report: dict[str, Any] = {"status": "FAIL", "findings": []}
    security_report: dict[str, Any] = {"status": "PASS", "findings": []}
    try:
        workspace.create()
        machine.transition(RunStatus.IMPLEMENTING)

        if request.operation == "ai_generate":

            if ai_router is None:
                raise ValueError(
                    "AI Developer requires "
                    "local AI router"
                )

            source_texts = (
                _read_ai_developer_targets(
                    workspace.path,  # type: ignore[arg-type]
                    target_paths,
                )
            )

            files_context = "\n\n".join(
                (
                    f"--- BEGIN FILE {path} ---\n"
                    f"{source_texts[path]}\n"
                    f"--- END FILE {path} ---"
                )
                for path in target_paths
            )

            authorized_list = "\n".join(
                f"- {path}"
                for path in target_paths
            )

            if len(target_paths) == 1:
                schema_instructions = f"""
{{
  "schema_version": "1.0",
  "path": "{target_paths[0]}",
  "old_text": "<exact existing contiguous text>",
  "new_text": "<replacement text>",
  "summary": "<short implementation summary>"
}}
"""
            else:
                change_examples = ",\n".join(
                    (
                        "    {\n"
                        f'      "path": "{path}",\n'
                        '      "old_text": "<exact existing contiguous text>",\n'
                        '      "new_text": "<replacement text>",\n'
                        '      "summary": "<short per-file summary>"\n'
                        "    }"
                    )
                    for path in target_paths
                )

                schema_instructions = (
                    "{\n"
                    '  "schema_version": "2.0",\n'
                    '  "summary": "<short overall implementation summary>",\n'
                    '  "changes": [\n'
                    f"{change_examples}\n"
                    "  ]\n"
                    "}"
                )

            developer_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

Your task is to propose the smallest correct bounded
replacement set needed to satisfy the objective.

Objective:
{request.objective}

Authorized target paths:
{authorized_list}

Governed read-only repository context (does NOT expand write scope):
{governed_context}

Current complete authorized files:
{files_context}

Return ONLY one JSON object.
No Markdown. No prose outside JSON.

Required schema:
{schema_instructions}

Rules:
- every path MUST be one of the authorized target paths.
- when more than one path is authorized, return exactly one change for each path.
- old_text MUST occur exactly once in its corresponding file.
- choose the smallest sufficient replacement for each file.
- do not modify any other file.
- do not claim tests have run.
- do not create dependencies.
"""

            developer_response = (
                ai_router.execute(
                    TaskClass.S2,
                    developer_prompt,
                    "implement",
                    Role.DEVELOPER.value,
                    (
                        "Generate bounded multi-file patch"
                        if len(target_paths) > 1
                        else "Generate bounded single-file patch"
                    ),
                    request.timeout_seconds,
                )
            )

            developer_route = ai_router.route(
                TaskClass.S2
            )

            generated_patch = (
                _validate_ai_developer_patch(
                    developer_response.text,
                    target_paths,
                    source_texts,
                )
            )

            generated_changes = (
                _ai_patch_changes(
                    generated_patch
                )
            )

            ai_developer_artifact = {
                "role":
                    Role.DEVELOPER.value,
                "provider":
                    developer_route.provider,
                "model":
                    developer_route.model,
                **generated_patch,
                "validated_match_count":
                    len(generated_changes),
                "validated_change_count":
                    len(generated_changes),
                "applied_by":
                    "deterministic_tool_gateway",
                "repair_attempts": [],
                "context_bundle_ref": "ContextBundle.json",
                "context_selection_sha256": context_bundle["selection_sha256"],
            }

            store.write_optional_json(
                "AIDeveloperPatch.json",
                ai_developer_artifact,
            )

            implementation_changes = [
                (
                    item["path"],
                    item["old_text"],
                    item["new_text"],
                )
                for item in generated_changes
            ]

            first_value = None
            final_value = None

            implementation_tool = (
                "ai_generate+replace_text"
            )

            implementation_summary = (
                "AI Developer generated a bounded "
                f"{len(implementation_changes)}-file change set; "
                "deterministic ToolGateway applied it "
                "in isolated workspace"
            )

        else:

            first_value = (
                request.initial_new_text
                if request.initial_new_text
                is not None
                else request.new_text
            )

            final_value = request.new_text

            implementation_changes = [(
                request.target_path,
                request.old_text,
                first_value,
            )]

            implementation_tool = (
                "replace_text"
            )

            implementation_summary = (
                "Change implemented in "
                "isolated workspace"
            )

        authorized_paths = set(target_paths)

        for (
            implementation_path,
            implementation_old,
            implementation_new,
        ) in implementation_changes:
            gateway.edit_text(
                Role.DEVELOPER,
                workspace.path,  # type: ignore[arg-type]
                authorized_paths,
                implementation_path,
                implementation_old,
                implementation_new,
            )

        evidence.append({
            "evidence_id":
                "ev-implementation",
            "check_type":
                "workspace_change",
            "command_or_tool":
                implementation_tool,
            "exit_status":
                0,
            "summary":
                "Changed authorized path set "
                f"{list(target_paths)} inside isolated workspace",
            "artifact_ref":
                (
                    "AIDeveloperPatch.json"
                    if request.operation
                    == "ai_generate"
                    else None
                ),
        })

        results.append(
            _result(
                store,
                "implement",
                ResultStatus.PASS,
                implementation_summary,
                ["ev-implementation"],
                "Run tests",
                changed=list(target_paths),
            )
        )
        machine.transition(RunStatus.TESTING)
        while True:
            test = gateway.run_test(Role.TESTER, workspace.path, request.test_command, request.timeout_seconds)  # type: ignore[arg-type]
            ev_id = f"ev-test-{repair_attempts}"
            evidence.append({
                "evidence_id": ev_id, "check_type": "tests", "command_or_tool": request.test_command,
                "exit_status": test.exit_status, "summary": "Tests passed" if test.exit_status == 0 else "Tests failed",
                "stdout": test.stdout[-4000:], "stderr": test.stderr[-4000:], "repair_attempt": repair_attempts,
            })
            if test.exit_status == 0:
                final_test_passed = True
                results.append(_result(store, "test", ResultStatus.PASS, "Acceptance tests passed", [ev_id], "Review patch"))
                break
            repair_available = (
                request.operation == "ai_generate"
                or request.initial_new_text is not None
            )

            if (
                repair_attempts >= request.max_repair_attempts
                or not repair_available
            ):
                results.append(_result(store, "test", ResultStatus.FAIL, "Tests failed and repair budget exhausted", [ev_id], "Human repair required"))
                machine.transition(RunStatus.DIAGNOSING)
                break

            machine.transition(RunStatus.DIAGNOSING)

            support_id = f"support-{repair_attempts + 1}"

            if ai_router is not None:
                diagnostic_prompt = f"""
You are the SUPPORT agent in ForgeLab.

A bounded software change failed its acceptance test.

Objective:
{request.objective}

Authorized targets:
{chr(10).join(f"- {path}" for path in target_paths)}

Failed deterministic evidence id:
{ev_id}

Test stdout:
{test.stdout[-2500:]}

Test stderr:
{test.stderr[-2500:]}

Governed read-only repository context (same contract used by Developer):
{governed_context}

Produce a NEW evidence-backed failure hypothesis for this
specific failed test and the smallest repair strategy.
Do not repeat a prior hypothesis. Do not invent test results.
"""

                diagnostic_response = ai_router.execute(
                    TaskClass.S2,
                    diagnostic_prompt,
                    support_id,
                    Role.SUPPORT.value,
                    "Diagnose failed acceptance test",
                    request.timeout_seconds,
                )

                hypothesis = (
                    diagnostic_response.text.strip()
                    or "Acceptance test failed"
                )
            else:
                hypothesis = "The initial candidate replacement does not satisfy the acceptance tests"

            normalized_hypothesis = " ".join(
                hypothesis.split()
            ).casefold()

            task_defs.append(_task(run_id, support_id, Role.SUPPORT, "Diagnose failed acceptance test", target_paths, ["logs_read"], ["test"]))
            validate_task_graph(task_defs)

            diagnostic_entry = {
                "attempt": repair_attempts + 1,
                "test_evidence_ref": ev_id,
                "hypothesis": hypothesis,
            }
            diagnostic_history.append(diagnostic_entry)

            store.write_optional_json(
                "AIDiagnostics.json",
                {
                    "role": Role.SUPPORT.value,
                    "text": hypothesis,
                    "attempts": diagnostic_history,
                    "context_bundle_ref": "ContextBundle.json",
                    "context_selection_sha256": context_bundle["selection_sha256"],
                },
            )

            if normalized_hypothesis in seen_hypotheses:
                _result(
                    store,
                    support_id,
                    ResultStatus.FAIL,
                    "Repeated diagnostic hypothesis rejected; new evidence-backed hypothesis required",
                    [ev_id],
                    "Human repair required",
                )
                break

            seen_hypotheses.add(
                normalized_hypothesis
            )

            _result(store, support_id, ResultStatus.PASS, hypothesis, [ev_id], "Generate bounded repair candidate")
            machine.transition(RunStatus.REPAIRING)

            if request.operation == "ai_generate":
                if ai_router is None:
                    raise ValueError(
                        "AI Developer repair requires "
                        "local AI router"
                    )

                repair_source_texts = (
                    _read_ai_developer_targets(
                        workspace.path,  # type: ignore[arg-type]
                        target_paths,
                    )
                )

                repair_files_context = "\n\n".join(
                    (
                        f"--- BEGIN FILE {path} ---\n"
                        f"{repair_source_texts[path]}\n"
                        f"--- END FILE {path} ---"
                    )
                    for path in target_paths
                )

                repair_authorized_list = "\n".join(
                    f"- {path}"
                    for path in target_paths
                )

                if len(target_paths) == 1:
                    repair_schema = f"""
{{
  "schema_version": "1.0",
  "path": "{target_paths[0]}",
  "old_text": "<exact existing contiguous text>",
  "new_text": "<replacement text>",
  "summary": "<short repair summary>"
}}
"""
                else:
                    repair_schema = """
{
  "schema_version": "2.0",
  "summary": "<short overall repair summary>",
  "changes": [
    {
      "path": "<one of the already-authorized paths>",
      "old_text": "<exact existing contiguous text>",
      "new_text": "<replacement text>",
      "summary": "<short per-file repair summary>"
    }
  ]
}
"""

                repair_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

A prior bounded AI patch failed a deterministic test.
Generate the smallest repair justified by the Support
hypothesis and failed-test evidence.

Objective:
{request.objective}

Original authorized paths (scope is immutable):
{repair_authorized_list}

Support hypothesis for {ev_id}:
{hypothesis}

Failed test stdout:
{test.stdout[-2500:]}

Failed test stderr:
{test.stderr[-2500:]}

Governed read-only repository context (same contract used by Support):
{governed_context}

Current complete authorized files AFTER the failed candidate:
{repair_files_context}

Return ONLY one JSON object.
No Markdown. No prose outside JSON.

Required schema:
{repair_schema}

Rules:
- every path MUST remain inside the ORIGINAL authorized path set.
- do not add, infer, or request any new path.
- for multi-file scope, repair only the non-empty subset actually needed.
- old_text MUST occur exactly once in the current corresponding file.
- choose the smallest sufficient repair.
- do not modify any other file.
- do not claim tests have run.
- do not create dependencies.
"""

                repair_id = f"repair-{repair_attempts + 1}"
                repair_response = ai_router.execute(
                    TaskClass.S2,
                    repair_prompt,
                    repair_id,
                    Role.DEVELOPER.value,
                    "Generate bounded AI repair",
                    request.timeout_seconds,
                )

                repair_route = ai_router.route(
                    TaskClass.S2
                )

                repair_patch = (
                    _validate_ai_developer_patch(
                        repair_response.text,
                        target_paths,
                        repair_source_texts,
                        require_all_paths=False,
                    )
                )

                repair_payload_key = json.dumps(
                    repair_patch,
                    sort_keys=True,
                    ensure_ascii=False,
                )

                if repair_payload_key in seen_repair_payloads:
                    raise ValueError(
                        "AI Developer repeated an identical "
                        "repair payload without new evidence"
                    )

                seen_repair_payloads.add(
                    repair_payload_key
                )

                repair_changes = _ai_patch_changes(
                    repair_patch
                )

                repair_changed_paths = [
                    item["path"]
                    for item in repair_changes
                ]

                task_defs.append(_task(run_id, repair_id, Role.DEVELOPER, "Apply bounded AI repair", target_paths, ["repo_edit"], [support_id]))
                validate_task_graph(task_defs)

                for repair_change in repair_changes:
                    gateway.edit_text(
                        Role.DEVELOPER,
                        workspace.path,  # type: ignore[arg-type]
                        authorized_paths,
                        repair_change["path"],
                        repair_change["old_text"],
                        repair_change["new_text"],
                    )

                _result(
                    store,
                    repair_id,
                    ResultStatus.PASS,
                    "Bounded AI repair applied through deterministic ToolGateway",
                    [ev_id],
                    "Rerun deterministic tests",
                    changed=repair_changed_paths,
                )

                if ai_developer_artifact is None:
                    raise RuntimeError(
                        "AI Developer artifact missing before repair"
                    )

                ai_developer_artifact[
                    "repair_attempts"
                ].append({
                    "attempt": repair_attempts + 1,
                    "test_evidence_ref": ev_id,
                    "support_task_id": support_id,
                    "developer_task_id": repair_id,
                    "provider": repair_route.provider,
                    "model": repair_route.model,
                    "changed_paths": repair_changed_paths,
                    "patch": repair_patch,
                    "applied_by": "deterministic_tool_gateway",
                })

                store.write_optional_json(
                    "AIDeveloperPatch.json",
                    ai_developer_artifact,
                )
            else:
                gateway.edit_text(Role.DEVELOPER, workspace.path, set(target_paths), request.target_path, first_value, final_value)  # type: ignore[arg-type]

            repair_attempts += 1
            machine.transition(RunStatus.TESTING)

        if final_test_passed:
            machine.transition(RunStatus.SMOKE_TEST)
            diff = workspace.diff()
            store.write_text("Changes.patch", diff)
            evidence.append({"evidence_id": "ev-diff", "check_type": "scope", "command_or_tool": "git diff", "exit_status": 0, "summary": "Patch captured", "artifact_ref": "Changes.patch"})
            machine.transition(RunStatus.REVIEW)
            review_report = review_patch(diff, set(target_paths))

            if ai_router is not None:
                review_prompt = f"""
You are the REVIEWER agent in ForgeLab.

Review this already-generated patch semantically.

Objective:
{request.objective}

Allowed targets:
{chr(10).join(f"- {path}" for path in target_paths)}

Patch:
{diff[-8000:]}

The deterministic test and policy engines remain authoritative.
Identify inconsistencies, missing acceptance concerns, or
unexpected semantic risk. Do not approve promotion.
"""

                ai_review = ai_router.execute(
                    TaskClass.S1,
                    review_prompt,
                    "review",
                    Role.REVIEWER.value,
                    "Independent AI semantic review",
                    request.timeout_seconds,
                )

                review_route = ai_router.route(
                    TaskClass.S1
                )

                store.write_optional_json(
                    "AIReview.json",
                    {
                        "role": Role.REVIEWER.value,
                        "provider": review_route.provider,
                        "model": review_route.model,
                        "text": ai_review.text,
                    },
                )

            reviewer_status = ResultStatus.PASS if review_report["status"] == "PASS" else ResultStatus.FAIL
            results.append(_result(store, "review", reviewer_status, "Independent deterministic review completed", ["ev-diff"], "Run security policy", review_report["findings"]))
            if review_report["status"] == "PASS":
                machine.transition(RunStatus.SECURITY_CHECK)
                security_report = security_review_patch(diff)
                if Role.SECURITY in roles:
                    sec_status = ResultStatus.PASS if security_report["status"] == "PASS" else ResultStatus.FAIL
                    results.append(_result(store, "security", sec_status, "Security review completed", ["ev-diff"], "Proceed to gate", security_report["findings"]))
                if Role.DOCUMENTATION in roles:
                    results.append(_result(store, "documentation", ResultStatus.PASS, "Documentation change is internally consistent", ["ev-diff"], "Proceed to gate"))
                if security_report["status"] == "PASS":
                    machine.transition(RunStatus.READY_FOR_DECISION)
    finally:
        source_unchanged = workspace.verify_source_unchanged() if workspace.base_head else False
        workspace.close()

    plan = json.loads((run_dir / "ExecutionPlan.json").read_text(encoding="utf-8"))
    plan["tasks"] = task_defs
    plan["base_head"] = workspace.base_head
    store.write("ExecutionPlan.json", plan)
    passed = machine.status == RunStatus.READY_FOR_DECISION and source_unchanged
    now = datetime.now(timezone.utc).isoformat()
    store.write("AgentResult.json", {"run_id": run_id, "status": "PASS" if passed else "FAIL", "results": results, "task_result_root": "tasks/"})
    store.write("TestEvidence.json", {"run_id": run_id, "evidence": evidence})
    store.write("ReviewReport.json", {"run_id": run_id, **review_report})
    tool_audit = gateway.report()
    store.write_optional_json("ToolAudit.json", tool_audit)
    store.write("SecurityReport.json", {
        "run_id": run_id, **security_report, "source_repository_unchanged": source_unchanged,
        "network_used": False, "tool_audit_ref": "ToolAudit.json",
        "tool_policy_denials": tool_audit["denied_count"],
    })
    if use_ai:
        usage_report = ai_ledger.report()
        usage_report.update({
            "run_id": run_id,
            "estimated_cost": str(ai_ledger.spent),
            "runtime": "hybrid_local_ai",
            "provider_mode": "local_zero_spend",
        })
        store.write(
            "UsageReport.json",
            usage_report,
        )
    else:
        store.write("UsageReport.json", {
            "run_id": run_id,
            "llm_calls": 0,
            "estimated_cost": 0.0,
            "runtime": "direct_deterministic",
            "routing_decisions": [
                {
                    "task_id": task["task_id"],
                    "task_class": TaskClass.S0.value,
                    "reason": "Direct deterministic adapter; LLM call prohibited",
                }
                for task in task_defs
            ],
        })
    store.write("RunSummary.json", {
        "run_id": run_id, "status": machine.status.value, "history": [state.value for state in machine.history],
        "repository": str(request.repository.resolve()), "base_head": workspace.base_head, "plan": request.objective,
        "selected_roles": [role.value for role in roles] + ([Role.SUPPORT.value] if repair_attempts else []),
        "changes": list(review_report.get("changed_paths", [])) if diff else [], "tests": "PASS" if final_test_passed else "FAIL",
        "repair_attempts": repair_attempts, "risk": "Patch only; source unchanged" if source_unchanged else "Source integrity failed",
        "model_usage": "Ollama local" if use_ai else "None", "decision": "Human gate pending" if passed else "Repair required", "created_at": now,
        "change_operation": request.operation,
        "context_bundle_ref": "ContextBundle.json",
        "context_selection_sha256": context_bundle["selection_sha256"],
        "context_selected_paths": context_bundle["selected_paths"],
    })
    store.write("GateDecision.json", {
        "gate_type": "G3_PROMOTE", "actor": "SYSTEM", "decision": "PENDING" if passed else "REPAIR",
        "scope": "Review multi-agent artifacts and Changes.patch", "timestamp": now,
    })
    return run_dir

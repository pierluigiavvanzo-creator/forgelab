from __future__ import annotations

import ast
import hashlib
import json
import os
import re
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
from .model_router import (
    ModelProvider,
    ModelRoute,
    ModelRouter,
    ProviderTransientError,
    TaskClass,
    UsageLedger,
    UsageRecord,
    load_routes,
    load_run_budget,
)
from .ollama_provider import OllamaProvider
from .anthropic_provider import AnthropicProvider
from .memory import ProjectMemory
from .governance import PolicyEngine, ToolGateway
from .editor_adapter import (
    AiderCliAdapter,
    AiderCliConfig,
    EditorAdapterError,
    EditorRequest,
)


@dataclass(frozen=True)
class MultiAgentRequest:
    repository: Path
    objective: str
    target_path: str
    old_text: str
    new_text: str
    test_command: list[str]
    timeout_seconds: int = 60
    editor_timeout_seconds: int = 300
    initial_new_text: str | None = None
    risk: str = "normal"
    max_repair_attempts: int = 1
    ai_mode: bool = False
    operation: str = "replace_text"
    allowed_paths: tuple[str, ...] = ()
    editor_engine: str = "custom"
    parent_run_id: str | None = None
    parent_base_head: str | None = None
    parent_candidate_patch: str | None = None

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

        editor_timeout_seconds = int(
            payload.get(
                "editor_timeout_seconds",
                300,
            )
        )

        if (
            editor_timeout_seconds < 60
            or editor_timeout_seconds > 600
        ):
            raise ValueError(
                "editor_timeout_seconds must be "
                "between 60 and 600"
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

        editor_engine = str(
            payload.get(
                "editor_engine",
                "custom",
            )
        ).strip().lower()

        if editor_engine not in {
            "custom",
            "aider",
        }:
            raise ValueError(
                "editor_engine must be custom or aider"
            )

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
            editor_timeout_seconds=editor_timeout_seconds,
            risk=payload.get(
                "risk",
                "normal",
            ),
            max_repair_attempts=attempts,
            ai_mode=ai_mode,
            operation=operation,
            allowed_paths=allowed_paths,
            editor_engine=editor_engine,
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

    if not configured and not routing_path.is_file():
        # Launched from outside the project folder: use the checkout's config.
        routing_path = (
            Path(__file__).resolve().parents[2]
            / ".forgelab"
            / "routing.yaml"
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

    # Zero-spend unless the routing config sets an explicit run_budget.
    ledger = UsageLedger(
        load_run_budget(routing_path)
    )

    providers: dict[str, ModelProvider] = {
        "ollama": OllamaProvider(
            endpoint
        ),
    }
    if any(
        route.provider == "anthropic"
        for route in routes.values()
    ):
        providers["anthropic"] = AnthropicProvider()

    router = ModelRouter(
        routes,
        providers,
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


def _ai_developer_response_schema(
    expected_paths: tuple[str, ...],
    *,
    require_all_paths: bool = True,
) -> dict[str, object]:
    change_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "enum": list(expected_paths),
            },
            "old_text": {
                "type": "string",
                "minLength": 1,
            },
            "new_text": {
                "type": "string",
            },
            "summary": {
                "type": "string",
                "minLength": 1,
            },
        },
        "required": [
            "path",
            "old_text",
            "new_text",
            "summary",
        ],
        "additionalProperties": False,
    }

    if len(expected_paths) == 1:
        return {
            "type": "object",
            "properties": {
                "schema_version": {
                    "type": "string",
                    "enum": ["1.0"],
                },
                **change_schema["properties"],
            },
            "required": [
                "schema_version",
                "path",
                "old_text",
                "new_text",
                "summary",
            ],
            "additionalProperties": False,
        }

    min_items = (
        len(expected_paths)
        if require_all_paths
        else 1
    )
    max_items = (
        len(expected_paths)
        if require_all_paths
        else len(expected_paths) * 4
    )

    return {
        "type": "object",
        "properties": {
            "schema_version": {
                "type": "string",
                "enum": ["2.0"],
            },
            "summary": {
                "type": "string",
                "minLength": 1,
            },
            "changes": {
                "type": "array",
                "minItems": min_items,
                "maxItems": max_items,
                "items": change_schema,
            },
        },
        "required": [
            "schema_version",
            "summary",
            "changes",
        ],
        "additionalProperties": False,
    }


def _ai_developer_full_file_response_schema(
    expected_paths: tuple[str, ...],
) -> dict[str, object]:
    file_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "enum": list(expected_paths),
            },
            "new_text": {
                "type": "string",
            },
            "summary": {
                "type": "string",
                "minLength": 1,
            },
        },
        "required": [
            "path",
            "new_text",
            "summary",
        ],
        "additionalProperties": False,
    }

    return {
        "type": "object",
        "properties": {
            "schema_version": {
                "type": "string",
                "enum": ["2.1"],
            },
            "summary": {
                "type": "string",
                "minLength": 1,
            },
            "files": {
                "type": "array",
                "minItems": 1,
                "maxItems": len(expected_paths),
                "items": file_schema,
            },
        },
        "required": [
            "schema_version",
            "summary",
            "files",
        ],
        "additionalProperties": False,
    }


class AIEditorExecutionError(RuntimeError):
    """Governed reusable-editor process or sandbox failure."""

    def __init__(self, phase: str, message: str) -> None:
        self.phase = phase
        super().__init__(message)


class AIDeveloperFormatError(ValueError):
    """Recoverable structured-output contract error."""


class AIDeveloperReferenceError(ValueError):
    """Recoverable exact-source reference error before write."""


class AIDeveloperSyntaxError(ValueError):
    """Recoverable Python syntax error before repository write."""


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

    raise AIDeveloperFormatError(
        "AI Developer did not return "
        "a valid JSON object"
    )



def _ai_plan_response_schema() -> dict[str, object]:
    text_item: dict[str, object] = {
        "type": "string",
        "minLength": 1,
    }

    return {
        "type": "object",
        "properties": {
            "schema_version": {
                "type": "string",
                "enum": ["1.0"],
            },
            "intended_outcome": {
                "type": "string",
                "minLength": 1,
            },
            "execution_steps": {
                "type": "array",
                "minItems": 1,
                "maxItems": 20,
                "items": text_item,
            },
            "acceptance_criteria": {
                "type": "array",
                "minItems": 1,
                "maxItems": 40,
                "items": text_item,
            },
            "principal_risks": {
                "type": "array",
                "maxItems": 20,
                "items": text_item,
            },
        },
        "required": [
            "schema_version",
            "intended_outcome",
            "execution_steps",
            "acceptance_criteria",
            "principal_risks",
        ],
        "additionalProperties": False,
    }


def _validate_ai_plan(
    response_text: str,
) -> dict[str, Any]:
    payload = _extract_ai_developer_json(response_text)

    required = {
        "schema_version",
        "intended_outcome",
        "execution_steps",
        "acceptance_criteria",
        "principal_risks",
    }
    missing = required - set(payload)
    if missing:
        raise ValueError(
            "AI Project Manager missing fields: "
            + ", ".join(sorted(missing))
        )

    if payload["schema_version"] != "1.0":
        raise ValueError(
            "AI Project Manager schema_version must be 1.0"
        )

    intended_outcome = payload["intended_outcome"]
    if (
        not isinstance(intended_outcome, str)
        or not intended_outcome.strip()
    ):
        raise ValueError(
            "AI Project Manager intended_outcome must be non-empty"
        )

    def validated_list(
        key: str,
        *,
        required_non_empty: bool,
    ) -> list[str]:
        raw = payload[key]
        if (
            not isinstance(raw, list)
            or (required_non_empty and not raw)
            or not all(
                isinstance(item, str)
                and item.strip()
                for item in raw
            )
        ):
            raise ValueError(
                f"AI Project Manager {key} "
                "must be a structured string list"
            )
        return [item.strip() for item in raw]

    return {
        "schema_version": "1.0",
        "intended_outcome": intended_outcome.strip(),
        "execution_steps": validated_list(
            "execution_steps",
            required_non_empty=True,
        ),
        "acceptance_criteria": validated_list(
            "acceptance_criteria",
            required_non_empty=True,
        ),
        "principal_risks": validated_list(
            "principal_risks",
            required_non_empty=False,
        ),
    }


def _ai_review_response_schema() -> dict[str, object]:
    requirement_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "requirement": {
                "type": "string",
                "minLength": 1,
            },
            "status": {
                "type": "string",
                "enum": [
                    "SATISFIED",
                    "MISSING",
                    "UNVERIFIED",
                    "PARTIAL",
                ],
            },
            "evidence": {
                "type": "string",
                "minLength": 1,
            },
        },
        "required": [
            "requirement",
            "status",
            "evidence",
        ],
        "additionalProperties": False,
    }

    finding_schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "severity": {
                "type": "string",
                "enum": [
                    "BLOCKER",
                    "WARN",
                    "INFO",
                ],
            },
            "category": {
                "type": "string",
                "minLength": 1,
            },
            "description": {
                "type": "string",
                "minLength": 1,
            },
        },
        "required": [
            "severity",
            "category",
            "description",
        ],
        "additionalProperties": False,
    }

    return {
        "type": "object",
        "properties": {
            "schema_version": {
                "type": "string",
                "enum": ["1.0"],
            },
            "status": {
                "type": "string",
                "enum": ["PASS", "FAIL"],
            },
            "summary": {
                "type": "string",
                "minLength": 1,
            },
            "requirements": {
                "type": "array",
                "minItems": 1,
                "maxItems": 40,
                "items": requirement_schema,
            },
            "findings": {
                "type": "array",
                "maxItems": 40,
                "items": finding_schema,
            },
        },
        "required": [
            "schema_version",
            "status",
            "summary",
            "requirements",
            "findings",
        ],
        "additionalProperties": False,
    }


def _validate_ai_review(
    response_text: str,
) -> dict[str, Any]:
    payload = _extract_ai_developer_json(
        response_text
    )

    required = {
        "schema_version",
        "status",
        "summary",
        "requirements",
        "findings",
    }

    missing = required - set(payload)

    if missing:
        raise ValueError(
            "AI Reviewer missing fields: "
            + ", ".join(sorted(missing))
        )

    if payload["schema_version"] != "1.0":
        raise ValueError(
            "AI Reviewer schema_version must be 1.0"
        )

    if payload["status"] not in {
        "PASS",
        "FAIL",
    }:
        raise ValueError(
            "AI Reviewer status must be PASS or FAIL"
        )

    summary = payload["summary"]

    if (
        not isinstance(summary, str)
        or not summary.strip()
    ):
        raise ValueError(
            "AI Reviewer summary must be non-empty"
        )

    raw_requirements = payload["requirements"]

    if (
        not isinstance(raw_requirements, list)
        or not raw_requirements
        or not all(
            isinstance(item, dict)
            for item in raw_requirements
        )
    ):
        raise ValueError(
            "AI Reviewer requirements must be "
            "a non-empty structured list"
        )

    requirements: list[dict[str, str]] = []

    for item in raw_requirements:
        requirement = item.get("requirement")
        status = item.get("status")
        evidence = item.get("evidence")

        if (
            not isinstance(requirement, str)
            or not requirement.strip()
            or status not in {
                "SATISFIED",
                "MISSING",
                "UNVERIFIED",
                "PARTIAL",
            }
            or not isinstance(evidence, str)
            or not evidence.strip()
        ):
            raise ValueError(
                "AI Reviewer requirement entry is invalid"
            )

        requirements.append({
            "requirement": requirement.strip(),
            "status": str(status),
            "evidence": evidence.strip(),
        })

    raw_findings = payload["findings"]

    if (
        not isinstance(raw_findings, list)
        or not all(
            isinstance(item, dict)
            for item in raw_findings
        )
    ):
        raise ValueError(
            "AI Reviewer findings must be "
            "a structured list"
        )

    findings: list[dict[str, str]] = []

    for item in raw_findings:
        severity = item.get("severity")
        category = item.get("category")
        description = item.get("description")

        if (
            severity not in {
                "BLOCKER",
                "WARN",
                "INFO",
            }
            or not isinstance(category, str)
            or not category.strip()
            or not isinstance(description, str)
            or not description.strip()
        ):
            raise ValueError(
                "AI Reviewer finding entry is invalid"
            )

        findings.append({
            "severity": str(severity),
            "category": category.strip(),
            "description": description.strip(),
        })

    missing_requirements = [
        item
        for item in requirements
        if item["status"] != "SATISFIED"
    ]

    blocker_findings = [
        item
        for item in findings
        if item["severity"] == "BLOCKER"
    ]

    status = (
        "FAIL"
        if (
            payload["status"] == "FAIL"
            or missing_requirements
            or blocker_findings
        )
        else "PASS"
    )

    if (
        status == "FAIL"
        and not findings
    ):
        findings = [
            {
                "severity": "BLOCKER",
                "category": "objective_coverage",
                "description": (
                    "One or more explicit objective "
                    "requirements are missing or unverified"
                ),
            }
        ]

    return {
        "schema_version": "1.0",
        "status": status,
        "summary": summary.strip(),
        "requirements": requirements,
        "findings": findings,
    }


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
        raise AIDeveloperFormatError(
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
        raise AIDeveloperFormatError(
            "AI Developer old_text must "
            "be non-empty"
        )

    if not isinstance(new_text, str):
        raise AIDeveloperFormatError(
            "AI Developer new_text must "
            "be a string"
        )

    if (
        not isinstance(summary, str)
        or not summary.strip()
    ):
        raise AIDeveloperFormatError(
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
        raise AIDeveloperFormatError(
            "AI Developer proposed "
            "a no-op replacement"
        )

    match_count = source_texts[path].count(
        old_text
    )

    if match_count != 1:
        raise AIDeveloperReferenceError(
            "AI Developer old_text must occur "
            f"exactly once in {path}; found {match_count}"
        )

    return {
        "path": path,
        "old_text": old_text,
        "new_text": new_text,
        "summary": summary.strip(),
    }


def _compose_ai_developer_changes(
    validated: list[dict[str, str]],
    expected_paths: tuple[str, ...],
    source_texts: dict[str, str],
) -> list[dict[str, str]]:
    grouped: dict[
        str,
        list[dict[str, str]],
    ] = {
        path: []
        for path in expected_paths
    }

    for item in validated:
        grouped[item["path"]].append(item)

    normalized: list[dict[str, str]] = []

    for path in expected_paths:
        path_changes = grouped[path]

        if not path_changes:
            continue

        if len(path_changes) > 4:
            raise AIDeveloperFormatError(
                "AI Developer may propose at most "
                f"4 changes per authorized path; "
                f"{path} has {len(path_changes)}"
            )

        if len(path_changes) == 1:
            normalized.append(path_changes[0])
            continue

        source = source_texts[path]
        spans: list[
            tuple[int, int, dict[str, str]]
        ] = []

        for item in path_changes:
            start = source.find(
                item["old_text"]
            )
            end = start + len(
                item["old_text"]
            )
            spans.append((
                start,
                end,
                item,
            ))

        spans.sort(key=lambda entry: entry[0])

        previous_end = -1

        for start, end, _ in spans:
            if start < previous_end:
                raise AIDeveloperFormatError(
                    "AI Developer changes overlap "
                    f"in {path}"
                )
            previous_end = end

        parts: list[str] = []
        cursor = 0
        summaries: list[str] = []

        for start, end, item in spans:
            parts.append(source[cursor:start])
            parts.append(item["new_text"])
            cursor = end
            summaries.append(item["summary"])

        parts.append(source[cursor:])
        composed = "".join(parts)

        if composed == source:
            raise AIDeveloperFormatError(
                "AI Developer composed a no-op "
                f"replacement for {path}"
            )

        if len(composed) > 100_000:
            raise ValueError(
                "AI Developer composed replacement "
                "exceeds size limit"
            )

        normalized.append({
            "path": path,
            "old_text": source,
            "new_text": composed,
            "summary": "; ".join(summaries),
        })

    return normalized


def _validate_ai_developer_full_file_patch(
    response_text: str,
    expected_paths: tuple[str, ...],
    source_texts: dict[str, str],
) -> dict[str, Any]:
    payload = _extract_ai_developer_json(
        response_text
    )

    required = {
        "schema_version",
        "summary",
        "files",
    }
    missing = required - set(payload)

    if missing:
        raise AIDeveloperFormatError(
            "AI Developer full-file recovery missing fields: "
            + ", ".join(sorted(missing))
        )

    if payload["schema_version"] != "2.1":
        raise AIDeveloperFormatError(
            "AI Developer full-file recovery "
            "schema_version must be 2.1"
        )

    summary = payload["summary"]
    raw_files = payload["files"]

    if (
        not isinstance(summary, str)
        or not summary.strip()
    ):
        raise AIDeveloperFormatError(
            "AI Developer full-file recovery "
            "summary must be non-empty"
        )

    if (
        not isinstance(raw_files, list)
        or not 1 <= len(raw_files) <= len(expected_paths)
        or not all(
            isinstance(item, dict)
            for item in raw_files
        )
    ):
        raise AIDeveloperFormatError(
            "AI Developer full-file recovery files "
            "must be a non-empty authorized subset"
        )

    normalized: dict[str, dict[str, str]] = {}

    for item in raw_files:
        item_required = {
            "path",
            "new_text",
            "summary",
        }
        item_missing = item_required - set(item)

        if item_missing:
            raise AIDeveloperFormatError(
                "AI Developer full-file entry missing fields: "
                + ", ".join(sorted(item_missing))
            )

        path = item["path"]
        new_text = item["new_text"]
        item_summary = item["summary"]

        if path not in expected_paths:
            raise ValueError(
                "AI Developer attempted path expansion"
            )

        if path in normalized:
            raise AIDeveloperFormatError(
                "AI Developer full-file recovery "
                "contains duplicate paths"
            )

        if not isinstance(new_text, str):
            raise AIDeveloperFormatError(
                "AI Developer full-file new_text "
                "must be a string"
            )

        if (
            not isinstance(item_summary, str)
            or not item_summary.strip()
        ):
            raise AIDeveloperFormatError(
                "AI Developer full-file summary "
                "must be non-empty"
            )

        if len(new_text) > 100_000:
            raise ValueError(
                "AI Developer full-file replacement "
                "exceeds size limit"
            )

        current = source_texts[path]

        if new_text == current:
            raise AIDeveloperFormatError(
                "AI Developer proposed a no-op "
                f"full-file replacement for {path}"
            )

        normalized[path] = {
            "path": path,
            "old_text": current,
            "new_text": new_text,
            "summary": item_summary.strip(),
        }

    return {
        "schema_version": "2.0",
        "summary": summary.strip(),
        "changes": [
            normalized[path]
            for path in expected_paths
            if path in normalized
        ],
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
            raise AIDeveloperFormatError(
                "AI Developer patch missing fields: "
                + ", ".join(sorted(missing))
            )

        if payload["schema_version"] != "1.0":
            raise AIDeveloperFormatError(
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

    flat_change_required = {
        "path",
        "old_text",
        "new_text",
        "summary",
    }

    if (
        missing
        and not require_all_paths
        and flat_change_required <= set(payload)
    ):
        normalized_change = (
            _validate_ai_developer_change(
                payload,
                expected_paths,
                source_texts,
            )
        )

        return {
            "schema_version": "2.0",
            "summary": normalized_change[
                "summary"
            ],
            "changes": [
                normalized_change
            ],
        }

    if missing:
        raise AIDeveloperFormatError(
            "AI Developer multi-file patch missing fields: "
            + ", ".join(sorted(missing))
        )

    if payload["schema_version"] != "2.0":
        raise AIDeveloperFormatError(
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
        raise AIDeveloperFormatError(
            "AI Developer multi-file changes must be "
            "a structured change list"
        )

    if require_all_paths:
        if len(raw_changes) != len(expected_paths):
            raise AIDeveloperFormatError(
                "AI Developer multi-file changes must contain "
                "exactly one structured change per authorized path"
            )
    elif not (
        1
        <= len(raw_changes)
        <= len(expected_paths) * 4
    ):
        raise AIDeveloperFormatError(
            "AI Developer must propose between 1 and "
            f"{len(expected_paths) * 4} bounded change "
            "operations inside authorized paths"
        )

    if (
        not isinstance(summary, str)
        or not summary.strip()
    ):
        raise AIDeveloperFormatError(
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

    if require_all_paths:
        if len(set(changed_paths)) != len(changed_paths):
            raise ValueError(
                "AI Developer multi-file patch "
                "contains duplicate paths"
            )

        if set(changed_paths) != set(expected_paths):
            raise ValueError(
                "AI Developer multi-file patch must "
                "change every authorized path exactly once"
            )

        by_path = {
            item["path"]: item
            for item in validated
        }
        normalized_changes = [
            by_path[path]
            for path in expected_paths
        ]
    else:
        normalized_changes = (
            _compose_ai_developer_changes(
                validated,
                expected_paths,
                source_texts,
            )
        )

    return {
        "schema_version": "2.0",
        "summary": summary.strip(),
        "changes": normalized_changes,
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


def _aider_process_failure_message(
    label: str,
    result: EditorResult,
    *,
    max_output_chars: int = 1600,
) -> str:
    parts = [
        (
            f"{label}: exit={result.exit_status}, "
            f"timed_out={result.timed_out}"
        )
    ]

    stderr_tail = (result.stderr or "").strip()
    stdout_tail = (result.stdout or "").strip()

    if stderr_tail:
        parts.append(
            "stderr_tail:\n"
            + stderr_tail[-max_output_chars:]
        )

    if stdout_tail:
        parts.append(
            "stdout_tail:\n"
            + stdout_tail[-max_output_chars:]
        )

    return "\n".join(parts)


_EDITOR_PROVIDER_ERROR = re.compile(r"litellm\.\w*Error")


def _run_aider_editor(
    *,
    repository: Path,
    objective: str,
    allowed_paths: tuple[str, ...],
    model: str,
    timeout_seconds: int,
    phase: str,
    route: ModelRoute | None = None,
    ledger: UsageLedger | None = None,
) -> EditorResult:
    labels = {
        "implementation": "Aider editor",
        "initial_prewrite_correction":
            "Aider initial pre-write correction",
        "test_failure_repair":
            "Aider test-failure repair",
        "semantic_review_repair":
            "Aider semantic repair",
    }
    label = labels.get(
        phase,
        "Aider reusable editor",
    )
    executable = os.environ.get(
        "FORGELAB_AIDER_EXECUTABLE",
        "aider",
    )
    provider = (
        route.provider
        if route is not None and route.provider
        else "ollama"
    )
    remote_route = route if provider != "ollama" else None
    pricing = None
    if remote_route is not None:
        if remote_route.pricing is None:
            raise AIEditorExecutionError(
                phase,
                f"{label} blocked: the {provider} route has no "
                "configured pricing",
            )
        if (
            ledger is not None
            and remote_route.max_call_cost > ledger.remaining
        ):
            raise AIEditorExecutionError(
                phase,
                f"{label} blocked: route reservation exceeds the "
                "remaining run budget",
            )
        pricing = (
            remote_route.pricing.input_per_million,
            remote_route.pricing.output_per_million,
        )
    try:
        result = AiderCliAdapter(
            AiderCliConfig(
                executable=(executable,),
                edit_format="whole",
            )
        ).run(
            EditorRequest(
                repository=repository,
                objective=objective,
                allowed_paths=allowed_paths,
                model=model,
                timeout_seconds=timeout_seconds,
                provider=provider,
                pricing=pricing,
            )
        )
    except EditorAdapterError as error:
        raise AIEditorExecutionError(
            phase,
            f"{label} failed before governed write: {error}",
        ) from error

    # Aider exits 0 when the provider rejects the call (bad key, quota, ...).
    provider_error = (
        remote_route is not None
        and not result.changed_paths
        and _EDITOR_PROVIDER_ERROR.search(result.stdout) is not None
    )

    if remote_route is not None and ledger is not None:
        # The editor calls the provider itself: charge what it reports, or
        # the full route reservation when a completed call reports nothing.
        cost = result.reported_cost
        if cost is None:
            cost = (
                Decimal("0")
                if provider_error
                else remote_route.max_call_cost
            )
        ledger.records.append(UsageRecord(
            f"aider-cli/{provider}", model,
            remote_route.task_class.value, "DEVELOPER", phase,
            0, 0, 0, str(cost),
            result.duration_ms, 1,
            "FAIL" if provider_error and cost == 0 else "SUCCESS",
            "Reusable editor call priced from its session report",
            "provider rejected the editor call" if provider_error
            else None if result.reported_cost is not None
            else "editor reported no cost; route reservation charged",
        ))

    if provider_error:
        raise AIEditorExecutionError(
            phase,
            _aider_process_failure_message(
                f"{label} was rejected by the {provider} provider",
                result,
            ),
        )

    if (
        result.exit_status != 0
        or result.timed_out
    ):
        raise AIEditorExecutionError(
            phase,
            _aider_process_failure_message(
                f"{label} did not complete successfully",
                result,
            ),
        )

    return result


def _validate_ai_developer_candidate_syntax(
    payload: dict[str, Any],
    source_texts: dict[str, str],
) -> None:
    for change in _ai_patch_changes(payload):
        path = change["path"]

        if not path.lower().endswith(".py"):
            continue

        source = source_texts[path]
        candidate = source.replace(
            change["old_text"],
            change["new_text"],
            1,
        )

        try:
            ast.parse(
                candidate.lstrip("\ufeff"),
                filename=path,
            )
        except SyntaxError as error:
            location = (
                f"line {error.lineno}"
                if error.lineno is not None
                else "unknown line"
            )
            raise AIDeveloperSyntaxError(
                "AI Developer Python candidate "
                f"does not parse in {path} at "
                f"{location}: {error.msg}"
            ) from error


def _extract_deterministic_test_outcomes(
    stdout: str,
    stderr: str,
) -> dict[str, str]:
    outcomes: dict[str, str] = {}

    for raw_line in (stdout + "\n" + stderr).splitlines():
        line = raw_line.strip()

        if " ... " not in line:
            continue

        test_name, raw_status = line.rsplit(
            " ... ",
            1,
        )
        status = raw_status.strip()

        if status == "ok":
            outcomes[test_name.strip()] = "PASS"
        elif status in {"FAIL", "ERROR"}:
            outcomes[test_name.strip()] = status

    return outcomes


def _regressed_passing_tests(
    before: dict[str, str],
    after: dict[str, str],
) -> list[str]:
    return sorted(
        test_name
        for test_name, status in before.items()
        if (
            status == "PASS"
            and after.get(test_name) in {
                "FAIL",
                "ERROR",
            }
        )
    )


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


def _record_provider_failure(
    store: ArtifactStore,
    run_id: str,
    ledger: UsageLedger,
    phase: str,
    error: ProviderTransientError,
) -> tuple[dict[str, Any], dict[str, Any]]:
    last_record = (
        ledger.records[-1]
        if ledger.records
        else None
    )
    task_id = (
        last_record.task_id
        if last_record is not None
        else "unknown"
    )
    attempts_for_task = sum(
        1
        for record in ledger.records
        if record.task_id == task_id
    )
    artifact = {
        "run_id": run_id,
        "status": "FAIL",
        "reason": "PROVIDER_TRANSIENT_RETRY_EXHAUSTED",
        "phase": phase,
        "provider": (
            last_record.provider
            if last_record is not None
            else None
        ),
        "model": (
            last_record.model_id
            if last_record is not None
            else None
        ),
        "task_id": task_id,
        "attempts": attempts_for_task,
        "final_error_type": type(error).__name__,
        "final_error": str(error),
        "estimated_cost": str(ledger.spent),
    }
    store.write_optional_json(
        "ProviderFailure.json",
        artifact,
    )
    evidence = {
        "evidence_id": "ev-provider-failure",
        "check_type": "provider_runtime",
        "command_or_tool": "local_zero_spend_model_router",
        "exit_status": 1,
        "summary": (
            "Local provider retries exhausted: "
            + str(error)
        ),
        "artifact_ref": "ProviderFailure.json",
        "phase": phase,
        "task_id": task_id,
    }
    return artifact, evidence


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


def run_multi_agent(
    request: MultiAgentRequest,
    output_root: Path,
    *,
    run_id: str | None = None,
) -> Path:
    run_id = run_id or f"run-{uuid4().hex[:12]}"
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

    if request.editor_engine not in {
        "custom",
        "aider",
    }:
        raise ValueError(
            "editor_engine must be custom or aider"
        )

    if (
        request.editor_engine == "aider"
        and request.operation != "ai_generate"
    ):
        raise ValueError(
            "aider editor_engine requires ai_generate"
        )

    use_ai = (
        request.ai_mode
        or request.operation == "ai_generate"
    )

    ai_router: ModelRouter | None = None
    ai_ledger = UsageLedger(Decimal("0"))
    ai_plan: dict[str, Any] | None = None
    plan_contract_text = ""

    machine.transition(
        RunStatus.PRECHECK
    )

    policy_dir = request.repository / ".forgelab"
    if (policy_dir / "agents.yaml").is_file() and (policy_dir / "policy.yaml").is_file():
        policy_engine = PolicyEngine.from_directory(policy_dir)
    else:
        policy_engine = PolicyEngine()
    gateway = ToolGateway(policy_engine)
    parent_source_texts: dict[str, str] | None = None
    parent_fields = (request.parent_run_id, request.parent_base_head, request.parent_candidate_patch)
    if any(value is not None for value in parent_fields):
        if request.operation != "ai_generate" or not all(parent_fields):
            raise ValueError("native repair requires parent run, baseline and candidate patch")
        with IsolatedWorkspace(request.repository, f"{run_id}-parent") as preview:
            if preview.base_head != request.parent_base_head:
                raise ValueError("parent candidate baseline differs from current source HEAD")
            # Validate existing targets before a patch can change the preview.
            original_texts = _read_ai_developer_targets(preview.path, target_paths)
            gateway.apply_candidate_patch(Role.DEVELOPER, preview.path, set(target_paths), request.parent_candidate_patch)
            parent_source_texts = _read_ai_developer_targets(preview.path, target_paths)
            changed_files = [{"path": path, "new_text": text, "summary": "Preserve parent candidate"}
                             for path, text in parent_source_texts.items() if text != original_texts[path]]
            parent_payload = _validate_ai_developer_full_file_patch(json.dumps({
                "schema_version": "2.1", "summary": "Preserve parent candidate", "files": changed_files,
            }), target_paths, original_texts)
            _validate_ai_developer_candidate_syntax(parent_payload, original_texts)
        store.write_optional_json("ParentCandidate.json", {
            "parent_run_id": request.parent_run_id, "base_head": request.parent_base_head,
            "patch_sha256": hashlib.sha256(request.parent_candidate_patch.encode("utf-8")).hexdigest(),
            "changed_paths": [item["path"] for item in changed_files],
            "source_files_sha256": {path: hashlib.sha256(text.encode("utf-8")).hexdigest()
                                    for path, text in parent_source_texts.items()},
        })
        store.write_text("ParentCandidate.patch", request.parent_candidate_patch)

    if use_ai:
        ai_router, ai_ledger = _build_local_ai_router()

        plan_targets = "\n".join(
            f"- {path}"
            for path in target_paths
        )

        plan_source_texts = parent_source_texts or _read_ai_developer_targets(
            request.repository,
            target_paths,
        )
        plan_files_context = "\n\n".join(
            (
                f"--- BEGIN AUTHORIZED FILE {path} ---\n"
                f"{plan_source_texts[path]}\n"
                f"--- END AUTHORIZED FILE {path} ---"
            )
            for path in target_paths
        )

        plan_prompt = f"""
You are the PROJECT_MANAGER agent in ForgeLab.

Create a concise bounded implementation plan AND a binding
acceptance contract for the downstream Developer.

Objective:
{request.objective}

Authorized target paths:
{plan_targets}

Governed read-only project/repository context:
{governed_context}

Current complete authorized files (read-only planning context):
{plan_files_context}

Rules:
- decompose the objective into every explicit obligation;
- do not invent product requirements, optional enhancements,
  dependencies or scope beyond the objective and governed context;
- preserve quantitative words and counts such as "three",
  "each", "all", ranges, percentages and exact limits;
- acceptance criteria must be observable in implementation,
  deterministic tests or user-visible behavior;
- include required test coverage as acceptance criteria when
  the objective asks for tests;
- do not expand the authorized write scope;
- do not claim tools or tests have already run.

Return ONLY the required structured JSON object.
"""

        try:
            plan_response = ai_router.execute(
                TaskClass.S1,
                plan_prompt,
                "plan",
                Role.PROJECT_MANAGER.value,
                "AI-assisted bounded planning",
                request.timeout_seconds,
                response_format=_ai_plan_response_schema(),
            )
        except ProviderTransientError as provider_error:
            _, provider_evidence = _record_provider_failure(
                store,
                run_id,
                ai_ledger,
                machine.status.value,
                provider_error,
            )
            early_tasks = [
                _task(
                    run_id,
                    "plan",
                    Role.PROJECT_MANAGER,
                    "Create bounded execution plan",
                    target_paths,
                    ["repo_read"],
                    [],
                ),
                _task(
                    run_id,
                    "implement",
                    Role.DEVELOPER,
                    request.objective,
                    target_paths,
                    ["repo_edit"],
                    ["plan"],
                ),
                _task(
                    run_id,
                    "test",
                    Role.TESTER,
                    "Run acceptance tests",
                    target_paths,
                    ["test_runner"],
                    ["implement"],
                ),
                _task(
                    run_id,
                    "review",
                    Role.REVIEWER,
                    "Review scope and correctness",
                    target_paths,
                    ["git_diff"],
                    ["test"],
                ),
            ]
            machine.transition(
                RunStatus.CLOSED
            )
            now = datetime.now(
                timezone.utc
            ).isoformat()
            store.write(
                "ExecutionPlan.json",
                {
                    "run_id": run_id,
                    "objective": request.objective,
                    "repository": str(
                        request.repository.resolve()
                    ),
                    "tasks": early_tasks,
                    "selected_roles": [
                        role.value
                        for role in roles
                    ],
                    "selection_reason": (
                        "Planning provider failed after "
                        "bounded local retries"
                    ),
                    "max_repair_attempts":
                        request.max_repair_attempts,
                    "test_command":
                        request.test_command,
                    "change_operation":
                        request.operation,
                    "editor_engine":
                        request.editor_engine,
                    "allowed_paths":
                        list(target_paths),
                    "timeout_seconds":
                        request.timeout_seconds,
                    "editor_timeout_seconds":
                        request.editor_timeout_seconds,
                    "requires_human_gate": True,
                    "memory_snapshot_ref":
                        "MemorySnapshot.json",
                    "context_bundle_ref":
                        "ContextBundle.json",
                    "memory_manifest_sha256":
                        memory_snapshot[
                            "manifest_sha256"
                        ],
                    "context_selection": {
                        "mode":
                            context_bundle["mode"],
                        "write_scope_expansion":
                            context_bundle[
                                "write_scope_expansion"
                            ],
                        "selection_sha256":
                            context_bundle[
                                "selection_sha256"
                            ],
                        "selected_paths":
                            context_bundle[
                                "selected_paths"
                            ],
                        "used_chars":
                            context_bundle["used_chars"],
                    },
                },
            )
            store.write(
                "AgentResult.json",
                {
                    "run_id": run_id,
                    "status": "FAIL",
                    "results": [
                        AgentResult(
                            ResultStatus.FAIL,
                            (
                                "Local provider retries exhausted "
                                "during planning"
                            ),
                            [],
                            ["ev-provider-failure"],
                            [],
                            [],
                            "Retry or inspect local provider",
                        ).to_dict()
                    ],
                    "task_result_root": "tasks/",
                },
            )
            store.write(
                "TestEvidence.json",
                {
                    "run_id": run_id,
                    "evidence": [
                        provider_evidence
                    ],
                },
            )
            store.write(
                "ReviewReport.json",
                {
                    "run_id": run_id,
                    "status": "FAIL",
                    "changed_paths": [],
                    "findings": [],
                    "deterministic_status": "NOT_RUN",
                    "semantic_status": "NOT_RUN",
                    "semantic_requirements": [],
                    "semantic_summary": (
                        "Review did not run because the "
                        "local provider failed during planning."
                    ),
                    "review_round": 0,
                },
            )
            store.write(
                "SecurityReport.json",
                {
                    "run_id": run_id,
                    "status": "NOT_RUN",
                    "findings": [],
                    "source_repository_unchanged": True,
                    "network_used": True,
                    "network_scope": "loopback_only",
                    "external_network_allowed": False,
                    "tool_policy_denials": 0,
                },
            )
            usage_report = ai_ledger.report()
            usage_report.update({
                "run_id": run_id,
                "estimated_cost":
                    str(ai_ledger.spent),
                "runtime":
                    "hybrid_local_ai",
                "provider_mode":
                    "local_zero_spend",
            })
            store.write(
                "UsageReport.json",
                usage_report,
            )
            store.write(
                "RunSummary.json",
                {
                    "run_id": run_id,
                    "status":
                        machine.status.value,
                    "history": [
                        state.value
                        for state in machine.history
                    ],
                    "repository": str(
                        request.repository.resolve()
                    ),
                    "base_head": None,
                    "plan":
                        request.objective,
                    "selected_roles": [
                        role.value
                        for role in roles
                    ],
                    "changes": [],
                    "tests": "FAIL",
                    "repair_attempts": 0,
                    "risk":
                        "Source unchanged; provider failure",
                    "model_usage":
                        "Ollama local",
                    "decision":
                        "Repair required",
                    "created_at": now,
                    "change_operation":
                        request.operation,
                    "editor_engine":
                        request.editor_engine,
                    "chatgpt_assistance_in_target_product_run":
                        0,
                    "product_owner_run_actions":
                        1,
                    "context_bundle_ref":
                        "ContextBundle.json",
                    "context_selection_sha256":
                        context_bundle[
                            "selection_sha256"
                        ],
                    "context_selected_paths":
                        context_bundle[
                            "selected_paths"
                        ],
                },
            )
            store.write(
                "GateDecision.json",
                {
                    "gate_type": "G3_PROMOTE",
                    "actor": "SYSTEM",
                    "decision": "REPAIR",
                    "scope": (
                        "Local provider failed before "
                        "implementation"
                    ),
                    "timestamp": now,
                },
            )
            return run_dir

        ai_plan = _validate_ai_plan(plan_response.text)
        plan_contract_text = json.dumps(
            ai_plan,
            indent=2,
            ensure_ascii=False,
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
                **ai_plan,
                "text": plan_response.text,
                "context_bundle_ref": "ContextBundle.json",
                "context_selection_sha256": context_bundle["selection_sha256"],
            },
        )
    task_defs = [
        _task(run_id, "plan", Role.PROJECT_MANAGER, "Create bounded execution plan", target_paths, ["repo_read"], []),
        _task(run_id, "implement", Role.DEVELOPER, request.objective, target_paths, ["repo_edit"], ["plan"]),
        _task(run_id, "test", Role.TESTER, "Run acceptance tests", target_paths, ["test_runner"], ["implement"]),
        _task(run_id, "review", Role.REVIEWER, "Review scope and correctness", target_paths, ["git_diff"], ["test"]),
    ]

    if ai_plan is not None:
        task_defs[1]["acceptance_criteria"] = list(
            ai_plan["acceptance_criteria"]
        )
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
        "editor_engine": request.editor_engine,
        "parent_run_id": request.parent_run_id,
        "parent_candidate_ref": "ParentCandidate.json" if parent_source_texts is not None else None,
        "allowed_paths": list(target_paths),
        "timeout_seconds": request.timeout_seconds,
        "editor_timeout_seconds": request.editor_timeout_seconds,
        "requires_human_gate": True,
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
    reusable_editor_calls = 0
    format_repair_attempts = 0
    reference_repair_attempts = 0
    syntax_repair_attempts = 0
    prewrite_repair_attempts = 0
    prewrite_recovery_context: dict[str, str] | None = None
    semantic_review_history: list[dict[str, Any]] = []
    semantic_noop: dict[str, Any] | None = None
    source_unchanged = False
    final_test_passed = False
    repair_regression_baseline: dict[str, str] | None = None
    repair_regression_baseline_stdout = ""
    repair_regression_baseline_stderr = ""
    repair_regression_snapshot: dict[str, str] | None = None
    repair_regression_changed_paths: list[str] = []
    repair_regression_correction_used = False
    repair_regression_attempt_number = 0
    repair_regression_evidence_ref = ""
    regression_correction_retest_pending = False
    review_report: dict[str, Any] = {"status": "FAIL", "findings": []}
    security_report: dict[str, Any] = {"status": "PASS", "findings": []}
    try:
        workspace.create()
        if parent_source_texts is not None:
            if workspace.base_head != request.parent_base_head:
                raise ValueError("parent candidate baseline changed before isolation")
            baseline_texts = _read_ai_developer_targets(workspace.path, target_paths)
            for path, text in parent_source_texts.items():
                if text != baseline_texts[path]:
                    gateway.edit_text(Role.DEVELOPER, workspace.path, set(target_paths), path, baseline_texts[path], text)
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
                schema_instructions = (
                    "{\n"
                    '  "schema_version": "2.0",\n'
                    '  "summary": "<short overall implementation summary>",\n'
                    '  "changes": [\n'
                    "    {\n"
                    '      "path": "<one authorized path that actually needs modification>",\n'
                    '      "old_text": "<exact existing contiguous text>",\n'
                    '      "new_text": "<replacement text>",\n'
                    '      "summary": "<short per-file summary>"\n'
                    "    }\n"
                    "  ]\n"
                    "}"
                )

            developer_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

Your task is to propose the smallest correct bounded
replacement set needed to satisfy the objective.

Objective:
{request.objective}

Project Manager structured implementation plan and binding
acceptance contract:
{plan_contract_text}

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
- every Project Manager acceptance_criteria item is binding.
- preserve exact quantitative requirements from the plan.
- passing existing tests is not proof of an uncovered criterion.
- add or strengthen tests inside authorized scope when required
  by the acceptance contract.
- for every acceptance criterion that can be deterministically tested
  inside authorized scope, include at least one test whose setup and
  assertions directly exercise that criterion; a test name alone is
  not evidence.
- quantitative requirements must be tested quantitatively: exact counts
  such as "three" require distinct inputs/items and assertions over the
  complete aggregate behavior, not merely generic collection support.
- do not repurpose an existing test name to assert unrelated behavior;
  test name, setup, exercised API, and assertions must agree.
- keep user-facing numeric/unit conventions consistent end-to-end;
  avoid applying the same conversion at multiple boundaries.
- when an authorized file contains an existing user-facing
  interface or entry point and the objective changes user-visible
  behavior, wire the required behavior through that interface;
  helper functions alone do not satisfy end-to-end acceptance.
- before returning, verify every acceptance criterion against the
  proposed implementation and tests in the authorized files.
- new or modified tests must exercise the candidate API consistently
  with its actual return types and public contract; do not write a
  test that combines or indexes values in a way the implementation
  contract does not support.
- preserve existing public return shapes, keys, and already-valid
  behavior unless the objective explicitly requires changing them.
- every path MUST be one of the authorized target paths.
- authorized paths define the maximum write scope, not mandatory edits.
- return one or more changes only for files that actually need modification.
- never emit a no-op change: old_text and new_text must differ; omit
  any unchanged file or region instead.
- multiple changes may target the same file only when their old_text regions are disjoint.
- use at most 4 changes per authorized path.
- old_text MUST occur exactly once in its corresponding file.
- choose the smallest sufficient replacement for each file.
- do not modify any other file.
- do not claim tests have run.
- do not create dependencies.
"""

            developer_schema = (
                _ai_developer_response_schema(
                    target_paths,
                    require_all_paths=False,
                )
            )

            developer_route = ai_router.route(
                TaskClass.S2
            )
            editor_metadata: dict[str, Any] = {
                "engine": request.editor_engine,
                "chatgpt_assistance": 0,
                "editor_timeout_seconds":
                    request.editor_timeout_seconds,
            }
            if request.editor_engine == "aider":
                editor_metadata.update({
                    "integration_contract":
                        "aider-stabilization-v1",
                    "tool_state_policy":
                        "isolated_tool_home",
                    "model_metadata_policy":
                        "local_explicit_metadata",
                    "network_policy": (
                        "loopback_ollama_with_process_env_egress_guard"
                        if developer_route.provider in (None, "ollama")
                        else f"{developer_route.provider}_api_host_only_"
                        "with_process_env_egress_guard"
                    ),
                    "environment_policy":
                        "minimal_safe_allowlist",
                })

            try:
                if request.editor_engine == "aider":
                    reusable_editor_calls += 1
                    aider_objective = (
                        request.objective
                        + "\n\nBinding Project Manager acceptance contract:\n"
                        + plan_contract_text
                        + "\n\nGoverned read-only repository context:\n"
                        + governed_context
                    )
                    editor_result = _run_aider_editor(
                        repository=workspace.path,  # type: ignore[arg-type]
                        objective=aider_objective,
                        allowed_paths=target_paths,
                        model=developer_route.model,
                        timeout_seconds=request.editor_timeout_seconds,
                        route=developer_route,
                        ledger=ai_ledger,
                        phase="implementation",
                    )

                    if not editor_result.changed_paths:
                        raise AIDeveloperFormatError(
                            "Aider editor returned no authorized changes"
                        )

                    generated_patch = {
                        "schema_version": "2.0",
                        "summary": (
                            "Aider reusable editor produced a bounded "
                            "full-file candidate set"
                        ),
                        "changes": [
                            {
                                "path": path,
                                "old_text": source_texts[path],
                                "new_text": editor_result.files[path],
                                "summary": (
                                    "Reusable Aider editor candidate"
                                ),
                            }
                            for path in editor_result.changed_paths
                        ],
                    }
                    editor_metadata.update({
                        "engine": "aider-cli",
                        "exit_status": editor_result.exit_status,
                        "timed_out": editor_result.timed_out,
                        "duration_ms": editor_result.duration_ms,
                        "changed_paths": list(
                            editor_result.changed_paths
                        ),
                    })
                else:
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
                            response_format=developer_schema,
                        )
                    )
                    generated_patch = (
                        _validate_ai_developer_patch(
                            developer_response.text,
                            target_paths,
                            source_texts,
                            require_all_paths=False,
                        )
                    )

                _validate_ai_developer_candidate_syntax(
                    generated_patch,
                    source_texts,
                )
            except (
                AIDeveloperFormatError,
                AIDeveloperReferenceError,
                AIDeveloperSyntaxError,
            ) as prewrite_error:
                prewrite_repair_attempts = 1
                format_repair_attempts = int(
                    isinstance(
                        prewrite_error,
                        AIDeveloperFormatError,
                    )
                )
                reference_repair_attempts = int(
                    isinstance(
                        prewrite_error,
                        AIDeveloperReferenceError,
                    )
                )
                syntax_repair_attempts = int(
                    isinstance(
                        prewrite_error,
                        AIDeveloperSyntaxError,
                    )
                )

                prewrite_recovery_context = {
                    "phase": "implementation",
                    "first_error": str(prewrite_error),
                }

                if request.editor_engine == "aider":
                    editor_metadata["fallback"] = (
                        "aider_prewrite_correction"
                    )
                    editor_metadata["aider_error"] = str(
                        prewrite_error
                    )

                    failed_candidate_context = "\n\n".join(
                        (
                            f"FILE {path}:\n"
                            + editor_result.files[path]
                        )
                        for path in editor_result.changed_paths
                    )

                    correction_objective = (
                        request.objective
                        + "\n\nBinding Project Manager acceptance contract:\n"
                        + plan_contract_text
                        + "\n\nYour first implementation candidate failed "
                        "ForgeLab deterministic pre-write validation. "
                        "Correct the candidate once while keeping the same "
                        "authorized scope and without weakening tests.\n"
                        + "Validation error:\n"
                        + str(prewrite_error)
                        + "\n\nFailed candidate content:\n"
                        + failed_candidate_context
                    )

                    reusable_editor_calls += 1

                    corrected_editor_result = _run_aider_editor(
                        repository=workspace.path,  # type: ignore[arg-type]
                        objective=correction_objective,
                        allowed_paths=target_paths,
                        model=developer_route.model,
                        timeout_seconds=request.editor_timeout_seconds,
                        route=developer_route,
                        ledger=ai_ledger,
                        phase="initial_prewrite_correction",
                    )

                    if not corrected_editor_result.changed_paths:
                        raise AIDeveloperFormatError(
                            "Aider initial pre-write correction returned "
                            "no authorized changes"
                        )

                    generated_patch = {
                        "schema_version": "2.0",
                        "summary": (
                            "Aider reusable editor corrected its initial "
                            "candidate after deterministic pre-write failure"
                        ),
                        "changes": [
                            {
                                "path": path,
                                "old_text": source_texts[path],
                                "new_text": corrected_editor_result.files[path],
                                "summary": (
                                    "Reusable Aider initial pre-write correction"
                                ),
                            }
                            for path in corrected_editor_result.changed_paths
                        ],
                    }

                    _validate_ai_developer_candidate_syntax(
                        generated_patch,
                        source_texts,
                    )

                    editor_metadata.update({
                        "prewrite_correction_engine": "aider-cli",
                        "prewrite_correction_exit_status":
                            corrected_editor_result.exit_status,
                        "prewrite_correction_timed_out":
                            corrected_editor_result.timed_out,
                        "prewrite_correction_duration_ms":
                            corrected_editor_result.duration_ms,
                        "prewrite_correction_changed_paths":
                            list(corrected_editor_result.changed_paths),
                    })
                else:
                    prewrite_repair_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

Your prior response failed deterministic pre-write
validation before any repository write occurred.

Validation error:
{prewrite_error}

Objective:
{request.objective}

Project Manager binding acceptance contract:
{plan_contract_text}

Authorized target paths:
{authorized_list}

Current complete authorized files:
{files_context}

Return ONLY one corrected JSON object.
No Markdown. No prose outside JSON.

Required schema:
{schema_instructions}

Rules:
- this is the ONE bounded pre-write repair attempt.
- every path MUST be one of the authorized target paths.
- authorized paths define the maximum write scope, not mandatory edits.
- return one or more changes only for files that actually need modification.
- never emit a no-op change: old_text and new_text must differ; omit
  any unchanged file or region instead.
- multiple changes may target the same file only when their old_text regions are disjoint.
- use at most 4 changes per authorized path.
- old_text MUST be copied verbatim from the current complete authorized file shown above.
- old_text MUST occur exactly once in its corresponding current file.
- do not reference text introduced only by a prior candidate or prior repair.
- choose the smallest sufficient replacement for each file.
- do not modify any other file.
- do not claim tests have run.
- do not create dependencies.
"""

                    full_file_recovery = isinstance(
                        prewrite_error,
                        (
                            AIDeveloperReferenceError,
                            AIDeveloperSyntaxError,
                        ),
                    )

                    if full_file_recovery:
                        recovery_mode = (
                            "REFERENCE RECOVERY MODE"
                            if isinstance(
                                prewrite_error,
                                AIDeveloperReferenceError,
                            )
                            else "SYNTAX RECOVERY MODE"
                        )
                        prewrite_repair_prompt += f"""

{recovery_mode}:
Return COMPLETE replacement content for each file that must
change. Do not return old_text snippets.

Required recovery schema:
{{
  "schema_version": "2.1",
  "summary": "<short overall recovery summary>",
  "files": [
    {{
      "path": "<one authorized path>",
      "new_text": "<COMPLETE replacement file content>",
      "summary": "<short per-file summary>"
    }}
  ]
}}

The current complete authorized files above are authoritative.
For Python files, return complete syntactically valid Python.
"""
                        prewrite_response_format = (
                            _ai_developer_full_file_response_schema(
                                target_paths
                            )
                        )
                    else:
                        prewrite_response_format = developer_schema

                    developer_response = ai_router.execute(
                        TaskClass.S2,
                        prewrite_repair_prompt,
                        "implement-prewrite-repair",
                        Role.DEVELOPER.value,
                        "Repair AI Developer pre-write validation once",
                        request.timeout_seconds,
                        response_format=prewrite_response_format,
                    )

                    if full_file_recovery:
                        generated_patch = (
                            _validate_ai_developer_full_file_patch(
                                developer_response.text,
                                target_paths,
                                source_texts,
                            )
                        )
                    else:
                        generated_patch = (
                            _validate_ai_developer_patch(
                                developer_response.text,
                                target_paths,
                                source_texts,
                                require_all_paths=False,
                            )
                        )

                    _validate_ai_developer_candidate_syntax(
                        generated_patch,
                        source_texts,
                    )

                prewrite_recovery_context = None

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
                "prewrite_repair_attempts":
                    prewrite_repair_attempts,
                "format_repair_attempts":
                    format_repair_attempts,
                "reference_repair_attempts":
                    reference_repair_attempts,
                "syntax_repair_attempts":
                    syntax_repair_attempts,
                "repair_attempts": [],
                "editor": editor_metadata,
                "chatgpt_assistance_in_target_product_run": 0,
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
        implementation_changed_paths = [
            item[0]
            for item in implementation_changes
        ]

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
                "Changed authorized path subset "
                f"{implementation_changed_paths} "
                "inside isolated workspace",
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
                changed=implementation_changed_paths,
            )
        )
        machine.transition(RunStatus.TESTING)
        while True:
            test = gateway.run_test(Role.TESTER, workspace.path, request.test_command, request.timeout_seconds)  # type: ignore[arg-type]
            ev_id = f"ev-test-{repair_attempts}"
            if regression_correction_retest_pending:
                ev_id += "-regression-correction"
                regression_correction_retest_pending = False

            evidence.append({
                "evidence_id": ev_id, "check_type": "tests", "command_or_tool": request.test_command,
                "exit_status": test.exit_status, "summary": "Tests passed" if test.exit_status == 0 else "Tests failed",
                "stdout": test.stdout[-4000:], "stderr": test.stderr[-4000:], "repair_attempt": repair_attempts,
            })
            current_test_outcomes = (
                _extract_deterministic_test_outcomes(
                    test.stdout,
                    test.stderr,
                )
            )

            if test.exit_status == 0:
                final_test_passed = True
                results.append(_result(store, "test", ResultStatus.PASS, "Acceptance tests passed", [ev_id], "Review patch"))
                break

            regressed_tests: list[str] = []

            if (
                request.operation == "ai_generate"
                and ai_router is not None
                and repair_regression_baseline is not None
                and repair_regression_snapshot is not None
                and repair_attempts
                == repair_regression_attempt_number
                and not repair_regression_correction_used
            ):
                regressed_tests = (
                    _regressed_passing_tests(
                        repair_regression_baseline,
                        current_test_outcomes,
                    )
                )

            if regressed_tests:
                regression_evidence_id = (
                    f"ev-repair-regression-{repair_attempts}"
                )
                evidence.append({
                    "evidence_id": regression_evidence_id,
                    "check_type": "repair_regression",
                    "command_or_tool": "deterministic_test_outcome_diff",
                    "exit_status": 1,
                    "repair_attempt": repair_attempts,
                    "summary": (
                        "Repair regressed previously passing tests: "
                        + ", ".join(regressed_tests)
                    ),
                    "regressed_tests": regressed_tests,
                    "before_test_evidence_ref":
                        repair_regression_evidence_ref,
                    "after_test_evidence_ref": ev_id,
                })

                machine.transition(RunStatus.DIAGNOSING)

                current_files = (
                    _read_ai_developer_targets(
                        workspace.path,  # type: ignore[arg-type]
                        target_paths,
                    )
                )

                for rollback_path in (
                    repair_regression_changed_paths
                ):
                    current_text = current_files[
                        rollback_path
                    ]
                    prior_text = repair_regression_snapshot[
                        rollback_path
                    ]

                    if current_text != prior_text:
                        gateway.edit_text(
                            Role.DEVELOPER,
                            workspace.path,  # type: ignore[arg-type]
                            authorized_paths,
                            rollback_path,
                            current_text,
                            prior_text,
                        )

                rollback_source_texts = (
                    _read_ai_developer_targets(
                        workspace.path,  # type: ignore[arg-type]
                        target_paths,
                    )
                )
                rollback_files_context = "\n\n".join(
                    (
                        f"--- BEGIN FILE {path} ---\n"
                        f"{rollback_source_texts[path]}\n"
                        f"--- END FILE {path} ---"
                    )
                    for path in target_paths
                )

                correction_id = (
                    f"repair-{repair_attempts}"
                    "-regression-correction"
                )

                correction_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

The single bounded repair attempt introduced a deterministic
regression. ForgeLab has rolled that repair back to the exact
candidate state that existed immediately before the repair.

This is the ONE bounded regression correction inside the same
repair attempt. It does not increase max_repair_attempts.

Objective:
{request.objective}

Project Manager binding acceptance contract:
{plan_contract_text}

Original failed-test evidence before the repair:
stdout:
{repair_regression_baseline_stdout[-2500:]}

stderr:
{repair_regression_baseline_stderr[-2500:]}

Previously passing tests that the repair regressed:
{chr(10).join(f"- {name}" for name in regressed_tests)}

Failed evidence after the regressing repair:
stdout:
{test.stdout[-2500:]}

stderr:
{test.stderr[-2500:]}

Current complete authorized files AFTER deterministic rollback:
{rollback_files_context}

Rules:
- preserve every previously passing test listed above.
- fix the original failing requirement without changing an established
  public return type, dictionary key, call signature, or passing
  semantic unless the Product Owner objective explicitly requires it.
- distinguish malformed/API-inconsistent test construction from a
  production-code defect before changing production code.
- preserve direct acceptance-test coverage for every binding criterion.
- do not weaken, delete, rename, or replace coverage merely to get green.
- quantitative criteria require direct quantitative tests.
- test names, setup, exercised API, and assertions must agree.
- return COMPLETE replacement content only for the authorized file
  subset that actually needs correction.
- do not modify dependencies or configuration.
- do not claim tests have run.

Return ONLY the required JSON object.
"""

                machine.transition(RunStatus.REPAIRING)

                task_defs.append(
                    _task(
                        run_id,
                        correction_id,
                        Role.DEVELOPER,
                        (
                            "Correct deterministic repair "
                            "regression once"
                        ),
                        target_paths,
                        ["repo_edit"],
                        [f"repair-{repair_attempts}"],
                    )
                )
                validate_task_graph(task_defs)

                correction_response = ai_router.execute(
                    TaskClass.S2,
                    correction_prompt,
                    correction_id,
                    Role.DEVELOPER.value,
                    "Correct regressing bounded repair once",
                    request.timeout_seconds,
                    response_format=(
                        _ai_developer_full_file_response_schema(
                            target_paths
                        )
                    ),
                )
                correction_route = ai_router.route(
                    TaskClass.S2
                )
                correction_error = ""
                correction_patch: dict[str, Any] | None = None

                try:
                    correction_patch = (
                        _validate_ai_developer_full_file_patch(
                            correction_response.text,
                            target_paths,
                            rollback_source_texts,
                        )
                    )
                    _validate_ai_developer_candidate_syntax(
                        correction_patch,
                        rollback_source_texts,
                    )

                    correction_payload_key = json.dumps(
                        correction_patch,
                        sort_keys=True,
                        ensure_ascii=False,
                    )

                    if (
                        correction_payload_key
                        in seen_repair_payloads
                    ):
                        raise ValueError(
                            "AI Developer repeated an identical "
                            "regression correction payload"
                        )

                    seen_repair_payloads.add(
                        correction_payload_key
                    )
                except ValueError as error:
                    correction_error = str(error)
                    correction_patch = None

                repair_regression_correction_used = True

                if correction_patch is not None:
                    correction_changes = _ai_patch_changes(
                        correction_patch
                    )
                    correction_changed_paths = [
                        item["path"]
                        for item in correction_changes
                    ]

                    for correction_change in (
                        correction_changes
                    ):
                        gateway.edit_text(
                            Role.DEVELOPER,
                            workspace.path,  # type: ignore[arg-type]
                            authorized_paths,
                            correction_change["path"],
                            correction_change["old_text"],
                            correction_change["new_text"],
                        )

                    _result(
                        store,
                        correction_id,
                        ResultStatus.PASS,
                        (
                            "Regressing repair rolled back and "
                            "corrected once"
                        ),
                        [
                            repair_regression_evidence_ref,
                            regression_evidence_id,
                        ],
                        "Rerun deterministic tests",
                        changed=correction_changed_paths,
                    )
                else:
                    correction_changed_paths = []
                    _result(
                        store,
                        correction_id,
                        ResultStatus.FAIL,
                        (
                            "Regression correction rejected "
                            f"before write: {correction_error}"
                        ),
                        [regression_evidence_id],
                        "Rerun rolled-back candidate tests",
                    )

                if (
                    ai_developer_artifact is not None
                    and ai_developer_artifact[
                        "repair_attempts"
                    ]
                ):
                    repair_record = (
                        ai_developer_artifact[
                            "repair_attempts"
                        ][-1]
                    )
                    repair_record[
                        "regression_correction_attempts"
                    ] = 1
                    repair_record[
                        "regressed_tests"
                    ] = regressed_tests
                    repair_record[
                        "regression_correction"
                    ] = {
                        "developer_task_id":
                            correction_id,
                        "provider":
                            correction_route.provider,
                        "model":
                            correction_route.model,
                        "changed_paths":
                            correction_changed_paths,
                        "patch":
                            correction_patch,
                        "validation_error":
                            correction_error or None,
                        "applied_by":
                            (
                                "deterministic_tool_gateway"
                                if correction_patch is not None
                                else None
                            ),
                    }
                    store.write_optional_json(
                        "AIDeveloperPatch.json",
                        ai_developer_artifact,
                    )

                regression_correction_retest_pending = True
                machine.transition(RunStatus.TESTING)
                continue

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

Diagnosis rules:
- distinguish a production-code defect from a malformed or
  API-inconsistent newly-added test;
- tests reported as "ok" in the same deterministic run are regression
  constraints that the repair should preserve unless they conflict
  explicitly with the Product Owner objective;
- preserve established public return types/shapes and semantics unless
  the objective explicitly requires changing them;
- prefer repairing the narrowest incorrect test or implementation
  assumption instead of redesigning a working public contract;
- do not weaken an acceptance requirement merely to obtain green tests.

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

Project Manager binding acceptance contract:
{plan_contract_text}

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
- treat every test shown as "ok" in the failed deterministic evidence
  as a regression constraint; the repair must preserve those behaviors
  unless they explicitly conflict with the Product Owner objective.
- distinguish an implementation defect from a malformed or
  API-inconsistent newly-added test before changing production code.
- preserve direct acceptance-test coverage for every testable binding
  criterion; do not repair one deterministic failure by deleting,
  weakening, renaming, or replacing coverage for another criterion.
- quantitative criteria must retain direct quantitative tests with the
  required distinct inputs/items and aggregate assertions.
- test names, setup, exercised API, and assertions must remain
  semantically aligned.
- preserve established public return types, dictionary keys, call
  signatures, and already-passing semantics unless the objective
  explicitly requires changing them.
- do not weaken tests merely to make them pass; correcting a malformed
  test is allowed only when it is inconsistent with the actual intended
  API or objective.
- before returning, mentally re-check the proposed repair against all
  previously passing tests plus the currently failing test.
- old_text MUST occur exactly once in the current corresponding file.
- choose the smallest sufficient repair.
- do not modify any other file.
- do not claim tests have run.
- do not create dependencies.
"""

                repair_id = f"repair-{repair_attempts + 1}"
                repair_route = ai_router.route(
                    TaskClass.S2
                )
                repair_prewrite_attempts = 0
                repair_engine = "custom"

                if request.editor_engine == "aider":
                    repair_engine = "aider-cli"
                    repair_aider_objective = (
                        request.objective
                        + "\n\nBinding Project Manager acceptance contract:\n"
                        + plan_contract_text
                        + "\n\nSupport diagnosis for failed deterministic test:\n"
                        + hypothesis
                        + "\n\nFailed test stdout:\n"
                        + test.stdout[-2500:]
                        + "\n\nFailed test stderr:\n"
                        + test.stderr[-2500:]
                        + "\n\nRepair the smallest complete cause of the "
                        "failed test while preserving all passing behavior, "
                        "the public API, quantitative acceptance coverage, "
                        "and the authorized file scope. Do not weaken tests."
                    )

                    def run_aider_repair(
                        objective: str,
                    ) -> dict[str, Any]:
                        nonlocal reusable_editor_calls
                        reusable_editor_calls += 1
                        editor_result = _run_aider_editor(
                            repository=workspace.path,  # type: ignore[arg-type]
                            objective=objective,
                            allowed_paths=target_paths,
                            model=repair_route.model,
                            timeout_seconds=request.editor_timeout_seconds,
                            route=repair_route,
                            ledger=ai_ledger,
                            phase="test_failure_repair",
                        )

                        if not editor_result.changed_paths:
                            raise AIDeveloperFormatError(
                                "Aider test-failure repair returned "
                                "no authorized changes"
                            )

                        candidate = {
                            "schema_version": "2.1",
                            "summary": (
                                "Aider reusable editor repaired failed "
                                "deterministic tests"
                            ),
                            "files": [
                                {
                                    "path": path,
                                    "new_text": editor_result.files[path],
                                    "summary": (
                                        "Reusable Aider test-failure repair"
                                    ),
                                }
                                for path in editor_result.changed_paths
                            ],
                        }

                        validated = (
                            _validate_ai_developer_full_file_patch(
                                json.dumps(
                                    candidate,
                                    ensure_ascii=False,
                                ),
                                target_paths,
                                repair_source_texts,
                            )
                        )
                        _validate_ai_developer_candidate_syntax(
                            validated,
                            repair_source_texts,
                        )
                        return validated

                    try:
                        repair_patch = run_aider_repair(
                            repair_aider_objective
                        )
                    except (
                        AIDeveloperFormatError,
                        AIDeveloperReferenceError,
                        AIDeveloperSyntaxError,
                    ) as repair_prewrite_error:
                        repair_prewrite_attempts = 1
                        prewrite_recovery_context = {
                            "phase": "test_failure_repair",
                            "first_error": str(
                                repair_prewrite_error
                            ),
                        }
                        correction_objective = (
                            repair_aider_objective
                            + "\n\nYour first repair candidate failed "
                            "ForgeLab deterministic pre-write validation. "
                            "Correct the candidate once without changing "
                            "scope or weakening tests.\n"
                            + "Validation error:\n"
                            + str(repair_prewrite_error)
                        )
                        repair_patch = run_aider_repair(
                            correction_objective
                        )
                        prewrite_recovery_context = None
                else:
                    repair_response = ai_router.execute(
                        TaskClass.S2,
                        repair_prompt,
                        repair_id,
                        Role.DEVELOPER.value,
                        "Generate bounded AI repair",
                        request.timeout_seconds,
                        response_format=(
                            _ai_developer_response_schema(
                                target_paths,
                                require_all_paths=False,
                            )
                        ),
                    )

                    try:
                        repair_patch = (
                            _validate_ai_developer_patch(
                                repair_response.text,
                                target_paths,
                                repair_source_texts,
                                require_all_paths=False,
                            )
                        )
                        _validate_ai_developer_candidate_syntax(
                            repair_patch,
                            repair_source_texts,
                        )
                    except (
                        AIDeveloperFormatError,
                        AIDeveloperReferenceError,
                        AIDeveloperSyntaxError,
                    ) as repair_prewrite_error:
                        repair_prewrite_attempts = 1

                        repair_prewrite_prompt = f"""
    You are the DEVELOPER agent in ForgeLab.

    Your prior test-failure repair candidate failed deterministic
    pre-write validation before any repair write occurred.

    Validation error:
    {repair_prewrite_error}

    Objective:
    {request.objective}

    Project Manager binding acceptance contract:
    {plan_contract_text}

    Original authorized paths (scope is immutable):
    {repair_authorized_list}

    Support hypothesis for {ev_id}:
    {hypothesis}

    Failed test stdout:
    {test.stdout[-2500:]}

    Failed test stderr:
    {test.stderr[-2500:]}

    Current complete authorized files AFTER the failed candidate:
    {repair_files_context}

    Return ONLY one corrected JSON object.
    No Markdown. No prose outside JSON.

    Required schema:
    {repair_schema}

    Rules:
    - this is the ONE bounded pre-write correction for this repair candidate.
    - every path MUST remain inside the ORIGINAL authorized path set.
    - repair only the non-empty subset actually needed.
    - multiple changes may target the same file only when their old_text regions are disjoint.
    - use at most 4 changes per authorized path.
    - old_text MUST be copied verbatim from the current corresponding file.
    - old_text MUST occur exactly once.
    - preserve valid Python syntax in every modified .py file.
    - preserve tests already reported as "ok" in the failed deterministic
      evidence and preserve the public API contract they exercise unless
      the Product Owner objective explicitly requires a breaking change.
    - distinguish malformed test construction from production-code defects;
      do not redesign a working return type just to satisfy an inconsistent
      test.
    - do not weaken tests merely to make them pass.
    - do not modify dependencies or configuration.
    - do not claim tests have run.
    """

                        repair_full_file_recovery = isinstance(
                            repair_prewrite_error,
                            (
                                AIDeveloperReferenceError,
                                AIDeveloperSyntaxError,
                            ),
                        )

                        if repair_full_file_recovery:
                            repair_recovery_mode = (
                                "REFERENCE RECOVERY MODE"
                                if isinstance(
                                    repair_prewrite_error,
                                    AIDeveloperReferenceError,
                                )
                                else "SYNTAX RECOVERY MODE"
                            )
                            repair_prewrite_prompt += f"""

    {repair_recovery_mode}:
    Return COMPLETE replacement content for each file that must
    change. Do not return old_text snippets.

    Required recovery schema:
    {{
      "schema_version": "2.1",
      "summary": "<short overall recovery summary>",
      "files": [
        {{
          "path": "<one authorized path>",
          "new_text": "<COMPLETE replacement file content>",
          "summary": "<short per-file summary>"
        }}
      ]
    }}

    The current complete authorized files above are authoritative.
    For Python files, return complete syntactically valid Python.
    """
                            repair_response_format = (
                                _ai_developer_full_file_response_schema(
                                    target_paths
                                )
                            )
                        else:
                            repair_response_format = (
                                _ai_developer_response_schema(
                                    target_paths,
                                    require_all_paths=False,
                                )
                            )

                        prewrite_recovery_context = {
                            "phase": "test_failure_repair",
                            "first_error": str(
                                repair_prewrite_error
                            ),
                        }

                        repair_response = ai_router.execute(
                            TaskClass.S2,
                            repair_prewrite_prompt,
                            f"{repair_id}-prewrite",
                            Role.DEVELOPER.value,
                            "Correct repair pre-write validation once",
                            request.timeout_seconds,
                            response_format=repair_response_format,
                        )

                        if repair_full_file_recovery:
                            repair_patch = (
                                _validate_ai_developer_full_file_patch(
                                    repair_response.text,
                                    target_paths,
                                    repair_source_texts,
                                )
                            )
                        else:
                            repair_patch = (
                                _validate_ai_developer_patch(
                                    repair_response.text,
                                    target_paths,
                                    repair_source_texts,
                                    require_all_paths=False,
                                )
                            )

                        _validate_ai_developer_candidate_syntax(
                            repair_patch,
                            repair_source_texts,
                        )
                        prewrite_recovery_context = None


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

                repair_regression_baseline = dict(
                    current_test_outcomes
                )
                repair_regression_baseline_stdout = (
                    test.stdout
                )
                repair_regression_baseline_stderr = (
                    test.stderr
                )
                repair_regression_snapshot = dict(
                    repair_source_texts
                )
                repair_regression_changed_paths = list(
                    repair_changed_paths
                )
                repair_regression_correction_used = False
                repair_regression_attempt_number = (
                    repair_attempts + 1
                )
                repair_regression_evidence_ref = ev_id

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
                    "provider": (
                        "aider-cli"
                        if repair_engine == "aider-cli"
                        else repair_route.provider
                    ),
                    "model": repair_route.model,
                    "editor_engine": repair_engine,
                    "chatgpt_assistance_in_target_product_run": 0,
                    "changed_paths": repair_changed_paths,
                    "patch": repair_patch,
                    "prewrite_correction_attempts":
                        repair_prewrite_attempts,
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
            review_round = 0

            while final_test_passed:
                machine.transition(
                    RunStatus.SMOKE_TEST
                )

                diff = workspace.diff()

                store.write_text(
                    "Changes.patch",
                    diff,
                )

                diff_evidence_id = (
                    f"ev-diff-{review_round}"
                )

                evidence.append({
                    "evidence_id":
                        diff_evidence_id,
                    "check_type":
                        "scope",
                    "command_or_tool":
                        "git diff",
                    "exit_status":
                        0,
                    "summary":
                        "Patch captured",
                    "artifact_ref":
                        "Changes.patch",
                })

                machine.transition(
                    RunStatus.REVIEW
                )

                deterministic_review = (
                    review_patch(
                        diff,
                        set(target_paths),
                    )
                )

                semantic_review: (
                    dict[str, Any] | None
                ) = None

                if ai_router is not None:
                    review_source_texts = (
                        _read_ai_developer_targets(
                            workspace.path,  # type: ignore[arg-type]
                            target_paths,
                        )
                    )
                    review_files_context = "\n\n".join(
                        (
                            f"--- BEGIN CANDIDATE FILE {path} ---\n"
                            f"{review_source_texts[path]}\n"
                            f"--- END CANDIDATE FILE {path} ---"
                        )
                        for path in target_paths
                    )

                    review_prompt = f"""
You are the REVIEWER agent in ForgeLab.

Review this already-generated patch against the full
Product Owner objective. This review is a blocking quality
gate, not advisory prose.

Objective:
{request.objective}

Binding Product Owner acceptance contract:
{plan_contract_text}

{('The editor returned an unchanged candidate. Independently reconsider every obligation against the current files; a no-op is not approval.' if semantic_noop is not None else '')}

Allowed targets:
{chr(10).join(f"- {path}" for path in target_paths)}

Current complete authorized candidate files:
{review_files_context}

Latest deterministic test evidence:
stdout:
{test.stdout[-2500:]}

stderr:
{test.stderr[-2500:]}

Instructions:
- requirements[] must describe only obligations from the Objective and
  binding acceptance contract above; these review instructions are not
  product requirements;
- decompose the objective into EVERY explicit obligation;
- include one requirements[] entry for each obligation;
- preserve quantitative requirements such as exact counts,
  "three", "each", "all", percentages, validation, and tests;
- mark SATISFIED only when the candidate files and test
  evidence contain direct support for the complete requirement;
- evaluate user-visible requirements end-to-end through the
  existing interface or entry point when one is present;
- helper/backend logic without required interface integration is
  PARTIAL, not MISSING;
- use PARTIAL whenever relevant implementation or tests exist but do
  not yet satisfy the complete requirement; use MISSING only when no
  relevant implementation/test evidence exists at all;
- before marking MISSING, search the complete candidate files for
  related functions, methods, fields, UI controls, and tests and cite
  any partial evidence instead of denying its existence;
- a passing test suite does NOT satisfy an objective requirement
  that the tests do not cover;
- a test satisfies a requirement only when its setup, exercised API,
  and assertions directly test that requirement; misleading test names
  or unrelated assertions are not acceptance evidence;
- quantitative requirements such as exact counts must have direct
  quantitative evidence in implementation and tests.
- if tests or partial implementation are present but insufficient,
  acknowledge that evidence precisely and describe the remaining
  gap; do not claim required behavior or tests are absent when the
  candidate files directly show them;
- mark missing or insufficiently evidenced behavior as MISSING
  or UNVERIFIED and set overall status FAIL;
- use BLOCKER findings for missing required behavior;
- do not approve promotion.

Return ONLY the required JSON object.
"""

                    ai_review_response = (
                        ai_router.execute(
                            TaskClass.S1,
                            review_prompt,
                            f"review-{review_round}",
                            Role.REVIEWER.value,
                            "Blocking AI semantic review",
                            request.timeout_seconds,
                            response_format=(
                                _ai_review_response_schema()
                            ),
                        )
                    )

                    review_route = (
                        ai_router.route(
                            TaskClass.S1
                        )
                    )

                    semantic_review = (
                        _validate_ai_review(
                            ai_review_response.text
                        )
                    )

                    semantic_review_history.append({
                        "round":
                            review_round,
                        **semantic_review,
                    })

                    store.write_optional_json(
                        "AIReview.json",
                        {
                            "role":
                                Role.REVIEWER.value,
                            "provider":
                                review_route.provider,
                            "model":
                                review_route.model,
                            **semantic_review,
                            "attempts":
                                semantic_review_history,
                        },
                    )

                combined_findings = list(
                    deterministic_review[
                        "findings"
                    ]
                )

                if semantic_review is not None:
                    combined_findings.extend(
                        semantic_review[
                            "findings"
                        ]
                    )

                semantic_status = (
                    semantic_review["status"]
                    if semantic_review is not None
                    else "NOT_RUN"
                )

                review_status = (
                    "PASS"
                    if (
                        deterministic_review[
                            "status"
                        ] == "PASS"
                        and (
                            semantic_review is None
                            or semantic_status
                            == "PASS"
                        )
                    )
                    else "FAIL"
                )

                review_report = {
                    "status":
                        review_status,
                    "changed_paths":
                        deterministic_review[
                            "changed_paths"
                        ],
                    "findings":
                        combined_findings,
                    "deterministic_status":
                        deterministic_review[
                            "status"
                        ],
                    "semantic_status":
                        semantic_status,
                    "semantic_requirements":
                        (
                            semantic_review[
                                "requirements"
                            ]
                            if semantic_review
                            is not None
                            else []
                        ),
                    "semantic_summary":
                        (
                            semantic_review[
                                "summary"
                            ]
                            if semantic_review
                            is not None
                            else ""
                        ),
                    "review_round":
                        review_round,
                }

                if semantic_noop is not None:
                    semantic_noop.update({
                        "status": review_status,
                        "reconsideration_status": review_status,
                        "reconsideration_review_round": review_round,
                        "reconsideration_requirements": review_report["semantic_requirements"],
                        "final_error": ("" if review_status == "PASS" else
                                        "Aider returned no authorized changes and independent review remains blocking"),
                    })
                    store.write_optional_json("SemanticRepairNoop.json", semantic_noop)
                    if review_status != "PASS":
                        results.append(_result(
                            store, "review", ResultStatus.FAIL,
                            "SEMANTIC_REPAIR_NOOP: unchanged candidate remains blocked by independent review",
                            ["ev-semantic-repair-noop", diff_evidence_id], "Human repair required", combined_findings,
                        ))
                        _result(store, semantic_noop["developer_task_id"], ResultStatus.FAIL,
                                "Semantic repair made no changes; candidate remains blocked",
                                ["ev-semantic-repair-noop"], "Human repair required")
                        machine.transition(RunStatus.CLOSED)
                        break

                if review_status == "PASS":
                    results.append(
                        _result(
                            store,
                            "review",
                            ResultStatus.PASS,
                            (
                                "Deterministic and semantic "
                                "review passed"
                                if semantic_review
                                is not None
                                else (
                                    "Independent deterministic "
                                    "review completed"
                                )
                            ),
                            [diff_evidence_id],
                            "Run security policy",
                            combined_findings,
                        )
                    )
                    break

                semantic_repair_available = (
                    semantic_review is not None
                    and semantic_status == "FAIL"
                    and deterministic_review[
                        "status"
                    ] == "PASS"
                    and request.operation
                    == "ai_generate"
                    and repair_attempts
                    < request.max_repair_attempts
                )

                latest_semantic_repair_record = None
                if (
                    ai_developer_artifact is not None
                    and ai_developer_artifact[
                        "repair_attempts"
                    ]
                ):
                    candidate_repair_record = (
                        ai_developer_artifact[
                            "repair_attempts"
                        ][-1]
                    )
                    if (
                        candidate_repair_record.get(
                            "cause"
                        )
                        == "semantic_review"
                    ):
                        latest_semantic_repair_record = (
                            candidate_repair_record
                        )

                semantic_rereview_correction_available = (
                    not semantic_repair_available
                    and semantic_review is not None
                    and semantic_status == "FAIL"
                    and deterministic_review[
                        "status"
                    ] == "PASS"
                    and request.operation
                    == "ai_generate"
                    and latest_semantic_repair_record
                    is not None
                    and latest_semantic_repair_record.get(
                        "semantic_review_correction_attempts",
                        0,
                    )
                    < 1
                )

                if semantic_rereview_correction_available:
                    machine.transition(
                        RunStatus.REPAIRING
                    )

                    semantic_review_correction_id = (
                        f"review-repair-{repair_attempts}"
                        "-semantic-correction"
                    )
                    semantic_review_correction_source_texts = (
                        _read_ai_developer_targets(
                            workspace.path,  # type: ignore[arg-type]
                            target_paths,
                        )
                    )
                    semantic_review_correction_files = (
                        "\n\n".join(
                            (
                                f"--- BEGIN FILE {path} ---\n"
                                f"{semantic_review_correction_source_texts[path]}\n"
                                f"--- END FILE {path} ---"
                            )
                            for path in target_paths
                        )
                    )

                    semantic_review_correction_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

The single top-level semantic-review repair has already been used and
its deterministic tests PASS, but independent semantic re-review still
FAILS the Product Owner objective.

This is the ONE bounded semantic correction inside the SAME top-level
repair attempt. It does NOT increase max_repair_attempts.

Original objective:
{request.objective}

Project Manager binding acceptance contract:
{plan_contract_text}

Latest blocking semantic re-review:
{json.dumps(semantic_review, indent=2, ensure_ascii=False)}

Latest deterministic test evidence:
stdout:
{test.stdout[-2500:]}

stderr:
{test.stderr[-2500:]}

Current complete authorized files:
{semantic_review_correction_files}

Rules:
- resolve every latest MISSING, PARTIAL, or UNVERIFIED objective
  obligation that is actually supported by the objective and current
  repository context;
- inspect the complete current files before acting on Reviewer wording;
  if the Reviewer describes present behavior as absent, preserve that
  behavior and repair the real remaining gap rather than deleting or
  duplicating working code;
- preserve all currently passing deterministic tests and established
  public contracts unless the Product Owner objective explicitly
  requires a breaking change;
- do not satisfy semantic review by weakening, deleting, bypassing, or
  trivializing acceptance tests;
- quantitative requirements such as exact counts require direct
  implementation and direct quantitative test evidence;
- user-visible requirements must be wired through the existing
  interface or entry point when one exists;
- prefer the smallest coherent end-to-end repair over helper-only
  additions;
- return COMPLETE replacement content only for the authorized file
  subset that actually needs correction;
- for Python files, return complete syntactically valid Python;
- do not modify dependencies or configuration;
- do not claim tests have run.

Return ONLY the required JSON object.
Output contract: {json.dumps(_ai_developer_full_file_response_schema(target_paths))}
Return schema_version "2.1", summary, and files with path, new_text,
summary. new_text must contain complete replacement source, not a diff.
"""

                    task_defs.append(
                        _task(
                            run_id,
                            semantic_review_correction_id,
                            Role.DEVELOPER,
                            (
                                "Correct remaining semantic "
                                "re-review findings once"
                            ),
                            target_paths,
                            ["repo_edit"],
                            [
                                latest_semantic_repair_record[
                                    "developer_task_id"
                                ]
                            ],
                        )
                    )
                    validate_task_graph(
                        task_defs
                    )

                    semantic_review_correction_response = (
                        ai_router.execute(
                            TaskClass.S2,
                            semantic_review_correction_prompt,
                            semantic_review_correction_id,
                            Role.DEVELOPER.value,
                            (
                                "Correct remaining semantic "
                                "review findings once"
                            ),
                            request.timeout_seconds,
                            response_format=(
                                _ai_developer_full_file_response_schema(
                                    target_paths
                                )
                            ),
                        )
                    )
                    semantic_review_correction_route = (
                        ai_router.route(
                            TaskClass.S2
                        )
                    )

                    semantic_review_correction_patch: (
                        dict[str, Any] | None
                    ) = None
                    semantic_review_correction_error = ""

                    try:
                        semantic_review_correction_patch = (
                            _validate_ai_developer_full_file_patch(
                                semantic_review_correction_response.text,
                                target_paths,
                                semantic_review_correction_source_texts,
                            )
                        )
                        _validate_ai_developer_candidate_syntax(
                            semantic_review_correction_patch,
                            semantic_review_correction_source_texts,
                        )
                    except ValueError as error:
                        semantic_review_correction_error = str(
                            error
                        )
                        semantic_review_correction_patch = None

                    latest_semantic_repair_record[
                        "semantic_review_correction_attempts"
                    ] = 1

                    if semantic_review_correction_patch is None:
                        latest_semantic_repair_record[
                            "semantic_review_correction"
                        ] = {
                            "developer_task_id":
                                semantic_review_correction_id,
                            "provider":
                                semantic_review_correction_route.provider,
                            "model":
                                semantic_review_correction_route.model,
                            "changed_paths": [],
                            "patch": None,
                            "validation_error":
                                semantic_review_correction_error,
                            "applied_by": None,
                        }
                        store.write_optional_json(
                            "AIDeveloperPatch.json",
                            ai_developer_artifact,
                        )
                        evidence.append({
                            "evidence_id":
                                (
                                    "ev-semantic-review-correction-"
                                    f"{repair_attempts}"
                                ),
                            "check_type":
                                "semantic_review_correction",
                            "command_or_tool":
                                (
                                    "ai_generate+"
                                    "deterministic_prewrite_validation"
                                ),
                            "exit_status":
                                1,
                            "repair_attempt":
                                repair_attempts,
                            "summary":
                                (
                                    "Semantic re-review correction "
                                    "rejected before write: "
                                    + semantic_review_correction_error
                                ),
                        })
                        results.append(
                            _result(
                                store,
                                semantic_review_correction_id,
                                ResultStatus.FAIL,
                                (
                                    "Semantic re-review correction "
                                    "rejected before write"
                                ),
                                [diff_evidence_id],
                                "Human repair required",
                            )
                        )
                        machine.transition(
                            RunStatus.CLOSED
                        )
                        break

                    semantic_review_correction_changes = (
                        _ai_patch_changes(
                            semantic_review_correction_patch
                        )
                    )
                    semantic_review_correction_changed_paths = [
                        item["path"]
                        for item in
                        semantic_review_correction_changes
                    ]

                    for semantic_review_correction_change in (
                        semantic_review_correction_changes
                    ):
                        gateway.edit_text(
                            Role.DEVELOPER,
                            workspace.path,  # type: ignore[arg-type]
                            authorized_paths,
                            semantic_review_correction_change[
                                "path"
                            ],
                            semantic_review_correction_change[
                                "old_text"
                            ],
                            semantic_review_correction_change[
                                "new_text"
                            ],
                        )

                    latest_semantic_repair_record[
                        "semantic_review_correction"
                    ] = {
                        "developer_task_id":
                            semantic_review_correction_id,
                        "provider":
                            semantic_review_correction_route.provider,
                        "model":
                            semantic_review_correction_route.model,
                        "changed_paths":
                            semantic_review_correction_changed_paths,
                        "patch":
                            semantic_review_correction_patch,
                        "validation_error": None,
                        "applied_by":
                            "deterministic_tool_gateway",
                    }
                    store.write_optional_json(
                        "AIDeveloperPatch.json",
                        ai_developer_artifact,
                    )

                    results.append(
                        _result(
                            store,
                            semantic_review_correction_id,
                            ResultStatus.PASS,
                            (
                                "Remaining semantic re-review "
                                "findings corrected once"
                            ),
                            [diff_evidence_id],
                            "Rerun deterministic tests",
                            changed=(
                                semantic_review_correction_changed_paths
                            ),
                        )
                    )

                    diff = workspace.diff()
                    semantic_review_correction_diff_id = (
                        "ev-diff-semantic-review-correction-"
                        f"{repair_attempts}"
                    )
                    store.write_text(
                        "Changes.patch",
                        diff,
                    )
                    evidence.append({
                        "evidence_id":
                            semantic_review_correction_diff_id,
                        "check_type":
                            "scope",
                        "command_or_tool":
                            "git diff",
                        "exit_status":
                            0,
                        "summary":
                            (
                                "Patch refreshed after semantic "
                                "re-review correction"
                            ),
                        "artifact_ref":
                            "Changes.patch",
                        "repair_attempt":
                            repair_attempts,
                        "repair_cause":
                            (
                                "semantic_review_"
                                "rereview_correction"
                            ),
                    })

                    machine.transition(
                        RunStatus.TESTING
                    )
                    test = gateway.run_test(
                        Role.TESTER,
                        workspace.path,  # type: ignore[arg-type]
                        request.test_command,
                        request.timeout_seconds,
                    )
                    semantic_review_correction_test_id = (
                        f"ev-test-{repair_attempts}"
                        "-semantic-review-correction"
                    )
                    evidence.append({
                        "evidence_id":
                            semantic_review_correction_test_id,
                        "check_type":
                            "tests",
                        "command_or_tool":
                            request.test_command,
                        "exit_status":
                            test.exit_status,
                        "summary":
                            (
                                "Tests passed"
                                if test.exit_status == 0
                                else "Tests failed"
                            ),
                        "stdout":
                            test.stdout[-4000:],
                        "stderr":
                            test.stderr[-4000:],
                        "repair_attempt":
                            repair_attempts,
                        "repair_cause":
                            (
                                "semantic_review_"
                                "rereview_correction"
                            ),
                    })

                    if test.exit_status != 0:
                        final_test_passed = False
                        results.append(
                            _result(
                                store,
                                "test",
                                ResultStatus.FAIL,
                                (
                                    "Tests failed after one "
                                    "semantic re-review correction"
                                ),
                                [
                                    semantic_review_correction_test_id
                                ],
                                "Human repair required",
                            )
                        )
                        machine.transition(
                            RunStatus.DIAGNOSING
                        )
                        break

                    final_test_passed = True
                    results.append(
                        _result(
                            store,
                            "test",
                            ResultStatus.PASS,
                            (
                                "Acceptance tests passed after "
                                "semantic re-review correction"
                            ),
                            [
                                semantic_review_correction_test_id
                            ],
                            "Re-run semantic review",
                        )
                    )
                    review_round += 1
                    continue

                if not semantic_repair_available:
                    results.append(
                        _result(
                            store,
                            "review",
                            ResultStatus.FAIL,
                            (
                                "Semantic objective coverage "
                                "review failed"
                                if semantic_review
                                is not None
                                else (
                                    "Independent deterministic "
                                    "review failed"
                                )
                            ),
                            [diff_evidence_id],
                            "Human repair required",
                            combined_findings,
                        )
                    )
                    break

                machine.transition(
                    RunStatus.REPAIRING
                )

                semantic_repair_source_texts = (
                    _read_ai_developer_targets(
                        workspace.path,  # type: ignore[arg-type]
                        target_paths,
                    )
                )

                semantic_repair_files = (
                    "\n\n".join(
                        (
                            f"--- BEGIN FILE {path} ---\n"
                            f"{semantic_repair_source_texts[path]}\n"
                            f"--- END FILE {path} ---"
                        )
                        for path in target_paths
                    )
                )

                semantic_repair_id = (
                    f"review-repair-"
                    f"{repair_attempts + 1}"
                )
                semantic_pre_repair_test_stdout = (
                    test.stdout
                )
                semantic_pre_repair_test_stderr = (
                    test.stderr
                )

                semantic_repair_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

The candidate passed deterministic tests but FAILED the
independent semantic objective-coverage review.

Original objective:
{request.objective}

Project Manager binding acceptance contract:
{plan_contract_text}

Original authorized paths (scope is immutable):
{chr(10).join(f"- {path}" for path in target_paths)}

Blocking semantic review:
{json.dumps(semantic_review, indent=2, ensure_ascii=False)}

Current complete authorized files AFTER the candidate:
{semantic_repair_files}

Current full candidate diff:
{diff[-8000:]}

Generate the smallest coherent repair that resolves every MISSING,
PARTIAL, or UNVERIFIED required behavior identified by the Reviewer
and supported by the Product Owner objective.

FULL-FILE SEMANTIC REPAIR MODE:
Return COMPLETE replacement content only for each authorized file
that actually needs to change. Do not return old_text snippets.

Rules:
- every returned path MUST stay inside the ORIGINAL authorized path set;
- repair only the non-empty subset actually needed;
- omit unchanged files;
- inspect the complete current files before acting on Reviewer wording;
- preserve valid existing behavior instead of duplicating it;
- do not weaken or delete valid tests merely to make them pass;
- add or strengthen tests when the review identifies missing
  required behavior or missing objective coverage;
- quantitative requirements require direct quantitative behavior
  and direct quantitative test evidence;
- user-visible requirements must be wired through the existing
  interface or entry point when one exists;
- for Python files, return complete syntactically valid Python;
- do not modify dependencies or configuration unless the
  original objective explicitly requires it;
- do not claim tests have run.

Return ONLY the required structured JSON object.
"""

                semantic_repair_route = (
                    ai_router.route(
                        TaskClass.S2
                    )
                )

                semantic_prewrite_attempts = 0
                semantic_repair_engine = "custom"

                if request.editor_engine == "aider":
                    reusable_editor_calls += 1
                    semantic_repair_engine = "aider-cli"
                    semantic_aider_objective = (
                        request.objective
                        + "\n\nBinding Project Manager acceptance contract:\n"
                        + plan_contract_text
                        + "\n\nBlocking semantic review:\n"
                        + json.dumps(
                            semantic_review,
                            indent=2,
                            ensure_ascii=False,
                        )
                        + "\n\nRepair every blocking requirement while "
                        "preserving passing tests and unrelated behavior. "
                        "Stay inside the authorized files."
                    )
                    semantic_editor_result = _run_aider_editor(
                        repository=workspace.path,  # type: ignore[arg-type]
                        objective=semantic_aider_objective,
                        allowed_paths=target_paths,
                        model=semantic_repair_route.model,
                        timeout_seconds=request.editor_timeout_seconds,
                        route=semantic_repair_route,
                        ledger=ai_ledger,
                        phase="semantic_review_repair",
                    )

                    if not semantic_editor_result.changed_paths:
                        if semantic_editor_result.files != semantic_repair_source_texts:
                            raise AIEditorExecutionError("semantic_review_repair",
                                                         "Editor reported no changes but candidate file evidence differs")
                        repair_attempts += 1
                        semantic_noop = {
                            "run_id": run_id, "status": "PENDING", "reason": "SEMANTIC_REPAIR_NOOP",
                            "phase": "semantic_review_repair", "attempt": repair_attempts,
                            "review_round": review_round, "developer_task_id": semantic_repair_id,
                            "objective": semantic_aider_objective,
                            "blocking_review": semantic_review, "changed_paths": [],
                            "before_sha256": {path: hashlib.sha256(text.encode("utf-8")).hexdigest()
                                              for path, text in semantic_repair_source_texts.items()},
                            "after_sha256": {path: hashlib.sha256(text.encode("utf-8")).hexdigest()
                                             for path, text in semantic_editor_result.files.items()},
                            "stdout": semantic_editor_result.stdout, "stderr": semantic_editor_result.stderr,
                            "exit_status": semantic_editor_result.exit_status,
                            "timed_out": semantic_editor_result.timed_out,
                            "duration_ms": semantic_editor_result.duration_ms,
                            "prewrite_repair_attempts": 0, "candidate_write_performed": False,
                            "final_error": "Aider returned no authorized changes; independent reconsideration required",
                        }
                        store.write_optional_json("SemanticRepairNoop.json", semantic_noop)
                        if ai_developer_artifact is None:
                            raise RuntimeError("AI Developer artifact missing before semantic no-op")
                        ai_developer_artifact["repair_attempts"].append({
                            "attempt": repair_attempts, "cause": "semantic_review", "outcome": "NO_OP",
                            "review_round": review_round, "developer_task_id": semantic_repair_id,
                            "editor_engine": "aider-cli", "provider": "aider-cli",
                            "model": semantic_repair_route.model, "changed_paths": [],
                            "prewrite_repair_attempts": 0, "applied_by": "none",
                            "patch": {"schema_version": "2.1", "summary": "No patch applied", "files": []},
                            "evidence_ref": "SemanticRepairNoop.json",
                        })
                        store.write_optional_json("AIDeveloperPatch.json", ai_developer_artifact)
                        evidence.append({
                            "evidence_id": "ev-semantic-repair-noop", "check_type": "semantic_repair",
                            "command_or_tool": "aider", "exit_status": 0, "repair_attempt": repair_attempts,
                            "summary": "No candidate writes; reuse unchanged passing tests and reconsider review once",
                            "artifact_ref": "SemanticRepairNoop.json",
                        })
                        task_defs.append(_task(run_id, semantic_repair_id, Role.DEVELOPER,
                                               "Reconsider unchanged candidate after semantic repair no-op",
                                               target_paths, ["repo_edit"], ["review"]))
                        validate_task_graph(task_defs)
                        _result(store, semantic_repair_id, ResultStatus.PASS,
                                "Editor returned no changes; objective acceptance still requires independent review",
                                ["ev-semantic-repair-noop"], "Re-run semantic review")
                        # Content is identical: the existing deterministic test evidence remains valid.
                        machine.transition(RunStatus.TESTING)
                        review_round += 1
                        continue

                    semantic_repair_patch = {
                        "schema_version": "2.1",
                        "summary": (
                            "Aider reusable editor repaired blocking "
                            "semantic review findings"
                        ),
                        "files": [
                            {
                                "path": path,
                                "new_text": semantic_editor_result.files[path],
                                "summary": "Reusable Aider semantic repair",
                            }
                            for path in semantic_editor_result.changed_paths
                        ],
                    }
                    semantic_repair_patch = (
                        _validate_ai_developer_full_file_patch(
                            json.dumps(
                                semantic_repair_patch,
                                ensure_ascii=False,
                            ),
                            target_paths,
                            semantic_repair_source_texts,
                        )
                    )
                    _validate_ai_developer_candidate_syntax(
                        semantic_repair_patch,
                        semantic_repair_source_texts,
                    )
                else:
                    semantic_repair_response = (
                        ai_router.execute(
                            TaskClass.S2,
                            semantic_repair_prompt,
                            semantic_repair_id,
                            Role.DEVELOPER.value,
                            (
                                "Repair blocking semantic "
                                "review findings"
                            ),
                            request.timeout_seconds,
                            response_format=(
                                _ai_developer_full_file_response_schema(
                                    target_paths
                                )
                            ),
                        )
                    )

                    try:
                        semantic_repair_patch = (
                            _validate_ai_developer_full_file_patch(
                                semantic_repair_response.text,
                                target_paths,
                                semantic_repair_source_texts,
                            )
                        )
                        _validate_ai_developer_candidate_syntax(
                            semantic_repair_patch,
                            semantic_repair_source_texts,
                        )
                    except (
                        AIDeveloperFormatError,
                        AIDeveloperReferenceError,
                        AIDeveloperSyntaxError,
                    ) as semantic_prewrite_error:
                        semantic_prewrite_attempts = 1

                        semantic_prewrite_prompt = f"""
    You are the DEVELOPER agent in ForgeLab.

    Your semantic-review repair failed deterministic pre-write
    validation before any repository write occurred.

    Validation error:
    {semantic_prewrite_error}

    Original objective:
    {request.objective}

    Project Manager binding acceptance contract:
    {plan_contract_text}

    Blocking semantic review:
    {json.dumps(semantic_review, indent=2, ensure_ascii=False)}

    Original authorized paths:
    {chr(10).join(f"- {path}" for path in target_paths)}

    Current complete authorized files:
    {semantic_repair_files}

    Return ONLY one corrected structured JSON object.

    Rules:
    - this is the ONE bounded pre-write correction for this repair;
    - stay inside the original authorized path set;
    - repair only the non-empty subset actually needed;
    - multiple changes may target the same file only when their old_text regions are disjoint;
    - use at most 4 changes per authorized path;
    - old_text MUST be copied verbatim from the current file;
    - old_text MUST occur exactly once;
    - do not reference text from an earlier candidate state;
    - do not weaken tests;
    - do not modify dependencies or configuration.
    """

                        semantic_prewrite_prompt += """
                            
    FULL-FILE SEMANTIC REPAIR RECOVERY MODE:
    Return COMPLETE replacement content only for each authorized file
    that actually needs to change. Do not return old_text snippets.

    Required recovery schema:
    {
      "schema_version": "2.1",
      "summary": "<short overall recovery summary>",
      "files": [
        {
          "path": "<one authorized path>",
          "new_text": "<COMPLETE replacement file content>",
          "summary": "<short per-file summary>"
        }
      ]
    }

    The current complete authorized files above are authoritative.
    For Python files, return complete syntactically valid Python.
    """
                        semantic_response_format = (
                            _ai_developer_full_file_response_schema(
                                target_paths
                            )
                        )

                        prewrite_recovery_context = {
                            "phase": "semantic_review_repair",
                            "first_error": str(
                                semantic_prewrite_error
                            ),
                        }

                        semantic_repair_response = (
                            ai_router.execute(
                                TaskClass.S2,
                                semantic_prewrite_prompt,
                                (
                                    f"{semantic_repair_id}"
                                    "-prewrite"
                                ),
                                Role.DEVELOPER.value,
                                (
                                    "Correct semantic repair "
                                    "pre-write validation once"
                                ),
                                request.timeout_seconds,
                                response_format=semantic_response_format,
                            )
                        )

                        semantic_repair_patch = (
                            _validate_ai_developer_full_file_patch(
                                semantic_repair_response.text,
                                target_paths,
                                semantic_repair_source_texts,
                            )
                        )

                        _validate_ai_developer_candidate_syntax(
                            semantic_repair_patch,
                            semantic_repair_source_texts,
                        )
                        prewrite_recovery_context = None

                semantic_repair_payload_key = (
                    json.dumps(
                        semantic_repair_patch,
                        sort_keys=True,
                        ensure_ascii=False,
                    )
                )

                if (
                    semantic_repair_payload_key
                    in seen_repair_payloads
                ):
                    raise ValueError(
                        "AI Developer repeated an identical "
                        "semantic repair payload without "
                        "new evidence"
                    )

                seen_repair_payloads.add(
                    semantic_repair_payload_key
                )

                semantic_repair_changes = (
                    _ai_patch_changes(
                        semantic_repair_patch
                    )
                )

                semantic_changed_paths = [
                    item["path"]
                    for item in semantic_repair_changes
                ]

                task_defs.append(
                    _task(
                        run_id,
                        semantic_repair_id,
                        Role.DEVELOPER,
                        (
                            "Repair blocking semantic "
                            "review findings"
                        ),
                        target_paths,
                        ["repo_edit"],
                        ["review"],
                    )
                )

                validate_task_graph(
                    task_defs
                )

                for semantic_change in (
                    semantic_repair_changes
                ):
                    gateway.edit_text(
                        Role.DEVELOPER,
                        workspace.path,  # type: ignore[arg-type]
                        authorized_paths,
                        semantic_change["path"],
                        semantic_change["old_text"],
                        semantic_change["new_text"],
                    )

                _result(
                    store,
                    semantic_repair_id,
                    ResultStatus.PASS,
                    (
                        "Bounded semantic-review repair "
                        "applied through ToolGateway"
                    ),
                    [diff_evidence_id],
                    "Rerun deterministic tests",
                    changed=semantic_changed_paths,
                )

                if ai_developer_artifact is None:
                    raise RuntimeError(
                        "AI Developer artifact missing "
                        "before semantic repair"
                    )

                ai_developer_artifact[
                    "repair_attempts"
                ].append({
                    "attempt":
                        repair_attempts + 1,
                    "cause":
                        "semantic_review",
                    "review_round":
                        review_round,
                    "review_evidence_ref":
                        "AIReview.json",
                    "developer_task_id":
                        semantic_repair_id,
                    "provider":
                        (
                            "aider-cli"
                            if semantic_repair_engine == "aider-cli"
                            else semantic_repair_route.provider
                        ),
                    "model":
                        semantic_repair_route.model,
                    "editor_engine":
                        semantic_repair_engine,
                    "chatgpt_assistance_in_target_product_run":
                        0,
                    "changed_paths":
                        semantic_changed_paths,
                    "patch":
                        semantic_repair_patch,
                    "prewrite_repair_attempts":
                        semantic_prewrite_attempts,
                    "applied_by":
                        "deterministic_tool_gateway",
                })

                store.write_optional_json(
                    "AIDeveloperPatch.json",
                    ai_developer_artifact,
                )

                repair_attempts += 1

                diff = workspace.diff()
                semantic_repair_diff_evidence_id = (
                    f"ev-diff-semantic-repair-"
                    f"{repair_attempts}"
                )
                if diff:
                    store.write_text(
                        "Changes.patch",
                        diff,
                    )
                    evidence.append({
                        "evidence_id":
                            semantic_repair_diff_evidence_id,
                        "check_type":
                            "scope",
                        "command_or_tool":
                            "git diff",
                        "exit_status":
                            0,
                        "summary":
                            (
                                "Patch refreshed after "
                                "semantic-review repair"
                            ),
                        "artifact_ref":
                            "Changes.patch",
                        "repair_attempt":
                            repair_attempts,
                        "repair_cause":
                            "semantic_review",
                    })

                machine.transition(
                    RunStatus.TESTING
                )

                test = gateway.run_test(
                    Role.TESTER,
                    workspace.path,  # type: ignore[arg-type]
                    request.test_command,
                    request.timeout_seconds,
                )

                semantic_test_evidence_id = (
                    f"ev-test-{repair_attempts}"
                )

                evidence.append({
                    "evidence_id":
                        semantic_test_evidence_id,
                    "check_type":
                        "tests",
                    "command_or_tool":
                        request.test_command,
                    "exit_status":
                        test.exit_status,
                    "summary":
                        (
                            "Tests passed"
                            if test.exit_status == 0
                            else "Tests failed"
                        ),
                    "stdout":
                        test.stdout[-4000:],
                    "stderr":
                        test.stderr[-4000:],
                    "repair_attempt":
                        repair_attempts,
                    "repair_cause":
                        "semantic_review",
                })

                if test.exit_status != 0:
                    final_test_passed = False
                    machine.transition(
                        RunStatus.DIAGNOSING
                    )

                    semantic_test_correction_id = (
                        f"{semantic_repair_id}"
                        "-test-correction"
                    )
                    semantic_test_correction_source_texts = (
                        _read_ai_developer_targets(
                            workspace.path,  # type: ignore[arg-type]
                            target_paths,
                        )
                    )
                    semantic_test_correction_files = (
                        "\n\n".join(
                            (
                                f"--- BEGIN FILE {path} ---\n"
                                f"{semantic_test_correction_source_texts[path]}\n"
                                f"--- END FILE {path} ---"
                            )
                            for path in target_paths
                        )
                    )

                    semantic_test_correction_prompt = f"""
You are the DEVELOPER agent in ForgeLab.

The single bounded semantic-review repair was applied, but its
deterministic test run FAILED.

This is the ONE bounded test correction inside the SAME semantic
repair attempt. It does NOT increase max_repair_attempts.

Original objective:
{request.objective}

Project Manager binding acceptance contract:
{plan_contract_text}

Blocking semantic review that triggered the repair:
{json.dumps(semantic_review, indent=2, ensure_ascii=False)}

Deterministic evidence BEFORE the semantic repair:
stdout:
{semantic_pre_repair_test_stdout[-2500:]}

stderr:
{semantic_pre_repair_test_stderr[-2500:]}

Deterministic evidence AFTER the semantic repair:
stdout:
{test.stdout[-2500:]}

stderr:
{test.stderr[-2500:]}

Current complete authorized files AFTER the semantic repair:
{semantic_test_correction_files}

Rules:
- preserve every behavior and test that passed before the semantic repair;
- fix the current deterministic failure without weakening, deleting,
  renaming, bypassing, or trivializing required acceptance coverage;
- preserve the original Product Owner objective and every binding
  acceptance criterion;
- if the failing test is malformed or inconsistent with the intended
  public API, correct that test while preserving the requirement it is
  meant to prove;
- if implementation is incomplete, correct the implementation and keep
  direct tests for the required behavior;
- preserve established public return types, keys, call signatures, and
  passing semantics unless the objective explicitly requires a change;
- quantitative requirements require direct quantitative tests;
- user-visible requirements must remain wired through the existing
  interface or entry point when present;
- return COMPLETE replacement content only for the authorized file
  subset that actually needs correction;
- for Python files, return complete syntactically valid Python;
- do not modify dependencies or configuration;
- do not claim tests have run.

Return ONLY the required JSON object.
"""

                    machine.transition(
                        RunStatus.REPAIRING
                    )

                    task_defs.append(
                        _task(
                            run_id,
                            semantic_test_correction_id,
                            Role.DEVELOPER,
                            (
                                "Correct deterministic failure "
                                "inside semantic-review repair"
                            ),
                            target_paths,
                            ["repo_edit"],
                            [semantic_repair_id],
                        )
                    )
                    validate_task_graph(
                        task_defs
                    )

                    semantic_test_correction_response = (
                        ai_router.execute(
                            TaskClass.S2,
                            semantic_test_correction_prompt,
                            semantic_test_correction_id,
                            Role.DEVELOPER.value,
                            (
                                "Correct failed semantic-review "
                                "repair tests once"
                            ),
                            request.timeout_seconds,
                            response_format=(
                                _ai_developer_full_file_response_schema(
                                    target_paths
                                )
                            ),
                        )
                    )
                    semantic_test_correction_route = (
                        ai_router.route(
                            TaskClass.S2
                        )
                    )

                    semantic_test_correction_patch: (
                        dict[str, Any] | None
                    ) = None
                    semantic_test_correction_error = ""

                    try:
                        semantic_test_correction_patch = (
                            _validate_ai_developer_full_file_patch(
                                semantic_test_correction_response.text,
                                target_paths,
                                semantic_test_correction_source_texts,
                            )
                        )
                        _validate_ai_developer_candidate_syntax(
                            semantic_test_correction_patch,
                            semantic_test_correction_source_texts,
                        )
                    except ValueError as error:
                        semantic_test_correction_error = str(
                            error
                        )
                        semantic_test_correction_patch = None

                    semantic_repair_record = (
                        ai_developer_artifact[
                            "repair_attempts"
                        ][-1]
                    )
                    semantic_repair_record[
                        "semantic_test_correction_attempts"
                    ] = 1

                    if semantic_test_correction_patch is None:
                        semantic_repair_record[
                            "semantic_test_correction"
                        ] = {
                            "developer_task_id":
                                semantic_test_correction_id,
                            "provider":
                                semantic_test_correction_route.provider,
                            "model":
                                semantic_test_correction_route.model,
                            "changed_paths": [],
                            "patch": None,
                            "validation_error":
                                semantic_test_correction_error,
                            "applied_by": None,
                        }
                        store.write_optional_json(
                            "AIDeveloperPatch.json",
                            ai_developer_artifact,
                        )

                        evidence.append({
                            "evidence_id":
                                (
                                    "ev-semantic-test-correction-"
                                    f"{repair_attempts}"
                                ),
                            "check_type":
                                "semantic_repair_test_correction",
                            "command_or_tool":
                                (
                                    "ai_generate+"
                                    "deterministic_prewrite_validation"
                                ),
                            "exit_status":
                                1,
                            "repair_attempt":
                                repair_attempts,
                            "summary":
                                (
                                    "Semantic repair test "
                                    "correction rejected before "
                                    "write: "
                                    + semantic_test_correction_error
                                ),
                        })
                        results.append(
                            _result(
                                store,
                                semantic_test_correction_id,
                                ResultStatus.FAIL,
                                (
                                    "Semantic repair test "
                                    "correction rejected before write"
                                ),
                                [
                                    semantic_test_evidence_id
                                ],
                                "Human repair required",
                            )
                        )
                        machine.transition(
                            RunStatus.CLOSED
                        )
                        break

                    semantic_test_correction_changes = (
                        _ai_patch_changes(
                            semantic_test_correction_patch
                        )
                    )
                    semantic_test_correction_changed_paths = [
                        item["path"]
                        for item in
                        semantic_test_correction_changes
                    ]

                    for semantic_test_correction_change in (
                        semantic_test_correction_changes
                    ):
                        gateway.edit_text(
                            Role.DEVELOPER,
                            workspace.path,  # type: ignore[arg-type]
                            authorized_paths,
                            semantic_test_correction_change[
                                "path"
                            ],
                            semantic_test_correction_change[
                                "old_text"
                            ],
                            semantic_test_correction_change[
                                "new_text"
                            ],
                        )

                    semantic_repair_record[
                        "semantic_test_correction"
                    ] = {
                        "developer_task_id":
                            semantic_test_correction_id,
                        "provider":
                            semantic_test_correction_route.provider,
                        "model":
                            semantic_test_correction_route.model,
                        "changed_paths":
                            semantic_test_correction_changed_paths,
                        "patch":
                            semantic_test_correction_patch,
                        "validation_error": None,
                        "applied_by":
                            "deterministic_tool_gateway",
                    }
                    store.write_optional_json(
                        "AIDeveloperPatch.json",
                        ai_developer_artifact,
                    )

                    results.append(
                        _result(
                            store,
                            semantic_test_correction_id,
                            ResultStatus.PASS,
                            (
                                "Semantic repair deterministic "
                                "failure corrected once"
                            ),
                            [
                                semantic_test_evidence_id
                            ],
                            "Rerun deterministic tests",
                            changed=(
                                semantic_test_correction_changed_paths
                            ),
                        )
                    )

                    diff = workspace.diff()
                    semantic_test_correction_diff_id = (
                        "ev-diff-semantic-test-correction-"
                        f"{repair_attempts}"
                    )
                    if diff:
                        store.write_text(
                            "Changes.patch",
                            diff,
                        )
                        evidence.append({
                            "evidence_id":
                                semantic_test_correction_diff_id,
                            "check_type":
                                "scope",
                            "command_or_tool":
                                "git diff",
                            "exit_status":
                                0,
                            "summary":
                                (
                                    "Patch refreshed after "
                                    "semantic repair test correction"
                                ),
                            "artifact_ref":
                                "Changes.patch",
                            "repair_attempt":
                                repair_attempts,
                            "repair_cause":
                                "semantic_review_test_correction",
                        })

                    machine.transition(
                        RunStatus.TESTING
                    )
                    test = gateway.run_test(
                        Role.TESTER,
                        workspace.path,  # type: ignore[arg-type]
                        request.test_command,
                        request.timeout_seconds,
                    )
                    semantic_correction_test_evidence_id = (
                        f"ev-test-{repair_attempts}"
                        "-semantic-correction"
                    )
                    evidence.append({
                        "evidence_id":
                            semantic_correction_test_evidence_id,
                        "check_type":
                            "tests",
                        "command_or_tool":
                            request.test_command,
                        "exit_status":
                            test.exit_status,
                        "summary":
                            (
                                "Tests passed"
                                if test.exit_status == 0
                                else "Tests failed"
                            ),
                        "stdout":
                            test.stdout[-4000:],
                        "stderr":
                            test.stderr[-4000:],
                        "repair_attempt":
                            repair_attempts,
                        "repair_cause":
                            (
                                "semantic_review_"
                                "test_correction"
                            ),
                    })

                    if test.exit_status != 0:
                        results.append(
                            _result(
                                store,
                                "test",
                                ResultStatus.FAIL,
                                (
                                    "Tests failed after one "
                                    "semantic repair test correction"
                                ),
                                [
                                    semantic_correction_test_evidence_id
                                ],
                                "Human repair required",
                            )
                        )
                        machine.transition(
                            RunStatus.DIAGNOSING
                        )
                        break

                    final_test_passed = True
                    results.append(
                        _result(
                            store,
                            "test",
                            ResultStatus.PASS,
                            (
                                "Acceptance tests passed after "
                                "semantic repair test correction"
                            ),
                            [
                                semantic_correction_test_evidence_id
                            ],
                            "Re-run semantic review",
                        )
                    )
                    review_round += 1
                    continue

                results.append(
                    _result(
                        store,
                        "test",
                        ResultStatus.PASS,
                        (
                            "Acceptance tests passed after "
                            "semantic-review repair"
                        ),
                        [
                            semantic_test_evidence_id
                        ],
                        "Re-run semantic review",
                    )
                )

                review_round += 1

            if (
                final_test_passed
                and review_report["status"] == "PASS"
            ):
                machine.transition(
                    RunStatus.SECURITY_CHECK
                )

                security_report = (
                    security_review_patch(
                        diff
                    )
                )

                if Role.SECURITY in roles:
                    sec_status = (
                        ResultStatus.PASS
                        if security_report[
                            "status"
                        ] == "PASS"
                        else ResultStatus.FAIL
                    )

                    results.append(
                        _result(
                            store,
                            "security",
                            sec_status,
                            "Security review completed",
                            [
                                f"ev-diff-{review_round}"
                            ],
                            "Proceed to gate",
                            security_report[
                                "findings"
                            ],
                        )
                    )

                if Role.DOCUMENTATION in roles:
                    results.append(
                        _result(
                            store,
                            "documentation",
                            ResultStatus.PASS,
                            (
                                "Documentation change is "
                                "internally consistent"
                            ),
                            [
                                f"ev-diff-{review_round}"
                            ],
                            "Proceed to gate",
                        )
                    )

                if (
                    security_report[
                        "status"
                    ] == "PASS"
                ):
                    machine.transition(
                        RunStatus.READY_FOR_DECISION
                    )
    except AIEditorExecutionError as editor_error:
        editor_failure = {
            "run_id": run_id,
            "status": "FAIL",
            "reason": "EDITOR_EXECUTION_FAILED",
            "phase": editor_error.phase,
            "final_error_type": type(editor_error).__name__,
            "final_error": str(editor_error),
            "source_repository_write_performed": False,
        }
        store.write_optional_json(
            "EditorFailure.json",
            editor_failure,
        )
        evidence.append({
            "evidence_id": "ev-editor-execution-failed",
            "check_type": "editor_execution",
            "command_or_tool": "aider-cli",
            "exit_status": 1,
            "summary": str(editor_error),
            "artifact_ref": "EditorFailure.json",
            "phase": editor_error.phase,
        })
        results.append(
            AgentResult(
                ResultStatus.FAIL,
                "Reusable editor execution failed inside governed run",
                [],
                ["ev-editor-execution-failed"],
                [],
                [],
                "Inspect editor failure evidence",
            ).to_dict()
        )
        if machine.status != RunStatus.CLOSED:
            machine.transition(
                RunStatus.CLOSED
            )
    except ProviderTransientError as provider_error:
        _, provider_evidence = _record_provider_failure(
            store,
            run_id,
            ai_ledger,
            machine.status.value,
            provider_error,
        )
        evidence.append(
            provider_evidence
        )
        results.append(
            AgentResult(
                ResultStatus.FAIL,
                (
                    "Local provider retries exhausted "
                    "inside governed run"
                ),
                [],
                ["ev-provider-failure"],
                [],
                [],
                "Retry or inspect local provider",
            ).to_dict()
        )

        if machine.status != RunStatus.CLOSED:
            machine.transition(
                RunStatus.CLOSED
            )
    except (
        AIDeveloperFormatError,
        AIDeveloperReferenceError,
        AIDeveloperSyntaxError,
    ) as exhausted_prewrite_error:
        failure_context = (
            prewrite_recovery_context
            or {
                "phase": machine.status.value,
                "first_error": "",
            }
        )
        failure_artifact = {
            "run_id": run_id,
            "status": "FAIL",
            "reason": "PREWRITE_RECOVERY_EXHAUSTED",
            "phase": failure_context["phase"],
            "first_error": failure_context["first_error"],
            "final_error_type": type(
                exhausted_prewrite_error
            ).__name__,
            "final_error": str(
                exhausted_prewrite_error
            ),
            "prewrite_repair_attempts": 1,
            "repository_write_performed": False,
        }
        store.write_optional_json(
            "PrewriteRecoveryFailure.json",
            failure_artifact,
        )
        evidence.append({
            "evidence_id":
                "ev-prewrite-recovery-exhausted",
            "check_type":
                "prewrite_validation",
            "command_or_tool":
                "ai_generate+deterministic_prewrite_validation",
            "exit_status":
                1,
            "summary":
                (
                    "Bounded pre-write recovery exhausted: "
                    + str(exhausted_prewrite_error)
                ),
            "artifact_ref":
                "PrewriteRecoveryFailure.json",
            "phase":
                failure_context["phase"],
        })
        results.append(
            AgentResult(
                ResultStatus.FAIL,
                (
                    "Bounded pre-write recovery exhausted "
                    "without repository write"
                ),
                [],
                ["ev-prewrite-recovery-exhausted"],
                [],
                [],
                "Human repair required",
            ).to_dict()
        )

        if machine.status != RunStatus.CLOSED:
            machine.transition(
                RunStatus.CLOSED
            )
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
        "run_id": run_id,
        **security_report,
        "source_repository_unchanged": source_unchanged,
        "network_used": bool(use_ai),
        "network_scope": (
            "loopback_only"
            if use_ai
            else "none"
        ),
        "external_network_allowed": False,
        "editor_egress_guard": (
            "process_env_proxy_guard"
            if request.editor_engine == "aider"
            else "not_applicable"
        ),
        "tool_audit_ref": "ToolAudit.json",
        "tool_policy_denials": tool_audit["denied_count"],
    })
    if use_ai:
        usage_report = ai_ledger.report()
        usage_report.update({
            "run_id": run_id,
            "estimated_cost": str(ai_ledger.spent),
            "runtime": "hybrid_local_ai",
            "provider_mode": "local_zero_spend",
            "editor_engine": request.editor_engine,
            "editor_timeout_seconds":
                request.editor_timeout_seconds,
            "reusable_editor_calls": reusable_editor_calls,
            "network_scope": "loopback_only",
            "external_network_allowed": False,
            "editor_egress_guard": (
                "process_env_proxy_guard"
                if request.editor_engine == "aider"
                else "not_applicable"
            ),
            "chatgpt_assistance_in_target_product_run": 0,
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
        "model_usage": (
            "Aider + Ollama local"
            if request.editor_engine == "aider"
            else ("Ollama local" if use_ai else "None")
        ),
        "decision": "Human gate pending" if passed else "Repair required", "created_at": now,
        "change_operation": request.operation,
        "editor_engine": request.editor_engine,
        "chatgpt_assistance_in_target_product_run": 0,
        "product_owner_run_actions": 1,
        "context_bundle_ref": "ContextBundle.json",
        "context_selection_sha256": context_bundle["selection_sha256"],
        "context_selected_paths": context_bundle["selected_paths"],
    })
    store.write("GateDecision.json", {
        "gate_type": "G3_PROMOTE", "actor": "SYSTEM", "decision": "PENDING" if passed else "REPAIR",
        "scope": "Review multi-agent artifacts and Changes.patch", "timestamp": now,
    })
    return run_dir

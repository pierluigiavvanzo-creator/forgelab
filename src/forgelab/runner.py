from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .artifacts import ArtifactStore
from .domain import RunStatus
from .state_machine import RunStateMachine
from .tools import replace_text, run_bounded
from .workspace import IsolatedWorkspace
from .quality import review_patch, security_review_patch


@dataclass(frozen=True)
class RunRequest:
    repository: Path
    objective: str
    target_path: str
    old_text: str
    new_text: str
    test_command: list[str]
    timeout_seconds: int = 60

    @classmethod
    def from_json(cls, path: Path) -> "RunRequest":
        payload = json.loads(path.read_text(encoding="utf-8"))
        change = payload["change"]
        if change.get("operation") != "replace_text":
            raise ValueError("M1 supports only the replace_text operation")
        return cls(
            repository=Path(payload["repository"]), objective=payload["objective"],
            target_path=change["path"], old_text=change["old"], new_text=change["new"],
            test_command=list(payload["test_command"]),
            timeout_seconds=int(payload.get("timeout_seconds", 60)),
        )


def run_isolated(request: RunRequest, output_root: Path) -> Path:
    run_id = f"run-{uuid4().hex[:12]}"
    run_dir = output_root.resolve() / run_id
    store = ArtifactStore(run_dir)
    machine = RunStateMachine()
    evidence: list[dict[str, Any]] = []
    changed: list[str] = []
    diff = ""
    source_unchanged = False
    test_status = "FAIL"

    for state in (RunStatus.PRECHECK, RunStatus.PLANNED, RunStatus.ISOLATED):
        machine.transition(state)

    workspace = IsolatedWorkspace(request.repository, run_id)
    try:
        workspace.create()
        machine.transition(RunStatus.IMPLEMENTING)
        target = replace_text(workspace.path, request.target_path, request.old_text, request.new_text)  # type: ignore[arg-type]
        changed.append(request.target_path)
        machine.transition(RunStatus.TESTING)
        command_result = run_bounded(request.test_command, workspace.path, request.timeout_seconds)  # type: ignore[arg-type]
        evidence.append({
            "evidence_id": "ev-tests", "check_type": "tests",
            "command_or_tool": request.test_command, "exit_status": command_result.exit_status,
            "summary": "Tests passed" if command_result.exit_status == 0 else "Tests failed",
            "stdout": command_result.stdout[-4000:], "stderr": command_result.stderr[-4000:],
            "timed_out": command_result.timed_out,
        })
        if command_result.exit_status != 0:
            machine.transition(RunStatus.DIAGNOSING)
            test_status = "FAIL"
        else:
            test_status = "PASS"
            machine.transition(RunStatus.SMOKE_TEST)
            diff = workspace.diff()
            if not diff:
                raise RuntimeError("implementation produced no diff")
            evidence.append({
                "evidence_id": "ev-diff", "check_type": "scope",
                "command_or_tool": "git diff --binary --no-ext-diff", "exit_status": 0,
                "summary": f"Diff captured for {target.relative_to(workspace.path)}",
                "artifact_ref": "Changes.patch",
            })
            machine.transition(RunStatus.REVIEW)
            review = review_patch(diff, {request.target_path})
            if review["status"] != "PASS":
                raise RuntimeError("deterministic review rejected the patch")
            machine.transition(RunStatus.SECURITY_CHECK)
            security = security_review_patch(diff)
            if security["status"] != "PASS":
                raise RuntimeError("security review rejected the patch")
            machine.transition(RunStatus.READY_FOR_DECISION)
    finally:
        source_unchanged = workspace.verify_source_unchanged() if workspace.base_head else False
        workspace.close()

    now = datetime.now(timezone.utc).isoformat()
    if diff:
        store.write_text("Changes.patch", diff)
    status = "PASS" if test_status == "PASS" and source_unchanged else "FAIL"
    store.write("ExecutionPlan.json", {
        "run_id": run_id, "objective": request.objective,
        "repository": str(request.repository.resolve()), "base_head": workspace.base_head,
        "test_command": request.test_command, "timeout_seconds": request.timeout_seconds,
        "tasks": [{"role": "DEVELOPER", "operation": "replace_text", "path": request.target_path}],
        "requires_human_gate": True,
    })
    store.write("AgentResult.json", {
        "status": status, "summary": "Isolated change and verification completed" if status == "PASS" else "Run stopped before decision",
        "changed_artifacts": changed, "evidence_refs": [item["evidence_id"] for item in evidence],
        "findings": [], "assumptions": [], "next_action": "Human review of Changes.patch",
    })
    store.write("TestEvidence.json", {"run_id": run_id, "evidence": evidence})
    review_report = review_patch(diff, {request.target_path}) if diff else {"status": "FAIL", "findings": [{"severity": "BLOCKER", "description": "No patch"}]}
    store.write("ReviewReport.json", {"run_id": run_id, **review_report})
    security_report = security_review_patch(diff) if diff else {"status": "FAIL", "findings": [{"severity": "BLOCKER", "description": "No patch"}]}
    store.write("SecurityReport.json", {
        "run_id": run_id, **security_report, "network_used": False,
        "source_repository_unchanged": source_unchanged,
    })
    store.write("UsageReport.json", {"run_id": run_id, "llm_calls": 0, "estimated_cost": 0.0})
    store.write("RunSummary.json", {
        "run_id": run_id, "status": machine.status.value,
        "repository": str(request.repository.resolve()), "base_head": workspace.base_head,
        "history": [state.value for state in machine.history], "plan": request.objective,
        "changes": changed, "tests": test_status,
        "risk": "Patch only; source repository unchanged" if source_unchanged else "Source integrity check failed",
        "model_usage": "None", "decision": "Human gate pending" if status == "PASS" else "Repair required",
        "created_at": now,
    })
    store.write("GateDecision.json", {
        "gate_type": "G3_PROMOTE", "actor": "SYSTEM",
        "decision": "PENDING" if status == "PASS" else "REPAIR",
        "scope": "Review Changes.patch; M1 never promotes automatically", "timestamp": now,
    })
    return run_dir

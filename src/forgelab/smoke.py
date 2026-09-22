from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .artifacts import ArtifactStore
from .domain import AgentResult, AgentTask, Evidence, GateDecision, ResourceLimits, ResultStatus, Role, RunStatus, Scope
from .state_machine import RunStateMachine


def run_smoke(output_root: Path) -> Path:
    run_id = f"run-{uuid4().hex[:12]}"
    run_dir = output_root / run_id
    store = ArtifactStore(run_dir)
    machine = RunStateMachine()
    for state in (
        RunStatus.PRECHECK, RunStatus.BENCHMARKED, RunStatus.PLANNED,
        RunStatus.ISOLATED, RunStatus.IMPLEMENTING, RunStatus.TESTING,
        RunStatus.SMOKE_TEST, RunStatus.REVIEW, RunStatus.SECURITY_CHECK,
        RunStatus.READY_FOR_DECISION,
    ):
        machine.transition(state)

    task = AgentTask(
        task_id="task-smoke-1", run_id=run_id, role=Role.DEVELOPER,
        objective="Prove the M0 contracts and state flow without external side effects",
        scope=Scope(allowed_paths=[str(run_dir)], forbidden_paths=["main"]),
        inputs={"mode": "deterministic"},
        acceptance_criteria=["All mandatory artifacts exist", "Run stops at the human gate"],
        allowed_tools=["artifact_store"],
        resource_limits=ResourceLimits(max_steps=20, max_runtime_seconds=30, max_cost=0.0),
        escalation_conditions=["Any mandatory artifact cannot be written"],
    )
    evidence = Evidence("ev-smoke", "smoke", "forgelab smoke", 0, "M0 deterministic flow completed")
    result = AgentResult(ResultStatus.PASS, "M0 smoke completed", [], [evidence.evidence_id], [], [], "Await human promotion decision")
    now = datetime.now(timezone.utc).isoformat()

    store.write("ExecutionPlan.json", {"run_id": run_id, "tasks": [task.to_dict()], "requires_human_gate": True})
    store.write("AgentResult.json", result.to_dict())
    store.write("TestEvidence.json", {"run_id": run_id, "evidence": [evidence.to_dict()]})
    store.write("ReviewReport.json", {"run_id": run_id, "status": "PASS", "findings": []})
    store.write("SecurityReport.json", {"run_id": run_id, "status": "PASS", "findings": [], "network_used": False})
    store.write("UsageReport.json", {"run_id": run_id, "llm_calls": 0, "estimated_cost": 0.0})
    store.write("RunSummary.json", {
        "run_id": run_id, "status": machine.status.value,
        "history": [item.value for item in machine.history],
        "plan": "Validate M0 deterministically", "changes": [], "tests": "PASS",
        "risk": "No external side effects", "model_usage": "None",
        "decision": "Human gate pending", "created_at": now,
    })
    gate = GateDecision("G3_PROMOTE", "SYSTEM", "PENDING", "Human promotion decision required", now)
    store.write("GateDecision.json", gate.to_dict())
    if missing := store.missing():
        raise RuntimeError(f"smoke run missing artifacts: {missing}")
    return run_dir

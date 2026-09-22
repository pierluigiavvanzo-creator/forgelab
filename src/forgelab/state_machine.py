from __future__ import annotations

from dataclasses import dataclass, field

from .domain import RunStatus


class InvalidTransition(ValueError):
    pass


TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.RECEIVED: {RunStatus.PRECHECK},
    RunStatus.PRECHECK: {RunStatus.BENCHMARKED, RunStatus.PLANNED, RunStatus.CLOSED},
    RunStatus.BENCHMARKED: {RunStatus.PLANNED, RunStatus.CLOSED},
    RunStatus.PLANNED: {RunStatus.ISOLATED, RunStatus.CLOSED},
    RunStatus.ISOLATED: {RunStatus.IMPLEMENTING, RunStatus.CLOSED},
    RunStatus.IMPLEMENTING: {RunStatus.TESTING, RunStatus.CLOSED},
    RunStatus.TESTING: {RunStatus.DIAGNOSING, RunStatus.SMOKE_TEST, RunStatus.CLOSED},
    RunStatus.DIAGNOSING: {RunStatus.REPAIRING, RunStatus.CLOSED},
    RunStatus.REPAIRING: {RunStatus.TESTING, RunStatus.CLOSED},
    RunStatus.SMOKE_TEST: {RunStatus.REVIEW, RunStatus.DIAGNOSING, RunStatus.CLOSED},
    RunStatus.REVIEW: {RunStatus.SECURITY_CHECK, RunStatus.REPAIRING, RunStatus.CLOSED},
    RunStatus.SECURITY_CHECK: {RunStatus.READY_FOR_DECISION, RunStatus.REPAIRING, RunStatus.CLOSED},
    RunStatus.READY_FOR_DECISION: {RunStatus.APPROVED, RunStatus.REJECTED, RunStatus.REPAIRING},
    RunStatus.APPROVED: {RunStatus.PROMOTE},
    RunStatus.REJECTED: {RunStatus.CLOSED},
    RunStatus.PROMOTE: {RunStatus.VERIFIED, RunStatus.CLOSED},
    RunStatus.VERIFIED: {RunStatus.DONE},
    RunStatus.DONE: set(),
    RunStatus.CLOSED: set(),
}


@dataclass
class RunStateMachine:
    status: RunStatus = RunStatus.RECEIVED
    history: list[RunStatus] = field(default_factory=lambda: [RunStatus.RECEIVED])

    def transition(self, target: RunStatus) -> None:
        if target not in TRANSITIONS[self.status]:
            raise InvalidTransition(f"cannot transition from {self.status.value} to {target.value}")
        self.status = target
        self.history.append(target)


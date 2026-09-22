from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class ContractError(ValueError):
    pass


class Role(str, Enum):
    ARCHITECT = "ARCHITECT"
    PROJECT_MANAGER = "PROJECT_MANAGER"
    DEVELOPER = "DEVELOPER"
    TESTER = "TESTER"
    REVIEWER = "REVIEWER"
    SECURITY = "SECURITY"
    DOCUMENTATION = "DOCUMENTATION"
    SUPPORT = "SUPPORT"


class ResultStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NEEDS_GATE = "NEEDS_GATE"


class RunStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PRECHECK = "PRECHECK"
    BENCHMARKED = "BENCHMARKED"
    PLANNED = "PLANNED"
    ISOLATED = "ISOLATED"
    IMPLEMENTING = "IMPLEMENTING"
    TESTING = "TESTING"
    DIAGNOSING = "DIAGNOSING"
    REPAIRING = "REPAIRING"
    SMOKE_TEST = "SMOKE_TEST"
    REVIEW = "REVIEW"
    SECURITY_CHECK = "SECURITY_CHECK"
    READY_FOR_DECISION = "READY_FOR_DECISION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROMOTE = "PROMOTE"
    VERIFIED = "VERIFIED"
    DONE = "DONE"
    CLOSED = "CLOSED"


def _required(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{name} must be a non-empty string")


@dataclass(frozen=True)
class Scope:
    allowed_paths: list[str]
    forbidden_paths: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.allowed_paths:
            raise ContractError("scope.allowed_paths must not be empty")
        overlap = set(self.allowed_paths) & set(self.forbidden_paths)
        if overlap:
            raise ContractError(f"paths cannot be both allowed and forbidden: {sorted(overlap)}")


@dataclass(frozen=True)
class ResourceLimits:
    max_steps: int
    max_runtime_seconds: int
    max_cost: float

    def validate(self) -> None:
        if self.max_steps < 1 or self.max_runtime_seconds < 1 or self.max_cost < 0:
            raise ContractError("resource limits must be positive; max_cost may be zero")


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    run_id: str
    role: Role
    objective: str
    scope: Scope
    inputs: dict[str, Any]
    acceptance_criteria: list[str]
    allowed_tools: list[str]
    resource_limits: ResourceLimits
    escalation_conditions: list[str]

    def validate(self) -> None:
        for name in ("task_id", "run_id", "objective"):
            _required(getattr(self, name), name)
        self.scope.validate()
        self.resource_limits.validate()
        if not self.acceptance_criteria:
            raise ContractError("acceptance_criteria must not be empty")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return _serialize(asdict(self))


@dataclass(frozen=True)
class AgentResult:
    status: ResultStatus
    summary: str
    changed_artifacts: list[str]
    evidence_refs: list[str]
    findings: list[dict[str, Any]]
    assumptions: list[str]
    next_action: str

    def validate(self) -> None:
        _required(self.summary, "summary")
        _required(self.next_action, "next_action")
        if self.status is ResultStatus.PASS and not self.evidence_refs:
            raise ContractError("PASS requires at least one evidence reference")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return _serialize(asdict(self))


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    check_type: str
    command_or_tool: str
    exit_status: int
    summary: str
    artifact_ref: str | None = None

    def validate(self) -> None:
        for name in ("evidence_id", "check_type", "command_or_tool", "summary"):
            _required(getattr(self, name), name)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class GateDecision:
    gate_type: str
    actor: str
    decision: str
    scope: str
    timestamp: str

    def validate(self) -> None:
        for name in ("gate_type", "actor", "decision", "scope", "timestamp"):
            _required(getattr(self, name), name)
        if self.decision not in {"PENDING", "APPROVE", "REJECT", "REPAIR"}:
            raise ContractError("unsupported gate decision")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value

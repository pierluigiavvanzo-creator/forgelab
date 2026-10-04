from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Protocol


class TaskClass(str, Enum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


class RouterError(RuntimeError):
    pass


class BudgetExceeded(RouterError):
    pass


class ProviderTransientError(RouterError):
    pass


class ProviderPermanentError(RouterError):
    pass


@dataclass(frozen=True)
class TaskProfile:
    deterministic: bool = False
    implementation: bool = False
    cross_component_count: int = 1
    architecture_change: bool = False
    high_impact: bool = False
    security_sensitive: bool = False


def classify(profile: TaskProfile) -> TaskClass:
    if profile.deterministic:
        return TaskClass.S0
    if profile.high_impact or profile.security_sensitive:
        return TaskClass.S4
    if profile.architecture_change or profile.cross_component_count >= 4:
        return TaskClass.S3
    if profile.implementation:
        return TaskClass.S2
    return TaskClass.S1


@dataclass(frozen=True)
class Pricing:
    input_per_million: Decimal
    output_per_million: Decimal


@dataclass(frozen=True)
class ModelRoute:
    task_class: TaskClass
    provider: str | None
    model: str
    max_retries: int
    max_call_cost: Decimal
    pricing: Pricing | None
    human_review_required: bool = False


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    input_tokens: int
    output_tokens: int
    actual_cost: Decimal | None = None
    cache_read_tokens: int = 0


class ModelProvider(Protocol):
    def invoke(
        self,
        model: str,
        prompt: str,
        timeout_seconds: int,
        response_format: dict[str, object] | str | None = None,
    ) -> ProviderResponse: ...


@dataclass(frozen=True)
class UsageRecord:
    provider: str
    model_id: str
    policy_route: str
    agent_role: str
    task_id: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cost: str
    latency_ms: int
    attempt: int
    outcome: str
    routing_reason: str
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class UsageLedger:
    def __init__(self, budget: Decimal) -> None:
        if budget < 0:
            raise ValueError("budget cannot be negative")
        self.budget = budget
        self.records: list[UsageRecord] = []

    @property
    def spent(self) -> Decimal:
        return sum((Decimal(record.cost) for record in self.records if record.outcome in {"SUCCESS", "BUDGET_BLOCKED"}), Decimal("0"))

    @property
    def remaining(self) -> Decimal:
        return self.budget - self.spent

    def report(self) -> dict[str, object]:
        return {
            "budget": str(self.budget), "spent": str(self.spent), "remaining": str(self.remaining),
            "llm_calls": len(self.records),
            "attempts": len(self.records), "records": [record.to_dict() for record in self.records],
        }


def load_routes(path: Path) -> dict[TaskClass, ModelRoute]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    routes: dict[TaskClass, ModelRoute] = {}
    for key, raw in payload["routes"].items():
        pricing = raw.get("pricing")
        routes[TaskClass(key)] = ModelRoute(
            task_class=TaskClass(key), provider=raw.get("provider"), model=raw["model"],
            max_retries=int(raw.get("max_retries", 0)), max_call_cost=Decimal(str(raw["max_call_cost"])),
            pricing=Pricing(Decimal(str(pricing["input_per_million"])), Decimal(str(pricing["output_per_million"]))) if pricing else None,
            human_review_required=bool(raw.get("human_review_required", False)),
        )
    if set(routes) != set(TaskClass):
        raise RouterError("routing configuration must define S0 through S4")
    return routes


def _cost(response: ProviderResponse, pricing: Pricing | None) -> Decimal:
    if response.actual_cost is not None:
        return response.actual_cost
    if pricing is None:
        raise RouterError("provider did not return actual cost and route has no configured pricing")
    million = Decimal("1000000")
    return (
        Decimal(response.input_tokens) * pricing.input_per_million / million
        + Decimal(response.output_tokens) * pricing.output_per_million / million
    )


class ModelRouter:
    def __init__(self, routes: dict[TaskClass, ModelRoute], providers: dict[str, ModelProvider], ledger: UsageLedger) -> None:
        self.routes = routes
        self.providers = providers
        self.ledger = ledger

    def route(self, task_class: TaskClass) -> ModelRoute:
        return self.routes[task_class]

    def execute(self, task_class: TaskClass, prompt: str, task_id: str, agent_role: str,
                routing_reason: str, timeout_seconds: int = 60,
                response_format: dict[str, object] | str | None = None) -> ProviderResponse:
        route = self.route(task_class)
        if task_class is TaskClass.S0 or route.provider is None:
            raise RouterError("S0 deterministic work must not call an LLM provider")
        if route.max_call_cost > self.ledger.remaining:
            raise BudgetExceeded("route reservation exceeds remaining run budget")
        provider = self.providers.get(route.provider)
        if provider is None:
            raise RouterError(f"provider is not configured: {route.provider}")
        previous_transient_error: ProviderTransientError | None = None

        for attempt in range(1, route.max_retries + 2):
            attempt_timeout_seconds = timeout_seconds
            attempt_prompt = prompt

            if (
                route.provider == "ollama"
                and attempt > 1
            ):
                attempt_timeout_seconds = min(
                    600,
                    max(
                        timeout_seconds,
                        timeout_seconds * 3,
                    ),
                )

                if (
                    previous_transient_error is not None
                    and "token repeat limit reached"
                    in str(previous_transient_error).lower()
                ):
                    attempt_prompt = (
                        prompt.rstrip()
                        + "\n\nLOCAL PROVIDER RECOVERY:\n"
                        + "- The previous generation was aborted because "
                        "its output became repetitive.\n"
                        + "- Produce one concise, non-repetitive answer.\n"
                        + "- Do not restate sections, duplicate JSON "
                        "objects, or repeat the same tokens.\n"
                        + "- If structured output is requested, emit "
                        "exactly one object matching the schema and stop."
                    )

            started = time.monotonic()

            try:
                response = (
                    provider.invoke(
                        route.model,
                        attempt_prompt,
                        attempt_timeout_seconds,
                    )
                    if response_format is None
                    else provider.invoke(
                        route.model,
                        attempt_prompt,
                        attempt_timeout_seconds,
                        response_format,
                    )
                )
                cost = _cost(response, route.pricing)
                latency = int((time.monotonic() - started) * 1000)
                if cost > route.max_call_cost or cost > self.ledger.remaining:
                    self.ledger.records.append(UsageRecord(
                        route.provider, route.model, task_class.value, agent_role, task_id,
                        response.input_tokens, response.output_tokens, response.cache_read_tokens,
                        str(cost), latency, attempt, "BUDGET_BLOCKED", routing_reason,
                        "actual cost exceeded reservation or remaining budget",
                    ))
                    raise BudgetExceeded("actual call cost exceeded policy budget")
                self.ledger.records.append(UsageRecord(
                    route.provider, route.model, task_class.value, agent_role, task_id,
                    response.input_tokens, response.output_tokens, response.cache_read_tokens,
                    str(cost), latency, attempt, "SUCCESS", routing_reason,
                ))
                return response
            except ProviderTransientError as error:
                previous_transient_error = error
                latency = int((time.monotonic() - started) * 1000)
                self.ledger.records.append(UsageRecord(
                    route.provider, route.model, task_class.value, agent_role, task_id,
                    0, 0, 0, "0", latency, attempt, "RETRY" if attempt <= route.max_retries else "FAIL",
                    routing_reason, str(error),
                ))
                if attempt > route.max_retries:
                    raise
            except ProviderPermanentError as error:
                latency = int((time.monotonic() - started) * 1000)
                self.ledger.records.append(UsageRecord(
                    route.provider, route.model, task_class.value, agent_role, task_id,
                    0, 0, 0, "0", latency, attempt, "FAIL", routing_reason, str(error),
                ))
                raise
        raise AssertionError("unreachable")

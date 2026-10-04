import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from forgelab.benchmark import BenchmarkCase, run_benchmark
from forgelab.model_router import (
    BudgetExceeded, ModelRoute, ModelRouter, Pricing, ProviderResponse,
    ProviderPermanentError, ProviderTransientError, RouterError, TaskClass, TaskProfile, UsageLedger,
    classify, load_routes,
)


class ScriptedProvider:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0
        self.response_formats = []
        self.timeouts = []
        self.prompts = []
        self.repeat_resets = []

    def invoke(
        self,
        model,
        prompt,
        timeout_seconds,
        response_format=None,
    ):
        self.response_formats.append(
            response_format
        )
        self.timeouts.append(
            timeout_seconds
        )
        self.prompts.append(
            prompt
        )
        outcome = self.outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def reset_after_repeat_limit(
        self,
        model,
        timeout_seconds,
    ):
        self.repeat_resets.append(
            (model, timeout_seconds)
        )


def routes(
    pricing=None,
    retries=1,
    max_cost="0.50",
    provider_name="test",
):
    return {
        task_class: ModelRoute(
            task_class,
            None if task_class is TaskClass.S0 else provider_name,
            "deterministic" if task_class is TaskClass.S0 else "model",
            0 if task_class is TaskClass.S0 else retries,
            Decimal("0") if task_class is TaskClass.S0 else Decimal(max_cost),
            pricing,
            task_class is TaskClass.S4,
        )
        for task_class in TaskClass
    }


class ModelRouterTests(unittest.TestCase):
    def test_deterministic_classifier_has_priority(self):
        self.assertEqual(classify(TaskProfile(deterministic=True, high_impact=True)), TaskClass.S0)
        self.assertEqual(classify(TaskProfile(security_sensitive=True)), TaskClass.S4)
        self.assertEqual(classify(TaskProfile(architecture_change=True)), TaskClass.S3)
        self.assertEqual(classify(TaskProfile(implementation=True)), TaskClass.S2)
        self.assertEqual(classify(TaskProfile()), TaskClass.S1)

    def test_s0_can_never_call_provider(self):
        provider = ScriptedProvider([])
        router = ModelRouter(routes(), {"test": provider}, UsageLedger(Decimal("1")))
        with self.assertRaises(RouterError):
            router.execute(TaskClass.S0, "lint", "t", "TESTER", "deterministic")
        self.assertEqual(provider.calls, 0)

    def test_usage_and_configured_pricing_are_recorded(self):
        provider = ScriptedProvider([ProviderResponse("ok", 1000, 500)])
        pricing = Pricing(Decimal("2"), Decimal("4"))
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(routes(pricing=pricing), {"test": provider}, ledger)
        router.execute(TaskClass.S1, "prompt", "t1", "PM", "summary")
        self.assertEqual(ledger.spent, Decimal("0.004"))
        self.assertEqual(ledger.records[0].input_tokens, 1000)

    def test_actual_provider_cost_overrides_configured_pricing(self):
        provider = ScriptedProvider([ProviderResponse("ok", 1, 1, actual_cost=Decimal("0.03"))])
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(routes(), {"test": provider}, ledger)
        router.execute(TaskClass.S1, "prompt", "t1", "PM", "provider cost")
        self.assertEqual(ledger.spent, Decimal("0.03"))

    def test_structured_response_format_is_forwarded(self):
        provider = ScriptedProvider([
            ProviderResponse(
                "{\"value\": 1}",
                1,
                1,
                actual_cost=Decimal("0"),
            )
        ])
        router = ModelRouter(
            routes(),
            {"test": provider},
            UsageLedger(Decimal("1")),
        )
        schema = {
            "type": "object",
            "properties": {
                "value": {"type": "integer"},
            },
            "required": ["value"],
        }

        router.execute(
            TaskClass.S2,
            "prompt",
            "t-format",
            "DEVELOPER",
            "structured implementation",
            response_format=schema,
        )

        self.assertEqual(
            provider.response_formats,
            [schema],
        )

    def test_transient_failure_retries_with_bounded_attempts(self):
        provider = ScriptedProvider([
            ProviderTransientError("busy"),
            ProviderResponse(
                "ok",
                1,
                1,
                actual_cost=Decimal("0.01"),
            ),
        ])
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(
            routes(retries=1),
            {"test": provider},
            ledger,
        )
        router.execute(
            TaskClass.S2,
            "prompt",
            "t2",
            "DEVELOPER",
            "local implementation",
        )
        self.assertEqual(
            [
                record.outcome
                for record in ledger.records
            ],
            ["RETRY", "SUCCESS"],
        )
        self.assertEqual(
            provider.timeouts,
            [60, 60],
        )

    def test_ollama_retry_uses_wider_bounded_timeout(self):
        provider = ScriptedProvider([
            ProviderTransientError("timed out"),
            ProviderResponse(
                "ok",
                1,
                1,
                actual_cost=Decimal("0"),
            ),
        ])
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(
            routes(
                retries=1,
                provider_name="ollama",
            ),
            {"ollama": provider},
            ledger,
        )

        router.execute(
            TaskClass.S2,
            "prompt",
            "t-ollama-timeout",
            "DEVELOPER",
            "local structured repair",
            timeout_seconds=60,
        )

        self.assertEqual(
            provider.timeouts,
            [60, 180],
        )
        self.assertEqual(
            provider.repeat_resets,
            [],
        )
        self.assertEqual(
            [
                record.outcome
                for record in ledger.records
            ],
            ["RETRY", "SUCCESS"],
        )

    def test_ollama_repeat_limit_retry_uses_adaptive_prompt(self):
        provider = ScriptedProvider([
            ProviderTransientError(
                "Ollama HTTP 500: prediction aborted, "
                "token repeat limit reached"
            ),
            ProviderResponse(
                "{\"value\": 1}",
                1,
                1,
                actual_cost=Decimal("0"),
            ),
        ])
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(
            routes(
                retries=1,
                provider_name="ollama",
            ),
            {"ollama": provider},
            ledger,
        )
        schema = {
            "type": "object",
            "properties": {
                "value": {"type": "integer"},
            },
            "required": ["value"],
        }

        router.execute(
            TaskClass.S2,
            "original structured prompt",
            "t-ollama-repeat",
            "DEVELOPER",
            "local structured repair",
            timeout_seconds=60,
            response_format=schema,
        )

        self.assertEqual(
            provider.prompts[0],
            "original structured prompt",
        )
        self.assertIn(
            "original structured prompt",
            provider.prompts[1],
        )
        self.assertIn(
            "LOCAL PROVIDER RECOVERY",
            provider.prompts[1],
        )
        self.assertIn(
            "exactly one JSON object",
            provider.prompts[1],
        )
        self.assertIn(
            "Preserve all required keys and values",
            provider.prompts[1],
        )
        self.assertEqual(
            provider.response_formats,
            [schema, "json"],
        )
        self.assertEqual(
            provider.timeouts,
            [60, 180],
        )
        self.assertEqual(
            provider.repeat_resets,
            [("model", 180)],
        )
        self.assertEqual(
            [
                record.outcome
                for record in ledger.records
            ],
            ["RETRY", "SUCCESS"],
        )

    def test_ollama_repeat_limit_non_developer_keeps_schema(self):
        provider = ScriptedProvider([
            ProviderTransientError(
                "Ollama HTTP 500: prediction aborted, "
                "token repeat limit reached"
            ),
            ProviderResponse(
                "{\"value\": 1}",
                1,
                1,
                actual_cost=Decimal("0"),
            ),
        ])
        router = ModelRouter(
            routes(
                retries=1,
                provider_name="ollama",
            ),
            {"ollama": provider},
            UsageLedger(Decimal("1")),
        )
        schema = {
            "type": "object",
            "properties": {
                "value": {"type": "integer"},
            },
            "required": ["value"],
        }

        router.execute(
            TaskClass.S1,
            "review prompt",
            "t-review-repeat",
            "REVIEWER",
            "blocking semantic review",
            timeout_seconds=60,
            response_format=schema,
        )

        self.assertEqual(
            provider.response_formats,
            [schema, schema],
        )


    def test_ollama_repeat_limit_retry_continues_when_reset_fails(self):
        provider = ScriptedProvider([
            ProviderTransientError(
                "Ollama HTTP 500: prediction aborted, "
                "token repeat limit reached"
            ),
            ProviderResponse(
                "ok",
                1,
                1,
                actual_cost=Decimal("0"),
            ),
        ])

        def failing_reset(model, timeout_seconds):
            provider.repeat_resets.append(
                (model, timeout_seconds)
            )
            raise ProviderTransientError(
                "reset unavailable"
            )

        provider.reset_after_repeat_limit = failing_reset
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(
            routes(
                retries=1,
                provider_name="ollama",
            ),
            {"ollama": provider},
            ledger,
        )

        router.execute(
            TaskClass.S2,
            "prompt",
            "t-ollama-repeat-reset-failure",
            "DEVELOPER",
            "local structured repair",
            timeout_seconds=60,
        )

        self.assertEqual(
            provider.repeat_resets,
            [("model", 180)],
        )
        self.assertEqual(
            provider.timeouts,
            [60, 180],
        )
        self.assertEqual(
            [
                record.outcome
                for record in ledger.records
            ],
            ["RETRY", "SUCCESS"],
        )

    def test_ollama_retry_timeout_is_capped(self):
        provider = ScriptedProvider([
            ProviderTransientError("timed out"),
            ProviderResponse(
                "ok",
                1,
                1,
                actual_cost=Decimal("0"),
            ),
        ])
        router = ModelRouter(
            routes(
                retries=1,
                provider_name="ollama",
            ),
            {"ollama": provider},
            UsageLedger(Decimal("1")),
        )

        router.execute(
            TaskClass.S1,
            "prompt",
            "t-ollama-cap",
            "REVIEWER",
            "blocking semantic review",
            timeout_seconds=300,
        )

        self.assertEqual(
            provider.timeouts,
            [300, 600],
        )

    def test_permanent_failure_is_recorded_without_retry(self):
        provider = ScriptedProvider([ProviderPermanentError("invalid request")])
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(routes(retries=2), {"test": provider}, ledger)
        with self.assertRaises(ProviderPermanentError):
            router.execute(TaskClass.S2, "prompt", "t2", "DEVELOPER", "local implementation")
        self.assertEqual([record.outcome for record in ledger.records], ["FAIL"])

    def test_actual_cost_over_policy_is_recorded_and_blocked(self):
        provider = ScriptedProvider([ProviderResponse("ok", 1, 1, actual_cost=Decimal("0.60"))])
        ledger = UsageLedger(Decimal("1"))
        router = ModelRouter(routes(max_cost="0.50"), {"test": provider}, ledger)
        with self.assertRaises(BudgetExceeded):
            router.execute(TaskClass.S1, "prompt", "t", "PM", "budget")
        self.assertEqual(ledger.records[0].outcome, "BUDGET_BLOCKED")
        self.assertEqual(ledger.spent, Decimal("0.60"))

    def test_budget_reservation_blocks_call_before_provider(self):
        provider = ScriptedProvider([ProviderResponse("ok", 1, 1, actual_cost=Decimal("0.01"))])
        router = ModelRouter(routes(max_cost="0.50"), {"test": provider}, UsageLedger(Decimal("0.10")))
        with self.assertRaises(BudgetExceeded):
            router.execute(TaskClass.S1, "prompt", "t", "PM", "budget")
        self.assertEqual(provider.calls, 0)

    def test_unpriced_response_is_rejected(self):
        provider = ScriptedProvider([ProviderResponse("ok", 1, 1)])
        router = ModelRouter(routes(), {"test": provider}, UsageLedger(Decimal("1")))
        with self.assertRaises(RouterError):
            router.execute(TaskClass.S1, "prompt", "t", "PM", "missing price")

    def test_benchmark_reports_quality_and_cost(self):
        provider = ScriptedProvider([
            ProviderResponse("answer alpha", 1, 1, actual_cost=Decimal("0.01")),
            ProviderResponse("answer beta", 1, 1, actual_cost=Decimal("0.02")),
        ])
        router = ModelRouter(routes(), {"test": provider}, UsageLedger(Decimal("1")))
        report = run_benchmark(router, [
            BenchmarkCase("a", TaskClass.S1, "a", "alpha"),
            BenchmarkCase("b", TaskClass.S1, "b", "missing"),
        ])
        self.assertEqual(report["quality_rate"], 0.5)
        self.assertEqual(report["cost"], "0.03")

    def test_repository_routing_config_is_complete_and_unpriced(self):
        config = Path(__file__).parents[1] / ".forgelab" / "routing.yaml"
        loaded = load_routes(config)
        self.assertEqual(set(loaded), set(TaskClass))
        self.assertIsNone(loaded[TaskClass.S1].pricing)


if __name__ == "__main__":
    unittest.main()

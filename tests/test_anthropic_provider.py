import json
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from forgelab.anthropic_provider import AnthropicProvider, _transport_schema
from forgelab.model_router import (
    BudgetExceeded, ModelRouter, ProviderPermanentError, ProviderTransientError,
    TaskClass, UsageLedger, load_routes, load_run_budget,
)
from forgelab.orchestrator import _build_local_ai_router


class _StatusError(Exception):
    def __init__(self, status_code):
        super().__init__(f"status {status_code}")
        self.status_code = status_code


class _RateLimitError(_StatusError):
    def __init__(self):
        super().__init__(429)


class _ConnectionError(Exception):
    pass


class FakeSdk:
    """Stands in for the `anthropic` module; records every request."""

    RateLimitError = _RateLimitError
    APIConnectionError = _ConnectionError
    APIStatusError = _StatusError

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.client_options = None
        self.timeouts = []

    def Anthropic(self, **options):
        self.client_options = options
        sdk = self

        class Messages:
            def create(self, **request):
                sdk.requests.append(request)
                outcome = sdk.outcomes.pop(0)
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome

        class Client:
            messages = Messages()

            def with_options(self, **options):
                sdk.timeouts.append(options["timeout"])
                return self

        return Client()


def message(text, stop_reason="end_turn", input_tokens=100, output_tokens=20, cache_read=0):
    return SimpleNamespace(
        stop_reason=stop_reason,
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        usage=SimpleNamespace(
            input_tokens=input_tokens, output_tokens=output_tokens,
            cache_read_input_tokens=cache_read, cache_creation_input_tokens=0,
        ),
    )


class AnthropicProviderTests(unittest.TestCase):
    def test_text_call_returns_text_and_token_usage_without_cost(self):
        sdk = FakeSdk([message("hello", cache_read=40)])
        response = AnthropicProvider(sdk).invoke("claude-haiku-5-5", "prompt", 45)
        self.assertEqual(response.text, "hello")
        self.assertEqual((response.input_tokens, response.output_tokens), (140, 20))
        self.assertEqual(response.cache_read_tokens, 40)
        self.assertIsNone(response.actual_cost)
        self.assertEqual(sdk.client_options, {"max_retries": 0})
        self.assertEqual(sdk.timeouts, [45.0])
        request = sdk.requests[0]
        self.assertEqual(request["model"], "claude-haiku-5-5")
        self.assertNotIn("temperature", request)
        self.assertNotIn("output_config", request)

    def test_schema_uses_structured_output_without_validator_only_keywords(self):
        schema = {
            "type": "object",
            "properties": {"items": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}}},
            "required": ["items"], "additionalProperties": False,
        }
        sdk = FakeSdk([message('{"items": ["a"]}')])
        AnthropicProvider(sdk).invoke("claude-haiku-5-5", "prompt", 30, schema)
        sent = sdk.requests[0]["output_config"]["format"]
        self.assertEqual(sent["type"], "json_schema")
        self.assertNotIn("minItems", json.dumps(sent))
        self.assertNotIn("minLength", json.dumps(sent))
        self.assertEqual(sent["schema"]["required"], ["items"])
        self.assertEqual(schema["properties"]["items"]["minItems"], 1)
        self.assertEqual(_transport_schema({"enum": ["minLength"]}), {"enum": ["minLength"]})

    def test_errors_map_to_router_retry_classes(self):
        cases = [
            (_RateLimitError(), ProviderTransientError),
            (_ConnectionError("down"), ProviderTransientError),
            (_StatusError(529), ProviderTransientError),
            (_StatusError(400), ProviderPermanentError),
            (_StatusError(401), ProviderPermanentError),
            (message("", stop_reason="refusal"), ProviderPermanentError),
            (message("partial", stop_reason="max_tokens"), ProviderPermanentError),
            (message("   "), ProviderPermanentError),
        ]
        for outcome, expected in cases:
            with self.subTest(outcome=outcome):
                with self.assertRaises(expected):
                    AnthropicProvider(FakeSdk([outcome])).invoke("claude-haiku-5-5", "prompt", 30)

    def test_invalid_structured_json_is_permanent(self):
        with self.assertRaises(ProviderPermanentError):
            AnthropicProvider(FakeSdk([message("not json")])).invoke(
                "claude-haiku-5-5", "prompt", 30, {"type": "object"})

    def test_missing_sdk_is_reported_as_permanent_error(self):
        with patch.dict("sys.modules", {"anthropic": None}):
            with self.assertRaises(ProviderPermanentError) as raised:
                AnthropicProvider().invoke("claude-haiku-5-5", "prompt", 30)
        self.assertIn("pip install anthropic", str(raised.exception))


class CloudRoutingTests(unittest.TestCase):
    CLOUD_CONFIG = Path(__file__).parents[1] / ".forgelab" / "routing.cloud.yaml"

    def test_cloud_example_is_priced_bounded_and_keeps_default_untouched(self):
        routes = load_routes(self.CLOUD_CONFIG)
        budget = load_run_budget(self.CLOUD_CONFIG)
        self.assertGreater(budget, 0)
        for task_class in (TaskClass.S1, TaskClass.S2):
            route = routes[task_class]
            self.assertEqual(route.provider, "anthropic")
            self.assertIsNotNone(route.pricing)
            self.assertLessEqual(route.max_call_cost, budget)
        default = Path(__file__).parents[1] / ".forgelab" / "routing.yaml"
        self.assertEqual(load_run_budget(default), Decimal("0"))

    def test_router_prices_cloud_calls_and_enforces_run_budget(self):
        routes = load_routes(self.CLOUD_CONFIG)
        sdk = FakeSdk([
            message("ok", input_tokens=10_000, output_tokens=2_000),
            message("too expensive", input_tokens=1_000_000, output_tokens=0),
        ])
        ledger = UsageLedger(load_run_budget(self.CLOUD_CONFIG))
        router = ModelRouter(routes, {"anthropic": AnthropicProvider(sdk)}, ledger)
        router.execute(TaskClass.S1, "prompt", "t", "PM", "cloud")
        self.assertEqual(ledger.spent, Decimal("0.002"))
        with self.assertRaises(BudgetExceeded):
            router.execute(TaskClass.S1, "prompt", "t", "PM", "cloud")
        self.assertEqual(ledger.records[-1].outcome, "BUDGET_BLOCKED")

    def test_router_builder_finds_project_config_from_another_directory(self):
        previous = os.getcwd()
        with tempfile.TemporaryDirectory() as folder:
            os.chdir(folder)
            try:
                with patch.dict(os.environ, {}, clear=False):
                    os.environ.pop("FORGELAB_ROUTING_CONFIG", None)
                    router, ledger = _build_local_ai_router()
            finally:
                os.chdir(previous)
        self.assertEqual(ledger.budget, Decimal("0"))
        self.assertEqual(set(router.providers), {"ollama"})

    def test_router_builder_adds_cloud_provider_and_budget_when_configured(self):
        with patch.dict(os.environ, {"FORGELAB_ROUTING_CONFIG": str(self.CLOUD_CONFIG)}):
            router, ledger = _build_local_ai_router()
        self.assertIn("anthropic", router.providers)
        self.assertEqual(ledger.budget, load_run_budget(self.CLOUD_CONFIG))

    def test_explicit_missing_config_still_fails(self):
        with patch.dict(os.environ, {"FORGELAB_ROUTING_CONFIG": "missing-routing.yaml"}):
            with self.assertRaises(FileNotFoundError):
                _build_local_ai_router()


if __name__ == "__main__":
    unittest.main()

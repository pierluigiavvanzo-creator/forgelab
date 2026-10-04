import json
import unittest
from decimal import Decimal
from unittest.mock import patch
from urllib.error import URLError

from forgelab.model_router import ProviderTransientError
from forgelab.ollama_provider import OllamaProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(
            self.payload
        ).encode("utf-8")


class OllamaProviderTests(unittest.TestCase):
    def test_endpoint_must_be_loopback(self):
        with self.assertRaises(ValueError):
            OllamaProvider(
                "https://example.com"
            )

    @patch("forgelab.ollama_provider.urlopen")
    def test_usage_is_returned_at_zero_cost(
        self,
        mocked,
    ):
        mocked.return_value = FakeResponse({
            "response": "plan",
            "prompt_eval_count": 123,
            "eval_count": 45,
        })

        response = OllamaProvider().invoke(
            "qwen2.5-coder:7b",
            "hello",
            10,
        )

        self.assertEqual(
            response.text,
            "plan",
        )

        self.assertEqual(
            response.input_tokens,
            123,
        )

        self.assertEqual(
            response.output_tokens,
            45,
        )

        self.assertEqual(
            response.actual_cost,
            Decimal("0"),
        )

    @patch("forgelab.ollama_provider.urlopen")
    def test_multifile_output_budget_is_bounded_and_sufficient(
        self,
        mocked,
    ):
        mocked.return_value = FakeResponse({
            "response": "{\"schema_version\": \"2.0\"}",
            "prompt_eval_count": 12,
            "eval_count": 8,
        })

        OllamaProvider().invoke(
            "qwen2.5-coder:7b",
            "return structured multi-file JSON",
            60,
        )

        request = mocked.call_args.args[0]
        payload = json.loads(
            request.data.decode("utf-8")
        )

        self.assertEqual(
            payload["options"]["num_ctx"],
            4096,
        )
        self.assertEqual(
            payload["options"]["num_predict"],
            2048,
        )
        self.assertEqual(
            payload["options"]["temperature"],
            0.1,
        )

    @patch("forgelab.ollama_provider.urlopen")
    def test_repeat_limit_recovery_uses_explicit_anti_repeat_sampling(
        self,
        mocked,
    ):
        mocked.return_value = FakeResponse({
            "response": "{\"schema_version\": \"2.1\"}",
            "prompt_eval_count": 12,
            "eval_count": 8,
        })

        schema = {
            "type": "object",
            "properties": {
                "schema_version": {
                    "type": "string",
                    "enum": ["2.1"],
                },
            },
            "required": ["schema_version"],
        }

        OllamaProvider().invoke_repeat_limit_recovery(
            "qwen2.5-coder:7b",
            "return one structured object",
            180,
            schema,
        )

        request = mocked.call_args.args[0]
        payload = json.loads(
            request.data.decode("utf-8")
        )

        self.assertEqual(
            payload["format"],
            schema,
        )
        self.assertEqual(
            payload["options"]["repeat_penalty"],
            1.1,
        )
        self.assertEqual(
            payload["options"]["repeat_last_n"],
            128,
        )
        self.assertEqual(
            payload["options"]["temperature"],
            0.1,
        )
        self.assertEqual(
            payload["options"]["num_ctx"],
            4096,
        )
        self.assertEqual(
            payload["options"]["num_predict"],
            2048,
        )

    @patch("forgelab.ollama_provider.urlopen")
    def test_structured_output_schema_is_sent_to_generate(
        self,
        mocked,
    ):
        mocked.return_value = FakeResponse({
            "response": "{\"schema_version\": \"2.0\"}",
            "prompt_eval_count": 12,
            "eval_count": 8,
        })

        schema = {
            "type": "object",
            "properties": {
                "schema_version": {
                    "type": "string",
                    "enum": ["2.0"],
                },
            },
            "required": ["schema_version"],
        }

        OllamaProvider().invoke(
            "qwen2.5-coder:7b",
            "return structured JSON",
            60,
            schema,
        )

        request = mocked.call_args.args[0]
        payload = json.loads(
            request.data.decode("utf-8")
        )

        self.assertEqual(
            payload["format"],
            schema,
        )

    @patch("forgelab.ollama_provider.urlopen")
    def test_repeat_limit_reset_unloads_local_model(
        self,
        mocked,
    ):
        mocked.return_value = FakeResponse({
            "model": "qwen2.5-coder:7b",
            "response": "",
            "done": True,
            "done_reason": "unload",
        })

        OllamaProvider().reset_after_repeat_limit(
            "qwen2.5-coder:7b",
            180,
        )

        request = mocked.call_args.args[0]
        payload = json.loads(
            request.data.decode("utf-8")
        )

        self.assertEqual(
            request.full_url,
            "http://127.0.0.1:11434/api/generate",
        )
        self.assertEqual(
            payload,
            {
                "model": "qwen2.5-coder:7b",
                "prompt": "",
                "stream": False,
                "keep_alive": 0,
            },
        )
        self.assertEqual(
            mocked.call_args.kwargs["timeout"],
            180,
        )

    @patch("forgelab.ollama_provider.urlopen")
    def test_connection_failure_is_transient(
        self,
        mocked,
    ):
        mocked.side_effect = URLError(
            "offline"
        )

        with self.assertRaises(
            ProviderTransientError
        ):
            OllamaProvider().invoke(
                "qwen2.5-coder:7b",
                "hello",
                10,
            )


if __name__ == "__main__":
    unittest.main()

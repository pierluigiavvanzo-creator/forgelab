from __future__ import annotations

import json
import unittest
from decimal import Decimal
from pathlib import Path

from forgelab.model_router import (
    ModelRouter,
    ProviderResponse,
    UsageLedger,
    load_routes,
    with_output_contract,
)

SCHEMA = {
    "type": "object",
    "properties": {"schema_version": {"type": "string", "enum": ["1.0"]}},
    "required": ["schema_version"],
    "additionalProperties": False,
}
COMPACT = json.dumps(SCHEMA, separators=(",", ":"))


class RecordingProvider:
    def __init__(self):
        self.calls = []

    def invoke(self, *args):
        self.calls.append(args)
        return ProviderResponse('{"schema_version":"1.0"}', 5, 3, actual_cost=Decimal("0"))


class CloudOutputContractTests(unittest.TestCase):
    def test_schema_is_appended_once(self):
        prompt = with_output_contract("Plan this.", SCHEMA)
        self.assertTrue(prompt.startswith("Plan this."))
        self.assertEqual(prompt.count(COMPACT), 1)
        self.assertEqual(with_output_contract(prompt, SCHEMA), prompt)

    def test_prompt_without_structured_output_is_unchanged(self):
        self.assertEqual(with_output_contract("Diagnose.", None), "Diagnose.")
        self.assertEqual(with_output_contract("Diagnose.", "json"), "Diagnose.")

    def test_every_cloud_role_receives_the_contract(self):
        for role in ("PROJECT_MANAGER", "REVIEWER", "SUPPORT"):
            with self.subTest(role=role):
                provider = RecordingProvider()
                router = ModelRouter(load_routes(Path(".forgelab/routing.yaml")),
                                     {"ollama": provider}, UsageLedger(Decimal("0")))
                router.execute_cloud_role(role, "Do the task.", "t1", 60, SCHEMA)
                model, sent_prompt, _timeout, sent_format = provider.calls[0]
                self.assertEqual(model, "gemma4:31b-cloud")
                self.assertEqual(sent_prompt.count(COMPACT), 1)
                self.assertEqual(sent_format, SCHEMA)


if __name__ == "__main__":
    unittest.main()

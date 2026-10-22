from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from forgelab.model_router import ProviderResponse
from forgelab.orchestrator import (
    _ai_review_output_contract,
    _ai_review_response_schema,
    _validate_ai_review,
    run_multi_agent,
)
from test_orchestrator import ai_plan, make_demo, request, semantic_review_pass


class ReviewerOutputContractTests(unittest.TestCase):
    def test_contract_names_every_required_field_and_embeds_the_schema(self):
        contract = _ai_review_output_contract()

        for field in ("schema_version", "status", "summary", "requirements",
                      "findings", "requirement", "evidence", "severity",
                      "category", "description"):
            self.assertIn(field, contract)

        schema_text = contract[contract.index("{"):]
        self.assertEqual(json.loads(schema_text), _ai_review_response_schema())

    def test_reviewer_prompt_carries_the_contract(self):
        developer_patch = json.dumps({
            "schema_version": "1.0",
            "path": "calculator.py",
            "old_text": "return a - b",
            "new_text": "return a + b",
            "summary": "Apply addition policy",
        })
        scripted = [
            ProviderResponse(ai_plan(), 10, 5, actual_cost=Decimal("0")),
            ProviderResponse(developer_patch, 30, 20, actual_cost=Decimal("0")),
            ProviderResponse(semantic_review_pass(), 12, 6, actual_cost=Decimal("0")),
        ]

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)
            with patch("forgelab.orchestrator.OllamaProvider.invoke",
                       side_effect=scripted) as invoke:
                run_multi_agent(
                    request(repo, objective="Fix addition",
                            operation="ai_generate", old_text="",
                            new_text="", max_repair_attempts=0),
                    root / "runs",
                )

        review_prompt = invoke.call_args_list[2].args[1]
        self.assertIn("You are the REVIEWER agent", review_prompt)
        self.assertIn(_ai_review_output_contract(), review_prompt)

    def test_validation_stays_strict_for_invented_keys(self):
        # Shape returned by gemma4:31b-cloud in PR #77 (format not enforced).
        invented = json.dumps({
            "status": "PASS",
            "blocking": False,
            "requirements": [{"id": "REQ1", "description": "x",
                              "status": "SATISFIED", "evidence": "y"}],
        })

        with self.assertRaisesRegex(ValueError, "missing fields"):
            _validate_ai_review(f"```json\n{invented}\n```")


if __name__ == "__main__":
    unittest.main()

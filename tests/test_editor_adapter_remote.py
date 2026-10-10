from __future__ import annotations

import os
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from forgelab.editor_adapter import (
    AiderCliAdapter,
    AiderCliConfig,
    EditorAdapterError,
    EditorRequest,
    _reported_cost,
    _sandbox_environment,
)
from forgelab.model_router import ModelRoute, Pricing, TaskClass, UsageLedger
from forgelab.orchestrator import AIEditorExecutionError, _run_aider_editor

PRICING = (Decimal("0.10"), Decimal("0.50"))

# Fails unless the adapter passed exactly the remote-provider contract.
FAKE_AIDER = r"""
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
model = args[args.index('--model') + 1]
metadata = json.loads(Path(args[args.index('--model-metadata-file') + 1]).read_text(encoding='utf-8'))
settings = Path(args[args.index('--model-settings-file') + 1]).read_text(encoding='utf-8')
entry = metadata[model]
checks = [
    model == 'anthropic/claude-haiku-5-5',
    entry['litellm_provider'] == 'anthropic',
    abs(entry['input_cost_per_token'] - 1e-07) < 1e-12,
    abs(entry['output_cost_per_token'] - 5e-07) < 1e-12,
    'use_temperature: false' in settings and model in settings,
    os.environ.get('ANTHROPIC_API_KEY') == 'test-key-not-real',
    'api.anthropic.com' in os.environ['NO_PROXY'],
    os.environ['HTTPS_PROXY'] == 'http://127.0.0.1:9',
    'OPENAI_API_KEY' not in os.environ,
]
if not all(checks):
    raise SystemExit(10 + checks.index(False))
Path(args[-1]).write_text('VALUE = 2\n', encoding='utf-8')
print('Tokens: 1.2k sent, 300 received. Cost: $0.0002 message, $0.0002 session.')
print('Tokens: 2.0k sent, 500 received. Cost: $0.0005 message, $0.0007 session.')
"""


class RemoteEditorTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        (self.repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.fake = root / "fake_aider.py"
        self.fake.write_text(FAKE_AIDER, encoding="utf-8")
        self.environment = patch.dict(os.environ, {
            "ANTHROPIC_API_KEY": "test-key-not-real",
            "OPENAI_API_KEY": "should-not-pass",
        })
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.folder.cleanup()

    def request(self, **overrides):
        values = dict(
            repository=self.repo, objective="Change VALUE.", allowed_paths=("app.py",),
            model="claude-haiku-5-5", timeout_seconds=30, provider="anthropic", pricing=PRICING,
        )
        values.update(overrides)
        return EditorRequest(**values)

    def adapter(self):
        return AiderCliAdapter(AiderCliConfig(executable=(sys.executable, str(self.fake))))

    def test_remote_run_passes_only_the_selected_credential_and_reports_cost(self):
        result = self.adapter().run(self.request())
        self.assertEqual(result.exit_status, 0, result.stdout + result.stderr)
        self.assertEqual(result.changed_paths, ("app.py",))
        self.assertEqual(result.reported_cost, Decimal("0.0007"))
        self.assertNotIn("test-key-not-real", " ".join(result.command))
        self.assertEqual((self.repo / "app.py").read_text(encoding="utf-8"), "VALUE = 1\n")

    def test_remote_run_requires_credential_pricing_and_known_provider(self):
        with self.assertRaisesRegex(EditorAdapterError, "pricing is required"):
            self.adapter().run(self.request(pricing=None))
        with self.assertRaisesRegex(EditorAdapterError, "not supported"):
            self.adapter().run(self.request(provider="unknown"))
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": " "}):
            with self.assertRaisesRegex(EditorAdapterError, "ANTHROPIC_API_KEY is required"):
                self.adapter().run(self.request())

    def test_local_sandbox_still_strips_the_credential(self):
        environment = _sandbox_environment(Path(self.folder.name))
        self.assertNotIn("ANTHROPIC_API_KEY", environment)
        self.assertEqual(environment["NO_PROXY"], "127.0.0.1,localhost,::1")

    def test_cost_parser_uses_last_session_total(self):
        self.assertIsNone(_reported_cost("no cost line"))
        self.assertEqual(
            _reported_cost("Cost: $0.01 message, $0.01 session.\nCost: $0.02 message, $0.03 session."),
            Decimal("0.03"),
        )

    def route(self, max_call_cost="0.05", pricing=Pricing(*PRICING)):
        return ModelRoute(TaskClass.S2, "anthropic", "claude-haiku-5-5", 1, Decimal(max_call_cost), pricing)

    def run_editor(self, ledger, route):
        with patch.dict(os.environ, {"FORGELAB_AIDER_EXECUTABLE": sys.executable}):
            with patch("forgelab.orchestrator.AiderCliConfig", lambda **_: AiderCliConfig(
                    executable=(sys.executable, str(self.fake)))):
                return _run_aider_editor(
                    repository=self.repo, objective="Change VALUE.", allowed_paths=("app.py",),
                    model=route.model, timeout_seconds=30, phase="implementation",
                    route=route, ledger=ledger,
                )

    def test_orchestrator_charges_reported_editor_cost_to_the_run_ledger(self):
        ledger = UsageLedger(Decimal("1.00"))
        self.run_editor(ledger, self.route())
        self.assertEqual(ledger.spent, Decimal("0.0007"))
        record = ledger.records[-1]
        self.assertEqual((record.provider, record.model_id, record.task_id),
                         ("aider-cli/anthropic", "claude-haiku-5-5", "implementation"))

    def test_orchestrator_charges_full_reservation_when_editor_reports_no_cost(self):
        self.fake.write_text(
            "import sys\nfrom pathlib import Path\nPath(sys.argv[-1]).write_text('VALUE = 2\\n', encoding='utf-8')\n",
            encoding="utf-8",
        )
        ledger = UsageLedger(Decimal("1.00"))
        self.run_editor(ledger, self.route())
        self.assertEqual(ledger.spent, Decimal("0.05"))
        self.assertIn("reservation charged", ledger.records[-1].error)

    def test_orchestrator_fails_and_charges_nothing_when_provider_rejects_the_call(self):
        self.fake.write_text(
            "print('litellm.AuthenticationError: AnthropicException - invalid x-api-key')\n",
            encoding="utf-8",
        )
        ledger = UsageLedger(Decimal("1.00"))
        with self.assertRaisesRegex(AIEditorExecutionError, "rejected by the anthropic provider"):
            self.run_editor(ledger, self.route())
        self.assertEqual(ledger.spent, Decimal("0"))
        self.assertEqual(ledger.records[-1].outcome, "FAIL")

    def test_orchestrator_blocks_editor_before_spending_beyond_budget_or_without_pricing(self):
        ledger = UsageLedger(Decimal("0.01"))
        with self.assertRaisesRegex(AIEditorExecutionError, "remaining run budget"):
            self.run_editor(ledger, self.route())
        with self.assertRaisesRegex(AIEditorExecutionError, "no configured pricing"):
            self.run_editor(UsageLedger(Decimal("1.00")), self.route(pricing=None))
        self.assertEqual(ledger.records, [])
        self.assertEqual((self.repo / "app.py").read_text(encoding="utf-8"), "VALUE = 1\n")


if __name__ == "__main__":
    unittest.main()

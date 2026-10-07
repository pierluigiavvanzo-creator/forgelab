import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dashboard" / "app" / "page.tsx"
START = ROOT / "Start-ForgeLab.ps1"


class DashboardRunFormFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8-sig")
        cls.start = START.read_text(encoding="utf-8-sig")

    def test_run_button_is_only_disabled_during_execution(self):
        self.assertIn(
            "disabled={creatingRun}",
            self.source,
        )
        self.assertNotIn(
            "creatingRun ||\n                  !apiConnected",
            self.source,
        )

    def test_run_form_renders_inline_validation_feedback(self):
        self.assertIn(
            "runFormError",
            self.source,
        )
        self.assertIn(
            'role="alert"',
            self.source,
        )
        self.assertIn(
            "Runner locale non collegato.",
            self.source,
        )
        self.assertIn(
            "Repository locale mancante.",
            self.source,
        )
        self.assertIn(
            "Indica almeno un file autorizzato.",
            self.source,
        )

    def test_ai_developer_uses_reuse_first_aider_engine(self):
        self.assertIn(
            'editor_engine:',
            self.source,
        )
        self.assertIn(
            '? "aider"',
            self.source,
        )
        self.assertIn(
            "REUSE-FIRST",
            self.source,
        )
        self.assertIn(
            "Aider + Ollama",
            self.source,
        )
        self.assertIn(
            "ChatGPT assistance target run: 0",
            self.source,
        )

    def test_dashboard_sends_separate_bounded_editor_timeout(self):
        self.assertIn(
            "timeout_seconds: 60",
            self.source,
        )
        self.assertIn(
            "editor_timeout_seconds:",
            self.source,
        )
        self.assertIn(
            "? 300",
            self.source,
        )

    def test_launcher_bootstraps_pinned_reuse_first_editor(self):
        self.assertIn(
            '$AiderVersion = "0.86.2"',
            self.start,
        )
        self.assertIn(
            '"aider-chat==$AiderVersion"',
            self.start,
        )
        self.assertIn(
            "FORGELAB_AIDER_EXECUTABLE",
            self.start,
        )
        self.assertIn(
            "FORGELAB_OLLAMA_URL",
            self.start,
        )
        self.assertIn(
            "Verifica contratto Aider",
            self.start,
        )
        self.assertIn(
            "pip check",
            self.start,
        )
        self.assertIn(
            "aider-freeze.txt",
            self.start,
        )
        self.assertIn(
            "Aider stabilization gate",
            self.start,
        )
        self.assertIn(
            '"test_editor_adapter.py"',
            self.start,
        )
        self.assertIn(
            '"test_orchestrator.py"',
            self.start,
        )
        self.assertIn(
            '"test_api.py"',
            self.start,
        )
        self.assertIn(
            '"test_dashboard_run_form_feedback.py"',
            self.start,
        )

    def test_dashboard_surfaces_terminal_blocker_evidence(self):
        self.assertIn(
            "BLOCCO CORRENTE",
            self.source,
        )
        self.assertIn(
            "PrewriteRecoveryFailure.json",
            self.source,
        )
        self.assertIn(
            "EditorFailure.json",
            self.source,
        )
        self.assertIn(
            "EDITOR_EXECUTION_FAILED",
            self.source,
        )
        self.assertIn(
            "ProviderFailure.json",
            self.source,
        )
        self.assertIn(
            "DETERMINISTIC_TEST_FAILED",
            self.source,
        )
        self.assertIn(
            "SEMANTIC_REVIEW_FAILED",
            self.source,
        )
        self.assertIn(
            "Apri evidenza:",
            self.source,
        )

    def test_dashboard_shows_active_runner_sha(self):
        self.assertIn(
            "runtimeSha",
            self.source,
        )
        self.assertIn(
            "runner {",
            self.source,
        )
        self.assertIn(
            "FORGELAB_RUNTIME_SHA",
            self.start,
        )

    def test_real_run_without_changes_does_not_show_internal_fallback_changes(self):
        self.assertIn(
            "Nessuna modifica applicata",
            self.source,
        )
        self.assertIn(
            "artifactCount > 0",
            self.source,
        )

    def test_dashboard_polls_accepted_run_until_terminal(self):
        self.assertIn(
            "waitForRunCompletion",
            self.source,
        )
        self.assertIn(
            "/status",
            self.source,
        )
        self.assertIn(
            "payload.terminal",
            self.source,
        )
        self.assertIn(
            "monitoraggio in corso",
            self.source,
        )
        self.assertIn(
            "setActiveRun",
            self.source,
        )

    def test_dashboard_resumes_polling_after_refresh(self):
        self.assertIn(
            "latest.terminal === false",
            self.source,
        )
        self.assertIn(
            "ripresa run",
            self.source,
        )
        self.assertIn(
            "void waitForRunCompletion",
            self.source,
        )
        self.assertIn(
            '"RunStatus.json"',
            self.source,
        )

    def test_api_failures_are_visible_inside_run_modal(self):
        self.assertIn(
            "setRunFormError(message);",
            self.source,
        )
        self.assertIn(
            "Nuova run fallita:",
            self.source,
        )


if __name__ == "__main__":
    unittest.main()

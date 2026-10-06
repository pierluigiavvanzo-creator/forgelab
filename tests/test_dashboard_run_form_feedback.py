import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dashboard" / "app" / "page.tsx"


class DashboardRunFormFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8-sig")

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

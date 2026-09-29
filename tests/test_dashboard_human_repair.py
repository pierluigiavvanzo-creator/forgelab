import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dashboard" / "app" / "page.tsx"


class DashboardHumanRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(
            encoding="utf-8-sig"
        )

    def test_repair_button_opens_feedback_dialog(self):
        self.assertIn(
            'setRepairDialog(true);',
            self.source,
        )
        self.assertIn(
            'id="repair-title"',
            self.source,
        )
        self.assertIn(
            'id="repair-feedback"',
            self.source,
        )
        self.assertNotIn(
            'decide("repair")',
            self.source,
        )

    def test_repair_posts_feedback_to_child_run_endpoint(self):
        self.assertIn(
            '}/repairs',
            self.source,
        )
        self.assertIn(
            'actor: "Product Owner"',
            self.source,
        )
        self.assertIn(
            'feedback,',
            self.source,
        )
        self.assertIn(
            'await loadRunFromApi(',
            self.source,
        )
        self.assertIn(
            'setActiveTab("overview");',
            self.source,
        )

    def test_repair_has_inline_progress_and_error_feedback(self):
        self.assertIn(
            'repairing',
            self.source,
        )
        self.assertIn(
            '"Correzione..."',
            self.source,
        )
        self.assertIn(
            'repairError',
            self.source,
        )
        self.assertIn(
            'Descrivi il fix richiesto con almeno 8 caratteri.',
            self.source,
        )


if __name__ == "__main__":
    unittest.main()

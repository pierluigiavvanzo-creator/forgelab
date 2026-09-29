import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dashboard" / "app" / "page.tsx"
CSS = ROOT / "dashboard" / "app" / "globals.css"


class DashboardGateEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(
            encoding="utf-8-sig"
        )
        cls.css = CSS.read_text(
            encoding="utf-8-sig"
        )

    def test_sidebar_controls_same_workspace_tabs(self):
        self.assertIn(
            'useState<WorkspaceTab>("overview")',
            self.page,
        )
        self.assertIn(
            'value={activeTab}',
            self.page,
        )
        self.assertIn(
            'setActiveTab("evidence");',
            self.page,
        )
        self.assertIn(
            'setActiveTab("memory");',
            self.page,
        )
        self.assertNotIn(
            'defaultValue="overview"',
            self.page,
        )

    def test_evidence_viewer_includes_exact_reviewed_patch(self):
        self.assertIn(
            '"Changes.patch"',
            self.page,
        )
        self.assertIn(
            'selectedEvidence',
            self.page,
        )
        self.assertIn(
            'setSelectedEvidence(file)',
            self.page,
        )
        self.assertIn(
            'Contenuto in sola lettura',
            self.page,
        )
        self.assertIn(
            'className="evidence-detail"',
            self.page,
        )

    def test_evidence_rows_are_visibly_selectable(self):
        self.assertIn(
            ".evidence-row-button.selected",
            self.css,
        )
        self.assertIn(
            ".evidence-detail pre",
            self.css,
        )


if __name__ == "__main__":
    unittest.main()

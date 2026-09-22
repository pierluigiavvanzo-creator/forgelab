import tempfile
import unittest
from pathlib import Path

from forgelab.memory import MemoryError, MemorySecurityError, ProjectMemory


class ProjectMemoryTests(unittest.TestCase):
    def test_snapshot_reconstructs_canonical_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "AGENTS.md").write_text("# Rules\nUse tests.\n", encoding="utf-8")
            (root / "PROJECT_STATE.md").write_text("# State\nM5 active.\n", encoding="utf-8")
            (root / "docs" / "decisions").mkdir(parents=True)
            (root / "docs" / "decisions" / "ADR-001.md").write_text("# Decision\nUse SQLite.\n", encoding="utf-8")
            snapshot = ProjectMemory(root).snapshot()
            second = ProjectMemory(root).snapshot()
            self.assertEqual(snapshot["document_count"], 3)
            self.assertEqual(len(snapshot["manifest_sha256"]), 64)
            self.assertEqual(snapshot["manifest_sha256"], second["manifest_sha256"])

    def test_oversized_memory_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "AGENTS.md").write_text("too large", encoding="utf-8")
            with self.assertRaises(MemoryError):
                ProjectMemory(root, max_file_chars=3).snapshot()

    def test_selection_keeps_mandatory_memory_and_relevant_decision(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "AGENTS.md").write_text("rules\n", encoding="utf-8")
            (root / "PROJECT_STATE.md").write_text("state\n", encoding="utf-8")
            (root / "DECISIONS.md").write_text("database choice sqlite\n", encoding="utf-8")
            (root / "ROADMAP.md").write_text("dashboard later\n", encoding="utf-8")
            bundle = ProjectMemory(root).select("change sqlite database", max_chars=200)
            paths = {item["path"] for item in bundle["documents"]}
            self.assertEqual(paths, {"AGENTS.md", "PROJECT_STATE.md", "DECISIONS.md"})

    def test_too_small_budget_never_truncates_mandatory_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "AGENTS.md").write_text("rules are mandatory", encoding="utf-8")
            with self.assertRaises(MemoryError):
                ProjectMemory(root).select("rules", max_chars=2)

    def test_potential_secret_blocks_memory_ingestion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "AGENTS.md").write_text("api_key='abcdefghijklmnop1234'\n", encoding="utf-8")
            with self.assertRaises(MemorySecurityError):
                ProjectMemory(root).snapshot()

    def test_symlink_memory_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            outside = root / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            project = root / "project"
            project.mkdir()
            try:
                (project / "AGENTS.md").symlink_to(outside)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaises(MemorySecurityError):
                ProjectMemory(project).snapshot()


if __name__ == "__main__":
    unittest.main()

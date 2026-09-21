import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from forgelab.runner import RunRequest, run_isolated
from forgelab.tools import ToolPolicyError, run_bounded, safe_target


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


class IsolatedRunnerTests(unittest.TestCase):
    def test_path_escape_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ToolPolicyError):
                safe_target(Path(folder), "../outside.py")

    def test_non_allowlisted_executable_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ToolPolicyError):
                run_bounded(["sh", "-c", "echo unsafe"], Path(folder))

    def test_real_change_runs_tests_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "demo"
            repo.mkdir()
            (repo / "calculator.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
            (repo / "test_calculator.py").write_text(
                "import unittest\nfrom calculator import add\n\n"
                "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(add(2, 3), 5)\n",
                encoding="utf-8",
            )
            git(repo, "init", "-b", "main")
            git(repo, "add", ".")
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@local",
                            "commit", "-m", "demo"], check=True, capture_output=True)
            before = git(repo, "rev-parse", "HEAD")
            request = RunRequest(
                repository=repo, objective="Fix addition",
                target_path="calculator.py", old_text="return a - b", new_text="return a + b",
                test_command=[sys.executable, "-m", "unittest", "discover", "-v"],
            )
            run_dir = run_isolated(request, root / "runs")
            summary = json.loads((run_dir / "RunSummary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "READY_FOR_DECISION")
            self.assertEqual(summary["tests"], "PASS")
            self.assertEqual(git(repo, "rev-parse", "HEAD"), before)
            self.assertIn("return a - b", (repo / "calculator.py").read_text(encoding="utf-8"))
            self.assertIn("return a + b", (run_dir / "Changes.patch").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

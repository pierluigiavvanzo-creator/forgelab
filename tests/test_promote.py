import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from forgelab.promote import PromotionError, decide
from forgelab.runner import RunRequest, run_isolated


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def demo(root: Path) -> tuple[Path, RunRequest]:
    repo = root / "demo"
    repo.mkdir()
    (repo / "calculator.py").write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )
    (repo / "test_calculator.py").write_text(
        "import unittest\nfrom calculator import add\n\n"
        "class T(unittest.TestCase):\n"
        "    def test_add(self): self.assertEqual(add(2, 3), 5)\n",
        encoding="utf-8",
    )
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@local",
            "commit",
            "-m",
            "demo",
        ],
        check=True,
        capture_output=True,
    )
    request = RunRequest(
        repository=repo,
        objective="Fix addition",
        target_path="calculator.py",
        old_text="return a - b",
        new_text="return a + b",
        test_command=[sys.executable, "-m", "unittest", "discover", "-v"],
    )
    return repo, request


class PromotionTests(unittest.TestCase):
    def test_system_cannot_self_approve(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo, request = demo(root)
            run_dir = run_isolated(request, root / "runs")
            with self.assertRaises(PromotionError):
                decide(run_dir, repo, "SYSTEM", "approve")

    def test_human_approval_creates_local_branch_commit_and_preserves_main_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo, request = demo(root)
            run_dir = run_isolated(request, root / "runs")
            source_head = git(repo, "rev-parse", "HEAD")

            result = decide(run_dir, repo, "Sergio", "approve")

            branch = f"forgelab/promote/{run_dir.name}"
            self.assertEqual(result["status"], "DONE")
            self.assertEqual(git(repo, "branch", "--show-current"), "main")
            self.assertEqual(git(repo, "rev-parse", "HEAD"), source_head)
            self.assertEqual(git(repo, "status", "--porcelain"), "")
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "return a + b",
                git(repo, "show", f"{branch}:calculator.py"),
            )

            gate = json.loads(
                (run_dir / "GateDecision.json").read_text(encoding="utf-8")
            )
            self.assertEqual(gate["decision"], "APPROVE")

            evidence = json.loads(
                (run_dir / "TestEvidence.json").read_text(encoding="utf-8")
            )
            self.assertEqual(evidence["evidence"][-1]["exit_status"], 0)
            self.assertEqual(
                evidence["evidence"][-1]["check_type"],
                "promotion_tests",
            )

            promotion = json.loads(
                (run_dir / "PromotionResult.json").read_text(encoding="utf-8")
            )
            self.assertEqual(promotion["promotion_branch"], branch)
            self.assertEqual(promotion["source_base_head"], source_head)
            self.assertEqual(promotion["tests"], "PASS")
            self.assertTrue(promotion["source_main_untouched"])
            self.assertTrue(promotion["source_head_unchanged"])
            self.assertFalse(promotion["push_executed"])
            self.assertFalse(promotion["merge_executed"])
            self.assertFalse(promotion["force_operations_executed"])
            self.assertEqual(
                promotion["commit"],
                git(repo, "rev-parse", branch),
            )

            with self.assertRaises(PromotionError):
                decide(run_dir, repo, "Sergio", "approve")

    def test_utf8_bom_patch_round_trips_through_capture_and_promotion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "demo-bom"
            repo.mkdir()

            (repo / "calculator.py").write_text(
                "def add(a, b):\n    return a - b\n",
                encoding="utf-8-sig",
            )
            (repo / "test_calculator.py").write_text(
                "import unittest\nfrom calculator import add\n\n"
                "class T(unittest.TestCase):\n"
                "    def test_add(self): self.assertEqual(add(2, 3), 5)\n",
                encoding="utf-8",
            )

            git(repo, "init", "-b", "main")
            git(repo, "add", ".")
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@local",
                    "commit",
                    "-m",
                    "demo bom",
                ],
                check=True,
                capture_output=True,
            )

            request = RunRequest(
                repository=repo,
                objective="Fix addition in UTF-8 BOM source",
                target_path="calculator.py",
                old_text="return a - b",
                new_text="return a + b",
                test_command=[
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ],
            )

            run_dir = run_isolated(request, root / "runs")
            patch_path = run_dir / "Changes.patch"
            patch_bytes = patch_path.read_bytes()

            # Correct round-trip keeps the real UTF-8 BOM bytes in diff context
            # and never persists the Windows cp1252 mojibake representation.
            self.assertIn(b"\xef\xbb\xbfdef add", patch_bytes)
            self.assertNotIn(b"\xc3\xaf\xc2\xbb\xc2\xbfdef add", patch_bytes)

            source_head = git(repo, "rev-parse", "HEAD")
            result = decide(run_dir, repo, "Product Owner", "approve")

            branch = f"forgelab/promote/{run_dir.name}"
            self.assertEqual(result["status"], "DONE")
            self.assertEqual(git(repo, "rev-parse", "HEAD"), source_head)
            self.assertEqual(git(repo, "branch", "--show-current"), "main")
            self.assertEqual(git(repo, "status", "--porcelain"), "")
            self.assertEqual(
                git(repo, "rev-parse", branch),
                json.loads(
                    (run_dir / "PromotionResult.json").read_text(
                        encoding="utf-8"
                    )
                )["commit"],
            )


    def test_rejection_preserves_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo, request = demo(root)
            run_dir = run_isolated(request, root / "runs")
            result = decide(run_dir, repo, "Sergio", "reject")
            self.assertEqual(result["status"], "CLOSED")
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(encoding="utf-8"),
            )

    def test_repair_decision_preserves_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo, request = demo(root)
            run_dir = run_isolated(request, root / "runs")
            result = decide(run_dir, repo, "Sergio", "repair")
            self.assertEqual(result["status"], "REPAIRING")
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(encoding="utf-8"),
            )

    def test_dirty_repository_blocks_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo, request = demo(root)
            run_dir = run_isolated(request, root / "runs")
            (repo / "calculator.py").write_text(
                "changed after review\n",
                encoding="utf-8",
            )
            with self.assertRaises(PromotionError):
                decide(run_dir, repo, "Sergio", "approve")

    def test_head_drift_blocks_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo, request = demo(root)
            run_dir = run_isolated(request, root / "runs")
            (repo / "drift.txt").write_text("drift\n", encoding="utf-8")
            git(repo, "add", "drift.txt")
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@local",
                    "commit",
                    "-m",
                    "drift",
                ],
                check=True,
                capture_output=True,
            )
            with self.assertRaises(PromotionError):
                decide(run_dir, repo, "Sergio", "approve")

    def test_failed_promotion_test_removes_temporary_branch_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo, request = demo(root)
            conditional = RunRequest(
                repository=repo,
                objective=request.objective,
                target_path=request.target_path,
                old_text=request.old_text,
                new_text=request.new_text,
                test_command=[
                    sys.executable,
                    "-c",
                    "import pathlib,sys; sys.exit(1 if pathlib.Path.cwd().parent.name.startswith('forgelab-promote-') else 0)",
                ],
            )
            run_dir = run_isolated(conditional, root / "runs")
            source_head = git(repo, "rev-parse", "HEAD")
            result = decide(run_dir, repo, "Sergio", "approve")
            branch = f"forgelab/promote/{run_dir.name}"

            self.assertEqual(result["status"], "REPAIRING")
            self.assertEqual(git(repo, "rev-parse", "HEAD"), source_head)
            self.assertEqual(git(repo, "status", "--porcelain"), "")
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                git(repo, "show-ref", "--verify", f"refs/heads/{branch}", check=False),
                "",
            )
            gate = json.loads(
                (run_dir / "GateDecision.json").read_text(encoding="utf-8")
            )
            self.assertEqual(gate["decision"], "REPAIR")
            self.assertFalse((run_dir / "PromotionResult.json").exists())


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from forgelab.editor_adapter import (
    EditorRequest,
    EditorResult,
)
from forgelab.editor_bakeoff import (
    EditorBakeoffRequest,
    evaluate_editor_candidate,
    run_editor_bakeoff,
)


class FixtureAdapter:
    name = "fixture-editor"

    def __init__(
        self,
        files: dict[str, str],
        *,
        exit_status: int = 0,
    ) -> None:
        self.files = files
        self.exit_status = exit_status

    def run(
        self,
        request: EditorRequest,
    ) -> EditorResult:
        before = {
            path: (
                request.repository
                / path
            ).read_text(
                encoding="utf-8",
            )
            for path
            in request.allowed_paths
        }

        changed = tuple(
            path
            for path, content
            in self.files.items()
            if before.get(path)
            != content
        )

        return EditorResult(
            engine=self.name,
            files=dict(self.files),
            changed_paths=changed,
            stdout="fixture",
            stderr="",
            exit_status=self.exit_status,
            timed_out=False,
            duration_ms=1,
            command=("fixture",),
        )


def make_repo(
    root: Path,
) -> Path:
    repo = root / "repo"
    repo.mkdir()

    (repo / "calculator.py").write_text(
        (
            "def add(a, b):\n"
            "    return a - b\n"
        ),
        encoding="utf-8",
    )

    (repo / "test_calculator.py").write_text(
        (
            "import unittest\n"
            "from calculator import add\n\n"
            "class CalculatorTests(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        ),
        encoding="utf-8",
    )

    return repo


class EditorBakeoffTests(unittest.TestCase):
    def test_good_candidate_passes_compile_tests_scope_and_security(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_repo(root)

            request = EditorBakeoffRequest(
                repository=repo,
                objective="Fix addition.",
                allowed_paths=(
                    "calculator.py",
                ),
                test_command=(
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ),
                timeout_seconds=30,
            )

            result = evaluate_editor_candidate(
                request,
                FixtureAdapter({
                    "calculator.py": (
                        "def add(a, b):\n"
                        "    return a + b\n"
                    )
                }),
            )

            self.assertEqual(
                result["status"],
                "PASS",
            )
            self.assertEqual(
                result["compile_status"],
                "PASS",
            )
            self.assertEqual(
                result["tests"]["status"],
                "PASS",
            )
            self.assertEqual(
                result["scope_review"]["status"],
                "PASS",
            )
            self.assertEqual(
                result["security_review"]["status"],
                "PASS",
            )
            self.assertEqual(
                result["product_owner_touches"],
                0,
            )
            self.assertIn(
                "+++ b/calculator.py",
                result["patch"],
            )
            self.assertEqual(
                (
                    repo
                    / "calculator.py"
                ).read_text(
                    encoding="utf-8"
                ),
                (
                    "def add(a, b):\n"
                    "    return a - b\n"
                ),
            )

    def test_compile_invalid_candidate_stops_before_tests(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_repo(root)

            request = EditorBakeoffRequest(
                repository=repo,
                objective="Fix addition.",
                allowed_paths=(
                    "calculator.py",
                ),
                test_command=(
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ),
                timeout_seconds=30,
            )

            result = evaluate_editor_candidate(
                request,
                FixtureAdapter({
                    "calculator.py":
                        "def add(a, b):\n"
                        "return a + b\n"
                }),
            )

            self.assertEqual(
                result["status"],
                "FAIL",
            )
            self.assertEqual(
                result["failure_stage"],
                "compile",
            )
            self.assertEqual(
                result["compile_status"],
                "FAIL",
            )
            self.assertIsNone(
                result["tests"],
            )

    def test_out_of_scope_returned_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_repo(root)

            request = EditorBakeoffRequest(
                repository=repo,
                objective="Fix addition.",
                allowed_paths=(
                    "calculator.py",
                ),
                test_command=(
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ),
            )

            result = evaluate_editor_candidate(
                request,
                FixtureAdapter({
                    "calculator.py": (
                        "def add(a, b):\n"
                        "    return a + b\n"
                    ),
                    "outside.py":
                        "VALUE = 1\n",
                }),
            )

            self.assertEqual(
                result["status"],
                "FAIL",
            )
            self.assertEqual(
                result["failure_stage"],
                "scope",
            )
            self.assertEqual(
                result["unexpected_paths"],
                ["outside.py"],
            )

    def test_run_editor_bakeoff_writes_machine_readable_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_repo(root)
            output = (
                root
                / "EditorBakeoff.json"
            )

            request = EditorBakeoffRequest(
                repository=repo,
                objective="Fix addition.",
                allowed_paths=(
                    "calculator.py",
                ),
                test_command=(
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ),
            )

            report = run_editor_bakeoff(
                request,
                output,
                adapters=(
                    FixtureAdapter({
                        "calculator.py": (
                            "def add(a, b):\n"
                            "    return a + b\n"
                        )
                    }),
                ),
            )

            persisted = json.loads(
                output.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                report["experiment"],
                "EDITOR_ENGINE_BAKEOFF_01",
            )
            self.assertEqual(
                persisted["candidates"][0]["status"],
                "PASS",
            )
            self.assertEqual(
                persisted["decision_gate"],
                "HUMAN_REVIEW_AFTER_COMPARATIVE_EVIDENCE",
            )
            self.assertEqual(
                persisted["semantic_review"],
                "DEFERRED_BY_ADR_002_FIRST_BOUNDARY_EXPERIMENT",
            )

    def test_request_json_accepts_windows_py_test_command(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_repo(root)
            request_path = (
                root
                / "request.json"
            )

            request_path.write_text(
                json.dumps({
                    "repository":
                        str(repo),
                    "objective":
                        "Fix addition.",
                    "allowed_paths": [
                        "calculator.py",
                    ],
                    "test_command": [
                        "py",
                        "-3.11",
                        "-m",
                        "unittest",
                        "discover",
                        "-v",
                    ],
                    "model":
                        "qwen2.5-coder:7b",
                }),
                encoding="utf-8",
            )

            request = (
                EditorBakeoffRequest
                .from_json(
                    request_path
                )
            )

            self.assertEqual(
                request.allowed_paths,
                ("calculator.py",),
            )
            self.assertEqual(
                request.test_command[0],
                "py",
            )


if __name__ == "__main__":
    unittest.main()

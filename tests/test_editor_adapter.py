from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from forgelab.editor_adapter import (
    AiderCliAdapter,
    AiderCliConfig,
    EditorAdapterError,
    EditorRequest,
)


class EditorAdapterTests(unittest.TestCase):
    def test_aider_runs_in_sandbox_and_leaves_source_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()

            source = repo / "app.py"
            source.write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            fake = root / "fake_aider.py"
            fake.write_text(
                (
                    "from pathlib import Path\n"
                    "import sys\n"
                    "target = Path(sys.argv[-1])\n"
                    "target.write_text('VALUE = 2\\n', encoding='utf-8')\n"
                ),
                encoding="utf-8",
            )

            adapter = AiderCliAdapter(
                AiderCliConfig(
                    executable=(
                        sys.executable,
                        str(fake),
                    )
                )
            )

            result = adapter.run(
                EditorRequest(
                    repository=repo,
                    objective="Change VALUE to 2.",
                    allowed_paths=("app.py",),
                    timeout_seconds=30,
                )
            )

            self.assertEqual(
                result.exit_status,
                0,
            )
            self.assertFalse(
                result.timed_out
            )
            self.assertEqual(
                result.changed_paths,
                ("app.py",),
            )
            self.assertEqual(
                result.files["app.py"],
                "VALUE = 2\n",
            )
            self.assertEqual(
                source.read_text(
                    encoding="utf-8"
                ),
                "VALUE = 1\n",
            )

            command = list(
                result.command
            )
            self.assertIn(
                "--no-git",
                command,
            )
            self.assertIn(
                "--no-auto-commits",
                command,
            )
            self.assertIn(
                "--no-auto-lint",
                command,
            )
            self.assertIn(
                "--no-auto-test",
                command,
            )
            self.assertIn(
                "--no-suggest-shell-commands",
                command,
            )
            self.assertIn(
                "--analytics-disable",
                command,
            )
            self.assertIn(
                "--no-check-update",
                command,
            )
            self.assertIn(
                "--message-file",
                command,
            )
            self.assertIn(
                "ollama/qwen2.5-coder:7b",
                command,
            )

    def test_aider_rejects_read_only_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()

            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )
            (repo / "context.py").write_text(
                "CONTEXT = 1\n",
                encoding="utf-8",
            )

            fake = root / "fake_aider.py"
            fake.write_text(
                (
                    "from pathlib import Path\n"
                    "import sys\n"
                    "args = sys.argv[1:]\n"
                    "idx = args.index('--read')\n"
                    "Path(args[idx + 1]).write_text("
                    "'CONTEXT = 2\\n', encoding='utf-8')\n"
                ),
                encoding="utf-8",
            )

            adapter = AiderCliAdapter(
                AiderCliConfig(
                    executable=(
                        sys.executable,
                        str(fake),
                    )
                )
            )

            with self.assertRaisesRegex(
                EditorAdapterError,
                "read-only",
            ):
                adapter.run(
                    EditorRequest(
                        repository=repo,
                        objective="Change VALUE to 2.",
                        allowed_paths=(
                            "app.py",
                        ),
                        read_only_paths=(
                            "context.py",
                        ),
                        timeout_seconds=30,
                    )
                )

            self.assertEqual(
                (
                    repo
                    / "context.py"
                ).read_text(
                    encoding="utf-8"
                ),
                "CONTEXT = 1\n",
            )

    def test_aider_rejects_scope_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            adapter = AiderCliAdapter(
                AiderCliConfig(
                    executable=(
                        sys.executable,
                    )
                )
            )

            with self.assertRaisesRegex(
                EditorAdapterError,
                "escapes",
            ):
                adapter.run(
                    EditorRequest(
                        repository=repo,
                        objective="Change file.",
                        allowed_paths=(
                            "../outside.py",
                        ),
                    )
                )


if __name__ == "__main__":
    unittest.main()

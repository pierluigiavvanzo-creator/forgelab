from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from forgelab.editor_adapter import (
    AiderCliAdapter,
    AiderCliConfig,
    EditorAdapterError,
    EditorRequest,
    _sandbox_environment,
)


class EditorAdapterTests(unittest.TestCase):
    def test_sandbox_forces_utf8_without_changing_parent_environment(self):
        with patch.dict(os.environ, {"PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"}):
            environment = _sandbox_environment(Path("tool-home"))
            self.assertEqual(environment.get("PYTHONUTF8"), "1")
            self.assertEqual(environment.get("PYTHONIOENCODING"), "utf-8")
            self.assertEqual(os.environ["PYTHONUTF8"], "0")
            self.assertEqual(os.environ["PYTHONIOENCODING"], "cp1252")

    def test_bom_output_is_utf8_safe_and_source_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            original = b"\xef\xbb\xbfVALUE = 1\n"
            (repo / "app.py").write_bytes(original)
            editor = AiderCliAdapter(AiderCliConfig(executable=(sys.executable, "-c", (
                "from pathlib import Path; import sys; "
                "text = Path('app.py').read_text(encoding='utf-8'); "
                "print(text, end=''); print(text, end='', file=sys.stderr); "
                "Path('app.py').write_text(text.replace('1', '2'), encoding='utf-8')"
            ))))
            result = editor.run(EditorRequest(repo, "Change VALUE", ("app.py",), timeout_seconds=10))
            self.assertEqual(result.exit_status, 0, result.stderr)
            self.assertFalse(result.timed_out)
            self.assertIn("\ufeffVALUE = 1", result.stdout)
            self.assertIn("\ufeffVALUE = 1", result.stderr)
            self.assertEqual(result.files["app.py"], "\ufeffVALUE = 2\n")
            self.assertEqual((repo / "app.py").read_bytes(), original)

    def test_editor_crash_cannot_wait_on_inherited_interactive_stdin(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            original = b"\xef\xbb\xbfVALUE = 1\n"
            (repo / "app.py").write_bytes(original)
            crash = (
                "import sys\n"
                "print('crash stdout', flush=True)\n"
                "print('crash stderr', file=sys.stderr, flush=True)\n"
                "try:\n"
                "    input('Open a GitHub Issue? (Y/n) ')\n"
                "except EOFError:\n"
                "    print('stdin EOF', file=sys.stderr)\n"
                "    sys.exit(7)\n"
                "raise RuntimeError('interactive input must not be available')\n"
            )
            worker = (
                "import dataclasses, json, sys\n"
                "from pathlib import Path\n"
                "from forgelab.editor_adapter import AiderCliAdapter, AiderCliConfig, EditorRequest\n"
                f"editor = AiderCliAdapter(AiderCliConfig(executable=(sys.executable, '-c', {crash!r})))\n"
                f"result = editor.run(EditorRequest(Path({str(repo)!r}), 'Crash', ('app.py',), timeout_seconds=3))\n"
                "print(json.dumps(dataclasses.asdict(result)))\n"
            )
            environment = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
            # Keep the writer open while waiting: inherited stdin would block until timeout.
            with subprocess.Popen(
                [sys.executable, "-c", worker], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
            ) as process:
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    self.fail("adapter worker did not finish")
                output = process.stdout.read().decode("utf-8")
                self.assertEqual(process.returncode, 0, process.stderr.read().decode("utf-8"))
            result = json.loads(output)
            self.assertFalse(result["timed_out"], result)
            self.assertEqual(result["exit_status"], 7)
            self.assertIn("crash stdout", result["stdout"])
            self.assertIn("crash stderr", result["stderr"])
            self.assertIn("stdin EOF", result["stderr"])
            self.assertEqual((repo / "app.py").read_bytes(), original)

    def test_aider_noop_detects_identical_files_and_preserves_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            source = repo / "app.py"
            source.write_text("VALUE = 1\n", encoding="utf-8")
            fake = root / "fake_aider.py"
            fake.write_text("import sys\nprint('No edits necessary')\nprint('diagnostic stderr', file=sys.stderr)\n", encoding="utf-8")
            result = AiderCliAdapter(AiderCliConfig(executable=(sys.executable, str(fake)))).run(
                EditorRequest(repository=repo, objective="Keep VALUE", allowed_paths=("app.py",), timeout_seconds=30))
            self.assertEqual(result.changed_paths, ())
            self.assertEqual(result.files, {"app.py": "VALUE = 1\n"})
            self.assertIn("No edits necessary", result.stdout)
            self.assertIn("diagnostic stderr", result.stderr)
            self.assertEqual(source.read_text(encoding="utf-8"), "VALUE = 1\n")

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
            for required_flag in (
                "--no-git",
                "--no-gitignore",
                "--no-add-gitignore-files",
                "--no-auto-commits",
                "--no-dirty-commits",
                "--no-auto-lint",
                "--no-auto-test",
                "--no-watch-files",
                "--no-cache-prompts",
                "--no-restore-chat-history",
                "--no-suggest-shell-commands",
                "--no-notifications",
                "--no-detect-urls",
                "--no-pretty",
                "--no-stream",
                "--no-show-model-warnings",
                "--no-check-model-accepts-settings",
                "--analytics-disable",
                "--no-check-update",
                "--no-show-release-notes",
                "--model-metadata-file",
                "--timeout",
                "--map-tokens",
            ):
                self.assertIn(
                    required_flag,
                    command,
                )
            self.assertIn(
                "--chat-history-file",
                command,
            )
            self.assertIn(
                "--input-history-file",
                command,
            )
            self.assertIn(
                "ollama_chat/qwen2.5-coder:7b",
                command,
            )

    def test_aider_receives_valid_empty_yaml_config(self):
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
                    "args = sys.argv[1:]\n"
                    "config = Path(args[args.index('--config') + 1])\n"
                    "if config.read_text(encoding='utf-8') != '{}\\n':\n"
                    "    print('invalid config', file=sys.stderr)\n"
                    "    raise SystemExit(2)\n"
                    "target = Path(args[-1])\n"
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

    def test_sandbox_environment_strips_paid_provider_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(
                "os.environ",
                {
                    "OPENAI_API_KEY": "should-not-pass",
                    "ANTHROPIC_API_KEY": "should-not-pass",
                    "PATH": "keep-me",
                    "AIDER_MODEL": "ignore-user-config",
                    "GOOGLE_API_KEY": "should-not-pass",
                    "AWS_ACCESS_KEY_ID": "should-not-pass",
                    "AWS_SECRET_ACCESS_KEY": "should-not-pass",
                    "GITHUB_TOKEN": "should-not-pass",
                    "HF_TOKEN": "should-not-pass",
                    "FORGELAB_API_TOKEN": "should-not-pass",
                    "STRIPE_SECRET_KEY": "should-not-pass",
                    "DATABASE_URL": "should-not-pass",
                    "PYTHONPATH": "should-not-pass",
                    "VIRTUAL_ENV": "should-not-pass",
                },
                clear=True,
            ):
                environment = _sandbox_environment(Path(folder))

            self.assertNotIn("OPENAI_API_KEY", environment)
            self.assertNotIn("ANTHROPIC_API_KEY", environment)
            self.assertNotIn("AIDER_MODEL", environment)
            self.assertNotIn("GOOGLE_API_KEY", environment)
            self.assertNotIn("AWS_ACCESS_KEY_ID", environment)
            self.assertNotIn("AWS_SECRET_ACCESS_KEY", environment)
            self.assertNotIn("GITHUB_TOKEN", environment)
            self.assertNotIn("HF_TOKEN", environment)
            self.assertNotIn("FORGELAB_API_TOKEN", environment)
            self.assertNotIn("STRIPE_SECRET_KEY", environment)
            self.assertNotIn("DATABASE_URL", environment)
            self.assertNotIn("PYTHONPATH", environment)
            self.assertNotIn("VIRTUAL_ENV", environment)
            self.assertEqual(environment["PATH"], "keep-me")
            self.assertEqual(environment["AIDER_ANALYTICS"], "0")
            self.assertEqual(
                environment["HOME"],
                folder,
            )
            self.assertEqual(
                environment["USERPROFILE"],
                folder,
            )
            self.assertEqual(
                environment["OLLAMA_API_BASE"],
                "http://127.0.0.1:11434",
            )
            self.assertEqual(
                environment["HTTPS_PROXY"],
                "http://127.0.0.1:9",
            )
            self.assertEqual(
                environment["NO_PROXY"],
                "127.0.0.1,localhost,::1",
            )

    def test_external_ollama_endpoint_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(
                "os.environ",
                {
                    "FORGELAB_OLLAMA_URL":
                        "https://example.com:11434",
                },
                clear=True,
            ):
                with self.assertRaisesRegex(
                    EditorAdapterError,
                    "loopback-only",
                ):
                    _sandbox_environment(
                        Path(folder)
                    )

    def test_aider_history_files_are_routed_to_tool_home(self):
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
                    "args = sys.argv[1:]\n"
                    "chat = Path(args[args.index('--chat-history-file') + 1])\n"
                    "inp = Path(args[args.index('--input-history-file') + 1])\n"
                    "chat.write_text('chat\\n', encoding='utf-8')\n"
                    "inp.write_text('input\\n', encoding='utf-8')\n"
                    "target = Path(args[-1])\n"
                    "target.write_text('VALUE = 2\\n', encoding='utf-8')\n"
                    "cwd = Path.cwd().resolve()\n"
                    "if chat.resolve().parent == cwd or inp.resolve().parent == cwd:\n"
                    "    print('history leaked into workspace', file=sys.stderr)\n"
                    "    raise SystemExit(9)\n"
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

            self.assertEqual(result.exit_status, 0)
            self.assertEqual(
                result.changed_paths,
                ("app.py",),
            )
            self.assertEqual(
                result.files["app.py"],
                "VALUE = 2\n",
            )

            command = list(result.command)
            chat_index = command.index(
                "--chat-history-file"
            )
            input_index = command.index(
                "--input-history-file"
            )
            chat_path = Path(
                command[chat_index + 1]
            )
            input_path = Path(
                command[input_index + 1]
            )

            self.assertEqual(
                chat_path.parent.name,
                "tool-home",
            )
            self.assertEqual(
                input_path.parent.name,
                "tool-home",
            )
            self.assertEqual(
                source.read_text(
                    encoding="utf-8",
                ),
                "VALUE = 1\n",
            )


    def test_aider_tool_metadata_isolated_from_workspace(self):
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
                    "import os\n"
                    "from pathlib import Path\n"
                    "import sys\n"
                    "home = Path(os.environ['HOME'])\n"
                    "cache = home / '.aider' / 'caches'\n"
                    "cache.mkdir(parents=True, exist_ok=True)\n"
                    "(home / '.aider' / 'analytics.json').write_text("
                    "'{}\\n', encoding='utf-8')\n"
                    "(cache / 'model_prices_and_context_window.json').write_text("
                    "'{}\\n', encoding='utf-8')\n"
                    "(home / '.aider' / 'installs.json').write_text("
                    "'{}\\n', encoding='utf-8')\n"
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
                result.changed_paths,
                ("app.py",),
            )
            self.assertEqual(
                result.files["app.py"],
                "VALUE = 2\n",
            )
            self.assertEqual(
                source.read_text(
                    encoding="utf-8",
                ),
                "VALUE = 1\n",
            )

    def test_aider_rejects_hidden_workspace_file_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            fake = root / "fake_aider.py"
            fake.write_text(
                (
                    "from pathlib import Path\n"
                    "Path('.unexpected').write_text("
                    "'tool leak\\n', encoding='utf-8')\n"
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
                "created files",
            ):
                adapter.run(
                    EditorRequest(
                        repository=repo,
                        objective="Change VALUE.",
                        allowed_paths=("app.py",),
                        timeout_seconds=30,
                    )
                )

            self.assertFalse(
                (repo / ".unexpected").exists()
            )

    def test_aider_rejects_new_source_file_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")

            fake = root / "fake_aider.py"
            fake.write_text(
                (
                    "from pathlib import Path\n"
                    "Path('outside.py').write_text('VALUE = 2\\n', encoding='utf-8')\n"
                ),
                encoding="utf-8",
            )
            adapter = AiderCliAdapter(AiderCliConfig(
                executable=(sys.executable, str(fake))
            ))

            with self.assertRaisesRegex(EditorAdapterError, "created files"):
                adapter.run(EditorRequest(
                    repository=repo,
                    objective="Change VALUE.",
                    allowed_paths=("app.py",),
                    timeout_seconds=30,
                ))

            self.assertFalse((repo / "outside.py").exists())

    def test_aider_model_metadata_is_local_and_minimal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            fake = root / "fake_aider.py"
            fake.write_text(
                (
                    "import json\n"
                    "from pathlib import Path\n"
                    "import sys\n"
                    "args = sys.argv[1:]\n"
                    "metadata = Path(args[args.index('--model-metadata-file') + 1])\n"
                    "data = json.loads(metadata.read_text(encoding='utf-8'))\n"
                    "model = 'ollama_chat/qwen2.5-coder:7b'\n"
                    "entry = data.get(model, {})\n"
                    "if entry.get('litellm_provider') != 'ollama_chat':\n"
                    "    raise SystemExit(7)\n"
                    "if entry.get('mode') != 'chat':\n"
                    "    raise SystemExit(8)\n"
                    "target = Path(args[-1])\n"
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
                    objective="Change VALUE.",
                    allowed_paths=("app.py",),
                    timeout_seconds=30,
                )
            )

            self.assertEqual(
                result.exit_status,
                0,
            )
            self.assertEqual(
                result.changed_paths,
                ("app.py",),
            )

    def test_aider_timeout_is_bounded_and_output_is_normalized(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )
            adapter = AiderCliAdapter(
                AiderCliConfig(
                    executable=("fake-aider",)
                )
            )

            timeout = subprocess.TimeoutExpired(
                cmd=["fake-aider"],
                timeout=30,
                output=b"partial stdout",
                stderr=b"partial stderr",
            )
            with patch(
                "forgelab.editor_adapter.subprocess.run",
                side_effect=timeout,
            ):
                result = adapter.run(
                    EditorRequest(
                        repository=repo,
                        objective="Change VALUE.",
                        allowed_paths=("app.py",),
                        timeout_seconds=30,
                    )
                )

            self.assertTrue(
                result.timed_out
            )
            self.assertEqual(
                result.exit_status,
                124,
            )
            self.assertEqual(
                result.stdout,
                "partial stdout",
            )
            self.assertEqual(
                result.stderr,
                "partial stderr",
            )

    def test_aider_os_execution_error_is_governed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )
            adapter = AiderCliAdapter(
                AiderCliConfig(
                    executable=("fake-aider",)
                )
            )

            with patch(
                "forgelab.editor_adapter.subprocess.run",
                side_effect=PermissionError(
                    "execution denied"
                ),
            ):
                with self.assertRaisesRegex(
                    EditorAdapterError,
                    "could not be executed",
                ):
                    adapter.run(
                        EditorRequest(
                            repository=repo,
                            objective="Change VALUE.",
                            allowed_paths=("app.py",),
                            timeout_seconds=30,
                        )
                    )

    def test_aider_deleted_writable_file_is_governed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )

            fake = root / "fake_aider.py"
            fake.write_text(
                (
                    "from pathlib import Path\n"
                    "import sys\n"
                    "Path(sys.argv[-1]).unlink()\n"
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
                "disappeared from sandbox",
            ):
                adapter.run(
                    EditorRequest(
                        repository=repo,
                        objective="Change VALUE.",
                        allowed_paths=("app.py",),
                        timeout_seconds=30,
                    )
                )

    def test_non_utf8_authorized_file_is_governed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = root / "repo"
            repo.mkdir()
            (repo / "app.py").write_bytes(
                b"\xff\xfe\x00\x00"
            )

            adapter = AiderCliAdapter(
                AiderCliConfig(
                    executable=("fake-aider",)
                )
            )

            with self.assertRaisesRegex(
                EditorAdapterError,
                "UTF-8",
            ):
                adapter.run(
                    EditorRequest(
                        repository=repo,
                        objective="Change VALUE.",
                        allowed_paths=("app.py",),
                        timeout_seconds=30,
                    )
                )

    def test_editor_timeout_contract_rejects_invalid_values(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            (repo / "app.py").write_text(
                "VALUE = 1\n",
                encoding="utf-8",
            )
            adapter = AiderCliAdapter(
                AiderCliConfig(
                    executable=("fake-aider",)
                )
            )
            for timeout_seconds in (0, 601):
                with self.subTest(
                    timeout_seconds=timeout_seconds
                ):
                    with self.assertRaisesRegex(
                        EditorAdapterError,
                        "timeout_seconds",
                    ):
                        adapter.run(
                            EditorRequest(
                                repository=repo,
                                objective="Change VALUE.",
                                allowed_paths=("app.py",),
                                timeout_seconds=timeout_seconds,
                            )
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

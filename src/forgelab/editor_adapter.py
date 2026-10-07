from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse


class EditorAdapterError(RuntimeError):
    pass


@dataclass(frozen=True)
class EditorRequest:
    repository: Path
    objective: str
    allowed_paths: tuple[str, ...]
    model: str = "qwen2.5-coder:7b"
    timeout_seconds: int = 300
    read_only_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class EditorResult:
    engine: str
    files: dict[str, str]
    changed_paths: tuple[str, ...]
    stdout: str
    stderr: str
    exit_status: int
    timed_out: bool
    duration_ms: int
    command: tuple[str, ...]


class EditorAdapter(Protocol):
    name: str

    def run(self, request: EditorRequest) -> EditorResult:
        ...


def _source_file(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if (
        not relative_path.strip()
        or relative.is_absolute()
        or ".." in relative.parts
        or ".git" in {part.lower() for part in relative.parts}
    ):
        raise EditorAdapterError(
            f"editor path escapes authorized scope: {relative_path}"
        )
    resolved_root = root.resolve()
    target = (resolved_root / relative).resolve()
    try:
        target.relative_to(resolved_root)
    except ValueError as error:
        raise EditorAdapterError(
            f"editor path escapes authorized scope: {relative_path}"
        ) from error
    if not target.is_file():
        raise EditorAdapterError(
            f"editor file does not exist: {relative_path}"
        )
    return target


def _copy_authorized(
    source_root: Path,
    sandbox: Path,
    relative_path: str,
) -> None:
    source = _source_file(source_root, relative_path)
    target = sandbox / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _read_files(root: Path, paths: tuple[str, ...]) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in paths:
        target = root / path
        try:
            files[path] = target.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise EditorAdapterError(
                f"editor file disappeared from sandbox: {path}"
            ) from error
        except UnicodeError as error:
            raise EditorAdapterError(
                f"editor file must be UTF-8 text: {path}"
            ) from error
        except OSError as error:
            raise EditorAdapterError(
                f"editor file could not be read: {path}: {error}"
            ) from error
    return files


def _process_output(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


_SAFE_INHERITED_ENV_NAMES = {
    "COMSPEC",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "NUMBER_OF_PROCESSORS",
    "OS",
    "PATH",
    "PATHEXT",
    "SYSTEMDRIVE",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "TZ",
    "WINDIR",
}

_LOOPBACK_HOSTS = {
    "127.0.0.1",
    "localhost",
    "::1",
}

_BLOCKED_PROXY = "http://127.0.0.1:9"

def _ollama_url() -> str:
    raw = os.environ.get(
        "FORGELAB_OLLAMA_URL",
        "http://127.0.0.1:11434",
    ).strip()
    parsed = urlparse(raw)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in _LOOPBACK_HOSTS
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise EditorAdapterError(
            "FORGELAB_OLLAMA_URL must use a loopback-only HTTP endpoint"
        )
    return raw.rstrip("/")


def _sandbox_environment(tool_home: Path) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in _SAFE_INHERITED_ENV_NAMES
    }
    ollama_url = _ollama_url()
    environment.update({
        "HOME": str(tool_home),
        "USERPROFILE": str(tool_home),
        "AIDER_ANALYTICS": "0",
        "OLLAMA_API_BASE": ollama_url,
        "HTTP_PROXY": _BLOCKED_PROXY,
        "HTTPS_PROXY": _BLOCKED_PROXY,
        "ALL_PROXY": _BLOCKED_PROXY,
        "NO_PROXY": "127.0.0.1,localhost,::1",
        "http_proxy": _BLOCKED_PROXY,
        "https_proxy": _BLOCKED_PROXY,
        "all_proxy": _BLOCKED_PROXY,
        "no_proxy": "127.0.0.1,localhost,::1",
    })
    return environment


@dataclass(frozen=True)
class AiderCliConfig:
    executable: tuple[str, ...] = ("aider",)
    edit_format: str = "whole"


class AiderCliAdapter:
    """Edit disposable copies; never write the governed workspace."""

    name = "aider-cli"

    def __init__(self, config: AiderCliConfig | None = None) -> None:
        self.config = config or AiderCliConfig()

    @staticmethod
    def _model(model: str) -> str:
        model = model.strip()
        if not model:
            raise EditorAdapterError("editor model must not be empty")
        if model.startswith(("ollama/", "ollama_chat/")):
            return model
        return f"ollama_chat/{model}"

    @staticmethod
    def _prompt(request: EditorRequest) -> str:
        writable = "\n".join(f"- {path}" for path in request.allowed_paths)
        return f"""You are the bounded code editor inside ForgeLab.

Objective:
{request.objective}

Writable files:
{writable}

Edit only those files. Do not create or delete files, run shell commands,
install dependencies, or claim tests ran. Preserve unrelated behavior and
exact quantitative requirements. Make the smallest complete implementation,
including tests only when they are inside the writable set.
"""

    def run(self, request: EditorRequest) -> EditorResult:
        if not request.allowed_paths:
            raise EditorAdapterError("at least one writable path is required")
        if len(set(request.allowed_paths)) != len(request.allowed_paths):
            raise EditorAdapterError("writable paths must be unique")
        if set(request.allowed_paths) & set(request.read_only_paths):
            raise EditorAdapterError(
                "writable and read-only paths must not overlap"
            )
        if not self.config.executable:
            raise EditorAdapterError("Aider executable must not be empty")
        if request.timeout_seconds < 1 or request.timeout_seconds > 600:
            raise EditorAdapterError(
                "editor timeout_seconds must be between 1 and 600"
            )

        source_root = request.repository.resolve()
        if not source_root.is_dir():
            raise EditorAdapterError(
                f"editor repository does not exist: {source_root}"
            )

        with tempfile.TemporaryDirectory(
            prefix="forgelab-editor-aider-"
        ) as folder:
            sandbox_root = Path(folder)
            workspace = sandbox_root / "workspace"
            tool_home = sandbox_root / "tool-home"
            workspace.mkdir()
            tool_home.mkdir()

            visible_paths = request.allowed_paths + request.read_only_paths
            resolved_scope: dict[str, str] = {}
            for path in visible_paths:
                source = _source_file(source_root, path)
                identity = os.path.normcase(str(source.resolve()))
                previous = resolved_scope.get(identity)
                if previous is not None and previous != path:
                    raise EditorAdapterError(
                        "editor paths alias the same source file: "
                        f"{previous}, {path}"
                    )
                resolved_scope[identity] = path
                _copy_authorized(source_root, workspace, path)

            before_writable = _read_files(
                workspace,
                request.allowed_paths,
            )
            before_read_only = _read_files(
                workspace,
                request.read_only_paths,
            )

            prompt_file = tool_home / ".forgelab-aider-prompt.txt"
            config_file = tool_home / ".forgelab-aider.conf.yml"
            env_file = tool_home / ".forgelab-aider.env"
            chat_history_file = (
                tool_home / ".aider.chat.history.md"
            )
            input_history_file = (
                tool_home / ".aider.input.history"
            )
            model_metadata_file = (
                tool_home / ".forgelab-aider.model.metadata.json"
            )
            prompt_file.write_text(
                self._prompt(request),
                encoding="utf-8",
            )
            config_file.write_text(
                "{}\n",
                encoding="utf-8",
            )
            env_file.write_text(
                "",
                encoding="utf-8",
            )
            model_name = self._model(request.model)
            model_metadata_file.write_text(
                json.dumps(
                    {
                        model_name: {
                            "litellm_provider": "ollama_chat",
                            "mode": "chat",
                        }
                    },
                    indent=2,
                    sort_keys=True,
                ) + "\n",
                encoding="utf-8",
            )

            command = [
                *self.config.executable,
                "--model", model_name,
                "--edit-format", self.config.edit_format,
                "--timeout", str(request.timeout_seconds),
                "--map-tokens", "0",
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
                "--yes-always",
                "--config", str(config_file),
                "--env-file", str(env_file),
                "--model-metadata-file",
                str(model_metadata_file),
                "--message-file", str(prompt_file),
                "--chat-history-file",
                str(chat_history_file),
                "--input-history-file",
                str(input_history_file),
            ]
            for path in request.read_only_paths:
                command.extend(["--read", path])
            command.extend(request.allowed_paths)

            environment = _sandbox_environment(tool_home)
            started = time.monotonic()
            try:
                completed = subprocess.run(
                    command,
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=environment,
                    timeout=request.timeout_seconds,
                    check=False,
                )
                exit_status = completed.returncode
                stdout, stderr = completed.stdout, completed.stderr
                timed_out = False
            except FileNotFoundError as error:
                raise EditorAdapterError(
                    f"Aider CLI is not installed: {self.config.executable[0]}"
                ) from error
            except subprocess.TimeoutExpired as error:
                return EditorResult(
                    self.name,
                    before_writable,
                    (),
                    _process_output(error.stdout),
                    _process_output(error.stderr),
                    124,
                    True,
                    int((time.monotonic() - started) * 1000),
                    tuple(command),
                )
            except OSError as error:
                raise EditorAdapterError(
                    f"Aider CLI could not be executed: {error}"
                ) from error

            if (
                _read_files(
                    workspace,
                    request.read_only_paths,
                )
                != before_read_only
            ):
                raise EditorAdapterError(
                    "Aider modified read-only sandbox files"
                )

            allowed_visible = set(visible_paths)
            created = sorted(
                str(
                    path.relative_to(workspace)
                ).replace("\\", "/")
                for path in workspace.rglob("*")
                if (
                    path.is_file()
                    and str(
                        path.relative_to(workspace)
                    ).replace("\\", "/")
                    not in allowed_visible
                )
            )
            if created:
                raise EditorAdapterError(
                    "Aider created files outside authorized scope: "
                    + ", ".join(created)
                )

            after = _read_files(
                workspace,
                request.allowed_paths,
            )
            changed = tuple(
                path for path in request.allowed_paths
                if after[path] != before_writable[path]
            )
            return EditorResult(
                self.name,
                after,
                changed,
                stdout,
                stderr,
                exit_status,
                timed_out,
                int((time.monotonic() - started) * 1000),
                tuple(command),
            )

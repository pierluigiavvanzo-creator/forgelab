from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class EditorAdapterError(RuntimeError):
    pass


@dataclass(frozen=True)
class EditorRequest:
    repository: Path
    objective: str
    allowed_paths: tuple[str, ...]
    model: str = "qwen2.5-coder:7b"
    timeout_seconds: int = 180
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
    return {
        path: (root / path).read_text(encoding="utf-8")
        for path in paths
    }


_PAID_PROVIDER_KEY_NAMES = {
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "CEREBRAS_API_KEY",
    "COHERE_API_KEY",
    "DEEPSEEK_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "MISTRAL_API_KEY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "TOGETHERAI_API_KEY",
}


def _sandbox_environment(sandbox: Path) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if (
            not key.upper().startswith("AIDER_")
            and key.upper() not in _PAID_PROVIDER_KEY_NAMES
        )
    }
    environment.update({
        "HOME": str(sandbox),
        "USERPROFILE": str(sandbox),
        "AIDER_ANALYTICS": "0",
        "OLLAMA_API_BASE": os.environ.get(
            "FORGELAB_OLLAMA_URL",
            "http://127.0.0.1:11434",
        ),
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
        return f"ollama/{model}"

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

        source_root = request.repository.resolve()
        if not source_root.is_dir():
            raise EditorAdapterError(
                f"editor repository does not exist: {source_root}"
            )

        with tempfile.TemporaryDirectory(
            prefix="forgelab-editor-aider-"
        ) as folder:
            sandbox = Path(folder)
            visible_paths = request.allowed_paths + request.read_only_paths
            for path in visible_paths:
                _copy_authorized(source_root, sandbox, path)

            before_writable = _read_files(sandbox, request.allowed_paths)
            before_read_only = _read_files(sandbox, request.read_only_paths)

            prompt_file = sandbox / ".forgelab-aider-prompt.txt"
            config_file = sandbox / ".forgelab-aider.conf.yml"
            env_file = sandbox / ".forgelab-aider.env"
            prompt_file.write_text(self._prompt(request), encoding="utf-8")
            config_file.write_text("", encoding="utf-8")
            env_file.write_text("", encoding="utf-8")

            command = [
                *self.config.executable,
                "--model", self._model(request.model),
                "--edit-format", self.config.edit_format,
                "--no-git",
                "--no-auto-commits",
                "--no-dirty-commits",
                "--no-auto-lint",
                "--no-auto-test",
                "--no-suggest-shell-commands",
                "--analytics-disable",
                "--no-check-update",
                "--no-show-release-notes",
                "--yes-always",
                "--config", str(config_file),
                "--env-file", str(env_file),
                "--message-file", str(prompt_file),
            ]
            for path in request.read_only_paths:
                command.extend(["--read", path])
            command.extend(request.allowed_paths)

            environment = _sandbox_environment(sandbox)
            started = time.monotonic()
            try:
                completed = subprocess.run(
                    command,
                    cwd=sandbox,
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
                    error.stdout or "",
                    error.stderr or "",
                    124,
                    True,
                    int((time.monotonic() - started) * 1000),
                    tuple(command),
                )

            if _read_files(sandbox, request.read_only_paths) != before_read_only:
                raise EditorAdapterError("Aider modified read-only sandbox files")

            allowed_visible = set(visible_paths)
            created = sorted(
                str(path.relative_to(sandbox)).replace("\\", "/")
                for path in sandbox.rglob("*")
                if path.is_file()
                and not path.name.startswith(".")
                and str(path.relative_to(sandbox)).replace("\\", "/")
                not in allowed_visible
            )
            if created:
                raise EditorAdapterError(
                    "Aider created files outside authorized scope: "
                    + ", ".join(created)
                )

            after = _read_files(sandbox, request.allowed_paths)
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

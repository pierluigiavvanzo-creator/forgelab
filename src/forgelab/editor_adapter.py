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
    """Raised when a bounded editor adapter cannot produce a safe candidate."""


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


def _safe_relative_file(
    repository: Path,
    relative_path: str,
) -> Path:
    if not relative_path.strip():
        raise EditorAdapterError("editor path must not be empty")

    relative = Path(relative_path)

    if (
        relative.is_absolute()
        or ".." in relative.parts
        or any(part.lower() == ".git" for part in relative.parts)
    ):
        raise EditorAdapterError(
            f"editor path escapes authorized repository scope: {relative_path}"
        )

    root = repository.resolve()
    target = (root / relative).resolve()

    try:
        target.relative_to(root)
    except ValueError as error:
        raise EditorAdapterError(
            f"editor path escapes authorized repository scope: {relative_path}"
        ) from error

    if not target.is_file():
        raise EditorAdapterError(
            f"authorized editor file does not exist: {relative_path}"
        )

    return target


def _copy_file(
    source_root: Path,
    sandbox_root: Path,
    relative_path: str,
) -> None:
    source = _safe_relative_file(
        source_root,
        relative_path,
    )
    target = sandbox_root / relative_path
    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    shutil.copy2(
        source,
        target,
    )


def _read_utf8(
    root: Path,
    relative_path: str,
) -> str:
    return (root / relative_path).read_text(
        encoding="utf-8",
    )


def _aider_model_name(
    model: str,
) -> str:
    cleaned = model.strip()

    if not cleaned:
        raise EditorAdapterError(
            "editor model must not be empty"
        )

    if cleaned.startswith(
        ("ollama/", "ollama_chat/")
    ):
        return cleaned

    return f"ollama/{cleaned}"


@dataclass(frozen=True)
class AiderCliConfig:
    executable: tuple[str, ...] = ("aider",)
    edit_format: str = "whole"


class AiderCliAdapter:
    """Run Aider in a disposable file sandbox.

    The adapter never receives the governed ForgeLab workspace as its cwd.
    It receives copies of explicitly authorized files and returns candidate
    file contents for later deterministic validation and ToolGateway apply.
    """

    name = "aider-cli"

    def __init__(
        self,
        config: AiderCliConfig | None = None,
    ) -> None:
        self.config = config or AiderCliConfig()

    def _prompt(
        self,
        request: EditorRequest,
    ) -> str:
        allowed = "\n".join(
            f"- {path}"
            for path in request.allowed_paths
        )

        return f"""You are the bounded code editor inside ForgeLab.

Product Owner objective:
{request.objective}

Writable files:
{allowed}

Rules:
- edit only the writable files supplied to you;
- do not create new files;
- do not delete files;
- do not run shell commands;
- do not install or add dependencies;
- preserve unrelated behavior;
- implement the smallest complete change that satisfies the objective;
- preserve exact quantitative requirements;
- update tests inside the writable file set when needed;
- do not claim tests have run;
- finish after applying the code edits.
"""

    def run(
        self,
        request: EditorRequest,
    ) -> EditorResult:
        if not request.allowed_paths:
            raise EditorAdapterError(
                "Aider requires at least one writable path"
            )

        if len(set(request.allowed_paths)) != len(
            request.allowed_paths
        ):
            raise EditorAdapterError(
                "Aider writable paths must be unique"
            )

        if set(request.allowed_paths).intersection(
            request.read_only_paths
        ):
            raise EditorAdapterError(
                "Aider writable and read-only paths must not overlap"
            )

        source_root = request.repository.resolve()

        if not source_root.is_dir():
            raise EditorAdapterError(
                f"editor repository does not exist: {source_root}"
            )

        executable = self.config.executable

        if not executable:
            raise EditorAdapterError(
                "Aider executable must not be empty"
            )

        with tempfile.TemporaryDirectory(
            prefix="forgelab-editor-aider-",
        ) as folder:
            sandbox = Path(folder)

            for path in request.allowed_paths:
                _copy_file(
                    source_root,
                    sandbox,
                    path,
                )

            for path in request.read_only_paths:
                _copy_file(
                    source_root,
                    sandbox,
                    path,
                )

            before_writable = {
                path: _read_utf8(
                    sandbox,
                    path,
                )
                for path in request.allowed_paths
            }
            before_read_only = {
                path: _read_utf8(
                    sandbox,
                    path,
                )
                for path in request.read_only_paths
            }

            prompt_file = (
                sandbox
                / ".forgelab-aider-prompt.txt"
            )
            config_file = (
                sandbox
                / ".forgelab-aider.conf.yml"
            )
            env_file = (
                sandbox
                / ".forgelab-aider.env"
            )

            prompt_file.write_text(
                self._prompt(request),
                encoding="utf-8",
            )
            config_file.write_text(
                "",
                encoding="utf-8",
            )
            env_file.write_text(
                "",
                encoding="utf-8",
            )

            command = [
                *executable,
                "--model",
                _aider_model_name(
                    request.model
                ),
                "--edit-format",
                self.config.edit_format,
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
                "--config",
                str(config_file),
                "--env-file",
                str(env_file),
                "--message-file",
                str(prompt_file),
            ]

            for path in request.read_only_paths:
                command.extend(
                    ["--read", path]
                )

            command.extend(
                request.allowed_paths
            )

            environment = os.environ.copy()
            environment["HOME"] = str(sandbox)
            environment["USERPROFILE"] = str(
                sandbox
            )
            environment["AIDER_ANALYTICS"] = "0"

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
                timed_out = False
                stdout = completed.stdout
                stderr = completed.stderr
                exit_status = (
                    completed.returncode
                )
            except FileNotFoundError as error:
                raise EditorAdapterError(
                    "Aider CLI is not installed or "
                    f"not executable: {executable[0]}"
                ) from error
            except subprocess.TimeoutExpired as error:
                duration_ms = int(
                    (
                        time.monotonic()
                        - started
                    )
                    * 1000
                )
                return EditorResult(
                    engine=self.name,
                    files=before_writable,
                    changed_paths=(),
                    stdout=(
                        error.stdout or ""
                    ),
                    stderr=(
                        error.stderr or ""
                    ),
                    exit_status=124,
                    timed_out=True,
                    duration_ms=duration_ms,
                    command=tuple(command),
                )

            duration_ms = int(
                (
                    time.monotonic()
                    - started
                )
                * 1000
            )

            after_read_only = {
                path: _read_utf8(
                    sandbox,
                    path,
                )
                for path in request.read_only_paths
            }

            if (
                after_read_only
                != before_read_only
            ):
                changed = sorted(
                    path
                    for path in request.read_only_paths
                    if after_read_only[path]
                    != before_read_only[path]
                )
                raise EditorAdapterError(
                    "Aider modified read-only "
                    "sandbox files: "
                    + ", ".join(changed)
                )

            after_writable = {
                path: _read_utf8(
                    sandbox,
                    path,
                )
                for path in request.allowed_paths
            }

            changed_paths = tuple(
                path
                for path in request.allowed_paths
                if after_writable[path]
                != before_writable[path]
            )

            return EditorResult(
                engine=self.name,
                files=after_writable,
                changed_paths=changed_paths,
                stdout=stdout,
                stderr=stderr,
                exit_status=exit_status,
                timed_out=timed_out,
                duration_ms=duration_ms,
                command=tuple(command),
            )

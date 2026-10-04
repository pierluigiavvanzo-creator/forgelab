from __future__ import annotations

import subprocess
import sys
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


class ToolPolicyError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandEvidence:
    command: list[str]
    exit_status: int
    stdout: str
    stderr: str
    timed_out: bool = False


def safe_target(workspace: Path, relative_path: str) -> Path:
    if Path(relative_path).is_absolute():
        raise ToolPolicyError("target path must be relative")
    root = workspace.resolve()
    target = (root / relative_path).resolve()
    if root not in target.parents or ".git" in target.parts:
        raise ToolPolicyError("target path escapes the workspace or enters .git")
    if not target.is_file():
        raise ToolPolicyError(f"target file does not exist: {relative_path}")
    return target


def replace_text(workspace: Path, relative_path: str, old: str, new: str) -> Path:
    if not old or old == new:
        raise ToolPolicyError("replacement requires distinct non-empty old text")
    target = safe_target(workspace, relative_path)
    content = target.read_text(encoding="utf-8")
    occurrences = content.count(old)
    if occurrences != 1:
        raise ToolPolicyError(f"expected exactly one replacement match, found {occurrences}")
    target.write_text(content.replace(old, new, 1), encoding="utf-8")
    return target


def run_bounded(command: list[str], cwd: Path, timeout: int = 60) -> CommandEvidence:
    if not command:
        raise ToolPolicyError("command must not be empty")
    allowed = {"python", "python3", Path(sys.executable).name}
    if os.name == "nt":
        allowed.update({"py", "py.exe"})
    if Path(command[0]).name not in allowed:
        raise ToolPolicyError(f"executable is not allowed in M1: {command[0]}")
    try:
        with tempfile.TemporaryDirectory(prefix="forgelab-pycache-") as pycache:
            environment = os.environ.copy()
            environment["PYTHONPYCACHEPREFIX"] = pycache
            completed = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, env=environment,
                timeout=timeout, check=False,
            )
        return CommandEvidence(command, completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as error:
        return CommandEvidence(command, 124, error.stdout or "", error.stderr or "", True)

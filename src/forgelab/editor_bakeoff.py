from __future__ import annotations

import difflib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .editor_adapter import (
    AiderCliAdapter,
    EditorAdapter,
    EditorAdapterError,
    EditorRequest,
)
from .quality import review_patch, security_review_patch


@dataclass(frozen=True)
class EditorBakeoffRequest:
    repository: Path
    objective: str
    allowed_paths: tuple[str, ...]
    test_command: tuple[str, ...]
    model: str = "qwen2.5-coder:7b"
    timeout_seconds: int = 180
    read_only_paths: tuple[str, ...] = ()

    @classmethod
    def from_json(cls, path: Path) -> "EditorBakeoffRequest":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        allowed = payload.get("allowed_paths", payload.get("paths"))
        tests = payload.get("test_command")
        read_only = payload.get("read_only_paths", [])
        objective = payload.get("objective")

        if not isinstance(allowed, list) or not allowed or not all(
            isinstance(item, str) and item.strip() for item in allowed
        ):
            raise ValueError("allowed_paths must be a non-empty string array")
        if not isinstance(tests, list) or not tests or not all(
            isinstance(item, str) and item for item in tests
        ):
            raise ValueError("test_command must be a non-empty string array")
        if not isinstance(read_only, list) or not all(
            isinstance(item, str) and item.strip() for item in read_only
        ):
            raise ValueError("read_only_paths must be a string array")
        if not isinstance(objective, str) or not objective.strip():
            raise ValueError("objective must be non-empty")

        return cls(
            repository=Path(payload["repository"]),
            objective=objective.strip(),
            allowed_paths=tuple(item.strip() for item in allowed),
            test_command=tuple(tests),
            model=str(payload.get("model", "qwen2.5-coder:7b")),
            timeout_seconds=int(payload.get("timeout_seconds", 180)),
            read_only_paths=tuple(item.strip() for item in read_only),
        )


def _safe_target(root: Path, relative_path: str) -> Path:
    relative = Path(relative_path)
    if (
        not relative_path.strip()
        or relative.is_absolute()
        or ".." in relative.parts
        or ".git" in {part.lower() for part in relative.parts}
    ):
        raise ValueError(f"bakeoff path escapes repository: {relative_path}")
    resolved_root = root.resolve()
    target = (resolved_root / relative).resolve()
    try:
        target.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(
            f"bakeoff path escapes repository: {relative_path}"
        ) from error
    return target


def _compile(files: dict[str, str]) -> tuple[str, list[str]]:
    errors: list[str] = []
    for path, content in files.items():
        if not path.lower().endswith(".py"):
            continue
        try:
            compile(content.lstrip("\ufeff"), path, "exec", dont_inherit=True)
        except SyntaxError as error:
            errors.append(
                f"{path}: {error.msg} (line {error.lineno or 'unknown'})"
            )
    return ("PASS", []) if not errors else ("FAIL", errors)


def _patch(repository: Path, files: dict[str, str]) -> str:
    chunks: list[str] = []
    for path in sorted(files):
        source = _safe_target(repository, path)
        if not source.is_file():
            raise ValueError(f"candidate source missing: {path}")
        before = source.read_text(encoding="utf-8")
        after = files[path]
        if before != after:
            chunks.extend(difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            ))
    return "".join(chunks)


def _test_command(command: tuple[str, ...]) -> list[str]:
    parts = list(command)
    if not parts:
        raise ValueError("test command must not be empty")
    first = Path(parts[0]).name.lower()
    if first in {"py", "py.exe"}:
        parts = parts[1:]
        if parts and parts[0].startswith("-3."):
            parts = parts[1:]
        return [sys.executable, *parts]
    if first not in {
        "python",
        "python3",
        Path(sys.executable).name.lower(),
    }:
        raise ValueError(f"test executable is not allowed: {command[0]}")
    return parts


def _run_tests(
    request: EditorBakeoffRequest,
    candidate_files: dict[str, str],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(
        prefix="forgelab-bakeoff-test-"
    ) as folder:
        root = Path(folder) / "repo"
        shutil.copytree(
            request.repository.resolve(),
            root,
            ignore=shutil.ignore_patterns(
                ".git", ".forgelab", "__pycache__",
                ".pytest_cache", ".mypy_cache", ".ruff_cache",
                ".venv", "venv",
            ),
        )
        for path, content in candidate_files.items():
            target = _safe_target(root, path)
            if not target.is_file():
                raise ValueError(f"candidate attempted new file: {path}")
            target.write_text(content, encoding="utf-8")

        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        command = _test_command(request.test_command)
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=root,
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
        except subprocess.TimeoutExpired as error:
            exit_status = 124
            stdout, stderr = error.stdout or "", error.stderr or ""
            timed_out = True

    return {
        "command": command,
        "exit_status": exit_status,
        "status": "PASS" if exit_status == 0 else "FAIL",
        "timed_out": timed_out,
        "duration_ms": int((time.monotonic() - started) * 1000),
        "stdout": stdout,
        "stderr": stderr,
    }


def evaluate_editor_candidate(
    request: EditorBakeoffRequest,
    adapter: EditorAdapter,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        result = adapter.run(EditorRequest(
            repository=request.repository,
            objective=request.objective,
            allowed_paths=request.allowed_paths,
            model=request.model,
            timeout_seconds=request.timeout_seconds,
            read_only_paths=request.read_only_paths,
        ))
    except EditorAdapterError as error:
        return {
            "engine": getattr(adapter, "name", adapter.__class__.__name__),
            "status": "FAIL",
            "failure_stage": "editor",
            "error": str(error),
            "duration_ms": int((time.monotonic() - started) * 1000),
        }

    allowed = set(request.allowed_paths)
    returned = set(result.files)
    changed = set(result.changed_paths)
    unexpected = sorted((returned | changed) - allowed)
    if unexpected:
        return {
            "engine": result.engine,
            "status": "FAIL",
            "failure_stage": "scope",
            "unexpected_paths": unexpected,
        }
    if result.exit_status != 0 or result.timed_out:
        return {
            "engine": result.engine,
            "status": "FAIL",
            "failure_stage": "editor",
            "editor_exit_status": result.exit_status,
            "editor_timed_out": result.timed_out,
            "editor_duration_ms": result.duration_ms,
            "changed_paths": list(result.changed_paths),
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    compile_status, compile_errors = _compile(result.files)
    patch = _patch(request.repository, result.files)
    scope = review_patch(patch, allowed)
    security = security_review_patch(patch)
    tests = (
        _run_tests(request, result.files)
        if compile_status == "PASS"
        else None
    )
    passed = bool(
        result.changed_paths
        and compile_status == "PASS"
        and tests and tests["status"] == "PASS"
        and scope["status"] == "PASS"
        and security["status"] == "PASS"
    )
    if passed:
        failure_stage = None
    elif not result.changed_paths:
        failure_stage = "no_change"
    elif compile_status != "PASS":
        failure_stage = "compile"
    elif not tests or tests["status"] != "PASS":
        failure_stage = "tests"
    elif scope["status"] != "PASS":
        failure_stage = "scope_review"
    else:
        failure_stage = "security"

    return {
        "engine": result.engine,
        "status": "PASS" if passed else "FAIL",
        "failure_stage": failure_stage,
        "changed_paths": list(result.changed_paths),
        "editor_exit_status": result.exit_status,
        "editor_timed_out": result.timed_out,
        "editor_duration_ms": result.duration_ms,
        "compile_status": compile_status,
        "compile_errors": compile_errors,
        "scope_review": scope,
        "security_review": security,
        "tests": tests,
        "patch": patch,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "semantic_review": "NOT_RUN_IN_EDITOR_BOUNDARY_BAKEOFF",
        "product_owner_touches": 0,
    }


def run_editor_bakeoff(
    request: EditorBakeoffRequest,
    output_path: Path,
    adapters: tuple[EditorAdapter, ...] | None = None,
) -> dict[str, Any]:
    selected = adapters if adapters is not None else (AiderCliAdapter(),)
    if not selected:
        raise ValueError("at least one editor adapter is required")

    report = {
        "schema_version": "1.0",
        "experiment": "EDITOR_ENGINE_BAKEOFF_01",
        "objective": request.objective,
        "repository": str(request.repository.resolve()),
        "allowed_paths": list(request.allowed_paths),
        "model": request.model,
        "test_command": list(request.test_command),
        "semantic_review":
            "DEFERRED_BY_ADR_002_FIRST_BOUNDARY_EXPERIMENT",
        "candidates": [
            evaluate_editor_candidate(request, adapter)
            for adapter in selected
        ],
        "decision_gate": "HUMAN_REVIEW_AFTER_COMPARATIVE_EVIDENCE",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report

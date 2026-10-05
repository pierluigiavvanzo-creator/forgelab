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
from .quality import (
    review_patch,
    security_review_patch,
)


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
    def from_json(
        cls,
        path: Path,
    ) -> "EditorBakeoffRequest":
        payload = json.loads(
            path.read_text(
                encoding="utf-8-sig",
            )
        )

        raw_paths = payload.get(
            "allowed_paths",
            payload.get("paths"),
        )

        if (
            not isinstance(raw_paths, list)
            or not raw_paths
            or not all(
                isinstance(item, str)
                and item.strip()
                for item in raw_paths
            )
        ):
            raise ValueError(
                "allowed_paths must contain "
                "one or more non-empty strings"
            )

        raw_test = payload.get(
            "test_command"
        )

        if (
            not isinstance(raw_test, list)
            or not raw_test
            or not all(
                isinstance(item, str)
                and item
                for item in raw_test
            )
        ):
            raise ValueError(
                "test_command must be a "
                "non-empty string array"
            )

        read_only = payload.get(
            "read_only_paths",
            [],
        )

        if (
            not isinstance(read_only, list)
            or not all(
                isinstance(item, str)
                and item.strip()
                for item in read_only
            )
        ):
            raise ValueError(
                "read_only_paths must be "
                "a string array"
            )

        objective = payload.get(
            "objective"
        )

        if (
            not isinstance(objective, str)
            or not objective.strip()
        ):
            raise ValueError(
                "objective must be non-empty"
            )

        return cls(
            repository=Path(
                payload["repository"]
            ),
            objective=objective.strip(),
            allowed_paths=tuple(
                item.strip()
                for item in raw_paths
            ),
            test_command=tuple(
                raw_test
            ),
            model=str(
                payload.get(
                    "model",
                    "qwen2.5-coder:7b",
                )
            ),
            timeout_seconds=int(
                payload.get(
                    "timeout_seconds",
                    180,
                )
            ),
            read_only_paths=tuple(
                item.strip()
                for item in read_only
            ),
        )


def _safe_target(
    root: Path,
    relative_path: str,
) -> Path:
    relative = Path(relative_path)

    if (
        not relative_path.strip()
        or relative.is_absolute()
        or ".." in relative.parts
        or any(
            part.lower() == ".git"
            for part in relative.parts
        )
    ):
        raise ValueError(
            "bakeoff path escapes repository: "
            f"{relative_path}"
        )

    resolved_root = root.resolve()
    target = (
        resolved_root
        / relative
    ).resolve()

    try:
        target.relative_to(
            resolved_root
        )
    except ValueError as error:
        raise ValueError(
            "bakeoff path escapes repository: "
            f"{relative_path}"
        ) from error

    return target


def _python_compile_status(
    candidate_files: dict[str, str],
) -> tuple[str, list[str]]:
    errors: list[str] = []

    for path, content in (
        candidate_files.items()
    ):
        if not path.lower().endswith(
            ".py"
        ):
            continue

        try:
            compile(
                content.lstrip("\ufeff"),
                path,
                "exec",
                dont_inherit=True,
            )
        except SyntaxError as error:
            location = (
                f"line {error.lineno}"
                if error.lineno
                else "unknown line"
            )
            errors.append(
                f"{path}: {error.msg} "
                f"({location})"
            )

    return (
        ("PASS", [])
        if not errors
        else ("FAIL", errors)
    )


def _candidate_patch(
    repository: Path,
    candidate_files: dict[str, str],
) -> str:
    chunks: list[str] = []

    for path in sorted(
        candidate_files
    ):
        source = _safe_target(
            repository,
            path,
        )

        if not source.is_file():
            raise ValueError(
                f"candidate source missing: {path}"
            )

        before = source.read_text(
            encoding="utf-8",
        )
        after = candidate_files[path]

        if before == after:
            continue

        chunks.extend(
            difflib.unified_diff(
                before.splitlines(
                    keepends=True
                ),
                after.splitlines(
                    keepends=True
                ),
                fromfile=f"a/{path}",
                tofile=f"b/{path}",
            )
        )

    return "".join(chunks)


def _copy_repository_for_test(
    source: Path,
    destination: Path,
) -> None:
    def ignore(
        _directory: str,
        names: list[str],
    ) -> set[str]:
        ignored = {
            ".git",
            ".forgelab",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".venv",
            "venv",
        }
        return {
            name
            for name in names
            if name in ignored
        }

    shutil.copytree(
        source,
        destination,
        ignore=ignore,
    )


def _normalized_test_command(
    command: tuple[str, ...],
) -> list[str]:
    normalized = list(command)

    if not normalized:
        raise ValueError(
            "test command must not be empty"
        )

    first = Path(
        normalized[0]
    ).name.lower()

    if first in {
        "py",
        "py.exe",
    }:
        normalized = normalized[1:]

        if (
            normalized
            and normalized[0].startswith(
                "-3."
            )
        ):
            normalized = normalized[1:]

        return [
            sys.executable,
            *normalized,
        ]

    allowed = {
        "python",
        "python3",
        Path(sys.executable).name.lower(),
    }

    if first not in allowed:
        raise ValueError(
            "bakeoff test executable is "
            f"not allowed: {command[0]}"
        )

    return normalized


def _run_candidate_tests(
    request: EditorBakeoffRequest,
    candidate_files: dict[str, str],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(
        prefix="forgelab-bakeoff-test-",
    ) as folder:
        root = Path(folder) / "repo"
        _copy_repository_for_test(
            request.repository.resolve(),
            root,
        )

        for path, content in (
            candidate_files.items()
        ):
            target = _safe_target(
                root,
                path,
            )

            if not target.is_file():
                raise ValueError(
                    "adapter attempted to create "
                    f"unauthorized file: {path}"
                )

            target.write_text(
                content,
                encoding="utf-8",
            )

        command = (
            _normalized_test_command(
                request.test_command
            )
        )

        environment = os.environ.copy()
        environment[
            "PYTHONDONTWRITEBYTECODE"
        ] = "1"

        with tempfile.TemporaryDirectory(
            prefix="forgelab-bakeoff-pycache-",
        ) as pycache:
            environment[
                "PYTHONPYCACHEPREFIX"
            ] = pycache

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
                timed_out = False
                exit_status = (
                    completed.returncode
                )
                stdout = completed.stdout
                stderr = completed.stderr
            except subprocess.TimeoutExpired as error:
                timed_out = True
                exit_status = 124
                stdout = error.stdout or ""
                stderr = error.stderr or ""

            duration_ms = int(
                (
                    time.monotonic()
                    - started
                )
                * 1000
            )

    return {
        "command": command,
        "exit_status":
            exit_status,
        "status":
            (
                "PASS"
                if exit_status == 0
                else "FAIL"
            ),
        "timed_out":
            timed_out,
        "duration_ms":
            duration_ms,
        "stdout":
            stdout,
        "stderr":
            stderr,
    }


def evaluate_editor_candidate(
    request: EditorBakeoffRequest,
    adapter: EditorAdapter,
) -> dict[str, Any]:
    editor_request = EditorRequest(
        repository=request.repository,
        objective=request.objective,
        allowed_paths=request.allowed_paths,
        read_only_paths=(
            request.read_only_paths
        ),
        model=request.model,
        timeout_seconds=(
            request.timeout_seconds
        ),
    )

    started = time.monotonic()

    try:
        editor_result = adapter.run(
            editor_request
        )
    except EditorAdapterError as error:
        return {
            "engine":
                getattr(
                    adapter,
                    "name",
                    adapter.__class__.__name__,
                ),
            "status": "FAIL",
            "failure_stage": "editor",
            "error": str(error),
            "duration_ms": int(
                (
                    time.monotonic()
                    - started
                )
                * 1000
            ),
        }

    allowed = set(
        request.allowed_paths
    )
    changed = set(
        editor_result.changed_paths
    )
    returned = set(
        editor_result.files
    )

    if not returned.issubset(
        allowed
    ):
        return {
            "engine": editor_result.engine,
            "status": "FAIL",
            "failure_stage": "scope",
            "error":
                "adapter returned files outside "
                "authorized scope",
            "unexpected_paths":
                sorted(
                    returned - allowed
                ),
        }

    if not changed.issubset(
        allowed
    ):
        return {
            "engine": editor_result.engine,
            "status": "FAIL",
            "failure_stage": "scope",
            "error":
                "adapter changed files outside "
                "authorized scope",
            "unexpected_paths":
                sorted(
                    changed - allowed
                ),
        }

    if (
        editor_result.exit_status != 0
        or editor_result.timed_out
    ):
        return {
            "engine": editor_result.engine,
            "status": "FAIL",
            "failure_stage": "editor",
            "editor_exit_status":
                editor_result.exit_status,
            "editor_timed_out":
                editor_result.timed_out,
            "editor_duration_ms":
                editor_result.duration_ms,
            "changed_paths":
                list(
                    editor_result.changed_paths
                ),
            "stdout":
                editor_result.stdout,
            "stderr":
                editor_result.stderr,
        }

    compile_status, compile_errors = (
        _python_compile_status(
            editor_result.files
        )
    )

    patch = _candidate_patch(
        request.repository,
        editor_result.files,
    )

    scope_review = review_patch(
        patch,
        allowed,
    )
    security_review = (
        security_review_patch(
            patch
        )
    )

    tests: dict[str, Any] | None = None

    if compile_status == "PASS":
        tests = _run_candidate_tests(
            request,
            editor_result.files,
        )

    status = (
        "PASS"
        if (
            editor_result.changed_paths
            and compile_status == "PASS"
            and tests is not None
            and tests["status"] == "PASS"
            and scope_review["status"]
            == "PASS"
            and security_review["status"]
            == "PASS"
        )
        else "FAIL"
    )

    return {
        "engine": editor_result.engine,
        "status": status,
        "failure_stage": (
            None
            if status == "PASS"
            else (
                "no_change"
                if not editor_result.changed_paths
                else (
                    "compile"
                    if compile_status
                    != "PASS"
                    else (
                        "tests"
                        if (
                            tests is None
                            or tests[
                                "status"
                            ]
                            != "PASS"
                        )
                        else (
                            "scope_review"
                            if scope_review[
                                "status"
                            ]
                            != "PASS"
                            else "security"
                        )
                    )
                )
            )
        ),
        "changed_paths":
            list(
                editor_result.changed_paths
            ),
        "editor_exit_status":
            editor_result.exit_status,
        "editor_timed_out":
            editor_result.timed_out,
        "editor_duration_ms":
            editor_result.duration_ms,
        "compile_status":
            compile_status,
        "compile_errors":
            compile_errors,
        "scope_review":
            scope_review,
        "security_review":
            security_review,
        "tests":
            tests,
        "patch":
            patch,
        "stdout":
            editor_result.stdout,
        "stderr":
            editor_result.stderr,
        "semantic_review":
            "NOT_RUN_IN_EDITOR_BOUNDARY_BAKEOFF",
        "product_owner_touches":
            0,
    }


def run_editor_bakeoff(
    request: EditorBakeoffRequest,
    output_path: Path,
    adapters: tuple[
        EditorAdapter,
        ...,
    ] | None = None,
) -> dict[str, Any]:
    selected = (
        adapters
        if adapters is not None
        else (AiderCliAdapter(),)
    )

    if not selected:
        raise ValueError(
            "at least one editor adapter "
            "is required"
        )

    results = [
        evaluate_editor_candidate(
            request,
            adapter,
        )
        for adapter in selected
    ]

    report = {
        "schema_version": "1.0",
        "experiment":
            "EDITOR_ENGINE_BAKEOFF_01",
        "objective":
            request.objective,
        "repository":
            str(
                request.repository.resolve()
            ),
        "allowed_paths":
            list(
                request.allowed_paths
            ),
        "model":
            request.model,
        "test_command":
            list(
                request.test_command
            ),
        "semantic_review":
            "DEFERRED_BY_ADR_002_FIRST_BOUNDARY_EXPERIMENT",
        "candidates":
            results,
        "decision_gate":
            "HUMAN_REVIEW_AFTER_COMPARATIVE_EVIDENCE",
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return report

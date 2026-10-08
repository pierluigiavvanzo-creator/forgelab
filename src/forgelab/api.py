from __future__ import annotations

import hmac
import os
import json
import re
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from threading import Lock, Thread
from uuid import uuid4
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .orchestrator import MultiAgentRequest, run_multi_agent
from .promote import PromotionError, decide


RUN_ID = re.compile(r"^run-[A-Za-z0-9_-]+$")
ARTIFACTS = (
    "ExecutionPlan.json",
    "AgentResult.json",
    "TestEvidence.json",
    "ReviewReport.json",
    "SecurityReport.json",
    "UsageReport.json",
    "RunSummary.json",
    "GateDecision.json",
    "MemorySnapshot.json",
    "ContextBundle.json",
    "ToolAudit.json",
    "AIPlan.json",
    "AIDiagnostics.json",
    "AIReview.json",
    "AIDeveloperPatch.json",
    "PromotionResult.json",
    "HumanRepairRequest.json",
    "PrewriteRecoveryFailure.json",
    "ProviderFailure.json",
    "EditorFailure.json",
    "RunStatus.json",
)
TEXT_ARTIFACTS = (
    "Changes.patch",
)
DECISIONS = {"approve": "APPROVE", "repair": "REPAIR", "reject": "REJECT"}


class ApiError(ValueError):
    pass


class ApiConflict(ApiError):
    pass


def _write_json_atomic(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    temporary = path.with_suffix(
        path.suffix + ".tmp"
    )
    temporary.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ApiError(f"artifact is not a JSON object: {path.name}")
    return payload


def _required_string(
    payload: dict[str, Any],
    key: str,
    *,
    minimum: int = 1,
    maximum: int = 100_000,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise ApiError(f"{key} must be a string")
    if len(value.strip()) < minimum:
        raise ApiError(f"{key} is too short")
    if len(value) > maximum:
        raise ApiError(f"{key} is too long")
    return value


def _normalize_test_command(
    command: list[str],
) -> list[str]:

    normalized = list(command)

    if not normalized:
        raise ApiError(
            "test command must not be empty"
        )

    executable = Path(
        normalized[0]
    ).name.lower()

    # Windows Python launcher is convenient for
    # Product Owner input but is intentionally not
    # executed directly by the M1 bounded runner.
    #
    # Convert only the explicitly pinned Python 3.11
    # form into the interpreter already running
    # ForgeLab. No shell expansion is involved.
    if executable in {
        "py",
        "py.exe",
    }:

        if (
            len(normalized) < 2
            or normalized[1] != "-3.11"
        ):
            raise ApiError(
                "py launcher is accepted only "
                "with explicit -3.11"
            )

        normalized = [
            sys.executable,
            *normalized[2:],
        ]

    return normalized


class ForgeLabApi:
    def __init__(self, runs_root: Path, token: str, allowed_origin: str) -> None:
        if len(token) < 24:
            raise ApiError("API token must contain at least 24 characters")
        self.runs_root = runs_root.resolve()
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.token = token
        self.allowed_origin = allowed_origin.rstrip("/")
        self._run_lock = Lock()
        self._active_run_id: str | None = None
        self._recover_interrupted_runs()

    def _recover_interrupted_runs(self) -> None:
        for directory in self.runs_root.iterdir():
            if (
                not directory.is_dir()
                or not RUN_ID.fullmatch(
                    directory.name
                )
            ):
                continue
            status_path = (
                directory /
                "RunStatus.json"
            )
            if not status_path.is_file():
                continue
            try:
                status = _read_json(
                    status_path
                )
            except (
                ApiError,
                json.JSONDecodeError,
                OSError,
            ):
                continue
            if (
                str(
                    status.get(
                        "status",
                        "",
                    )
                ).upper()
                in {"QUEUED", "RUNNING"}
            ):
                summary_path = (
                    directory /
                    "RunSummary.json"
                )
                if summary_path.is_file():
                    try:
                        summary = _read_json(
                            summary_path
                        )
                    except (
                        ApiError,
                        json.JSONDecodeError,
                        OSError,
                    ):
                        summary = {}
                    if summary:
                        status.update({
                            "status":
                                summary.get(
                                    "status",
                                    "UNKNOWN",
                                ),
                            "decision":
                                summary.get(
                                    "decision"
                                ),
                            "terminal": True,
                            "completed_at":
                                datetime.now(
                                    timezone.utc
                                ).isoformat(),
                        })
                        _write_json_atomic(
                            status_path,
                            status,
                        )
                        continue

                status.update({
                    "status": "INTERRUPTED",
                    "terminal": True,
                    "completed_at":
                        datetime.now(
                            timezone.utc
                        ).isoformat(),
                    "error": (
                        "ForgeLab API restarted "
                        "before run completion"
                    ),
                })
                _write_json_atomic(
                    status_path,
                    status,
                )

    def _write_run_status(
        self,
        run_id: str,
        payload: dict[str, Any],
    ) -> None:
        if not RUN_ID.fullmatch(run_id):
            raise ApiError(
                "invalid run id"
            )
        directory = (
            self.runs_root /
            run_id
        ).resolve()
        if directory.parent != self.runs_root:
            raise ApiError(
                "invalid run id"
            )
        _write_json_atomic(
            directory /
            "RunStatus.json",
            payload,
        )

    def run_status(
        self,
        run_id: str,
    ) -> dict[str, Any]:
        directory = self.run_dir(
            run_id
        )
        status_path = (
            directory /
            "RunStatus.json"
        )
        status = _read_json(status_path) if status_path.is_file() else {}
        # A summary can appear before the worker has finished writing the
        # remaining gate artifacts. Its presence alone must not end polling.
        if status and (
            status.get("terminal") is False
            or status.get("status") in {"FAILED", "INTERRUPTED"}
        ):
            return status

        summary_path = (
            directory /
            "RunSummary.json"
        )
        if summary_path.is_file():
            summary = _read_json(
                summary_path
            )
            return {
                **status,
                "run_id": run_id,
                "status": summary.get(
                    "status",
                    "UNKNOWN",
                ),
                "terminal": True,
                "created_at":
                    summary.get(
                        "created_at"
                    ),
                "decision":
                    summary.get(
                        "decision"
                    ),
            }

        if status:
            return status

        raise ApiError(
            "run has no status"
        )

    def authorize(self, header: str | None) -> bool:
        if not header or not header.startswith("Bearer "):
            return False
        return hmac.compare_digest(header[7:], self.token)

    def run_dir(self, run_id: str) -> Path:
        if not RUN_ID.fullmatch(run_id):
            raise ApiError("invalid run id")
        candidate = (self.runs_root / run_id).resolve()
        if candidate.parent != self.runs_root or not candidate.is_dir():
            raise ApiError("run not found")
        return candidate

    def list_runs(self) -> list[dict[str, Any]]:
        runs: list[dict[str, Any]] = []
        for directory in self.runs_root.iterdir():
            if (
                not directory.is_dir()
                or not RUN_ID.fullmatch(
                    directory.name
                )
            ):
                continue
            summary_path = (
                directory /
                "RunSummary.json"
            )
            status_path = (
                directory /
                "RunStatus.json"
            )
            if summary_path.is_file() or status_path.is_file():
                status = self.run_status(directory.name)
                runs.append({
                    "run_id":
                        directory.name,
                    "status":
                        status.get(
                            "status",
                            "UNKNOWN",
                        ),
                    "created_at":
                        status.get(
                            "created_at"
                        ),
                    "decision":
                        status.get(
                            "decision"
                        ),
                    "terminal":
                        bool(
                            status.get(
                                "terminal",
                                False,
                            )
                        ),
                })

        return sorted(
            runs,
            key=lambda item: str(
                item.get(
                    "created_at"
                ) or ""
            ),
            reverse=True,
        )


    def artifacts(self, run_id: str) -> dict[str, Any]:
        directory = self.run_dir(run_id)
        artifacts: dict[str, Any] = {
            name: _read_json(directory / name)
            for name in ARTIFACTS
            if (directory / name).is_file()
        }
        if "RunStatus.json" in artifacts:
            artifacts["RunStatus.json"] = self.run_status(run_id)

        for name in TEXT_ARTIFACTS:
            path = directory / name
            if path.is_file():
                artifacts[name] = {
                    "text": path.read_text(
                        encoding="utf-8",
                    ),
                }

        return artifacts

    def create_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        repository_text = _required_string(
            payload,
            "repository",
            maximum=4096,
        )

        repository = Path(repository_text).expanduser()

        if not repository.is_absolute():
            raise ApiError("repository must be an absolute path")

        repository = repository.resolve()

        if not repository.is_dir():
            raise ApiError("repository does not exist")

        if not (repository / ".git").exists():
            raise ApiError("repository must be a Git repository")

        objective = _required_string(
            payload,
            "objective",
            minimum=8,
            maximum=4000,
        ).strip()

        change = payload.get("change")
        if not isinstance(change, dict):
            raise ApiError("change must be a JSON object")

        operation = change.get(
            "operation",
            "replace_text",
        )

        if operation not in {
            "replace_text",
            "ai_generate",
        }:
            raise ApiError(
                "change.operation must be "
                "replace_text or ai_generate"
            )

        if operation == "ai_generate" and "paths" in change:
            raw_paths = change.get("paths")

            if (
                not isinstance(raw_paths, list)
                or not 1 <= len(raw_paths) <= 3
                or not all(
                    isinstance(item, str)
                    and item.strip()
                    and len(item) <= 4096
                    for item in raw_paths
                )
            ):
                raise ApiError(
                    "change.paths must contain "
                    "1 to 3 non-empty path strings"
                )

            target_paths = [
                item.strip()
                for item in raw_paths
            ]

            if len(set(target_paths)) != len(target_paths):
                raise ApiError(
                    "change.paths must be unique"
                )

            if "path" in change:
                raise ApiError(
                    "ai_generate must use either path "
                    "or paths, not both"
                )

            target_path = target_paths[0]

        else:
            target_path = _required_string(
                change,
                "path",
                maximum=4096,
            ).strip()

            target_paths = [target_path]

        for candidate in target_paths:
            relative_target = Path(candidate)

            if (
                relative_target.is_absolute()
                or ".." in relative_target.parts
                or ".git" in relative_target.parts
            ):
                raise ApiError(
                    "target path must remain inside repository"
                )

            target_file = (
                repository / relative_target
            ).resolve()

            try:
                target_file.relative_to(repository)
            except ValueError as error:
                raise ApiError(
                    "target path must remain inside repository"
                ) from error

            if not target_file.is_file():
                raise ApiError(
                    f"target file does not exist: {candidate}"
                )

        if operation == "replace_text":

            if "paths" in change:
                raise ApiError(
                    "replace_text accepts exactly one path"
                )

            old_text = _required_string(
                change,
                "old",
                maximum=100_000,
            )

            new_text = change.get("new")

            if not isinstance(new_text, str):
                raise ApiError(
                    "new must be a string"
                )

            if len(new_text) > 100_000:
                raise ApiError(
                    "new is too long"
                )

            initial_new = change.get(
                "initial_new"
            )

            if (
                initial_new is not None
                and not isinstance(
                    initial_new,
                    str,
                )
            ):
                raise ApiError(
                    "initial_new must be a "
                    "string when provided"
                )

            if (
                isinstance(
                    initial_new,
                    str,
                )
                and len(initial_new)
                > 100_000
            ):
                raise ApiError(
                    "initial_new is too long"
                )

        else:

            forbidden = {
                key
                for key in (
                    "old",
                    "new",
                    "initial_new",
                )
                if key in change
            }

            if forbidden:
                raise ApiError(
                    "ai_generate accepts path/paths only; "
                    "do not supply old/new content"
                )

            old_text = ""
            new_text = ""
            initial_new = None

        command = payload.get("test_command")

        if (
            not isinstance(command, list)
            or not command
            or len(command) > 32
            or not all(
                isinstance(item, str)
                and item.strip()
                and len(item) <= 2048
                for item in command
            )
        ):
            raise ApiError(
                "test_command must contain 1 to 32 non-empty string arguments"
            )

        try:
            timeout_seconds = int(
                payload.get("timeout_seconds", 60)
            )
        except (TypeError, ValueError) as error:
            raise ApiError("timeout_seconds must be an integer") from error

        if timeout_seconds < 1 or timeout_seconds > 600:
            raise ApiError(
                "timeout_seconds must be between 1 and 600"
            )

        try:
            editor_timeout_seconds = int(
                payload.get(
                    "editor_timeout_seconds",
                    300,
                )
            )
        except (TypeError, ValueError) as error:
            raise ApiError(
                "editor_timeout_seconds must be an integer"
            ) from error

        if (
            editor_timeout_seconds < 60
            or editor_timeout_seconds > 600
        ):
            raise ApiError(
                "editor_timeout_seconds must be between 60 and 600"
            )

        try:
            max_repair_attempts = int(
                payload.get("max_repair_attempts", 1)
            )
        except (TypeError, ValueError) as error:
            raise ApiError(
                "max_repair_attempts must be an integer"
            ) from error

        if max_repair_attempts < 0 or max_repair_attempts > 3:
            raise ApiError(
                "max_repair_attempts must be between 0 and 3"
            )

        risk = str(payload.get("risk", "normal")).lower()

        if risk not in {"normal", "high"}:
            raise ApiError("risk must be normal or high")

        ai_mode = payload.get("ai_mode", False)

        if not isinstance(ai_mode, bool):
            raise ApiError("ai_mode must be boolean")

        editor_engine = str(
            payload.get(
                "editor_engine",
                "custom",
            )
        ).strip().lower()

        if editor_engine not in {
            "custom",
            "aider",
        }:
            raise ApiError(
                "editor_engine must be custom or aider"
            )

        if (
            editor_engine == "aider"
            and operation != "ai_generate"
        ):
            raise ApiError(
                "aider editor_engine requires ai_generate"
            )

        if operation == "ai_generate":
            # The operation itself is explicit
            # local-AI opt-in.
            ai_mode = True

        request = MultiAgentRequest(
            repository=repository,
            objective=objective,
            target_path=target_path,
            old_text=old_text,
            new_text=new_text,
            initial_new_text=initial_new,
            test_command=_normalize_test_command(
                list(command)
            ),
            timeout_seconds=timeout_seconds,
            editor_timeout_seconds=editor_timeout_seconds,
            risk=risk,
            max_repair_attempts=max_repair_attempts,
            ai_mode=ai_mode,
            operation=operation,
            allowed_paths=tuple(target_paths),
            editor_engine=editor_engine,
        )

        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        with self._run_lock:
            if self._active_run_id is not None:
                raise ApiConflict(
                    "another ForgeLab run is already active: "
                    + self._active_run_id
                )

            run_id = (
                f"run-{uuid4().hex[:12]}"
            )

            queued_status = {
                "run_id": run_id,
                "status": "QUEUED",
                "terminal": False,
                "created_at": created_at,
                "repository":
                    str(repository),
                "objective":
                    objective,
                "operation":
                    operation,
                "editor_engine":
                    editor_engine,
                "allowed_paths":
                    target_paths,
            }
            try:
                self._write_run_status(run_id, queued_status)
            except OSError as error:
                raise ApiError(f"run could not be queued: {error}") from error

            worker = Thread(
                target=self._execute_run,
                args=(
                    run_id,
                    request,
                ),
                daemon=True,
                name=(
                    "forgelab-run-"
                    + run_id
                ),
            )

            try:
                self._active_run_id = run_id
                worker.start()
            except RuntimeError as error:
                self._active_run_id = None
                failed = dict(
                    queued_status
                )
                failed.update({
                    "status": "FAILED",
                    "terminal": True,
                    "completed_at":
                        datetime.now(
                            timezone.utc
                        ).isoformat(),
                    "error":
                        "run worker could not start: "
                        + str(error),
                })
                self._write_run_status(
                    run_id,
                    failed,
                )
                raise ApiError(
                    failed["error"]
                ) from error

        return {
            "run_id": run_id,
            "status": "QUEUED",
            "terminal": False,
            "accepted": True,
            "repository": str(repository),
            "operation": operation,
            "editor_engine": editor_engine,
            "allowed_paths": target_paths,
            "status_url": (
                f"/v1/runs/{run_id}/status"
            ),
            "artifacts_url": (
                f"/v1/runs/{run_id}/artifacts"
            ),
        }

    def _execute_run(
        self,
        run_id: str,
        request: MultiAgentRequest,
    ) -> None:
        started_at = datetime.now(
            timezone.utc
        ).isoformat()
        try:
            current = self.run_status(
                run_id
            )
            current.update({
                "status": "RUNNING",
                "terminal": False,
                "started_at": started_at,
            })
            self._write_run_status(
                run_id,
                current,
            )

            run_dir = run_multi_agent(
                request,
                self.runs_root,
                run_id=run_id,
            )
            summary = _read_json(
                run_dir /
                "RunSummary.json"
            )
            current.update({
                "status":
                    summary.get(
                        "status",
                        "UNKNOWN",
                    ),
                "decision":
                    summary.get(
                        "decision"
                    ),
                "terminal": True,
                "completed_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
            })
            self._write_run_status(
                run_id,
                current,
            )
        except Exception as error:
            try:
                current = self.run_status(
                    run_id
                )
            except (ApiError, json.JSONDecodeError, OSError):
                current = {
                    "run_id": run_id,
                    "created_at":
                        started_at,
                }
            current.update({
                "status": "FAILED",
                "terminal": True,
                "completed_at":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),
                "error": (
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
            })
            self._write_run_status(
                run_id,
                current,
            )
        finally:
            with self._run_lock:
                if (
                    self._active_run_id
                    == run_id
                ):
                    self._active_run_id = None

    @contextmanager
    def _exclusive_operation(self, run_id: str):
        # Decisions and synchronous human repairs share the same local slot
        # as asynchronous submissions. Never hold the mutex while executing.
        with self._run_lock:
            if self._active_run_id is not None:
                raise ApiConflict(
                    "another ForgeLab run is already active: " + self._active_run_id
                )
            self._active_run_id = run_id
        try:
            yield
        finally:
            with self._run_lock:
                self._active_run_id = None

    def request_repair(
        self,
        run_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        with self._exclusive_operation(run_id):
            return self._request_repair(run_id, payload)

    def _request_repair(
        self,
        run_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        feedback = _required_string(
            payload,
            "feedback",
            minimum=8,
            maximum=4000,
        ).strip()

        actor = " ".join(
            str(
                payload.get(
                    "actor",
                    "",
                )
            ).split()
        )

        if not actor or len(actor) > 120:
            raise ApiError(
                "actor must be a non-empty "
                "string up to 120 characters"
            )

        directory = self.run_dir(run_id)
        plan = _read_json(
            directory /
            "ExecutionPlan.json"
        )
        gate = _read_json(
            directory /
            "GateDecision.json"
        )

        gate_decision = str(
            gate.get(
                "decision",
                "",
            )
        ).upper()

        if gate_decision not in {
            "PENDING",
            "REPAIR",
        }:
            raise ApiError(
                "human repair is allowed only "
                "for a pending or repair-requested run"
            )

        operation = str(
            plan.get(
                "change_operation",
                "",
            )
        )

        if operation != "ai_generate":
            raise ApiError(
                "human repair currently requires "
                "an ai_generate run"
            )

        repository_text = plan.get(
            "repository"
        )

        if (
            not isinstance(
                repository_text,
                str,
            )
            or not repository_text
        ):
            raise ApiError(
                "run execution plan has no repository"
            )

        repository = Path(
            repository_text
        ).resolve()

        if (
            not repository.is_dir()
            or not (
                repository /
                ".git"
            ).exists()
        ):
            raise ApiError(
                "repair repository is unavailable"
            )

        raw_paths = plan.get(
            "allowed_paths"
        )

        if (
            not isinstance(
                raw_paths,
                list,
            )
            or not 1 <= len(raw_paths) <= 3
            or not all(
                isinstance(
                    item,
                    str,
                )
                and item.strip()
                for item in raw_paths
            )
        ):
            raise ApiError(
                "run execution plan has invalid "
                "repair path scope"
            )

        allowed_paths = tuple(
            item.strip()
            for item in raw_paths
        )

        if (
            len(
                set(
                    allowed_paths
                )
            )
            != len(
                allowed_paths
            )
        ):
            raise ApiError(
                "repair path scope must be unique"
            )

        test_command = plan.get(
            "test_command"
        )

        if (
            not isinstance(
                test_command,
                list,
            )
            or not test_command
            or not all(
                isinstance(
                    item,
                    str,
                )
                and item
                for item in test_command
            )
        ):
            raise ApiError(
                "run execution plan has invalid "
                "test command"
            )

        original_objective = str(
            plan.get(
                "objective",
                "",
            )
        ).strip()

        if not original_objective:
            raise ApiError(
                "run execution plan has no objective"
            )

        selected_roles = {
            str(item)
            for item in (
                plan.get(
                    "selected_roles",
                    []
                )
                if isinstance(
                    plan.get(
                        "selected_roles",
                        []
                    ),
                    list,
                )
                else []
            )
        }

        risk = (
            "high"
            if "SECURITY" in selected_roles
            else "normal"
        )

        repaired_objective = (
            original_objective
            + "\n\n"
            + "Product Owner repair feedback:\n"
            + feedback
            + "\n\n"
            + "Repair instruction: address the feedback "
            + "while preserving the original objective, "
            + "authorized path scope, dependencies, "
            + "configuration, tests, and governance."
        )

        editor_engine = str(
            plan.get(
                "editor_engine",
                "custom",
            )
        ).strip().lower()

        request = MultiAgentRequest(
            repository=repository,
            objective=repaired_objective,
            target_path=allowed_paths[0],
            old_text="",
            new_text="",
            test_command=list(
                test_command
            ),
            timeout_seconds=int(
                plan.get(
                    "timeout_seconds",
                    60,
                )
            ),
            editor_timeout_seconds=int(
                plan.get(
                    "editor_timeout_seconds",
                    300,
                )
            ),
            risk=risk,
            max_repair_attempts=int(
                plan.get(
                    "max_repair_attempts",
                    1,
                )
            ),
            ai_mode=True,
            operation="ai_generate",
            allowed_paths=allowed_paths,
            editor_engine=editor_engine,
        )

        try:
            child_dir = run_multi_agent(
                request,
                self.runs_root,
            )
        except Exception as error:
            raise ApiError(
                "repair run execution failed: "
                f"{type(error).__name__}: {error}"
            ) from error

        child_summary = _read_json(
            child_dir /
            "RunSummary.json"
        )

        if gate_decision == "PENDING":
            try:
                decide(
                    directory,
                    repository,
                    actor,
                    "repair",
                )
            except PromotionError as error:
                current_gate = _read_json(
                    directory /
                    "GateDecision.json"
                )

                if (
                    str(
                        current_gate.get(
                            "decision",
                            "",
                        )
                    ).upper()
                    != "REPAIR"
                ):
                    raise ApiError(
                        str(error)
                    ) from error

        now = datetime.now(
            timezone.utc
        ).isoformat()

        repair_record = {
            "actor": actor,
            "parent_run_id": run_id,
            "child_run_id": child_dir.name,
            "feedback": feedback,
            "original_objective": (
                original_objective
            ),
            "allowed_paths": list(
                allowed_paths
            ),
            "timestamp": now,
        }

        for repair_dir in (
            directory,
            child_dir,
        ):
            (
                repair_dir /
                "HumanRepairRequest.json"
            ).write_text(
                json.dumps(
                    repair_record,
                    indent=2,
                    sort_keys=True,
                ) + "\n",
                encoding="utf-8",
            )

        return {
            "run_id": child_dir.name,
            "parent_run_id": run_id,
            "decision": "REPAIR",
            "status": child_summary.get(
                "status"
            ),
            "promotion_executed": False,
            "artifacts_url": (
                f"/v1/runs/{child_dir.name}/artifacts"
            ),
        }

    def stage_decision(
        self,
        run_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        with self._exclusive_operation(run_id):
            return self._stage_decision(run_id, payload)

    def _stage_decision(
        self,
        run_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        raw_decision = str(
            payload.get("decision", "")
        ).lower()

        actor = " ".join(
            str(payload.get("actor", "")).split()
        )

        if raw_decision not in DECISIONS:
            raise ApiError(
                "decision must be approve, repair, or reject"
            )

        if not actor or len(actor) > 120:
            raise ApiError(
                "actor must be a non-empty string up to 120 characters"
            )

        directory = self.run_dir(run_id)
        plan_path = directory / "ExecutionPlan.json"
        if not plan_path.is_file():
            raise ApiError("run has no ExecutionPlan.json")

        plan = _read_json(plan_path)
        repository_text = plan.get("repository")
        if not isinstance(repository_text, str) or not repository_text:
            raise ApiError("run execution plan has no repository")

        staged = {
            "gate_type": "G3_PROMOTE",
            "actor": actor,
            "requested_decision": DECISIONS[raw_decision],
            "scope": "One-shot human decision for the reviewed run",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "consumed": False,
            "promotion_executed": False,
        }

        target = directory / "GateDecision.staged.json"

        def write_staged() -> None:
            temporary = target.with_suffix(".tmp")
            temporary.write_text(
                json.dumps(
                    staged,
                    indent=2,
                    sort_keys=True,
                ) + "\n",
                encoding="utf-8",
            )
            temporary.replace(target)

        write_staged()

        try:
            summary = decide(
                directory,
                Path(repository_text),
                actor,
                raw_decision,
            )
        except PromotionError as error:
            staged["consumed"] = True
            staged["consumed_at"] = datetime.now(
                timezone.utc
            ).isoformat()
            staged["error"] = str(error)
            write_staged()
            raise ApiError(str(error)) from error

        canonical_gate = _read_json(
            directory / "GateDecision.json"
        )
        promotion_path = directory / "PromotionResult.json"
        promotion = (
            _read_json(promotion_path)
            if promotion_path.is_file()
            else {}
        )

        staged["consumed"] = True
        staged["consumed_at"] = datetime.now(
            timezone.utc
        ).isoformat()
        staged["decision"] = canonical_gate.get("decision")
        staged["status"] = summary.get("status")
        staged["promotion_executed"] = bool(promotion)
        if promotion:
            staged["promotion_branch"] = promotion.get(
                "promotion_branch"
            )
            staged["commit"] = promotion.get("commit")
        write_staged()

        return staged


def make_handler(
    api: ForgeLabApi,
) -> type[BaseHTTPRequestHandler]:

    class Handler(BaseHTTPRequestHandler):
        server_version = "ForgeLabAPI/0.9.1"

        def log_message(
            self,
            format: str,
            *args: object,
        ) -> None:
            return

        def _origin_allowed(self) -> bool:
            origin = self.headers.get("Origin")
            return (
                origin is None
                or origin.rstrip("/") == api.allowed_origin
            )

        def _send(
            self,
            status: HTTPStatus,
            payload: object,
        ) -> None:
            body = json.dumps(
                payload,
                sort_keys=True,
            ).encode("utf-8")

            self.send_response(status)

            origin = self.headers.get("Origin")

            if origin and self._origin_allowed():
                self.send_header(
                    "Access-Control-Allow-Origin",
                    origin,
                )
                self.send_header("Vary", "Origin")

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8",
            )
            self.send_header(
                "Content-Length",
                str(len(body)),
            )
            self.send_header(
                "Cache-Control",
                "no-store",
            )
            self.send_header(
                "X-Content-Type-Options",
                "nosniff",
            )
            self.end_headers()
            self.wfile.write(body)

        def _authorized(self) -> bool:
            if not self._origin_allowed():
                self._send(
                    HTTPStatus.FORBIDDEN,
                    {"error": "origin_not_allowed"},
                )
                return False

            if not api.authorize(
                self.headers.get("Authorization")
            ):
                self._send(
                    HTTPStatus.UNAUTHORIZED,
                    {"error": "unauthorized"},
                )
                return False

            return True

        def _json_body(
            self,
            maximum: int,
        ) -> dict[str, Any]:
            try:
                length = int(
                    self.headers.get(
                        "Content-Length",
                        "0",
                    )
                )
            except ValueError as error:
                raise ApiError(
                    "invalid Content-Length"
                ) from error

            if length < 2 or length > maximum:
                raise ApiError(
                    "invalid request size"
                )

            payload = json.loads(
                self.rfile.read(length)
            )

            if not isinstance(payload, dict):
                raise ApiError(
                    "request body must be a JSON object"
                )

            return payload

        def do_OPTIONS(self) -> None:
            if not self._origin_allowed():
                self._send(
                    HTTPStatus.FORBIDDEN,
                    {"error": "origin_not_allowed"},
                )
                return

            self.send_response(
                HTTPStatus.NO_CONTENT
            )

            origin = self.headers.get("Origin")

            if origin:
                self.send_header(
                    "Access-Control-Allow-Origin",
                    origin,
                )
                self.send_header(
                    "Vary",
                    "Origin",
                )

            self.send_header(
                "Access-Control-Allow-Headers",
                "Authorization, Content-Type",
            )
            self.send_header(
                "Access-Control-Allow-Methods",
                "GET, POST, OPTIONS",
            )
            self.end_headers()

        def do_GET(self) -> None:
            path = unquote(
                urlparse(self.path).path
            )

            if path == "/health":
                self._send(
                    HTTPStatus.OK,
                    {
                        "status": "ok",
                        "version": "0.9.1",
                        "runtime_sha": os.environ.get(
                            "FORGELAB_RUNTIME_SHA",
                            "unknown",
                        ),
                    },
                )
                return

            if not self._authorized():
                return

            try:
                if path == "/v1/runs":
                    self._send(
                        HTTPStatus.OK,
                        {"runs": api.list_runs()},
                    )
                    return

                status_match = re.fullmatch(
                    r"/v1/runs/([^/]+)/status",
                    path,
                )

                if status_match:
                    run_id = (
                        status_match.group(1)
                    )
                    self._send(
                        HTTPStatus.OK,
                        api.run_status(
                            run_id
                        ),
                    )
                    return

                match = re.fullmatch(
                    r"/v1/runs/([^/]+)/artifacts",
                    path,
                )

                if match:
                    run_id = match.group(1)

                    self._send(
                        HTTPStatus.OK,
                        {
                            "run_id": run_id,
                            "artifacts": api.artifacts(
                                run_id
                            ),
                        },
                    )
                    return

                self._send(
                    HTTPStatus.NOT_FOUND,
                    {"error": "not_found"},
                )

            except (
                ApiError,
                json.JSONDecodeError,
            ) as error:
                self._send(
                    HTTPStatus.NOT_FOUND,
                    {"error": str(error)},
                )

        def do_POST(self) -> None:
            path = unquote(
                urlparse(self.path).path
            )

            if not self._authorized():
                return

            try:
                if path == "/v1/runs":
                    payload = self._json_body(
                        262_144
                    )

                    created = api.create_run(
                        payload
                    )

                    self._send(
                        HTTPStatus.ACCEPTED,
                        created,
                    )
                    return

                repair_match = re.fullmatch(
                    r"/v1/runs/([^/]+)/repairs",
                    path,
                )

                if repair_match:
                    payload = self._json_body(
                        8192
                    )

                    repaired = api.request_repair(
                        repair_match.group(1),
                        payload,
                    )

                    self._send(
                        HTTPStatus.CREATED,
                        repaired,
                    )
                    return

                match = re.fullmatch(
                    r"/v1/runs/([^/]+)/decisions",
                    path,
                )

                if match:
                    payload = self._json_body(
                        4096
                    )

                    staged = api.stage_decision(
                        match.group(1),
                        payload,
                    )

                    self._send(
                        HTTPStatus.CREATED,
                        staged,
                    )
                    return

                self._send(
                    HTTPStatus.NOT_FOUND,
                    {"error": "not_found"},
                )

            except ApiConflict as error:
                self._send(
                    HTTPStatus.CONFLICT,
                    {"error": str(error)},
                )
            except (
                ApiError,
                json.JSONDecodeError,
                ValueError,
            ) as error:
                self._send(
                    HTTPStatus.BAD_REQUEST,
                    {"error": str(error)},
                )

    return Handler


def make_server(
    runs_root: Path,
    token: str,
    allowed_origin: str,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> ThreadingHTTPServer:

    if host not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        raise ApiError(
            "M8.1 API may bind only to loopback"
        )

    api = ForgeLabApi(
        runs_root,
        token,
        allowed_origin,
    )

    return ThreadingHTTPServer(
        (host, port),
        make_handler(api),
    )


def serve(
    runs_root: Path,
    token: str,
    allowed_origin: str,
    host: str = "127.0.0.1",
    port: int = 8765,
) -> None:

    server = make_server(
        runs_root,
        token,
        allowed_origin,
        host,
        port,
    )

    try:
        print(
            f"ForgeLab API listening on "
            f"http://{host}:{server.server_port}"
        )
        server.serve_forever()
    finally:
        server.server_close()

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifacts import ArtifactStore
from .quality import changed_paths
from .tools import run_bounded


class PromotionError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
        timeout=30,
    )


def _git_ok(repo: Path, *args: str) -> str:
    result = _git(repo, *args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PromotionError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def _ref(repo: Path, name: str) -> str | None:
    result = _git(repo, "rev-parse", "--verify", name)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _write_decision(store: ArtifactStore, actor: str, decision: str, scope: str) -> None:
    store.write(
        "GateDecision.json",
        {
            "gate_type": "G3_PROMOTE",
            "actor": actor,
            "decision": decision,
            "scope": scope,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


def _normalized_patch(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


def _branch_name(run_id: str) -> str:
    if not re.fullmatch(r"run-[A-Za-z0-9_-]+", run_id):
        raise PromotionError("invalid run id for promotion branch")
    return f"forgelab/promote/{run_id}"


def _remove_uncommitted_promotion(
    repository: Path,
    worktree: Path,
    branch: str,
    patch_path: Path,
    patch_was_applied: bool,
) -> None:
    if patch_was_applied and worktree.exists():
        reverse = _git(worktree, "apply", "--reverse", str(patch_path))
        if reverse.returncode != 0:
            raise PromotionError(
                "promotion failed and exact patch rollback failed; "
                f"temporary worktree retained at {worktree}: {reverse.stderr.strip()}"
            )

    if worktree.exists():
        status = _git(worktree, "status", "--porcelain", "--untracked-files=all")
        if status.returncode != 0 or status.stdout.strip():
            raise PromotionError(
                "promotion cleanup refused because temporary worktree is not clean; "
                f"retained at {worktree}"
            )
        removed = _git(repository, "worktree", "remove", str(worktree))
        if removed.returncode != 0:
            raise PromotionError(
                "promotion cleanup could not remove temporary worktree: "
                f"{removed.stderr.strip()}"
            )

    existing = _ref(repository, f"refs/heads/{branch}")
    if existing is not None:
        deleted = _git(repository, "branch", "-d", branch)
        if deleted.returncode != 0:
            raise PromotionError(
                "promotion cleanup could not safely delete uncommitted branch: "
                f"{deleted.stderr.strip()}"
            )


def decide(run_dir: Path, repository: Path, actor: str, decision: str) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    repository = repository.resolve()
    actor = " ".join(actor.split())
    if not actor or actor.upper() == "SYSTEM":
        raise PromotionError("a non-system human actor is required")

    decision = decision.upper()
    if decision not in {"APPROVE", "REJECT", "REPAIR"}:
        raise PromotionError("decision must be approve, reject, or repair")

    store = ArtifactStore(run_dir)
    summary = _load(run_dir / "RunSummary.json")
    plan = _load(run_dir / "ExecutionPlan.json")
    gate = _load(run_dir / "GateDecision.json")
    if gate.get("decision") != "PENDING":
        raise PromotionError("gate has already been decided")

    if decision in {"REJECT", "REPAIR"}:
        _write_decision(store, actor, decision, "Candidate patch not promoted")
        summary["decision"] = decision
        summary["status"] = "CLOSED" if decision == "REJECT" else "REPAIRING"
        summary.setdefault("history", []).append(summary["status"])
        store.write("RunSummary.json", summary)
        return summary

    required = {
        "run": summary.get("status") == "READY_FOR_DECISION",
        "tests": summary.get("tests") == "PASS",
        "review": _load(run_dir / "ReviewReport.json").get("status") == "PASS",
        "security": _load(run_dir / "SecurityReport.json").get("status") == "PASS",
        "patch": (run_dir / "Changes.patch").is_file(),
        "repository": str(repository) == plan.get("repository"),
    }
    failed = [name for name, passed in required.items() if not passed]
    if failed:
        raise PromotionError(f"promotion prerequisites failed: {failed}")

    base_head = str(plan.get("base_head") or "")
    source_head = _git_ok(repository, "rev-parse", "HEAD")
    source_branch = _git_ok(repository, "branch", "--show-current")
    source_status = _git_ok(repository, "status", "--porcelain", "--untracked-files=all")
    if source_head != base_head:
        raise PromotionError("repository HEAD no longer matches the reviewed base")
    if source_status:
        raise PromotionError("repository must be clean before promotion")

    patch_path = run_dir / "Changes.patch"
    patch = patch_path.read_text(encoding="utf-8")
    patch_sha256 = hashlib.sha256(patch_path.read_bytes()).hexdigest()
    patch_paths = changed_paths(patch)

    allowed: set[str] = set()
    for task in plan["tasks"]:
        if "path" in task:
            allowed.add(task["path"])
        else:
            allowed.update(task.get("scope", {}).get("allowed_paths", []))
    allowed.discard(".git")
    allowed.discard("main")
    if not allowed:
        raise PromotionError("execution plan has no promotable path scope")
    if not patch_paths or patch_paths - allowed:
        raise PromotionError("patch scope no longer matches the reviewed plan")

    review_paths = set(_load(run_dir / "ReviewReport.json").get("changed_paths", []))
    if review_paths and patch_paths != review_paths:
        raise PromotionError("reviewed changed paths no longer match Changes.patch")

    branch = _branch_name(run_dir.name)
    if _ref(repository, f"refs/heads/{branch}") is not None:
        raise PromotionError("promotion branch already exists; approval cannot be reused")

    main_before = _ref(repository, "refs/heads/main")
    worktree_root = Path(tempfile.mkdtemp(prefix=f"forgelab-promote-{run_dir.name}-"))
    worktree = worktree_root / "worktree"
    branch_created = False
    patch_applied = False

    try:
        created = _git(
            repository,
            "worktree",
            "add",
            "-b",
            branch,
            str(worktree),
            base_head,
        )
        if created.returncode != 0:
            raise PromotionError(f"promotion worktree creation failed: {created.stderr.strip()}")
        branch_created = True

        check = _git(worktree, "apply", "--check", str(patch_path))
        if check.returncode != 0:
            raise PromotionError(f"patch preflight failed: {check.stderr.strip()}")

        applied = _git(worktree, "apply", str(patch_path))
        if applied.returncode != 0:
            raise PromotionError(f"patch application failed: {applied.stderr.strip()}")
        patch_applied = True

        actual_diff = _git_ok(worktree, "diff", "--binary", "--no-ext-diff")
        if _normalized_patch(actual_diff) != _normalized_patch(patch):
            raise PromotionError("applied diff is not byte-equivalent to the reviewed patch")

        test = run_bounded(
            list(plan["test_command"]),
            worktree,
            int(plan.get("timeout_seconds", 60)),
        )
        evidence = _load(run_dir / "TestEvidence.json")
        evidence.setdefault("evidence", []).append(
            {
                "evidence_id": "ev-promotion-tests",
                "check_type": "promotion_tests",
                "command_or_tool": plan["test_command"],
                "exit_status": test.exit_status,
                "summary": (
                    "Promotion branch tests passed"
                    if test.exit_status == 0
                    else "Promotion branch tests failed; promotion rolled back"
                ),
                "stdout": test.stdout[-4000:],
                "stderr": test.stderr[-4000:],
                "timed_out": test.timed_out,
            }
        )
        store.write("TestEvidence.json", evidence)

        if test.exit_status != 0:
            _remove_uncommitted_promotion(
                repository,
                worktree,
                branch,
                patch_path,
                patch_applied,
            )
            branch_created = False
            patch_applied = False
            shutil.rmtree(worktree_root, ignore_errors=True)
            _write_decision(
                store,
                actor,
                "REPAIR",
                "Approval consumed; promotion tests failed and the temporary branch was removed",
            )
            summary["status"] = "REPAIRING"
            summary["decision"] = "Repair required after failed promotion tests"
            summary.setdefault("history", []).extend(["APPROVED", "PROMOTE", "REPAIRING"])
            store.write("RunSummary.json", summary)
            return summary

        status_after_test = _git_ok(worktree, "status", "--porcelain", "--untracked-files=all")
        diff_after_test = _git_ok(worktree, "diff", "--binary", "--no-ext-diff")
        if _normalized_patch(diff_after_test) != _normalized_patch(patch):
            raise PromotionError("tests changed the reviewed diff; promotion blocked")
        untracked = [line for line in status_after_test.splitlines() if line.startswith("?? ")]
        if untracked:
            raise PromotionError("tests created untracked files in promotion worktree")

        _git_ok(worktree, "add", "--", *sorted(patch_paths))
        staged_diff = _git_ok(worktree, "diff", "--cached", "--binary", "--no-ext-diff")
        if _normalized_patch(staged_diff) != _normalized_patch(patch):
            raise PromotionError("staged commit diff differs from the reviewed patch")

        commit_message = f"ForgeLab approved promotion {run_dir.name}"
        committed = _git(
            worktree,
            "-c",
            "user.name=ForgeLab Promotion",
            "-c",
            "user.email=forgelab@local",
            "commit",
            "-m",
            commit_message,
        )
        if committed.returncode != 0:
            raise PromotionError(f"local promotion commit failed: {committed.stderr.strip()}")

        commit = _git_ok(worktree, "rev-parse", "HEAD")
        committed_branch = _git_ok(worktree, "branch", "--show-current")
        if committed_branch != branch:
            raise PromotionError("promotion commit was created on an unexpected branch")

        removed = _git(repository, "worktree", "remove", str(worktree))
        if removed.returncode != 0:
            raise PromotionError(f"verified promotion worktree could not be removed: {removed.stderr.strip()}")
        shutil.rmtree(worktree_root, ignore_errors=True)

        source_head_after = _git_ok(repository, "rev-parse", "HEAD")
        source_branch_after = _git_ok(repository, "branch", "--show-current")
        source_status_after = _git_ok(repository, "status", "--porcelain", "--untracked-files=all")
        main_after = _ref(repository, "refs/heads/main")
        source_unchanged = (
            source_head_after == source_head
            and source_branch_after == source_branch
            and not source_status_after
        )
        main_untouched = main_before == main_after
        if not source_unchanged or not main_untouched:
            raise PromotionError("source checkout or main ref changed during isolated promotion")

        result = {
            "schema_version": "1.0",
            "run_id": run_dir.name,
            "actor": actor,
            "source_repository": str(repository),
            "source_base_head": base_head,
            "source_branch": source_branch,
            "source_head_unchanged": True,
            "promotion_branch": branch,
            "commit": commit,
            "changed_paths": sorted(patch_paths),
            "patch_sha256": patch_sha256,
            "tests": "PASS",
            "source_main_untouched": True,
            "push_executed": False,
            "merge_executed": False,
            "force_operations_executed": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        store.write_optional_json("PromotionResult.json", result)
        _write_decision(
            store,
            actor,
            "APPROVE",
            f"Verified patch committed locally to {branch}; no push or merge executed",
        )
        summary["status"] = "DONE"
        summary["decision"] = f"Approved by {actor}; committed locally to {branch}"
        summary["promotion_branch"] = branch
        summary["promotion_commit"] = commit
        summary["source_repository_unchanged"] = True
        summary.setdefault("history", []).extend(["APPROVED", "PROMOTE", "VERIFIED", "DONE"])
        store.write("RunSummary.json", summary)
        return summary

    except Exception:
        if branch_created and _ref(repository, f"refs/heads/{branch}") == base_head:
            _remove_uncommitted_promotion(
                repository,
                worktree,
                branch,
                patch_path,
                patch_applied,
            )
        if not worktree.exists():
            shutil.rmtree(worktree_root, ignore_errors=True)
        raise

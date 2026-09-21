from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class WorkspaceError(RuntimeError):
    pass


def _git(repo: Path, *args: str, timeout: int = 30) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise WorkspaceError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


@dataclass
class IsolatedWorkspace:
    source_repo: Path
    run_id: str
    path: Path | None = None
    branch: str | None = None
    base_head: str | None = None
    _temporary: tempfile.TemporaryDirectory[str] | None = None

    def create(self) -> Path:
        repo = self.source_repo.resolve()
        if not (repo / ".git").exists():
            raise WorkspaceError(f"not a Git repository: {repo}")
        if _git(repo, "status", "--porcelain"):
            raise WorkspaceError("source repository must be clean before isolation")
        self.base_head = _git(repo, "rev-parse", "HEAD")
        self.branch = f"forgelab/{self.run_id}"
        self._temporary = tempfile.TemporaryDirectory(prefix=f"forgelab-{self.run_id}-")
        self.path = Path(self._temporary.name) / "worktree"
        _git(repo, "worktree", "add", "--detach", str(self.path), self.base_head)
        return self.path

    def diff(self) -> str:
        if self.path is None:
            raise WorkspaceError("workspace has not been created")
        patch = _git(self.path, "diff", "--binary", "--no-ext-diff")
        return patch + "\n" if patch else ""

    def verify_source_unchanged(self) -> bool:
        if self.base_head is None:
            return False
        return (
            _git(self.source_repo, "rev-parse", "HEAD") == self.base_head
            and not _git(self.source_repo, "status", "--porcelain")
        )

    def close(self) -> None:
        if self.path is not None and self.path.exists():
            _git(self.source_repo, "worktree", "remove", "--force", str(self.path))
        if self._temporary is not None:
            self._temporary.cleanup()
        self.path = None

    def __enter__(self) -> "IsolatedWorkspace":
        self.create()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

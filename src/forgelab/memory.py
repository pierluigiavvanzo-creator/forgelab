from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


class MemoryError(RuntimeError):
    pass


class MemorySecurityError(MemoryError):
    pass


ROOT_FILES = ("AGENTS.md", "PROJECT_STATE.md", "ROADMAP.md", "DECISIONS.md")
EXACT_DOCS = ("docs/architecture.md", "docs/contracts.md", "docs/handovers/HANDOVER_CURRENT.md")
GLOBS = ("docs/decisions/ADR-*.md", "docs/*_ACCEPTANCE_REPORT.md")
MANDATORY_CONTEXT = ("AGENTS.md", "PROJECT_STATE.md")
REPOSITORY_TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml",
    ".ps1", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".sql",
}
REPOSITORY_TEXT_NAMES = {"Dockerfile", "Makefile"}
DISALLOWED_DIRECTORY_NAMES = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__",
    "dist", "build", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
}
DISALLOWED_FORGELAB_DIRECTORIES = {"runtime", "demo-repositories"}
SECRET_FILE_NAMES = {
    ".env", "id_rsa", "id_ed25519", "credentials", "credentials.json",
    "secrets.json", "secrets.yaml", "secrets.yml",
}
SECRET_FILE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
SECRET_PATTERNS = (
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(r"(?i)(?:api[_-]?key|secret|token|password)\s*[=:]\s*['\"][A-Za-z0-9_\-./+=]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
)


@dataclass(frozen=True)
class MemoryDocument:
    path: str
    sha256: str
    size_chars: int
    priority: int
    content: str
    source: str = "canonical"

    def metadata(self) -> dict[str, object]:
        data = asdict(self)
        data.pop("content")
        return data


def _candidate_paths(root: Path) -> Iterable[Path]:
    for relative in ROOT_FILES + EXACT_DOCS:
        candidate = root / relative
        if candidate.is_file():
            yield candidate
    for pattern in GLOBS:
        yield from sorted(root.glob(pattern))


def _priority(relative: str) -> int:
    if relative in MANDATORY_CONTEXT:
        return 100
    if relative in {"DECISIONS.md", "ROADMAP.md"}:
        return 80
    if relative.startswith("docs/decisions/"):
        return 70
    if relative in EXACT_DOCS:
        return 60
    return 30


def _contains_secret(content: str) -> bool:
    return any(pattern.search(content) for pattern in SECRET_PATTERNS)


def _is_secret_filename(relative: str) -> bool:
    path = Path(relative)
    name = path.name.casefold()
    if name in SECRET_FILE_NAMES or name.startswith(".env."):
        return True
    return path.suffix.casefold() in SECRET_FILE_SUFFIXES


def _is_disallowed_repository_path(relative: str) -> bool:
    path = Path(relative)
    parts = path.parts
    if any(part in DISALLOWED_DIRECTORY_NAMES for part in parts[:-1]):
        return True
    if any(part.startswith("_repair_backup") for part in parts[:-1]):
        return True
    if len(parts) >= 2 and parts[0] == ".forgelab" and parts[1] in DISALLOWED_FORGELAB_DIRECTORIES:
        return True
    return _is_secret_filename(relative)


def _is_text_candidate(path: Path) -> bool:
    return path.name in REPOSITORY_TEXT_NAMES or path.suffix.casefold() in REPOSITORY_TEXT_SUFFIXES


def _repository_candidate_paths(root: Path, max_candidates: int) -> Iterable[Path]:
    emitted = 0
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        relative_dir = current_path.relative_to(root)

        kept_directories: list[str] = []
        for name in sorted(directory_names):
            relative = (relative_dir / name).as_posix()
            if _is_disallowed_repository_path(f"{relative}/placeholder"):
                continue
            kept_directories.append(name)
        directory_names[:] = kept_directories

        for name in sorted(file_names):
            candidate = current_path / name
            relative = candidate.relative_to(root).as_posix()
            if _is_disallowed_repository_path(relative) or not _is_text_candidate(candidate):
                continue
            yield candidate
            emitted += 1
            if emitted >= max_candidates:
                return


def _terms(query: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9_]{3,}", query.lower())}


def _relevance(document: MemoryDocument, terms: set[str]) -> int:
    if not terms:
        return 0
    haystack = f"{document.path}\n{document.content}".lower()
    return sum(haystack.count(term) for term in terms)


class ProjectMemory:
    def __init__(self, root: Path, max_file_chars: int = 200_000) -> None:
        self.root = root.resolve()
        self.max_file_chars = max_file_chars

    def load(self) -> list[MemoryDocument]:
        documents: list[MemoryDocument] = []
        seen: set[str] = set()
        for candidate in _candidate_paths(self.root):
            resolved = candidate.resolve()
            if candidate.is_symlink() or self.root not in resolved.parents:
                raise MemorySecurityError(f"memory path escapes project root: {candidate}")
            relative = resolved.relative_to(self.root).as_posix()
            if relative in seen:
                continue
            content = resolved.read_text(encoding="utf-8")
            if len(content) > self.max_file_chars:
                raise MemoryError(f"memory file exceeds size limit: {relative}")
            if _contains_secret(content):
                raise MemorySecurityError(f"potential secret found in canonical memory: {relative}")
            seen.add(relative)
            documents.append(MemoryDocument(
                relative,
                hashlib.sha256(content.encode("utf-8")).hexdigest(),
                len(content),
                _priority(relative),
                content,
                "canonical",
            ))
        return documents

    def snapshot(self) -> dict[str, object]:
        documents = self.load()
        manifest_source = "\n".join(f"{item.path}:{item.sha256}" for item in documents)
        return {
            "project_root": str(self.root),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "document_count": len(documents),
            "manifest_sha256": hashlib.sha256(manifest_source.encode("utf-8")).hexdigest(),
            "documents": [item.metadata() for item in documents],
        }

    def _load_repository_documents(
        self,
        canonical_paths: set[str],
        excluded_paths: set[str],
        max_repository_file_chars: int,
        max_repository_candidates: int,
    ) -> tuple[list[MemoryDocument], dict[str, int]]:
        documents: list[MemoryDocument] = []
        skipped = {
            "excluded_path": 0,
            "symlink_or_escape": 0,
            "decode_error": 0,
            "oversized": 0,
            "potential_secret": 0,
        }

        for candidate in _repository_candidate_paths(self.root, max_repository_candidates):
            try:
                resolved = candidate.resolve()
                relative = candidate.relative_to(self.root).as_posix()
            except (OSError, ValueError):
                skipped["symlink_or_escape"] += 1
                continue

            if relative in canonical_paths or relative in excluded_paths:
                skipped["excluded_path"] += 1
                continue
            if candidate.is_symlink() or self.root not in resolved.parents:
                skipped["symlink_or_escape"] += 1
                continue

            try:
                content = resolved.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                skipped["decode_error"] += 1
                continue

            if len(content) > max_repository_file_chars:
                skipped["oversized"] += 1
                continue
            if _contains_secret(content):
                skipped["potential_secret"] += 1
                continue

            documents.append(MemoryDocument(
                relative,
                hashlib.sha256(content.encode("utf-8")).hexdigest(),
                len(content),
                10,
                content,
                "repository",
            ))

        return documents, skipped

    def select(
        self,
        query: str,
        max_chars: int = 20_000,
        *,
        max_repository_files: int = 8,
        max_repository_file_chars: int = 12_000,
        max_repository_candidates: int = 2_000,
        exclude_paths: Iterable[str] = (),
    ) -> dict[str, object]:
        if max_chars < 1:
            raise ValueError("max_chars must be positive")
        if max_repository_files < 0:
            raise ValueError("max_repository_files cannot be negative")
        if max_repository_file_chars < 1 or max_repository_candidates < 1:
            raise ValueError("repository context caps must be positive")

        canonical = self.load()
        canonical_paths = {item.path for item in canonical}
        normalized_exclusions = {Path(item).as_posix() for item in exclude_paths}
        repository, skipped = self._load_repository_documents(
            canonical_paths,
            normalized_exclusions,
            max_repository_file_chars,
            max_repository_candidates,
        )
        terms = _terms(query)

        def ordering(document: MemoryDocument) -> tuple[int, int, str]:
            mandatory = 1 if document.path in MANDATORY_CONTEXT else 0
            score = _relevance(document, terms) * 100 + document.priority
            return (-mandatory, -score, document.path)

        ordered = sorted(canonical + repository, key=ordering)
        selected: list[MemoryDocument] = []
        used = 0
        repository_count = 0

        for document in ordered:
            required = document.path in MANDATORY_CONTEXT
            relevance = _relevance(document, terms)
            if document.source == "repository" and repository_count >= max_repository_files:
                continue
            if used + document.size_chars > max_chars:
                if required:
                    raise MemoryError("context budget is too small for mandatory project memory")
                continue
            if not required and relevance == 0:
                continue

            selected.append(document)
            used += document.size_chars
            if document.source == "repository":
                repository_count += 1

        manifest_source = "\n".join(
            f"{item.source}:{item.path}:{item.sha256}"
            for item in selected
        )
        canonical_count = sum(item.source == "canonical" for item in selected)

        return {
            "context_contract_version": "1.0",
            "mode": "read_only",
            "write_scope_expansion": False,
            "query": query,
            "max_chars": max_chars,
            "used_chars": used,
            "selection_sha256": hashlib.sha256(manifest_source.encode("utf-8")).hexdigest(),
            "selected_paths": [item.path for item in selected],
            "canonical_document_count": canonical_count,
            "repository_document_count": repository_count,
            "selection_policy": {
                "max_repository_files": max_repository_files,
                "max_repository_file_chars": max_repository_file_chars,
                "max_repository_candidates": max_repository_candidates,
                "excluded_write_paths": sorted(normalized_exclusions),
                "disallowed_paths_enforced": True,
                "secret_filter_enforced": True,
            },
            "excluded_summary": skipped,
            "documents": [
                {
                    "path": item.path,
                    "sha256": item.sha256,
                    "size_chars": item.size_chars,
                    "source": item.source,
                    "content": item.content,
                }
                for item in selected
            ],
        }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)

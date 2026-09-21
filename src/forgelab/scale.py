from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat()


@contextmanager
def _connect(path: Path) -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(path, timeout=10, isolation_level=None)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        with connection:
            yield connection
    finally:
        connection.close()


class DurableTaskQueue:
    """SQLite queue with tenant isolation, idempotency, leases, and bounded retry."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _connect(path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS queue_tasks (
                    tenant_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL,
                    leased_by TEXT,
                    lease_until TEXT,
                    available_at TEXT NOT NULL,
                    last_error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, task_id),
                    UNIQUE (tenant_id, idempotency_key)
                );
                CREATE INDEX IF NOT EXISTS queue_ready
                ON queue_tasks (tenant_id, status, available_at);
            """)

    def enqueue(self, tenant_id: str, task_id: str, payload: dict[str, Any],
                *, max_attempts: int = 3, idempotency_key: str | None = None) -> bool:
        if not tenant_id or not task_id:
            raise ValueError("tenant_id and task_id are required")
        if max_attempts < 1 or max_attempts > 20:
            raise ValueError("max_attempts must be between 1 and 20")
        now = _iso()
        key = idempotency_key or task_id
        with _connect(self.path) as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO queue_tasks "
                "(tenant_id, task_id, idempotency_key, payload, max_attempts, available_at, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (tenant_id, task_id, key, json.dumps(payload, sort_keys=True), max_attempts, now, now, now),
            )
            return cursor.rowcount == 1

    def lease(self, tenant_id: str, worker_id: str, *, lease_seconds: int = 60) -> dict[str, Any] | None:
        if lease_seconds < 1:
            raise ValueError("lease_seconds must be positive")
        now = _now()
        with _connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "UPDATE queue_tasks SET status='queued', leased_by=NULL, lease_until=NULL, updated_at=? "
                "WHERE tenant_id=? AND status='leased' AND lease_until < ? AND attempts < max_attempts",
                (_iso(now), tenant_id, _iso(now)),
            )
            row = db.execute(
                "SELECT * FROM queue_tasks WHERE tenant_id=? AND status='queued' "
                "AND available_at <= ? AND attempts < max_attempts ORDER BY created_at, task_id LIMIT 1",
                (tenant_id, _iso(now)),
            ).fetchone()
            if row is None:
                db.execute("COMMIT")
                return None
            attempts = int(row["attempts"]) + 1
            lease_until = now + timedelta(seconds=lease_seconds)
            db.execute(
                "UPDATE queue_tasks SET status='leased', attempts=?, leased_by=?, lease_until=?, updated_at=? "
                "WHERE tenant_id=? AND task_id=?",
                (attempts, worker_id, _iso(lease_until), _iso(now), tenant_id, row["task_id"]),
            )
            db.execute("COMMIT")
            return {"tenant_id": tenant_id, "task_id": row["task_id"], "payload": json.loads(row["payload"]),
                    "attempt": attempts, "max_attempts": int(row["max_attempts"]), "lease_until": _iso(lease_until)}

    def complete(self, tenant_id: str, task_id: str, worker_id: str) -> None:
        self._finish(tenant_id, task_id, worker_id, "done", None, 0)

    def fail(self, tenant_id: str, task_id: str, worker_id: str, error: str, *, retry_delay_seconds: int = 0) -> str:
        return self._finish(tenant_id, task_id, worker_id, "failed", error, retry_delay_seconds)

    def _finish(self, tenant_id: str, task_id: str, worker_id: str, outcome: str,
                error: str | None, retry_delay_seconds: int) -> str:
        with _connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM queue_tasks WHERE tenant_id=? AND task_id=?", (tenant_id, task_id)).fetchone()
            if row is None or row["status"] != "leased" or row["leased_by"] != worker_id:
                db.execute("ROLLBACK")
                raise ValueError("task is not leased by this worker")
            if outcome == "done":
                status, available = "done", row["available_at"]
            elif int(row["attempts"]) < int(row["max_attempts"]):
                status, available = "queued", _iso(_now() + timedelta(seconds=max(0, retry_delay_seconds)))
            else:
                status, available = "dead", row["available_at"]
            db.execute(
                "UPDATE queue_tasks SET status=?, available_at=?, leased_by=NULL, lease_until=NULL, last_error=?, updated_at=? "
                "WHERE tenant_id=? AND task_id=?",
                (status, available, error, _iso(), tenant_id, task_id),
            )
            db.execute("COMMIT")
            return status

    def counts(self, tenant_id: str) -> dict[str, int]:
        with _connect(self.path) as db:
            rows = db.execute("SELECT status, COUNT(*) AS n FROM queue_tasks WHERE tenant_id=? GROUP BY status", (tenant_id,)).fetchall()
        return {row["status"]: int(row["n"]) for row in rows}


class TenantResultCache:
    """Content-addressed JSON cache; tenant is part of every lookup boundary."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with _connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS result_cache (tenant_id TEXT, cache_key TEXT, value TEXT, expires_at TEXT, created_at TEXT, PRIMARY KEY (tenant_id, cache_key))")

    @staticmethod
    def key(namespace: str, payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return f"{namespace}:{hashlib.sha256(canonical.encode()).hexdigest()}"

    def put(self, tenant_id: str, cache_key: str, value: dict[str, Any], *, ttl_seconds: int = 3600) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        with _connect(self.path) as db:
            db.execute(
                "INSERT INTO result_cache VALUES (?, ?, ?, ?, ?) ON CONFLICT(tenant_id, cache_key) DO UPDATE SET value=excluded.value, expires_at=excluded.expires_at, created_at=excluded.created_at",
                (tenant_id, cache_key, json.dumps(value, sort_keys=True), _iso(_now()+timedelta(seconds=ttl_seconds)), _iso()),
            )

    def get(self, tenant_id: str, cache_key: str) -> dict[str, Any] | None:
        with _connect(self.path) as db:
            row = db.execute("SELECT value, expires_at FROM result_cache WHERE tenant_id=? AND cache_key=?", (tenant_id, cache_key)).fetchone()
            if row is None:
                return None
            if datetime.fromisoformat(row["expires_at"]) <= _now():
                db.execute("DELETE FROM result_cache WHERE tenant_id=? AND cache_key=?", (tenant_id, cache_key))
                return None
            return json.loads(row["value"])


@dataclass(frozen=True)
class ScheduledResult:
    task_id: str
    status: str
    value: Any = None
    error: str | None = None


def run_parallel_dag(tasks: list[dict[str, Any]], execute: Callable[[dict[str, Any]], Any], *, max_workers: int = 4) -> list[ScheduledResult]:
    """Run independent DAG layers concurrently and block descendants of failures."""
    if max_workers < 1 or max_workers > 32:
        raise ValueError("max_workers must be between 1 and 32")
    by_id = {task["task_id"]: task for task in tasks}
    if len(by_id) != len(tasks):
        raise ValueError("task ids must be unique")
    for task in tasks:
        missing = set(task.get("dependencies", [])) - set(by_id)
        if missing:
            raise ValueError(f"unknown dependencies: {sorted(missing)}")
    pending = set(by_id); results: dict[str, ScheduledResult] = {}
    while pending:
        blocked = [task_id for task_id in pending if any(results.get(dep, ScheduledResult(dep,"pending")).status in {"failed","blocked"} for dep in by_id[task_id].get("dependencies", []))]
        for task_id in blocked:
            results[task_id] = ScheduledResult(task_id, "blocked", error="dependency failed"); pending.remove(task_id)
        ready = [task_id for task_id in pending if all(dep in results and results[dep].status == "passed" for dep in by_id[task_id].get("dependencies", []))]
        if not ready:
            if pending:
                raise ValueError("task graph contains a cycle")
            break
        with ThreadPoolExecutor(max_workers=min(max_workers, len(ready)), thread_name_prefix="forgelab") as pool:
            futures = {pool.submit(execute, by_id[task_id]): task_id for task_id in ready}
            for future in as_completed(futures):
                task_id = futures[future]
                try: results[task_id] = ScheduledResult(task_id, "passed", value=future.result())
                except Exception as exc: results[task_id] = ScheduledResult(task_id, "failed", error=str(exc))
                pending.remove(task_id)
    return [results[task["task_id"]] for task in tasks]


class UsageMeter:
    """Append-only per-tenant usage ledger with an enforceable cost cap."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        with _connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS usage_events (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT, run_id TEXT, kind TEXT, units REAL, cost REAL, created_at TEXT)")

    def record(self, tenant_id: str, run_id: str, kind: str, units: float, cost: float, *, cost_cap: float | None = None) -> None:
        if units < 0 or cost < 0:
            raise ValueError("usage and cost cannot be negative")
        with self._lock, _connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            current = float(db.execute("SELECT COALESCE(SUM(cost),0) FROM usage_events WHERE tenant_id=? AND run_id=?", (tenant_id, run_id)).fetchone()[0])
            if cost_cap is not None and current + cost > cost_cap:
                db.execute("ROLLBACK"); raise ValueError("run cost cap exceeded")
            db.execute("INSERT INTO usage_events (tenant_id,run_id,kind,units,cost,created_at) VALUES (?,?,?,?,?,?)", (tenant_id,run_id,kind,units,cost,_iso()))
            db.execute("COMMIT")

    def summary(self, tenant_id: str) -> dict[str, Any]:
        with _connect(self.path) as db:
            rows = db.execute("SELECT kind, SUM(units) units, SUM(cost) cost FROM usage_events WHERE tenant_id=? GROUP BY kind", (tenant_id,)).fetchall()
        return {"tenant_id":tenant_id,"total_cost":sum(float(r["cost"]) for r in rows),"by_kind":[{"kind":r["kind"],"units":float(r["units"]),"cost":float(r["cost"])} for r in rows]}

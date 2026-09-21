# M8 Core Acceptance Report

Date: 2026-09-18

## Outcome

M8 Core establishes measurable, tenant-safe scale primitives without adopting
production infrastructure before demand metrics exist.

## Accepted capabilities

- KPI report derived from canonical run artifacts, with unavailable signals stated explicitly.
- Idempotent SQLite task queue scoped by tenant.
- Atomic work leases, expired-lease recovery, bounded retries, and dead-letter state.
- Content-addressed result cache scoped by tenant with deterministic keys and expiry.
- Bounded execution of independent DAG tasks while preserving dependency order.
- Automatic blocking of descendants after an upstream failure.
- Append-only usage events and per-run cost-cap enforcement.
- CLI access to the KPI report through `forgelab metrics`.

## Verification

- 57 automated tests pass.
- Tests cover cross-tenant isolation, idempotency, lease ownership, retry caps,
  cache boundaries, concurrent DAG layers, failure propagation, cost caps, and
  artifact-derived KPI calculation.
- Existing M0 through M7 tests remain green.

## Boundary

The local SQLite and in-process implementations are reference adapters, not a
claim of horizontal production scale. A distributed broker, shared database,
production billing integration, and multi-node workers require observed demand,
operational SLOs, and a repository-first benchmark before adoption.

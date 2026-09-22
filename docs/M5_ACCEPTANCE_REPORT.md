# M5 Acceptance Report

Date: 2026-09-18.

## Outcome

M5 makes project memory repository-backed and independently reconstructible.
Every document is represented by path, size, priority, and SHA-256 hash. Each
multi-agent run stores both a metadata snapshot and the exact selected context.

## Canonical sources

- `AGENTS.md`
- `PROJECT_STATE.md`
- `ROADMAP.md`
- `DECISIONS.md`
- `docs/architecture.md`
- `docs/contracts.md`
- `docs/handovers/HANDOVER_CURRENT.md`
- `docs/decisions/ADR-*.md`
- milestone acceptance reports

## Acceptance evidence

| Scenario | Result | Enforced behavior |
| --- | --- | --- |
| New process loads project | PASS | Canonical sources discovered without chat history |
| Memory snapshot | PASS | Stable content hashes and manifest hash produced |
| Task-specific query | PASS | Mandatory memory plus relevant decisions selected |
| Context budget too small | PASS | Mandatory memory is never silently truncated |
| Oversized memory file | PASS | Ingestion stops with explicit failure |
| Symlink or path escape | PASS | File is rejected before content use |
| Potential embedded secret | PASS | Memory ingestion is blocked |
| Multi-agent run | PASS | Snapshot and context bundle references recorded in plan |

## Retrieval boundary

M5 uses deterministic lexical relevance. It does not claim semantic retrieval,
embedding similarity, or complete recall. Those mechanisms should be added only
after a representative task set demonstrates a material context-selection gap.

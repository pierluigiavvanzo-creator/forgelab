# M6 Acceptance Report

Date: 2026-09-18.

## Outcome

M6 moves security policy from documentation into the execution boundary. The
multi-agent orchestrator now uses a single `ToolGateway` for edits and tests.
Every authorization and result is represented in `ToolAudit.json`, while raw
arguments and secret values are excluded.

## Acceptance evidence

| Scenario | Result | Enforced behavior |
| --- | --- | --- |
| Role requests unassigned tool | PASS | Request denied before execution |
| Developer edits outside task scope | PASS | File remains unchanged |
| Network host not allowlisted | PASS | Default-deny blocks authorization |
| Network host explicitly allowlisted | PASS | Security role can authorize it |
| Dependency lacks provenance | PASS | Adoption blocked |
| Dependency has license provenance review | PASS | Authorization recorded |
| Destructive action lacks approval | PASS | Action blocked |
| Approved destructive action | PASS | Only authorized role can proceed |
| Secret access | PASS | Value passed directly to callback and omitted from audit |
| Tool arguments | PASS | Audit stores SHA-256 and metadata, not raw arguments |
| Multi-agent run | PASS | Tool audit referenced by SecurityReport |

## Remaining isolation boundary

M6 enforces application-level governance around the current local worktree.
Operating-system containers, process resource quotas, egress firewalling, and a
managed secret store remain later deployment concerns. The current controls do
not claim to replace those infrastructure boundaries.

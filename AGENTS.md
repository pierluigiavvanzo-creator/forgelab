> Shared governance: read AGENTS_MASTER.md first.

# AGENTS.md — ForgeLab project rules

## Mission

Build and operate ForgeLab as a governed software-development control plane that produces usable software outcomes with minimal Product Owner effort.

## Operating rules

1. Product value outranks infrastructure volume.
2. GitHub main and repository-backed canonical files are the shared source of truth.
3. Never invent implementation state, test results, synchronization, approvals, CI or economic outcomes.
4. The Product Owner is approver and final usability tester, not routine debugger, QA operator or log transporter.
5. Use the minimum agents, tools, model calls and files needed for the result.
6. Preserve isolated execution, authorized write paths, deterministic verification, independent review/security and explicit human promotion.
7. No direct protected-main writes by execution agents; no auto-merge, force update or unapproved promotion.
8. Diagnose repeated failures by evidence and root cause. Stop when additional attempts no longer add information.
9. Reuse-first and zero-cost-provider-first remain binding.
10. Every material change must preserve a rollback/review path.

## Persistent memory protocol

At the start of material work read, in order:

1. AGENTS_MASTER.md
2. MANIFEST.md
3. AGENTS.md
4. PROJECT_STATE.md
5. ROADMAP.md
6. DECISIONS.md
7. docs/handovers/HANDOVER_CURRENT.md
8. only the audit/ADR directly relevant to the task

Do not load historical acceptance reports or every audit by default.

At completion update only the canonical files materially affected and record:
- what changed;
- what was tested;
- what passed/failed;
- unresolved risk;
- single next action.

Historical detail belongs in Git history, DECISIONS.md, ADRs and focused audit reports rather than being duplicated into every canonical file.

## Current gate

Canonical main before the repository-cleanup proposal:
1d7024f46d03709587913b3e4905d0b324ae7f40

Dental Golden Path: NOT PASS.

The repository-cleanup branch is diagnostic/optimization work and must not change ForgeLab execution semantics. It requires validation and explicit Product Owner approval before merge.

Current single next action:

HUMAN_REVIEW_AND_VALIDATE_REPOSITORY_CLEANUP

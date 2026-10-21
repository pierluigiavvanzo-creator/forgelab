# HANDOVER_CURRENT.md — ForgeLab

Date: 2026-10-21

## Current all-real-role diagnostic checkpoint — 2026-10-21

Task A / PR #75 is merged; synchronized baseline main `4dfb0ab596ba1d94b2fc27abc7e81b1ac6645b97`. Task B ran the protected fixture and unchanged objective through the real production orchestrator with real local planner/reviewer and cloud Aider, without response stubs.

Run 1 CLOSED after 167.187 s; Run 2 NOT RUN under the stop rule. Initial/final candidates passed generated tests (9/11, child exit 0) and independent acceptance 6/6 each. Two local reviews falsely denied implemented validation. Ollama logs prove reviewer prompts were truncated from 4,475/4,815 to 2,050 tokens. Final unchanged editor correction was rejected before write. Support was not called despite appearing in selected_roles; it remains unqualified.

Three primary cloud completions used 29,557 tokens (17,474 input / 12,083 output). EUR 0, no paid action or quota error observed. Original fixture/source and API/dashboard/Ollama processes unchanged. No Dental, approval or promotion. The unchanged failed-run gate writes SYSTEM/REPAIR, not PENDING; it was preserved, not rewritten.

Verdict: current non-editor route cannot be accepted unchanged for Dental. Reviewer needs full-context qualification or separately approved migration; a single planner success and no Support invocation do not qualify those roles. Intrinsic 7B capability with full context and Free allowance remain unknown. RAM headroom fell to 0.72 GB; no observed OOM/timeout.

Evidence: `docs/audits/FORGELAB_ALL_REAL_ROLES_SYNTHETIC_2026-10-21.md`. Documentation-only branch `codex/all-real-roles-synthetic-audit`; no production change or merge in Task B.

Single next action: authorize a bounded reviewer qualification with complete context before any Dental decision.

## Canonical repository

Repository:
pierluigiavvanzo-creator/forgelab

Canonical main before repository-cleanup proposal:
1d7024f46d03709587913b3e4905d0b324ae7f40

Historical cleanup branch (merged):
cleanup/repository-weight-redundancy-2026-10-09

Never reconstruct current state from old chat history when GitHub is available.

## Product status

ForgeLab: PRE-MVP.
Dental Quote Golden Path: NOT PASS.
Paid API/token target: EUR 0.
Product Owner role: approve and usability-test; do not use as routine debugger/log courier.

## Current runtime architecture

Dashboard
→ local authenticated API
→ acceptance contract
→ reusable editor/provider
→ isolated workspace
→ pre-write validation
→ ToolGateway
→ deterministic tests
→ bounded repair
→ independent Reviewer
→ Security
→ READY_FOR_DECISION
→ explicit human approval
→ exact reviewed promotion.

Target source stays protected until approval.

## Material merged corrections to preserve

PR #68:
parent candidate continuity and grounded reviewer evidence.

PR #69:
truthful SEMANTIC_REPAIR_NOOP accounting/evidence; a no-op is never automatic PASS.

PR #70:
documentation-only Aider empty-edit investigation; rendered empty diffs are not raw model completions and no production fix was introduced.

Do not reopen these without concrete regression evidence.

## Current blocker

The current local qwen2.5-coder:7b semantic-repair path has not met the required reliability gate for complex multi-obligation repair. Subsequent small-model exploration has not yet yielded a qualified replacement.

Do not start a fresh Dental target run until the semantic-repair execution path first passes the unchanged synthetic qualification gate.

## Historical repository cleanup proposal (merged)

The cleanup branch removes only high-confidence live-tree waste:
- generic dashboard starter documentation/assets no longer referenced;
- obsolete npm install path while pnpm is canonical;
- completed editor-bakeoff experiment runtime/CLI/test surface;
- old milestone acceptance reports already preserved in Git history;
- repeated historical material from canonical state/handover documents.

It does not intentionally alter:
- orchestrator runtime;
- API;
- editor adapter;
- model router;
- Reviewer/Security;
- promotion;
- ToolGateway;
- Dental source.

## Test/size audit baseline

Canonical main tracked tree:
- 125 blobs;
- 1,613,850 B (~1.54 MiB).

Static Python inventory:
- 21 Python test files;
- 180 Python tests.

Dashboard lifecycle:
- 4 Node tests.

Total named baseline:
184.

After removal of the superseded editor-bakeoff test file:
- 20 Python test files;
- expected 175 Python tests;
- 4 dashboard lifecycle tests;
- expected 179 named tests/checks.

The startup launcher runs a focused 108-test Python subset plus 4 lifecycle tests, not the full suite.

No new CI/PASS claim exists until local validation is executed.

## Resume protocol

1. Read AGENTS_MASTER.md.
2. Read AGENTS.md.
3. Read PROJECT_STATE.md and ROADMAP.md.
4. Read only the audit/ADR relevant to the active task.
5. Verify remote main and current branch/head.
6. For cloud qualification, read the current checkpoint and model-specific authorization before inference.
7. For product work, return to semantic-model qualification before Dental.

## Single next action

PO_USAGE_PAGE_REVIEW_AND_IMPLEMENTATION_PR_MERGE_DECISION

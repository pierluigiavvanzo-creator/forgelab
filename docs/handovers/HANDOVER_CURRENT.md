# HANDOVER_CURRENT.md — ForgeLab

Date: 2026-10-21

## Current qualification checkpoint — 2026-10-21

Verified precheck main: `b9ba77db5db89ffdf4e5fdda41de18cfaca9e23c`, identical to remote main, clean working tree. The repository-cleanup branch was merged in `8c1f442`; old cleanup counts below are historical evidence, not today's test results.

**Ollama Cloud qualification BLOCKED:** the one authorized `qwen3-coder:480b-cloud` smoke through local Ollama returned HTTP 410, reporting retirement on July 15, 2026. No qualification runs, fallback model or Dental run occurred. The 2/2 gate is NOT EVALUATED; the capability/hardware hypothesis remains untested. Production routing and source are unchanged.

The PO authorized a diagnostic-only ADR-002 exception, synthetic data only and EUR 0 Free plan. No paid activation/purchase occurred; actual account allowance/debits are not inspected. Ask the PO to read session/weekly usage if displayed, otherwise monthly included credits/reset date. Further inference needs a separately named model authorization.

Audit: `docs/audits/FORGELAB_OLLAMA_CLOUD_QWEN3_CODER_480B_QUALIFICATION_2026-10-21.md`. Dental Golden Path remains NOT PASS.

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

PO_DECISION_ON_SEPARATELY_AUTHORIZED_AVAILABLE_FREE_MODEL

# HANDOVER_CURRENT.md — ForgeLab

Date: 2026-10-21

## Current qualification checkpoint — 2026-10-21

**Synthetic cloud qualification PASS:** `gpt-oss:120b-cloud` 2/2 and `gemma4:31b-cloud` 2/2. Four sequential executions, no new smoke/retry: editor exits 0 in 12.640–18.202 seconds, generated-test child exits 0, independent acceptance 6/6 each. Both gpt-oss completions contained final content. Fixture/objective hashes unchanged; no manual output correction. Prior Qwen retirement remains historical, not the current qualification blocker.

This diagnostic extended the PO-authorized ADR-002 exception only to these two models, local signed-in Ollama, synthetic data and EUR 0 Free plan. No payment action or quota/credit error observed; actual account usage/debits are not inspected. PO should read the usage page (session/weekly or monthly included credits/reset). Production routing/configuration and services are unchanged. Dental Golden Path remains NOT PASS.

Base: PR #72 head `a4be803e7449aa600d05c024ea30e6a26190e9ac`; fetched main `b9ba77db5db89ffdf4e5fdda41de18cfaca9e23c` did not yet include it. Follow-up branch: `audit/ollama-cloud-two-models-2026-10-21`. Repository cleanup was already merged; older cleanup test counts below remain historical.

Audit: `docs/audits/FORGELAB_OLLAMA_CLOUD_TWO_MODEL_QUALIFICATION_2026-10-21.md`. Proposed separate routing PR/ADR update requires PO approval; no production/Dental readiness claim follows from this fixture alone.

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

PO_APPROVAL_OF_SEPARATE_SEMANTIC_ROUTING_PR_AND_ADR_UPDATE_AFTER_USAGE_REVIEW

# HANDOVER_CURRENT.md — ForgeLab

Date: 2026-10-22

## Current Task G checkpoint — 2026-10-22

Base main `b2f67cd` (PR #80), branch `codex/cloud-planner-visible-scope`. Planner joins the shared Gemma/gpt-oss cloud policy; all LLM roles in the Aider path are cloud-only. PO explicitly leaves the legacy custom editor/S1/S2 routes unchanged. Planner/reviewer prompts require user-visible GUI/CLI/web scope and make the original Objective prevail over a narrower contract. Actual planning model/attempts and early STOP evidence recorded; Aider chain, budgets and human gate unchanged.

Validation: **37 focused tests PASS; 218 full Python tests PASS (71.300 s)**. No real model calls or E2E run; EUR 0. Dental repository and promotion branch untouched, services not restarted. PO-reported Dental run `run-a29e11c3fa7b` missed usable workflow despite backend completion; Golden Path points 5/8 remain NOT met. Prompt effectiveness and current Dental behavior are NOT independently verified by this task.

Delivery: one code/docs PR; merge authorized only after full-suite and GitHub checks pass. Runtime test log: `.forgelab/runtime/task-g-planner-2026-10-22/python-suite.txt` (ignored). Rollback: revert Task G. Single next action: PO verifies the real Dental user workflow from the dashboard with updated runtime; no autonomous Dental execution.

## Previous cloud Support / test-oracle checkpoint — 2026-10-22

Task F base main `c4ff897` includes PR #79 merged. Branch `codex/cloud-support-test-oracle`: shared cloud REVIEWER/SUPPORT policy (Gemma primary, gpt-oss only on unavailability, reduced independence); quota stops and never local. Planner stays local; editor chain unchanged. Support receives current authorized files/contract, and all repair/correction prompts require recomputing generated-test expectations before modifying implementation.

**PASS:** 216 Python tests; exactly one real production run `cloud-support-1`, 120.063 s, READY_FOR_DECISION, generated tests 11/11 exit 0, independent 6/6, strict Gemma review PASS/no findings. One repair used from cap 2: incorrect CLI test expectation fixed; implementation unchanged during repair. Human gate PENDING, no promotion. Cloud 22,562 tokens, EUR 0 ledger. Fixture/source and service PIDs unchanged; no second run, Dental or service restart.

One code/docs PR; conditional merge criterion met. General reliability, exact old arithmetic-failure replay, live fallback/quota and account capacity are NOT VERIFIED. Already-running services have not been restarted to load new code. [Task F audit](../audits/FORGELAB_CLOUD_SUPPORT_TEST_ORACLE_2026-10-22.md). Local ignored evidence: `.forgelab/runtime/semantic-completion-audit/cloud-support-production-2026-10-22/`. Rollback: revert this change set, preserving runtime evidence.

Single next action: PO reads Ollama session/weekly usage before authorizing any further real workload. Dental remains separately undecided.

## Previous checkpoint — PR #77 reviewer qualification — 2026-10-22

Task C on main `0af1398` (PR #76 merged; production code unchanged from `4dfb0ab`) completed 8 local and 8 cloud reviewer-only synthetic replays. Both configurations FAIL. Local qwen2.5-coder:7b at diagnostic num_ctx=8192 receives complete prompts but falsely rejects GOOD final twice and misses both documented BAD defects. Gemma4:31b-cloud produces 8/8 responses rejected by the production schema validator and misses aggregate discount validation twice. No editor calls, production changes, Dental, approval or promotion.

Ollama 0.40.4's overflow/context-shift formula explains 2050: 4096-floor((4096-4)/2). It is not num_predict reservation or parallel slots. All 16 local log windows show no truncation; local request counts are corroborated by slot logs. Remote cloud internals remain unverified.

Local minimum free RAM 1.395 GiB, resident peak 2.36 GB, reported model VRAM 4.10 GB; no 1 GiB-floor breach. Cloud 49,507 tokens (41,986 input / 7,521 output), cost EUR 0; remaining account allowance unknown. No configuration qualifies REVIEWER for Dental; Planner/Support also remain outside this qualification.

Evidence: [reviewer audit](../audits/FORGELAB_REVIEWER_COMPLETE_CONTEXT_QUALIFICATION_2026-10-22.md). Proposed separately: reviewer-only num_ctx=8192, other options/routes unchanged, strict validation and context evidence. This addresses truncation only, not the failed semantic gate; no Gemma production routing is justified yet.

Single next action: PO reviews this audit and Ollama usage, then decides whether to authorize the separate reviewer-context implementation PR, with Dental remaining blocked.

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

CLEAN_OBJECTIVE_REVIEWER_REPLAY_ON_CONTRACT_FIX_BRANCH

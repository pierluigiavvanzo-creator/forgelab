# HANDOVER_CURRENT.md — ForgeLab

Date: 2026-10-22

## Current reviewer gate checkpoint — 2026-10-22 (after PR #77)

The PR #76/#77 reviewer failures are confounded: their objective was the semantic-repair objective, which embeds a stale "Blocking semantic review" of the original one-item code (AC1/AC2/AC6 missing, AC3/AC4/AC5 satisfied). The reviewer prompt shows it under `Objective:`. Local false blockers repeat AC1/AC2/AC6; Gemma's two misses repeat AC3/AC4 "satisfied". Causality is a hypothesis until a clean-objective replay.

Branch `claude/reviewer-context-output-contract-2026-10-22` fixes two production defects without changing routes, models, timeouts, budgets or gates: (1) the reviewer prompt now states the JSON contract and schema (Ollama Cloud did not enforce `format`; Gemma invented keys 8/8); (2) `OllamaProvider` sizes `num_ctx` from the prompt (floor 4096, ceiling 16384) and fails closed on oversized or truncated prompts. 200 tests pass. Live behaviour with the new prompt is NOT VERIFIED.

Evidence: [confound and fix](../audits/FORGELAB_REVIEWER_GATE_CONFOUND_AND_CONTRACT_FIX_2026-10-22.md). Dental remains blocked.

Single next action: clean-objective reviewer replay on this branch (local first, Gemma only if local fails).

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

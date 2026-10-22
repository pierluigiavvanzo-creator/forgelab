# PROJECT_STATE.md

Last updated: 2026-10-22

## Current cloud Support / test-oracle checkpoint — 2026-10-22

Task F base main `c4ff897` includes PR #79 merged. Branch `codex/cloud-support-test-oracle`: shared cloud REVIEWER/SUPPORT policy (Gemma primary, gpt-oss only on unavailability, reduced independence); quota stops and never local. Planner stays local; editor chain unchanged. Support receives current authorized files/contract, and all repair/correction prompts require recomputing generated-test expectations before modifying implementation.

**PASS:** 216 Python tests; exactly one real production run `cloud-support-1`, 120.063 s, READY_FOR_DECISION, generated tests 11/11 exit 0, independent 6/6, strict Gemma review PASS/no findings. One repair used from cap 2: incorrect CLI test expectation fixed; implementation unchanged during repair. Human gate PENDING, no promotion. Cloud 22,562 tokens, EUR 0 ledger. Fixture/source and service PIDs unchanged; no second run, Dental or service restart.

One code/docs PR; conditional merge criterion met. General reliability, exact old arithmetic-failure replay, live fallback/quota and account capacity are NOT VERIFIED. Already-running services have not been restarted to load new code. [Task F audit](docs/audits/FORGELAB_CLOUD_SUPPORT_TEST_ORACLE_2026-10-22.md). Local ignored evidence: `.forgelab/runtime/semantic-completion-audit/cloud-support-production-2026-10-22/`. Rollback: revert this change set, preserving runtime evidence.

Single next action: PO reads Ollama session/weekly usage before authorizing any further real workload. Dental remains separately undecided.

## Previous checkpoint — PR #77 reviewer qualification — 2026-10-22

Task C on main `0af1398` (PR #76 merged; production code unchanged from `4dfb0ab`) completed 8 local and 8 cloud reviewer-only synthetic replays. Both configurations FAIL. Local qwen2.5-coder:7b at diagnostic num_ctx=8192 receives complete prompts but falsely rejects GOOD final twice and misses both documented BAD defects. Gemma4:31b-cloud produces 8/8 responses rejected by the production schema validator and misses aggregate discount validation twice. No editor calls, production changes, Dental, approval or promotion.

Ollama 0.40.4's overflow/context-shift formula explains 2050: 4096-floor((4096-4)/2). It is not num_predict reservation or parallel slots. All 16 local log windows show no truncation; local request counts are corroborated by slot logs. Remote cloud internals remain unverified.

Local minimum free RAM 1.395 GiB, resident peak 2.36 GB, reported model VRAM 4.10 GB; no 1 GiB-floor breach. Cloud 49,507 tokens (41,986 input / 7,521 output), cost EUR 0; remaining account allowance unknown. No configuration qualifies REVIEWER for Dental; Planner/Support also remain outside this qualification.

Evidence: [reviewer audit](docs/audits/FORGELAB_REVIEWER_COMPLETE_CONTEXT_QUALIFICATION_2026-10-22.md). Proposed separately: reviewer-only num_ctx=8192, other options/routes unchanged, strict validation and context evidence. This addresses truncation only, not the failed semantic gate; no Gemma production routing is justified yet.

Single next action: PO reviews this audit and Ollama usage, then decides whether to authorize the separate reviewer-context implementation PR, with Dental remaining blocked.

## Current state

Project: ForgeLab
Repository: pierluigiavvanzo-creator/forgelab
Canonical branch: main
Canonical main before cleanup proposal: 1d7024f46d03709587913b3e4905d0b324ae7f40

Product state: PRE-MVP
Commercial evidence: C0 — hypothesis
Priority: A — restore a repeatable dashboard-first Golden Path
Dental Golden Path: NOT PASS

## Proven runtime foundation

ForgeLab currently has:
- dashboard + authenticated local API;
- isolated candidate workspaces;
- bounded authorized-file writes;
- Aider 0.86.2 reusable editor boundary;
- local Ollama routing;
- deterministic tests;
- bounded repair;
- independent semantic review;
- security gate;
- protected target source until explicit approval;
- exact reviewed promotion path;
- durable run/status/evidence artifacts;
- Windows launcher with readiness/stability checks.

These technical capabilities do not constitute product PASS.

## Current semantic-repair status

PR #68 is merged:
- native repair preserves the parent candidate and validates lineage/baseline/scope.

PR #69 is merged:
- a zero-change semantic Aider repair is recorded truthfully as SEMANTIC_REPAIR_NOOP;
- it is not misreported as PREWRITE_RECOVERY_EXHAUSTED;
- no-op never becomes automatic acceptance.

PR #70 is merged:
- documentation-only investigation of Aider empty-edit behavior;
- no runtime fix was introduced;
- rendered empty diffs do not prove an empty raw model response.

Subsequent bounded model experiments showed that the current qwen2.5-coder:7b semantic-repair path is not sufficiently reliable for the required multi-obligation repair class. Small-model experiments likewise have not yet produced a qualified replacement.

Do not launch another Dental Golden Path run until a semantic-repair model/path first passes the synthetic qualification gate.

## Repository cleanup checkpoint

Branch:
cleanup/repository-weight-redundancy-2026-10-09

Purpose:
- remove obsolete starter/experiment artifacts;
- remove completed milestone acceptance reports from the live tree while preserving them in Git history;
- remove dead editor-bakeoff runtime/CLI surface;
- compact canonical state files that had accumulated repeated historical checkpoints;
- keep production behavior, security gates and current runtime architecture unchanged.

Historical cleanup proposal; merged in 8c1f442. No new test PASS is claimed here.

## Test inventory at cleanup baseline

Static test inventory on canonical main:
- 21 Python test files;
- 180 Python test_* methods/functions;
- 4 Node dashboard lifecycle tests;
- 184 named test/check cases total.

Important:
- Start-ForgeLab.ps1 intentionally runs a focused 108-test Python stabilization subset plus 4 dashboard lifecycle tests.
- 108 is not the full Python suite.
- No new remote CI PASS is claimed.

After removing the superseded editor-bakeoff experiment test file:
- expected Python tests: 175;
- expected Python test files: 20;
- dashboard lifecycle tests: 4;
- expected named total: 179.

A local full-suite run is required before merge.

## Repository size at cleanup baseline

Tracked Git-tree blobs:
- 125 files/blobs;
- 1,613,850 bytes total (~1.54 MiB).

Largest tracked areas:
- dashboard: 522,972 B;
- src: 373,726 B;
- tests: 349,230 B;
- docs: 174,525 B.

The dominant single tracked file is dashboard/pnpm-lock.yaml (342,352 B), which is required for deterministic dependency resolution and is not cleanup waste.

Ignored local runtime/tool/model directories can be much larger than the tracked repository and are not represented by GitHub tree size.

## Non-negotiable protections

Do not:
- manually repair Dental during a target run;
- weaken Reviewer/Security;
- auto-promote;
- add paid API/token spend without explicit approval;
- delete runtime evidence needed for an active/nonterminal run;
- delete the pinned Aider toolchain merely to make local disk usage look smaller;
- describe cleanup as Golden Path progress.

## Single next action

CLEAN_OBJECTIVE_REVIEWER_REPLAY_ON_CONTRACT_FIX_BRANCH

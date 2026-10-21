# PROJECT_STATE.md

Last updated: 2026-10-21

## Current all-real-role diagnostic checkpoint — 2026-10-21

Task A / PR #75 is merged; synchronized baseline main `4dfb0ab596ba1d94b2fc27abc7e81b1ac6645b97`. Task B ran the protected fixture and unchanged objective through the real production orchestrator with real local planner/reviewer and cloud Aider, without response stubs.

Run 1 CLOSED after 167.187 s; Run 2 NOT RUN under the stop rule. Initial/final candidates passed generated tests (9/11, child exit 0) and independent acceptance 6/6 each. Two local reviews falsely denied implemented validation. Ollama logs prove reviewer prompts were truncated from 4,475/4,815 to 2,050 tokens. Final unchanged editor correction was rejected before write. Support was not called despite appearing in selected_roles; it remains unqualified.

Three primary cloud completions used 29,557 tokens (17,474 input / 12,083 output). EUR 0, no paid action or quota error observed. Original fixture/source and API/dashboard/Ollama processes unchanged. No Dental, approval or promotion. The unchanged failed-run gate writes SYSTEM/REPAIR, not PENDING; it was preserved, not rewritten.

Verdict: current non-editor route cannot be accepted unchanged for Dental. Reviewer needs full-context qualification or separately approved migration; a single planner success and no Support invocation do not qualify those roles. Intrinsic 7B capability with full context and Free allowance remain unknown. RAM headroom fell to 0.72 GB; no observed OOM/timeout.

Evidence: `docs/audits/FORGELAB_ALL_REAL_ROLES_SYNTHETIC_2026-10-21.md`. Documentation-only branch `codex/all-real-roles-synthetic-audit`; no production change or merge in Task B.

Single next action: authorize a bounded reviewer qualification with complete context before any Dental decision.

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

PO_USAGE_PAGE_REVIEW_AND_IMPLEMENTATION_PR_MERGE_DECISION

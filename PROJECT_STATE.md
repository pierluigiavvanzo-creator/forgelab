# PROJECT_STATE.md

Last updated: 2026-10-21

## Current cloud STOP correction checkpoint — 2026-10-21

PR #74 is merged at synchronized baseline `8f2c47d7e517cc92eee816960b61cb8cb6dcd40a`. Proposed fix on `codex/fix-cloud-editor-error-classification`: route only on separately captured provider exceptions, never generated code or stdout/stderr. Exit-0 provider errors still stop/switch correctly. Original exception-chain HTTP codes survive litellm mapping. Launcher text now names the approved cloud chain. Model order, flags, version, timeouts, budgets, non-editor roles and human gate are unchanged.

Validation: 192 Python tests PASS in 68.697 s; offline installed Aider/litellm boundary verified with network forbidden. Exactly one authorized retired-model diagnostic: exit 0, 73.655 s, no changed files/completion; nine Aider-internal attempts, no external retry. Protected fixture hashes match. EUR 0; no paid action, Dental, promotion, service restart or merge.

Not verified: real 402/429, remaining Free quota, post-fix successful live cloud edit, Dental and live non-editor roles. Existing internal retries and pinned-version observer compatibility remain risks. Runtime evidence stays ignored. This is proposed branch state, not a deployment claim.

Evidence: `docs/audits/FORGELAB_EDITOR_CLOUD_STOP_FIX_2026-10-21.md`.

Single next action: PO reviews the PR and Ollama usage, then decides whether to merge.

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

# PROJECT_STATE.md

Last updated: 2026-10-21

## Current qualification checkpoint — 2026-10-21

Verified precheck main: `b9ba77db5db89ffdf4e5fdda41de18cfaca9e23c`, identical to remote main, clean working tree. The repository-cleanup branch was merged in `8c1f442`; old cleanup counts below are historical evidence, not today's test results.

**Ollama Cloud qualification BLOCKED:** the one authorized `qwen3-coder:480b-cloud` smoke through local Ollama returned HTTP 410, reporting retirement on July 15, 2026. No qualification runs, fallback model or Dental run occurred. The 2/2 gate is NOT EVALUATED; the capability/hardware hypothesis remains untested. Production routing and source are unchanged.

The PO authorized a diagnostic-only ADR-002 exception, synthetic data only and EUR 0 Free plan. No paid activation/purchase occurred; actual account allowance/debits are not inspected. Ask the PO to read session/weekly usage if displayed, otherwise monthly included credits/reset date. Further inference needs a separately named model authorization.

Audit: `docs/audits/FORGELAB_OLLAMA_CLOUD_QWEN3_CODER_480B_QUALIFICATION_2026-10-21.md`. Dental Golden Path remains NOT PASS.

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

PO_DECISION_ON_SEPARATELY_AUTHORIZED_AVAILABLE_FREE_MODEL

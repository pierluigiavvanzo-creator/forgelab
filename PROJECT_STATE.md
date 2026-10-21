# PROJECT_STATE.md

Last updated: 2026-10-21

## Current qualification checkpoint — 2026-10-21

**Synthetic cloud qualification PASS:** `gpt-oss:120b-cloud` 2/2 and `gemma4:31b-cloud` 2/2. Four sequential executions, no new smoke/retry: editor exits 0 in 12.640–18.202 seconds, generated-test child exits 0, independent acceptance 6/6 each. Both gpt-oss completions contained final content. Fixture/objective hashes unchanged; no manual output correction. Prior Qwen retirement remains historical, not the current qualification blocker.

This diagnostic extended the PO-authorized ADR-002 exception only to these two models, local signed-in Ollama, synthetic data and EUR 0 Free plan. No payment action or quota/credit error observed; actual account usage/debits are not inspected. PO should read the usage page (session/weekly or monthly included credits/reset). Production routing/configuration and services are unchanged. Dental Golden Path remains NOT PASS.

Base: PR #72 head `a4be803e7449aa600d05c024ea30e6a26190e9ac`; fetched main `b9ba77db5db89ffdf4e5fdda41de18cfaca9e23c` did not yet include it. Follow-up branch: `audit/ollama-cloud-two-models-2026-10-21`. Repository cleanup was already merged; older cleanup test counts below remain historical.

Audit: `docs/audits/FORGELAB_OLLAMA_CLOUD_TWO_MODEL_QUALIFICATION_2026-10-21.md`. Proposed separate routing PR/ADR update requires PO approval; no production/Dental readiness claim follows from this fixture alone.

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

PO_APPROVAL_OF_SEPARATE_SEMANTIC_ROUTING_PR_AND_ADR_UPDATE_AFTER_USAGE_REVIEW

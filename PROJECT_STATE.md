# PROJECT_STATE.md

**Last updated:** 2026-09-30
**Current phase:** PRE-MVP / Software Factory Golden Path validation
**Current priority:** A — Product Critical

## Canonical source

Repository: `pierluigiavvanzo-creator/forgelab`

Canonical shared truth: `main`

Verified pre-stabilization `main` checkpoint: `20c3c2565c6ce066520b8ce831b13640858cde2b` (merged PR #17).

## Stabilization publication candidate

Branch: `mvp1-stabilization-cleanup`

Reviewed local code change:

- 68 high-confidence dead/premature files removed;
- 4 existing files modified;
- 72 tracked files total;
- 19 insertions / 7,633 deletions;
- API integration 12/12 PASS;
- full Python suite 106/106 PASS;
- dashboard production build PASS, Product Owner-confirmed;
- no generated/untracked backup artifacts included.

The stabilization removes non-authoritative/dead starter surface and the untracked Sites Vite plugin dependency, aligns stale semantic-review test fixtures, and does not intentionally change the core orchestrator, ToolGateway, repair budget, semantic review runtime, promotion logic, runner, smoke behavior or telemetry.

## Product direction

ForgeLab remains the primary product.

Target workflow:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED REPAIR -> REVIEW -> WORKING PREVIEW -> HUMAN APPROVAL -> PROMOTION`

Provider remains replaceable; current zero-cost local path is Ollama.

## Golden Path sequence

1. Dental Quote — calculator/business logic.
2. Small CRUD SaaS — records/users/workflow.
3. Automation/reporting tool — ingest -> transform -> report.

Dental Quote target: `C:\\Users\\NITRO\\source\\FORGELAB_MVP1_DENTAL_QUOTE`

Objective: add support for three treatments, automatic subtotals, percentage discount and final total; validate inputs; modify only necessary files; add tests; do not change dependencies/configuration unless necessary and justified.

## MVP gates

- G1 Usability: materially demonstrated.
- G2 Autonomy: pending fresh Golden Path validation after stabilization.
- G3 Real output: not yet PASS for the complete three-treatment objective.
- G4 Quality: deterministic tests and blocking semantic review exist; fresh end-to-end validation pending.
- G5 Human control: PASS so far; no candidate promoted without explicit approval.

## Single next action

Review the stabilization PR and CI. Do not merge without explicit Product Owner approval. After approved merge, immediately run Dental Quote Golden Path end-to-end and fix only blockers that prevent that product journey.

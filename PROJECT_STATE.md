# PROJECT_STATE.md

**Last updated:** 2026-09-29
**Current phase:** PRE-MVP / real application validation
**Current priority:** A — Product Critical

## Canonical source

Repository:

`pierluigiavvanzo-creator/forgelab`

Canonical shared truth:

`main`

Main checkpoint before the current semantic-review proposal:

`ba8e0fee79676e3b65fc82d980d24989c1d22c90`

Local root used for MVP validation:

`C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`

## Current product state

ForgeLab has now demonstrated most of the real external-application workflow on the Dental Quote Calculator:

`Dashboard -> objective -> bounded multi-file AI Developer -> isolated ToolGateway writes -> deterministic tests -> review/security -> evidence viewer -> Product Owner gate -> Product Owner repair child run`

The project is still **PRE-MVP** because the real candidate has not yet satisfied the original Product Owner objective and has not been approved/promoted.

## Real MVP-1 target

Target repository:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

Original objective:

> Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.

Original decision-ready run observed:

`run-2e19fed4860c`

The candidate reached `READY_FOR_DECISION`, with tests PASS and zero provider cost, but Product Owner inspection correctly found that the implementation still supported only one treatment.

No promotion was approved.

## MVP-1 blockers discovered and corrected on main

The real run exposed product blockers that were fixed narrowly, one at a time:

- PR #5 — dashboard now surfaces run-form blockers instead of silently disabling `Avvia run`;
- PR #6 — bounded Ollama output budget raised from 256 to 2048 for structured multi-file patches;
- PR #7 — one bounded structured-output repair attempt;
- PR #8 — AI Developer JSON Schema enforced through Ollama structured outputs;
- PR #9 — sidebar navigation + read-only evidence viewer + allowlisted `Changes.patch`;
- PR #10 — `Richiedi fix` now creates a bounded child run with Product Owner feedback instead of only recording a label;
- PR #11 — one bounded pre-write correction when AI Developer `old_text` does not exactly match current authorized source.

Main after PR #11:

`ba8e0fee79676e3b65fc82d980d24989c1d22c90`

## Current confirmed blocker

**Semantic review is not authoritative.**

The latest repair candidate again produced the same incomplete behavior: one treatment + discount rather than the requested three-treatment quote.

Code inspection identified the reason:

- `AIReview.json` is generated from the full objective and patch;
- however its content is advisory only;
- authoritative `ReviewReport.json` is produced by `review_patch()`;
- current deterministic `review_patch()` checks only non-empty diff and authorized paths;
- therefore semantic incompleteness can still reach `READY_FOR_DECISION`.

This is a G3/G4 Product Critical blocker.

## Current proposal under validation

Branch:

`mvp1-semantic-review-gate`

Intent:

- make AI semantic review structured and blocking;
- require explicit requirement-by-requirement objective coverage;
- treat missing/unverified required behavior as review FAIL;
- combine deterministic scope review and semantic review into the authoritative `ReviewReport.json`;
- when deterministic scope passes but semantic review fails, use the remaining bounded repair budget automatically;
- perform repair -> deterministic retest -> semantic re-review;
- reach `READY_FOR_DECISION` only when both deterministic and semantic review pass;
- preserve explicit Product Owner promotion gate.

The proposal does not change authorized paths, ToolGateway, provider cost, push/merge policy, or promotion semantics.

## MVP gates current status

- **G1 Usability:** materially demonstrated; dashboard can initiate real runs.
- **G2 Autonomy:** improved but not yet accepted as final PASS while semantic repair behavior is being completed.
- **G3 Real output:** FAIL / not yet proven for the full three-treatment objective.
- **G4 Quality:** FAIL / current main can allow semantically incomplete work through deterministic scope review.
- **G5 Human control:** PASS so far; no candidate has been promoted without explicit Product Owner approval.

## Infrastructure freeze

Still active.

Do not add deployment, multi-tenant, billing, advanced observability, scaling, unrelated hardening, or provider expansion unless a real MVP gate proves it necessary.

## Single next action

Validate and, only after explicit Product Owner approval, merge the bounded semantic-review gate proposal.

Then rerun the same Dental Quote Product Owner repair scenario and inspect the resulting `Changes.patch` before any promotion.

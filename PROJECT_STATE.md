# PROJECT_STATE.md

**Last updated:** 2026-09-29
**Current phase:** PRE-MVP / real application validation
**Current priority:** A — Product Critical

## Canonical source

Repository:

`pierluigiavvanzo-creator/forgelab`

Canonical shared truth:

`main`

Current canonical main checkpoint:

`82ffb781f0791e133f2faa6a1c6bd14f5226a742`

This includes merged PR #13: bounded wider timeout only on transient Ollama retry.

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
- PR #11 — one bounded pre-write correction when AI Developer `old_text` does not exactly match current authorized source;
- PR #12 — semantic review is now structured, blocking, authoritative in `ReviewReport.json`, and can consume the remaining bounded repair budget before `READY_FOR_DECISION`;
- PR #13 — transient Ollama retry keeps the first timeout unchanged and widens only the single retry (default 60 -> 180 seconds, cap 600).

Main after PR #13:

`82ffb781f0791e133f2faa6a1c6bd14f5226a742`

## Current confirmed blocker

**Authorized paths are incorrectly treated as mandatory edits.**

The next real Dental Quote repair attempt passed the timeout blocker but failed with:

`repair run execution failed: AIDeveloperFormatError: AI Developer multi-file patch missing fields: changes, schema_version`

Canonical code inspection found:

- the run authorizes two paths: `quote_calculator.py` and `test_quote_calculator.py`;
- initial multi-file JSON Schema currently sets `minItems == len(authorized_paths)`;
- the Developer prompt says to return exactly one change for every authorized path;
- the deterministic validator defaults to `require_all_paths=True`;
- therefore an otherwise complete single-file change inside an authorized two-file scope is rejected as malformed instead of being treated as a valid subset proposal.

This confuses permission scope with mandatory edits.

## Current proposal under validation

Branch:

`mvp1-authorized-scope-subset-normalization`

Intent:

- keep 1–3 authorized paths as the immutable maximum write scope;
- allow the Developer to modify any non-empty subset actually required by the objective;
- set the multi-file structured-output schema to `minItems=1`, `maxItems=len(authorized_paths)`;
- deterministically normalize a complete flat single-change object into the existing `schema_version: 2.0 / changes:[...]` contract when it stays inside scope;
- invent no missing change and perform no fuzzy patching;
- keep exact `old_text`, path-expansion, no-op and size checks authoritative;
- record actual changed artifacts separately from the larger authorized scope;
- rely on the blocking semantic review from PR #12 to reject a subset that fails to implement required tests or behavior.

## MVP gates current status

- **G1 Usability:** materially demonstrated; dashboard can initiate real runs.
- **G2 Autonomy:** not yet PASS; the current multi-file contract still rejects valid in-scope subset proposals before the semantic repair path can operate.
- **G3 Real output:** FAIL / not yet proven for the full three-treatment objective.
- **G4 Quality:** semantic review is authoritative on main after PR #12; real-run validation is still pending because the current Developer contract failed before review.
- **G5 Human control:** PASS so far; no candidate has been promoted without explicit Product Owner approval.

## Infrastructure freeze

Still active.

Do not add deployment, multi-tenant, billing, advanced observability, scaling, unrelated hardening, or provider expansion unless a real MVP gate proves it necessary.

## Single next action

Validate and, only after explicit Product Owner approval, merge the authorized-scope subset/normalization proposal.

Then rerun the same Dental Quote Product Owner repair scenario once. Inspect `ReviewReport.json` and `Changes.patch` before any promotion.

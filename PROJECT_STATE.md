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

`45fa433ef408f600ab6890ac43e170b327f1eec3`

This includes merged PR #14: authorized paths are maximum write scope, not mandatory edits.

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
- PR #13 — transient Ollama retry keeps the first timeout unchanged and widens only the single retry (default 60 -> 180 seconds, cap 600);
- PR #14 — authorized paths are now maximum write scope; a valid non-empty subset is allowed and a complete flat single-change response can be normalized deterministically.

Main after PR #14:

`45fa433ef408f600ab6890ac43e170b327f1eec3`

## Current confirmed blocker

**Multiple independent edits to the same authorized file are rejected as duplicate paths.**

The next real Dental Quote repair attempt passed the PR #14 contract blocker but failed with:

`repair run execution failed: ValueError: AI Developer multi-file patch contains duplicate paths`

Canonical code inspection confirmed that the validator still assumes at most one structured change per file. That is too strict for a real file that may need separate edits to calculation logic and UI while remaining inside the same authorized path.

## Current proposal under validation

Branch:

`mvp1-disjoint-same-file-change-composition`

Intent:

- preserve the immutable 1–3 authorized path scope;
- permit at most 4 structured operations per authorized path in subset mode;
- require every `old_text` to occur exactly once in the same current source snapshot;
- permit multiple operations on one file only when their original-source spans are disjoint;
- reject overlapping/conflicting same-file operations before any write;
- compose disjoint operations deterministically into one final replacement per file;
- keep ToolGateway to one authoritative write per changed file;
- keep no fuzzy patching, path expansion rejection, no-op/size checks, tests, semantic review and Product Owner promotion gate unchanged.

## MVP gates current status

- **G1 Usability:** materially demonstrated; dashboard can initiate real runs.
- **G2 Autonomy:** not yet PASS; the current validator still rejects valid disjoint same-file operations before tests and semantic review can complete.
- **G3 Real output:** FAIL / not yet proven for the full three-treatment objective.
- **G4 Quality:** semantic review is authoritative on main after PR #12; real-run validation is still pending because the current Developer contract failed before review.
- **G5 Human control:** PASS so far; no candidate has been promoted without explicit Product Owner approval.

## Infrastructure freeze

Still active.

Do not add deployment, multi-tenant, billing, advanced observability, scaling, unrelated hardening, or provider expansion unless a real MVP gate proves it necessary.

## Single next action

Validate and, only after explicit Product Owner approval, merge the disjoint same-file change composition proposal.

Then rerun the same Dental Quote Product Owner repair scenario once. Inspect `ReviewReport.json` and `Changes.patch` before any promotion.

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

`9b50ea11ca0d679adaa643d7dbc4b7c308866c01`

This includes merged PR #15: bounded disjoint same-file AI changes are composed deterministically before ToolGateway write.

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
- PR #14 — authorized paths are now maximum write scope; a valid non-empty subset is allowed and a complete flat single-change response can be normalized deterministically;
- PR #15 — up to four disjoint operations per authorized path can be composed deterministically into one ToolGateway write per file; overlapping operations remain blocked.

Main after PR #15:

`9b50ea11ca0d679adaa643d7dbc4b7c308866c01`

## Current confirmed blocker

**A syntactically invalid Python repair can consume the only repair budget.**

Real child run:

`run-be067c4915d2`

Observed sequence:

- initial candidate changed both authorized Dental Quote files;
- deterministic tests failed because the generated function still accepted two positional arguments while the new test called it with six;
- Support/Developer used the one allowed repair attempt;
- the repair candidate introduced invalid Python, including malformed indentation;
- the second deterministic test stopped at import with `IndentationError: unexpected indent`;
- run ended `DIAGNOSING`, tests FAIL, repair attempts 1;
- no `Changes.patch` was produced because the candidate never reached the review phase.

## Current proposal under validation

Branch:

`mvp1-python-syntax-prewrite-repair`

Intent:

- validate the final in-memory candidate for every modified `.py` file with Python AST parsing before ToolGateway write;
- treat Python syntax failure as recoverable pre-write validation, not as a consumed functional repair;
- initial generation and semantic-repair paths also receive the same syntax guard;
- for test-failure repair, allow exactly one bounded pre-write correction when format, exact-source reference, or Python syntax validation fails;
- only a syntactically valid repair candidate is written and increments the real repair counter;
- keep max repair attempts, authorized paths, no fuzzy patching, deterministic tests, semantic review and Product Owner gate unchanged.

## MVP gates current status

- **G1 Usability:** materially demonstrated; dashboard can initiate real runs.
- **G2 Autonomy:** not yet PASS; a malformed Python repair can currently exhaust the single repair budget and return debugging work to the Product Owner.
- **G3 Real output:** FAIL / not yet proven for the full three-treatment objective.
- **G4 Quality:** semantic review is authoritative on main after PR #12; real-run validation is still pending because the repair candidate failed Python syntax before review.
- **G5 Human control:** PASS so far; no candidate has been promoted without explicit Product Owner approval.

## Infrastructure freeze

Still active.

Do not add deployment, multi-tenant, billing, advanced observability, scaling, unrelated hardening, or provider expansion unless a real MVP gate proves it necessary.

## Single next action

Validate and, only after explicit Product Owner approval, merge the Python syntax pre-write repair proposal.

Then rerun the same Dental Quote Product Owner repair scenario once. Inspect `TestEvidence.json`, `ReviewReport.json` and `Changes.patch` before any promotion.

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

`fdaf5a6e2b637ee44452f3d8e56ea4b78386d2bb`

This includes merged PR #16: modified Python candidates are syntax-validated before ToolGateway write, with one bounded pre-write correction for malformed repair output.

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

Main after PR #16:

`fdaf5a6e2b637ee44452f3d8e56ea4b78386d2bb`

## Current confirmed blocker

**The single pre-write correction can still fail when Ollama repeats a stale `old_text` reference.**

After PR #16, a new Product Owner repair request from active run `run-be067c4915d2` failed before returning a completed child run with:

`AIDeveloperReferenceError: AI Developer old_text must occur exactly once in quote_calculator.py; found 0`

Canonical inspection confirms that the first stale-reference error is caught, but the one correction still uses the same fragment-based `old_text/new_text` contract. If Ollama again returns stale text, the second validation is terminal and the API surfaces the exception.

## Current proposal under validation

Branch:

`mvp1-reference-error-full-file-fallback`

Intent:

- preserve exactly one pre-write correction;
- when the validation failure is specifically `AIDeveloperReferenceError`, change the correction contract instead of retrying the same anchor contract;
- request complete replacement content only for the authorized files that actually need modification;
- use a dedicated structured schema `2.1` with `path + new_text + summary`, no model-provided `old_text`;
- deterministically normalize the response back to the internal schema 2.0 by using the current complete file as authoritative `old_text`;
- validate Python syntax before write;
- preserve immutable scope, no fuzzy matching, one ToolGateway write per file, repair budget, deterministic tests, semantic review and Product Owner gate.

## MVP gates current status

- **G1 Usability:** materially demonstrated; dashboard can initiate real runs.
- **G2 Autonomy:** not yet PASS; repeated stale source anchors can still escape the single pre-write correction and return retry/debugging work to the Product Owner.
- **G3 Real output:** FAIL / not yet proven for the full three-treatment objective.
- **G4 Quality:** syntax validation is now pre-write after PR #16, but real-run validation is still pending because stale-reference recovery can terminate before tests/review.
- **G5 Human control:** PASS so far; no candidate has been promoted without explicit Product Owner approval.

## Infrastructure freeze

Still active.

Do not add deployment, multi-tenant, billing, advanced observability, scaling, unrelated hardening, or provider expansion unless a real MVP gate proves it necessary.

## Single next action

Validate and, only after explicit Product Owner approval, merge the stale-reference full-file recovery proposal.

Then rerun the same Dental Quote Product Owner repair scenario once. Inspect `TestEvidence.json`, `ReviewReport.json` and `Changes.patch` before any promotion.

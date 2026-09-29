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

`0d557c57ed991c1ab8cf90cd96dd47952fa564ce`

This includes merged PR #12: blocking semantic review with bounded repair.

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
- PR #12 — semantic review is now structured, blocking, authoritative in `ReviewReport.json`, and can consume the remaining bounded repair budget before `READY_FOR_DECISION`.

Main after PR #12:

`0d557c57ed991c1ab8cf90cd96dd47952fa564ce`

## Current confirmed blocker

**Local Ollama retry timeout is too narrow for the richer semantic-review path.**

The first Dental Quote repair attempt after PR #12 failed with:

`repair run execution failed: ProviderTransientError: Ollama unavailable: timed out`

Canonical code inspection confirmed:

- parent run timeout defaults to 60 seconds;
- Product Owner child repair inherits that timeout unchanged;
- S1 and S2 local Ollama routes each allow one retry;
- both first attempt and retry currently use the same 60-second timeout;
- therefore one transiently slow local generation gets at most two identical 60-second windows.

This is a G2 Product Critical reliability blocker, not a patch-quality or scope failure.

## Current proposal under validation

Branch:

`mvp1-ollama-transient-timeout-retry`

Intent:

- preserve the first Ollama attempt at the existing requested timeout;
- only after a transient Ollama failure, widen the retry timeout to 3x the original value, capped at 600 seconds;
- keep the existing retry count unchanged;
- leave non-Ollama providers unchanged;
- do not change deterministic test timeouts;
- do not change model, provider, cost, ToolGateway, semantic gate or Product Owner promotion rules.

For the current default 60-second run, the bounded local sequence becomes:

`60s first attempt -> transient timeout -> one 180s Ollama retry`

## MVP gates current status

- **G1 Usability:** materially demonstrated; dashboard can initiate real runs.
- **G2 Autonomy:** not yet PASS; local semantic-repair flow currently fails on a repeated 60-second Ollama timeout window.
- **G3 Real output:** FAIL / not yet proven for the full three-treatment objective.
- **G4 Quality:** semantic review blocker was corrected by PR #12; real-run validation is still pending because the Ollama timeout prevented completion.
- **G5 Human control:** PASS so far; no candidate has been promoted without explicit Product Owner approval.

## Infrastructure freeze

Still active.

Do not add deployment, multi-tenant, billing, advanced observability, scaling, unrelated hardening, or provider expansion unless a real MVP gate proves it necessary.

## Single next action

Validate and, only after explicit Product Owner approval, merge the bounded Ollama retry-timeout proposal.

Then rerun the same Dental Quote Product Owner repair scenario. Inspect `ReviewReport.json` and `Changes.patch` before any promotion.

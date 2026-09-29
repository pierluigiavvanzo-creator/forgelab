# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-09-29  
**Checkpoint:** MVP-1 real Dental Quote validation / semantic-review blocker  
**Status:** PRE-MVP; no Dental Quote candidate approved or promoted

## 1. Mission and operating contract

ForgeLab is a governed multi-agent software-development control plane.

Target workflow:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> AGENT SELECTION -> ISOLATED IMPLEMENTATION -> DETERMINISTIC TEST -> BOUNDED REPAIR -> REVIEW -> SECURITY -> READY_FOR_DECISION -> APPROVE | REJECT | REPAIR -> EXACT REVIEWED PROMOTION -> VERIFIED OUTPUT`

Guiding metric:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / USER TIME`

Product Owner contract:

- Product Owner is approver and final usability tester;
- Product Owner is not routine QA, debugger, log transporter or retry orchestrator;
- failures in that contract are product defects.

Operating preference:

- normal ChatGPT chat + Windows PowerShell;
- no Work or Codex;
- GitHub repository is source of truth;
- local Ollama zero-spend path preferred;
- bounded autonomy;
- infrastructure freeze until MVP evidence requires a change.

## 2. Canonical repository and local environment

GitHub:

`pierluigiavvanzo-creator/forgelab`

Canonical branch:

`main`

Current main checkpoint after PR #12:

`0d557c57ed991c1ab8cf90cd96dd47952fa564ce`

Local ForgeLab root:

`C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`

Launcher:

`Start-ForgeLab.ps1`

Dashboard:

`http://127.0.0.1:5173`

API:

`http://127.0.0.1:8765`

Local AI:

- Ollama 0.34.2;
- `qwen2.5-coder:7b`;
- provider alias `ollama`;
- provider cost EUR 0.

## 3. Historical foundation — do not repeat absent regression evidence

- M8.5 — Human-approved local promotion — PASS
- M8.5.1 — UTF-8/BOM Git patch handling — PASS
- M8.6 — Bounded multi-file AI Developer — PASS
- M8.7 — Bounded AI Developer repair — PASS
- M8.7.1 — Windows-safe exact patch persistence — PASS
- M8.8 — Bounded repository context/project-memory injection — PASS
- M8.9 — Canonical Git source/self-hosting readiness — TECHNICAL PASS

Historical M8.9 baseline:

- commit `58d22eeca66c27871738c04c6d850c59efabf115`;
- tree `63b6c91427edb19cd038cf557904451dfc08a947`;
- 168 tracked canonical files;
- canonical manifest SHA-256 `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3`;
- 88 regression tests PASS at acceptance.

## 4. MVP-1 target

Target repository:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

Original objective:

> Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.

Authorized files:

- `quote_calculator.py`
- `test_quote_calculator.py`

Test command:

`["py","-3.11","-m","unittest","discover","-v"]`

Mode:

- AI Developer;
- risk Normal;
- max repair attempts 1;
- local Ollama / EUR 0.

Original decision-ready run observed:

`run-2e19fed4860c`

## 5. What the real MVP run proved

The first real run eventually reached `READY_FOR_DECISION`.

Observed UI evidence:

- Plan complete;
- Execute complete;
- Verify complete;
- Test PASS;
- Review displayed complete;
- two authorized files changed;
- provider Ollama / qwen2.5-coder:7b;
- provider cost EUR 0;
- source repository reported protected/unchanged during isolated execution;
- explicit Product Owner gate remained pending;
- evidence bundle became directly inspectable.

No approval/promotion was performed.

## 6. Why the first candidate was rejected by the Product Owner

`Changes.patch` showed only:

- one treatment;
- one price;
- percentage discount;
- subtotal;
- final total;
- discount tests.

It did **not** implement:

- exactly three treatments in one quote;
- individual treatment names/prices for all three;
- per-treatment subtotals;
- combined subtotal across all three;
- discount on the combined subtotal;
- tests proving the complete three-treatment behavior.

Therefore green tests were insufficient and the Product Owner correctly refused promotion.

## 7. Product blockers found through the real run

### PR #5 — merged

Run-form errors were hidden behind a silently disabled `Avvia run`.

Fix: clickable validation + inline errors.

### PR #6 — merged

AI Developer output was truncated/non-JSON at `num_predict=256`.

Fix: bounded output budget `2048`.

### PR #7 — merged

A structurally malformed AI Developer JSON response immediately killed the run.

Fix: one bounded structured-output retry.

### PR #8 — merged

Prompt-only schema instructions remained unreliable.

Fix: Ollama native structured outputs using JSON Schema.

### PR #9 — merged

Sidebar `Evidenze` did not activate the central tab and the Product Owner could not inspect the exact reviewed patch/reports.

Fix:

- controlled tab state;
- read-only evidence viewer;
- authenticated allowlisted exposure of `Changes.patch`.

### PR #10 — merged

`Richiedi fix` only recorded `REPAIR`; it performed no corrective work and gave weak feedback.

Fix:

- Product Owner feedback dialog;
- bounded authenticated repair endpoint;
- automatic child run;
- same repository, authorized paths, tests, timeout and repair budget;
- `HumanRepairRequest.json` parent/child audit evidence;
- parent candidate never promoted.

Main after PR #10:

`20010917c83564cd76c01c6e86cc39ebea7911fa`

### PR #11 — merged

Real child repair failed pre-write:

`AI Developer old_text must occur exactly once in quote_calculator.py; found 0`

Fix:

- classify only exact-source `old_text` mismatch as recoverable;
- allow one bounded pre-write correction;
- require literal current-source `old_text`;
- preserve immediate failure for path expansion, no-op and size violations.

Main after PR #11:

`ba8e0fee79676e3b65fc82d980d24989c1d22c90`

## 8. Latest observed result after PR #11

The Product Owner repair path ran and produced another inspectable `Changes.patch`.

The technical `old_text` blocker was passed, but the candidate was still semantically incomplete: it again implemented one treatment + discount rather than the requested three-treatment quote.

**Do not approve this candidate.**

Exact child run ID was not captured in the chat evidence and must not be invented.

## 9. PR #12 — semantic review blocker corrected

PR #12 was merged to main:

`0d557c57ed991c1ab8cf90cd96dd47952fa564ce`

It makes semantic objective coverage structured and blocking:

- Reviewer returns JSON Schema-constrained requirement coverage;
- quantitative requirements such as `three`, `each`, `all`, validation and tests are explicitly reviewed;
- MISSING/UNVERIFIED required behavior causes semantic FAIL;
- authoritative `ReviewReport.json` combines deterministic scope review and semantic review;
- if bounded repair budget remains, semantic FAIL triggers Developer repair -> deterministic retest -> semantic re-review;
- `READY_FOR_DECISION` is allowed only after review PASS;
- explicit Product Owner promotion gate remains unchanged.

## 10. Latest real-run blocker after PR #12

The next Product Owner repair attempt did not reach a new candidate. The UI returned:

`repair run execution failed: ProviderTransientError: Ollama unavailable: timed out`

Canonical code inspection confirmed:

- run timeout defaults to 60 seconds;
- the Product Owner child repair inherits the parent timeout;
- local S1/S2 routes use Ollama and allow one retry;
- the router currently passes the same 60-second timeout to both attempts.

Therefore the current local failure sequence is:

`60s attempt -> transient timeout -> 60s retry -> FAIL`

This is not evidence that the semantic-review logic failed. The run stopped because the local model provider exhausted its two identical timeout windows.

## 11. Current proposal

Working branch:

`mvp1-ollama-transient-timeout-retry`

Base:

`0d557c57ed991c1ab8cf90cd96dd47952fa564ce`

Proposal:

1. first Ollama attempt keeps the original requested timeout;
2. only after a transient Ollama failure, the existing retry uses 3x the original timeout, capped at 600 seconds;
3. current 60-second default therefore becomes `60 -> 180` for the two bounded attempts;
4. retry count remains exactly one;
5. non-Ollama providers keep unchanged timeout behavior;
6. deterministic test timeout remains unchanged;
7. model, cost, routing class, structured output, ToolGateway, semantic gate and promotion rules remain unchanged.

Regression tests cover:

- generic transient provider remains `60 -> 60`;
- Ollama transient retry becomes `60 -> 180`;
- widened retry is capped at 600 seconds.

No automatic GitHub CI has been available on the recent PRs, so local regression execution remains required after an approved merge.

## 11. Current MVP gate assessment

### G1 — Usability

**Materially demonstrated.**

The Product Owner can initiate a real run from the dashboard and receive visible validation errors.

### G2 — Autonomy

**FAIL / current blocker.**

The bounded child-run path now exists, but a transient local Ollama timeout currently exhausts two identical 60-second windows instead of recovering with a wider bounded retry window.

### G3 — Real output

**FAIL / not yet proven.**

Three-treatment visible behavior has not yet been delivered.

### G4 — Quality

**Implementation corrected by PR #12; real-run validation pending.**

Semantic review is now authoritative and blocking on main, but the first real validation attempt after PR #12 stopped at provider timeout before the semantic path could complete.

### G5 — Human control

**PASS so far.**

No Dental Quote candidate has been promoted. Explicit approval remains required.

## 12. Preserve / do not regress

Preserve:

- GitHub `main` as canonical source of truth;
- local checkout aligned by fast-forward only;
- deterministic mode;
- AI-assisted mode;
- AI Developer 1–3 path limit;
- read-only repository context;
- canonical project memory;
- ToolGateway authoritative writes;
- isolated worktrees;
- deterministic tests/retests;
- structured Ollama output;
- bounded repair;
- exact-source `old_text` validation;
- no fuzzy patch application;
- independent security review;
- explicit Product Owner promotion gate;
- exact reviewed-diff promotion;
- no automatic push;
- no automatic merge;
- no force/rebase;
- stale approvals not reusable;
- zero-cost local Ollama path.

## 13. Infrastructure freeze

Still active.

Do not start:

- deployment;
- advanced observability;
- multi-tenancy;
- billing;
- scale optimization;
- unrelated hardening/refactors;
- paid-provider expansion.

Only fix blockers concretely exposed by MVP-1.

## 14. Single next action

Validate the branch:

`mvp1-ollama-transient-timeout-retry`

If the proposal is sound, open/approve/merge its PR under the existing governed workflow.

Then:

1. fast-forward local ForgeLab to the approved `main`;
2. rerun the same Dental Quote Product Owner repair scenario once;
3. allow the existing Ollama retry to use the wider bounded timeout only if the first local call times out;
4. inspect `ReviewReport.json` and `Changes.patch`;
5. approve only if the patch genuinely implements the complete three-treatment objective;
6. after approval, verify exact promotion/retest/commit and visible target-app behavior.

Do not start MVP-2 until MVP-1 is actually PASS.

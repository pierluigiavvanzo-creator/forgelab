# ROADMAP.md

## Guiding metric

`ECONOMIC VALUE × USABLE PRODUCT VALUE / PRODUCT OWNER TIME`

ForgeLab is optimized for usable product output with low Product Owner effort, not for code volume, agent count, test count or infrastructure complexity.

## Governance baseline

`AGENTS_MASTER.md v2` is the shared operating standard.

For Golden Path work:

- classify work before execution;
- prefer REUSE/ADAPT over new custom infrastructure;
- use the smallest meaningful vertical slice;
- automate stable/reversible work;
- bound unstable learning loops;
- keep merge/promotion human-gated;
- treat green tests as necessary but not sufficient for usable product value.

## Completed technical foundation

- M8.5 — Human-approved local promotion — PASS
- M8.5.1 — UTF-8/BOM Git patch handling — PASS
- M8.6 — Bounded multi-file AI Developer — PASS
- M8.7 — Bounded AI Developer repair — PASS
- M8.7.1 — Windows-safe exact patch artifact persistence — PASS
- M8.8 — Bounded repository context / project-memory injection — PASS
- M8.9 — Canonical local ForgeLab source repository / self-hosting readiness — TECHNICAL PASS
- stabilization PR #18 — MERGED
- shared governance v2 / Marketability Card — present on `main`

Current canonical `main`:

`6d55b5587bf44a7efbcc0a81090ba5b6a7bdc98d`

## NOW — A Product Critical

### Aider Integration Stabilization Gate — PR #64

**Status:** PR #64 MERGED / post-merge lifecycle defects reproduced / correction at human review gate

The sequence PR #60–#63 proved that Aider integration must be validated as a complete reusable component rather than by repeated Dental target runs.

Binding gate before another Dental run:

`FORGELAB_AIDER_INTEGRATION_STABILIZATION_GATE`

Delivered by merged PR #64:

1. stabilized reusable-editor process/filesystem/environment boundary;
2. one centralized Aider execution contract across implementation and repair phases;
3. focused internal regression matrix;
4. launcher-enforced preflight against the actual pinned Aider 0.86.2 runtime;
5. dependency fingerprint evidence;
6. long-run API/dashboard lifecycle with immediate run id and observable status;
7. formal audit and residual-risk register.

Post-merge verification (2026-10-08): original 90 focused tests PASS on Windows/Python 3.11.9, but new executable regressions proved lifecycle defects. Corrections are isolated on `fix/post-pr64-run-lifecycle-stabilization`. Full executed evidence and the 16-PR hygiene proposal are in [docs/audits/FORGELAB_POST_PR64_VERIFICATION_2026-10-08.md](docs/audits/FORGELAB_POST_PR64_VERIFICATION_2026-10-08.md).

Single next action: `HUMAN_REVIEW_POST_PR64_LIFECYCLE_STABILIZATION`. Review the one correction PR; no automatic merge. Dental stays blocked on current `main` until the corrections are integrated and the merged runtime gate is verified.

The sections below retain the recovery rationale and future product sequence; they do not supersede this gate.

### MVP Recovery — Editor Boundary Reset

Problem:

The Golden Path is not blocked by missing dashboard/API/governance infrastructure. It is blocked by an unstable custom LLM-to-edit contract and a development loop that has transferred too much QA/retry work to the Product Owner.

Runtime PRs #37–#48 are frozen.

Do not extend the stacked recovery chain.

Primary task:

`DENTAL_QUOTE_AUTONOMOUS_GOLDEN_PATH` — integrate merged reusable editor harness into the real dashboard run

Target architecture:

`Planner -> EditorAdapter -> restricted editor sandbox -> deterministic validation -> ToolGateway apply -> tests -> Reviewer -> Security -> dashboard gate`

First reusable editor candidate:

`Aider CLI`

Why Aider first:

- narrow fit to code editing;
- Python implementation;
- Apache-2.0;
- local Ollama support;
- mature edit formats;
- scriptable one-shot CLI;
- auto commits can be disabled.

Bakeoff rule:

Compare current merged-main editor vs Aider adapter with the same Dental Quote objective and the same `qwen2.5-coder:7b`.

Measure:

- compile-valid candidate rate;
- malformed edit/recovery events;
- deterministic test status;
- semantic review status;
- model calls;
- repair attempts;
- wall time;
- Product Owner touches;
- unauthorized path changes;
- usable-output result.

Harness gate completed:

- adapter works only on disposable copies of authorized files;
- source repository remains unchanged;
- read-only mutation, path escape and new-file creation are blocked;
- paid-provider API keys are stripped from the editor subprocess;
- compile-invalid candidates stop before tests;
- deterministic scope/security/test evidence is produced;
- focused verification: 10 / 10 PASS;
- historical harness checkpoint: no Aider runtime dependency had yet been added; the later merged launcher now provisions isolated Aider 0.86.2.

PR #50 editor harness is MERGED.

Current product gate:

`DENTAL_QUOTE_AUTONOMY_GATE`

Exit gate:

1. initiate the unchanged Dental Quote objective from the dashboard;
2. use Aider + Ollama as the initial reusable editor path;
3. record any fallback explicitly;
4. reach tests PASS + semantic Reviewer PASS + Security PASS;
5. record ChatGPT assistance in target run = 0 and paid API cost EUR 0;
6. reach READY_FOR_DECISION without Product Owner log/debug work;
7. after approval, launch and manually verify the Dental Quote application;
8. only then mark Golden Path #1 PASS.

### Golden Path 1 — Dental Quote after integrated stabilization PASS

Required Product Owner journey:

`START LOCAL SERVICES ONCE -> OPEN DASHBOARD -> ENTER OBJECTIVE -> RUN -> DECISION-READY RESULT -> APPROVE | REJECT | REPAIR`

Pass condition:

ForgeLab produces the requested three-treatment application with tests/review/security evidence and without routine ChatGPT-directed PowerShell debugging.

## NEXT — only after Dental Quote PASS

### Golden Path 2 — Playable Game

ForgeLab must create a small game through the same dashboard-first governed workflow. This is a visible generalization proof, not a replacement for Dental Quote.

### Golden Path 3 — Small CRUD SaaS

Category: `records/users/workflow`.

Acceptance direction: create/read/update/delete records, bounded validation, workflow/status handling, deterministic tests, usable preview, same review and human-promotion gate.

### Golden Path 4 — Automation / Reporting Tool

Category: `ingest -> transform -> report`.

Acceptance direction: bounded input ingestion, deterministic validation/transformation, explicit invalid-record handling, generated report/output, deterministic tests, usable result, same review and human-promotion gate.

Generality PASS requires the same ForgeLab workflow across Dental Quote, playable game, CRUD, and reporting without hardcoding product-specific behavior into ForgeLab.

## Failure rule

For every Golden Path failure:

1. reproduce with concrete evidence;
2. trace the single blocking product gap;
3. make the smallest safe correction;
4. preserve isolation, ToolGateway, deterministic verification and human gate;
5. rerun the same scenario;
6. stop broad infrastructure work unless the Golden Path proves it is required.

## LATER — evidence-driven only

Deployment platform expansion, advanced observability, multi-tenancy, billing, scale optimization, additional paid providers/models, and unrelated architecture work.

## Economic validation

Track:

- Product Owner active minutes;
- Product Owner touches;
- time from objective to usable output;
- provider/model cost;
- autonomous repair cycles;
- manual developer time avoided;
- post-approval defects.

Primary near-term KPI:

`USER_TIME_SAVED_PER_SUCCESSFUL_RUN`

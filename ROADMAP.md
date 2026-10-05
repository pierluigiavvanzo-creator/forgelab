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

`8b67b98c61d6bd90af839d1cad185f05454a2e66`

## NOW — A Product Critical

### MVP Recovery — Editor Boundary Reset

Problem:

The Golden Path is not blocked by missing dashboard/API/governance infrastructure. It is blocked by an unstable custom LLM-to-edit contract and a development loop that has transferred too much QA/retry work to the Product Owner.

Runtime PRs #37–#48 are frozen.

Do not extend the stacked recovery chain.

Primary task:

`EDITOR_ENGINE_BAKEOFF_01` — harness candidate implemented; human merge review is the current gate

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
- no Aider runtime dependency has been added.

Current human gate:

`HUMAN_REVIEW_EDITOR_ADAPTER_BAKEOFF_HARNESS`

Post-merge experiment exit gate:

1. run the real Aider/Ollama boundary experiment;
2. compare edit reliability with current ForgeLab evidence;
3. Aider materially reduces malformed-edit failures OR is rejected with evidence;
4. only then decide whether to integrate an EditorAdapter into the Golden Path;
5. ordinary Golden Path validation returns to the dashboard;
6. Product Owner is not used as the repeated CLI/PowerShell test harness.

### Golden Path 1 — Dental Quote resumes after bakeoff

Required Product Owner journey:

`START LOCAL SERVICES ONCE -> OPEN DASHBOARD -> ENTER OBJECTIVE -> RUN -> DECISION-READY RESULT -> APPROVE | REJECT | REPAIR`

Pass condition:

ForgeLab produces the requested three-treatment application with tests/review/security evidence and without routine ChatGPT-directed PowerShell debugging.

## NEXT — only after Dental Quote PASS

### Golden Path 2 — Small CRUD SaaS

Category: `records/users/workflow`.

Acceptance direction: create/read/update/delete records, bounded validation, workflow/status handling, deterministic tests, usable preview, same review and human-promotion gate.

### Golden Path 3 — Automation / Reporting Tool

Category: `ingest -> transform -> report`.

Acceptance direction: bounded input ingestion, deterministic validation/transformation, explicit invalid-record handling, generated report/output, deterministic tests, usable result, same review and human-promotion gate.

Generality PASS requires the same ForgeLab workflow across all three categories without hardcoding for Dental Quote.

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

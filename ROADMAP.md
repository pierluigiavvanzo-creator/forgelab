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

Current canonical `main` before PR #28:

`a3fefabd1a39a3a8d8c20ffd88ccfca5bc732496`

## NOW — A Product Critical

### Golden Path 1 — Dental Quote

Required journey:

`PRODUCT OBJECTIVE -> PROJECT/REPO CONTEXT -> STRUCTURED PLAN -> IMPLEMENT -> TEST -> BOUNDED AUTO-REPAIR -> RETEST -> INDEPENDENT REQUIREMENT REVIEW -> WORKING PREVIEW -> PRODUCT OWNER APPROVAL -> PROMOTABLE PRODUCT`

Target:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

Pass condition:

ForgeLab produces the complete requested three-treatment application without ChatGPT manually orchestrating routine repair/debug steps.

### Latest Golden Path evidence

PR #26 was merged to `main` at `97f25bdb358adaa050735d463000495bafcf0b85`; PR #27 subsequently updated governance only.

Fresh rerun `run-0a4726594909`:

- syntax recovery worked and execution reached deterministic testing;
- first test run: 4 PASS / 1 ERROR;
- one bounded repair fixed the originally failing test;
- the same repair regressed two tests that had been PASS;
- repair changed established dictionary-return behavior into float-return behavior;
- run stopped before semantic review.

Current blocker:

`PROMPT_ONLY_REGRESSION_CONSTRAINT_NOT_ENFORCED_DETERMINISTICALLY`

### Current remediation — PR #28

PR #28 implements the smallest product-relevant correction:

`FAILED TEST -> BOUNDED REPAIR -> DETERMINISTIC REGRESSION DIFF -> ROLLBACK -> ONE IN-ATTEMPT CORRECTION -> RETEST`

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

It upgrades the existing prompt-level regression rule into a deterministic orchestration gate.

No new dependency, provider, agent role, top-level repair budget or broad infrastructure was added.

Local validation reached `FORGELAB VALIDATION PASS`.

### PR #28 exit gate

PR #28 is not complete until:

1. Product Owner explicitly approves merge;
2. exact approved PR HEAD is merged to `main`;
3. the same unchanged Dental Quote Golden Path is rerun;
4. a repair that breaks previously passing tests is deterministically detected, rolled back, and corrected once or safely blocked.

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

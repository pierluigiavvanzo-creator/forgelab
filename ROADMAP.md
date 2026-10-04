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

Current canonical `main` before PR #29:

`718af139078537a29bbb93ed06089f52162f526a`

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

Fresh rerun after PR #28 failed before write after the single full-file syntax recovery also produced invalid Python.

Current blocker:

`PREWRITE_RECOVERY_EXHAUSTION_NOT_GOVERNED`

### Current remediation — PR #29

PR #29 implements the smallest product-relevant correction:

`INVALID CANDIDATE -> ONE PRE-WRITE RECOVERY -> INVALID AGAIN -> GOVERNED CLOSED / REPAIR REQUIRED + ARTIFACTS`

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

It converts exhausted pre-write recovery from an uncaught exception into a normal governed terminal state.

No new dependency, provider, agent role, repair budget or broad infrastructure was added.

Local validation reached `FORGELAB VALIDATION PASS`.

### PR #29 exit gate

PR #29 is not complete until:

1. Product Owner explicitly approves merge;
2. exact approved PR HEAD is merged to `main`;
3. the same unchanged Dental Quote Golden Path is rerun;
4. exhausted pre-write recovery produces governed artifacts and never surfaces as `run execution failed`.

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

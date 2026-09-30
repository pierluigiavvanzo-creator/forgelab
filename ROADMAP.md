# ROADMAP.md

## Guiding metric

`ECONOMIC VALUE × USABLE PRODUCT VALUE / USER TIME`

ForgeLab is optimized for usable product output with low Product Owner effort, not for code volume, agent count, test count or infrastructure complexity.

## Completed technical foundation

- M8.5 — Human-approved local promotion — PASS
- M8.5.1 — UTF-8/BOM Git patch handling — PASS
- M8.6 — Bounded multi-file AI Developer — PASS
- M8.7 — Bounded AI Developer repair — PASS
- M8.7.1 — Windows-safe exact patch artifact persistence — PASS
- M8.8 — Bounded repository context / project-memory injection — PASS
- M8.9 — Canonical local ForgeLab source repository / self-hosting readiness — TECHNICAL PASS
- MVP-1 blocker sequence PR #5 through PR #17 — merged on `main`

Current verified `main` before stabilization: `20c3c2565c6ce066520b8ce831b13640858cde2b`.

## NOW — A Product Critical

### Stabilization publication gate

Candidate branch: `mvp1-stabilization-cleanup`

Evidence:

- 68 dead/premature files removed;
- 72 tracked files in the reviewed local code change;
- 19 insertions / 7,633 deletions;
- API integration tests 12/12 PASS;
- full Python suite 106/106 PASS;
- dashboard production build PASS reported by Product Owner;
- no intentional core orchestrator, ToolGateway, promotion, repair-budget, runner, smoke or telemetry changes.

Exit condition: PR diff matches reviewed scope, CI has no new blocker, and Product Owner explicitly approves merge.

### Golden Path 1 — Dental Quote

Immediately after approved stabilization merge:

`PRODUCT OBJECTIVE -> CREATE/SELECT PROJECT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED AUTO-REPAIR -> RETEST -> REQUIREMENT REVIEW -> WORKING PREVIEW -> PRODUCT OWNER APPROVAL -> PROMOTABLE PRODUCT`

Target: `C:\\Users\\NITRO\\source\\FORGELAB_MVP1_DENTAL_QUOTE`

Pass condition: ForgeLab produces the complete requested three-treatment application without ChatGPT manually orchestrating routine repair/debug steps.

Only blockers demonstrated by this journey may justify additional ForgeLab changes.

## NEXT — generality proof after Dental Quote PASS

### Golden Path 2 — Small CRUD SaaS

Category: `records/users/workflow`.

Acceptance direction: create/read/update/delete records, bounded validation, workflow/status handling, deterministic tests, usable preview, same review and human-promotion gate.

### Golden Path 3 — Automation / Reporting Tool

Category: `ingest -> transform -> report`.

Acceptance direction: bounded input ingestion, deterministic validation/transformation, explicit invalid-record handling, generated report/output, deterministic tests, usable result, same review and human-promotion gate.

Generality PASS requires the same ForgeLab workflow across all three categories without being hardcoded for Dental Quote.

## Failure rule

For every Golden Path failure: identify one blocking product gap, make the smallest safe correction, preserve isolation/ToolGateway/deterministic verification/human gate, rerun the same scenario, and do not start broad infrastructure work.

## LATER — evidence-driven only

Deployment platform expansion, advanced observability, multi-tenancy, billing, scale optimization and expanded paid provider/model routing.

## Economic validation

Track Product Owner active minutes, user touches, time to usable output, provider/model cost, autonomous repair cycles, manual developer time avoided and post-approval defects.

Primary economic KPI: `USER_TIME_SAVED_PER_SUCCESSFUL_RUN`.

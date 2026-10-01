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

---

## Commercial evidence realignment — 2026-10-01

**Commercial evidence level:** `C0 — Hypothesis`.

ForgeLab's stabilization and Golden Path work remain Product Critical only because they can create a credible, measurable demo asset. They are **not** market validation.

### Commercialization hypothesis to test

For the first market test, prefer selling a **bounded usable software outcome produced by ForgeLab** rather than asking an external buyer to purchase the ForgeLab control plane itself.

This is a testable go-to-market hypothesis, not a permanent product-positioning decision.

### Evidence sequence

`C0A — INTERNAL CAPABILITY PROOF`
- complete the already-reviewed stabilization publication gate;
- run the Dental Quote Golden Path once end-to-end;
- record elapsed time, Product Owner intervention minutes, repair attempts, runtime/model cost and final usable-output status;
- treat the result as a demo/evidence asset only.

`C1 — BUYER/PROBLEM EVIDENCE`
- select one narrow buyer segment and one bounded software job;
- validate that the job is frequent/costly/risky enough to justify external help or tooling;
- identify current alternative, decision maker, expected time-to-value and acceptable delivery model.

`C2 — REAL BRIEF / SOLUTION EVIDENCE`
- obtain a real external software brief from a qualified prospect;
- use ForgeLab to produce a reviewable working preview/output;
- record buyer feedback, required corrections, trust objections and delivery burden.

`C3 — TRANSACTION EVIDENCE`
- paid pilot, paid bounded build, signed LOI with economic commitment or equivalent strong willingness-to-pay signal.

### Freeze rule after Dental Quote

After one fresh Dental Quote Golden Path PASS, freeze additional internal benchmark apps, agent expansion, platform breadth and infrastructure work unless:
- a real buyer brief exposes a concrete blocker; or
- a specific commercial objection requires evidence.

The previously planned generic second application becomes secondary to external proof. It should run only when it answers a commercial/generalization question that a real prospect makes material.

### Single next commercial action

`FORGELAB_C1_OUTPUT_FIRST_BUYER_VALIDATION`

Prepare the narrow ICP/job hypothesis and a bounded external pilot offer. No external commercial commitment is authorized by this roadmap update.

### Sellability metrics

Track alongside technical quality:
- objective-to-working-preview elapsed time;
- Product Owner/human minutes per delivered outcome;
- repair/retry count;
- runtime/model/infrastructure cost per delivered outcome;
- buyer-requested correction count;
- time from first brief to usable result;
- support/onboarding minutes;
- transaction outcome.


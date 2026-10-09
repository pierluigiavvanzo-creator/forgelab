# ROADMAP.md

Guiding metric:

ECONOMIC VALUE × USABLE PRODUCT VALUE / PRODUCT OWNER TIME

## NOW — bounded repository cleanup

Goal:
reduce repository noise and stale live-tree material without changing ForgeLab execution semantics.

Cleanup proposal:
- remove obsolete dashboard starter files/assets and unused npm installer path;
- retire the completed editor-bakeoff experiment surface;
- remove old milestone acceptance reports from the live tree while preserving Git history;
- compact canonical state/handover documents;
- keep lockfile, active runtime code, current audits/ADRs and governance.

Exit gate:
- branch diff reviewed;
- imports/references clean;
- full Python suite PASS locally;
- dashboard lifecycle tests PASS;
- dashboard production build PASS;
- launcher readiness/stability PASS;
- no source/runtime behavior regression;
- explicit Product Owner merge approval.

## NEXT — qualify semantic-repair execution

Do not rerun Dental until one semantic-repair path passes the unchanged synthetic acceptance fixture with the required reliability threshold.

Preferred sequence:
1. resource-fit local model candidate;
2. exactly two independent qualification runs;
3. 2/2 PASS required;
4. role-specific provider/model change only if qualified;
5. no paid fallback without approval.

## THEN — Dental Golden Path

Run the unchanged Dental objective from the dashboard.

PASS requires:
- three treatments;
- visible/correct subtotals;
- percentage discount validation;
- correct final total;
- invalid-input handling;
- direct tests PASS;
- independent Reviewer PASS;
- Security PASS;
- READY_FOR_DECISION;
- explicit Product Owner approval;
- promoted application launches and is visibly usable;
- paid API cost EUR 0 unless separately approved;
- no Product Owner debugging/log-transport loop.

## AFTER DENTAL PASS

Golden Path 2 — playable small game.

Golden Path 3 — small CRUD SaaS.

Golden Path 4 — ingest/transform/report automation.

Generality is proven only when the same governed workflow succeeds across these categories without product-specific logic in ForgeLab.

## Deferred until product evidence requires it

- multi-tenancy;
- billing sophistication;
- broad cloud infrastructure;
- advanced observability;
- large provider matrix;
- unrelated architecture refactors;
- cleanup driven only by aesthetics rather than measurable maintenance/runtime value.

## Failure rule

REPRODUCE → TRACE → ROOT CAUSE → ONE BOUNDED FIX → SAME TEST → STOP OR CONTINUE

Do not stack speculative fixes or call green tests product validation.

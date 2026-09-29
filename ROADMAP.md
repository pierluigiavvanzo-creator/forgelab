# ROADMAP.md

## Guiding metric

`ECONOMIC VALUE × USABLE PRODUCT VALUE / USER TIME`

Do not optimize milestones, test count or infrastructure complexity as ends in themselves.

## Completed technical foundation

- M8.5 — Human-approved local promotion — PASS
- M8.5.1 — UTF-8/BOM Git patch handling — PASS
- M8.6 — Bounded multi-file AI Developer — PASS
- M8.7 — Bounded AI Developer repair — PASS
- M8.7.1 — Windows-safe exact patch artifact persistence — PASS
- M8.8 — Bounded repository context / project-memory injection — PASS
- M8.9 — Canonical local ForgeLab source repository / self-hosting readiness — TECHNICAL PASS

## NOW — A Product Critical

### MVP-1 — Real Application Test

Target:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

Original objective:

> Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.

Current evidence:

- dashboard run initiation works;
- local Ollama structured multi-file generation works;
- deterministic tests execute;
- evidence is directly inspectable;
- Product Owner human gate works;
- Product Owner repair can launch a bounded child run;
- exact-source `old_text` mismatch has one bounded pre-write correction;
- no provider spend was introduced;
- no candidate has been promoted.

Current Product Critical blocker:

> Semantic review is generated but not authoritative. Scope-only `ReviewReport.json` can PASS while the patch fails the actual objective.

Current proposal:

`mvp1-semantic-review-gate`

Required validation:

`objective -> structured semantic review -> FAIL on missing requirement -> bounded repair -> retest -> semantic re-review -> READY_FOR_DECISION only on full review PASS`

### MVP-1 gates

1. **Usability** — materially demonstrated.
2. **Autonomy** — in progress; semantic review repair must stop Product Owner retry orchestration.
3. **Real output** — not yet PASS; three-treatment behavior remains unproven.
4. **Quality** — not yet PASS; semantic objective coverage must become blocking.
5. **Human control** — PASS so far; explicit approval remains required before promotion.

## Failure rule

For every MVP-1 failure:

1. identify the single blocking product gap;
2. make the smallest safe correction;
3. preserve repository/tool/human-gate governance;
4. rerun the same Dental Quote scenario;
5. do not start broad infrastructure work.

## NEXT — only after MVP-1 PASS

### MVP-2 — Real multi-file feature

Repeat on a real multi-file task without increasing Product Owner operational burden.

### MVP-3 — Failure + autonomous bounded repair

Demonstrate a real failing candidate diagnosed and repaired without Product Owner debugging/retry orchestration.

### MVP-4 — Second unrelated repository

Prove repeatability outside the Dental Quote test repository.

## LATER — evidence-driven only

- deployment;
- advanced observability;
- multi-tenant;
- billing;
- scale optimization;
- expanded paid provider/model routing.

## Economic validation track

For every real MVP run record:

- Product Owner active minutes;
- user touches;
- elapsed time to usable result;
- provider/model cost;
- autonomous repair cycles;
- manual developer time avoided;
- post-approval defects.

Primary economic KPI:

`USER_TIME_SAVED_PER_SUCCESSFUL_RUN`

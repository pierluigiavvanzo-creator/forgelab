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


## 2026-09-29 MVP-1 live blocker update

PR #12 merged the blocking semantic-review gate.

The next real Product Owner repair attempt failed before candidate completion with:

`ProviderTransientError: Ollama unavailable: timed out`

Current code gives local Ollama one retry, but both attempts use the same inherited 60-second timeout.

Current proposal branch:

`mvp1-ollama-transient-timeout-retry`

Minimal intended behavior:

`60s first local attempt -> transient timeout -> one 180s retry`

No extra retry, no paid provider, no model change, no deterministic test-timeout change.

Single next action: validate and, only with explicit Product Owner approval, merge that proposal; then repeat the same Dental Quote repair scenario.


## 2026-09-29 MVP-1 live blocker update — authorized scope vs mandatory edits

PR #13 merged the bounded Ollama transient retry timeout.

The next real Product Owner repair attempt then failed with:

`AIDeveloperFormatError: AI Developer multi-file patch missing fields: changes, schema_version`

Root cause: initial AI Developer generation currently treats every authorized path as a mandatory edit.

Current proposal branch:

`mvp1-authorized-scope-subset-normalization`

Required behavior:

- authorized paths remain immutable maximum write scope;
- initial AI Developer may return any non-empty subset of those paths;
- a complete flat single-change response may be deterministically wrapped into the multi-file contract;
- no missing change is invented;
- exact-source/path/scope/no-op/size validation remains authoritative;
- blocking semantic review decides whether the subset actually satisfies the objective.

Single next action: validate and, only with explicit Product Owner approval, merge that proposal; then repeat the same Dental Quote repair scenario once.


## 2026-09-29 MVP-1 live blocker update — disjoint same-file operations

PR #14 merged the authorized-scope subset/normalization correction.

The next real Product Owner repair attempt then failed with:

`ValueError: AI Developer multi-file patch contains duplicate paths`

Root cause: the multi-file validator still assumes one structured change per file, even when separate edits to the same authorized file are independent.

Current proposal branch:

`mvp1-disjoint-same-file-change-composition`

Required behavior:

- subset mode remains inside the same authorized path set;
- permit at most 4 operations per authorized path;
- validate every `old_text` against the same current source snapshot;
- reject overlapping original-source spans;
- deterministically compose disjoint same-file operations into one final file replacement;
- apply one ToolGateway write per changed file;
- preserve deterministic tests, semantic review and explicit Product Owner gate.

Single next action: validate and, only with explicit Product Owner approval, merge this proposal; then repeat the same Dental Quote repair scenario once.

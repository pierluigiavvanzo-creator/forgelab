# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-09-22
**Checkpoint:** M8.9 source synchronization complete / infrastructure freeze
**Status:** GitHub + local main aligned; next action is MVP-1

## 1. Mission

ForgeLab is a governed multi-agent software-development control plane.

Target outcome:

> Receive a Product Owner objective, understand repository/context, plan, modify software in an isolated workspace, test, diagnose/repair in bounded loops, perform independent review/security, and present APPROVE / REJECT / REPAIR without routine manual debugging by the Product Owner.

Guiding metric:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / USER TIME`

Operating preferences:

- normal ChatGPT chat + local PowerShell;
- no Work or Codex;
- bounded autonomy;
- Product Owner involved only at material decision gates;
- product before infrastructure;
- avoid diagnostic/governance loops that do not increase usable value.

## 2. Local environment

Validated local ForgeLab root:

`C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`

Dashboard:

`http://127.0.0.1:5173`

API:

`http://127.0.0.1:8765`

Launcher:

`Start-ForgeLab.ps1`

Local AI:

- Ollama 0.34.2;
- `qwen2.5-coder:7b`;
- provider alias `ollama`;
- provider cost EUR 0.

## 3. Milestones already validated

Do not repeat without concrete regression evidence:

- M8.5 — Human-approved local promotion — PASS
- M8.5.1 — UTF-8/BOM Git patch handling — PASS
- M8.6 — Bounded multi-file AI Developer — PASS
- M8.7 — Bounded AI Developer repair — PASS
- M8.7.1 — Windows-safe exact patch artifact persistence — PASS
- M8.8 — Bounded repository context / project-memory injection — PASS
- M8.9 — Canonical Git source / self-hosting readiness — TECHNICAL PASS

Validated flow:

`objective`
→ canonical project memory
→ bounded read-only repository context
→ Planner
→ AI Developer
→ authorized write paths
→ structured patch
→ isolated workspace / ToolGateway
→ deterministic tests
→ bounded repair
→ independent Reviewer
→ Security
→ `READY_FOR_DECISION`
→ explicit Product Owner gate
→ exact reviewed promotion
→ local promotion branch
→ deterministic retest
→ local commit
→ reviewed-diff equivalence
→ `DONE`

## 4. M8.9 validated baseline

Historical validated M8.9 baseline:

- baseline commit: `58d22eeca66c27871738c04c6d850c59efabf115`
- baseline tree: `63b6c91427edb19cd038cf557904451dfc08a947`
- tracked canonical files: 168
- canonical manifest SHA-256: `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3`
- worktree smoke: PASS
- regression suite: 88 tests PASS, exit 0
- API `/health`: HTTP 200
- dashboard `/`: HTTP 200
- protected unauthenticated API behavior: HTTP 401

M8.9 separated canonical source from runtime/cache/log/backup/generated material and established Git discipline.

## 5. GitHub and local synchronization state

Repository:

`pierluigiavvanzo-creator/forgelab`

Synchronization is **COMPLETE**.

Evidence:

- exact M8.9 source baseline published to `baseline/m8.9-local` at `58d22eeca66c27871738c04c6d850c59efabf115`;
- code + governance integrated on `integration/m8.9-code-plus-governance`;
- integration commit `8dfd9c81a9c8b1c17ef16833beaef7cc437c46a4`;
- PR #2 merged into GitHub `main`;
- PR #2 merge commit `9560729bfc9f27422d92d20d8fb43db5886a1cba`;
- local `main` fast-forwarded to the same GitHub `main` commit and verified clean;
- no force push or rebase used.

Decision:

**GitHub `main` is now the canonical shared source of truth for ForgeLab code and project governance.**

The local checkout tracks the same canonical history.

## 6. Product Owner decision — infrastructure freeze

Do not continue with broad infrastructure work before MVP evidence.

Freeze unless a real MVP failure proves it is required:

- additional hardening;
- new validation harnesses;
- advanced observability;
- deployment;
- scaling;
- multi-tenant;
- billing;
- unrelated governance/refactor work.

## 7. Current product status

ForgeLab is:

**PRE-MVP / TECHNICALLY CAPABLE**

What is proven:

- substantial technical foundation;
- isolation;
- deterministic verification;
- bounded repair;
- review/security;
- human approval/promotion controls;
- canonical source synchronized between GitHub and local checkout.

What is not yet proven:

- a real external application changed successfully from the dashboard with minimal Product Owner intervention;
- measurable user-time/cost savings;
- repeatability across unrelated real repositories;
- commercial willingness to pay.

## 8. SINGLE NEXT ACTION

### FORGELAB_MVP_1_REAL_APPLICATION_TEST

Classification:

**A — Product Critical**

Goal:

Prove ForgeLab works as a product, not merely as a technically sound framework.

Required Product Owner journey:

1. open dashboard;
2. select/register a real target application;
3. enter one feature objective;
4. press Run;
5. receive actual software change and evidence;
6. choose APPROVE / REJECT / REPAIR;
7. approve only if satisfied;
8. verify the promoted application actually works.

Recommended test application:

**Dental Quote Calculator** or another small external application with visible behavior.

Example feature objective:

> Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies/configuration unless necessary and explicitly justified.

## 9. Five MVP gates

MVP-1 passes only if all five pass:

1. **Usability** — run initiated from dashboard.
2. **Autonomy** — no routine log-copy/manual debugging/retry orchestration.
3. **Real output** — target application visibly changes.
4. **Quality** — tests + review + security pass.
5. **Human control** — nothing is promoted before explicit APPROVE.

## 10. Failure rule

If MVP-1 fails:

1. stop;
2. identify the single blocking product gap;
3. fix only that gap;
4. rerun the same scenario.

Do not hide a failed product journey behind another broad infrastructure milestone.

## 11. Preserve / do not regress

Preserve:

- GitHub `main` as canonical shared source truth;
- local checkout aligned to canonical history;
- deterministic mode;
- AI-assisted mode;
- bounded multi-file scope;
- bounded repair;
- read-only context selection;
- canonical project memory;
- ToolGateway authoritative writes;
- deterministic tests/retests;
- evidence-backed diagnostics;
- independent review;
- security check;
- explicit human promotion gate;
- isolated worktree execution;
- exact reviewed-diff promotion;
- UTF-8/BOM handling;
- Windows LF/CRLF-safe patch persistence;
- no direct-main execution writes;
- no automatic push/merge/force;
- stale/consumed approvals not reusable;
- zero-cost local Ollama path.

## 12. MVP measurement

For each real run measure:

- Product Owner active minutes;
- user touches;
- elapsed time to usable result;
- provider/model cost;
- autonomous repair cycles;
- manual developer time avoided;
- defects after approval.

Primary economic KPI:

`USER_TIME_SAVED_PER_SUCCESSFUL_RUN`

## 13. Bootstrap instruction for a new session

Use GitHub `pierluigiavvanzo-creator/forgelab` as the source of truth and read, in order:

1. `MANIFEST.md`
2. `AGENTS.md`
3. `PROJECT_STATE.md`
4. `ROADMAP.md`
5. `DECISIONS.md`
6. this handover
7. relevant audit/baseline documents

Then execute only:

`FORGELAB_MVP_1_REAL_APPLICATION_TEST`

Do not reconstruct M8.5–M8.9 unless a concrete inconsistency is found.

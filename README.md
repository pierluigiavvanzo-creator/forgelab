# ForgeLab

ForgeLab is a governed multi-agent software-development control plane.

Its target workflow is:

`Objective -> project/repository context -> plan -> minimum necessary agents -> isolated implementation -> deterministic tests -> bounded repair -> independent review -> security -> READY_FOR_DECISION -> Product Owner approval -> exact reviewed promotion`

## Current status

**PRE-MVP / MVP validation active**

Historical M8.9 acceptance passed the following checks (not the current test count):

- 88 regression tests PASS;
- API health PASS;
- dashboard PASS;
- bounded multi-file AI development;
- bounded repair;
- repository-context selection;
- independent review/security;
- explicit human promotion gate;
- canonical Git source baseline.

ForgeLab has **not yet passed a real product MVP test** on an external application with minimal Product Owner intervention.

## Current priority

`HUMAN_REVIEW_POST_PR64_LIFECYCLE_STABILIZATION`

PR #64 is merged at `6d55b5587bf44a7efbcc0a81090ba5b6a7bdc98d`. Post-merge verification found lifecycle defects despite the original focused tests passing. See [executed evidence](docs/audits/FORGELAB_POST_PR64_VERIFICATION_2026-10-08.md); Dental remains pending integrated stabilization PASS.

The Product Owner should ideally be able to:

`Dashboard -> choose/register target project -> objective -> Run -> inspect result -> APPROVE / REJECT / REPAIR`

If normal use requires repeated PowerShell scripts, log transport or manual debugging, the MVP test is considered failed.

## Canonical source and M8.9 baseline

Historical validated M8.9 baseline:

- root: `C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`
- baseline commit: `58d22eeca66c27871738c04c6d850c59efabf115`
- baseline tree: `63b6c91427edb19cd038cf557904451dfc08a947`
- tracked canonical files: 168
- canonical manifest SHA-256: `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3`

Synchronization status:

- exact M8.9 baseline published to `baseline/m8.9-local`;
- code + governance integrated on `integration/m8.9-code-plus-governance`;
- PR #2 merged with merge commit `9560729bfc9f27422d92d20d8fb43db5886a1cba`;
- local `main` fast-forwarded to that GitHub `main` commit and verified clean.

GitHub `pierluigiavvanzo-creator/forgelab` is now the canonical shared source of truth for ForgeLab code and project governance. The local checkout tracks the same canonical history.

## Start here

Read in this order:

1. `MANIFEST.md`
2. `AGENTS.md`
3. `PROJECT_STATE.md`
4. `ROADMAP.md`
5. `DECISIONS.md`
6. `docs/handovers/HANDOVER_CURRENT.md`
7. `docs/audits/FORGELAB_PRODUCT_OUTCOME_AUDIT_2026-09-22.md`
8. `docs/governance/REGOLE_OPERATIVE_COMUNI_PROGETTI.md`

## Product rule

Green tests and sound architecture are necessary, but they do not prove product value.

Progress is measured by usable outcomes, reduced Product Owner effort and credible economic value.

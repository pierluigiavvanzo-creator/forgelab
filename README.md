# ForgeLab

ForgeLab is a governed multi-agent software-development control plane.

Its target workflow is:

`Objective -> project/repository context -> plan -> minimum necessary agents -> isolated implementation -> deterministic tests -> bounded repair -> independent review -> security -> READY_FOR_DECISION -> Product Owner approval -> exact reviewed promotion`

## Current status

**PRE-MVP / MVP validation active**

The technical foundation has passed M8.9 local acceptance, including:

- 88 regression tests PASS;
- API health PASS;
- dashboard PASS;
- bounded multi-file AI development;
- bounded repair;
- repository-context selection;
- independent review/security;
- explicit human promotion gate;
- canonical local Git source baseline.

However, ForgeLab has **not yet passed a real product MVP test** on an external application with minimal Product Owner intervention.

## Current priority

`FORGELAB_MVP_1_REAL_APPLICATION_TEST`

The Product Owner should ideally be able to:

`Dashboard -> choose/register target project -> objective -> Run -> inspect result -> APPROVE / REJECT / REPAIR`

If normal use requires repeated PowerShell scripts, log transport or manual debugging, the MVP test is considered failed.

## Canonical local baseline

The currently validated local control-plane source is **not yet fully synchronized to this GitHub repository**.

Local baseline:

- root: `C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`
- local branch: `main`
- commit: `58d22eeca66c27871738c04c6d850c59efabf115`
- tree: `63b6c91427edb19cd038cf557904451dfc08a947`
- tracked canonical files: 168
- manifest SHA-256: `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3b`

This remote currently serves as the canonical **project/governance memory** until the local source is separately reviewed and synchronized.

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

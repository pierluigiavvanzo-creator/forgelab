# PROJECT_STATE.md

**Last updated:** 2026-10-01
**Current phase:** PRE-MVP / Software Factory Golden Path validation
**Current priority:** A — Product Critical
**Commercial evidence level:** C0 — Hypothesis

## Canonical source

Repository: `pierluigiavvanzo-creator/forgelab`

Canonical shared truth: `main`

Current canonical `main` before PR #20: `3fb2e6940325650f9c97a18d0e845355c4eab404`.

PR #18 stabilization was merged previously; later governance updates added `AGENTS_MASTER.md v2` and `MARKETABILITY_CARD.md` on `main`.

## Product direction

ForgeLab remains the primary product.

Target workflow:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED REPAIR -> REVIEW -> WORKING PREVIEW -> HUMAN APPROVAL -> PROMOTION`

Provider remains replaceable; current zero-cost local path is Ollama.

Primary product/economic metric:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / PRODUCT OWNER TIME`

## Golden Path sequence

1. Dental Quote — calculator/business logic.
2. Small CRUD SaaS — records/users/workflow.
3. Automation/reporting tool — ingest -> transform -> report.

Dental Quote target:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

Objective:

`Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.`

## Golden Path 1 evidence

Fresh run:

`run-6a0c2c512498`

Observed result:

- isolated AI Developer run executed;
- only `quote_calculator.py` and `test_quote_calculator.py` were modified;
- deterministic tests passed after one bounded repair;
- independent semantic review correctly blocked promotion;
- final candidate still implemented a one-treatment workflow and did not fully satisfy the three-treatment objective;
- reviewer identified missing objective coverage and missing tests;
- no candidate was promoted.

Root cause established from the runtime:

`PROJECT_MANAGER_OUTPUT_NOT_CONSUMED_BY_DEVELOPER`

The Project Manager generated a plan, but the Developer did not consume that plan/acceptance criteria before implementation. The Reviewer was stricter than the initial Developer because it explicitly decomposed every obligation, including quantitative requirements.

## PR #20 — acceptance contract propagation

Branch:

`mvp1-plan-to-developer-acceptance-contract`

Current tested candidate HEAD before memory-only update:

`2d3e766f4c9f58f29c71816422ebc41f6ab70df2`

PR:

`#20 — MVP-1: propagate PM acceptance contract to Developer`

Candidate behavior:

- Project Manager returns a structured implementation plan;
- structured plan contains `intended_outcome`, `execution_steps`, `acceptance_criteria`, and `principal_risks`;
- Project Manager is instructed to preserve quantitative requirements and not invent new product scope;
- Developer task contract consumes PM `acceptance_criteria`;
- initial Developer generation consumes the binding acceptance contract;
- test-failure repair and semantic-review repair consume the same contract;
- Reviewer remains independent and evaluates the original Product Owner objective;
- no new agent, provider, dependency, repair budget or remote infrastructure was added.

## Validation evidence for PR #20

Product Owner local validation on 2026-10-01 reached:

`=== FORGELAB VALIDATION PASS ===`

The self-checking validation harness requires all of the following before PASS:

- clean worktree before tests;
- focused PM -> Developer -> semantic-repair contract test exits 0;
- two API AI-generate regression tests exit 0;
- full Python unittest discovery over `tests/test*.py` exits 0;
- full discovery must execute more than zero tests;
- clean worktree after tests.

Evidence state:

**TESTED locally; NOT YET MERGED; NOT YET REAL-WORKFLOW REVALIDATED.**

## MVP gates

- G1 Usability: materially demonstrated.
- G2 Autonomy: improved but not PASS until the same Dental Quote objective is rerun successfully after PR #20 integration.
- G3 Real output: not yet PASS for the complete three-treatment objective.
- G4 Quality: deterministic tests plus independent semantic blocking are working; PR #20 contract propagation is locally TESTED.
- G5 Human control: PASS so far; no candidate or PR is merged/promoted without explicit Product Owner approval.

## Single next action

Review PR #20 and obtain explicit Product Owner approval before merge.

After approved merge, rerun the **same unchanged Dental Quote Golden Path** with the same bounded repair budget. Do not start CRUD/reporting validation until Dental Quote passes.

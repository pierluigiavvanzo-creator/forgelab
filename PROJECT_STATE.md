# PROJECT_STATE.md

**Last updated:** 2026-10-01
**Current phase:** PRE-MVP / Software Factory Golden Path validation
**Current priority:** A — Product Critical
**Commercial evidence level:** C0 — Hypothesis

## Canonical source

Repository: `pierluigiavvanzo-creator/forgelab`

Canonical shared truth: `main`

Current canonical `main` before PR #24: `18a49ab54f90efefabdd5e54c4abeebd962cd35a` (merge of PR #23).

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

Earlier run:

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

**PR #20 was TESTED locally and merged to `main` at `c0c7fafb604893840efe22597f1ae18bb4cd32f5`.**

## Golden Path rerun after PR #20

Run:

`run-c135dcec0887`

Observed result:

- deterministic status PASS;
- Developer added aggregate multi-treatment calculation helpers;
- Developer added explicit tests for three treatments and percentage-discount calculations;
- existing Tkinter UI remained a one-treatment workflow;
- aggregate discount remained hard-coded at 10% instead of being user-configurable end-to-end;
- independent Reviewer correctly blocked promotion overall;
- Reviewer wording was partially inaccurate because it described present-but-incomplete behavior/tests as absent.

New blocker:

`END_TO_END_ACCEPTANCE_NOT_ENFORCED_AND_REVIEW_EVIDENCE_NOT_GROUNDED`

## PR #22 — end-to-end acceptance and grounded review

Branch:

`mvp1-end-to-end-acceptance-and-review-evidence`

Runtime/test candidate HEAD validated locally:

`0bd8cd2c937eaca93d18ab2b0b2bbfcaf0ec61b4`

PR:

`#22 — MVP-1: enforce end-to-end acceptance and grounded review`

Candidate behavior:

- Project Manager receives complete authorized target files as bounded read-only planning context;
- Developer must wire user-visible requirements through an existing interface/entry point;
- helper-only implementation no longer counts as end-to-end acceptance;
- Developer must self-check every acceptance criterion against implementation and tests;
- Reviewer receives complete final authorized candidate files in addition to patch/test evidence;
- Reviewer must distinguish partial/incomplete evidence from absent behavior;
- Reviewer remains independent from the PM contract and still judges the original Product Owner objective;
- no new agent, provider, dependency, repair budget or infrastructure was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #22 was TESTED locally and merged to `main` at `e8a768044ed0e61c2f5619c5d558c2025b0eafa2`.**

## Golden Path rerun after PR #22

Run:

`run-81c1ceb4506c`

Observed result:

- initial candidate changed both authorized files;
- deterministic tests: 4 PASS / 1 ERROR;
- failing test attempted to add two dictionary results directly;
- the single bounded repair was used;
- after repair, previously passing behavior regressed: 2 ERROR + 1 FAIL;
- run stopped in DIAGNOSING with `repair_attempts=1`;
- no `Changes.patch` was produced and semantic review was never reached.

New blocker:

`BOUNDED_REPAIR_REGRESSION_AND_TEST_CONTRACT_DRIFT`

## PR #23 — preserve passing contracts during bounded repair

Branch:

`mvp1-repair-regression-contract`

Runtime/test candidate HEAD validated locally:

`f271b71e60c696018ae15226f6cd4353a2e53791`

PR:

`#23 — MVP-1: preserve passing contracts during bounded repair`

Candidate behavior:

- new/modified tests must use the actual candidate API consistently;
- Support must distinguish production defects from malformed/API-inconsistent tests;
- tests already reported as `ok` become regression constraints;
- repairs must preserve established public return types, keys, call signatures and passing semantics unless the Product Owner objective explicitly requires a breaking change;
- malformed tests may be corrected without weakening acceptance requirements;
- repair rechecks both previously passing and currently failing tests;
- no new agent, provider, dependency, repair-budget increase or infrastructure was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #23 was TESTED locally and merged to `main` at `18a49ab54f90efefabdd5e54c4abeebd962cd35a`.**

## Golden Path rerun after PR #23

Observed failure:

`ValueError: AI Developer proposed a no-op replacement`

Run behavior:

- ForgeLab rejected the candidate before any repository write;
- the no-op safety rule worked correctly;
- the recoverable no-op was raised as generic `ValueError`;
- generic `ValueError` bypassed the existing bounded pre-write recovery;
- the run terminated before implementation/testing/review could continue.

New blocker:

`NOOP_PATCH_BYPASSES_PREWRITE_RECOVERY`

## PR #24 — recover no-op AI patches before write

Branch:

`mvp1-noop-prewrite-recovery`

Runtime/test candidate HEAD validated locally:

`baa0dc1eb43509af733b5d3fcb245b7b717d7947`

PR:

`#24 — MVP-1: recover no-op AI patches before write`

Candidate behavior:

- single-change, composed multi-change, and full-file no-op candidates are classified as `AIDeveloperFormatError`;
- no-op safety rejection remains intact and no no-op is written;
- recoverable no-op output enters the existing single bounded pre-write correction;
- Developer/pre-write prompts explicitly prohibit unchanged replacements and require omitting unchanged files/regions;
- regression coverage proves a no-op first response can be corrected once and execution can continue;
- no new agent, provider, dependency, repair-budget increase or infrastructure was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #24 runtime/test code is TESTED locally; PR #24 is NOT MERGED; Dental Quote has NOT yet been rerun after PR #24.**

## MVP gates

- G1 Usability: materially demonstrated.
- G2 Autonomy: improved but not PASS until the same Dental Quote objective succeeds after PR #24 integration.
- G3 Real output: not yet PASS for the complete three-treatment objective.
- G4 Quality: deterministic tests plus independent semantic blocking are working; PR #24 no-op pre-write recovery is locally TESTED.
- G5 Human control: PASS so far; no candidate or PR is merged/promoted without explicit Product Owner approval.

## Single next action

Review PR #24 and obtain explicit Product Owner approval before merge.

After approved merge, rerun the **same unchanged Dental Quote Golden Path** with the same bounded repair budget. Do not start CRUD/reporting validation until Dental Quote passes.

# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-01
**Checkpoint:** PR #24 locally TESTED / explicit merge approval pending
**Status:** PRE-MVP / Golden Path 1 blocker remediation

## 1. Strategic operating model

ForgeLab is the primary product: a governed multi-agent software factory that should convert a Product Owner objective into usable, tested, reviewed software with minimal Product Owner operational work.

Canonical workflow:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED REPAIR -> REVIEW -> WORKING PREVIEW -> HUMAN APPROVAL -> PROMOTION`

Shared governance:

`AGENTS_MASTER.md v2`

Key operating principle:

`Autonomous within the box; human approval to change the box.`

Current commercial evidence level:

`C0 — Hypothesis`

## 2. Canonical repository

Repository:

`pierluigiavvanzo-creator/forgelab`

Canonical branch:

`main`

Current canonical `main` before PR #24:

`18a49ab54f90efefabdd5e54c4abeebd962cd35a` (merge of PR #23)

Current remediation branch:

`mvp1-noop-prewrite-recovery`

PR:

`#24 — MVP-1: recover no-op AI patches before write`

Runtime/test candidate validated locally:

`baa0dc1eb43509af733b5d3fcb245b7b717d7947`

## 3. Product Owner contract

The Product Owner is:

- strategic decision maker;
- approver at merge/promotion gates;
- final product tester.

Do not routinely use the Product Owner as:

- debugger;
- repetitive QA;
- log transporter;
- retry orchestrator;
- operator of long diagnostic command sequences.

Operating preference remains normal ChatGPT chat plus Windows PowerShell only when necessary; no Work or Codex.

## 4. Golden Path 1 — Dental Quote

Target:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

Objective:

`Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.`

Authorized files:

- `quote_calculator.py`
- `test_quote_calculator.py`

Test command:

`py -3.11 -m unittest discover -v`

Risk:

`normal`

Repair budget:

`1`

## 5. Earlier Golden Path evidence

Run:

`run-6a0c2c512498`

Observed:

- AI Developer generated a bounded two-file candidate;
- one bounded repair was used;
- deterministic tests passed;
- independent semantic Reviewer blocked promotion;
- final candidate still represented a one-treatment workflow;
- automatic subtotals / complete three-treatment behavior and matching tests were not fully evidenced;
- no promotion occurred.

This was a valid product failure, not a Reviewer false positive.

## 6. Root cause

Blocker:

`PROJECT_MANAGER_OUTPUT_NOT_CONSUMED_BY_DEVELOPER`

The Project Manager generated an implementation plan, but the downstream Developer prompt did not consume the plan or its acceptance criteria.

The Reviewer did explicitly decompose the original objective into every obligation, which is why it correctly caught the incomplete result.

## 7. PR #20 remediation

PR #20 introduces the smallest meaningful correction:

`OBJECTIVE -> STRUCTURED PM ACCEPTANCE CONTRACT -> DEVELOPER -> TEST -> INDEPENDENT REVIEW -> BOUNDED REPAIR -> HUMAN GATE`

It:

- makes PM output structured JSON;
- includes `intended_outcome`, `execution_steps`, `acceptance_criteria`, `principal_risks`;
- preserves quantitative requirements;
- prohibits PM scope invention;
- propagates PM acceptance criteria into the Developer task;
- passes the contract to initial generation and repair paths;
- keeps Reviewer independent;
- adds no new agent, provider, dependency, repair budget or broad infrastructure.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 8. Golden Path rerun after PR #20

Run:

`run-c135dcec0887`

Observed:

- deterministic status PASS;
- Developer added aggregate multi-treatment calculation logic;
- tests covered three treatments and percentage-discount calculations;
- Tkinter UI remained one-treatment only;
- aggregate discount remained hard-coded at 10%;
- semantic Reviewer correctly blocked promotion;
- Reviewer wording incorrectly characterized some partial implementation/tests as absent.

Current blocker:

`END_TO_END_ACCEPTANCE_NOT_ENFORCED_AND_REVIEW_EVIDENCE_NOT_GROUNDED`

## 9. PR #22 remediation

PR #22:

- provides complete authorized target files to the Project Manager as bounded read-only planning context;
- requires Developer to wire user-visible behavior through an existing interface/entry point;
- treats helper-only implementation as insufficient for end-to-end acceptance;
- requires Developer self-check against every acceptance criterion;
- provides complete final authorized candidate files to Reviewer;
- requires Reviewer to describe partial evidence precisely rather than falsely calling it absent;
- preserves Reviewer independence from the PM contract;
- adds no agent, provider, dependency, repair-budget increase or infrastructure expansion.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 10. Golden Path rerun after PR #22

Run:

`run-81c1ceb4506c`

Observed:

- initial candidate changed both authorized files;
- first deterministic run: 4 PASS / 1 ERROR;
- failing test attempted to add two dictionary results directly;
- one bounded repair was used;
- after repair, previously passing tests regressed: 2 ERROR + 1 FAIL;
- run ended in DIAGNOSING with `repair_attempts=1`;
- no `Changes.patch` was produced;
- semantic review was never reached.

Current blocker:

`BOUNDED_REPAIR_REGRESSION_AND_TEST_CONTRACT_DRIFT`

## 11. PR #23 remediation

PR #23:

- makes newly-added tests follow the actual candidate API consistently;
- requires Support to distinguish implementation defects from malformed/API-inconsistent tests;
- treats tests already reported as `ok` as regression constraints;
- preserves public return types, dictionary keys, call signatures and passing semantics unless the objective explicitly requires change;
- allows correcting malformed tests without weakening acceptance requirements;
- carries the same constraints into bounded pre-write repair;
- keeps `max repair attempts = 1`;
- adds no agent, provider, dependency or infrastructure.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 12. Golden Path rerun after PR #23

Observed failure:

`ValueError: AI Developer proposed a no-op replacement`

Observed behavior:

- candidate was rejected before repository write;
- no-op safety rule worked;
- generic `ValueError` bypassed bounded pre-write recovery;
- run terminated before the normal implementation/test/review flow.

Current blocker:

`NOOP_PATCH_BYPASSES_PREWRITE_RECOVERY`

## 13. PR #24 remediation

PR #24:

- classifies no-op patch candidates as recoverable `AIDeveloperFormatError`;
- keeps no-op writes prohibited;
- routes no-op responses through the existing one bounded pre-write correction;
- tells Developer to omit unchanged files/regions and never emit a no-op replacement;
- adds regression coverage for successful bounded recovery;
- adds no agent, provider, dependency, repair-budget increase or infrastructure.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 14. Validation evidence

Product Owner local validation reached:

`=== FORGELAB VALIDATION PASS ===`

The checked harness requires:

- clean worktree before tests;
- focused PM -> Developer -> semantic repair contract test PASS;
- two API AI-generate regression tests PASS;
- explicit full Python discovery over `tests/test*.py` PASS;
- full discovery executes more than zero tests;
- clean worktree after tests.

Current evidence classification:

- PR #20: **MERGED** at `c0c7fafb604893840efe22597f1ae18bb4cd32f5`
- PR #22: **MERGED** at `e8a768044ed0e61c2f5619c5d558c2025b0eafa2`
- PR #23: **MERGED** at `18a49ab54f90efefabdd5e54c4abeebd962cd35a`
- PR #24 runtime/test code: **TESTED locally**
- PR #24: **NOT MERGED**
- Dental Quote after PR #24: **NOT YET REAL-WORKFLOW VALIDATED**

## 15. Out of scope until Dental Quote PASS

Do not prioritize:

- multi-tenancy;
- billing;
- advanced scaling;
- deployment expansion;
- paid-provider expansion;
- new agent roles;
- broad observability;
- new configuration frameworks;
- unrelated refactors.

Only a concrete Golden Path blocker may justify additional ForgeLab development.

## 16. Generality proof after Dental Quote PASS

1. Dental Quote — calculator/business logic.
2. Small CRUD SaaS — records/users/workflow.
3. Automation/reporting tool — ingest -> transform -> report.

Do not begin #2 or #3 until #1 passes.

## 17. Current gate

PR #24 is locally TESTED and awaits explicit Product Owner merge approval.

Do not merge, force-update, rebase or promote without explicit approval.

## 18. Single next action

Obtain explicit Product Owner approval for PR #24 merge.

After approved merge:

1. verify exact merged HEAD on `main`;
2. align local ForgeLab checkout;
3. rerun the same unchanged Dental Quote objective;
4. evaluate the real output through deterministic tests and independent semantic review;
5. only after Dental Quote PASS proceed to Golden Path 2.

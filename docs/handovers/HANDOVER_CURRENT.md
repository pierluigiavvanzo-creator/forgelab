# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-01
**Checkpoint:** PR #22 locally TESTED / explicit merge approval pending
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

Current canonical `main` before PR #22:

`c0c7fafb604893840efe22597f1ae18bb4cd32f5` (merge of PR #20)

Current remediation branch:

`mvp1-end-to-end-acceptance-and-review-evidence`

PR:

`#22 — MVP-1: enforce end-to-end acceptance and grounded review`

Runtime/test candidate validated locally:

`0bd8cd2c937eaca93d18ab2b0b2bbfcaf0ec61b4`

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

## 10. Validation evidence

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
- PR #22 runtime/test code: **TESTED locally**
- PR #22: **NOT MERGED**
- Dental Quote after PR #22: **NOT YET REAL-WORKFLOW VALIDATED**

## 11. Out of scope until Dental Quote PASS

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

## 12. Generality proof after Dental Quote PASS

1. Dental Quote — calculator/business logic.
2. Small CRUD SaaS — records/users/workflow.
3. Automation/reporting tool — ingest -> transform -> report.

Do not begin #2 or #3 until #1 passes.

## 13. Current gate

PR #22 is locally TESTED and awaits explicit Product Owner merge approval.

Do not merge, force-update, rebase or promote without explicit approval.

## 14. Single next action

Obtain explicit Product Owner approval for PR #22 merge.

After approved merge:

1. verify exact merged HEAD on `main`;
2. align local ForgeLab checkout;
3. rerun the same unchanged Dental Quote objective;
4. evaluate the real output through deterministic tests and independent semantic review;
5. only after Dental Quote PASS proceed to Golden Path 2.

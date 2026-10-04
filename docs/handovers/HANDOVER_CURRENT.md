# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-04
**Checkpoint:** PR #33 locally TESTED / explicit merge approval pending
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

Current canonical `main` before PR #33:

`fb3188890573e484640b7a4c667c3f4703218685` (merge of PR #32)

Current remediation branch:

`mvp1-semantic-repair-full-file-first`

PR:

`#33 — MVP-1: use full-file semantic repair from first attempt`

Runtime/test candidate validated locally:

`259666e04d118fc8ba4f57a13b12d8b688261e6e`

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

## 14. Golden Path rerun after PR #24

Run:

`run-e83f1cfbebff`

Observed:

- no-op recovery worked and the run continued;
- first deterministic run failed;
- one bounded repair was used;
- second deterministic run passed;
- independent semantic review was reached;
- candidate still lacked an explicit three-treatment GUI workflow;
- no direct test exercised exactly three distinct treatments;
- a test name no longer matched the behavior it exercised;
- discount percentage conversion was inconsistent end-to-end;
- Reviewer blocked promotion but mislabeled existing partial logic as absent.

Current blocker:

`ACCEPTANCE_TEST_TRACEABILITY_GAP_AND_NO_PARTIAL_REVIEW_STATE`

## 15. PR #25 remediation

PR #25:

- adds `PARTIAL` semantic requirement status;
- reserves `MISSING` for genuinely absent evidence;
- requires Reviewer to inspect complete candidate files before claiming absence;
- requires direct tests for each testable acceptance criterion;
- requires direct quantitative tests for quantitative requirements;
- requires semantic alignment among test name, setup, exercised API and assertions;
- carries criterion-coverage constraints into bounded repair;
- requires consistent numeric/unit conversion across boundaries;
- adds no agent, provider, dependency, repair-budget increase or infrastructure.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 16. Golden Path rerun after PR #25

Observed failure:

`AIDeveloperSyntaxError: AI Developer Python candidate does not parse in quote_calculator.py at line 41: unterminated string literal`

Observed behavior:

- invalid Python was rejected before repository write;
- the existing single pre-write correction path was entered;
- snippet-oriented syntax correction could still compose invalid Python;
- a subsequent syntax error escaped the normal governed run lifecycle.

Current blocker:

`EXHAUSTED_PREWRITE_CORRECTION_ESCAPES_RUN_LIFECYCLE`

## 17. PR #26 remediation

PR #26:

- reuses full-file recovery for `AIDeveloperSyntaxError`;
- uses complete current authorized files as authoritative recovery context;
- requires complete syntactically valid Python for changed Python files;
- runs deterministic syntax validation before write;
- applies the same rule to syntax errors inside bounded test-failure repair;
- retains exactly one pre-write correction;
- adds no agent, provider, dependency, repair-budget increase or infrastructure.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 18. Golden Path rerun after PR #26

Run:

`run-0a4726594909`

Observed:

- full-file syntax recovery prevented the prior pre-write crash;
- initial deterministic tests: 4 PASS / 1 ERROR;
- `test_multiple_treatments` failed because it added two dictionary results directly;
- one bounded repair was used;
- repaired run made `test_multiple_treatments` PASS;
- repaired run regressed `test_discount_applied` and `test_single_treatment_total` from PASS to ERROR;
- repair changed established mapping/dictionary behavior into float behavior;
- run ended in DIAGNOSING with repair budget exhausted;
- no patch artifact was produced and semantic review was not reached.

Current blocker:

`PROMPT_ONLY_REGRESSION_CONSTRAINT_NOT_ENFORCED_DETERMINISTICALLY`

## 19. PR #28 remediation

PR #28:

- parses deterministic test outcomes before and after repair;
- turns previously PASS tests into machine-enforced regression constraints;
- emits explicit `repair_regression` evidence;
- rolls back a regressing repair to the exact pre-repair candidate state;
- allows one regression correction inside the same top-level repair attempt;
- uses full-file correction for the authorized subset;
- reruns deterministic tests after correction;
- keeps `max repair attempts = 1`;
- adds no new agent, provider, dependency or infrastructure.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 20. Golden Path rerun after PR #28

Observed failure:

`AIDeveloperSyntaxError: AI Developer Python candidate does not parse in quote_calculator.py at line 43: unterminated string literal`

Observed:

- initial syntax validation blocked invalid Python before write;
- the single full-file syntax recovery was attempted;
- the recovery also produced invalid Python;
- second pre-write validation failure escaped as `run execution failed`;
- no validated candidate reached implementation/testing.

Current blocker:

`PREWRITE_RECOVERY_EXHAUSTION_NOT_GOVERNED`

## 21. PR #29 remediation

PR #29:

- keeps exactly one pre-write correction;
- converts second recoverable pre-write validation failure into `PREWRITE_RECOVERY_EXHAUSTED`;
- emits `PrewriteRecoveryFailure.json`;
- records explicit pre-write validation evidence;
- closes as `CLOSED / Repair required`;
- writes the normal terminal artifacts even without a candidate patch;
- guarantees no repository write on exhausted pre-write recovery;
- applies the same handling to implementation, test-failure repair and semantic-review repair;
- extends semantic syntax recovery to full-file mode;
- adds no new agent, provider, dependency or repair-budget increase.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 22. Golden Path rerun after PR #29

Run:

`run-81f814fa23f5`

Observed:

- PR #29 eliminated the uncaught pre-write lifecycle crash;
- initial deterministic tests passed 5 / 5;
- independent semantic review correctly blocked the incomplete exact three-treatment workflow;
- one semantic-review repair was applied;
- the repair added a direct treatment-validation test;
- deterministic retest failed because the expected `ValueError` was not raised;
- the run stopped in DIAGNOSING with `repair_attempts=1`;
- `Changes.patch` remained stale relative to the semantic repair candidate;
- Reviewer overall FAIL was correct, but its wording understated partial existing treatment/subtotal/final-total implementation.

Current blocker:

`SEMANTIC_REPAIR_TEST_FAILURE_HAS_NO_IN_ATTEMPT_RECOVERY`

## 23. PR #30 remediation

PR #30:

- preserves `max repair attempts = 1`;
- allows one deterministic test correction inside the same semantic-review repair attempt;
- supplies the correction with objective, PM contract, semantic findings, before/after test evidence, and complete current authorized files;
- uses full-file replacement for only the authorized subset;
- validates scope and syntax before write;
- reruns tests after correction;
- re-enters semantic review only after tests pass;
- safely blocks if correction is invalid or retest still fails;
- records `semantic_test_correction_attempts = 1` separately;
- refreshes `Changes.patch` after semantic repair and after correction;
- adds no agent, provider, dependency, infrastructure, or top-level repair-budget increase.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 24. Golden Path rerun after PR #30

Run:

`run-7676d5c968dc`

Observed:

- PR #30 successfully returned a failed semantic repair through deterministic retest and back to independent semantic review;
- initial deterministic tests passed 6 / 6;
- the single semantic-review repair was applied;
- deterministic retest passed 9 / 9;
- `Changes.patch` correctly reflected the semantic repair candidate;
- second semantic review still failed;
- Reviewer overall blocking decision was directionally correct because the exact three-treatment end-to-end workflow remained incomplete;
- Reviewer wording remained partly inaccurate about present-but-incomplete behavior;
- the run stopped in REVIEW with tests PASS and `repair_attempts=1`;
- no further bounded semantic correction existed inside the already-used repair attempt.

Current blocker:

`SEMANTIC_REPAIR_REVIEW_FAILURE_HAS_NO_IN_ATTEMPT_CORRECTION`

## 25. PR #31 remediation

PR #31:

- preserves `max repair attempts = 1`;
- allows one semantic correction inside the same top-level semantic repair when deterministic retest passes but semantic re-review still fails;
- supplies objective, PM contract, latest semantic findings, latest passing tests, complete current authorized files and current diff;
- requires inspection of current files before acting on Reviewer wording;
- uses full-file replacement for only the authorized subset;
- validates scope and syntax before write;
- reruns deterministic tests;
- performs one further independent semantic review only after tests pass;
- safely blocks if correction is invalid, retest fails or final semantic review still fails;
- records `semantic_review_correction_attempts = 1` separately;
- refreshes `Changes.patch` after the correction;
- adds no agent, provider, dependency, infrastructure or top-level repair-budget increase.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 26. Golden Path rerun after PR #31

Observed:

- the unchanged Dental Quote run did not reach product acceptance evaluation;
- local Ollama returned HTTP 500 with `prediction aborted, token repeat limit reached`;
- the configured bounded retry was exhausted;
- the transient provider error escaped the governed run lifecycle as `run execution failed`;
- this is a provider-runtime lifecycle blocker, not evidence that the Dental Quote candidate itself failed acceptance.

Current blocker:

`OLLAMA_REPEAT_LIMIT_RETRY_EXHAUSTION_ESCAPES_RUN_LIFECYCLE`

## 27. PR #32 remediation

PR #32:

- keeps Ollama and provider cost EUR 0;
- keeps the configured retry count unchanged;
- makes the existing retry adaptive only for `token repeat limit reached`;
- preserves the original prompt and response schema while appending a concise anti-loop recovery instruction;
- preserves the existing bounded timeout widening;
- emits `ProviderFailure.json` when the bounded retry is exhausted;
- converts planning-time provider exhaustion into `CLOSED / Repair required` with normal terminal artifacts;
- converts in-run provider exhaustion into the same governed outcome;
- records provider-runtime evidence and usage RETRY/FAIL outcomes;
- adds no paid fallback, extra retry, provider, agent, dependency or infrastructure.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 28. Golden Path rerun after PR #32

Run:

`run-0960eae66316`

Observed:

- PR #32 eliminated the uncaught provider failure path;
- initial deterministic tests passed;
- semantic review returned FAIL/PARTIAL for incomplete three-treatment and automatic-subtotal behavior;
- semantic repair entered REPAIRING;
- the first semantic repair candidate failed deterministic Python syntax validation;
- the one bounded pre-write recovery also failed syntax validation;
- ForgeLab emitted `PrewriteRecoveryFailure.json` and closed as `CLOSED / Repair required`;
- final syntax error was `f-string: unmatched '['`.

Current blocker:

`SEMANTIC_REPAIR_FRAGMENT_SCHEMA_CAUSES_AVOIDABLE_SYNTAX_COMPOSITION_RISK`

## 29. PR #33 remediation

PR #33:

- preserves `max repair attempts = 1`;
- preserves the one bounded pre-write correction;
- starts semantic-review repair directly in full-file schema `2.1`;
- returns complete replacement content only for the authorized changed subset;
- validates complete Python files before write;
- keeps the one bounded pre-write correction in full-file mode;
- removes snippet-specific recovery branching from this semantic-repair path;
- strengthens repair grounding against inaccurate Reviewer wording and incomplete quantitative/user-visible acceptance;
- adds no agent, provider, dependency, retry, infrastructure or top-level repair-budget increase.

Reuse status:

`ADAPT -> INTEGRATED CANDIDATE`

## 30. Validation evidence

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
- PR #24: **MERGED** at `0af0a75b2be4b66ab3da8d26449265c4d0ef8c78`
- PR #25: **MERGED** at `2eaa2f0399b4080e54633357bc9668cd6975e96e`
- PR #26: **MERGED** at `97f25bdb358adaa050735d463000495bafcf0b85`
- PR #27: **MERGED** governance-only update to `AGENTS_MASTER.md`; canonical main advanced to `a3fefabd1a39a3a8d8c20ffd88ccfca5bc732496`
- PR #28: **MERGED** at `718af139078537a29bbb93ed06089f52162f526a`
- PR #29: **MERGED** at `02980f17c6ba85c77c2bd2b00e6ca92cf2aa1f14`
- PR #30: **MERGED** at `081960cb6c0c696567010010dd387a49c6750114`
- PR #31: **MERGED** at `af63c04cf401771499988b30a6c4f45fbef4c8b0`
- PR #32: **MERGED** at `fb3188890573e484640b7a4c667c3f4703218685`
- PR #33 runtime/test code: **TESTED locally** at `259666e04d118fc8ba4f57a13b12d8b688261e6e`
- PR #33: **NOT MERGED**
- Dental Quote after PR #33: **NOT YET REAL-WORKFLOW VALIDATED**

## 31. Out of scope until Dental Quote PASS

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

## 32. Generality proof after Dental Quote PASS

1. Dental Quote — calculator/business logic.
2. Small CRUD SaaS — records/users/workflow.
3. Automation/reporting tool — ingest -> transform -> report.

Do not begin #2 or #3 until #1 passes.

## 33. Current gate

PR #33 is locally TESTED and awaits explicit Product Owner merge approval.

Do not merge, force-update, rebase or promote without explicit approval.

## 34. Single next action

Obtain explicit Product Owner approval for PR #33 merge.

After approved merge:

1. verify exact merged HEAD on `main`;
2. align local ForgeLab checkout;
3. rerun the same unchanged Dental Quote objective;
4. evaluate the real output through deterministic tests and independent semantic review;
5. only after Dental Quote PASS proceed to Golden Path 2.

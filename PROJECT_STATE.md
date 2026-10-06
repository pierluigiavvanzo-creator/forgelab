# PROJECT_STATE.md

**Last updated:** 2026-10-06
**Current phase:** PRE-MVP / MVP Recovery Architecture Reset
**Current priority:** A — Product Critical / restore autonomous dashboard-first Golden Path
**Commercial evidence level:** C0 — Hypothesis

## Canonical source

Repository: `pierluigiavvanzo-creator/forgelab`

Canonical shared truth: `main`

Current canonical `main`: `1fac126023444052623da0c8027cc7209522bbbb` (merge of PR #50 editor bakeoff harness).

PR #18 stabilization was merged previously; later governance updates added `AGENTS_MASTER.md v2` and `MARKETABILITY_CARD.md` on `main`.

## 2026-10-05 MVP recovery architecture reset

Status:

`RUNTIME STACK FROZEN / VALID EMPTY AIDER CONFIG AT HUMAN MERGE GATE`

Audit:

`docs/audits/FORGELAB_MVP_RECOVERY_ARCHITECTURE_AUDIT_2026-10-05.md`

ADR candidate:

`docs/decisions/ADR-002-editor-adapter-boundary.md`

Key findings:

- dashboard/API are real and already support run creation, artifact loading, repair and decisions;
- the recent PowerShell workflow was a developer diagnostic path, not the intended Product Owner experience;
- repeated Product Owner PowerShell reruns violate the autonomy/usability contract;
- runtime PRs #37–#48 are frozen pending architecture reset;
- custom Developer edit/recovery logic has become the dominant instability source;
- `orchestrator.py` concentration and the stacked PR chain create maintainability and source-of-truth risk;
- the next build step is not PR #49-style recovery logic, but an `EditorAdapter` bakeoff.

Reuse decision:

- Aider: `BENCHMARKED -> ADOPTED FOR BOUNDED EXPERIMENT`;
- OpenHands SDK: `BENCHMARKED -> REJECTED FOR CURRENT NARROW EDITOR SWAP`;
- Cline: `BENCHMARKED -> REJECTED FOR CURRENT NARROW EDITOR SWAP`;
- Continue: `BENCHMARKED -> REJECTED` because its current README declares the repository no longer actively maintained.

Immediate technical objective:

`EDITOR_ENGINE_BAKEOFF_01` — harness implemented and focused boundary verification PASS

Compare:

A. merged-main custom ForgeLab editor;  
B. Aider CLI editor adapter in a restricted editor sandbox.

Hold constant:

- Dental Quote baseline/objective;
- `qwen2.5-coder:7b`;
- Planner acceptance contract;
- authorized files;
- deterministic tests;
- Reviewer/Security;
- repair cap;
- EUR 0 provider cost.

PR #50 is merged. The next work is no longer a detached bakeoff: integrate the reusable editor into the real Dental Quote Golden Path while preserving dashboard/API/ToolGateway/test/review/security governance. Binding product metrics are in `docs/experiments/DENTAL_QUOTE_AUTONOMY_GATE.md`.

## 2026-10-06 real Dental dashboard evidence

Observed real dashboard run:

`run-f03a38460154`

Visible outcome:

- status: `CLOSED`;
- gate: `Repair`;
- deterministic tests: `PASS`;
- repair attempts applied: `0`;
- provider cost: `EUR 0`;
- dashboard reports 6 LLM calls / 10004 tokens.

Interpretation:

The product is **not PASS**. Tests succeeded, but the run did not reach
`READY_FOR_DECISION`.

Architecture trace on canonical main shows that the initial Developer edit uses
Aider, while the semantic-review repair path still returns to the old custom
structured/full-file Developer protocol. This is inconsistent with the
REUSE-FIRST reset and is the next proven general blocker.

Current remediation:

`mvp1-aider-semantic-repair`

Scope:

- use Aider for the one bounded semantic-review repair when
  `editor_engine=aider`;
- preserve ToolGateway, deterministic retest, semantic re-review and existing
  repair budget;
- no new recovery catalogue;
- no Dental-specific product logic.

## 2026-10-06 second real Dental dashboard evidence

Observed real dashboard run:

`run-bee503005ab4`

Visible outcome:

- status: `CLOSED`;
- gate: `Repair`;
- deterministic tests: `FAIL`;
- test attempts: `0/1 PASS`;
- repair attempts applied: `0`;
- provider cost: `EUR 0`;
- dashboard reports 6 LLM calls / 15669 tokens.

Interpretation:

The product is **not PASS**. The run failed before any bounded repair was applied.

Code trace on canonical main shows that deterministic test-failure repair still
uses the legacy custom JSON/snippet Developer path even when
`editor_engine=aider`. The smallest general remediation is to keep this
repair on the same reusable Aider editor path.

Current remediation PR:

`#53 — MVP-1: keep failed-test repair on reusable Aider path`

## 2026-10-06 third real Dental dashboard evidence

Observed real dashboard run:

`run-08dcbcbfe1a3`

Visible outcome:

- status: `CLOSED`;
- gate: `Repair`;
- deterministic tests: `FAIL`;
- repair attempts applied: `0`;
- provider cost: `EUR 0`;
- dashboard reports 2 LLM calls / 3599 tokens.

Interpretation:

This is the first real run known to be executed on the locally synchronized
ForgeLab runtime containing PRs #50–#53.

The low LLM-call count plus `TEST FAIL / REPAIR 0` is consistent with:

1. Planner succeeds;
2. Aider initial implementation runs outside the LLM ledger;
3. deterministic tests fail;
4. Support diagnosis runs;
5. Aider test-failure repair is attempted;
6. the repair candidate fails before governed application, so the top-level
   repair counter never increments.

Code inspection confirms the Aider test-failure repair path had no bounded
reusable-editor pre-write correction. A single invalid/no-op repair candidate
therefore closed the run immediately.

Current remediation:

`mvp1-aider-prewrite-correction`

Scope:

- one Aider pre-write correction inside the same failed-test repair attempt;
- correction receives the deterministic validation error;
- no new top-level repair budget;
- no Dental-specific product logic;
- no custom syntax/string recovery catalogue.

## 2026-10-06 fourth real Dental dashboard evidence

Observed synchronized dashboard run:

`run-1df61ea4f109`

Visible outcome:

- status: `CLOSED`;
- gate: `Repair`;
- deterministic tests: `FAIL`;
- repair attempts applied: `0`;
- provider cost: `EUR 0`;
- dashboard reports 2 LLM calls / 3443 tokens.

This run is a valid Dental product FAIL.

However, the current dashboard/API contract does not expose the terminal
failure artifact that explains why the run stopped. In particular,
`PrewriteRecoveryFailure.json` and `ProviderFailure.json` may exist on disk
but are not returned by the artifact API or summarized in Panoramica.

Decision:

Do **not** create another repair-engine remediation from this screenshot alone.

Current remediation is observability only:

`mvp1-dashboard-terminal-blocker-observability`

It must:

- expose terminal failure artifacts through the existing allowlisted API;
- display the current blocking reason, phase and final error in Panoramica;
- link directly to the supporting evidence artifact;
- show the active ForgeLab runtime Git SHA;
- stop showing ForgeLab internal fallback changes when a real target run has
  no applied change-set.

Only a subsequent run with visible terminal evidence may justify another
runtime repair change.

## 2026-10-06 fifth real Dental dashboard evidence

Observed synchronized dashboard run:

`run-f667d5cdf772`

Visible outcome:

- active runner SHA: `a9f3cb7c9511...`;
- status: `CLOSED`;
- gate: `Repair`;
- deterministic tests: `FAIL`;
- repair attempts applied: `0`;
- provider cost: `EUR 0`;
- terminal blocker: `PREWRITE_RECOVERY_EXHAUSTED`;
- blocker phase: `implementation`;
- final error: `quote_calculator.py line 50: f-string: unmatched '['`.

This is the first run where ForgeLab itself exposed the precise terminal blocker
in Panoramica.

Code inspection on the same runtime shows:

1. initial implementation uses Aider;
2. Aider candidate fails deterministic pre-write syntax validation;
3. the initial pre-write recovery still falls back to the legacy custom
   Developer JSON/full-file path;
4. that recovery exhausts and closes the run before tests.

Decision:

Keep REUSE-FIRST. Do not restore the old custom f-string normalizer yet.

Current remediation:

`mvp1-aider-initial-prewrite-correction`

Scope:

- one Aider correction of its own initial candidate;
- correction receives the exact deterministic validation error and failed
  candidate content;
- same authorized files;
- no additional top-level repair budget;
- no Dental-specific logic;
- no regex/string recovery catalogue.

## 2026-10-06 sixth real Dental dashboard evidence

Observed synchronized dashboard run:

`run-160a0cc0cc6a`

Visible outcome:

- active runner SHA: `f09ec5801fb9...`;
- status: `CLOSED`;
- gate: `Repair`;
- deterministic tests: `FAIL`;
- repair attempts applied: `0`;
- provider cost: `EUR 0`;
- terminal blocker: `PREWRITE_RECOVERY_EXHAUSTED`;
- blocker phase: `implementation`;
- final error:
  `Aider initial pre-write correction did not complete successfully: exit=2, timed_out=False`.

Interpretation:

PR #56 is active and the reusable initial pre-write correction is being
attempted. The blocker has moved from malformed Python syntax to a non-zero
Aider process exit during that correction.

Aider 0.86.2 has no explicit normal `return 2` in its one-shot message-file
path; code 2 is consistent with a SystemExit/argument parsing class of failure,
but the exact reason is currently hidden because ForgeLab discards Aider
`stderr` and `stdout` when constructing the terminal error.

Decision:

Do not change editor/retry behavior again from `exit=2` alone.

Current remediation:

`mvp1-aider-failure-output-evidence`

Scope:

- preserve a bounded tail of Aider stderr/stdout in terminal failure evidence;
- apply the same evidence behavior to initial edit, initial pre-write
  correction, failed-test repair and semantic repair;
- no routing/model/retry/product logic change.

## 2026-10-06 seventh real Dental dashboard evidence

Observed synchronized dashboard run:

`run-ebf29be889fe`

Visible outcome:

- active runner SHA: `df32388e1d0b...`;
- status: `CLOSED`;
- gate: `Repair`;
- deterministic tests: `FAIL`;
- repair attempts applied: `0`;
- provider cost: `EUR 0`;
- terminal blocker: `PREWRITE_RECOVERY_EXHAUSTED`;
- blocker phase: `implementation`;
- Aider correction process exit: `2`.

The dashboard now exposes the real Aider stderr:

`The config file doesn't appear to contain 'key: value' pairs ... yaml.load(.../.forgelab-aider.conf.yml) returned type 'NoneType' instead of 'dict'.`

Root cause:

`AiderCliAdapter` creates `.forgelab-aider.conf.yml` as a zero-byte file.
Aider 0.86.2 parses an empty YAML document as `None`, but expects a mapping.

Smallest remediation:

- write a valid empty YAML mapping: `{}\n`;
- keep the existing explicit `--config` isolation boundary;
- no retry/model/provider/repair-budget change;
- no Dental-specific logic.

## Binding Dental autonomy metrics

- `CHATGPT_ASSISTANCE_IN_TARGET_PRODUCT_RUN = 0`;
- `PRODUCT_OWNER_LOG_COPY_ACTIONS = 0`;
- `PRODUCT_OWNER_MANUAL_DEBUG_ACTIONS = 0`;
- `PAID_API_COST_EUR = 0`;
- tests PASS + independent semantic Reviewer PASS + Security PASS;
- source protected until human approval;
- approved Dental Quote must be launchable and usable.

The game is Golden Path #2 and cannot replace or defer Dental Quote.

## Product direction

ForgeLab remains the primary product.

Target workflow:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED REPAIR -> REVIEW -> WORKING PREVIEW -> HUMAN APPROVAL -> PROMOTION`

Provider remains replaceable; current zero-cost local path is Ollama.

Primary product/economic metric:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / PRODUCT OWNER TIME`

## Golden Path sequence

1. Dental Quote — autonomous usable product proof.
2. Playable game — visual/generalization proof.
3. Small CRUD SaaS — records/users/workflow.
4. Automation/reporting tool — ingest -> transform -> report.

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

**PR #24 was TESTED locally and merged to `main` at `0af0a75b2be4b66ab3da8d26449265c4d0ef8c78`.**

## Golden Path rerun after PR #24

Run:

`run-e83f1cfbebff`

Observed result:

- no-op recovery no longer terminated the run;
- initial deterministic tests failed on discount behavior;
- one bounded repair was used;
- deterministic tests then passed;
- run reached independent semantic review;
- Reviewer correctly blocked promotion overall;
- candidate still exposed only one treatment in the GUI;
- no direct test exercised exactly three distinct treatments;
- `test_blank_treatment_rejected` no longer tested a blank treatment name;
- discount percentage conversion was inconsistent across UI/domain boundaries;
- Reviewer incorrectly described existing subtotal/discount/final-total logic as absent rather than incomplete.

New blocker:

`ACCEPTANCE_TEST_TRACEABILITY_GAP_AND_NO_PARTIAL_REVIEW_STATE`

## PR #25 — acceptance-test traceability and partial review evidence

Branch:

`mvp1-acceptance-test-traceability-and-partial-review`

Runtime/test candidate HEAD validated locally:

`f1d23fc0c6588b4400ff5507312031027a15fb23`

PR:

`#25 — MVP-1: trace acceptance tests and represent partial review evidence`

Candidate behavior:

- Reviewer supports `PARTIAL` for present-but-incomplete evidence;
- `MISSING` is reserved for genuinely absent relevant evidence;
- Reviewer must inspect complete candidate files before claiming behavior is absent;
- each deterministically testable acceptance criterion requires direct test evidence;
- quantitative requirements require direct quantitative tests;
- test name, setup, exercised API and assertions must align;
- numeric/unit conversions must remain consistent end-to-end;
- bounded repair must preserve acceptance-test coverage;
- no new agent, provider, dependency, repair-budget increase or infrastructure was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #25 was TESTED locally and merged to `main` at `2eaa2f0399b4080e54633357bc9668cd6975e96e`.**

## Golden Path rerun after PR #25

Observed failure:

`AIDeveloperSyntaxError: AI Developer Python candidate does not parse in quote_calculator.py at line 41: unterminated string literal`

Run behavior:

- deterministic syntax validation correctly blocked invalid Python before repository write;
- the first syntax failure entered the existing single pre-write correction path;
- snippet-oriented syntax recovery could still compose invalid Python;
- a subsequent syntax failure escaped the governed run lifecycle and surfaced as `run execution failed`.

New blocker:

`EXHAUSTED_PREWRITE_CORRECTION_ESCAPES_RUN_LIFECYCLE`

## PR #26 — full-file recovery for Python syntax failures

Branch:

`mvp1-syntax-prewrite-full-file-recovery`

Runtime/test candidate HEAD validated locally:

`8551e5967c429d11d132fa03fd165030b3544ded`

PR:

`#26 — MVP-1: use full-file recovery for Python syntax failures`

Candidate behavior:

- `AIDeveloperSyntaxError` reuses the existing full-file recovery mechanism already used for stale-reference recovery;
- syntax recovery receives complete current authorized files as authoritative context;
- recovery still uses exactly one bounded pre-write correction;
- complete Python replacement content is deterministically parsed before any repository write;
- the same full-file syntax recovery applies inside the bounded test-failure repair path;
- no new agent, provider, dependency, repair-budget increase or infrastructure was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #26 was TESTED locally and merged to `main` at `97f25bdb358adaa050735d463000495bafcf0b85`. PR #27 subsequently changed only `AGENTS_MASTER.md`.**

## Golden Path rerun after PR #26

Run:

`run-0a4726594909`

Observed result:

- syntax recovery no longer terminated the run;
- initial deterministic run produced 4 PASS / 1 ERROR;
- `test_multiple_treatments` failed because two dictionary results were added directly;
- one bounded repair was used;
- after repair, `test_multiple_treatments` passed;
- two tests that were previously PASS regressed to ERROR:
  - `test_discount_applied`;
  - `test_single_treatment_total`;
- the repair changed an established mapping/dictionary return contract into float semantics;
- the run stopped in DIAGNOSING with `repair_attempts=1`;
- no `Changes.patch` was produced and semantic review was not reached.

New blocker:

`PROMPT_ONLY_REGRESSION_CONSTRAINT_NOT_ENFORCED_DETERMINISTICALLY`

## PR #28 — deterministic repair regression gate

Branch:

`mvp1-deterministic-repair-regression-gate`

Runtime/test candidate HEAD validated locally:

`356eef408926e8c97139b2fa3c9c0b18143093d2`

PR:

`#28 — MVP-1: enforce repair regression constraints deterministically`

Candidate behavior:

- deterministic unittest outcomes are parsed before and after bounded repair;
- tests that were PASS before repair become machine-enforced regression constraints;
- if a repair turns a previously PASS test into FAIL/ERROR, ForgeLab records `repair_regression` evidence;
- the regressing repair is rolled back to the exact pre-repair candidate state;
- one bounded regression correction is allowed inside the same top-level repair attempt;
- regression correction uses complete authorized-file replacements to reduce stale-reference/syntax risk;
- `max_repair_attempts` remains unchanged;
- no new agent, provider, dependency or infrastructure was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #28 was TESTED locally and merged to `main` at `718af139078537a29bbb93ed06089f52162f526a`.**

## Golden Path rerun after PR #28

Observed failure:

`AIDeveloperSyntaxError: AI Developer Python candidate does not parse in quote_calculator.py at line 43: unterminated string literal`

Observed behavior:

- the initial invalid Python candidate was rejected before write;
- full-file syntax recovery was attempted once;
- the single bounded recovery also produced invalid Python;
- the second pre-write validation error escaped and surfaced as `run execution failed`;
- no validated candidate reached implementation/testing.

New blocker:

`PREWRITE_RECOVERY_EXHAUSTION_NOT_GOVERNED`

## PR #29 — governed pre-write recovery exhaustion

Branch:

`mvp1-govern-prewrite-recovery-exhaustion`

Runtime/test candidate HEAD validated locally:

`ed6d0587173fc6fce4ed78e717d78275b938387a`

PR:

`#29 — MVP-1: govern exhausted prewrite recovery`

Candidate behavior:

- keeps exactly one bounded pre-write correction;
- if the corrected candidate still fails deterministic pre-write validation, ForgeLab emits `PREWRITE_RECOVERY_EXHAUSTED` instead of raising an uncaught exception;
- emits `PrewriteRecoveryFailure.json` plus normal terminal artifacts;
- records explicit `prewrite_validation` evidence;
- closes the run through the state machine with `CLOSED / Repair required`;
- guarantees no repository write when pre-write recovery is exhausted;
- applies the same terminal handling to initial implementation, test-failure repair, and semantic-review repair;
- semantic syntax recovery reuses full-file recovery;
- no new agent, provider, dependency, or repair-budget increase was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #29 was TESTED locally and merged to `main` at `02980f17c6ba85c77c2bd2b00e6ca92cf2aa1f14`.**

## Golden Path rerun after PR #29

Run:

`run-81f814fa23f5`

Observed result:

- no uncaught pre-write recovery failure occurred; PR #29 behaved as intended;
- initial candidate changed only the two authorized files;
- initial deterministic tests: 5 / 5 PASS;
- independent semantic review correctly blocked overall promotion because the required exact three-treatment end-to-end workflow was incomplete;
- Reviewer wording was partly inaccurate because treatment/subtotal/final-total logic existed but was incomplete rather than absent;
- the single semantic-review repair attempt added a direct treatment-validation test;
- deterministic retest failed because the expected `ValueError` was not raised;
- the run stopped in DIAGNOSING with `repair_attempts=1`;
- the displayed `Changes.patch` still reflected the pre-semantic-repair candidate instead of the current repaired candidate.

New blocker:

`SEMANTIC_REPAIR_TEST_FAILURE_HAS_NO_IN_ATTEMPT_RECOVERY`

## PR #30 — bounded semantic-repair test correction

Branch:

`mvp1-semantic-repair-test-correction`

Runtime/test candidate HEAD validated locally:

`8ca4bdbc744bdebaed004491cd6bd52acc4b90b6`

PR:

`#30 — MVP-1: recover failed semantic repair tests within attempt`

Candidate behavior:

- keeps the single top-level repair attempt unchanged;
- if a semantic-review repair fails deterministic tests, ForgeLab enters DIAGNOSING and allows exactly one correction inside the SAME semantic repair attempt;
- the correction receives the original objective, PM acceptance contract, blocking semantic review, pre-repair passing test evidence, failed post-repair test evidence, and complete current authorized files;
- correction output uses complete-file replacements for only the authorized subset that needs change;
- scope and Python syntax are deterministically validated before write;
- if corrected tests PASS, ForgeLab re-enters semantic review;
- if correction is invalid or corrected tests still FAIL, ForgeLab stops through the governed failure path;
- `max_repair_attempts` remains 1;
- `semantic_test_correction_attempts` is recorded separately;
- `Changes.patch` is refreshed after semantic repair and after in-attempt correction so artifacts match the actual candidate;
- no new agent, provider, dependency or infrastructure was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #30 was TESTED locally and merged to `main` at `081960cb6c0c696567010010dd387a49c6750114`.**

## Golden Path rerun after PR #30

Run:

`run-7676d5c968dc`

Observed result:

- PR #30 behaved as intended: semantic repair ran, deterministic retest completed, and the run returned to independent semantic review;
- initial deterministic tests: 6 / 6 PASS;
- one semantic-review repair was applied;
- deterministic retest after semantic repair: 9 / 9 PASS;
- `Changes.patch` was refreshed after semantic repair and represented the current candidate;
- second semantic review still returned FAIL;
- overall semantic blocking was directionally correct because the exact three-treatment end-to-end workflow remained incomplete;
- Reviewer wording remained partly inaccurate because it described some present-but-incomplete treatment/subtotal/discount behavior as absent;
- the run stopped in REVIEW with tests PASS and `repair_attempts=1`;
- no further bounded semantic correction was available because the single top-level repair attempt was already consumed.

New blocker:

`SEMANTIC_REPAIR_REVIEW_FAILURE_HAS_NO_IN_ATTEMPT_CORRECTION`

## PR #31 — bounded semantic re-review correction

Branch:

`mvp1-semantic-rereview-in-attempt-correction`

Runtime/test candidate HEAD validated locally:

`8595a2c756f1db63b0e9eea9c425d72bbcbf40d4`

PR:

`#31 — MVP-1: correct failed semantic rereview within repair`

Candidate behavior:

- keeps `max_repair_attempts = 1`;
- if the single semantic-review repair passes deterministic tests but the next semantic re-review still FAILS, ForgeLab allows exactly one semantic correction inside the same already-authorized repair attempt;
- the correction receives the original objective, PM acceptance contract, latest semantic re-review, latest passing deterministic evidence, complete current authorized files, and current candidate diff;
- the correction prompt requires the Developer to inspect current files before acting on Reviewer wording and repair the real remaining gap rather than duplicating/deleting existing behavior;
- full-file replacement is required for only the authorized subset that actually needs correction;
- scope and Python syntax are deterministically validated before write;
- deterministic tests are rerun after the correction;
- if tests PASS, ForgeLab performs one further independent semantic review;
- if correction validation fails, tests fail, or the next review still fails, ForgeLab stops through the governed failure path;
- `semantic_review_correction_attempts = 1` is recorded separately from the top-level repair count;
- `Changes.patch` is refreshed after the correction;
- no new agent, provider, dependency, infrastructure or top-level repair-budget increase was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #31 was TESTED locally and merged to `main` at `af63c04cf401771499988b30a6c4f45fbef4c8b0`.**

## Golden Path rerun after PR #31

Observed result:

- ForgeLab started the same unchanged Dental Quote Golden Path;
- execution terminated before product evaluation completed because the local Ollama provider returned HTTP 500 with `prediction aborted, token repeat limit reached`;
- the failure surfaced as uncaught `ProviderTransientError` / `run execution failed`;
- no Dental Quote acceptance result was reached, so this is a provider-runtime lifecycle failure rather than a product failure;
- existing router policy already allowed one bounded retry, but the retry reused the same prompt and exhausted outside the governed run lifecycle.

New blocker:

`OLLAMA_REPEAT_LIMIT_RETRY_EXHAUSTION_ESCAPES_RUN_LIFECYCLE`

## PR #32 — governed Ollama repeat-limit exhaustion

Branch:

`mvp1-govern-ollama-repeat-limit`

Runtime/test candidate HEAD validated locally:

`d57c727379b395ce3f353748d00cd8a191748c9b`

PR:

`#32 — MVP-1: govern Ollama repeat-limit exhaustion`

Candidate behavior:

- keeps Ollama as the zero-cost local provider;
- keeps the configured retry count unchanged;
- if an Ollama transient error contains `token repeat limit reached`, the existing retry becomes adaptive by appending a concise anti-repetition recovery instruction;
- the original prompt and structured response schema are preserved;
- the adaptive retry remains bounded by the existing timeout policy;
- if the retry is exhausted, ForgeLab emits `ProviderFailure.json` with provider, model, task, attempt count, final error and zero-cost evidence;
- planning-time provider exhaustion is converted into a governed `CLOSED / Repair required` run with normal terminal artifacts;
- provider exhaustion after the isolated run begins is likewise converted into a governed terminal outcome;
- no paid fallback, extra retry, new agent, dependency or configuration expansion was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #32 was TESTED locally and merged to `main` at `fb3188890573e484640b7a4c667c3f4703218685`.**

## Golden Path rerun after PR #32

Run:

`run-0960eae66316`

Observed result:

- PR #32 behaved as intended: no provider-runtime crash surfaced;
- initial deterministic tests passed;
- independent semantic review returned FAIL with the main requirement PARTIAL because three treatments and automatic subtotals were still missing;
- semantic repair entered REPAIRING;
- the first semantic repair candidate failed deterministic Python syntax validation;
- the one bounded pre-write recovery also failed syntax validation;
- ForgeLab emitted `PrewriteRecoveryFailure.json` and closed as `CLOSED / Repair required`;
- final reported syntax error: `f-string: unmatched '['`;
- this was a governed repair-generation failure rather than a provider lifecycle failure.

New blocker:

`SEMANTIC_REPAIR_FRAGMENT_SCHEMA_CAUSES_AVOIDABLE_SYNTAX_COMPOSITION_RISK`

## PR #33 — full-file semantic repair from first attempt

Branch:

`mvp1-semantic-repair-full-file-first`

Runtime/test candidate HEAD validated locally:

`259666e04d118fc8ba4f57a13b12d8b688261e6e`

PR:

`#33 — MVP-1: use full-file semantic repair from first attempt`

Candidate behavior:

- keeps `max_repair_attempts = 1`;
- keeps the one bounded pre-write correction unchanged;
- starts the initial semantic-review repair directly in full-file schema `2.1` instead of snippet-based old_text/new_text patch composition;
- returns complete replacement content only for the authorized subset that actually needs change;
- validates complete Python files before any repository write;
- if the initial full-file repair is invalid, the one bounded pre-write correction also remains full-file;
- removes snippet-specific branching from the semantic-repair recovery path;
- strengthens the repair prompt to inspect complete current files, preserve valid existing behavior, avoid duplicating behavior because of inaccurate Reviewer wording, require direct quantitative evidence, and wire user-visible requirements through the existing interface;
- no new agent, provider, dependency, retry, infrastructure, or top-level repair-budget increase was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #33 was TESTED locally and merged to `main` at `dd027196182da4701dafc035806acffd194f125b`.**

## Golden Path rerun after PR #33

Run:

`run-98f2c045a9f3`

Observed result:

- PR #32 governed provider failure correctly: no uncaught `run execution failed`;
- initial deterministic tests passed 5 / 5;
- independent semantic review blocked incomplete three-treatment / automatic-subtotal behavior;
- semantic repair task `review-repair-1` started;
- Ollama returned HTTP 500 `prediction aborted, token repeat limit reached`;
- the existing adaptive generation retry was exhausted;
- ForgeLab emitted `ProviderFailure.json` and closed as `CLOSED / Repair required`;
- no semantic repair candidate was produced, so PR #33 full-file-first behavior was not exercised in the real Golden Path.

New blocker:

`OLLAMA_REPEAT_LIMIT_RETRY_REUSES_LOADED_MODEL_STATE`

## PR #34 — reset Ollama state before repeat-limit retry

Branch:

`mvp1-ollama-repeat-reset-retry`

Runtime/test candidate HEAD validated locally:

`64ce31f1310b73076da74766c93968125c7ea3d7`

PR:

`#34 — MVP-1: reset Ollama state before repeat-limit retry`

Candidate behavior:

- keeps Ollama as the zero-cost local provider;
- keeps the configured generation retry count unchanged;
- keeps the existing anti-repetition adaptive retry prompt;
- before the existing retry for `token repeat limit reached`, requests an Ollama model-state reset/unload through the loopback `/api/generate` endpoint using an empty prompt and `keep_alive: 0`;
- then performs the same one bounded generation retry with the existing widened timeout;
- if the reset control call itself fails, ForgeLab still proceeds with the already-authorized generation retry rather than consuming another retry or crashing;
- ordinary transient retries do not trigger the reset;
- if generation retry still fails, PR #32 governed `ProviderFailure.json` / `CLOSED / Repair required` behavior remains the final stop;
- no paid fallback, extra generation retry, new provider, agent, dependency or configuration expansion was added.

Validation evidence:

`=== FORGELAB VALIDATION PASS ===`

Evidence state:

**PR #34 was merged on 2026-10-04; PR #49 subsequently merged the architecture reset on 2026-10-05. Post-PR34 runtime PRs #37–#48 remain frozen and unmerged.**

## MVP gates

- G1 Usability: materially demonstrated.
- G2 Autonomy: improved but not PASS until the same Dental Quote objective succeeds after PR #34 integration.
- G3 Real output: not yet PASS for the complete three-treatment objective.
- G4 Quality: deterministic syntax validation, governed pre-write exhaustion, deterministic repair regression protection, full-file-first semantic repair, semantic repair test correction, semantic re-review correction, independent semantic blocking, governed provider retry exhaustion, and repeat-limit model-state reset are working; PR #34 is locally TESTED.
- G5 Human control: PASS so far; no candidate or PR is merged/promoted without explicit Product Owner approval.

## Single next action

`HUMAN_REVIEW_EDITOR_ADAPTER_BAKEOFF_HARNESS`

The candidate implements only the isolated editor boundary and deterministic bakeoff harness. It does not integrate Aider into the production Golden Path and does not add Aider as a ForgeLab runtime dependency.

After explicit merge approval, the next development phase is the real bounded Aider/Ollama boundary experiment. No Product Owner PowerShell debug loop is authorized.

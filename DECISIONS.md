# DECISIONS.md

## D-001 — Product before infrastructure

**Date:** 2026-09-22
**Status:** Accepted

ForgeLab development is frozen at the infrastructure layer unless a real MVP test exposes a concrete product blocker.

Reason: the project has accumulated substantial technical capability, but usable product value must now be demonstrated through a real external-application workflow.

---

## D-002 — MVP status

**Date:** 2026-09-22
**Status:** Accepted

ForgeLab is classified as:

**PRE-MVP / technically capable**

It must not be called MVP-complete until all five MVP gates pass on a real external application:

1. usability;
2. autonomy;
3. real output;
4. quality;
5. human control.

---

## D-003 — Product Owner role

**Date:** 2026-09-22
**Status:** Accepted

The Product Owner is approver and final usability tester.

Routine use must not require the Product Owner to act as repetitive QA, debugger, log transporter, retry orchestrator or executor of long micro-command sequences.

---

## D-004 — Canonical M8.9 baseline

**Date:** 2026-09-22
**Status:** Accepted

The validated ForgeLab M8.9 baseline is:

- commit `58d22eeca66c27871738c04c6d850c59efabf115`
- tree `63b6c91427edb19cd038cf557904451dfc08a947`
- 168 tracked canonical files
- canonical manifest SHA-256 `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3`

This record documents the validated source state at M8.9 acceptance.

---

## D-005 — Initial GitHub repository role

**Date:** 2026-09-22
**Status:** Superseded by D-007

The repository `pierluigiavvanzo-creator/forgelab` was initially established as shared remote project/governance memory before the full validated source was synchronized.

This decision is preserved as historical context and is superseded by D-007 after successful source synchronization and local alignment.

---

## D-006 — Repository-first

**Date:** 2026-09-22
**Status:** Accepted

Before substantial custom development, evaluate mature reuse candidates when reuse could materially reduce time, cost or risk.

Track candidates through:

`DISCOVERED -> BENCHMARKED -> ADOPTED | REJECTED -> INTEGRATED -> USED`

Discovery alone does not count as reuse.

This rule must not become an excuse to delay MVP validation when the current system can already perform the required product test.

---

## D-007 — GitHub main is canonical shared source of truth

**Date:** 2026-09-22
**Status:** Accepted

The validated M8.9 source baseline was published to `baseline/m8.9-local`, integrated with canonical governance on `integration/m8.9-code-plus-governance`, and merged through PR #2.

PR #2 merge commit:

`9560729bfc9f27422d92d20d8fb43db5886a1cba`

Decision:

- GitHub `pierluigiavvanzo-creator/forgelab` on `main` is the canonical shared source of truth for ForgeLab code and governance;
- the local checkout tracks that history;
- no force or rebase is used for synchronization;
- future material changes continue to follow governed branch/review/approval discipline.

---

## D-008 — ForgeLab is the primary software factory; Golden Path outranks infrastructure

**Date:** 2026-09-30
**Status:** Accepted

ForgeLab is the primary product: a provider-replaceable software/product creation platform that must own the workflow from Product Owner objective through planning, implementation, deterministic verification, bounded repair, independent review, working preview and explicit human promotion.

Decision:

- do not use ChatGPT chat as ForgeLab's orchestration layer;
- prefer the local zero-cost Ollama path where practical while keeping the provider replaceable;
- prioritize product-level Golden Path failures over generic infrastructure or refactor work;
- after Dental Quote PASS, validate generality on a small CRUD SaaS and an automation/reporting tool;
- defer multi-tenancy, billing, advanced scaling, broad observability, paid-provider expansion and unrelated architecture work until product evidence requires them;
- preserve explicit Product Owner approval before promotion.

Rationale:

The primary risk is no longer lack of infrastructure. It is failure to convert an objective into a genuinely usable software product with low Product Owner effort.

---

## D-009 — Project Manager acceptance contract must govern implementation

**Date:** 2026-10-01
**Status:** Accepted — PR #20 merged 2026-10-01

Evidence:

Dental Quote run `run-6a0c2c512498` passed deterministic tests after a bounded repair but failed independent semantic review because the generated application did not satisfy the complete three-treatment objective.

Root cause:

The Project Manager produced a plan, but the Developer did not consume that plan or its acceptance criteria before implementation.

Decision candidate:

- Project Manager output must be structured, not advisory free text;
- explicit Product Owner obligations must be decomposed into binding `acceptance_criteria`;
- quantitative requirements such as exact counts, "three", "each", "all", percentages and limits must be preserved;
- the Project Manager must not invent new product scope;
- Developer and bounded repair paths must consume the same acceptance contract;
- independent Reviewer must continue evaluating the original Product Owner objective rather than inheriting the PM contract as truth;
- existing isolation, ToolGateway, test, repair-budget and human-promotion controls remain unchanged.

Rationale:

A multi-agent plan that is stored but not consumed does not govern execution. Propagating the acceptance contract closes that gap without adding agents, dependencies or infrastructure.


---

## D-010 — End-to-end acceptance and grounded reviewer evidence

**Date:** 2026-10-01
**Status:** Accepted — PR #22 merged 2026-10-01

Evidence:

Dental Quote rerun `run-c135dcec0887` after PR #20 showed that structured PM acceptance criteria materially improved Developer output, but the generated application still stopped at helper/backend coverage while the existing Tkinter interface remained a one-treatment workflow. The Reviewer blocked promotion correctly, yet described present-but-incomplete implementation/tests as absent.

Decision candidate:

- Project Manager may inspect the complete authorized target files as bounded read-only planning context;
- when an existing user-facing interface or entry point is inside authorized scope, Developer must wire user-visible requirements through it;
- helper/backend functions alone do not satisfy an end-to-end user-visible requirement;
- Developer must self-check every acceptance criterion against implementation and tests before returning;
- Reviewer must inspect complete final authorized candidate files in addition to patch and deterministic test evidence;
- Reviewer must distinguish absent behavior from partially implemented or insufficiently evidenced behavior;
- Reviewer remains independent and continues to judge the original Product Owner objective rather than inheriting PM conclusions;
- existing isolation, ToolGateway, repair budget, deterministic test gate and human promotion gate remain unchanged.

Rationale:

The next product risk is not planning availability but incomplete vertical-slice execution and imprecise semantic evidence. The smallest safe correction is to make planning file-aware, implementation explicitly end-to-end, and review grounded in the complete candidate state.


---

## D-011 — Bounded repair must preserve passing contracts

**Date:** 2026-10-01
**Status:** Accepted — PR #23 merged 2026-10-01

Evidence:

Dental Quote run `run-81c1ceb4506c` after PR #22 produced an initial candidate with 4 passing tests and 1 error. The single bounded repair then broke behavior exercised by tests that had already passed, ending with 2 errors and 1 failure and stopping before semantic review.

Root cause:

`BOUNDED_REPAIR_REGRESSION_AND_TEST_CONTRACT_DRIFT`

Decision candidate:

- tests reported as passing in the failed deterministic run become regression constraints for the repair;
- Support must distinguish production-code defects from malformed or API-inconsistent newly-added tests;
- Developer repair must preserve established public return types, dictionary keys, call signatures and already-passing semantics unless the Product Owner objective explicitly requires a breaking change;
- a malformed test may be corrected when inconsistent with the intended API/objective, but acceptance requirements must not be weakened merely to obtain green tests;
- initial Developer output must keep new/modified tests consistent with the candidate API it creates;
- the repair budget remains unchanged.

Rationale:

A bounded repair that fixes one failing assertion by breaking previously green behavior is not a valid repair. The smallest safe improvement is to make existing green behavior an explicit contract during diagnosis and repair.


---

## D-012 — Recoverable no-op patches use bounded pre-write correction

**Date:** 2026-10-01
**Status:** Accepted — PR #24 merged 2026-10-02

Evidence:

A fresh Dental Quote run after PR #23 terminated before write with `ValueError: AI Developer proposed a no-op replacement`.

Root cause:

`NOOP_PATCH_BYPASSES_PREWRITE_RECOVERY`

Decision candidate:

- no-op replacements remain invalid and must never be written;
- single-change, composed multi-change and full-file no-op candidates are classified as `AIDeveloperFormatError`;
- recoverable no-op output is routed through the existing one bounded pre-write correction;
- Developer prompts explicitly prohibit `old_text == new_text` and require unchanged files/regions to be omitted;
- no repair-budget increase, new agent, provider or dependency is introduced.

Rationale:

A safe deterministic rejection should not terminate the entire run when the failure is a recoverable response-format defect and ForgeLab already has a bounded pre-write correction mechanism for that class of error.


---

## D-013 — Acceptance criteria require direct test traceability; partial evidence must remain partial

**Date:** 2026-10-02
**Status:** Accepted — PR #25 merged 2026-10-02

Evidence:

Dental Quote run `run-e83f1cfbebff` reached deterministic PASS after one bounded repair and then failed semantic review. The candidate still lacked the complete three-treatment user workflow and direct three-treatment test coverage. Some test names no longer matched the behavior exercised, and percentage conversion was inconsistent across UI/domain boundaries. Reviewer blocking was appropriate, but existing subtotal/discount/final-total logic was described as absent rather than incomplete.

Root cause:

`ACCEPTANCE_TEST_TRACEABILITY_GAP_AND_NO_PARTIAL_REVIEW_STATE`

Decision candidate:

- every deterministically testable acceptance criterion requires at least one direct test whose setup, exercised API and assertions prove that criterion;
- exact quantitative requirements require direct quantitative evidence using the required distinct inputs/items;
- test names must remain semantically aligned with setup and assertions;
- bounded repair must preserve coverage for all binding criteria rather than trading one criterion for another;
- user-facing numeric/unit conversions must be applied consistently at one boundary;
- Reviewer requirement status adds `PARTIAL`;
- `PARTIAL` is used when relevant implementation/tests exist but do not satisfy the complete requirement;
- `MISSING` is reserved for genuinely absent relevant evidence.

Rationale:

Green tests are insufficient when the tests do not trace to the Product Owner's actual acceptance criteria, and review evidence must distinguish incomplete implementation from absent implementation.


---

## D-014 — Python syntax failures use full-file bounded pre-write recovery

**Date:** 2026-10-02
**Status:** Accepted — PR #26 merged 2026-10-02

Evidence:

A fresh Dental Quote run after PR #25 was blocked before write with `AIDeveloperSyntaxError` caused by an unterminated string literal in `quote_calculator.py`. Initial syntax validation worked, but snippet-oriented correction could still produce syntactically invalid composed Python.

Root cause:

`EXHAUSTED_PREWRITE_CORRECTION_ESCAPES_RUN_LIFECYCLE`

Decision candidate:

- `AIDeveloperSyntaxError` uses the existing full-file recovery mechanism already used for stale-reference recovery;
- recovery receives complete authorized current files as authoritative context;
- only authorized files that actually need changes may be returned;
- complete Python replacement content must pass deterministic syntax parsing before any write;
- the same recovery rule applies inside the bounded test-failure repair path;
- exactly one bounded pre-write correction remains allowed;
- no repair-budget increase, new provider, agent or dependency is introduced.

Rationale:

When syntax failure is caused by composing partial text fragments, retrying with the same fragment format unnecessarily repeats the failure mode. Full-file recovery reduces ambiguity while preserving scope, deterministic validation and the existing single-attempt bound.


---

## D-015 — Previously passing tests are deterministic repair constraints

**Date:** 2026-10-02
**Status:** Accepted — PR #28 merged 2026-10-02

Evidence:

Dental Quote run `run-0a4726594909` after PR #26 produced an initial deterministic result of 4 PASS / 1 ERROR. The single bounded repair fixed the originally failing `test_multiple_treatments` but regressed `test_discount_applied` and `test_single_treatment_total`, changing established dictionary-return semantics into float-return semantics.

Root cause:

`PROMPT_ONLY_REGRESSION_CONSTRAINT_NOT_ENFORCED_DETERMINISTICALLY`

Decision candidate:

- parse deterministic unittest outcomes before and after bounded repair;
- tests reported PASS before repair become machine-enforced regression constraints;
- if a repair turns a previously PASS test into FAIL/ERROR, record explicit `repair_regression` evidence;
- rollback the regressing repair to the exact pre-repair candidate state;
- allow one regression correction inside the same top-level repair attempt;
- regression correction must receive both original failure evidence and regression evidence;
- use complete authorized-file replacement for the regression correction to reduce stale-reference and syntax-composition risk;
- `max_repair_attempts` remains unchanged;
- if the bounded correction still fails, stop through the governed failure path.

Rationale:

A prompt-level instruction is not a reliable safety/control boundary when a local model can ignore it. Previously passing deterministic behavior must be enforced by orchestration logic rather than model compliance alone.


---

## D-016 — Exhausted pre-write recovery is a governed terminal outcome

**Date:** 2026-10-04
**Status:** Accepted — PR #29 merged 2026-10-04

Evidence:

A fresh Dental Quote run after PR #28 produced an invalid Python candidate. ForgeLab correctly attempted the single full-file syntax recovery, but that recovery also produced invalid Python. The second deterministic pre-write validation error escaped as `run execution failed`.

Root cause:

`PREWRITE_RECOVERY_EXHAUSTION_NOT_GOVERNED`

Decision candidate:

- preserve exactly one bounded pre-write correction;
- if the corrected candidate still fails with a recoverable format/reference/syntax error, do not request another model attempt;
- emit `PrewriteRecoveryFailure.json` with first error, final error, phase and confirmation that no repository write occurred;
- emit explicit `prewrite_validation` evidence;
- close the run through the normal state machine as `CLOSED / Repair required`;
- still emit the normal terminal run artifacts;
- emit no `Changes.patch` when no validated candidate was written;
- apply the same exhaustion handling to initial implementation, test-failure repair and semantic-review repair;
- semantic syntax recovery uses the same full-file recovery strategy as other syntax-recovery paths;
- no repair-budget increase is introduced.

Rationale:

Exhausting a bounded recovery is an expected governed failure mode, not an exceptional runtime crash. The system must preserve evidence, source integrity and a clear human decision state even when the local model cannot produce a valid candidate.


---

## D-017 — Semantic-review repair gets one bounded deterministic test correction inside the same repair attempt

**Date:** 2026-10-04
**Status:** Accepted — PR #30 merged 2026-10-04

Evidence:

Dental Quote run `run-81f814fa23f5` after PR #29 passed all initial deterministic tests, then correctly failed independent semantic review because the exact three-treatment workflow was incomplete. The single semantic-review repair introduced a direct treatment-validation test, but deterministic retest failed and the run stopped in DIAGNOSING with the top-level repair budget exhausted.

Root cause:

`SEMANTIC_REPAIR_TEST_FAILURE_HAS_NO_IN_ATTEMPT_RECOVERY`

Decision candidate:

- keep `max_repair_attempts = 1`;
- when the single semantic-review repair fails deterministic tests, allow exactly one correction inside that same repair attempt;
- correction receives the original objective, binding acceptance contract, blocking semantic review, pre-repair passing evidence, failed post-repair evidence, and complete current authorized files;
- use complete-file replacement for only the authorized subset that needs correction;
- deterministically validate scope and Python syntax before write;
- rerun deterministic tests after correction;
- if tests pass, re-enter independent semantic review;
- if correction validation fails or corrected tests still fail, stop through the governed failure path;
- record the internal correction separately as `semantic_test_correction_attempts = 1`;
- refresh `Changes.patch` after semantic repair and correction so artifacts represent the actual current candidate;
- do not add agents, providers, dependencies, infrastructure, or top-level repair attempts.

Rationale:

A semantic-review repair is already the one authorized repair attempt. If that repair introduces a directly observable deterministic defect, one bounded internal correction improves autonomy without silently expanding the Product Owner-approved repair budget.


---

## D-018 — Failed semantic re-review gets one bounded correction inside the same repair attempt

**Date:** 2026-10-04
**Status:** Proposed in PR #31; becomes Accepted only if PR #31 is explicitly approved and merged

Evidence:

Dental Quote run `run-7676d5c968dc` after PR #30 passed the initial deterministic suite, used the single semantic-review repair, passed deterministic retest 9 / 9, and then failed the second independent semantic review because the exact three-treatment end-to-end workflow was still incomplete. The run stopped in REVIEW because the single top-level repair budget had already been consumed.

Root cause:

`SEMANTIC_REPAIR_REVIEW_FAILURE_HAS_NO_IN_ATTEMPT_CORRECTION`

Decision candidate:

- keep `max_repair_attempts = 1`;
- when the single semantic-review repair passes deterministic tests but the next independent semantic review still fails, allow exactly one semantic correction inside the same already-authorized repair attempt;
- correction receives the original objective, binding acceptance contract, latest semantic review, latest passing deterministic evidence, complete current authorized files, and current full candidate diff;
- correction must inspect complete current files before acting on Reviewer wording and must preserve existing valid behavior;
- use complete-file replacement for only the authorized subset that needs correction;
- deterministically validate scope and Python syntax before write;
- rerun deterministic tests;
- if tests pass, perform one further independent semantic review;
- if correction validation fails, corrected tests fail, or the next review still fails, stop through the governed failure path;
- record `semantic_review_correction_attempts = 1` separately from the top-level repair count;
- refresh `Changes.patch` after the correction;
- do not add agents, providers, dependencies, infrastructure, or top-level repair attempts.

Rationale:

A deterministically green semantic repair can still be semantically incomplete. One bounded correction inside that already-authorized repair reduces Product Owner debugging burden without expanding the explicit repair budget or weakening independent review.

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
**Status:** Accepted — PR #31 merged 2026-10-04

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


---

## D-019 — Exhausted local-provider transient retries are governed run outcomes

**Date:** 2026-10-04
**Status:** Accepted — PR #32 merged 2026-10-04

Evidence:

A fresh unchanged Dental Quote run after PR #31 terminated with `ProviderTransientError: Ollama HTTP 500: {"error":"prediction aborted, token repeat limit reached"}`. ForgeLab already classified the HTTP 5xx as transient and allowed one configured retry, but the retry reused the same prompt. When the retry also failed, the exception escaped as `run execution failed`.

Root cause:

`OLLAMA_REPEAT_LIMIT_RETRY_EXHAUSTION_ESCAPES_RUN_LIFECYCLE`

Decision candidate:

- keep Ollama as the zero-cost local provider;
- keep the configured retry count unchanged;
- when the prior Ollama transient error contains `token repeat limit reached`, make the existing retry adaptive by appending a concise anti-repetition instruction;
- preserve the original prompt, structured response schema and bounded timeout policy;
- if the bounded retry still fails, emit `ProviderFailure.json` with provider/model/task/attempt/final-error/cost evidence;
- convert both planning-time and in-run provider retry exhaustion into a governed `CLOSED / Repair required` outcome with normal terminal artifacts;
- do not add paid fallback, extra retries, providers, agents, dependencies or infrastructure.

Rationale:

A local-provider generation abort is an expected runtime failure mode. It should either recover within the already-authorized retry or end with explicit artifacts and state, never as an uncaught runtime exception that turns the Product Owner into the retry operator.


---

## D-020 — Semantic-review repair uses full-file replacement from the first attempt

**Date:** 2026-10-04
**Status:** Accepted — PR #33 merged 2026-10-04

Evidence:

Dental Quote run `run-0960eae66316` after PR #32 passed the initial deterministic suite and reached semantic repair. The initial semantic repair used snippet composition, failed Python syntax validation, and then consumed its one full-file pre-write recovery, which also failed with `f-string: unmatched '['`. ForgeLab closed correctly with `PrewriteRecoveryFailure.json`.

Root cause:

`SEMANTIC_REPAIR_FRAGMENT_SCHEMA_CAUSES_AVOIDABLE_SYNTAX_COMPOSITION_RISK`

Decision candidate:

- keep `max_repair_attempts = 1`;
- keep the one bounded pre-write correction;
- make the first semantic-review repair use full-file schema `2.1`;
- return complete replacement content only for the authorized subset that actually needs change;
- validate complete Python files before write;
- keep the one bounded pre-write correction in full-file mode;
- remove snippet-specific branching from this semantic-repair recovery path;
- require the repair to inspect complete current files, preserve valid existing behavior, avoid duplicating present behavior because of Reviewer wording, preserve direct tests, and satisfy quantitative/user-visible acceptance end-to-end;
- do not add agents, providers, dependencies, retries, infrastructure, or top-level repair attempts.

Rationale:

The semantic repair already has complete current authorized files available. Generating complete changed files directly avoids fragile old_text/new_text composition and reduces avoidable syntax/reference failure without expanding the authorized repair budget.


---

## D-021 — Reset local Ollama model state before the existing repeat-limit retry

**Date:** 2026-10-04
**Status:** Accepted — PR #34 merged 2026-10-04 at `5f83844a36063722c2979dae19576d57c0f06c5a`

Evidence:

Dental Quote run `run-98f2c045a9f3` after PR #33 passed initial deterministic tests and reached semantic repair, but task `review-repair-1` exhausted the existing adaptive Ollama retry with `prediction aborted, token repeat limit reached`. PR #32 correctly governed the failure with `ProviderFailure.json`, but no semantic repair candidate was produced, so PR #33 full-file repair behavior was not exercised.

Root cause:

`OLLAMA_REPEAT_LIMIT_RETRY_REUSES_LOADED_MODEL_STATE`

Decision candidate:

- keep Ollama as the zero-cost local provider;
- keep the configured generation retry count unchanged;
- keep the existing anti-repetition retry prompt;
- before the existing retry for `token repeat limit reached`, request a local model unload/reset through Ollama `/api/generate` using the same model, an empty prompt, `stream: false`, and `keep_alive: 0`;
- then perform the same one bounded generation retry with the existing widened timeout;
- if the reset control call fails, still proceed with the existing generation retry and do not add another retry;
- ordinary transient retries must not trigger repeat-limit reset;
- if generation still fails, preserve the existing governed provider-failure terminal path;
- do not add paid fallback, providers, agents, dependencies, configuration expansion, or generation retries.

Rationale:

The provider already exposes a local unload/reset capability. Reusing that capability before the same authorized retry is lower-cost and more bounded than adding retries, paid fallback, or new infrastructure, while targeting the observed repeat-limit failure mode directly.


---

## D-022 — MVP recovery architecture reset and reusable editor boundary

**Date:** 2026-10-05
**Status:** Proposed — architecture audit candidate

Evidence:

After PR #34, Dental Quote debugging continued through a long stacked runtime chain (#37–#48). The chain improved governed failure handling, but repeated real runs continued to fail on custom LLM edit-contract behavior: exact-source references, structured schema adherence, full-file regeneration, Python quoting/f-strings and related pre-write recovery cases.

At the same time:

- Product Owner manual PowerShell touches increased;
- canonical `main` remained behind the active runtime experiments;
- `orchestrator.py` accumulated hundreds of additional lines of recovery logic;
- the dashboard, despite already supporting real API run/create/repair/decision flows, was bypassed during ordinary MVP validation;
- repository-first benchmarking had not been completed for the narrow code-editing engine problem.

Root cause:

`CUSTOM_LLM_EDIT_PROTOCOL_IS_BECOMING_THE_PRODUCT_BOTTLENECK`

Decision candidate:

- freeze runtime PRs #37–#48 and stop extending their special-case recovery chain;
- keep ForgeLab as the control plane;
- preserve dashboard, API, planner acceptance contract, isolated workspace, ToolGateway, deterministic tests, Reviewer, Security, usage evidence and human promotion gate;
- introduce an explicit `EditorAdapter` boundary;
- benchmark Aider as the first reusable code-editing engine through a bounded CLI adapter;
- run the external editor in a restricted editor sandbox and preserve ToolGateway as the authoritative apply boundary;
- compare the current editor and Aider using the same Dental Quote baseline, objective, local model, tests, Reviewer and repair cap;
- do not change the model in phase 1 so the experiment isolates the editor engine;
- do not add a paid API without explicit Product Owner approval;
- after the bakeoff, rebuild only the generally necessary runtime behavior on a fresh branch from canonical `main`;
- restore dashboard-first Golden Path validation before declaring MVP progress.

Rationale:

ForgeLab's differentiating asset is governed software production, not custom parsing of every possible malformed model edit. Reusing a mature editor engine behind a narrow adapter can reduce model-output fragility while retaining ForgeLab's governance and lowering Product Owner time.


---

## D-023 — Dental Quote remains the first autonomous product proof

**Date:** 2026-10-06
**Status:** Proposed — pending integration PR approval
**Class:** A — Product Critical

Decision:

- Dental Quote remains Golden Path #1 and must not be replaced or deferred by the playable-game proof.
- The playable game becomes Golden Path #2 and starts only after Dental Quote product PASS.
- ChatGPT may develop ForgeLab, but target-product execution must record `CHATGPT_ASSISTANCE_IN_TARGET_PRODUCT_RUN = 0`.
- A Dental Quote run requiring ChatGPT-authored target-code correction is FAIL.
- The merged `EditorAdapter` boundary is integrated into the real dashboard Golden Path using Aider as the initial Developer editor.
- Aider is a reused editing component, not the ForgeLab control plane.
- ForgeLab retains Planner acceptance contract, authorized scope, ToolGateway, deterministic tests, independent Reviewer, Security and human promotion gate.
- Existing repair governance remains bounded and internal to ForgeLab; any fallback away from Aider must be recorded explicitly.
- No paid provider fallback is authorized.
- Test count is not a product KPI.
- Dental Quote is PASS only after a dashboard-initiated run reaches decision-ready evidence, receives explicit human approval, and the promoted application is visibly launchable and usable.

Binding autonomy/cost metrics:

- `CHATGPT_ASSISTANCE_IN_TARGET_PRODUCT_RUN = 0`
- `PRODUCT_OWNER_LOG_COPY_ACTIONS = 0`
- `PRODUCT_OWNER_MANUAL_DEBUG_ACTIONS = 0`
- `PRODUCT_OWNER_RUN_SUBMISSIONS = 1`
- `PAID_API_COST_EUR = 0`

Rationale:

ForgeLab must prove that it can transform a Product Owner objective into a usable product with low Product Owner time. Dental Quote is the existing unresolved proof and therefore remains the priority. A second product category is useful only after the first product is actually delivered.


---

## D-024 — Stabilize Aider as a complete reusable component before another Dental run

**Date:** 2026-10-07
**Status:** Accepted — PR #64 merged at `6d55b5587bf44a7efbcc0a81090ba5b6a7bdc98d`; local execution gate remains evidence-dependent
**Class:** A — Product Critical

Evidence:

PR #60–#63 and the associated real Dental runs exposed multiple symptoms of one incomplete Aider integration contract: cross-phase timeout coupling, incorrect editor-result lifecycle handling, tool-home/workspace collision and CWD-relative Aider history.

Continuing with one Dental run per integration edge transfers QA cost to the Product Owner and conflicts with the Golden Path autonomy objective.

Decision:

- stop real Dental reruns until the Aider component passes a focused internal stabilization gate;
- consolidate hardening in one PR (#64), not a sequence of symptom-specific PRs;
- preserve Aider as a reused component behind ForgeLab's control plane;
- centralize all Aider process/error handling in one orchestrator boundary;
- make the Aider subprocess deterministic and non-interactive through explicit 0.86.2 CLI flags;
- isolate product workspace, tool state, history, model metadata and environment;
- inherit only a minimal safe set of process environment variables;
- require loopback-only Ollama;
- add best-effort proxy-based external HTTP egress suppression, while explicitly recording that this is not OS-level network isolation;
- keep source scope strict and ToolGateway authoritative;
- preserve generic timeout and editor timeout as separate bounded contracts;
- fingerprint transitive Aider dependencies rather than inventing an unverified lockfile in this PR;
- make top-level long-running runs asynchronous and observable with one-active-run boundedness and durable status;
- make `Start-ForgeLab.ps1` execute the focused stabilization test set before normal runtime startup;
- prohibit another Dental Golden Path run unless the launcher gate passes;
- keep paid API cost EUR 0, ChatGPT target-run assistance 0 and human promotion gating unchanged.

Rationale:

The economic/product objective is to reduce Product Owner time while increasing usable output reliability. Testing foreseeable reusable-editor integration failures internally is higher-value than repeatedly using the Dental product proof as the integration test harness.

Residual risk accepted for this gate:

- subprocess HTTP proxy control is best-effort and is not an OS firewall;
- transitive Aider dependencies are observable through a frozen snapshot/fingerprint but are not yet fully locked.

These residuals must not be silently upgraded to stronger guarantees in product evidence.

---

## D-025 — Correct demonstrated asynchronous lifecycle gaps after PR #64

**Date:** 2026-10-08
**Status:** Accepted and merged via PR #65 at `2227c2487b8858738db7bcf38cdcebeff4699c4f`
**Class:** A — Product Critical

The 90 existing focused tests pass on Windows/Python 3.11.9. New executable regressions demonstrate queue-reservation leakage after a failed status write, inconsistent summary/status observations, corrupt-status worker failure, repair concurrency bypass, lost browser-refresh connection, and missing terminal failure evidence in the dashboard.

Use the existing local run slot for repair/decision exclusion; keep run status/list/artifacts coherent without treating a partially written summary as worker completion; retain connection credentials only in tab-scoped session storage; load evidence for all terminal states. Move dashboard form/artifact state updates to their originating events to resolve the executed lint failures. Add the behavioral dashboard regression gate to the launcher.

Do not alter Aider, Dental target code, providers, repair budgets, ToolGateway or the human promotion gate. One branch and one PR; no auto-merge. Full evidence: [docs/audits/FORGELAB_POST_PR64_VERIFICATION_2026-10-08.md](docs/audits/FORGELAB_POST_PR64_VERIFICATION_2026-10-08.md). Original D-024 residual risks remain unchanged. PRE-MVP / C0 remains the product/commercial state.

---

## Windows Aider process encoding and non-interactive failure — 2026-10-08

**Status:** Merged via PR #66 at `d9f6d2faa6fa776244f96a2be1df9d296d76d1f2`
**Class:** A — Product Critical

Canonical main independently reproduces the observed U+FEFF/cp1252 failure with Aider 0.86.2. Its crash handler calls built-in input outside the normal yes-always CLI policy, so inherited interactive stdin can turn a crash into timeout 124.

Force PYTHONUTF8=1 and PYTHONIOENCODING=utf-8 in the existing isolated subprocess environment; use subprocess.DEVNULL for stdin. Preserve source BOM bytes and stdout/stderr evidence. A crash then exits nonzero at EOF and follows the existing AIEditorExecutionError -> EditorFailure.json -> CLOSED path. No retries, provider/model change, timeout increase, dependency change or Dental edit.

Executable evidence and the single review action are in PROJECT_STATE.md. The separate launcher-hardening checkpoint on fix/post-pr65-final-stabilization is preserved, not silently included or merged.

---

## Ollama semantic-correction output contract — 2026-10-08

**Status:** Merged via PR #67 at `ad6f460e8b3cc43f041badd4686d8b09676b27c1`
**Class:** A — Product Critical

The actual semantic-correction request reproduces repeat limit after the existing unload/retry. Context enlargement alone and prompt compaction alone fail. An explicit output contract with the duplicate diff removed recovers valid JSON/Python on the existing model. The demonstrated defect is in request construction; no claim is made about Ollama's internal token-loop mechanism.

Reuse `_ai_developer_full_file_response_schema` inside the semantic-correction prompt and retain complete authorized files once. Keep objective/feedback, acceptance contract, review obligations, tests, validation, provider/model/options, bounded retry/repair budgets and human promotion unchanged. No target-product generation is applied during diagnosis. Evidence: [root-cause report](docs/audits/FORGELAB_OLLAMA_REPEAT_LIMIT_ROOT_CAUSE_2026-10-08.md).

---

## Native repair must preserve the current candidate — 2026-10-09

**Status:** Merged via PR #68 at `741ba4f65a10a7d3628dec74982477d0108492f1`
**Class:** A — Product Critical

Actual child artifacts prove native repair starts from protected baseline rather than the final unpromoted parent. Actual Reviewer input is also truncated after complete files are duplicated in the diff; final extracted requirements drift into evaluator instructions. The latest Dental candidate is genuinely incomplete, so semantic review must continue to block.

Carry forward the final cumulative parent patch only when exact baseline, existing authorized text targets, patch applicability and candidate syntax validate in isolation before any model call. Reuse existing full-file validators and governed edits; record parent lineage/hashes. Supply planner/editor/current Reviewer with coherent candidate evidence. Retain complete review files once and ground requirements in objective/acceptance contract. Reject stale or missing evidence; do not silently rebase or loosen gates. No target-product fixes, provider change or increased retry/repair budgets. Evidence and tests: [2026-10-09 audit](docs/audits/FORGELAB_REPEATED_SEMANTIC_REPAIR_ROOT_CAUSE_2026-10-09.md).

---

## Semantic repair no-op is not prewrite exhaustion — 2026-10-09

**Status:** Candidate correction; human review/merge pending
**Class:** A — Product Critical

The fresh real run proves a completed zero-change semantic editor call is thrown as AIDeveloperFormatError and mapped to fabricated prewrite exhaustion, while repair accounting remains zero. Candidate is incomplete and Reviewer partially inaccurate. The original editor response was discarded; its model/CLI motive is unverified and must not be invented.

Record no-op objective/output/hashes, consume one semantic attempt and use one independent review of the same candidate with unchanged passing deterministic evidence. Only normal Reviewer/Security PASS permits READY_FOR_DECISION, with promotion still human-gated. Persistent blockers close with SEMANTIC_REPAIR_NOOP; real prewrite exhaustion stays unchanged. Reject inconsistent returned-file evidence before test reuse. Preserve PR #68, models/providers/budgets and Dental boundary. Evidence: [no-op report](docs/audits/FORGELAB_SEMANTIC_REPAIR_NOOP_ROOT_CAUSE_2026-10-09.md).

## Scoped ADR-002 exception — Ollama Cloud qualification — 2026-10-21

**Status:** Explicitly authorized by Product Owner for this diagnostic only; execution stopped after model-retired smoke.
**Class:** D, to unblock A-class semantic repair.

Exception scope: only `qwen3-coder:480b-cloud`, only via signed-in local Ollama at `http://127.0.0.1:11434`, only the synthetic qualification fixture, EUR 0 Free plan. Exactly one smoke, then at most the two prescribed independent unchanged-gate executions if available. No retries beyond the specified boundary, timeout/repair-budget increase, manual correction, account/credential handling, direct ollama.com API/key, paid plan/trial/credits/spend, other model, Dental run, promotion, production source/configuration change or merge. Stop on auth/model/quota failure. One documentation-only branch and PR authorized.

Observed: one smoke returned HTTP 410, model retired July 15, 2026; qualification executions 0, no alternate attempted. This is not evidence about model quality or Aider. Production ADR-002 restrictions remain unchanged. Any replacement model or later production route needs a new explicit decision.

Evidence: [cloud qualification audit](docs/audits/FORGELAB_OLLAMA_CLOUD_QWEN3_CODER_480B_QUALIFICATION_2026-10-21.md).

Next: Product Owner decision on a separately named Free-plan candidate after checking the account usage page.

## Scoped ADR-002 exception extension — two Cloud Free models — 2026-10-21

PO explicitly authorized exactly `gpt-oss:120b-cloud`, then `gemma4:31b-cloud`, through local signed-in Ollama only, synthetic qualification only, EUR 0 Free plan. No new smoke; exactly two independent unchanged-gate executions per model, sequential, with model 2 required even if model 1 passes. STOP on HTTP 402/429 or any quota/credit message; existing auth/unavailability stop conditions remain. No paid plan/trial/purchase/payment method, other model, direct cloud API/key, credentials handling, timeout/repair-budget increase, manual output fixes, reasoning-setting change, Dental, production changes, promotion or merge. One documentation-only PR is authorized, based on PR #72 while it is unmerged.

Observed: both models PASS 2/2; four editor exits 0 within 300 seconds, four generated-test child exits 0 and independent acceptance 24/24. Both gpt-oss runs returned final content. No new smoke/retry; fixture unchanged. This qualifies the synthetic path only; production ADR-002 restrictions remain in force. Account quota/debits and Dental capacity are not verified; PO usage-page check requested.

Evidence: [two-model qualification](docs/audits/FORGELAB_OLLAMA_CLOUD_TWO_MODEL_QUALIFICATION_2026-10-21.md).

Next: PO decision on a separate semantic-routing implementation PR and ADR-002 update after reviewing usage. No production routing change is included here.

## Qualified cloud chain for all Aider editor phases — 2026-10-21

PO approved gpt-oss:120b-cloud primary, gemma4:31b-cloud alternative, and explicitly rejected the previously proposed local fallback. Shared validated configuration covers implementation, pre-write correction, test repair, semantic repair and three correction subpaths. Only primary unavailability permits one alternative attempt; quota/credit/billing/402/429 stops, both unavailable stops. Evidence records models/reasons. No automatic return to local/custom editing.

Local signed-in Ollama only; EUR 0; no key/direct cloud API/new provider/payment action. Synthetic data only: Dental source transfer is undecided and no Dental run is authorized. Non-editor roles, Aider engine/version/flags, timeout ceilings, repair budgets and human gate remain unchanged. One implementation PR, no merge.

Validation: full Python suite PASS; one real primary-editor integration smoke through the production orchestrator, with synthetic non-editor responses, reached READY_FOR_DECISION; generated tests exit 0 and independent acceptance 6/6. Actual account quota/billing and live non-editor capability remain unverified.

Evidence: [cloud routing audit](docs/audits/FORGELAB_CLOUD_EDITOR_ROUTING_2026-10-21.md). Next: PO reviews usage page and decides whether to merge the implementation PR.

## Provider-only cloud STOP detection — 2026-10-21

PO authorized the Class-A correction to PR #74 and exactly one retired qwen3-coder:480b-cloud editor diagnostic on the protected synthetic fixture, through signed-in loopback Ollama, EUR 0. This is not qualification or production model expansion. No real 402/429 is provoked; signatures come from installed source and offline injected exceptions. One branch/PR, no merge.

Decision: stdout/stderr are not an error-provenance boundary because Aider renders generated files there. Observe raised provider exceptions at Aider's send_completion boundary into private tool-home JSONL; classify only this evidence and preserve original HTTP codes through exception chains. Missing/corrupt observer evidence fails closed. No model/flag/version/timeout/budget/gate/non-editor-role change; launcher text only.

Evidence: one diagnostic exited 0 in 73.655 s with the retirement error, no completion or modified fixture, nine existing Aider-internal attempts and no external retry. Full suite: 192 PASS in 68.697 s. Offline installed boundary verified; real quota/account usage and Dental remain unverified. Cost EUR 0; no payment action.

Audit: [cloud STOP fix](docs/audits/FORGELAB_EDITOR_CLOUD_STOP_FIX_2026-10-21.md). Next: PO reviews the PR and Ollama usage, then decides whether to merge.

## All-real-role synthetic diagnostic — 2026-10-21

PO authorized at most two sequential synthetic-only runs after Task A merge, with all actual production roles, unchanged objective/routes/models/limits/gates, EUR 0 and no dashboard-token use. Stop after Run 1 unless READY_FOR_DECISION; no Dental, approval, promotion or production modification.

Observed on main baseline 4dfb0ab: Run 1 CLOSED in 167.187 s; Run 2 omitted. Initial/final candidates pass generated tests and independent acceptance 6/6; both real local reviews falsely reject implemented behavior. Ollama proves review prompt truncation to 2,050 tokens from 4,475/4,815. The last cloud correction is unchanged and rejected before write. Planner succeeds once; Support has no actual call. Three cloud completions use 29,557 tokens; no paid action/quota error. Services and protected source remain unchanged. Production automatically writes gate SYSTEM/REPAIR on this failure; no human approval was applied and the gate artifact was not altered to PENDING.

Disposition: the current non-editor path is not qualified for Dental. Do not infer inherent model incapability from a truncated-context run or qualify Support from selected_roles metadata. No route/configuration change is authorized by this diagnostic result.

Evidence: [all-real-role audit](docs/audits/FORGELAB_ALL_REAL_ROLES_SYNTHETIC_2026-10-21.md). Next: authorize one bounded reviewer qualification with complete context before any Dental decision.

## Complete-context reviewer qualification — 2026-10-22

PO authorized a synthetic-only reviewer replay: local qwen2.5-coder:7b with diagnostic context override, then gemma4:31b-cloud only after local failure, eight reviews per configuration, EUR 0 through signed-in loopback Ollama. No editor, Dental, production changes, purchases or merge. This is a diagnostic exception, not approval to route a production non-editor role to cloud.

Observed: local 8192 resolves truncation but fails the semantic gate; Gemma fails the strict response contract 8/8 and misses aggregate discount validation twice. Neither reviewer is qualified. Ollama's 2050-token result is its overflow context-shift calculation, not output reservation or parallel slots. Local minimum free RAM 1.395 GiB stayed above the declared 1 GiB abort floor. Cloud 49,507 tokens; no quota/payment event; account balance unverified.

Disposition: retain production routes. Proposed for separate approval only: reviewer-specific num_ctx=8192 with existing num_predict=2048/temperature=0.1 / 60 s timeout, strict schema validation and context evidence. This corrects the demonstrated truncation, not semantic reliability; no automatic schema conversion or cloud reviewer promotion. Dental remains blocked pending a passing reviewer gate.

Evidence: [reviewer qualification audit](docs/audits/FORGELAB_REVIEWER_COMPLETE_CONTEXT_QUALIFICATION_2026-10-22.md). Next: PO reviews audit and Ollama usage and decides on the separate reviewer-context implementation PR.

## Reviewer gate confound and reviewer contract fix — 2026-10-22

PR #76/#77 measured the reviewer with the semantic-repair objective, which contains a stale blocking review of the pre-change code. Their reviewer results are not a valid measurement of reviewer reliability; they remain valid evidence of truncation (PR #76) and of the cloud schema failure (PR #77).

Decision (implementation PR, PO merge required): state the reviewer JSON contract in the prompt with the exact schema, keep strict validation, and size Ollama `num_ctx` from the prompt (4096 to 16384, fail closed above the ceiling or when the evaluated prompt is implausibly short). Routes, models, timeouts, repair budgets, gates and the cloud editor chain are unchanged; no cloud reviewer route is introduced.

Evidence: [confound and fix](docs/audits/FORGELAB_REVIEWER_GATE_CONFOUND_AND_CONTRACT_FIX_2026-10-22.md). Next: clean-objective reviewer replay on this code before any routing decision; Dental remains blocked.

## Cloud reviewer decision and conditional end-to-end delivery — 2026-10-22

The PO explicitly accepts immediate REVIEWER cloud routing without separate qualification rounds, using exactly one end-to-end synthetic run as verification. Primary gemma4:31b-cloud (different family from gpt-oss editor); alternative gpt-oss:120b-cloud only on 404/410/retired/not-found, recorded as reduced independence. Quota/credit/billing/402/429 stops; never a local reviewer. Planner and Support stay local qwen2.5-coder:7b; editor chain unchanged. Signed-in local Ollama 127.0.0.1:11434 only, EUR 0, no purchases, Dental, promotion or service restart.

PO also authorizes one gpt-oss-primary repeat only if failure is solely due to invalid/wrong Gemma review, and merge only after end-to-end PASS. Implementation reuses PR #75 classification and PR #78 context/contract checks; strict validation stays intact.

Observed: 213 Python tests PASS; one clean-objective run ends REVIEW in 108.375 s. Generated tests pass after one repair, but independent acceptance is 2/6 test methods (5 failure records). An incorrect generated test expects 20 from 10+6+3; Support suggests rounding and editor introduces rounding to tens. Gemma returns valid JSON and correctly blocks that line, while missing exact item count in requirements. Cloud 17,564 tokens, EUR 0. Conditional repeat and merge are not authorized by this outcome: neither is performed. Unchanged failure gate remains SYSTEM/REPAIR; no promotion.

Evidence: [cloud reviewer route](docs/audits/FORGELAB_CLOUD_REVIEWER_ROUTE_2026-10-22.md). Next: PO reviews the PR and authorizes a separate bounded fix for generated-test expectations and repair reasoning before another end-to-end run.

## Shared cloud Reviewer/Support and generated-test oracle decision — 2026-10-22

PO Task F supersedes the previous local Support restriction: SUPPORT and REVIEWER share gemma4:31b-cloud primary and gpt-oss:120b-cloud alternative only on 404/410/retired/not-found, recording reduced independence. Quota/credit/billing/402/429 stops, never local. Planner stays local qwen2.5-coder:7b; Aider/editor chain unchanged; only signed-in loopback Ollama, EUR 0, synthetic data. No Dental, purchases, promotion or service restart. Generalize the existing reviewer policy, do not duplicate it.

Generated tests are NOT an oracle. Support and every repair/correction prompt must recompute expected results from the objective and inputs, correct an incorrect TEST while preserving coverage, and forbid assertion-fitting implementation logic (including unjustified rounding/bucketing). Support receives complete authorized current files and the binding contract through existing bounded readers.

Git baseline c4ff897 confirms PR #79 was merged after Task E's audit checkpoint; its failed run remains valid historical evidence. Task F authorizes exactly one fresh production synthetic run with clean objective SHA-256 ebb6eb21a7293a6850eece17653625f949067ffdfeafb90cf8cada10446ba5f0 and max_repair_attempts=2. Merge is authorized only on the full end-to-end PASS.

Observed: 216 Python tests PASS; single run cloud-support-1 reaches READY_FOR_DECISION in 120.063 s after one test-only repair, generated tests 11/11 exit 0, independent acceptance 6/6, strict Gemma review PASS with no findings. Human gate PENDING; no promotion. Cloud 22,562 tokens, EUR 0 ledger; services/source unchanged. Conditional merge criterion is satisfied; no second run. Prompt compliance/general reliability and remaining account quota are not proven by one run.

Evidence: [Task F audit](docs/audits/FORGELAB_CLOUD_SUPPORT_TEST_ORACLE_2026-10-22.md). Single next action: PO reads Ollama session/weekly usage before any further real workload decision.

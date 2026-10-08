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

## D-026 — Verify launcher ownership and clean failed startup process trees

**Date:** 2026-10-08
**Status:** Candidate verified; human review/merge pending
**Class:** A — Product Critical

Post-PR65 regression execution proved that generic Vite command matching, health-only API matching and an unbounded workerd directory prefix could terminate unverified processes. A simulated stability failure also left both owned process trees running.

Restrict workerd paths to the actual node_modules directory; use checkout-local PID plus creation-time metadata for API/development process ownership; clean every owned startup tree on failure, including partial startup. Refuse legacy/unproven ownership. Seven executable regressions cover foreign processes, sibling prefixes, valid/reused PIDs and partial/stability failure cleanup, and run in the launcher gate.

Actual Windows full startup gate passed on existing configurable ports 8875/5273; original 5173/8765 processes belong to the old checkout and were preserved. This does not authorize a Dental submission or merge. Aider, application lifecycle, ToolGateway, review/security, repair budget and zero-paid-provider policy are unchanged. Evidence and next action: PROJECT_STATE.md.
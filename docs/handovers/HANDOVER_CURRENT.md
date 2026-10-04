# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-04  
**Checkpoint:** Golden Path 1 / Dental Quote — stacked runtime remediations through PR #43  
**Status:** PRE-MVP / product-critical validation  
**Commercial evidence level:** C0 — Hypothesis  
**Canonical repository:** `pierluigiavvanzo-creator/forgelab`

## 1. Executive state

ForgeLab is being validated as a governed multi-agent software-development control plane, not as a generic chat workflow.

Golden Path:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED REPAIR -> REVIEW -> WORKING PREVIEW -> HUMAN APPROVAL -> PROMOTION`

Primary constraint:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / PRODUCT OWNER TIME`

The Product Owner should approve strategy and final promotion, not act as routine debugger, QA operator, log courier or retry orchestrator.

Current work remains focused exclusively on Golden Path 1. Do not start new infrastructure or Golden Path 2 until Dental Quote reaches a decision-ready PASS.

## 2. Canonical baseline

Canonical branch:

`main`

Current verified `main` HEAD:

`5f83844a36063722c2979dae19576d57c0f06c5a`

This is the merge of PR #34:

`MVP-1: reset Ollama state before repeat-limit retry`

PR #34 is therefore **MERGED**. Any older document saying PR #34 is awaiting merge is stale.

Local ForgeLab path used for real runs:

`C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`

Dental Quote target:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

## 3. Product Owner operating constraints

Preserve these constraints unless explicitly changed:

- use normal ChatGPT chat plus Windows PowerShell only when necessary;
- do not use Work or Codex;
- ZERO-COST API/TOKEN FIRST;
- current local model: Ollama `qwen2.5-coder:7b`;
- no paid provider fallback;
- no paid API/token without explicit approval;
- `max_repair_attempts = 1`;
- no new agent, provider, dependency, configuration framework or infrastructure unless a concrete Golden Path blocker proves it necessary;
- no merge/promotion without explicit Product Owner approval;
- repository source must remain unchanged until explicit promotion.

## 4. Golden Path 1 contract

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

## 5. Merged remediation baseline

The main branch already contains the earlier MVP-1 remediations through PR #34.

Key merged behaviors now available on `main` include:

- PM acceptance contract propagation;
- end-to-end acceptance grounding;
- repair regression constraints;
- no-op pre-write recovery;
- acceptance-test traceability;
- full-file syntax recovery;
- deterministic repair-regression gate;
- governed pre-write recovery exhaustion;
- in-attempt semantic test correction;
- in-attempt semantic re-review correction;
- governed provider retry exhaustion;
- semantic repair full-file schema;
- Ollama model unload/reset before repeat-limit retry.

The current work after PR #34 is therefore not a restart. It is incremental hardening of the same real Golden Path.

## 6. Open stacked runtime PRs

Do not merge these automatically.

### PR #37 — govern unexpected run failures

Branch:

`mvp1-govern-early-run-failure-envelope`

HEAD:

`f2600c167edaecbe4351f6dbcac798cf84859074`

Base:

`main@5f83844a36063722c2979dae19576d57c0f06c5a`

Status:

**OPEN / mergeable / locally validated**

Purpose:

- terminalize unexpected started-run failures;
- emit `RunFailure.json`;
- emit normal terminal decision artifacts;
- close as `CLOSED / Repair required`;
- do not catch `KeyboardInterrupt` or `SystemExit`;
- do not invent test/security evidence.

Real-run evidence:

`run-9f2e9fdf5c8a`

Result:

- CLI exit 0;
- run safely CLOSED;
- failure became `PrewriteRecoveryFailure.json`;
- no repository write;
- PR #37 successfully eliminated the prior invisible/crashing lifecycle path.

### PR #38 — single-schema pre-write recovery

Branch:

`mvp1-prewrite-recovery-single-schema`

HEAD:

`473ddfd0435d74c690391b5880a8fb99e20c9cbc`

Base:

PR #37 branch.

Purpose:

- remove contradictory normal-patch + full-file contracts from the same recovery prompt;
- full-file reference/syntax recovery exposes only schema 2.1;
- preserve one bounded pre-write recovery.

Real-run evidence:

`run-8d44a83b7d99`

Result:

- valid two-file AI Developer candidate was produced;
- ForgeLab progressed beyond the earlier syntax/recovery blocker;
- run then stopped because Windows test command `py` was not allowlisted.

### PR #39 — Windows `py` launcher in bounded tests

Branch:

`mvp1-windows-py-test-runner`

HEAD:

`d4b20d7115cb108686f7b4edbd31d432da78a1b7`

Base:

PR #38 branch.

Purpose:

- allow `py` and `py.exe` only on Windows;
- preserve blocking of shell/other non-allowlisted executables;
- leave the Golden Path test command unchanged.

Real-run evidence:

`run-5c795866ebc5`

Result:

- deterministic tests actually ran and passed 6 / 6;
- Reviewer correctly blocked promotion because three-treatment and automatic-subtotal behavior were still incomplete;
- semantic repair started;
- Ollama repeat-limit was exhausted during `review-repair-1`.

### PR #40 — harden repeat-limit retry

Branch:

`mvp1-ollama-repeat-limit-recovery-profile`

HEAD:

`4ccd12cff2a86a7eb50390106a050dc7d8631bd4`

Base:

PR #39 branch.

Purpose:

- keep the same single existing provider retry;
- keep the same local model and EUR 0 cost;
- after repeat-limit only: unload/reset model, use anti-repeat prompt, JSON mode for S2 Developer retry, and retry-only anti-repeat generation options;
- retain deterministic ForgeLab schema validation after generation.

Real-run evidence:

`run-7188ab09e507`

Result:

- repeat-limit recovery **worked**;
- semantic repair succeeded on the second provider attempt;
- ForgeLab applied repair and reran tests;
- tests became 8 total with 2 errors;
- one in-attempt semantic test correction was activated;
- correction retry returned JSON with the wrong shape because its prompt did not explicitly carry schema 2.1 after JSON-mode fallback.

### PR #41 — self-describing semantic test-correction schema

Branch:

`mvp1-semantic-test-correction-self-describing-schema`

Current HEAD:

`a8fa650ee48b7660ddf47a62a6b4bee00dae4399`

Base:

PR #40 branch.

Purpose:

- write the full-file schema 2.1 directly into the semantic test-correction prompt;
- keep normal response-format enforcement on the first attempt;
- remain compatible with PR #40 JSON-mode repeat recovery;
- preserve all retry/model/provider/budget limits.

Important branch history:

- first PR #41 candidate HEAD `b0211eb636b73961022a567455a3b90de1f9978f` accidentally embedded JSON braces directly inside an f-string;
- real run `run-3b29af81a9f0` exposed the resulting Python `ValueError: Invalid format specifier ...`;
- PR #37 safely terminalized that failure;
- the branch was corrected in place;
- current PR #41 HEAD is `a8fa650ee48b7660ddf47a62a6b4bee00dae4399`;
- the schema now lives in a literal string outside the f-string and is inserted as a variable.

### PR #43 — semantic correction after bounded test repair

Branch:

`mvp1-post-test-repair-semantic-correction`

HEAD:

`a5e375dab9fdfb87cf441c5841044ace25d354a2`

Base:

PR #41 branch.

Purpose:

- tag ordinary bounded deterministic-test repairs with `cause: test_failure`;
- reuse the existing one in-attempt semantic correction when the only top-level repair was consumed by a deterministic test failure;
- allow that correction only after repaired deterministic tests PASS and independent semantic review still FAILS;
- preserve `max_repair_attempts = 1`;
- rerun deterministic tests after the correction;
- require another independent semantic review before decision readiness;
- add no agent, provider, dependency, paid fallback or scope expansion.

Regression target:

`test FAIL -> repair -> tests PASS -> semantic review FAIL -> one in-attempt semantic correction -> tests PASS -> re-review PASS`

This closes the exact orchestration gap exposed by the unchanged PR #41 rerun.

## 7. Real-run evidence at current PR #41 HEAD

### Run A — pre-write variability

Run:

`run-291a8c57536f`

Observed:

- CLI exit 0;
- initial Developer candidate failed deterministic reference validation;
- the one full-file pre-write recovery then produced invalid Python with an unterminated string literal;
- ForgeLab emitted `PrewriteRecoveryFailure.json`;
- repository write performed: false;
- Dental Quote source remained CLEAN;
- estimated/spent provider cost remained EUR 0.

Interpretation:

This run did not reach PR #41's target phase and showed that local-model output can fail early while the governed safety envelope remains intact.

### Run B — unchanged rerun required by prior handover

Run:

`run-827c3464862e`

ForgeLab HEAD:

`a8fa650ee48b7660ddf47a62a6b4bee00dae4399`

Observed:

- CLI exit 0;
- planning completed with explicit acceptance criteria for three treatments, automatic subtotal, discount, final total, input validation, tests and scope limits;
- initial deterministic tests ran and failed 1 / 6 because `test_multiple_treatments` attempted to add two dictionary results;
- Support diagnosed the deterministic failure;
- the single bounded top-level repair was used;
- deterministic retest then passed 6 / 6;
- independent semantic Reviewer correctly found that the repaired candidate still did not implement the required three-treatment / automatic-subtotal behavior;
- run stopped in `REVIEW` with `tests: PASS`, `repair_attempts: 1` and decision `Repair required`;
- no further semantic correction started;
- source repository remained CLEAN;
- 7 local Ollama calls were recorded at estimated/spent cost EUR 0.

Important interpretation:

The earlier pre-write failure is **not reproducible as the deterministic current blocker**. The unchanged rerun progressed through the pre-write layer and exposed a repeatable orchestration rule instead.

## 8. Current product diagnosis

The real rerun proves that ForgeLab can already execute:

`PLAN -> IMPLEMENT -> TEST FAIL -> BOUNDED TEST REPAIR -> RETEST PASS -> INDEPENDENT SEMANTIC REVIEW FAIL`

The remaining orchestration defect is that the deterministic test repair consumes the only top-level repair budget. After retest PASS, semantic review cannot start a normal semantic repair because:

`repair_attempts == max_repair_attempts == 1`

The existing PR #31 in-attempt semantic correction can operate after a semantic-review repair, but not after an ordinary deterministic-test repair.

This creates a false stopping point: deterministic tests are green, the Reviewer correctly detects missing Product Owner behavior, but ForgeLab cannot use the already-designed in-attempt semantic correction path.

## 9. Current blocker

Current blocker classification:

`TEST_FAILURE_REPAIR_CONSUMES_ONLY_TOP_LEVEL_BUDGET_BEFORE_SEMANTIC_ACCEPTANCE`

Smallest remediation:

PR #43 extends the existing in-attempt semantic correction to either top-level repair cause:

- `test_failure`;
- `semantic_review`.

The top-level repair budget remains exactly `1`.

No additional retry, provider, model, paid fallback, agent, dependency or write scope is introduced.

## 10. PR / merge state

- PR #34: **MERGED** into `main`.
- PR #36: **OPEN** docs-only canonical sync created after PR #34; now historically stale relative to PR #37–#41. Do not merge it without reconciliation.
- PR #37: **OPEN / not merged**.
- PR #38: **OPEN / stacked on #37 / not merged**.
- PR #39: **OPEN / stacked on #38 / not merged**.
- PR #40: **OPEN / stacked on #39 / not merged**.
- PR #41: **OPEN / stacked on #40 / not merged**.
- PR #43: **OPEN / stacked on #41 / not merged**.

No explicit approval has been given to merge PR #37–#43.

## 11. Out of scope until Golden Path 1 passes

Do not prioritize:

- multi-tenancy;
- billing;
- deployment expansion;
- paid-provider expansion;
- new agent roles;
- broad observability;
- new configuration frameworks;
- unrelated refactors;
- Golden Path 2 or 3.

Only a concrete blocker from the unchanged Dental Quote flow may justify another ForgeLab runtime change.

## 12. Single next action

`VALIDATE_PR43_AND_RERUN_UNCHANGED_DENTAL_QUOTE_ONCE`

Use exactly:

- ForgeLab candidate HEAD: `a5e375dab9fdfb87cf441c5841044ace25d354a2`;
- same Dental Quote repository;
- same Product Owner objective;
- same two authorized files;
- same test command;
- same `max_repair_attempts = 1`;
- same local Ollama model;
- no paid fallback;
- no configuration expansion.

Required sequence:

1. run the standard ForgeLab validation harness against the exact PR #43 HEAD;
2. only if validation PASS, rerun the unchanged Dental Quote once;
3. verify that a test-failure repair followed by PASS tests can enter the one in-attempt semantic correction when Reviewer still FAILS;
4. require deterministic retest and independent re-review after that correction;
5. only a final `READY_FOR_DECISION` with tests/review/security PASS can justify considering merge/promotion.

Decision rule:

- validation FAIL -> repair PR #43 only;
- governed runtime blocker -> fix only that blocker;
- `READY_FOR_DECISION` -> inspect final candidate and human gate;
- do not merge PR #37–#43 before decision-ready real-run evidence.

## 13. Resume protocol for the next chat

Before changing code:

1. read `AGENTS_MASTER.md`;
2. read `AGENTS.md`;
3. read `PROJECT_STATE.md`;
4. read `ROADMAP.md`;
5. read `DECISIONS.md`;
6. read this `docs/handovers/HANDOVER_CURRENT.md`;
7. verify live GitHub `main` and PR #37–#43 heads/states;
8. do not infer local checkout state from this handover.

Then execute only the Single Next Action unless new evidence invalidates it.

## 14. Economic / product significance

The work remains A — Product Critical because the goal is not to make individual tests green. The goal is to prove that ForgeLab can autonomously produce a usable software change, detect incomplete behavior that unit tests miss, repair within a bounded budget, and present a decision-ready result without routine Product Owner debugging.

Until that happens in one uninterrupted real run, ForgeLab remains PRE-MVP and Dental Quote remains the active acceptance test.

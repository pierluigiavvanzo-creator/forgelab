# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-05  
**Checkpoint:** Golden Path 1 / Dental Quote — stacked runtime remediations through PR #47  
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

### PR #44 — deterministic malformed f-string stabilization

Branch:

`mvp1-deterministic-fstring-recovery-stabilizer`

HEAD:

`252dc530455c086f1f3f9b9f2da22f7d3509d240`

Base:

PR #43 branch.

Purpose:

- address repeated initial full-file recovery failures caused by malformed f-string quoting/braces;
- use no extra AI retry;
- when full-file recovery fails syntax specifically on an f-string, restore the unique matching f-string statement from the authoritative source baseline;
- rerun deterministic Python syntax validation afterward;
- record `deterministic_fstring_stabilized_paths` for auditability;
- leave non-f-string syntax failures governed and unchanged.

Regression target:

A malformed recovery f-string is repaired from baseline while the intended non-f-string code change remains intact.

### PR #45 — compile Python candidates before repository write

Branch:

`mvp1-python-compile-prewrite-gate`

HEAD:

`d57df27b6649d62578a20d98b2c0e6147751a94b`

Base:

PR #44 branch.

Purpose:

- strengthen final Python pre-write validation from AST-only parsing to actual Python compilation with `compile(..., "exec")`;
- catch compile-time constraints such as module-level `return` before any repository/workspace write reaches deterministic tests;
- keep PR #44's AST-based f-string stabilizer only for locating malformed f-string lines;
- route compile-time failures through the existing single bounded pre-write recovery;
- add no retry, provider, model, paid API, agent or scope expansion.

Regression target:

A candidate that `ast.parse()` accepts but Python compilation rejects must be stopped pre-write and recovered through the existing one full-file recovery.

### PR #46 — self-describing semantic repair + semantic f-string stabilization

Branch:

`mvp1-semantic-repair-self-describing-stabilized`

HEAD:

`ab082de9eae9936f18a1f15614b6b8153eaac251`

Base:

PR #45 branch.

Purpose:

- make the initial semantic-review repair prompt explicitly include full-file schema 2.1, so PR #40's retry-only JSON mode still has the required contract;
- keep the schema literal outside the Python f-string prompt;
- apply the existing deterministic source-based f-string stabilizer to semantic-review pre-write recovery;
- retain PR #45 compile validation afterward;
- record `deterministic_fstring_stabilized_paths` on semantic repair records;
- add no retry, provider, model, paid API, agent or scope expansion.

Regression target:

`semantic review FAIL -> semantic repair malformed/JSON-mode fallback -> one pre-write recovery -> malformed f-string stabilized from source -> compile PASS -> tests PASS -> semantic re-review PASS`.

### PR #47 — deterministic f-string subscript normalization

Branch:

`mvp1-fstring-subscript-normalizer`

HEAD:

`02390da8cd1bad27a4b476aa3de6640553efc32f`

Base:

PR #46 branch.

Purpose:

- preserve same-scope source restoration as the first malformed f-string strategy;
- constrain restoration to the same enclosing Python function/class scope;
- when a newly introduced f-string has no unique same-scope baseline line, normalize only dictionary-subscript quote syntax inside its `{...}` expression;
- convert escaped/same-quote forms such as `data[\"key\"]` inside a double-quoted f-string to semantically equivalent `data['key']`;
- retain PR #45 compile validation afterward;
- add no AI call, retry, provider, model, paid API, agent or scope expansion.

Regression target:

Semantic pre-write recovery contains both a baseline-restorable malformed f-string and a newly introduced escaped dictionary-subscript f-string; both are repaired deterministically before compilation.

## 7. Latest real-run evidence

### Run A — PR #41 pre-write variability

`run-291a8c57536f`

- governed pre-write recovery exhaustion;
- source CLEAN;
- EUR 0.

### Run B — unchanged PR #41 rerun

`run-827c3464862e`

- deterministic test failure;
- one bounded test repair;
- repaired tests 6 / 6 PASS;
- independent semantic review correctly blocked missing three-treatment / automatic-subtotal behavior;
- exposed the PR #43 post-test semantic-correction orchestration gap.

### Run C — PR #43

`run-7ca3466ed4a7`

- initial and recovery candidates both failed on malformed f-string syntax;
- no repository write;
- source CLEAN;
- exposed repeated f-string regeneration and motivated PR #44.

### Run D — PR #44

`run-f07b2ecb940a`

ForgeLab HEAD:

`252dc530455c086f1f3f9b9f2da22f7d3509d240`

Observed:

- CLI exit 0;
- initial AI Developer candidate was accepted pre-write and applied in isolated workspace;
- deterministic tests then failed during import with `SyntaxError: 'return' outside function`;
- Support diagnosed the syntax failure;
- repair candidate and its one pre-write correction both collapsed to no-op output;
- ForgeLab emitted `PrewriteRecoveryFailure.json` for phase `test_failure_repair`;
- run closed safely;
- source repository remained CLEAN;
- `deterministic_fstring_stabilized_paths` was empty because this failure was not an f-string error;
- 5 local Ollama calls, EUR 0.

Root cause learned from Run D:

The final pre-write Python validator used `ast.parse()`. That parser accepts some constructs which Python later rejects at compile/import time, including module-level `return`. The pre-write gate therefore did not validate the same constraint enforced by the real test/import runtime.

### Run E — PR #45

`run-83a68ff67822`

ForgeLab HEAD:

`d57df27b6649d62578a20d98b2c0e6147751a94b`

Observed:

- CLI exit 0;
- initial implementation and its one pre-write recovery produced a compilable two-file candidate;
- deterministic tests ran and passed 4 / 4;
- independent semantic review correctly blocked incomplete Product Owner coverage, especially missing true three-treatment / automatic-subtotal behavior;
- semantic-review repair was activated;
- its first provider attempt hit Ollama repeat-limit;
- the existing anti-repeat retry succeeded but returned JSON without `schema_version`, `summary` and `files`;
- semantic pre-write recovery then timed out once, succeeded on its existing provider retry, but produced Python with `f-string: unmatched '['`;
- governed `PrewriteRecoveryFailure.json` recorded phase `semantic_review_repair`;
- source repository remained CLEAN;
- tests before semantic repair were PASS;
- 8 local Ollama calls, EUR 0.

Interpretation:

PR #45 worked for its intended purpose: compile-invalid Python did not leak into deterministic testing. The current blocker is now entirely inside semantic-review repair/recovery.

### Run F — PR #46

`run-a933b591f000`

ForgeLab HEAD:

`ab082de9eae9936f18a1f15614b6b8153eaac251`

Observed:

- CLI exit 0;
- initial implementation reached deterministic tests;
- deterministic tests passed 5 / 5;
- independent semantic review correctly blocked missing explicit three-treatment / automatic-subtotal behavior;
- semantic-review repair remained schema-grounded: the prior `missing fields: files, schema_version, summary` failure did not recur;
- semantic repair then failed pre-write on `f-string: unmatched '['`;
- its single pre-write recovery produced a second f-string error: `f-string expression part cannot include a backslash`;
- no semantic repair write occurred;
- source repository remained CLEAN;
- 7 local Ollama calls, EUR 0.

Interpretation:

PR #46 succeeded on the schema-contract half of its purpose. The remaining failure demonstrates that semantic repair may introduce a *new* malformed f-string with no baseline line that can be restored. This is the narrow gap addressed by PR #47.

## 8. Current product diagnosis

The stacked candidates now address five distinct proven gaps:

1. PR #43: semantic correction remains available after the one top-level repair was consumed by a deterministic test failure.
2. PR #44: malformed full-file recovery f-strings can be stabilized from the authoritative source baseline.
3. PR #45: every final Python candidate is compiled pre-write, not merely AST-parsed.
4. PR #46: semantic-review repair remains schema-grounded under retry-only JSON mode and inherits source-based f-string stabilization.
5. PR #47: newly introduced f-strings with malformed dictionary-subscript quoting can be normalized deterministically when no safe baseline restoration exists.

The intended uninterrupted proof remains:

`PLAN -> IMPLEMENT -> PREWRITE COMPILE GATE -> TEST -> BOUNDED REPAIR IF NEEDED -> TEST PASS -> SEMANTIC REVIEW -> SEMANTIC REPAIR/CORRECTION -> FSTRING STABILIZATION IF NEEDED -> PREWRITE COMPILE GATE -> RETEST -> RE-REVIEW -> READY_FOR_DECISION`

## 9. Current blocker

Current blocker classification:

`NEW_SEMANTIC_REPAIR_FSTRING_HAS_NO_BASELINE_MATCH_AND_ESCAPED_SUBSCRIPT_QUOTES_FAIL_COMPILE`

Smallest remediation:

PR #47 keeps source restoration scoped to the same enclosing function/class and, only when no unique safe source match exists, normalizes bracketed string-key quotes inside the failing f-string expression before compile validation.

No additional AI retry is introduced.

## 10. PR / merge state

- PR #34: **MERGED** into `main`.
- PR #36: **OPEN** docs-only canonical sync created after PR #34; now historically stale relative to PR #37–#41. Do not merge it without reconciliation.
- PR #37: **OPEN / not merged**.
- PR #38: **OPEN / stacked on #37 / not merged**.
- PR #39: **OPEN / stacked on #38 / not merged**.
- PR #40: **OPEN / stacked on #39 / not merged**.
- PR #41: **OPEN / stacked on #40 / not merged**.
- PR #43: **OPEN / stacked on #41 / not merged**.
- PR #44: **OPEN / stacked on #43 / not merged**.
- PR #45: **OPEN / stacked on #44 / not merged**.
- PR #46: **OPEN / stacked on #45 / not merged**.
- PR #47: **OPEN / stacked on #46 / not merged**.

No explicit approval has been given to merge PR #37–#47.

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

`VALIDATE_PR47_AND_RERUN_UNCHANGED_DENTAL_QUOTE_ONCE`

Use exactly:

- ForgeLab candidate HEAD: `02390da8cd1bad27a4b476aa3de6640553efc32f`;
- same Dental Quote repository;
- same Product Owner objective;
- same two authorized files;
- same test command;
- same `max_repair_attempts = 1`;
- same local Ollama model;
- no paid fallback;
- no configuration expansion.

Required sequence:

1. run standard ForgeLab validation harness on exact PR #47 HEAD;
2. only if validation PASS, rerun unchanged Dental Quote once;
3. verify initial implementation and semantic repair remain compile-valid before write;
4. if malformed semantic-repair f-strings occur, verify same-scope baseline restoration and/or deterministic subscript-quote normalization recover them without another AI call;
5. require deterministic retest and independent semantic re-review;
6. only final `READY_FOR_DECISION` with tests/review/security PASS and source CLEAN can justify merge/promotion review.

Do not merge PR #37–#47 before decision-ready real-run evidence.

## 13. Resume protocol for the next chat

Before changing code:

1. read `AGENTS_MASTER.md`;
2. read `AGENTS.md`;
3. read `PROJECT_STATE.md`;
4. read `ROADMAP.md`;
5. read `DECISIONS.md`;
6. read this `docs/handovers/HANDOVER_CURRENT.md`;
7. verify live GitHub `main` and PR #37–#47 heads/states;
8. do not infer local checkout state from this handover.

Then execute only the Single Next Action unless new evidence invalidates it.

## 14. Economic / product significance

The work remains A — Product Critical because the goal is not to make individual tests green. The goal is to prove that ForgeLab can autonomously produce a usable software change, detect incomplete behavior that unit tests miss, repair within a bounded budget, and present a decision-ready result without routine Product Owner debugging.

Until that happens in one uninterrupted real run, ForgeLab remains PRE-MVP and Dental Quote remains the active acceptance test.

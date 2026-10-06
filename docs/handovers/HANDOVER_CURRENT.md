# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-06  
**Checkpoint:** Dashboard exposed exact Aider empty-config integration bug  
**Status:** PRE-MVP / one-line Aider config fix / HUMAN MERGE GATE

## 1. Binding product priority

Dental Quote remains Golden Path #1.

It is not abandoned, replaced or deferred by the playable-game idea.

Required order:

1. Dental Quote — autonomous usable product proof;
2. Playable Game — visible/generalization proof;
3. Small CRUD SaaS;
4. Automation / Reporting Tool.

Binding Dental gate:

`docs/experiments/DENTAL_QUOTE_AUTONOMY_GATE.md`

## 2. Product Owner contract

The Product Owner:

- starts ForgeLab services once;
- initiates the target-product run from the dashboard;
- reviews the decision-ready candidate;
- approves, rejects or requests repair;
- performs the final visible usability check.

The Product Owner is not:

- the test harness;
- a log courier;
- a patch author;
- a PowerShell retry orchestrator;
- a ChatGPT-assisted Dental code fixer.

## 3. ChatGPT independence rule

ChatGPT may develop ForgeLab.

ChatGPT must not write, repair or manually transform Dental Quote target code during the target-product run.

Binding metric:

`CHATGPT_ASSISTANCE_IN_TARGET_PRODUCT_RUN = 0`

If target-product code must be pasted into ChatGPT for correction, that Dental run is FAIL.

## 4. Canonical repository

Repository:

`pierluigiavvanzo-creator/forgelab`

Canonical `main` at this checkpoint:

`1fac126023444052623da0c8027cc7209522bbbb`

This is the merge of PR #50:

`MVP Recovery: add bounded reusable editor bakeoff harness`

Runtime PRs #37–#48 remain frozen and unmerged.

## 5. Current integration PR

PR:

`#51 — MVP-1: make Dental Quote dashboard run use reusable Aider editor`

Branch:

`mvp1-dental-autonomous-aider-golden-path`

Purpose:

Connect the merged reusable editor boundary to the **real dashboard-created Dental Quote Golden Path** with the smallest safe change.

This is not a detached demo or separate CLI product path.

## 6. REUSE-FIRST implementation

The dashboard AI Developer mode now selects:

`editor_engine = aider`

Initial implementation path:

```text
Dashboard
  -> Local API
  -> Project Manager / acceptance contract
  -> AiderCliAdapter
  -> disposable authorized-file sandbox
  -> candidate file contents
  -> ForgeLab pre-write validation
  -> ToolGateway apply in isolated workspace
  -> deterministic tests
  -> independent semantic Reviewer
  -> Security
  -> READY_FOR_DECISION
  -> dashboard human gate
```

Aider is only the initial Developer editing engine in this candidate.

Existing ForgeLab repair governance remains available. If Aider fails pre-write and ForgeLab uses its existing one bounded custom repair, the artifact records:

`fallback = custom_prewrite_repair`

This preserves truthful attribution.

No additional recovery catalogue from frozen PRs #37–#48 is imported.

## 7. Local reusable toolchain

`Start-ForgeLab.ps1` now prepares a pinned isolated editor environment when needed:

- Aider version: `0.86.2`;
- package: `aider-chat==0.86.2`;
- isolated under `.forgelab/tools/aider-0.86.2`;
- local model transport: `ollama_chat/qwen2.5-coder:7b`;
- Ollama endpoint: loopback `http://127.0.0.1:11434`;
- known paid-provider API keys stripped from the Aider subprocess;
- no automatic Git use/commit;
- no Aider auto-test or auto-lint;
- no automatic push or merge.

API/model provider cost remains EUR 0.

## 8. Dashboard behavior

AI Developer mode visibly states:

`REUSE-FIRST / Aider + Ollama / EUR 0`

The create-run request includes:

`editor_engine: "aider"`

The dashboard also states:

`ChatGPT assistance target run: 0`

No diagnostic PowerShell run is part of the normal Dental workflow.

## 9. Evidence contract

Run artifacts record:

- `editor_engine`;
- reusable editor call count;
- editor metadata;
- explicit fallback if one occurs;
- `chatgpt_assistance_in_target_product_run = 0`;
- `product_owner_run_actions = 1`;
- local-zero-spend provider mode;
- tests;
- semantic review;
- security;
- source integrity.

## 10. Focused regressions added

New/updated regressions cover:

- Aider initial Developer path reaches `READY_FOR_DECISION` with Planner + Reviewer and without the legacy custom Developer generation call;
- API accepts `editor_engine=aider` and preserves it into run evidence;
- dashboard sends and displays REUSE-FIRST Aider mode;
- launcher pins the reusable editor toolchain;
- Aider uses `ollama_chat/qwen2.5-coder:7b`;
- local Ollama endpoint is explicit;
- cost remains zero;
- ChatGPT target-run assistance metric remains zero;
- source repository remains clean.

No claim is made yet that the **real** Dental Quote target succeeds. That requires a post-merge dashboard run on the user's local Ollama/Windows environment.

## 11. Binding real-run input after merge

Target repository:

`C:\Users\NITRO\source\FORGELAB_MVP1_DENTAL_QUOTE`

Objective:

`Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.`

Authorized files:

- `quote_calculator.py`;
- `test_quote_calculator.py`.

Test:

`py -3.11 -m unittest discover -v`

Repair cap:

`1`

Editor:

`Aider + local Ollama qwen2.5-coder:7b`

Paid fallback:

`NONE`

## 12. Dental Quote PASS

Do not mark Golden Path #1 PASS until:

- run initiated from dashboard;
- ChatGPT target assistance = 0;
- Product Owner log-copy/debug actions = 0;
- paid API cost = EUR 0;
- exactly-three-treatment behavior is actually implemented;
- automatic subtotal is correct;
- configurable percentage discount is correct;
- final total is correct;
- input validation is correct;
- direct quantitative tests PASS;
- independent semantic Reviewer PASS;
- Security PASS;
- source repository stays protected until approval;
- run reaches `READY_FOR_DECISION`;
- Product Owner approves;
- promoted application launches locally;
- Product Owner confirms the visible workflow is usable.

## 13. First real Dental dashboard run

Run:

`run-f03a38460154`

Dashboard evidence:

- `CLOSED`;
- Gate `Repair`;
- TEST `PASS`;
- repair attempts applied `0`;
- provider cost `EUR 0`;
- 6 LLM calls / 10004 tokens.

This run is FAIL for the Dental autonomy gate because it did not reach
`READY_FOR_DECISION`.

Code trace on merged PR #51 shows the reusable Aider editor is used for initial
implementation, but semantic-review repair still uses the legacy custom
structured/full-file Developer path.

The smallest general remediation is therefore:

`AIDER_FOR_BOUNDED_SEMANTIC_REPAIR`

The candidate keeps:

- one top-level repair budget;
- ToolGateway authority;
- deterministic retest;
- independent semantic re-review;
- zero paid API cost;
- ChatGPT target assistance = 0.

It adds no Dental-specific implementation logic.

## 14. Seventh real Dental dashboard run — exact Aider CLI root cause

Run:

`run-ebf29be889fe`

Runner:

`df32388e1d0b...`

Dashboard blocker:

`PREWRITE_RECOVERY_EXHAUSTED`

Aider stderr:

`The config file doesn't appear to contain 'key: value' pairs ... yaml.load(.../.forgelab-aider.conf.yml) returned type 'NoneType' instead of 'dict'.`

Exact root cause:

ForgeLab writes `.forgelab-aider.conf.yml` as an empty file. Aider expects a
YAML mapping, so an empty document is invalid for its config loader.

Remediation:

`config_file.write_text("{}\\n", encoding="utf-8")`

Regression:

A fake Aider process exits 2 unless the generated config is exactly a valid
empty YAML mapping. The source repository must remain unchanged.

No engine behavior beyond this integration bug is changed.

## 14. Sixth real Dental dashboard run — Aider process failure visible

Run:

`run-160a0cc0cc6a`

Runner:

`f09ec5801fb9...`

Dashboard blocker:

`PREWRITE_RECOVERY_EXHAUSTED`

Phase:

`implementation`

Final error:

`Aider initial pre-write correction did not complete successfully: exit=2, timed_out=False`

This proves PR #56 is active: the initial Aider correction is attempted.

Current evidence gap:

The adapter already captures Aider stdout/stderr, but the orchestrator discards
them when a non-zero process exit is converted into a terminal error. Therefore
`exit=2` alone is insufficient to distinguish CLI parsing, model/provider
failure or another subprocess problem.

Smallest next change:

`PRESERVE_BOUNDED_AIDER_STDERR_STDOUT_IN_FAILURE_EVIDENCE`

Do not change retry/editor behavior until the next dashboard blocker includes
the actual Aider process output.

## 14. Fifth real Dental dashboard run — exact blocker visible

Run:

`run-f667d5cdf772`

Runner:

`a9f3cb7c9511...`

Dashboard blocker:

`PREWRITE_RECOVERY_EXHAUSTED`

Phase:

`implementation`

Final error:

`AI Developer Python candidate does not parse in quote_calculator.py at line 50: f-string: unmatched '['`

Interpretation:

PR #55 observability is working. The blocker is no longer inferred.

The initial Aider implementation path still sends a pre-write-invalid Aider
candidate to the legacy custom pre-write recovery path. That violates the
REUSE-FIRST reset and recreates the fragile editor boundary.

Smallest remediation:

`AIDER_INITIAL_PREWRITE_CORRECTION_ONCE`

Expected path:

`Aider initial candidate -> deterministic pre-write FAIL -> exact error +
failed candidate returned to Aider once -> pre-write validation -> ToolGateway
-> tests -> Reviewer -> Security -> human gate`

No custom f-string normalization is authorized at this stage.

## 14. Fourth real Dental dashboard run

Run:

`run-1df61ea4f109`

Visible evidence:

- `CLOSED`;
- Gate `Repair`;
- TEST `FAIL`;
- repair attempts applied `0`;
- provider cost `EUR 0`;
- 2 LLM calls / 3443 tokens.

The run is FAIL, but the dashboard does not expose the terminal failure
artifact needed to distinguish:

- pre-write recovery exhaustion;
- local provider failure;
- deterministic test failure;
- semantic review failure;
- generic closed-before-decision state.

Therefore the next change is **observability only**.

Candidate branch:

`mvp1-dashboard-terminal-blocker-observability`

Expected UI after merge:

- active runner Git SHA visible;
- red `BLOCCO CORRENTE` card on CLOSED runs;
- phase;
- machine-readable reason;
- final error/detail;
- direct link to the supporting evidence artifact;
- no misleading ForgeLab internal fallback files in target-run changes.

No Product Owner diagnostic log transport is required.

## 14. Third real Dental dashboard run — synchronized runtime

Run:

`run-08dcbcbfe1a3`

Visible evidence:

- `CLOSED`;
- Gate `Repair`;
- TEST `FAIL`;
- repair attempts applied `0`;
- provider cost `EUR 0`;
- 2 LLM calls / 3599 tokens.

This run was executed after local `main` synchronization, so it is valid
evidence against the merged PR #53 runtime.

Root cause class:

`AIDER_FAILED_TEST_REPAIR_PREWRITE_CANDIDATE_NOT_CORRECTED`

Smallest remediation:

- keep the same top-level repair attempt;
- if Aider's failed-test repair is rejected by deterministic pre-write
  validation, send that validation error back to Aider once;
- validate again;
- only then allow ToolGateway apply;
- preserve retest, Reviewer, Security and human gate.

No Product Owner diagnostic action is required.

## 14. Second real Dental dashboard run

Run:

`run-bee503005ab4`

Dashboard evidence:

- `CLOSED`;
- Gate `Repair`;
- TEST `FAIL`;
- `0/1` tests PASS;
- repair attempts applied `0`;
- provider cost `EUR 0`;
- 6 LLM calls / 15669 tokens.

Root cause trace:

The initial Aider path is active, and PR #52 moved semantic-review repair to
Aider. However, deterministic test-failure repair still uses the legacy custom
JSON/snippet Developer path.

Current candidate:

`PR #53 — MVP-1: keep failed-test repair on reusable Aider path`

Expected governed flow after merge:

`Aider initial edit -> test FAIL -> Support diagnosis -> Aider bounded repair -> ToolGateway -> retest -> Reviewer -> Security -> human gate`

No new repair budget, no paid provider, no Dental-specific product logic.

## 14. Single next action

`HUMAN_REVIEW_VALID_EMPTY_AIDER_CONFIG_PR`

No Product Owner diagnostic command is required.

## 15. Resume protocol

1. read `AGENTS_MASTER.md`;
2. read `MANIFEST.md`;
3. read `PROJECT_STATE.md`;
4. read `ROADMAP.md`;
5. read `DECISIONS.md`;
6. read this handover;
7. read `DENTAL_QUOTE_AUTONOMY_GATE.md`;
8. verify canonical `main`;
9. verify the active integration PR head/state;
10. stop at human merge gate unless explicit approval exists;
11. after merge, perform the Dental product proof through the dashboard only.

Do not resume frozen PR #37–#48 work unless a new real product-run blocker specifically justifies a general behavior from them.

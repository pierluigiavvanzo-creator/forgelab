# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-06  
**Checkpoint:** First real Dental run reached tests PASS but semantic gate repair  
**Status:** PRE-MVP / Aider semantic-repair candidate

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

## 14. Single next action

`HUMAN_REVIEW_AIDER_SEMANTIC_REPAIR_PR`

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

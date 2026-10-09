# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-09
**Checkpoint:** PR #68 merged / semantic repair no-op evidence and bounded correction
**Status:** PRE-MVP / no-op correction at HUMAN REVIEW GATE / original model motive UNVERIFIED / Golden Path NOT PASS

## Current checkpoint — semantic repair no-op

Delivery: [PR #69](https://github.com/pierluigiavvanzo-creator/forgelab/pull/69), OPEN/unmerged; code `555d6ee` and evidence/state `bf0b0bc` pushed. Later delivery-link update is documentation only.

Main local/remote `741ba4f65a10a7d3628dec74982477d0108492f1` includes merged PR #68. Latest fresh `run-1772ceaf77f0`: CLOSED / REPAIR, six helper tests PASS, EUR 0, two ledger calls and two editor calls. Candidate has one treatment UI, no visible subtotals/aggregate/UI tests. Reviewer partially correct; Extraction/Implant helper support exists despite its claim.

Semantic Aider returned zero authorized net changes. ForgeLab incorrectly treated that as format/prewrite recovery exhaustion and reported zero repairs; no prewrite recovery actually ran. Original successful editor stdout/stderr and sandbox snapshots were not retained. The precise historical model/CLI cause is unverified; full root-cause diagnosis is not PASS.

Branch `fix/semantic-repair-noop-root-cause` records no-op objective/output/hash evidence and truthful accounting, verifies identical content before reusing tests, and independently reconsiders the current candidate once. Persistent blockers -> CLOSED/SEMANTIC_REPAIR_NOOP/REPAIR; acceptance -> existing Security/human gates. No generic retry, budget increase, Dental fix/run/promotion or PR #68 bypass. Running 8875 health reports main `741ba4f`; existing services are preserved.

Complete handoff: [no-op report](../audits/FORGELAB_SEMANTIC_REPAIR_NOOP_ROOT_CAUSE_2026-10-09.md). Single next action: `HUMAN_REVIEW_AND_MERGE_SEMANTIC_REPAIR_NOOP_FIX`. Do not launch Dental now. Earlier dated checkpoints are historical.

Internal gate PASS on code `555d6ee`: 108 Python tests, four dashboard callbacks, Aider preflight/pip consistency, production build, actual readiness and Windows stability 6/6. This validates the ForgeLab outcome correction; it does not recover the discarded historical Aider response or establish Golden Path PASS.

## Historical checkpoint — repeated semantic repair

Delivery: [PR #68](https://github.com/pierluigiavvanzo-creator/forgelab/pull/68), OPEN/unmerged, code `59537cf` and evidence/state `dd6db94` pushed. Later delivery-link updates are documentation only.

Canonical fetched main is `ad6f460e8b3cc43f041badd4686d8b09676b27c1`, containing PR #67. Child `run-a65d908fd535` of `run-797899d24f2a` is REVIEW / tests PASS / Repair required. The final candidate has three treatment rows and visible subtotals, but UI total ignores discount (230 instead of 217) and the six passing tests exercise only the helper. Reviewer is partially correct; its absent-implementation assertions and evaluator-instruction requirements are inaccurate.

Native repair previously discarded the unpromoted parent candidate and restarted from source baseline. The new branch `fix/repeated-semantic-repair-root-cause` validates and carries forward the parent's final cumulative patch into planner and governed isolated editor writes, records lineage hashes, rejects stale/incompatible evidence, and reviews complete current files once with the acceptance contract. The duplicate review diff caused observed input truncation; it is removed without weakening blocking review or changing provider/model/budgets.

Dental remains clean at `42e026093960a8acc4cb64087433d90c5f537efb`. No new target run/edit/promotion. Services on 8875/5273 and historical 8765/5173 are preserved; 8875 health reports baseline `ad6f460...`, so a running service is not proof that this new fix is loaded. Separate launcher hardening `ea00719` remains unmerged.

Handoff report: [2026-10-09 audit](../audits/FORGELAB_REPEATED_SEMANTIC_REPAIR_ROOT_CAUSE_2026-10-09.md). Single next action: `HUMAN_REVIEW_AND_MERGE_REPEATED_SEMANTIC_REPAIR_FIX`. Do not start Dental now. Historical entries below do not supersede this checkpoint.

Internal stabilization PASS on `59537cf`: 105 Python tests, four dashboard callbacks, preflight, production build, initial readiness and 6/6 stability. Verification services on 8876/5274 were stopped only after ownership/no-active-run checks; original listener PIDs remain unchanged. See audit for commands, failed diagnostic attempts and remaining risks. No remote CI or Dental PASS is claimed.

## Historical checkpoint — Ollama semantic correction

Fetched local/remote main is `d9f6d2faa6fa776244f96a2be1df9d296d76d1f2`. The later real repair `run-a9a839fc1963` exhausted its provider retry in semantic correction. The single candidate branch `fix/ollama-repeat-limit-recovery` adds the missing explicit JSON contract and removes the duplicate diff in that prompt. Live reproduction: original repeat limit -> one unload -> corrected retry SUCCESS, with existing schema/syntax validation and EUR 0. No Dental output was applied and no Dental run was started.

Full evidence and limits: [root-cause report](../audits/FORGELAB_OLLAMA_REPEAT_LIMIT_ROOT_CAUSE_2026-10-08.md). Model/options, retry/repair budgets, timeouts and human gates remain unchanged. Separate launcher hardening at `ea00719` is unmerged. The following UTF-8 checkpoint is historical.

## Historical checkpoint — UTF-8 fix and interrupted run

## Verified checkpoint — Windows Aider UTF-8 and interrupted Dental run, 2026-10-08

- Canonical fetched `main`: `2227c2487b8858738db7bcf38cdcebeff4699c4f`, containing merged PR #65. PR #66 branch: `fix/aider-windows-utf8-noninteractive`; reviewed code commit `08d1a7dccaa48d29f4d22d30422db1408d030be2`; documentation-only head before this update: `d75cb21cdd1374ad4bc546d7cec67e8101fafc9d`.
- Observed `run-7e1ae59bf235/EditorFailure.json` records implementation failure, cp1252/U+FEFF, GitHub-report prompt and timeout 124. The old service on 8765 reports SHA `96b1083ecb2e67f79728338fdbaaa3ed6f3f948b`, not canonical main; its health SHA is not treated as proof of the historical run SHA.
- Independently reproduced on canonical main with a disposable BOM fixture and installed Aider 0.86.2, without model calls: UnicodeEncodeError -> interactive report prompt -> timeout/exit 124. The boundary-only correction is exactly `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` in the isolated child environment plus `stdin=subprocess.DEVNULL`. No BOM/source normalization, global environment change, dependency/provider/model change, retry or timeout increase.
- After correction: BOM path exit 0; controlled crash path exit 1 with immediate EOF and preserved stdout/stderr. Focused evidence: 102 Python tests and 4 dashboard callbacks PASS; compileall, Aider preflight, `pip check`, production build, Windows launcher readiness and 6/6 stability checks PASS.
- One initial launcher invocation failed existing API test `test_create_run_accepts_ai_generate_without_old_new` (FAILED instead of READY_FOR_DECISION). The isolated test, diagnostic API suite and final launcher later passed. **Cause remains undiagnosed; do not claim this intermittent failure is resolved.**
- The Product Owner then started Dental run `run-1d9f29b59db7` from the dashboard at **2026-10-08 18:07:50 Europe/Rome**. The dashboard showed runner `08d1a7dccaa4`, therefore the run used the candidate containing the UTF-8 process-boundary fix.
- During later cleanup of the verification environment, Codex stopped the services without first proving that no run was active. This interrupted the runtime and caused the dashboard `Failed to fetch`. Existing run artifacts were preserved; `RunSummary.json` is absent. `AIReview.json` reports `FAIL`, but it is intermediate evidence only and is **not** a complete run conclusion.
- After explicit Product Owner authorization, Codex restarted the services **without rerunning Dental**. The API reconciled the existing run automatically to `INTERRUPTED`, `terminal=true`, with message `ForgeLab API restarted before run completion`. `completed_at` at **2026-10-08 18:49:15 Europe/Rome** records reconciliation at restart, not the exact interruption time.
- Pre-existing run artifacts and the Dental target Git state were unchanged during service restoration. Codex performed no promotion and no manual Dental code modification.
- Last observed restored runtime: API `http://127.0.0.1:8875`; dashboard `http://127.0.0.1:5273`; runtime SHA `d75cb21cdd1374ad4bc546d7cec67e8101fafc9d`; readiness and stability PASS; services were left running for consultation. This is the **last observed state, not a guarantee of current runtime state**. Standard ports `8765/5173` still belonged to the preserved old checkout.
- Evidence classification: **UTF-8/non-interactive technical gate PASS; Dental run INTERRUPTED; Golden Path #1 NOT PASS.**
- Separate launcher ownership/cleanup work remains local on `fix/post-pr65-final-stabilization` at `ea00719`; it is outside PR #66 and must not be described as integrated or merged. Original best-effort egress and dependency-fingerprint limitations remain.

Earlier dated entries are historical; this checkpoint and the single next action supersede stale PR #65 review instructions.

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

`2227c2487b8858738db7bcf38cdcebeff4699c4f`

This is the merge of PR #65:

`Fix post-PR64 run lifecycle gaps and synchronize verified project state`

PR #60–#65 are merged. Runtime PRs #37–#48 remain frozen/unmerged. Current review branch is `fix/aider-windows-utf8-noninteractive` (PR #66). Separate launcher work at `fix/post-pr65-final-stabilization` / `ea00719` remains local and is not integrated.

## 5. Historical integration sequence (superseded by current checkpoint)

The active Aider/Dental integration chain through PR #58 is merged to `main`.

Latest merged sequence:

- PR #51 — dashboard Dental run uses reusable Aider editor;
- PR #52 — semantic repair stays on reusable Aider path;
- PR #53 — failed-test repair stays on reusable Aider path;
- PR #54 — one bounded Aider pre-write correction on failed-test repair;
- PR #55 — dashboard terminal blocker + active runner SHA observability;
- PR #56 — initial pre-write correction stays on reusable Aider path;
- PR #57 — Aider stderr/stdout preserved in terminal failure evidence;
- PR #58 — valid empty YAML mapping written for isolated Aider config.

PR #59 was a documentation-only merge after PR #58. PR #60–#65 subsequently merged timeout/failure/isolation, consolidated Aider stabilization and corrected post-PR64 lifecycle gaps.

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

All four Aider phases now use `_run_aider_editor`: implementation, initial pre-write correction, failed-test repair and semantic-review repair. No custom-editor fallback is claimed for those Aider phases.

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

## 14. Post-PR58 evidence state

PR #58 is merged to canonical `main` at:

`566ffa0cdc7b4f3212709bbb6efc290f553728e6`

The most recent verified real Dental dashboard run remains:

`run-ebf29be889fe`

That run occurred before PR #58 and therefore remains FAIL evidence for the previous runtime, not for current `main`.

Its exact blocker was the zero-byte isolated Aider YAML config. PR #58 fixes that blocker by writing a valid empty YAML mapping:

`{}\n`

Current evidence classification:

- PR #58: **MERGED**;
- exact previous blocker: **FIXED IN CODE**;
- post-PR58 real Dental dashboard validation: **PENDING**;
- Dental Golden Path #1: **NOT PASS YET**;
- next blocker: **UNKNOWN UNTIL THE NEXT DASHBOARD RUN**.

No later verified Dental run after PR #58 was found at this checkpoint.

## 15. Eighth real Dental dashboard run — Aider timeout root cause

Run:

`run-a949ce0afbb9`

Active local runner shown by dashboard:

`566ffa0cdc7b...`

Visible outcome:

- status `CLOSED`;
- gate `Repair`;
- repair attempts applied `0`;
- provider cost `EUR 0`;
- blocker `PREWRITE_RECOVERY_EXHAUSTED`;
- phase `implementation`;
- final error `Aider initial pre-write correction did not complete successfully: exit=124, timed_out=True`.

Interpretation:

The PR #58 config-file bug is no longer the blocker. Aider starts and produces an initial candidate. ForgeLab then requests its one bounded pre-write correction, but the subprocess is terminated by the same 60-second timeout used for tests and ordinary routed model calls.

Root cause in current runtime:

`Dashboard timeout_seconds=60 -> MultiAgentRequest.timeout_seconds=60 -> every Aider EditorRequest.timeout_seconds=60`

This is a cross-phase resource-contract bug. It is not a Dental-specific failure and should not be handled by manually raising a timeout in the dashboard.

PR #60 remediation:

- generic/test/provider timeout remains 60 seconds;
- separate bounded `editor_timeout_seconds` defaults to 300 seconds;
- API validates 60..600 seconds;
- every Aider phase uses the editor timeout;
- `ExecutionPlan.json` records both timeout classes;
- human repair child-runs preserve the editor timeout;
- top-level repair budget remains unchanged;
- no additional retry, provider, dependency or Dental-specific logic is added.

Candidate branch:

`mvp1-aider-phase-timeout-policy`

Candidate code commit:

`10088be7142b67c3df61bac70e3a0421323563e5`

PR:

`#60 — MVP-1: separate bounded timeout for local Aider editor`

## 16. Post-PR60 submission — editor result lifecycle bug

After PR #60 was merged and the local runtime was restarted, the unchanged Dental submission did not create a new governed result. The dashboard surfaced:

`run execution failed: UnboundLocalError: cannot access local variable 'editor_result' where it is not associated with a value`

The evidence still visible for `run-a949ce0afbb9` is historical FAIL evidence and must not be approved.

Exact root cause:

`EditorAdapterError -> AIDeveloperFormatError -> pre-write correction path -> editor_result.files -> UnboundLocalError`

When Aider fails before returning an `EditorResult`, the runtime incorrectly treats the process/sandbox failure as if a candidate existed and tries to correct that nonexistent candidate.

PR #61 remediation:

- distinct `AIEditorExecutionError` for reusable-editor process/sandbox failures;
- no candidate correction when no candidate exists;
- consistent classification across initial implementation, initial pre-write correction, failed-test repair and semantic-review repair;
- governed terminal artifact `EditorFailure.json`;
- reason `EDITOR_EXECUTION_FAILED`;
- API exposes the artifact;
- dashboard displays it as the current blocker;
- state machine closes as `CLOSED` instead of leaking an API-level exception;
- no extra retry, no paid provider and no Dental-specific logic.

Candidate branch:

`mvp1-govern-aider-execution-failures`

Code candidate:

`77ad51de6337b09a5782341ef1777311589440a9`

PR:

`#61 — MVP-1: govern reusable editor execution failures`

## 17. Post-PR61 real Dental run — tool metadata isolated incorrectly

Run:

`run-0a7fb9e16cf5`

Runner:

`b20a4236bee1...`

Outcome:

- `CLOSED`;
- gate `Repair`;
- `EDITOR_EXECUTION_FAILED`;
- phase `implementation`;
- repair attempts `0`;
- provider cost `EUR 0`;
- one local LLM call;
- Aider tool metadata was reported as unauthorized:
  - `.aider/analytics.json`;
  - `.aider/caches/model_prices_and_context_window.json`;
  - `.aider/installs.json`.

This proves PR #61's governed editor-failure path is active and working.

Exact root cause:

The Aider adapter currently uses one temporary directory for both the disposable code workspace and Aider's `HOME` / `USERPROFILE`. Aider's normal tool metadata therefore appears inside the same filesystem tree that ForgeLab validates as target-product scope.

PR #62 remediation:

```text
temporary sandbox
├── workspace/     # authorized target/read-only files only
└── tool-home/     # HOME/USERPROFILE, Aider config/prompt/env and .aider metadata
```

Candidate behavior:

- Aider runs with `cwd=workspace`;
- `HOME` and `USERPROFILE` point to `tool-home`;
- ForgeLab/Aider control files live in `tool-home`;
- only `workspace` is checked for product scope;
- any unauthorized file inside `workspace`, including hidden files, remains a hard failure;
- source repository remains untouched;
- no retry, provider, dependency, repair-budget or Dental-specific behavior is added.

Candidate branch:

`mvp1-isolate-aider-tool-home`

Code candidate:

`a92195cdd35903ca9d3e4af79b0a6b9a38a0617f`

PR:

`#62 — MVP-1: isolate Aider tool home from editor workspace`

## 18. Post-PR62 real Dental run — CWD-relative Aider history file

Run:

`run-f564070471df`

Runner:

`96b1083ecb2e...`

Outcome:

- `CLOSED`;
- gate `Repair`;
- `EDITOR_EXECUTION_FAILED`;
- phase `implementation`;
- repair attempts `0`;
- provider cost `EUR 0`;
- one local LLM call;
- blocker detail: `Aider created files outside authorized scope: .aider.chat.history.md`.

Interpretation:

PR #62 correctly isolated HOME-owned tool metadata from the code workspace. This remaining file is different: Aider's documented default chat-history path is relative to the current working directory unless explicitly configured.

PR #63 remediation:

- explicitly pass `--chat-history-file <tool-home>/.aider.chat.history.md`;
- proactively pass `--input-history-file <tool-home>/.aider.input.history`;
- keep `cwd=workspace`;
- keep `HOME` and `USERPROFILE` on `tool-home`;
- keep the workspace scanner strict with no history-file exception or hidden-file bypass;
- preserve source-repository isolation and all existing zero-spend / bounded-repair rules.

Candidate branch:

`mvp1-route-aider-history-to-tool-home`

Code candidate:

`a1c379c1c799338ac223384f573bdb8216b4bc84`

PR:

`#63 — MVP-1: route Aider history files to tool home`

## 19. Complete Aider stabilization sweep — PR #64

Product Owner instruction:

Stop symptom-by-symptom Aider PRs and stabilize the component comprehensively before another Dental run.

PR:

`#64 — MVP-1: complete Aider integration stabilization gate`

Branch:

`mvp1-aider-integration-stabilization-gate`

Audit:

`docs/audits/FORGELAB_AIDER_INTEGRATION_STABILIZATION_AUDIT_2026-10-07.md`

Consolidated behavior:

- one Aider execution/error boundary across all four editor phases;
- explicit deterministic 0.86.2 CLI profile;
- strict product workspace + isolated tool-home/history/model metadata;
- minimal safe inherited environment;
- loopback-only Ollama validation;
- best-effort subprocess egress guard;
- governed delete/non-UTF8/OS-launch/timeout edge cases;
- dashboard explicitly sends 300-second editor timeout while generic pipeline timeout remains 60 seconds;
- runtime evidence records editor/network policy;
- launcher validates required Aider CLI flags and `pip check`;
- launcher captures dependency freeze + SHA-256 fingerprint;
- launcher executes adapter/orchestrator/API/dashboard focused tests;
- create-run returns `202 + run_id` immediately;
- durable `RunStatus.json` + polling;
- browser refresh resumes active polling;
- only one top-level run can be active;
- stale in-flight status is recovered after API restart.

Validation truth:

This candidate has regression coverage but has not yet produced Windows/local PASS evidence. No GitHub Actions workflow is present, therefore no remote CI PASS is claimed.

## 20. Single next action

`HUMAN_REVIEW_AND_MERGE_SEMANTIC_REPAIR_NOOP_FIX`

Review the single correction PR from `fix/semantic-repair-noop-root-cause`. No merge or Dental submission is automated. Historical statements above are superseded by the current checkpoint and no-op report; original discarded editor response must not be reconstructed by speculation.

## 21. Resume protocol

1. Read `AGENTS_MASTER.md`, `AGENTS.md`, `MANIFEST.md`, current project state, roadmap and decisions.
2. Read [the semantic no-op report](../audits/FORGELAB_SEMANTIC_REPAIR_NOOP_ROOT_CAUSE_2026-10-09.md).
3. Verify Git again: baseline `main = 741ba4f65a10a7d3628dec74982477d0108492f1`; PR #68 is merged. Do not assume the new no-op correction has merged or is loaded by the running service.
4. Preserve `DENTAL_QUOTE_AUTONOMY_GATE.md`, source protection, zero paid-provider cost and human promotion.
5. Resolve the single current review/integration gate before recommending another unchanged Dental run.

The earlier dated run/candidate sections are retained as history, not current instructions. Do not resume or close frozen PRs #37–#48 without Product Owner direction.

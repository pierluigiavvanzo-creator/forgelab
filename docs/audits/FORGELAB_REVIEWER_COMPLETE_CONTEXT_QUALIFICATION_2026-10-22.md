# ForgeLab — Reviewer qualification with complete context

Date: 2026-10-22 (Europe/Rome)
Class: D — diagnostic, prerequisite to Dental
Result: **FAIL — neither configuration qualifies the production reviewer**

## Authorization and baseline

Task C authorizes reviewer-only replay of existing synthetic candidates: local qwen2.5-coder:7b with a diagnostic context override, then gemma4:31b-cloud only if local fails. EUR 0; signed-in loopback Ollama only; no editor calls, Dental, purchases, production configuration/route changes, promotion or merge. Exactly eight sequential reviews per configuration were executed, with no retries, new smoke or response corrections. The cloud run began only after the local gate failed.

Branch: `codex/reviewer-complete-context-qualification`, based on synchronized remote main `0af139848b75e774383eb1a7bf5d1f37982e2634` (PR #76 merged). The requested code baseline `4dfb0ab596ba1d94b2fc27abc7e81b1ac6645b97` remains identical: the intervening merge changes documentation only. Initial worktree clean. Ollama reports 0.40.4. API/dashboard/Ollama were left running.

## Why 2050 rather than 4096 — VERIFIED

Pinned official [Ollama v0.40.4 source, llama_server.go lines 299–348](https://github.com/ollama/ollama/blob/v0.40.4/llm/llama_server.go#L299-L348) resolves the cause. Line 310 accepts tokenized input up to `num_ctx - 1`. On overflow with context shift enabled, lines 328–334 retain the prefix and suffix using the limit calculated at line 347: `numCtx - max((numCtx-numKeep)/2, 1)` (integer division).

For the recorded `num_ctx=4096`, `keep=4`, this is `4096 - floor((4096-4)/2) = 2050`. It is the retained size **after overflow**, not a universal 2050-token input ceiling. No `num_predict` reservation appears in this calculation. Task B logs show one slot with `n_ctx_slot=4096`, excluding division among parallel slots. Its warnings record 4475/4815 input tokens reduced to 2050 at source line 334. Thus the cause is the overflow/context-shift policy, not output reservation or parallelism.

The pinned source is saved locally alongside Task C evidence. New local logs confirm one slot with `n_ctx_slot=8192`, complete input counts, and `truncated = 0` for all eight requests.

## Method and immutable evidence

The runner compiles and evaluates the actual `review_prompt` f-string AST from `src/forgelab/orchestrator.py:4105`, rather than maintaining a rewritten prompt. Builder SHA-256: `dc1ec8cee48f87c41276e7872194c7318d89907a54fecc967e423b91d466505b`. Candidate wrapping and production test-output tails are preserved. The saved real Task B planner response is validated with `_validate_ai_plan` and serialized as production does. Each request carries the unchanged `_ai_review_response_schema()` and each raw response is checked with `_validate_ai_review` (line 775). No normalization or repair makes an invalid response pass.

The objective bytes retain SHA-256 `9203af70c369efc9d9ef6fa0707afc243cca418021e01b081bd78f52db64670a`. Protected fixture hashes remain:

- `inventory_app.py`: `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`
- `test_inventory_app.py`: `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`

| Candidate | Reused evidence | Existing generated tests | Existing independent acceptance |
|---|---|---|---|
| GOOD initial | all-real-roles-2026-10-21/run-1/editor-1.json | 9 PASS, child exit 0 | 6/6 |
| GOOD final | all-real-roles-2026-10-21/run-1/editor-2.json | 11 PASS, child exit 0 | 6/6 |
| BAD discount | qualification-qwen3-4b-instruct-2/result.json | child exit 1 | 6 cases, 5 failures / 1 error; missing aggregate discount validation |
| BAD helper | qualification-ministral-3b-1/result.json | child exit 1 | 6 cases, 1 error; calculate_item missing final_total |

No candidates or tests were regenerated. GOOD test stdout/stderr comes from production TestEvidence.json. Earlier BAD checkers stored stdout+stderr combined; that exact recorded combined text is provided as stderr with stdout empty, then the production 2500-character tail applies. Original separate streams cannot be reconstructed. Independent acceptance is the adjudication oracle, not extra evidence injected into the prompt. Per-file and per-prompt hashes are in the local manifest; all sixteen submitted prompt hashes were checked against it.

Requests use `/api/generate` at `http://127.0.0.1:11434`, stream false, temperature 0.1, num_predict 2048, timeout 60 s, diagnostic num_ctx 8192. No other generation setting changed. Each call is stateless (no previous response/context sent); two sequential rounds cover the same four candidates. Tokenizer-specific input counts need not match between model families.

## Results

### qwen2.5-coder:7b / diagnostic num_ctx=8192

| Review | Input tokens | Output tokens | Wall seconds | Raw/model status | Qualification |
|---|---:|---:|---:|---|---|
| 1-bad_discount | 4,513 | 764 | 48.563 | FAIL | FAIL |
| 1-bad_final_total | 3,988 | 382 | 25.922 | FAIL | FAIL |
| 1-good_final | 4,815 | 606 | 37.156 | FAIL | FAIL |
| 1-good_initial | 4,475 | 542 | 42.109 | PASS | PASS |
| 2-bad_discount | 4,513 | 779 | 54.203 | FAIL | FAIL |
| 2-bad_final_total | 3,988 | 582 | 37.390 | FAIL | FAIL |
| 2-good_final | 4,815 | 624 | 43.703 | FAIL | FAIL |
| 2-good_initial | 4,475 | 657 | 44.797 | PASS | PASS |

Totals: 35,582 input + 4,936 output = 40,518 tokens; 333.843 s summed observed wall time. Configuration gate: **FAIL**.

### gemma4:31b-cloud / requested num_ctx=8192

| Review | Input tokens | Output tokens | Wall seconds | Raw/model status | Qualification |
|---|---:|---:|---:|---|---|
| 1-bad_discount | 5,324 | 906 | 7.187 | Invalid production JSON contract | FAIL |
| 1-bad_final_total | 4,681 | 865 | 5.093 | Invalid production JSON contract | FAIL |
| 1-good_final | 5,699 | 1,009 | 3.078 | Invalid production JSON contract | FAIL |
| 1-good_initial | 5,289 | 952 | 4.094 | Invalid production JSON contract | FAIL |
| 2-bad_discount | 5,324 | 939 | 4.094 | Invalid production JSON contract | FAIL |
| 2-bad_final_total | 4,681 | 978 | 5.110 | Invalid production JSON contract | FAIL |
| 2-good_final | 5,699 | 948 | 4.125 | Invalid production JSON contract | FAIL |
| 2-good_initial | 5,289 | 924 | 5.109 | Invalid production JSON contract | FAIL |

Totals: 41,986 input + 7,521 output = 49,507 tokens; 37.890 s summed observed wall time. Configuration gate: **FAIL**.

### Adjudication against code and independent evidence

Local: GOOD initial passes twice. GOOD final fails twice with false blockers. Round 1 denies three-item support, correct aggregate calculation and tests; round 2 denies exact-count enforcement and JSON final_total. The candidate contains `if len(items) != 3: raise ValueError`, sums the item subtotals and serializes final_total, with passing direct tests and 6/6 independent acceptance. Both BAD candidates are rejected twice for unrelated or contradicted claims; neither pair identifies its documented defect. Local gate: 2/8 individual cases meet the required judgment; configuration FAIL. Completing the context fixes truncation, not reviewer reliability.

Cloud: all eight responses fail the unchanged production validator with `AI Reviewer missing fields: findings, schema_version, summary`. The schema was present in every request; the observed end-to-end path did not produce schema-conforming output. Some overall statuses are `SATISFIED`, also outside the required PASS/FAIL enum. This does not establish which remote component failed to enforce the format.

As a separate reading of the raw, rejected text: all four GOOD reviews are nonblocking; both BAD discount reviews block only failing/outdated tests while incorrectly marking aggregate discount validation satisfied. The code applies `discount / 100` directly in render_estimate without aggregate `_number` or range validation. Both BAD helper reviews mention missing calculate_item.final_total, but simultaneously mark helper preservation satisfied. A test-suite FAIL is not proof of identifying the required real defect. Even ignoring schema incompatibility, the two missed discount defects fail the semantic gate. Cloud production-compatible cases: 0/8; configuration FAIL.

The unchanged canonical objective contains a historical blocking-review description. Several local findings repeat its obsolete claims. Anchoring on that text is a **hypothesis**, not a proven causal explanation; this task did not rewrite or ablate the prompt.

## Context, resources and cost

Every request has an append-window capture of the actual Ollama server log: same file identity, no rotation/truncation, matching POST completion, and no input-truncation/context-shift warning. Local `task.n_tokens` matches response prompt_eval_count for every review, and each release logs `truncated = 0`. Maximum local input 4815 + maximum permitted output 2048 = 6863, below 8192.

Cloud input counts are the returned prompt_eval_count (4681–5699); identical prompts have identical counts on both rounds. All local proxy log windows have no truncation warning. Remote inference logs and whether cloud honors num_ctx=8192 internally are **NOT VERIFIED**; absence of a proxy warning is not proof of unseen remote internals. Reported maximum input 5699 plus 2048 output allowance is below 8192. All sixteen HTTP responses are 200 and done_reason=stop; no timeout, load failure, quota or billing error occurred.

Local memory was sampled throughout inference (322 samples, roughly 1 s cadence; API/GPU samples roughly 5 s). The declared abort floor was 1 GiB available physical RAM. Minimum observed free RAM: **1,498,341,376 bytes (1.395 GiB)**; no threshold stop. llama-server observed resident peak: **2,360,508,416 bytes**; private committed peak: **6,754,226,176 bytes**. Ollama-reported model VRAM peak: **4,104,734,637 bytes**; nvidia-smi peak GPU used 4021 MiB. Peaks are sampled observations, not guaranteed instantaneous maxima or hardware safety guarantees for larger prompts/concurrent applications.

During cloud replay, local model residency remained from the diagnostic; 37 resource samples showed minimum free RAM 1,547,890,688 bytes. Its resident/VRAM values are not Gemma's remote memory footprint. No PO applications were closed or services restarted.

Cost: **EUR 0**. Local tokens 40,518; cloud tokens **49,507** (41,986 input / 7,521 output). No payment, upgrade, credits, API key, direct cloud endpoint or dashboard session token used. Account allowance/billing pages were not accessed; the PO must read remaining session/weekly usage before deciding future cloud work.

## Verification and limitations

VERIFIED: 16 bounded reviewer-only calls; exact production builder/schema/validator reused; hashes checked; no logged truncation; local complete-token evidence; both gates FAIL; generated/acceptance evidence reused without inference duplication. No editor, Dental, approval, promotion, production code/config/route, timeout or budget change. Runtime evidence remains ignored under `.forgelab/runtime/semantic-completion-audit/reviewer-complete-context-2026-10-22/` (manifest, requests, raw responses, validation results, log windows, resources, adjudication and compact-summary.json).

NOT VERIFIED: remote internal context processing; account quota balance; larger-context memory headroom; reviewer reliability outside this fixture; effect of any future prompt change. Planner and Support were not qualified here. No new full Python suite was run for documentation-only changes; existing candidate test evidence was deliberately reused. Neither editor qualification nor correct GOOD candidates makes Dental ready.

## Concrete proposal — separate implementation PR, not applied

Introduce a **reviewer-specific context configuration** with `num_ctx=8192`, `num_predict=2048`, temperature=0.1 and the existing 60 s timeout. Pass it only for Role.REVIEWER; leave Planner/Support's options and all routes/models unchanged. Preserve strict response validation and add context/usage evidence at the reviewer boundary. This exact configuration removes the demonstrated local truncation for this fixture, but **must not be described as resolving the semantic blocker**: the local 8K gate already failed. Do not route production review to Gemma on the strength of this audit, and do not silently coerce its invalid responses.

The implementation should have focused tests proving reviewer-only option selection, unchanged other roles, complete context evidence and fail-closed schema errors. A subsequent, separately authorized prompt/contract qualification would still be needed to resolve false findings and Gemma schema/discount misses. No evidence here supports a passing replacement route.

Single next action: PO reviews this audit and Ollama usage, then decides whether to authorize the separate reviewer-context implementation PR, with Dental remaining blocked.

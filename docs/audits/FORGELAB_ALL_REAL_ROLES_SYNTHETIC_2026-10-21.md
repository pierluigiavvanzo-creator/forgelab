# ForgeLab — all-real-role synthetic diagnostic — 2026-10-21

## Verdict

**FAIL for end-to-end readiness; diagnostic completed. Do not proceed to Dental with the current non-editor route unchanged.** The local reviewer path must be qualified with complete input context, or separately approved for migration, before Dental. The evidence does not establish that the 7B model is intrinsically incapable: its review inputs were demonstrably truncated. Planner succeeded once; Support was not exercised and is not qualified by this run.

Run 1 closed after false blocking reviews and a downstream no-op correction rejection. Run 2 was **not executed**, as required when Run 1 does not reach READY_FOR_DECISION. No further inference was performed after closure; subsequent checks were deterministic replay only.

## Scope and precheck

Class D, synthetic-only, EUR 0. Baseline main = origin/main `4dfb0ab596ba1d94b2fc27abc7e81b1ac6645b97`, containing Task A / merged PR #75; tree clean. Documentation branch: `codex/all-real-roles-synthetic-audit`.

Production entry point: `run_multi_agent`, the same function invoked by the API worker at `src/forgelab/api.py:848`. No API/dashboard session token was read or used. A fresh isolated two-file Git repository was copied from the protected fixture; artifacts went to a separate ignored runs directory. Observation wrappers called the original router, editor and state-machine implementations and returned the real results; no planner/reviewer/provider response was substituted. The Aider child wrapper recorded completion usage without changing model parameters, retry behavior or flags. Task A's error observer remained active.

Unchanged request defaults: non-editor/test timeout 60 seconds, editor timeout 300 seconds, max_repair_attempts 1; Aider 0.86.2, whole format; S1/S2 qwen2.5-coder:7b; editor gpt-oss:120b-cloud primary / gemma4:31b-cloud alternative. No role, route, model, timeout, budget, gate or production file was changed. The canonical objective bytes, including its recorded acceptance context, were passed unchanged; this was not reduced to its first paragraph.

Protected SHA-256:
- inventory_app.py: `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`
- test_inventory_app.py: `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`
- objective: `9203af70c369efc9d9ef6fa0707afc243cca418021e01b081bd78f52db64670a`

Ollama 0.40.4 was reachable. qwen2.5-coder:7b (Q4_K_M, digest `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`) loaded successfully with an empty prompt and context 4096 in 7.438 seconds; done_reason=load, no generated text. The empty-prompt precheck was local only, not a cloud call or a second run.

Ollama PID 1980 / port 11434, ForgeLab API PID 62456 / port 8765 and dashboard PID 62440 / port 5173 were identical before and after. Services were neither stopped nor restarted. Their in-memory code version was not assumed to have changed; the isolated diagnostic imported the synchronized production source directly.

## Run 1 outcome and phase history

Run ID `all-real-roles-1`; total duration **167.187 seconds**. Final status **CLOSED**, decision **Repair required**, tests **PASS**, repair_attempts **1**. Protected fixture and synthetic source repository stayed unchanged.

`RECEIVED -> PRECHECK -> PLANNED -> ISOLATED -> IMPLEMENTING -> TESTING -> SMOKE_TEST -> REVIEW -> REPAIRING -> TESTING -> SMOKE_TEST -> REVIEW -> REPAIRING -> CLOSED`

The human gate was never approved and nothing was promoted. **Gate representation differs from the requested PENDING:** the unchanged production failure path writes `GateDecision.json` with actor SYSTEM, decision REPAIR, gate_type G3_PROMOTE. This artifact was not rewritten to manufacture a PENDING result. There is no human approval. SecurityReport is PASS with no findings/denials and source unchanged, but the successful-path SECURITY_CHECK/READY_FOR_DECISION transition was not reached.

## Actual role/model calls

| Step | Real role/model | Latency | Input / output tokens | Result |
|---|---|---:|---:|---|
| plan | PROJECT_MANAGER, S1 qwen2.5-coder:7b | 23.031 s | 2,003 / 498 | Structured plan accepted; all six canonical criteria retained |
| implementation | Aider, gpt-oss:120b-cloud | 23.750 s | 3,069 / 3,265 | Exit 0; two files changed |
| review-0 | REVIEWER, S1 qwen2.5-coder:7b | 35.922 s | 2,050 / 806 | FAIL; six blocking findings, contradicted by implementation/tests |
| semantic_review_repair | Aider, gpt-oss:120b-cloud | 19.781 s | 5,348 / 4,111 | Exit 0; added tests only; application unchanged |
| review-1 | REVIEWER, S1 qwen2.5-coder:7b | 35.109 s | 2,050 / 751 | FAIL; repeated false claims about count, names and discount |
| semantic_review_correction | Aider, gpt-oss:120b-cloud | 28.125 s | 9,057 / 4,707 | Exit 0; unchanged candidate; rejected before write |

Editor latencies include the editor subprocess, not just model inference. UsageReport records the three local calls (all attempt 1, no retry); EditorRouting records the three real editor invocations, all PRIMARY / EDITOR_COMPLETED, without switch, timeout or cloud-stop signal. Exact cloud token counts come from observed completion usage.

Cloud total: **17,474 input + 12,083 output = 29,557 tokens**, across three completions. The two repair/correction calls after blocking review consumed **23,223** of these tokens. The bounded semantic repair and its correction were existing production behavior, not additional diagnostic runs or a budget increase.

Tester executed real Python unittest children. Security/deterministic review used real deterministic production checks. **Support had zero provider calls**: tests never failed, so the S2 Support branch did not run. RunSummary includes SUPPORT in selected_roles because repair_attempts is nonzero; that list is not evidence that Support actually ran. UsageReport and observations establish actual execution.

## Reviewer findings versus independent evidence

The first candidate passed 9 generated tests (actual child exit 0) and the unchanged independent harness **6/6**, zero failures/errors. After semantic repair, the final written candidate passed 11 generated tests (actual child exit 0) and independent acceptance **6/6**, zero failures/errors. The final candidate was independently reconstructed from Changes.patch and matched editor invocation 2 exactly; invocation 3 returned those same bytes with no changed paths.

Both versions share application SHA-256 `120ea2dc7951a9d3267158918eeee802ec97cef026065854b943a7a4292477c7`. Initial test SHA `b11101f38dd7bff8202b0d2bcd5f26de2aa87ca3a33f55bcae3fca499698d4ac`; final test SHA `71efba4c4a0841193f256c93d3b63c45272801359ccc15abd237bd52d5e06b70` (UTF-8 candidate text).

| Reviewer claim | Contradicting candidate evidence |
|---|---|
| Exactly-three restriction absent, including CLI | inventory_app.py:53-54 rejects len != 3; main:97 calls render_estimate; generated invalid-count tests and independent test_counts/test_cli pass |
| Unsupported names not handled | :26-27 rejects unsupported names; render_estimate:71-73 delegates to calculate_item; supported-name tests and independent test_validation pass |
| Invalid prices/quantities not handled | _number rejects booleans/nonfinite values; :28-32 checks price and positive integral quantity; direct tests pass |
| Invalid discounts not handled, including CLI | :56-58 validates aggregate discount; main:97-99 invokes/catches validation; discount/endpoint tests pass |
| Invalid item data not handled | :65-69 checks item objects/required fields; generated malformed/missing-field tests pass |

Thus the reviewer **rejected candidates that passed the specified gate and asserted absence of behavior that exists**. This is not a claim of exhaustive correctness beyond the gate. No incorrect-candidate approval was observed; both real reviews returned FAIL.

## Failure classification and context evidence

Primary class: **REVIEWER / truncated local context / false blocking findings**. Secondary terminal mechanism: **unchanged editor correction rejected by deterministic pre-write validation** with `AI Developer full-file recovery files must be a non-empty authorized subset`. That was not an editor timeout, model-unavailable error, quota stop, failing generated test or RAM allocation error.

Production `src/forgelab/ollama_provider.py:137-140` sets num_ctx=4096 and num_predict=2048. The production review prompt includes the objective, acceptance contract, complete candidate files and test evidence (`orchestrator.py:4083-4177`), but the actual local model input was truncated by Ollama:

```text
time=2026-10-21T23:08:47.270+02:00 level=WARN source=llama_server.go:334 msg="truncating input prompt" limit=2050 prompt=4475 keep=4 new=2050
time=2026-10-21T23:09:43.305+02:00 level=WARN source=llama_server.go:334 msg="truncating input prompt" limit=2050 prompt=4815 keep=4 new=2050
```

These times align with review-0 and review-1; UsageReport reports prompt_eval_count/input_tokens 2050 for each. The truncated-input condition is VERIFIED. That truncation explains the missing-implementation claims is a strong causal hypothesis, not a completed counterfactual proof: no full-context rerun or model change was authorized/performed. The exact omitted token sequence and the model's behavior with full context are NOT VERIFIED.

## Observed RAM / VRAM

33 samples approximately five seconds apart; these are observed maxima/minima, not continuous peak guarantees. Precheck loading samples are recorded separately.

| Measurement during Run 1 | Observed value |
|---|---:|
| Local llama-server resident working-set maximum | 1,699,729,408 bytes (1.70 GB decimal) |
| Local llama-server private commit maximum | 6,181,122,048 bytes (6.18 GB; not physical resident RAM) |
| qwen2.5-coder:7b VRAM allocation, /api/ps maximum | 4,199,263,764 bytes (4.20 GB) |
| System physical RAM available minimum | 721,928,192 bytes (0.72 GB) |
| Resource sampling errors | 0 |

The model loaded and completed all three local calls, with no timeout/OOM in run evidence. Low remaining physical RAM is a residual operating risk; this is not hardware headroom qualification. Other running services were preserved.

## Evidence and limits

Ignored runtime root: `.forgelab/runtime/semantic-completion-audit/all-real-roles-2026-10-21/`.

- precheck.json and services-before/after.json;
- run-1/request.json, objective.txt, diagnostic-summary.json, observations.jsonl and resource-samples.jsonl;
- run-1/runs/all-real-roles-1/{RunSummary,EditorRouting,UsageReport,GateDecision,ReviewReport,AIPlan,AIReview,TestEvidence,SecurityReport}.json and Changes.patch;
- editor-1/2/3.json, cloud-completions.jsonl, ollama-truncation-evidence.txt, postcheck-summary.json;
- candidate-1 and final-candidate test-summary.json, generated-tests.txt and independent-acceptance.txt.

No runtime logs, model output, credentials or synthetic execution repositories are included in this documentation PR. The existing six-case checker was reused, changing only its evidence directory. No production source/configuration changed; the Task A 192-test suite evidence is reused, not claimed as a new full-suite execution for this documentation-only diagnostic.

VERIFIED: one real production-orchestrator run; real planner/two reviewers/three primary editor completions; both deterministic candidate gates pass; repeated false reviewer blocks; prompt truncation; no source changes, service restarts, approval, promotion, paid action or Dental transfer. No quota/credit error was observed.

NOT VERIFIED: repeatability (Run 2 intentionally not run), Support capability, alternative editor in this run, reviewer with full context, intrinsic model capability, account remaining allowance/billing, Dental readiness, exhaustive candidate correctness. Runtime-only details remain local and are unavailable from GitHub alone.

Cost: **EUR 0** under the authorized Free-plan route; no credits/payment method/upgrade/purchase. Local ledger spent=0. Exact account debits/remaining Free quota were not inspected; tokens above are measured usage, not a claim of unlimited allowance.

## Single next action

Authorize one bounded qualification of the reviewer path with complete context before any Dental decision; decide any configuration/model migration in that separate scope. Do not change routing or increase limits in this documentation PR.

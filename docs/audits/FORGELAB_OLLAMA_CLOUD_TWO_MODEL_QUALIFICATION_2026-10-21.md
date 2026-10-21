# ForgeLab — Two Ollama Cloud Free-plan model qualifications — 2026-10-21

## Result

**PASS for the synthetic qualification: gpt-oss:120b-cloud 2/2; gemma4:31b-cloud 2/2.** Four sequential independent executions; no new smoke, retries, manual candidate fixes, reasoning-setting changes or additional inference. Each editor exited 0 within 300 seconds, its generated-test child exited 0 and independent acceptance passed all six cases.

Class D diagnostic to unblock A-class semantic repair. Both larger cloud models can complete the unchanged fixture through Aider. This supports the practical hypothesis that the prior local execution/model path was the blocker, and demonstrates Aider can complete this gate. It does not isolate hardware from model capability or prove production/Dental readiness.

## Authorization and baseline

The Product Owner explicitly extended the 2026-10-21 diagnostic-only ADR-002 exception to exactly two models, in order: `gpt-oss:120b-cloud`, then `gemma4:31b-cloud`, each with exactly two independent executions unless a stop condition occurs. Model 2 remains required even if model 1 passes, to establish a second qualified candidate against retirement. PO reported same-day minimal probes returned HTTP 200 with no credits purchased; these probes were not repeated or independently reclassified as agent evidence.

Only signed-in local Ollama at `http://127.0.0.1:11434`; synthetic fixture/objective only; EUR 0 Free plan. HTTP 402/429 or quota/credit messages require STOP. No purchase, payment method, upgrade, trial, direct cloud API/key, credentials handling, other model, Dental, promotion, merge, production source/configuration change, timeout/budget expansion or manual model-output correction is authorized. The prior retired Qwen model was not called.

Live fetched remote main remained `b9ba77db5db89ffdf4e5fdda41de18cfaca9e23c`; PR #72 was not in main. As authorized, the clean branch was created from PR #72 head `a4be803e7449aa600d05c024ea30e6a26190e9ac`, on `audit/ollama-cloud-two-models-2026-10-21`. The new documentation PR targets the PR #72 branch so its review diff contains only this follow-up; retarget to main after #72 merges. No merge was performed.

## Unchanged qualification contract

Reused `run-llama31-q3ks-1.py` / `check-llama31-q3ks-1.py`. Clones were verified by reverse substitution to differ only in model and case directory. Installed Aider 0.86.2, whole format, original flags, no-stream, 300-second timeout, one generation per execution, no external retry. The adapter uses isolated candidate workspaces and local Ollama. No running ForgeLab service was stopped or restarted.

Canonical objective bytes were reconstructed before execution and checked in all four case artifacts: SHA-256 `9203af70c369efc9d9ef6fa0707afc243cca418021e01b081bd78f52db64670a`.

Protected fixture hashes, checked before and after all executions:

- `inventory_app.py`: `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`.
- `test_inventory_app.py`: `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`.

## Executed evidence

| Model | Run | Editor exit | Editor seconds | Generated tests / actual child exit | Independent acceptance | Input / output tokens | Final content |
|---|---:|---:|---:|---:|---:|---:|---|
| gpt-oss:120b-cloud | 1 | 0 | 15.500 | 10 / 0 | 6/6 | 2548 / 3117 | Yes |
| gpt-oss:120b-cloud | 2 | 0 | 18.202 | 9 / 0 | 6/6 | 2548 / 3529 | Yes |
| gemma4:31b-cloud | 1 | 0 | 13.484 | 9 / 0 | 6/6 | 2871 / 2163 | Yes |
| gemma4:31b-cloud | 2 | 0 | 12.640 | 9 / 0 | 6/6 | 2871 / 2143 | Yes |

All four changed exactly `inventory_app.py` and `test_inventory_app.py` in their candidate outputs; `source_unchanged=true` in every run. No timeout. Each trace captured one model completion with finish reason `stop`. gpt-oss final content was present in both executions; neither was reasoning-only. The baseline trace does not record a separate reasoning field, so reasoning token/content breakdown is NOT VERIFIED. No flags were changed to obtain final content.

Total reported usage: 10838 input + 10952 output = 21790 tokens across four completions. These are provider/Aider usage fields, not measured account credit debits or a production token-saving benchmark.

Acceptance covers quantitative three-item output, CLI integration, item counts, invalid values, preserved helper and discount endpoints. Generated-test exit codes were captured from the actual child process, not inferred from checker exit. All independent cases passed (24/24 across four runs).

The first gpt-oss trace contained one malformed auxiliary JSONL line. Its model-completion event, raw final content and usage were valid, as were editor result and both test artifacts. The reporting helper initially failed parsing that auxiliary line; the summary was recovered from already saved evidence without rerunning inference or tests. Subsequent collection tolerates malformed auxiliary lines and records their count. Runner/checker clones and model output were not altered. No malformed lines were found in the other three traces.

## Local evidence and validation

Ignored evidence root: `.forgelab/runtime/semantic-completion-audit/`. Case directories: `qualification-gpt-oss-120b-cloud-1`, `qualification-gpt-oss-120b-cloud-2`, `qualification-gemma4-31b-cloud-1`, `qualification-gemma4-31b-cloud-2`. Each contains objective, command, editor prompt, stdout/stderr, raw completion trace, candidate/result, generated tests, independent acceptance and test summary. Aggregate precheck and execution summaries are in `two-cloud-qualification-2026-10-21/`. Runtime evidence stays local/ignored.

Publication changes only this audit, DECISIONS.md, PROJECT_STATE.md and HANDOVER_CURRENT.md. No production source/configuration was modified. Validation includes fixture/objective hashes, clone equality, actual child exit codes and the unchanged independent harness. Full application tests are not claimed for a documentation-only change. Publication checks passed: exactly four staged Markdown files, clean diff whitespace, ignored runtime evidence and zero matches in the bounded tracked-file credential scan. A pattern scan cannot prove absence of every possible secret.

## Cost, quota and limitations

Budget EUR 0; no payment action, credit purchase, upgrade, paid activation or paid fallback. No HTTP 402/429 or quota/credit failure was observed. Free-plan status is PO-provided; the account was not accessed. Actual monetary debit, remaining quota and whether a Dental run fits Free are NOT VERIFIED. Aider token counts do not establish monetary cost.

PO: read the Ollama usage page after these four runs and report session/weekly usage if displayed, otherwise monthly included credits remaining and reset date. Do not buy credits or upgrade. No new smoke or model run is needed for this check.

Both candidates qualify only on this synthetic gate. Production routing, fallback behavior, end-to-end security/reviewer gates and Dental remain untested/unmodified. Dental Golden Path remains NOT PASS. Model retirement and Free-plan allowance remain external dependencies.

## Decision and single next action

**Next action:** PO approval of a separate implementation PR and ADR-002 update for semantic-repair routing, informed by the post-run usage check. Proposed scope: gpt-oss as primary cloud candidate, qualified gemma4 as a retirement alternative, and retain the local model fallback subject to unchanged acceptance gates; stop on credit/quota failures. This is a proposal only. Local fallback has not passed this gate and cannot bypass verification. No routing/configuration or Dental execution is authorized by this qualification result.

Rollback: close the unmerged documentation PR or revert its documentation commit; local ignored evidence does not affect production execution.

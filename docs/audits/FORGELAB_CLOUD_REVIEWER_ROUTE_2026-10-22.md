# ForgeLab — cloud reviewer route and one production synthetic run

Date: 2026-10-22
Class: A — remove the reviewer routing blocker while preserving fail-closed review.
Result: **Implementation tested; end-to-end gate FAIL. PR must remain unmerged.**

## PO authorization and baseline

Baseline main `67265731ef096d6b4e714568c32d9c7a3105d914`, PR #78 merged; worktree initially clean. Branch `codex/cloud-reviewer-route`. The PR #78 [confound/contract audit](FORGELAB_REVIEWER_GATE_CONFOUND_AND_CONTRACT_FIX_2026-10-22.md) was read before implementation.

On 2026-10-22 the PO explicitly accepts moving REVIEWER to cloud **without separate qualification rounds**, to save time. Primary gemma4:31b-cloud provides a different model family from the gpt-oss editor; gpt-oss:120b-cloud is permitted once only on primary unavailability and must be recorded as reduced independence. Quota/credit/billing/402/429 stops; never local reviewer fallback. Planner and Support remain local qwen2.5-coder:7b; editor chain unchanged. Only signed-in local Ollama at http://127.0.0.1:11434, EUR 0, synthetic data only. No purchases, Dental, promotion or service restart.

Exactly one production run is authorized. One additional run with gpt-oss reviewer primary is conditional on failure **only** from Gemma strict-validation failure or demonstrably wrong review. Merge is authorized only after an end-to-end PASS. Neither condition was met here: no second run and no merge.

## Smallest implemented slice and reuse

- `ModelRouter.execute_reviewer` is a dedicated REVIEWER policy independent of S1/S2. Validated immutable model configuration allows only the authorized cloud pair (or the PO's conditional gpt-oss-only configuration). Legacy calls naming REVIEWER also use this policy; S0 still prohibits inference.
- Reuses PR #75 `editor_cloud_stop_reason` exclusively on trusted provider exceptions. Generated review text is never scanned. Only model-unavailability switches; quota takes precedence, transient errors stop without local reset/retry. Alternative uses the remaining original deadline. Attempts, model, tokens, outcome, switch reason and independence are recorded in UsageReport.
- Reuses unchanged PR #78 OllamaProvider context sizing/truncation checks and exact review output contract/strict validator. No schema coercion. Validation failure writes REVIEWER_CONTRACT_INVALID; provider STOPs write REVIEWER_CLOUD_QUOTA_STOP / REVIEWER_MODEL_UNAVAILABLE / REVIEWER_PROVIDER_ERROR in ReviewerFailure.json and close the run. ReviewerResponse.json preserves the last raw response and route attempts. AIReview history records the model and attempts per round.
- Orchestrator review call uses the dedicated route; Planner/S1, Support/S2, editor/Aider, gates, timeouts, repair budgets and routing.yaml remain unchanged. Launcher and dashboard run-mode notes identify cloud review and reduced-independence fallback.

Value: removes the shared S1 routing constraint without moving the planner or weakening independent review. This does not claim completed product value or reviewer qualification from one run.

## Offline validation

Focused provider/router/contract tests: 41 PASS before final S0/UI adjustment. Final focused reviewer/UI tests: 24 PASS. Final full Python suite: **213 PASS in 76.896 s**, including 13 new reviewer tests. They cover primary, 404/410/retired/not-found fallback, quota precedence and STOP, both unavailable, transient STOP, never-local configuration/legacy entry, S0 prohibition, unchanged Planner/Support, no classification of completion text, zero-cost enforcement and production failure artifacts/usage.

An initial suite exposed a removed dashboard text invariant; the existing ChatGPT assistance indicator was restored and the final suite passes. No tests were weakened: the prior local retry-timeout test now uses Support because Reviewer no longer belongs to that local retry policy. No new dependencies. Dashboard changes are text only; no separate build/browser smoke or service restart was performed.

## Exactly one production run

Entry point: actual `run_multi_agent`, also used by API/dashboard, from this branch. Observation wrappers call and return the real implementations; no planner/reviewer response stubs, generated-code fixes or additional inference. Isolated runs directory and fresh Git copy of the protected two-file fixture. max_repair_attempts=1, provider timeout 60 s, editor timeout 300 s.

Objective: **only the first canonical product paragraph**, asserted identical to PR #74 smoke. UTF-8 SHA-256 `ebb6eb21a7293a6850eece17653625f949067ffdfeafb90cf8cada10446ba5f0`. No stale blocking review or repair instructions from the old qualification objective.

Fixture SHA-256:

- inventory_app.py: `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`
- test_inventory_app.py: `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`

Run `cloud-reviewer-1`: **REVIEW**, not READY_FOR_DECISION, after 108.375 s. History: RECEIVED → PRECHECK → PLANNED → ISOLATED → IMPLEMENTING → TESTING → DIAGNOSING → REPAIRING → TESTING → SMOKE_TEST → REVIEW. One repair consumed by the initial generated-test failure; no semantic repair budget remained. Original protected fixture and source repository unchanged.

| Role / call | Model | Input | Output | Seconds |
|---|---|---:|---:|---:|
| PROJECT_MANAGER / plan | qwen2.5-coder:7b | 1284 | 540 | 36.719 |
| SUPPORT / support-1 | qwen2.5-coder:7b | 742 | 367 | 20.405 |
| REVIEWER / review-0 | gemma4:31b-cloud | 4132 | 936 | 3.062 |
| Editor 1 | ollama_chat/gpt-oss:120b-cloud | 2393 | 3107 | 21.156 |
| Editor 2 | ollama_chat/gpt-oss:120b-cloud | 4024 | 2972 | 26.015 |

All provider attempts succeed technically; no model fallback, quota error, timeout or truncation warning. Gemma returns production-valid JSON with one genuine BLOCKER. Cloud tokens: **17,564** = editor 6,417 input + 6,079 output and reviewer 4,132 input + 936 output. Local Planner/Support: 2,026 input + 907 output. Cost **EUR 0**; no payment action, direct cloud API/key or PO dashboard token. Account remaining quota is not inspected.

## Failure evidence and gate adjudication

The first editor candidate accepts one through three items instead of exactly three. Its generated `test_render_estimate_three_items` asserts aggregate 20 for `10 + 6 + 3` (actually 19); ten generated tests run, one fails, child exit 1. Planner's contract correctly retained exactly three items.

Local Support diagnoses this arithmetic mismatch incorrectly as a rounding problem and asserts the test needs no correction (AIDiagnostics.json). The cloud editor's bounded repair adds `aggregate_subtotal = round(aggregate_subtotal / 10) * 10` (final inventory_app.py line 61). All 10 generated tests then pass, child exit 0, but the candidate now rounds correct totals to tens. This is repair fitting an incorrect generated assertion, not a reviewer routing failure.

Gemma correctly blocks that exact rounding line. No blocking finding is contradicted by the code. However, its requirements list incorrectly marks exactly-three satisfied despite citing `1 <= len(items) <= 3` (line 45): this is a reviewer coverage miss, not the sole cause of run failure and not grounds for the conditional rerun.

The unchanged six-case independent harness is applied to the actual final Changes.patch reconstructed over the protected baseline. **2/6 test methods pass**, 4 fail, with 5 failure records because invalid-count subcases fail twice; zero errors. Helper preservation and validation pass. CLI/visible totals/discount endpoints fail (aggregate 40 instead of 45; discounted 36 instead of 40.5), and counts 1/2 are wrongly accepted. Generated tests independently rerun: 10 PASS, exit 0. The end-to-end gate is unequivocally FAIL.

The unchanged production failure path writes human gate **SYSTEM/REPAIR**, not PENDING. It was not rewritten to imply success; no approval or promotion occurred. PENDING would require READY_FOR_DECISION. Because actual candidate defects exist and strict review validation succeeds, the fallback condition is false. No gpt-oss reviewer run, manual candidate fix or third attempt.

## Delivery, limitations and next action

VERIFIED: full suite green; cloud-only reviewer routing and evidence; one real local Planner/Support + cloud editor/reviewer run; valid reviewer contract and true blocking finding; independent acceptance failure; protected sources unchanged; API 62456 / dashboard 62440 / Ollama 1980 still listening on the original ports. Runtime evidence remains local/ignored at `.forgelab/runtime/semantic-completion-audit/cloud-reviewer-production-2026-10-22/` (runner, raw observations, completions, production artifacts, checker, resources, logs and test suite).

NOT VERIFIED: broader reviewer quality, live unavailable/quota paths (offline-tested only), remaining Free allowance, remote context internals, Dental readiness and live dashboard behavior. Existing PO services were not restarted to load branch changes. This branch is not deployed by this task.

One code+documentation PR, **NO MERGE** because the PO's conditional merge gate failed. Rollback: discard/revert this unmerged branch; production main remains the baseline. No production source is promoted.

Single next action: PO reviews this PR and authorizes a separate bounded fix for incorrect generated-test expectations and repair reasoning before another end-to-end run.

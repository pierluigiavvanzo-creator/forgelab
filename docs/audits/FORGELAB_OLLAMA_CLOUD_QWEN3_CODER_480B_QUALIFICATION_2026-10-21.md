# ForgeLab — Ollama Cloud Qwen3 Coder 480B qualification, 2026-10-21

## Result

**BLOCKED — requested cloud model unavailable; qualification NOT EXECUTED.** The single authorized smoke returned HTTP 410 in 0.343 seconds. Ollama reported that `qwen3-coder:480b` was retired on July 15, 2026. No alternate model was tried. No conclusion about model capability versus Aider can be drawn from a model-availability failure.

Class D, hypothesis-driven diagnostic intended to unblock the A-class semantic-repair blocker. Hypothesis: a larger cloud coding model can satisfy the unchanged gate where local models have failed. Hypothesis remains untested.

## Product Owner authorization

On 2026-10-21 the Product Owner explicitly authorized a scoped exception to ADR-002's no-provider/model-expansion rule: only this qualification, only `qwen3-coder:480b-cloud`, only through the signed-in local Ollama service at `http://127.0.0.1:11434`, with only the synthetic qualification fixture eligible for cloud transfer. Account creation and credential handling were excluded.

Budget was EUR 0 on the owner's Free plan. No Pro/Max, trial, purchased credits, paid activation or spend was authorized. Exhausted quota, authentication failure or model unavailability required STOP. Dental execution, promotion, production source/configuration changes, merge, other models, direct ollama.com API/key use, timeout/repair-budget increases and manual model-output correction were prohibited. The requested publication was one documentation-only branch/PR, without merge.

## Verified precheck

- Clean local `main`; local HEAD and live `git ls-remote origin refs/heads/main` both `b9ba77db5db89ffdf4e5fdda41de18cfaca9e23c`.
- Ollama 0.40.4; installed Aider distribution 0.86.2.
- Shared governance body hash matches the previously read AGENTS_MASTER v2.2; project instructions, state, handover and ADR-002 guardrail inspected.
- Read Qwen3 4B qualification and small-model-search audits from `backup/model-qualification-audits-2026-10-09`.
- Protected fixture exists under `.forgelab/runtime/semantic-completion-audit/fixture/` with both `inventory_app.py` and `test_inventory_app.py`. Contents match the recorded historical baseline.
- Most recent inspected standalone runner/checker: `.forgelab/runtime/run-llama31-q3ks-1.py` and `check-llama31-q3ks-1.py`; canonical six-case acceptance is present. These retain the original objective, contract and protected fixture, and the runner bounds generative requests.
- Reconstructed current canonical semantic objective is byte-identical to the recorded `qualification-llama31-q3ks-1/semantic-objective.txt` with the original Windows newline encoding. SHA-256: `9203af70c369efc9d9ef6fa0707afc243cca418021e01b081bd78f52db64670a`.
- Fixture SHA-256: inventory `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`; tests `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`.

## Executed smoke

Exactly one POST to `http://127.0.0.1:11434/api/generate`, with no authentication material read or supplied by the diagnostic:

```json
{"model":"qwen3-coder:480b-cloud","prompt":"Reply with exactly OK.","stream":false}
```

HTTP 410; elapsed 0.343 s. The response explicitly reports retirement on July 15, 2026. The server's alternative-model suggestion was not acted upon. No retries or direct cloud API requests were made by the diagnostic. The two qualification executions were not started. No fixture content was sent because the smoke was the only inference request.

`prompt_eval_count` and `eval_count` were not returned: NOT AVAILABLE, not measured zeros. No completion was returned, no editor candidate exists, generated tests and the six acceptance cases were not executed for this cloud model. Gate 2/2: NOT EVALUATED, not partial PASS and not two failed model executions.

## Cost and quota evidence

Authorized cost: EUR 0. No paid plan, trial, credit purchase, payment change or paid fallback was activated. The request was rejected as retired. Actual account debits and remaining allowance were not independently inspected; no claim of an account balance measurement is made. The owner's Free-plan declaration is authorization context, not an account lookup performed by the agent.

The public [Ollama pricing page](https://ollama.com/pricing), checked on 2026-10-21, describes starter credits on Free, monthly refresh and optional purchased credits; it does not establish this account's balance or billing state. [Cloud documentation](https://docs.ollama.com/cloud) also describes model retirements.

PO quota check requested: read the session/weekly usage shown on your Ollama usage page after this smoke, if those counters exist for your plan; if the page instead shows monthly starter credits, report the remaining included allowance and reset date. Do not buy credits or upgrade. A future Dental run's fit within Free is NOT VERIFIED, and no Dental run is authorized by this task.

## Evidence and preservation

Local ignored evidence: `.forgelab/runtime/semantic-completion-audit/ollama-cloud-precheck-2026-10-21/{precheck.json,smoke-request.json,smoke-result.json}`. Existing model outputs, fixture, runners and checkers were not modified. No production services were stopped or restarted. No production source/configuration, provider route, model inventory, timeout, repair budget or Dental file was changed.

Only four Markdown documents are proposed: this audit, DECISIONS.md, PROJECT_STATE.md and docs/handovers/HANDOVER_CURRENT.md. The latter two record the current blocker and correct their cleanup checkpoint to the merged history; historical test results are not represented as new validation. Runtime evidence stays ignored.

Publication checks: the staged diff is limited to four Markdown documents; `git diff --check` passes; runtime evidence is ignored; a bounded credential-pattern scan of tracked files and the new audit reports no matches. This pattern scan is not a proof that arbitrary secrets cannot exist in historical content. No full application suite is appropriate for this documentation-only stop outcome.

## Decision and single next action

Failure class: PROVIDER_MODEL_RETIRED / MODEL_UNAVAILABLE, not MODEL_QUALITY, AIDER_FORMAT, hardware exhaustion or quota exhaustion. The model-specific exception is consumed by this stopped diagnostic and does not extend to another model or production use. No routing PR is proposed because the 2/2 gate was not evaluated.

**Next action:** Product Owner decides whether to authorize a separate qualification of one explicitly named, currently available Free-plan model, informed by the usage-page check. Until then, STOP; no more inference or Dental run.

Publication branch: `audit/ollama-cloud-qualification-2026-10-21`; one documentation-only PR, no merge.

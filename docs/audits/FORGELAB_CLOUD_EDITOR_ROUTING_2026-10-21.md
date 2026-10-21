# ForgeLab — Qualified cloud editor routing — 2026-10-21

## Result and scope

**PASS for the Aider routing implementation and synthetic integration slice.** Class A: removes the proven local-model dependency from every Aider editor phase. One PR, no merge. Baseline local main and fetched origin/main were identical at `eed3a86460ec3c874eb19ed78b4fcb8a8a39647f` (merged PR #73), with a clean tree before branch creation. Branch: `feat/qualified-cloud-editor-chain-2026-10-21`.

PO authorized `gpt-oss:120b-cloud` primary and `gemma4:31b-cloud` alternative, based on PR #73's 2/2 qualification for each. No local fallback. Only the signed-in local Ollama service at `http://127.0.0.1:11434`; no new provider, direct cloud API/key, credential handling, purchase, payment method, upgrade or paid activation. EUR 0 only. This task authorizes synthetic data only; Dental data transfer and execution remain unapproved. No services were restarted and no Dental run occurred.

## Call-site map

| Surface / caller | Before | Implemented route |
|---|---|---|
| `.forgelab/routing.yaml`, S0 | deterministic | unchanged |
| S1 / Project Manager planning | OllamaProvider, local qwen2.5-coder:7b | unchanged |
| S1 / semantic reviewer and re-review | OllamaProvider, local qwen2.5-coder:7b | unchanged |
| S2 / Support diagnosis | OllamaProvider, local qwen2.5-coder:7b | unchanged |
| Aider implementation / initial pre-write correction | S2 model passed to central EditorRequest | shared qualified cloud chain |
| Aider failed-test repair / its pre-write correction | S2 model passed to central EditorRequest | shared qualified cloud chain |
| Aider semantic repair | S2 model passed to central EditorRequest | shared qualified cloud chain |
| Regression-test correction inside Aider run | direct S2 developer call | Aider, same cloud chain |
| Remaining-review correction inside Aider run | direct S2 developer call | Aider, same cloud chain |
| Semantic-repair test correction inside Aider run | direct S2 developer call | Aider, same cloud chain |
| Security, deterministic tests, ToolGateway, promotion gate | deterministic local checks | unchanged; Security has no LLM call in this orchestrator |
| Explicit legacy `custom` editor engine | separate S2 structured-patch path | unchanged legacy path, never selected as Aider fallback |
| S3/S4 | premium routes in configuration | unchanged; production router registers only Ollama and uses zero-spend ledger |
| `Start-ForgeLab.ps1` | Aider installation/version/flag checks, no local-model presence requirement | unchanged, no cloud probe added |

All production Aider requests pass through `_run_aider_editor` and the single `EditorRequest` construction. `EditorModelConfig` provides the validated immutable model pair, independent of S1/S2. The adapter rejects local, unknown and other-provider model requests before starting a process. A structural regression verifies every remaining direct S2 Developer call is guarded by the explicit non-Aider branch; none is reachable in Aider mode. The legacy `custom` engine is not migrated or disabled by this Aider-scoped change; it must not be selected to obtain a local fallback.

`OllamaProvider.invoke` and its existing repeat-limit reset remain untouched for non-editor routes. No global route swap was used. Default EditorRequest no longer names qwen2.5-coder:7b. Existing process environment sanitization, loopback guard and explicit local model metadata remain intact; 'local metadata' means a sandbox metadata file, not local inference.

## Failure and evidence contract

- Primary first. Only model-unavailability signals (HTTP 404/410, retirement or model-not-found) permit one alternative attempt, on a fresh sandbox copied from the original authorized source.
- HTTP 402/429 or quota/credit/billing/rate-limit messages take precedence, including when Aider returns exit 0: `EDITOR_CLOUD_QUOTA_STOP`, no model switch, no governed candidate write or later phase.
- Both unavailable: `EDITOR_MODEL_UNAVAILABLE`. Other process/auth/network/syntax failures retain the governed failure path; they do not trigger fallback.
- Alternative uses only the remaining overall editor deadline. The four original Aider phases keep their existing editor timeout; the three former direct correction calls retain their original `request.timeout_seconds` ceiling. Repair budgets are unchanged.
- `EditorRouting.json` records each phase, attempted model, primary/primary-unavailable reason, result status, exit code, timeout and duration. `EditorFailure.json` preserves the explicit stop reason and closes the run. Candidate metadata reports the actual selected model; run summaries identify cloud inference via the local daemon.
- Aider 0.86.2, whole format and the CLI argument construction are unchanged (AST equality checked). The loopback validation is also byte-structure-equivalent by AST. No retry/reflection flags were changed. Classification occurs when the bounded Aider process returns (including timeout); existing Aider-internal handling is not replaced by this router.

## Tests and exactly one live smoke

Focused routing tests: 12 PASS, including primary use, 404/410 switch, quota precedence, both unavailable, never-local validation, timeout accounting, all seven phase labels, whole-run quota closure, all three correction branches and absence of reachable local developer calls in Aider mode.

Full Python suite: **186 tests PASS in 69.560 seconds**, using `python -m unittest discover -s tests -q`. Existing sandbox, scope, test/review/security and human-gate tests pass. No full-suite inference calls are used.

Exactly one live integration smoke used `run_multi_agent` -> `_run_aider_editor` -> AiderCliAdapter -> Aider 0.86.2 -> local Ollama -> primary cloud model, with the protected synthetic inventory fixture. Planner/reviewer responses were deterministic synthetic fixtures (two responses), not live model evaluations; the production orchestrator, isolation, editor execution, governed candidate writes, deterministic tests and gate machinery were real. This is an integration slice, not a live end-to-end qualification of every role.

- One editor invocation, one captured completion, primary `gpt-oss:120b-cloud`; no alternative, retry or second smoke.
- Orchestrator result `READY_FOR_DECISION`; human gate remains pending, no promotion.
- Elapsed 23.171 s; editor attempt 22.609 s, exit 0, no timeout.
- Generated tests: 8 PASS, actual child exit 0. Independent unchanged acceptance: 6/6.
- Usage: 2,052 input + 3,190 output = 5,242 reported tokens. No separate reasoning-token count returned.
- Protected fixture hashes match PR #73; synthetic source repository remained byte-identical. No manual model-output correction.

Evidence remains ignored under `.forgelab/runtime/semantic-completion-audit/cloud-editor-production-smoke-2026-10-21/`, including `smoke-summary.json`, `editor-result.json`, raw completion/usage trace, independent checker outputs and `runs/run-4d4657c51e40/`. Full-suite output: `.forgelab/runtime/cloud-editor-full-suite-final.txt`. The subsequent correction-route completeness change was verified by deterministic tests; the successful initial-editor smoke was not repeated.

## Verified versus not verified

Verified: routing/control-flow tests, unchanged flags/guard, full Python suite, one primary-model synthetic editor integration, no paid actions, no Dental, no service restart, no model/provider expansion beyond the two authorized candidates.

Not verified: account monetary debits/remaining quota; whether Free can cover Dental; live non-editor role quality; live outage/quota switching (tested with controlled outputs); production/Dental readiness; model availability beyond the observed run. The configured EUR 0 policy and absence of purchase actions do not constitute a measured billing balance. The adapter enforces quota STOP but does not inspect or change account settings.

Residual risks: S1 planner/reviewer and S2 Support still use the previously unreliable local model. Proposed follow-up is a separate bounded qualification of those roles, with explicit authorization before routing changes. The legacy explicitly selected custom engine also remains outside this Aider-only migration. Free quota and future retirements remain external dependencies; the alternative is qualified but may also retire. Cloud source transfer requires PO data authorization for any non-synthetic target.

Publication checks: 11 scoped files; diff whitespace check passed; runtime trace/test evidence ignored; bounded tracked-file credential-pattern scan returned zero matches. This is a bounded scan, not proof against every possible secret.

## Single next action and rollback

PO reads the Ollama usage page after the smoke (session/weekly usage if present, otherwise included credits and reset date), then reviews and decides whether to merge this PR. No merge is performed by this task. Dental data authorization is a separate unresolved decision, not implied by this result.

Rollback: close the unmerged PR; after a separately authorized merge, revert its commit. Do not restore local automatic fallback. Runtime evidence stays local and ignored.

# ForgeLab — provider-only cloud STOP detection — 2026-10-21

## Result

PASS for the bounded false-positive repair; proposed branch, not deployed or merged. Baseline: clean local main = origin/main `8f2c47d7e517cc92eee816960b61cb8cb6dcd40a` (merged PR #74). Branch: `codex/fix-cloud-editor-error-classification`.

Root cause: Aider prints provider errors and whole-format generated code on stdout. Keyword matching the combined stdout/stderr therefore cannot establish error provenance. Exit code 0 also does not prove provider success.

## Change and preserved boundaries

A private child-process `sitecustomize` import observer wraps the pinned Aider `Model.send_completion` boundary. It records raised provider exceptions, including original exception-chain HTTP status codes, to JSONL in isolated tool-home. Successful completion values and rendered stdout/stderr are never classified. ForgeLab reads this separate error evidence, including on timeout. Missing/corrupt observer evidence fails closed. The original exception is re-raised unchanged; no completion, retry, model setting or Aider source is modified. The parent environment and installed packages are untouched.

`editor_cloud_stop_reason` now receives only this provider evidence. The existing quota-first classification and primary/alternative routing remain intact, including provider errors swallowed by Aider before exit 0. The injected PYTHONPATH contains only the private tool-home, not inherited paths or the editable workspace. No dependency was added.

The launcher change is one display string describing gpt-oss:120b-cloud / gemma4:31b-cloud without local fallback. CLI flags, Aider 0.86.2, whole format, model order, loopback route, timeouts, budgets, non-editor roles, gates and human approval are unchanged.

## One authorized real diagnostic

PO authorization: one editor invocation using retired `qwen3-coder:480b-cloud`, synthetic qualification fixture only, signed-in local Ollama only, EUR 0. This is not qualification and does not add that model to production configuration. The ignored diagnostic harness overrode model validation only for that `_run_once` invocation; no chain/fallback was invoked.

Fixture SHA-256 verified before execution:
- inventory_app.py: `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`
- test_inventory_app.py: `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`
- recorded semantic-objective.txt bytes: `9203af70c369efc9d9ef6fa0707afc243cca418021e01b081bd78f52db64670a`

Exactly one Aider invocation: exit 0, 73,655 ms, no timeout, no changed paths, original fixture unchanged. Stdout contains `litellm.APIConnectionError: Ollama_chatException` and the retirement message; stderr is empty. The known HTTP-410 retirement is rendered without its numeric status. Aider made nine internal attempts (eight retry messages) within that one invocation. There were no external retries. These internal retries are disclosed, not counted as one HTTP request. No completion or token usage was returned. Two preceding preflight failures (Python import path and hashing newline-normalized text) occurred before invoking Aider; the recorded raw-byte hash matched.

Runtime evidence: `.forgelab/runtime/semantic-completion-audit/cloud-stop-diagnostic-2026-10-21/{stdout.txt,stderr.txt,result.json}`. The complete non-secret stdout is retained as `tests/fixtures/aider_retired_stdout.txt` for replay. No further live model call was made.

## Source-derived 402/429 evidence

Installed versions: aider-chat 0.86.2; litellm 1.81.10. All paths below are relative to `.forgelab/tools/aider-0.86.2/Lib/site-packages/`:

- `aider/models.py:970-1022`: Model.send_completion calls litellm.completion and returns its result. This is the observed boundary, before rendering.
- `aider/io.py:965-993`: tool_error uses console output, not a distinct stderr-only transport.
- `aider/coders/base_coder.py:946-954,1461-1487`: provider exceptions are displayed and may be retried/swallowed; exit status alone is insufficient.
- `aider/exceptions.py:39-41`: RateLimitError description is `The API provider has rate limited you. Try again later or check your quotas.`
- `aider/exceptions.py:97-105`: the insufficient-credits/code-402 APIError case yields `Insufficient credits with the API provider. Please add credits.`
- `litellm/llms/custom_httpx/llm_http_handler.py:4596-4626`: the HTTP response status and error body become the provider error.
- `litellm/llms/ollama/chat/transformation.py:424-428` and `litellm/llms/ollama/common_utils.py:9-13`: OllamaError retains status_code and message.
- `litellm/litellm_core_utils/exception_mapping_utils.py:1998-2035,2343-2369`: Ollama-specific handling has no dedicated 402/429 mapping; generic mapping can convert these to APIConnectionError.
- `litellm/exceptions.py:699-713`: APIConnectionError has status_code 500. Reading the original exception chain preserves the actual 402/429/410.

Source SHA-256: aider/models.py `593cff096ba8e19ea4147f6e1e79e215f1d6c9c3978477aea7040b9dc2b5188b`; aider/exceptions.py `5996c16821bc39818bc0a8f2b1b6110271b24ae80dc5813c61e395776e19bfe5`; exception_mapping_utils.py `691e6ad63c3ce24a7f3d6c791bfef8bc72ea697d92a34cc3b1a53e1ace057004`.

Offline verification exercised the actual installed Model.send_completion and exception mapping with locally injected OllamaError 402/429/410. Socket connections were forbidden; no cloud request was possible. The observer retained each original status and the adapter returned EDITOR_CLOUD_QUOTA_STOP at child exit 0. Runtime record: `offline-installed-boundary.json`. It includes an asyncio cleanup warning caused by blocking socket creation/connectivity; assertions and process exit were successful. This is source-derived/offline evidence, not a real quota response.

## Tests

- Six new regression tests: all six reported code-like lines, Italian quota/credito, forged full provider output in stdout/stderr, successful actual subprocess edit, captured retirement error, source-derived 402/429, child import hook and original-status preservation, missing/corrupt evidence, successful completions/local exceptions excluded.
- Existing routing suite: 12 PASS, including primary, alternative, quota precedence, both unavailable, never-local, shared deadline and orchestrator evidence.
- Existing adapter suite: 20 PASS. The subprocess-timeout mock also mocks the observer result because it launches no child.
- Full Python suite: **192 tests PASS in 68.697 seconds**, exit 0. Command: `.forgelab/tools/aider-0.86.2/Scripts/python.exe -m unittest discover -s tests -q`, PYTHONPATH=src. Log: `.forgelab/runtime/cloud-stop-full-suite-2026-10-21.txt`.

## Verified / not verified and cost

VERIFIED: no stdout/stderr/completion-driven cloud routing; real captured retirement output; provider-exception replay with exit 0; offline installed boundary; full suite; unchanged protected fixture; no new dependency, credential handling, paid action, service restart, Dental run, promotion or merge. Runtime remains ignored; only the non-secret stdout fixture is tracked.

NOT VERIFIED: real account 402/429, remaining Free allowance/debits, a post-fix live successful cloud edit, Dental Golden Path, live non-editor capability. Existing Aider internal retry behavior remains and can delay a stop; changing retry settings is outside this task. Observer compatibility is pinned to Aider 0.86.2 and needs revalidation if upgraded.

Cost: EUR 0; no purchase/upgrade/payment action and no generated cloud completion. Account billing/allowance was not inspected.

Rollback: revert this PR; note that this restores PR #74's false-positive defect.

Single next action: PO reviews this PR and Ollama usage, then decides whether to merge. No Dental authorization is implied.

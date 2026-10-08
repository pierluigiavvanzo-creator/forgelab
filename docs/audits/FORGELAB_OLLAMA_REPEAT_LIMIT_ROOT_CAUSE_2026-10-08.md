# ForgeLab — Ollama repeat-limit root-cause report, 2026-10-08

## BASELINE

Fetched local/remote `main`: `d9f6d2faa6fa776244f96a2be1df9d296d76d1f2`, PR #66 merged. Correction branch: `fix/ollama-repeat-limit-recovery`; tested code commit: `61aab63`. Later commits in this change set update documentation only.

Real failure: `run-a9a839fc1963`, phase `REPAIRING`, task `review-repair-1-semantic-correction`, two provider attempts, `PROVIDER_TRANSIENT_RETRY_EXHAUSTED`. Deterministic tests had passed, one repair had been used, paid cost EUR 0. The original failure was not inside the Aider child process: the orchestrator's subsequent semantic correction called structured Ollama directly.

## REPRODUCTION

Read-only replay reconstructs current authorized files from `AIDeveloperPatch.json` and its repair delta, the five-field PM contract from `AIPlan.json`, latest semantic review and deterministic evidence, objective from `ExecutionPlan.json`, and `Changes.patch`. It evaluates the exact canonical prompt f-string and invokes the real ModelRouter/OllamaProvider with existing routing, timeout 60 seconds, one retry, unchanged schema and zero budget. Generated output is saved locally and validated, never applied to the target.

Environment: Windows, Python 3.11, Ollama 0.34.2, `qwen2.5-coder:7b`; generation options unchanged: temperature 0.1, context 4096, prediction limit 2048.

| Controlled request | Executed outcome |
| --- | --- |
| Canonical prompt, 17,568 characters | Repeat limit -> successful unload -> repeat limit; two ledger attempts, 93.938 seconds, EUR 0 |
| Context 8192 only | Timeout -> repeat limit; two attempts, 115.422 seconds; not a sufficient repair |
| Explicit output contract only | Timeout -> provider SUCCESS; JSON accepted, Python syntax rejected for unmatched f-string bracket; 124.766 seconds |
| Duplicate diff removed only | Timeout -> repeat limit; two attempts, 103.203 seconds |
| Explicit contract plus diff removal, diagnostic prompt | Timeout -> SUCCESS; JSON and Python syntax accepted; 154.531 seconds, EUR 0 |
| Final source prompt after a real original first failure | Repeat limit -> exactly one unload -> corrected retry SUCCESS; JSON and Python syntax accepted; 134.110 seconds, EUR 0 |

Final trace: request 1 reproduces the original 17,568-character prompt; request 2 unloads with empty prompt and `keep_alive=0`; request 3 uses the actual candidate prompt plus existing recovery suffix, 13,756 characters. Ledger: `RETRY` at attempt 1 (43,047 ms), `SUCCESS` at attempt 2 (91,047 ms), 3,031 input / 1,790 output tokens for the successful request. Both attempts cost EUR 0. The candidate prompt before the recovery suffix is 13,356 characters, versus 17,568 originally.

Local diagnostic harness: `.forgelab/runtime/repeat-limit-repro.py`. Local evidence: `.forgelab/runtime/repeat-limit-proof/`, especially `baseline-result.json`, `context8192-result.json`, `explicit-contract-result.json`, `compact-explicit-result.json`, `compact-result.json` (compaction-only result), `candidate-result.json`, and the three `candidate-request-*.json` traces. These are ignored local artifacts, not committed Dental source. Reproduce the final comparison with `py -3.11 .forgelab/runtime/repeat-limit-repro.py --candidate --baseline-first` while the original run artifacts remain available.

## ROOT CAUSE

The demonstrated defect is request construction on the bounded semantic-correction path: it requests an undefined "required JSON object" without describing the output contract, while embedding other JSON contracts/reviews, and duplicates complete source through the full diff. The provider schema constrains output but did not make this request recoverable. Resetting model state and appending anti-repetition instructions leaves that contract defect intact.

The original retry's Ollama log also reports input truncation from 4,127 to 2,050 tokens. The pinned [Ollama 0.34.2 context-shift implementation](https://raw.githubusercontent.com/ollama/ollama/v0.34.2/llm/llama_server.go) explains the truncation policy. Raising context alone failed in the controlled replay. No claim is made that a specific Ollama/KV/sampling implementation defect has been identified. The comparative tests demonstrate the complete bounded request repair, rather than proving an internal model mechanism.

## CHANGE

- `src/forgelab/orchestrator.py`: remove the duplicated diff only from semantic re-review correction; serialize the existing `_ai_developer_full_file_response_schema(target_paths)` into its prompt and name the full-file response keys. Preserve complete current files, objective/feedback, PM acceptance contract, all latest review obligations, deterministic evidence and existing rules.
- `tests/test_orchestrator.py`: extend the existing end-to-end correction regression to require the textual contract to equal the provider schema, omit the redundant diff and include each authorized file once. New assertions fail on canonical main and pass after repair.
- `tests/test_model_router.py`: extend the existing repeat-limit regression to assert original prompt appears once in recovery, exactly two generation calls, attempts 1/2 and spent cost zero.
- `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `docs/handovers/HANDOVER_CURRENT.md`, `AGENTS.md`, `MANIFEST.md`: record PR #66 as merged, preserve earlier checkpoints as history and set the Ollama human-review gate as the single next action.
- This report preserves reproduction, negative experiments, validation and residual risks for handoff to ChatGPT Web.

No provider/model/options, dependencies/configuration, timeouts, retry/repair budgets, ToolGateway, Reviewer/Security or human promotion policies changed. No Dental source modification, Dental run, paid provider call, automatic merge or old-PR closure occurred. Separate launcher hardening at `ea00719` remains outside this PR.

## TEST EVIDENCE

- Exact extended orchestrator regression: canonical-main FAIL (missing output contract); corrected PASS.
- `tests/test_model_router.py`: 16/16 PASS.
- `tests/test_ollama_provider.py`: 6/6 PASS, including unload and structured format preservation.
- Five adjacent orchestrator regressions: PASS, including governed planning/implementation provider exhaustion and bounded semantic repair.
- Real launcher internal stabilization gate: adapter 19, orchestrator 47, API 25, dashboard source regressions 11 — 102/102 PASS; dashboard lifecycle callbacks 4/4 PASS; Aider contract and `pip check` PASS.
- First production build in the existing checkout: FAIL, `EPERM` deleting `dashboard/dist`, with its existing dashboard still running on 5273. Existing services on 8875/5273 were preserved. No launcher code patch was made for this unrelated boundary.
- First isolated attempt: pnpm correctly rejected an external `node_modules` junction; initial offline preparation lacked policy metadata. Reused the validated policy/package cache and completed the same frozen-lockfile installation offline, exit 0, without downloads or policy bypass. The cache's `projects` link was excluded from further copying; interrupted diagnostic cache-copy attempts did not modify source code.
- Final unmodified Windows launcher in the isolated checkout: PASS, including repeated internal gate, frozen-lockfile supply-chain policy check, four dashboard lifecycle callbacks, production build, initial readiness and all 6/6 stability checks. Existing services on 8875/5273 were preserved. Test services used only 8876/5274.

Logs: `.forgelab/runtime/ollama-repeat-launcher.log`, `.forgelab/runtime/ollama-repeat-launcher-isolated.log`, `.forgelab/runtime/ollama-repeat-launcher-isolated-final.log`, and `.forgelab/runtime/ollama-repeat-isolated-install.log`. Isolated checkout: `C:\Users\NITRO\Documents\GitHub\forgelab-ollama-verify`, detached at the same code commit; Aider is reused through a junction, Node dependencies through the existing package cache, with independent build output/run/runtime roots. Raw launcher logs contain the local dashboard authentication URL; do not publish them without redacting it. This report contains no authentication token.

## PR

One branch and one PR targeting `main`; human review and merge required. No remote CI PASS is claimed. The verification API/dashboard processes were stopped only after proving their PID ownership and absence of non-terminal runs. Existing 8875/5273 listener PIDs remained unchanged. The temporary worktree registration and remaining files were removed; Windows long-path cleanup was required. Diagnostic evidence and this report are preserved in the primary repository.

## RESIDUAL RISK

Passing JSON/Python syntax validation proves provider recovery, not satisfaction of the Dental objective. No target tests or independent product re-review were executed against the generated output. Golden Path remains NOT PASS. The corrected response still needs the existing longer bounded timeout in the live replay. A stochastic local model can still genuinely fail; governed exhaustion remains covered. The earlier intermittent API assertion remains undiagnosed. Original egress/dependency-lock and separate launcher ownership limitations remain.

## SINGLE NEXT ACTION

`HUMAN_REVIEW_AND_MERGE_OLLAMA_REPEAT_LIMIT_FIX`

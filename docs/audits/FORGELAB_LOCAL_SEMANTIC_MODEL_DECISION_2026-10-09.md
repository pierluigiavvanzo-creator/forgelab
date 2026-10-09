# ForgeLab — local semantic model decision, 2026-10-09

## BASELINE / DECISION

Canonical local and fetched remote main: `1d7024f46d03709587913b3e4905d0b324ae7f40` (PR #70 merged). Production source/configuration is unchanged.

`qwen2.5-coder:7b` remains NOT QUALIFIED FOR FORGELAB SEMANTIC REPAIR based on the reused prior 0/2 experiment. Its failed experimental prompt extension remains reverted; no additional 7B inference or prompt fix was attempted.

**`QWEN14B_NOT_QUALIFIED` — 0/2 PASS under the current machine, canonical prompt and 300-second timeout.** Both independent executions time out before a complete editor response. This is an operational qualification failure; the 14B candidate's semantic correctness was not measured and must not be claimed inferior or incorrect.

## RESOURCE PREFLIGHT / AUTHORIZATION

Ollama 0.34.2. Initial installed models: only `qwen2.5-coder:7b` (Q4_K_M). Model storage defaults to `C:\Users\NITRO\.ollama\models`; no process/user/machine OLLAMA_MODELS override detected.

After the Product Owner separately authorized normal Comet closure to recover RAM, immediately before the authorized download:

- physical RAM: 15.71 GiB;
- available RAM: 5.70 GiB;
- GPU: NVIDIA RTX 4050 Laptop, 6141 MiB total / 5920 MiB free (about 5.78 GiB free VRAM);
- C: free disk: 762.79 GiB.

No unrelated user processes were forcibly terminated. ForgeLab API/dashboard, Codex and Ollama services remained running and unchanged. The bounded test was considered plausible with mixed RAM/GPU execution and limited resource margin; actual measurements below show substantial memory pressure.

The Product Owner explicitly approved the single-model download with “vai” after the download-approval gate. Only `qwen2.5-coder:14b` was pulled, using the existing local Ollama executable. No paid API, additional model download or production change occurred.

Installed model:

- name: `qwen2.5-coder:14b`;
- bytes: 8988124298 (about 9.0 GB / 8.37 GiB);
- digest: `9ec8897f747e246e970bc5cfdda85d22f1123dc2e3d34978a010a75968716849`;
- GGUF, Qwen2, 14.8B, Q4_K_M;
- reported model context capability: 32768.

Download completed and Ollama verified the model. It remains installed; it was released from memory after the benchmark.

## EXACT CONTROLLED BENCHMARK

Reused the exact protected fixture and independent acceptance harness in `.forgelab/runtime/semantic-completion-audit/`, corresponding to the prior unresolved-contract evidence ZIP. No fixture/acceptance edits, weakened assertions or diagnostic product special cases were introduced.

The existing diagnostic runner evaluates the actual `semantic_aider_objective` AST expression from canonical main. Its semantic objective bytes match the previously recorded canonical baseline; the failed experimental extension is absent. Only `EditorRequest.model` changes from 7B to `qwen2.5-coder:14b`.

Exactly two sequential independent editing executions used installed Aider 0.86.2, whole, current production flags/model options, local Ollama and the same 300-second timeout. Each creates a fresh temporary authorized workspace/tool-home/chat history from unchanged source files. No retries, timeout/repair-budget increase or manual generated-code repair was added. The second run uses an already loaded model but still has a new independent editor workspace/history/request.

Local evidence:

- `semantic-completion-audit/qualification-14b-1/` and `qualification-14b-2/` contain exact semantic objectives/editor prompts/commands, initial model-request trace, before/after result files and periodic resource samples.
- `qualification-14b-1/runner-observation.json` records a separate actual Ollama child-runner memory observation.
- Scripts: `.forgelab/runtime/run-14b-qualification-1.py`, `run-14b-qualification-2.py`, corresponding unchanged acceptance wrappers and `local-model-memory-probe.py`.
- Raw downloader progress remains intentionally local/ignored and is not necessary to publish.

The model request is captured before rendering. Because both calls time out inside nonstreaming inference, **no complete raw completion, parsed edits or provider token-usage response is captured**. This does not mean zero tokens were generated on the server. Input/output token counts are unavailable. No raw response is invented from startup output or elapsed time.

Diagnostic limitation: the subprocess capture wrapper records normal returned stdout/stderr but does not persist TimeoutExpired partial output. Consequently no complete rendered stdout/stderr artifact exists for these timed-out calls. The adapter handles timeout and returns the explicit exit/timing/file evidence; that is sufficient to reject qualification at the process gate. No extra inference was used to repair diagnostic logging.

## VALIDATION RUN 1

- Model: `ollama_chat/qwen2.5-coder:14b`.
- Exit status: **124**; `timed_out=true`.
- Total adapter duration: **300031 ms**.
- `changed_paths=[]`; both returned file contents equal the original protected fixture.
- `source_unchanged=true`; no successful candidate writes or unauthorized files reported.
- Raw completion: unavailable, zero complete characters captured.
- Input/output tokens: unavailable because inference did not complete.
- Generated deterministic tests: **not produced/executed**; unchanged baseline's prior six passing tests do not qualify a repair.
- Independent acceptance: **not executed**; there is no new candidate and the unchanged baseline is known incomplete.
- Result: **FAIL at editor completion/timeout gate**.

Resource sampling: 60 observations, minimum available physical RAM **0.26 GiB**. The first periodic sampler initially tracks executables named Ollama and omits its `llama-server.exe` descendant; its approximately 0.05 GiB aggregate is not the model's actual memory consumption. A separate verified child-process observation measures `llama-server.exe`, PID 86168 under Ollama PID 18748, at **6.81 GiB working set**.

At that observation, Ollama `/api/ps` reports model allocation 11405382121 bytes (about 10.62 GiB), of which 4226778398 bytes (about 3.94 GiB) are VRAM; active context length 11253. These are reported allocations and a sampled working set, not exact lifetime peaks or summed interchangeable memory metrics.

## VALIDATION RUN 2

- Same model, canonical semantic prompt, fixture, options and timeout.
- Exit status: **124**; `timed_out=true`.
- Total adapter duration: **300031 ms**.
- `changed_paths=[]`, source unchanged, no candidate produced.
- Complete raw response and input/output token usage: unavailable.
- Generated tests and independent acceptance: **not executed**, because there is no new candidate.
- Result: **FAIL at editor completion/timeout gate**.

The second periodic sampler includes the verified `llama-server.exe` model-runner executable. Across 60 samples, minimum available RAM is **0.31 GiB** and maximum observed summed Ollama/runner working set is **6.85 GiB**. This is a sampled maximum, not a proven instantaneous peak.

No quality PASS/FAIL is inferred from missing output. Both are operational failures under the unchanged existing timeout. RAM pressure is directly observed; its precise causal contribution versus CPU/offload/inference latency is not separately proved.

## QUALIFICATION / PRODUCTION SWITCH / CLEANUP

**0/2 PASS; `QWEN14B_NOT_QUALIFIED`.** The required 2/2 threshold is not met. No production semantic-route switch, branch, config test, PR, merge, broad stabilization or Windows launcher restart is justified or performed. Unchanged production source preserves PR #68 continuity, PR #69 no-op governance, scope/source protection, truthful accounting, paid-provider boundaries and Security/human gates. No Dental run, edit or promotion occurred.

After both owned benchmark processes completed, `ollama stop qwen2.5-coder:14b` released only the newly installed benchmark model from RAM. It did not uninstall the model or stop the Ollama service. `/api/ps` then reports no loaded models and available RAM recovers to **8.05 GiB**. User ForgeLab services were untouched.

Tracked `git diff --exit-code` is empty; canonical main remains unchanged. This audit and ignored diagnostic evidence are local, uncommitted delivery artifacts. There is no code commit and no PR.

## COMMAND EVIDENCE

| Command | Exit | Result |
| --- | --- | --- |
| Local/remote main verification | 0 | Both canonical SHA `1d7024f46d03709587913b3e4905d0b324ae7f40` |
| `ollama pull qwen2.5-coder:14b` | 0 | Only authorized 14B installed and digest verified |
| `<aider-python> .forgelab/runtime/run-14b-qualification-1.py` | Wrapper 0 / editor **124** | 300031 ms timeout, no candidate, source unchanged |
| `<aider-python> .forgelab/runtime/run-14b-qualification-2.py` | Wrapper 0 / editor **124** | 300031 ms timeout, no candidate, source unchanged |
| Objective-byte comparison to canonical recorded baseline | 0 | Identical; failed prompt extension not used |
| Periodic Win32 memory samples / descendant process inspection / Ollama `/api/ps` | 0 | Resource figures above; first sampler omission explicitly documented |
| `ollama stop qwen2.5-coder:14b`; `/api/ps` | 0 | Owned benchmark model unloaded; remains installed; RAM 8.05 GiB free |
| `git diff --exit-code` | 0 | No production source/configuration change |

EUR 0 for local inference; no paid fallback. Download uses local storage/network bandwidth and is not evidence of a production quality improvement.

## ONE NEXT LOCAL CANDIDATE / SINGLE NEXT ACTION

Recommend **`qwen3:8b`** as the single next *diagnostic* candidate, not a production replacement. Its default Ollama package is about **5.2 GB**, providing a smaller weight footprint than this 9.0 GB 14B on a 16 GiB RAM / 6 GB GPU machine. The Qwen team reports improvements in instruction following, reasoning, mathematics and coding for Qwen3; this motivates testing the semantic class, not assuming qualification.

Primary sources: [Ollama Qwen3 tags](https://registry.ollama.com/library/qwen3/tags), [Qwen3 official release](https://qwenlm.github.io/blog/qwen3/).

It is **not downloaded, benchmarked or selected for production**. Its quality, runtime fit and existing-timeout performance remain unverified. No second large model download is authorized automatically.

**SINGLE NEXT ACTION: `APPROVE_QWEN3_8B_DOWNLOAD_AND_BOUNDED_QUALIFICATION`.**

Do not run Dental.

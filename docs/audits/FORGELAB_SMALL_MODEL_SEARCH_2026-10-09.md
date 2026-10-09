# ForgeLab — bounded small-model search and cleanup, 2026-10-09

## Result

**No qualified replacement found among the four newly tested candidates.** Cleanup is complete; the requested model replacement remains unresolved. No production model switch or new Dental run is justified. This is not a claim that every small local model is incapable, or that hardware alone caused the failures.

The product purpose was reliable local semantic repair without excessive memory pressure and without paid inference. Local Ollama provider cost was EUR 0; no paid service or remote inference was activated.

Canonical Git main/HEAD remains `1d7024f46d03709587913b3e4905d0b324ae7f40`. Source/configuration, dependencies, timeouts, repair budgets, dashboard and Dental were not changed. No branch, commit, push, PR or merge was created. This report and diagnostic files are local/uncommitted.

## Cleanup and current machine state

Removed the previously failed `qwen3:4b-instruct-2507-q4_K_M`. Downloaded, evaluated, then unloaded and removed all four new candidates: `ministral-3:3b`, `qwen3.5:4b`, `phi4-mini`, `qwen2.5-coder:3b-instruct-q8_0`. The earlier 8B/14B removals are historical and were not repeated.

Final Ollama inventory contains only `qwen2.5-coder:7b`, retained because ForgeLab's current editor configuration references it. Its presence is not semantic qualification: previous evidence already rejected it for this repair contract. Final `/api/ps` reports **no loaded models**. Comet and ForgeLab services were preserved. No unrelated applications, logs or user data were deleted.

Final measured available RAM: **4.62 GiB**. Initial valid measurement for this task was 4.09 GiB, with the previous 4B loaded. These are snapshots under changing desktop load, not an exact attribution of memory savings.

## Executed evidence

Exactly **11 fresh Aider adapter executions** across four models and bounded configuration/contract experiments; this count is not a count of provider requests. Aider's existing internal reflections occurred for Phi's invalid format. No additional external retry or budget increase was introduced.

The protected two-file inventory fixture and original independent acceptance checks remained unchanged. Aider 0.86.2, whole edits, existing authorized scope and timeout 300 seconds were preserved. Seven produced candidates received both actual generated-unit-test execution and the six-case independent acceptance suite. Four produced no usable candidate; no baseline tests were substituted or claimed PASS. Every source_unchanged field is true.

| Execution | Editor exit | Seconds | Actual tests | Min free RAM / max observed Ollama working set, GiB | Gate |
| --- | --- | --- | --- | --- | --- |
| ministral-3b-1 | 0 | 56.875 | generated exit 1; acceptance FAIL | 4.17 / 0.89 | FAIL |
| ministral-3b-2 | 0 | 57.563 | generated exit 1; acceptance FAIL | 4.32 / 0.89 | FAIL |
| qwen35-4b-1 | 0 | 200.672 | not executed: no candidate | 3.44 / 1.26 | FAIL |
| qwen35-4b-direct-1 | 0 | 78.702 | generated exit 0; acceptance FAIL | 2.96 / 1.66 | FAIL |
| qwen35-4b-direct-2 | 0 | 85.578 | generated exit 0; acceptance FAIL | 3.50 / 1.12 | FAIL |
| qwen35-4b-contract-1 | 0 | 91.094 | generated exit 1; acceptance FAIL | 3.42 / 1.12 | FAIL |
| qwen35-4b-contract-2 | 0 | 100.468 | generated exit 1; acceptance PASS | 3.44 / 1.12 | FAIL |
| phi4-mini-1 | 0 | 50.780 | not executed: no candidate | 3.49 / 1.07 | FAIL |
| phi4-mini-2 | 0 | 47.187 | not executed: no candidate | 3.55 / 1.07 | FAIL |
| qwen25-coder-3b-q8-1 | 0 | 48.764 | generated exit 1; acceptance FAIL | 3.84 / 0.77 | FAIL |
| qwen25-coder-3b-q8-2 | 124 | 300.016 | not executed: no candidate | 3.69 / 0.94 | FAIL |

Memory values are periodic observations, including the llama-server process, not exact peaks. File size, working set, committed/private memory and GPU allocation are different measures. Lower observed RAM use did not establish correctness. One non-JSON line in contract-run-1's trace was excluded from response counting; the original trace is preserved unchanged and the structured summary records this diagnostic limitation.

### Failure classes demonstrated

- Ministral: both runs broke the preserved helper return contract (`final_total` absent); generated suites each had one failure and two errors. Other independent cases passed, but complete qualification failed.
- Qwen3.5 with current defaults: after 200.672 seconds, a complete response recorded 8602 completion tokens and empty final content. Rendered output contained reasoning without applicable edits. This establishes a response/content mismatch for that execution, not a universal model limitation.
- Qwen3.5 non-thinking configuration: generated tests passed in both runs; independent validation failed in both (five invalid-discount subtests and one nonnumeric-discount error). The caller calculated each item using discount zero and later performed unvalidated aggregate arithmetic.
- Qwen3.5 with generic contract clarification: run 1 corrected validation but changed render_estimate's return type from JSON string to dict; generated tests also failed. Run 2 passed all independent acceptance cases, but its 18 generated tests had two errors because tests expected ValueError at a CLI that exits via argparse/SystemExit. Neither run met the full gate; no generated file was manually patched.
- Phi4-mini: both runs returned exit 0 with no authorized net changes. First-run evidence explicitly shows whole-file format violations, placeholders and three built-in reflections exhausted. Complete exit is not successful editing.
- Qwen Coder 3B Q8: run 1 edited both files but failed generated tests (one failure, two errors) and independent output-contract checks (one failure, two errors). Run 2 timed out at 300.016 seconds without changes; no candidate acceptance was run.

No weaker test, hand-corrected model output or single partial PASS was used to qualify a model.

## Exact diagnostic delta

Ignored local scripts clone the existing actual-production-prompt runner and acceptance checker, changing only model and case directory for baseline qualification. Memory sampling and timeout capture are retained.

Qwen3.5's documented non-thinking experiment adds standard Aider `--model-settings-file` pointing to `.forgelab/runtime/qwen35-4b-model-settings.yml`: use_temperature 0.7; extra_params reasoning_effort none, top_p 0.8, top_k 20, presence_penalty 1.5. Installed LiteLLM mapping was explicitly checked: reasoning_effort none -> Ollama think false. This mapping check does not claim every optional parameter was independently verified on the wire.

Two later diagnostic runs additionally append the exact generic clarification retained in `prepare-qwen35-contract-qualification.py`: satisfied findings are scoped to proven original paths; new callers must preserve validation; helper contracts remain; superseded entry-point tests may be minimally updated. The clarification was not added to production, and these runs do not qualify the current canonical prompt.

Runtime evidence resides in `.forgelab/runtime/semantic-completion-audit/qualification-*` directories listed in the table. Each includes command/prompt, result, model trace and memory samples; candidate cases additionally include generated-tests.txt, independent-acceptance.txt and test-summary.json. The diagnostic checker wrapper's own exit 0 is not a test PASS; qualification uses actual generated subprocess exit and independent acceptance status.

Existing internal stabilization evidence (108 Python tests, four dashboard callbacks and Windows stability 6/6 on code 555d6ee) remains applicable to the unchanged production code. Those suites were not redundantly rerun or used to imply semantic qualification of any new model. No live Dental or full new-model orchestration Golden Path was executed.

## Handoff artifacts

Report: `docs/audits/FORGELAB_SMALL_MODEL_SEARCH_2026-10-09.md`. ZIP: `.forgelab/runtime/FORGELAB_SMALL_MODEL_SEARCH_EVIDENCE_2026-10-09.zip`, intentionally ignored by Git. The archive contains selected synthetic evidence, reproduction scripts, unchanged fixture, configuration experiment, resource measurements, final inventory, manifest hashes and security-scan.json. No production launcher logs or authenticated dashboard/session evidence is included.

All selected files were scanned before packaging for known credential formats, private-key headers, URL userinfo and authenticated loopback URL parameters; no matches were found. This bounded scan is not a universal guarantee of secret absence. ZIP integrity was checked. Runtime ZIP and raw evidence must not be committed automatically.

## Research and rejected options

Primary sources used: [Ministral Ollama](https://ollama.com/library/ministral-3:3b), [Qwen3.5 Ollama](https://ollama.com/library/qwen3.5:4b), [Qwen3.5 model card](https://huggingface.co/Qwen/Qwen3.5-4B), [Phi tags](https://ollama.com/library/phi4-mini/tags), [Phi model card](https://huggingface.co/microsoft/Phi-4-mini-instruct), [Qwen Coder tags](https://ollama.com/library/qwen2.5-coder/tags), [Aider model configuration](https://aider.chat/docs/config/adv-model-settings.html), [Ollama thinking](https://docs.ollama.com/capabilities/thinking).

[Gemma 4 E4B](https://ollama.com/library/gemma4:e4b) was researched but not downloaded: despite its effective-parameter label, the GGUF package is about 6.6 GB, with 7.52B displayed parameters, too large for this search's memory objective. Published benchmarks motivated candidates but were never treated as local test evidence.

## Blocker and single next action

The available tested configurations have not met the combined correctness, integration-format and latency contract. Further blind model downloads are not justified by these results. The root cause of individual timeout events remains unproven; do not declare the PC globally incapable.

**Single next action:** prepare a bounded proposal for a more capable inference backend, including a verified free option if available, and qualify it on the identical complete gate before any production switch. Paid activation, architecture changes and Dental remain outside this diagnostic result and require their applicable authorization.

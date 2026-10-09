# ForgeLab — Qwen3 8B qualification, 2026-10-09

## Result

**0/2 PASS: qwen3:8b is not qualified under the current ForgeLab configuration and 300-second timeout.** Installation works, but both actual semantic-editing executions time out before a complete response. Semantic correctness is unmeasured; this is not a universal claim that the model cannot generate correct code.

Canonical main remains `1d7024f46d03709587913b3e4905d0b324ae7f40`. Production source/configuration is unchanged. No Dental run/edit/promotion, paid API, retry or budget increase occurred. Comet remains open.

## Controlled evidence

Exactly two fresh independent adapter executions reused the protected two-file fixture, current canonical semantic objective and identical acceptance harness. Only the model request selects `qwen3:8b`. Aider 0.86.2, whole, current flags/options, local Ollama and timeout 300 remain unchanged. The failed experimental prompt extension is absent.

Installed model: Q4_K_M, 8.2B, 5225388164 bytes, digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.

Preflight available RAM: 5.40 GiB. The earlier authorized 14B removal and Comet restoration are not repeated in this task. Qwen3 remains installed; the owned benchmark model is unloaded from RAM after testing, without stopping the Ollama service.

| Run | Editor exit | Duration | Changes | Source | Qualification |
| --- | --- | --- | --- | --- | --- |
| 1 | 124, timeout | 300030 ms | None | Unchanged | FAIL |
| 2 | 124, timeout | 300047 ms | None | Unchanged | FAIL |

No complete raw completion/provider usage is returned. Zero complete characters are captured, not a claim of zero server-generated tokens. No generated candidate/tests exist, so candidate tests and independent acceptance are not executed or claimed PASS. Previous baseline tests do not qualify an unchanged incomplete candidate.

Raw initial requests, exact commands/prompts, resource samples and before/after results are retained locally under `.forgelab/runtime/semantic-completion-audit/qualification-qwen3-8b-1/` and `qualification-qwen3-8b-2/`. Timeout partial stdout/stderr are now persisted by the diagnostic wrapper; this diagnostic-only recording correction does not change model requests or production behavior. Scripts are `.forgelab/runtime/run-qwen3-8b-qualification-{1,2}.py` and the unchanged acceptance wrappers.

During observed execution, memory pressure is lower than for 14B (for example about 3.25 GiB Ollama working set and 2.09 GiB physical RAM free in run 1; about 3.72 GiB working set and 1.87 GiB RAM free in run 2). Periodic samples retain full measurements. Lower memory use is not sufficient to qualify functionality or latency.

No production switch, branch, PR, commit, stabilization relaunch or new Dental run is justified. Tracked diff is empty. This audit and runtime diagnostics remain local/uncommitted.

## Technical uncertainty

Official Qwen/Ollama documentation describes Qwen3 thinking mode and warns against greedy decoding in thinking mode. Installed Aider's default Model.send_completion resolves its unspecified temperature to 0; no model-specific settings were introduced for this test. This is a documented compatibility concern, not proof that it caused either timeout. No thinking/temperature/timeout change was made during the controlled runs and no additional experiment was silently added.

Sources: [Qwen quickstart](https://github.com/QwenLM/Qwen3/blob/main/docs/source/getting_started/quickstart.md), [Ollama thinking documentation](https://ollama.com/blog/thinking).

## Search result / one next candidate

The single next diagnostic candidate identified is **qwen3:4b-instruct-2507-q4_K_M**. Ollama lists approximately 2.5 GB; the official Qwen card states that the Instruct-2507 variant supports only non-thinking mode. Its smaller weight footprint and absence of a thinking phase motivate evaluation on this 16 GiB RAM / 6 GB GPU machine. They do not prove semantic accuracy, SLA compliance or successful Aider integration.

Sources: [Ollama model tags](https://ollama.com/library/qwen3/tags), [official Qwen model card](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507).

It has **not been downloaded, tested or selected for production**. No further model is downloaded automatically.

Single next action: **authorize a bounded qualification of this exact Instruct candidate**, including its download, before claiming it works for ForgeLab. Do not run Dental.

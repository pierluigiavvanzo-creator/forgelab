# ForgeLab — Aider empty-edit root-cause investigation, 2026-10-09

## Result / baseline

`STOP_AND_REPORT_UNVERIFIED_AIDER_FAILURE`.

Verified local and fetched remote main: `9fc7900af2d8b4521ee3c7ff3c3ab08ca8e8dc12`, containing merged PR #69. Working tree was clean before diagnostics. There is no proven production edit-format, parser, prompt or summarizer repair to deliver. No production code, dependency, model, provider, budget, retry, gate, Dental file or service was changed. No new Dental run or promotion was performed.

Subsequent explicit Product Owner instruction authorizes publication of this completed investigation on `fix/aider-empty-edit-root-cause`, with exactly one documentation-only PR against main and no merge. Publication does not change the UNVERIFIED diagnosis or introduce a production fix.

The principal correction is to the interpretation of the evidence: Aider's stdout is a **rendered diff**, not necessarily the raw model completion. Empty rendered diff blocks cannot establish an empty model response.

## Real run evidence

Read-only evidence: `.forgelab/runs/run-b0201c5aa9dd/SemanticRepairNoop.json` and `RunSummary.json`.

- Semantic editor exit 0, no timeout, duration 113811 ms; stderr empty.
- `changed_paths=[]`, `candidate_write_performed=false`, `prewrite_recovery_attempts=0`.
- Before/after UTF-8 hashes identical for both authorized files:
  - `quote_calculator.py`: `e08b6f0904b96f05473c94d64c966c227384b66e9f0c13310bfffe5f74665f4e`.
  - `test_quote_calculator.py`: `d167f565a0a640772ddf59dde5bf11311837cb3e1e6e337ac3ea31ed367ef4ec`.
- One semantic repair attempt counted; independent reconsideration FAIL; final CLOSED / REPAIR / `SEMANTIC_REPAIR_NOOP`; deterministic tests PASS; no automatic promotion.
- Legitimate blocking review: missing real three-treatment behavior, automatic subtotals and corresponding tests.
- stdout contains empty `diff` displays, `Applied edit` for both files, then shutdown summarizer warnings.

PR #69 correctly handles this outcome. Its evidence does not contain the raw original model completion. Therefore the exact model decision causing this real no-op is still unavailable.

## Parser reproduction — installed Aider 0.86.2, no model calls

Diagnostic script: `.forgelab/runtime/parser-empty-edit-probe.py`; complete cases/output: `.forgelab/runtime/empty-edit-audit/parser-probe.json`.

The probe uses the actual installed `WholeFileCoder.get_edits`, `render_incremental_response`, `apply_updates`, `apply_edits` and `InputOutput.write_text`, on two temporary Python files. Only unrelated constructor/state preparation is replaced. Results:

| Raw completion | Rendered stdout | Parser/application | Net content |
| --- | --- | --- | --- |
| Full identical file bodies | Empty fenced diff blocks | Two edits, `Applied edit` twice | Unchanged |
| Literally empty file bodies | Diffs deleting original content | Two zero-length replacements, `Applied edit` twice | Files emptied |
| Changed full file bodies | Nonempty diffs | Two edits, `Applied edit` twice | Changed |

Thus the actual signature **empty displayed diff + Applied edit + unchanged content** is reproducible without invalid or empty raw model blocks. In whole mode, filenames/content are parsed twice: once to render a diff, then to apply the complete replacements. Applied edit means the selected file was written, not that its content differs.

Source anchors in the installed pinned package:

- `aider/coders/wholefile_coder.py`: `render_incremental_response`, `get_edits(mode="diff")`, `do_live_diff`, `apply_edits`.
- `aider/diffs.py`: `diff_partial_update` renders identical text as an empty fenced diff.
- `aider/coders/base_coder.py`: `send` renders before application; `apply_updates` prints Applied edit for each parsed target.
- `aider/io.py`: `write_text` writes the given full content; it does not skip empty replacements or restore unchanged source files.

**Proven failure of the initial hypothesis:** displayed empty blocks do not prove that Qwen emitted empty replacements. Literal empty-block parsing would change the file hashes, unlike the real run.

## Live reproduction — generic fixture, local Ollama only

Script: `.forgelab/runtime/reproduce-empty-edit.py`.

Two synthetic writable files, `inventory.py` and `test_inventory.py`, initially support/test one inventory item. The semantic repair objective requests three items, automatic subtotals, percentage discount, final total, validation and tests, includes a binding PM acceptance contract and blocking reviewer JSON, and preserves the existing passing behavior. This reproduces the call shape, not the exact Dental candidate or prompt. No Dental files are used or modified.

The current main `AiderCliAdapter` constructs the actual disposable sandbox, prompt, metadata and all current CLI flags. A diagnostic wrapper invokes the installed `aider.main.main` unchanged and records raw completions, parsed edits and actual files before/after rendering/application. The wrapper adds logging only; it does not change model output, parsing, prompt, options or write behavior. The ForgeLab source fixture remains unchanged.

Exact command is captured in `empty-edit-audit/command.json`; the actual prompt in `prompt.txt`; raw CLI stdout/stderr in `stdout.txt`/`stderr.txt`; raw model response and application events in `live-trace.jsonl`; before/after content and result in `result.json`. Transient tool-home paths in that command no longer exist after adapter cleanup.

Command shape (only transient paths normalized):

```text
<installed-aider-python> <diagnostic-traced-aider.py>
--model ollama_chat/qwen2.5-coder:7b --edit-format whole --timeout 300
--map-tokens 0 --no-git --no-gitignore --no-add-gitignore-files
--no-auto-commits --no-dirty-commits --no-auto-lint --no-auto-test
--no-watch-files --no-cache-prompts --no-restore-chat-history
--no-suggest-shell-commands --no-notifications --no-detect-urls
--no-pretty --no-stream --no-show-model-warnings --no-check-model-accepts-settings
--analytics-disable --no-check-update --no-show-release-notes --yes-always
--config <isolated-empty-config> --env-file <isolated-empty-env>
--model-metadata-file <isolated-local-provider-metadata>
--message-file <exact-prompt> --chat-history-file <isolated-history>
--input-history-file <isolated-input-history> inventory.py test_inventory.py
```

Outcome: exit 0, 39547 ms, no timeout; both authorized files changed; complete raw model response recorded (1987 characters). No summarizer ran in this shorter live case. There was no whole-format parsing failure or empty-model-block result.

**The live candidate is not PASS:** isolated execution of its three generated tests fails with two failures and one error. It rejects the required preserved single-item case, lacks input validation, and its three-item test expects 45 despite a 5% discount (actual 42.75). Real editing proves format compatibility, not model quality, correct requirements or a completed Golden Path. The candidate was never applied to a governed project or promoted.

## Role of edit format

Installed `ModelSettings` defaults to whole. The special Qwen 2.5 coder diff preference in `models.py` requires **32b**, so it does not apply to the configured 7b model. The installed whole prompts require complete file listings. The current ForgeLab prompt does not tell the model to emit unified diffs. Raw live output conformed to whole-file replacements; stdout nevertheless showed diffs because Aider renders them.

Whole is supported and can edit this model's fixture. Neither global suitability nor reliable semantic correctness is proved. No alternative format comparison is needed to resolve the alleged stdout-format mismatch; no production format change is justified.

## Role of summarizer failure

Installed execution order is: render response -> apply/write edits -> print Applied edit -> move chat messages -> start background summarization. In single-message CLI mode, main returns after `coder.run`; summary-thread failures are warnings and do not themselves determine the CLI exit status. `ChatSummary.summarize_all` catches model exceptions and raises the final ValueError; the worker catches that error and warns. It does not write or restore project files.

The parser probe separately exercises the installed summary worker with a model stub deliberately raising `cannot schedule new futures after shutdown`. All three cases retain their already-persisted file contents after the warning. This is a **controlled simulation of that exception**, not a reproduced real interpreter shutdown race. The live fixture did not trigger summarization. The historical real run already records exit 0 and warning order after Applied edit.

Therefore source order and the controlled probe show no file-loss mechanism in the summarizer path. The exact historical shutdown race was not independently reproduced; do not claim it fixed, harmless under every configuration, or causal in the no-op.

## Change / delivery

- Production change-set: **none**. PR #68 continuity, PR #69 no-op handling, scope/source protection, budgets and human gates remain untouched.
- Diagnostic files and the evidence ZIP remain local ignored artifacts under `.forgelab/runtime`; only this audit is included in the publication change-set.
- No speculative production regression or fix was added. The parser probe supplies deterministic diagnostic cases; existing regressions verify the governed contracts.
- The later explicit publication request authorizes the branch and one PR despite the unverified root cause. This is an investigation report, not a code-fix PR; no production code commit exists.
- ZIP inspection read all 13 entries: zero HTTP/HTTPS URLs, zero authenticated local URLs and zero matches for common credential/token/private-key patterns. No secrets were found; pattern scanning is not a universal proof of absence. The ZIP contains local paths/runtime diagnostics and remains intentionally ignored and excluded from Git. Its embedded report reflects the earlier local-delivery checkpoint.

## Test evidence

| Command / evidence | Exit | Result |
| --- | --- | --- |
| `git fetch origin main`; local/remote main verification | 0 | Both `9fc7900af2d8b4521ee3c7ff3c3ab08ca8e8dc12` |
| `<aider-python> .forgelab/runtime/parser-empty-edit-probe.py` | 0 | Three actual-parser cases; empty rendered diff differs from empty raw body; simulated summarizer error preserves files |
| `<aider-python> .forgelab/runtime/reproduce-empty-edit.py` | 0 | Actual local model exit 0, both disposable files changed, protected fixture unchanged |
| `<aider-python> .forgelab/runtime/test-empty-edit-candidate.py` | Wrapper 0 / child **1** | Generated fixture candidate: 3 tests, 2 FAIL + 1 ERROR; not accepted |
| `PYTHONPATH=src <aider-python> -m unittest tests.test_editor_adapter tests.test_orchestrator.MultiAgentTests.test_aider_semantic_noop_is_rereviewed_and_truthfully_accounted tests.test_orchestrator.MultiAgentTests.test_semantic_noop_rejects_inconsistent_file_evidence tests.test_orchestrator.MultiAgentTests.test_native_repair_preserves_parent_candidate_for_planner_aider_and_review tests.test_orchestrator.MultiAgentTests.test_aider_initial_candidate_gets_one_prewrite_correction` | 0 | **24 tests PASS** on current main |
| `git diff 555d6ee1d7be02975afd8cd24f9f0b40f3587681 HEAD -- src tests dashboard Start-ForgeLab.ps1 scripts pyproject.toml` | 0 | Empty: relevant runtime/test/launcher trees identical to prior verified candidate |
| Prior PR #69 unmodified Windows launcher evidence, `noop-launcher.log` | 0, prior execution | Reused **108 Python + 4 dashboard tests**, Aider preflight/pip check, production build, readiness, stability **6/6 PASS** at code `555d6ee`; not rerun or claimed as a new current-session launcher execution |

Two diagnostic setup failures were corrected before valid probes: missing diagnostic environment variable (the adapter intentionally strips it), and missing cache field on the manually constructed coder. Both exited 1 before a valid model/parser result; neither is a product failure or a model retry. No duplicate live inference was performed after a valid result.

## Residual risk / single next action

The real no-op remains semantically unsuccessful; the exact original raw response and reason the model returned unchanged content are unverified. A single live successful edit does not establish reliability; its failed tests demonstrate remaining model quality risk. Existing baseline technical PASS is not Dental/Golden Path PASS.

`STOP_AND_REPORT_UNVERIFIED_AIDER_FAILURE`.

Do **not** launch another Dental run on the basis of this investigation. A future authorized diagnostic should capture the raw LLM response (not only rendered stdout) on an equivalently complex synthetic semantic-repair fixture before proposing a prompt/format/lifecycle repair.

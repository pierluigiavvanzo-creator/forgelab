# ForgeLab — Aider semantic repair completion investigation, 2026-10-09

## BASELINE / result

`STOP_AND_REPORT_UNVERIFIED_ROOT_CAUSE`.

Verified and fast-forwarded local main to fetched remote main `1d7024f46d03709587913b3e4905d0b324ae7f40`, containing merged PR #70. This main update adds only the previous audit; runtime code is unchanged. No production correction, fix branch, commit, push, PR, model/provider/options change, budget increase, retry, Dental edit/run/promotion or service manipulation was performed in this investigation.

The requested PASS criteria are **not met**: the original unchanged-candidate failure was not reproduced, no causally established production fix exists, and the generated candidate fails deterministic tests. Semantic Reviewer/Security PASS and Windows candidate stabilization are therefore not claimed.

## RAW COMPLETION EVIDENCE

An isolated generic fixture contains two Python files, `inventory_app.py` and `test_inventory_app.py`. Baseline: a validated single-item calculator, discount handling, supported names and CLI/JSON entry point; six existing tests PASS. Missing: exactly-three-item entry point, visible per-item subtotals, aggregate quote and tests for that integration. No Dental source was copied or modified.

The objective requires exactly three items through the existing CLI/JSON entry point; automatic subtotals/aggregate; validated discount 0–100; correct final total; validation; direct tests; preservation of valid single-item helper behavior. The PM contract contains six explicit acceptance criteria. Blocking review lists only unresolved entry-point/output/test requirements and separately identifies satisfied helper behavior.

The actual `semantic_aider_objective` assignment is extracted from current orchestrator source with Python AST and evaluated with this fixture's request, PM contract and blocking review. No reconstructed approximation replaces the production expression. The current `AiderCliAdapter` constructs its real isolated prompt/config/metadata/sandbox and all CLI flags, with Aider 0.86.2, `ollama_chat/qwen2.5-coder:7b`, `whole`, 300 seconds and the existing local provider.

A diagnostic-only wrapper instruments installed `Model.send_completion` and `WholeFileCoder` without changing requests, responses, parser behavior or writes. Capture occurs before Aider rendering. It records complete model messages, selected model metadata, raw completion/usage/finish reason, rendering, parsed edits, application snapshots, summary snapshots, stdout/stderr, exact CLI command, source files and returned result.

Local ignored evidence root: `.forgelab/runtime/semantic-completion-audit/`.

- `contract.json`, `blocking-review.json`: exact synthetic obligations.
- `fixture/`: protected synthetic baseline.
- `baseline/semantic-objective.txt`: actual production-expression result.
- `baseline/editor-prompt.txt`, `command.json`: complete ForgeLab editor prompt and exact CLI command; transient tool-home paths are intentionally local.
- `baseline/live-trace.jsonl`: full model request/completion, metadata/usage, parsed/application/summary snapshots.
- `baseline/result.json`: full before/after files and process evidence.
- `baseline/stdout.txt`, `stderr.txt`: complete rendered output.
- `baseline/generated-tests.txt`, `independent-acceptance.txt`, `test-summary.json`: candidate verification.

Actual main editing call: eight messages, 11076 content characters; metadata `litellm_provider=ollama_chat`, `mode=chat`; stream false; edit format whole. Usage: **2479 prompt tokens, 1796 completion tokens**, finish reason `stop`. Complete raw response: **7289 characters**. Aider subprocess exit 0, 138202 ms, no timeout; `changed_paths` correctly includes both authorized files. Source fixture remains unchanged.

Raw completion begins by explicitly planning three-item entry-point, aggregate quote and quantitative tests, then emits complete file listings. It is neither empty nor explanation-only. Its implementation includes:

```python
def render_estimate(items, discount=0):
    if len(items) != 3:
        raise ValueError("entry point currently accepts exactly three items")
    aggregate_subtotal = 0
    for item in items:
        result = calculate_item(item["name"], item["unit_price"], item["quantity"], item.get("discount", 0))
        aggregate_subtotal += result["final_total"]
        result["final_total"] = round(result["final_total"], 2)
    final_total = round(aggregate_subtotal * (1 - discount / 100), 2)
    return json.dumps({"items": items, "aggregate_subtotal": aggregate_subtotal, "final_total": final_total}, sort_keys=True)
```

This exact defect exists in the raw completion **before** parsing: calculated item results are discarded, the original input list is emitted without subtotals, the aggregate discount is not validated, and unrequested individual discounts affect aggregate arithmetic. Generated test expectations also contain incorrect arithmetic. Aider's application snapshot and returned candidate preserve this code; it is not an adapter-loss defect.

## FAILURE CLASS / ROOT CAUSE

For this synthetic call, the observed class is **changed complete files with semantic noncompliance already present in raw model output**. This is additional evidence under CASE G; it is not evidence that the original no-op has the same cause.

- CASE A: not reproduced; both files changed.
- CASE B: not reproduced; complete file listings were returned.
- CASE C: not reproduced; valid whole-file replacements were parsed and applied as returned.
- CASE D: not reproduced; no correct content was discarded by Aider.
- CASE E/F: prompt misunderstanding, length or duplication as a causal integration defect remains unverified; no controlled before/after comparison establishes it.
- Original real unchanged-candidate run: still unclassified from raw completion because its original raw response was not retained.

Do not convert a single semantically wrong output into a proven fundamental model-capability limitation. Do not infer that a more forceful prompt is a proven production fix when the target no-op is absent from the baseline reproduction. No speculative production change was made.

## SUMMARIZER / before-after observations

Unlike the prior shorter fixture, this call **actually reproduces**:

```text
Applied edit to test_inventory_app.py
Applied edit to inventory_app.py
Summarization failed for model ollama_chat/qwen2.5-coder:7b: cannot schedule new futures after shutdown
Summarization failed for model ollama_chat/qwen2.5-coder:7b: cannot schedule new futures after shutdown
summarizer unexpectedly failed for all models
```

Trace order: raw completion -> rendering -> apply_start -> apply_end -> main return -> summary_start -> main_exit -> failed summary model requests -> summary_end. File contents at summary_end exactly equal persisted apply_end contents. CLI exits 0. This real reproduction demonstrates that the shutdown warning can coexist with fully persisted changes, and did not cause file loss in this case. It does not establish all possible shutdown behavior or fix Aider lifecycle.

## CHANGE / BEFORE-AFTER PROOF

Only local ignored diagnostic scripts/evidence and this uncommitted audit were created. No production code changes or automated diagnostic artifact integration were added. Capturing broad production model prompts would need a justified bounded/redacted design; this fixture-only local capture is sufficient for the current investigation.

There is one valid live inference, not repeated generic attempts. No corrected candidate is claimed. The pre-edit synthetic baseline has six tests PASS but intentionally lacks required product behavior. The generated changed candidate fails its own tests and independent acceptance. It is never applied to the protected fixture and never promoted.

Independent acceptance checks quantitative JSON/CLI output, item count, validation, helper preservation and discount endpoints. Names for an aggregate-subtotal output key are not a prescribed product schema; the decisive missing output is the per-item subtotals, not a naming preference. An old single-item CLI test represents behavior intentionally superseded by the new exact-three entry-point objective, while helper compatibility remains required. That potential preserve-tests tension is a fixture confounder, not an established explanation of the historical no-op; independent output, validation and arithmetic defects remain directly observed.

## TEST EVIDENCE

| Command / evidence | Exit | Result |
| --- | --- | --- |
| `git fetch origin main`; `git switch main`; `git merge --ff-only origin/main` | 0 | Canonical baseline `1d7024f46d03709587913b3e4905d0b324ae7f40` |
| `<aider-python> .forgelab/runtime/setup-semantic-completion-fixture.py` | 0 | Two generic files only |
| `<aider-python> -m unittest discover -s .forgelab/runtime/semantic-completion-audit/fixture -v` | 0 | **6 baseline tests PASS** |
| `<aider-python> .forgelab/runtime/reproduce-semantic-completion.py` | Wrapper 0 / Aider 0 | Full raw completion captured; both files changed; source unchanged; real summary warning reproduced |
| `<aider-python> .forgelab/runtime/check-semantic-completion.py` | Wrapper 0 / generated test child **1** | **11 generated tests: 4 failures, 2 errors**; independent acceptance **6 cases: 5 failure records, 2 errors** including subtests; candidate not accepted |
| Existing current-runtime evidence from empty-edit investigation | 0, prior execution | **24 focused regressions PASS**: editor adapter, truthful semantic no-op/Security gate, inconsistent evidence fail-closed, PR #68 continuity, prewrite correction |
| Prior PR #69 Windows launcher evidence | 0, prior execution | **108 Python + 4 dashboard tests**, preflight/pip consistency/build/readiness and stability **6/6 PASS**; reused only for unchanged relevant code, not a new execution or candidate PASS |

No production candidate exists and the synthetic result already fails its first gate. Further Reviewer/Security approval, broad stabilization or Windows relaunch would not prove the missing root cause, so they were not performed. No PASS is invented for unexecuted checks. Existing no-op/source/scope/security/accounting/gate regressions remain unchanged.

## MODEL CAPABILITY ASSESSMENT / PR / residual risk

The local 7B model can emit and apply complete changed files, but this more complex single output is semantically wrong. Together with the earlier shorter failing synthetic candidate, this is a material reliability risk. It is insufficient evidence to declare a fundamental capability limit or to request a model/provider switch as the demonstrated remedy.

PR: **none**. The requested fix branch/PR is conditional on root cause and an effective correction being proved; that condition is not satisfied. No code commit exists.

The true original no-op still lacks its raw completion. No same-case before/fixed-after proof, deterministic candidate PASS, semantic Reviewer PASS or Security PASS exists. No Golden Path/Dental PASS is established.

## SINGLE NEXT ACTION

`STOP_AND_REPORT_UNVERIFIED_ROOT_CAUSE`.

Do not launch Dental. Preserve this raw synthetic evidence for Product Owner assessment before authorizing further diagnosis or any model decision.

# ForgeLab — semantic repair unresolved-contract validation, 2026-10-09

## RESULT / BASELINE EVIDENCE REUSED

**0/2 PASS — `STOP_AND_REQUEST_MODEL_DECISION`.**

Local and fetched remote main verified at `1d7024f46d03709587913b3e4905d0b324ae7f40`, containing PR #70. Reused the completed raw-completion investigation and its ignored evidence in `.forgelab/runtime/semantic-completion-audit/`; no baseline model call was repeated.

Before evidence: 2479 input tokens / 1796 output tokens, 7289-character raw completion; two authorized files changed but semantic defects already present before Aider parsing. Generated candidate: 11 tests, 4 failures and 2 errors; independent acceptance: six cases, five failure records and two errors including subtests. Mechanical whole-file application and post-write summarizer behavior were already established and were not investigated again.

The same protected two-file fixture, objective, acceptance contract, blocking review and independent acceptance harness were reused. The only experiment was the generic semantic-repair objective suffix. No Dental files were read/copied into the experiment or edited, no Dental run/promotion was performed, and existing services were left untouched.

## PROMPT CONTRACT CHANGE

An experimental change affected only the `semantic_aider_objective` construction in `src/forgelab/orchestrator.py`: 21 inserted / 3 removed lines, no generic initial-editor prompt changes.

The generic semantic contract explicitly states:

1. Blocking independent review means the candidate is not accepted.
2. SATISFIED requirements are preserved invariants unless a blocker requires a compatible extension.
3. Repair only unresolved blocking MISSING/PARTIAL/UNVERIFIED requirements.
4. Implement every blocker through authorized code/tests; discussion is insufficient.
5. Do not introduce unrequested concepts or behavior.
6. Derive quantitative test expectations from specified inputs/arithmetic.
7. Direct tests must prove each unresolved requirement.
8. Do not weaken/delete/rewrite valid tests just to obtain PASS.
9. Update explicitly superseded old tests only to the minimum extent required by the binding acceptance contract.
10. Internally check blocker-to-implementation/test mapping, arithmetic, preserved invariants and unauthorized behavior.
11. Unchanged files are not successful repair while blockers remain; use the unchanged whole-file edit contract.

No Dental, inventory, treatment or fixture wording was inserted into production. The exact experimental diff remains ignored locally as `semantic-completion-audit/experimental-contract.diff`. **The production change was reverted after validation failure.**

## CONTROLLED EXECUTION

Exactly two fresh local editing executions were performed, sequentially. Each started from the same unchanged protected source fixture, with a newly allocated disposable adapter workspace and fresh tool-home/history. Both use installed Aider 0.86.2, `ollama_chat/qwen2.5-coder:7b`, whole, existing production flags/options, 300-second timeout and local Ollama. Each trace contains exactly one editing completion; no editor retry or baseline re-execution was added. Background summary attempts do not constitute additional editing completions and were not changed or investigated.

The diagnostic runner evaluates the actual candidate `semantic_aider_objective` AST expression, as in the before experiment. It captures the complete model request/raw completion before rendering, parsed edits, snapshots, command, stdout/stderr, result and generated/independent tests. No model/parser response is modified by instrumentation.

Both runs use identical semantic-objective bytes, SHA256:

`2d130771fe93ac54277d13dc3b5e74e81538911776618f917c4e3715751cd074`.

The protected fixture source hashes before and after both runs are unchanged:

- `inventory_app.py`: `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`.
- `test_inventory_app.py`: `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`.

Model outputs differ between executions, but both exhibit the same decisive semantic failures.

## VALIDATION RUN 1

Local evidence: `semantic-completion-audit/validation-1/`.

- Raw completion: 6682 characters; 2687 input / 1641 output tokens.
- Aider exit 0; no timeout; duration 126828 ms.
- Both authorized paths changed; adapter scope checks complete; protected source unchanged.
- Generated tests: **10 tests; 2 failures, 3 errors; exit 1**.
- Independent acceptance: **6 cases; 1 failure, 1 error; FAIL**.
- CLI produces **36.45 instead of 40.50** for subtotals 20 + 15 + 10 and a 10% aggregate discount.
- Returned JSON includes original input items without their calculated `subtotal` values.
- Helper preservation, count rejection, discount endpoints and validation checks pass, but visible subtotals and the CLI quantitative result fail.

The raw returned code sums already-discounted item totals, then discounts the aggregate again. It also writes a subtotal into a transient result dictionary but emits the original items. These defects are present in the raw model completion and persist in the returned files. Generated tests invent expectations such as 75 and mishandle obsolete/invalid CLI test behavior.

## VALIDATION RUN 2

Local evidence: `semantic-completion-audit/validation-2/`.

- Raw completion: 6399 characters; 2687 input / 1591 output tokens.
- Aider exit 0; no timeout; duration 120547 ms.
- Both authorized paths changed; adapter scope checks complete; protected source unchanged.
- Generated tests: **9 tests; 2 failures, 1 error; exit 1**.
- Independent acceptance: **6 cases; 1 failure, 1 error; FAIL**.
- The same objective-level defects remain: no visible per-item subtotals; CLI returns **36.45 rather than 40.50** from double discounting.
- Other independent checks pass, but that partial success does not satisfy the all-requirements threshold.

## RELIABILITY RESULT / PRODUCTION CHANGE

**0/2 PASS**, against the required **2/2 PASS**. No weaker threshold, acceptance change, arithmetic accommodation, fixture modification or additional prompt layer was introduced. The exact independent harness was reused; its only differences are the selected evidence directory and local script filename.

The correction is not reliable enough for this semantic-repair class under the current ForgeLab constraints. This is the prescribed bounded validation result, not a universal claim that the model cannot perform any programming task. The historical Dental no-op remains unclassified; this experiment evaluates the captured semantic noncompliance class and does not retroactively fix that original run.

The experimental production change was reverted with:

`git restore --source=HEAD -- src/forgelab/orchestrator.py`.

`git diff --exit-code -- src/forgelab/orchestrator.py` and the final tracked diff are empty. PR #68 parent continuity, PR #69 SemanticRepairNoop, protected scope/source, truthful accounting, repair/prewrite distinctions, model/provider/budgets, Security and human gates are untouched. There is no production code commit, branch or PR. Both local calls remain EUR 0 through the existing local-only model path; no paid API was introduced.

## REGRESSION EVIDENCE

| Command | Exit | Result |
| --- | --- | --- |
| `git fetch origin main`; `git rev-parse main origin/main` | 0 | Both canonical SHA `1d7024f46d03709587913b3e4905d0b324ae7f40` |
| `<aider-python> .forgelab/runtime/run-unresolved-contract-1.py` | Wrapper 0 / Aider 0 | One fresh completion; two authorized changes; source unchanged |
| `<aider-python> .forgelab/runtime/check-unresolved-contract-1.py` | Wrapper 0 / generated child **1** | Generated tests FAIL; independent acceptance FAIL |
| `<aider-python> .forgelab/runtime/run-unresolved-contract-2.py` | Wrapper 0 / Aider 0 | Second and final fresh completion; two authorized changes; source unchanged |
| `<aider-python> .forgelab/runtime/check-unresolved-contract-2.py` | Wrapper 0 / generated child **1** | Generated tests FAIL; independent acceptance FAIL |
| `Get-FileHash <two protected fixture files> -Algorithm SHA256` | 0 | Exact before/after source hashes above |
| `git diff --check`; restore; `git diff --exit-code -- src/forgelab/orchestrator.py` | 0 | Experimental change reverted; no production diff |

Per the explicit <2/2 STOP instruction, no new production unit regression, component/stabilization/Windows launcher run or fix PR was added. Previous baseline regression evidence remains valid for unchanged production code, but no unexecuted new PASS is claimed. No semantic Reviewer/Security acceptance is claimed for failed synthetic candidates and no automatic promotion occurred.

## DELIVERY / MODEL DECISION STATUS

Only this local uncommitted audit and ignored diagnostic evidence were added. The earlier semantic-completion audit remains untouched. Runtime paths/model requests are intentionally not published automatically.

PR: **NONE**.

**Model decision required from the Product Owner.** Do not switch the model/provider automatically and do not add retries, repair-budget increases, format changes, deterministic product special cases or Dental-specific logic to conceal this failure. No additional model experiment is run under this task.

## SINGLE NEXT ACTION

`STOP_AND_REQUEST_MODEL_DECISION`.

Do not run Dental.

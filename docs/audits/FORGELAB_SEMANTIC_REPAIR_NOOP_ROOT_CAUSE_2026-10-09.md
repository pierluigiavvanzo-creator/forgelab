# Semantic repair no-op — evidence, bounded correction and diagnostic limit

## Baseline

Local and fetched remote main both equal `741ba4f65a10a7d3628dec74982477d0108492f1`, merge of PR #68. Main and protected Dental source were clean before diagnosis. One branch: `fix/semantic-repair-noop-root-cause`. Code commit for Windows verification: `555d6ee1d7be02975afd8cd24f9f0b40f3587681`.

Scope: ForgeLab only. No new Dental run, target file edit, promotion, paid API, model/provider/options change, increased retry/repair budget, historical PR closure or automatic merge. Dental remains at `42e026093960a8acc4cb64087433d90c5f537efb`.

## Latest run facts

`run-1772ceaf77f0`: CLOSED, terminal=true, GateDecision REPAIR, six deterministic tests PASS in one test execution, two ledger LLM calls (planner/review), two reusable editor calls, EUR 0. History reaches REVIEW -> REPAIRING -> CLOSED. RunSummary counts zero repairs; the developer artifact has zero prewrite attempts and an empty repair list. The failure artifact nevertheless claims PREWRITE_RECOVERY_EXHAUSTED and one prewrite recovery, with empty first_error.

All available artifacts and task results were inspected: RunSummary, RunStatus, ExecutionPlan, AIPlan, AIDeveloperPatch, Changes.patch, TestEvidence, AIReview, ReviewReport, PrewriteRecoveryFailure, UsageReport, ToolAudit, SecurityReport, GateDecision, ContextBundle/MemorySnapshot metadata, and plan/implement/test task results. No review-repair task result exists. ToolAudit shows two initial governed edits plus one successful test; no semantic-repair writes. SecurityReport reports protected source unchanged. The isolated original workspace no longer exists.

This is a fresh top-level run: `parent_run_id` and `parent_candidate_ref` are null. PR #68 parent seeding is not exercised by this run, and is not evidence of a parent-continuity regression.

## Deterministic candidate facts

The latest governed candidate is the initial full-file set in AIDeveloperPatch: no repair was applied. Read-only in-memory probes use captured strings and mocked Tk widgets; they do not write Dental files or constitute a new Dental run/UI usability PASS.

| Requirement | Actual candidate | Evidence |
| --- | --- | --- |
| Exactly three treatments in quote/UI | Missing | One treatment input; helper accepts three alternative names but operates on one treatment |
| Automatic subtotals | Partial | Single-item helper returns subtotal 80; no three-treatment accumulation |
| Visible subtotals | Missing | QuoteApp has no subtotal field/label |
| Discount range 0–100 | Present | -1 and 101 rejected; validation is explicit |
| Discounted final total | Correct for one item, missing aggregate | All three permitted names individually accept 80/10 -> 72; no combined three-treatment quote |
| Final-total label updates | Present for one item | Cleaning 80/10 displays EUR 72 |
| Invalid input handling | Present for ordinary invalid input | Nonnumeric price invokes error dialog; blank name/nonpositive price/invalid treatment/range checks exist |
| Tests verify required UI behaviors | Missing | Six tests PASS; tests exercise only calculate_quote, no UI, multi-row subtotal or positive-discount UI/aggregate assertion |

Candidate source SHA256 `0b171a267a8d223d8d90504bd964700778b325db3c921955955d27fa26b353c6`; test SHA256 `99cc6434040bd52f469756dfbc2dc0622ecbcfa4982cd62c03dccf3a99ada943`. Raw Changes.patch SHA256 `f164e50feb75a68d81f161f8dc3ef9756b98559ed7f3e1a68a9259ef9f8de327`. This probe is not exhaustive numerical edge-case or real-window usability validation.

## Reviewer accuracy

**Partially correct.** Blocking missing multi-treatment behavior/subtotals/test coverage is justified. Its statement that Extraction and Implant are not implemented is false: direct calls for all three allowed names succeed. Its broad final-total finding overlooks that single-item discount math is correct, while aggregate functionality is absent. The PM contract also frames three treatments as a calculate_quote function change; this may explain ambiguity, but is not proof of the model's no-op decision.

## Exact no-op trace and what cannot be proved

1. Initial Aider full-file candidate is validated and applied through ToolGateway; its tests pass.
2. Reviewer FAIL is built from complete current files, objective and acceptance contract without the duplicate diff removed in PR #68.
3. Semantic Aider objective combines the original objective, binding PM contract, complete blocking review and preservation/scope directive. The adapter supplies the authorized current files in its isolated sandbox.
4. `_run_aider_editor` rejects nonzero exit or timeout before returning. The observed later no-op exception therefore follows a completed editor call with empty changed_paths.
5. Adapter computes changed_paths by comparing every authorized file's final text with its initial text; real subprocess regressions verify both changed and identical files. No demonstrated detection bug exists. Transient internal edits reverted before return would still be a net no-op.
6. Orchestrator raises AIDeveloperFormatError before constructing any semantic patch/recovery. The generic outer format/reference/syntax handler fabricates PREWRITE_RECOVERY_EXHAUSTED, one attempt and no first_error. The repair counter increments only later after application and thus remains zero.

**Aider no-op: incorrect relative to the requested product outcome**, because required three-treatment UI/subtotal/tests remain absent. **The historical model/CLI reason for returning no edits is UNVERIFIED.** Successful editor stdout/stderr is not persisted on this path, the temporary tool home is deleted, and API logs do not retain it. The original before/after editor snapshots and chat response cannot be recovered from the available artifacts. A replay would be a new inference, not proof of the original decision; no replay/new Dental run was performed. Do not claim a parsing failure, prompt truncation, false-review recognition or model motive without that missing evidence.

| Requested hypothesis | Conclusion |
| --- | --- |
| A — already satisfies requirements | Ruled out by candidate audit |
| B — false Reviewer failure, correct no-op | Some assertions are false, but legitimate product blockers remain; not a correct product-completion no-op |
| C — insufficient/contradictory/truncated repair evidence | Original objective/review can be reconstructed; incorrect review statements exist. Causal model decision cannot be proved without its response |
| D — changed-path detection failure | No demonstrated bug; real adapter comparison regressions PASS |
| E — PR #68 continuity wrong here | Not applicable to fresh run; continuity and stale-baseline regressions remain PASS |
| F — legitimate zero-change return misclassified as exhaustion | **Proved**: no recovery call, empty first_error, hardcoded attempt count and generic exception handler |
| G — other model/CLI explanation | Unverified; original stdout/stderr was discarded |

## Bounded ForgeLab correction

- Treat zero-change semantic repair as its own governed outcome, not a format-validation/recovery exception. Consume/count one semantic repair attempt and record `outcome=NO_OP` in the developer history and a repair task.
- Verify returned files equal the current candidate before reusing passing deterministic evidence. Inconsistent file/changed-path evidence fails closed as EDITOR_EXECUTION_FAILED; it is not accepted as a no-op.
- Persist `SemanticRepairNoop.json`: exact repair objective and blocking review, complete editor stdout/stderr, exit/timeout/duration, before/after UTF-8 content hashes, zero prewrite attempts and no candidate writes.
- Perform exactly one fresh grounded semantic reconsideration of unchanged files and normal scope checks, using existing passing tests because content is identical. This is the normal post-repair review, not an editor retry or increased repair budget. Do not feed editor self-approval into product acceptance or force Reviewer PASS.
- If review remains blocking: record SEMANTIC_REPAIR_NOOP failure and failed task; CLOSED / REPAIR. If it passes: continue through the existing Security and explicit human gate. Security failure still blocks READY_FOR_DECISION. A zero-change return alone never approves anything.
- Expose the optional artifact through authenticated API and dashboard evidence; show its truthful reason only for failed no-op reconsideration. Real prewrite exhaustion remains unchanged.

Changed code: orchestrator.py, artifacts.py, api.py, dashboard/app/page.tsx. Extended existing tests: test_orchestrator.py, test_editor_adapter.py, test_api.py. No adapter detection implementation, governance/parent seeding, provider/router or dependency/configuration change. Canonical docs synchronize main/PR #68 and this pending review gate.

## Test evidence

| Command/check | Exit | Result |
| --- | --- | --- |
| New exact no-op regression on unmodified main behavior | 1 | Both scenarios fail: counter remains 0 and complete unchanged candidate closes without reconsideration |
| Focused no-op / real prewrite / continuity / actual changed-path / API artifact regressions | 0 | 6 tests PASS; no-op test includes incomplete, complete and Security-blocked subcases; no promotion/source mutation |
| `py -3.11 -m unittest tests.test_orchestrator.MultiAgentTests.test_aider_semantic_noop_is_rereviewed_and_truthfully_accounted tests.test_orchestrator.MultiAgentTests.test_aider_semantic_repair_retests_and_reaches_human_gate tests.test_orchestrator.MultiAgentTests.test_semantic_review_failure_uses_bounded_repair_and_rereview tests.test_orchestrator.MultiAgentTests.test_native_repair_rejects_stale_baseline_and_invalid_candidate_before_model -q` | 0 | 4 PASS |
| `py -3.11 -m unittest tests.test_orchestrator.MultiAgentTests.test_semantic_noop_rejects_inconsistent_file_evidence -q` | 0 | Inconsistent no-op file evidence fails closed before further review; no false prewrite failure/source write |
| Read-only captured candidate probe | 0 | One treatment UI, no subtotal UI, positive single-item discount label 72, ordinary invalid input rejected, six original helper tests PASS |
| Read-only full canonical patch reconstruction | 0 | Every hunk/context matches initial old_text and reconstructs exact new_text for both candidate files; no stale developer/Changes.patch mismatch |
| `CI=true; corepack pnpm install --offline --frozen-lockfile` in isolated dashboard | 0 | Existing policy/package cache reused; no downloads or dependency/configuration changes |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start-ForgeLab.ps1 -ApiPort 8876 -DashboardPort 5274` in isolated checkout | 0 | **108 Python tests PASS**: adapter 20, orchestrator 51, API 26, dashboard feedback 11; Aider preflight/pip consistency; **4 dashboard callbacks PASS**; frozen-lockfile installation, production build, initial readiness and **6/6 Windows stability PASS** |
| Isolated API health | 0 | Served exact code SHA `555d6ee1d7be02975afd8cd24f9f0b40f3587681`; Aider dependency fingerprint unchanged |

**Internal technical stabilization PASS. Full historical Aider-decision root-cause diagnosis remains UNVERIFIED, not PASS.** ModelRouter/provider unchanged; valid previous 16/6-test evidence reused. No GitHub Actions workflow/remote CI PASS is claimed. Failed baseline regressions and the first post-fix CLOSED assertion failure are preserved as diagnostic evidence; the latter exposed a missing explicit terminal transition and was corrected before the final gate.

Ignored evidence: `.forgelab/runtime/noop-regression-baseline.log`, `noop-candidate-facts.json`, `noop-offline-install.log`, `noop-launcher.log`, `noop-verification-runtime.json`. Launcher logs contain the authenticated local dashboard URL and must not be published without redaction. This audit does not contain that token or generated Dental implementation code.

Cleanup: only completed synthetic smoke `run-97db0d5afce7`, READY_FOR_DECISION, with no nonterminal status/new run. Verification API PID 87116 and dashboard tree rooted at 90128/listener 94504 were stopped after live SHA, listener ownership and common launcher-parent checks. Original listeners remain 8875/89104, 5273/89280, 8765/78632 and 5173/66608. Temporary worktree registration/files were removed after unlinking shared Aider; native extended-path cleanup handled Git's Windows Filename too long limitation. Original Aider executable remains present. Final Dental Git status is clean at the unchanged HEAD.

Canonical memory updated: PROJECT_STATE.md, ROADMAP.md, DECISIONS.md, HANDOVER_CURRENT.md, AGENTS.md and MANIFEST.md. The permanent AGENTS_MASTER mandate remains unchanged. Original run artifacts are preserved; the historical bad classification was documented rather than retroactively rewriting evidence.

## Residual risk and delivery gate

The specific ForgeLab no-op classification/accounting/evidence defect is fixed and regression-tested. This does not prove why the original local model made no edit; **do not label the full historical Aider root-cause investigation PASS**. The model may still fail to implement requirements. Complete stdout/stderr retention makes subsequent occurrences diagnosable, subject to the model actually explaining its decision. Independent semantic/Security/human gates remain essential. Unchanged candidate reconsideration adds one local review call within the existing repair attempt, with EUR 0 and no generic retry. Existing best-effort egress/transitive dependency limitations and separate launcher hardening remain unchanged.

Published single [PR #69](https://github.com/pierluigiavvanzo-creator/forgelab/pull/69), OPEN/unmerged against main `741ba4f65a10a7d3628dec74982477d0108492f1`. Code `555d6ee` and evidence/state `bf0b0bc` pushed; subsequent delivery-link update is documentation only. No merge or historical PR changes. Single next action: `HUMAN_REVIEW_AND_MERGE_SEMANTIC_REPAIR_NOOP_FIX`. **Do not launch a new Dental run now.** Golden Path remains NOT PASS. This report is the complete handoff for ChatGPT Web; original generated Dental code has not been manually corrected.

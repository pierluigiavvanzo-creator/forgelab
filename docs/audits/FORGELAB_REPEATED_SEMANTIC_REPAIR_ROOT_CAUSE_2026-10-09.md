# Repeated semantic repair — verified diagnosis, 2026-10-09

## Baseline and boundaries

Fetched local/remote main: `ad6f460e8b3cc43f041badd4686d8b09676b27c1`, containing merged PR #67. One branch: `fix/repeated-semantic-repair-root-cause`. Tested code commit: `59537cff8c1c0fd5c4e2f0cd773e352c9d9f9cb4`. No automatic merge, promotion, new Dental run, target edit, paid fallback, model/options change or retry/repair-budget increase.

Dental source remains clean at `42e026093960a8acc4cb64087433d90c5f537efb`. Captured candidate files were reconstructed from run artifacts into ignored `.py.txt` snapshots and executed only in memory with mocked Tk widgets. These diagnostic probes are not a new ForgeLab/Dental run or a visible usability gate.

## Latest candidate facts

Latest native repair: `run-a65d908fd535`, parent `run-797899d24f2a`. Final summary: REVIEW / tests PASS / Repair required. The original objective and PO feedback reach the child plan, acceptance contract and Aider semantic repair objective. This is not a demonstrated feedback-omission defect.

Final source SHA256: `f88b16d842f10fa0a07ea866232244ce8ae06f278e317e57d01553df48bd19ce`.
Final test source SHA256: `e5fef0cdd2d3a45a13e8908da7498bfed26c40dfa2255bb571ea06d4ea860f84`.

| Required behavior | Actual final candidate | Verification |
| --- | --- | --- |
| Exactly three treatments | Present: three UI entry rows | Widget probe: 3 |
| Visible calculated subtotals | Present | Labels EUR 80 / 100 / 50 |
| Percentage discount bounded 0–100 | Present in helper and UI call path | -1 and 101 rejected |
| Discounted final total | **Incorrect in UI** | Prices 80/100/50, discounts 10/5/0: expected 217, displayed 230 |
| Final UI label updates | Present, but updates to wrong value | `calculate()` sums undiscounted subtotals |
| Invalid-input handling | Present for ordinary invalid input | Nonnumeric UI price invokes error dialog; helper validates blank name, nonpositive price and discount range |
| Tests cover these behaviors | **Incomplete** | Six captured tests PASS; tests call only `calculate_quote`, without UI assertions |

The earlier Aider semantic-repair snapshot already displays the correct discounted EUR 217 for the same inputs and the three subtotal labels. The subsequent full-file semantic correction regresses the UI total to EUR 230. Passing helper tests miss this regression. This report does not claim exhaustive numeric-edge-case coverage or real-window usability PASS.

## Reviewer accuracy and root cause

Reviewer accuracy is **partially correct**. Final blocking review is justified by the incorrect UI total and absent UI coverage. Assertions that no treatment/subtotal UI or no relevant implementation exists contradict the captured source. Final extracted requirements also include review instructions as if they were product obligations.

Two demonstrated defects share the candidate/evidence continuity boundary:

1. Native API repair constructs a new request against protected source HEAD, without seeding the parent candidate. Parent final source is 5160 characters; child initial patch `old_text` is the original 1853-character baseline. Existing unpromoted progress is discarded before the planner/editor. Feedback alone cannot preserve it.
2. Semantic review sends complete current files plus a duplicate diff. Actual Ollama review1 logs show 4847 input tokens truncated to 2050 under the unchanged 4096 context. Its answer denies implementation present in the Aider repair snapshot. Orchestrator does reread the current workspace after edits; the proven issue is prompt duplication/context delivery, not a stale on-disk workspace read.

Review1 UsageReport input count is 2050. The final semantic-correction retry succeeds after one timeout; final review input count is 3868. All provider costs are EUR 0. These facts do not prove a general model-quality guarantee or that every future request fits the context window.

## Complete bounded change

- `api.py`: native repair passes trusted parent run ID, exact base HEAD and final cumulative `Changes.patch`; rejects missing parent evidence before child execution; exposes optional lineage JSON. External create-run JSON cannot supply the internal parent fields.
- `orchestrator.py`: validates parent baseline and patch in a temporary isolated workspace before any model call, validates existing target paths/full-file schema/Python syntax, supplies parent files to planner, and seeds actual isolated editor workspace through existing governed writes. Checks baseline again before execution. Child `Changes.patch` remains cumulative against protected source HEAD. Records parent ID, baseline, patch/content hashes and changed paths.
- `governance.py`: audited parent patch reconstruction, restricted to authorized existing text targets. Rejects out-of-scope headers, rename/copy, creation/deletion, mode and binary changes. Checks applicability before applying inside the preview; bounded subprocess execution. No promotion path or protected-source write.
- `artifacts.py`: optional lineage JSON and patch registration; mandatory run-artifact contract unchanged.
- Tests: API evidence propagation/missing-evidence rejection, planner/Aider/current Reviewer continuity, cumulative patch and unchanged protected source, stale baseline/malformed syntax/nonapplicable patch rejection before model/editor, denied scope/mode/rename/binary patch before Git, contract retention through semantic rereview without duplicate diff.
- Reviewer prompt retains current complete files, objective, acceptance contract and test evidence once; separates product obligations from evaluator instructions. Existing schema, blocking findings and human gate remain enforced. No PASS is forced.

## Executed evidence

| Command/check | Exit | Result |
| --- | --- | --- |
| Pre-fix exact native API/orchestrator regressions | 1 | Reproduced missing parent request fields/continuity |
| `py -3.11 -m unittest tests.test_api.ApiTests.test_human_repair_creates_bounded_child_run tests.test_orchestrator.MultiAgentTests.test_native_repair_preserves_parent_candidate_for_planner_aider_and_review -q` | 0 | Both PASS after repair |
| Focused safety regressions | 0 | Scope/mode/rename/binary denied; stale HEAD, bad Python and nonapplicable patch rejected before model/editor; source unchanged |
| `py -3.11 -m unittest tests.test_api.ApiTests.test_human_repair_requires_parent_candidate_evidence_before_child -q` | 0 | Missing summary/patch rejected; no child call |
| `py -3.11 -m unittest tests.test_orchestrator.MultiAgentTests.test_semantic_review_failure_uses_bounded_repair_and_rereview tests.test_patch_artifact_bytes -q` | 0 | 3 PASS; acceptance contract now reaches both reviews |
| Initial affected-component invocation | 1 | 83 actual tests: one stale prompt assertion failed; accidental nonexistent `tests.test_artifacts` import added a loader error. Corrected assertion and used existing patch-byte tests. No implementation failure hidden |
| Read-only captured final candidate probe | 0 | Six original helper tests PASS despite UI total 230 instead of 217 |
| Read-only captured Aider repair UI probe | 0 | Three subtotals and correct UI total 217 before subsequent correction regression |
| `CI=true; corepack pnpm install --offline --frozen-lockfile` in isolated dashboard | 0 | Existing package/policy cache reused; no dependency/configuration change |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start-ForgeLab.ps1 -ApiPort 8876 -DashboardPort 5274` in isolated checkout | 0 | **105 Python tests PASS**: editor 19, orchestrator 49, API 26, dashboard feedback 11; Aider CLI/flags/dependencies preflight PASS; **4 dashboard lifecycle callbacks PASS**; frozen-lockfile installation and production build PASS; initial readiness and **6/6 stability checks PASS** |
| Isolated health and ownership check | 0 | Served SHA exactly `59537cff8c1c0fd5c4e2f0cd773e352c9d9f9cb4`; expected test listener PIDs 70252/95192 |
| Cleanup safety check | 0 | Only completed synthetic smoke `run-4900b91df854`, READY_FOR_DECISION; no nonterminal status or new run. Stopped only owned verification API/dashboard tree. Existing ports/PIDs 8875/77276, 5273/61276, 8765/78632, 5173/66608 unchanged |

**Internal stabilization: PASS (success CASE 1).** The latest product candidate was incomplete and the demonstrated native repair orchestration defect is now fixed/regression-tested. This does not mark Dental Golden Path PASS.

ModelRouter/OllamaProvider are unchanged; previously verified 16/6 tests remain valid and are not duplicated. No GitHub Actions workflow exists, so no remote CI PASS is claimed. Aider dependency fingerprint remains `4ee13742aa59411f7a39e64fab38df189c529accf0258dba6608f0f7d8462202`.

Ignored diagnostic artifacts: `.forgelab/runtime/semantic-repair-proof/`, `repeated-repair-components.log`, `repeated-repair-api-negative.log`, `repeated-repair-offline-install.log`, `repeated-repair-launcher.log`. The launcher log includes the local authenticated dashboard URL and must not be published without redaction. The isolated checkout reused only policy-cache, package files and index database; its pnpm `projects` link was not copied from the primary cache. Cleanup initially refused an overly strict absolute-path CLI ownership check because the unmodified launcher passes a relative runs path; verified metadata, parentage, listener binary path and served SHA were used before any service stop.

## Delivery

One branch/PR; no automatic merge. Canonical state files updated: PROJECT_STATE, ROADMAP, DECISIONS, HANDOVER_CURRENT, AGENTS and MANIFEST. The permanent AGENTS_MASTER mandate is unchanged. Frozen older PRs are untouched; no PR has been closed. Full report above is the handoff for ChatGPT Web.

The temporary checkout registration and files were removed after stopping only its owned services. Git removal encountered Windows `Filename too long`; native PowerShell cleanup used the verified literal extended path after removing the Aider junction. The original Aider executable remains present. Ignored proof/metadata/log artifacts remain in the primary repository.

## Residual risk and single next action

The captured Dental candidate is incomplete and remains unpromoted. This fix restores native candidate continuity and reduces demonstrated review-context loss; it cannot guarantee that the unchanged local model preserves every behavior during future full-file corrections. Review/Security/test/human gates remain required. Large future candidate sets may still exceed model context. Missing, incompatible or stale parent patches fail closed rather than rebasing silently. Existing launcher hardening at `ea00719` remains separate/unmerged; the historical intermittent API failure remains undiagnosed.

After internal stabilization PASS: `HUMAN_REVIEW_AND_MERGE_REPEATED_SEMANTIC_REPAIR_FIX`. **Do not start another Dental run now.** No Golden Path PASS is claimed; merge and runtime alignment remain prerequisites for any later human-authorized unchanged Golden Path attempt.

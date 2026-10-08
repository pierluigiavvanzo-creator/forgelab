# ForgeLab post-PR64 verification — 2026-10-08

## Importance

**A — Product Critical.** Verify the reusable editor and long-run control plane before consuming another Product Owner Dental submission. Expected value: eliminate demonstrated operator/debugging failures without expanding product scope. Product remains PRE-MVP; commercial evidence remains C0.

## Verified baseline

- Repository: `pierluigiavvanzo-creator/forgelab`.
- Checkout: `C:\Users\NITRO\Documents\GitHub\forgelab`.
- Initial branch: `main`, tracked working tree clean.
- Local HEAD and live `git ls-remote origin refs/heads/main`: `6d55b5587bf44a7efbcc0a81090ba5b6a7bdc98d`.
- GitHub PR #64: merged 2026-10-07 12:56:43 UTC, merge SHA matches HEAD.
- One correction branch: `fix/post-pr64-run-lifecycle-stabilization`.
- Windows; PowerShell 7.6.5; supported launcher interpreter Python 3.11.9; default shell Python 3.14.5; Node 26.2.0; pnpm 11.25.0; actual installed Aider 0.86.2.
- No `.github/workflows`. GitHub connector's commit workflow query returned an empty list (the connector filters PR-triggered workflows). No remote CI PASS is asserted.

The two supplied handoff documents were evidence/checklists, not a substitute for the user's request or Git truth. Their SHA was reverified, their claims of missing execution were replaced with actual results, and their obsolete merge gates were corrected.

## Executed test evidence

Commands use the repository root unless marked dashboard. `PYTHONPATH=src`; `PY311` denotes the exact installed executable `C:\Users\NITRO\AppData\Local\Programs\Python\Python311\python.exe`.

| Command / stage | Exit | Executed result |
|---|---:|---|
| `git ls-remote origin refs/heads/main` outside sandbox | 0 | Canonical SHA above |
| Default Python 3.14.5 focused tests, outside sandbox | 0 / 1 / 0 / 0 | Adapter 16 PASS, orchestrator 44/46 (one failure, one error), API 17 PASS, dashboard source checks 11 PASS |
| `PY311 -m unittest discover -s tests -p test_editor_adapter.py -q` on baseline | 0 | 16 PASS |
| `PY311 -m unittest discover -s tests -p test_orchestrator.py -q` on baseline | 0 | 46 PASS |
| `PY311 -m unittest discover -s tests -p test_api.py -q` on baseline | 0 | 17 PASS |
| `PY311 -m unittest discover -s tests -p test_dashboard_run_form_feedback.py -q` on baseline | 0 | 11 PASS; source assertions, not browser behavior |
| `PY311 -m unittest test_api.RunLifecycleTests -v` with `PYTHONPATH=src;tests`, first four regressions before fix | 1 | 2 failures + 2 errors: queue reservation, status after decision, corrupt-status failure, concurrent repair |
| Dashboard: `node --test scripts/test-run-lifecycle.mjs` before fix | 1 | 3 failures / 1 PASS: refresh loses connection, FAILED and INTERRUPTED skip evidence |
| Dashboard: `corepack pnpm install --frozen-lockfile` | 0 | Existing lockfile installed unchanged |
| Dashboard: `corepack pnpm run build` | 0 | Production build PASS |
| Dashboard: `corepack pnpm run lint` before fix | 1 | 3 React set-state-in-effect errors, 4 warnings |
| Dashboard: `corepack pnpm exec tsc --noEmit` | 0 | Type check PASS |
| Candidate: `PY311 -m unittest discover -s tests -p 'test*.py' -q` | 0 | **169 PASS**, including **98 focused tests** (16 + 46 + 25 + 11) |
| Candidate dashboard: `node --test scripts/test-run-lifecycle.mjs` | 0 | **4 executable callback tests PASS** |
| Candidate dashboard: `node node_modules/typescript/bin/tsc --noEmit` | 0 | PASS |
| Candidate dashboard: `node node_modules/eslint/bin/eslint.js . --ignore-pattern dist --ignore-pattern .next` | 0 | No errors; 2 existing exhaustive-deps warnings remain |
| `PY311 -m compileall -q src tests` | 0 | Python syntax PASS |
| PowerShell Parser.ParseFile(`Start-ForgeLab.ps1`) | 0 | No parse errors |

Initial sandbox attempts were not application evidence: Python temporary directories returned WinError 5; the sandbox hid Python 3.11 from `py`; Corepack/Git DNS failed. The corresponding commands were rerun with approved access. The Python 3.14 failures were traced to two fixtures relying on nested-quote f-strings being invalid under Python 3.11; those strings are valid in 3.14. No runtime fix was invented for that interpreter-dependent fixture behavior. Supported Python 3.11 verification passes.

### Windows launcher and real toolchain

Executed the **original launcher statements through runtime metadata**, from an in-memory script block, with `$PSScriptRoot` set to this checkout. Only the final browser-opening/report section was omitted; no Dental submission occurred.

The exact extraction used:

```powershell
$launcherText = Get-Content -LiteralPath .\Start-ForgeLab.ps1 -Raw
$runtimeText = $launcherText.Substring(0, $launcherText.IndexOf('# OPEN AUTHENTICATED DASHBOARD'))
$runtimeText = $runtimeText.Replace('$PSScriptRoot', "'C:\Users\NITRO\Documents\GitHub\forgelab'")
& ([scriptblock]::Create($runtimeText)) -ApiPort 8875 -DashboardPort 5273
```

- Actual Aider `--version` and required `--help` CLI flags PASS for 0.86.2.
- Actual isolated Aider `python -m pip check`: exit 0, no broken requirements.
- Actual `pip freeze` snapshot SHA-256: `85ef66478d5910148604c517c8b61a5a7d6c9fd8d55e03cabe1a92487c1bfc6e`.
- Original focused 90-test launcher gate PASS before adding regressions.
- Candidate launcher focused gate and executable dashboard callbacks PASS.
- First standard-port startup stopped safely: 5173 was occupied by a workerd process not owned/identified as this checkout. That process was not terminated.
- Isolated ports 8875 (API) and 5273 (dashboard): launcher exit 0, initial readiness PASS and **6/6 stability checks over 30 seconds PASS**.
- Generated initial smoke run is an internal ForgeLab fixture, not Dental.
- Local raw logs: `.forgelab/runtime/post-pr64-launcher.log`, `post-pr64-launcher-isolated.log`, `post-pr64-full-tests.log`; dependency snapshot `aider-freeze.txt`. These are generated local evidence, not committed credentials or target-product code.
- Startup performed before commit reported the baseline HEAD even though candidate files were modified. It is candidate working-tree evidence, not proof that canonical main contains these fixes.

The dashboard behavioral tests execute the page's actual callbacks with browser/fetch doubles. They verify reconnect after fragment removal and polling termination/evidence loading; they are not a claim of a complete visual browser acceptance test.

## Findings and changes

**Canonical baseline stabilization: FAIL. Candidate local checks: PASS, human integration gate pending.**

All runtime corrections belong to the demonstrated **incomplete asynchronous run lifecycle** class.

1. **Queue reservation leaked after failed durable write.** `_active_run_id` was set before writing QUEUED; an OSError left subsequent submissions permanently blocked. Reserve only after successful queue persistence and normalize the write failure to ApiError.
2. **Run state diverged after a human decision.** The status endpoint kept returning the original READY_FOR_DECISION even when the durable summary had advanced to DONE/CLOSED/REPAIRING. Status, list and returned artifacts now use one effective view. A live worker's transient state and explicit FAILED/INTERRUPTED take precedence over an early summary, preventing premature polling completion and false success.
3. **Worker failure could fail again while reading corrupt status.** JSON/OSError exceptions in the failure handler were not covered. The fallback now writes a governed terminal failure and releases the reservation when storage is writable.
4. **Human repairs bypassed the run slot.** Repairs could execute alongside a new run. Existing synchronous repair and decision endpoints now share the same local exclusion slot, returning conflict instead of executing concurrently. No repair budget or promotion rule was changed.
5. **Refresh recovery lost authentication.** The launcher fragment was removed and connection data existed only in React memory. Connection credentials now survive same-tab refresh in sessionStorage, not persistent localStorage; storage-disabled browsers retain manual connection fallback.
6. **FAILED/INTERRUPTED polling skipped final artifacts.** Terminal evidence now loads before the error notice; dashboard status/run-id/error display supports status-only terminal runs.
7. **Executed lint failures.** Form feedback resets and artifact-prefill updates now occur in their originating events; initial connection runs in a cancellable scheduled callback. No rule was disabled. Two existing dependency warnings are recorded rather than silently claimed fixed.
8. **Regression gate.** Added eight API lifecycle tests and four executable dashboard callback tests; launcher invokes dashboard behavior checks after dependency installation. Background launcher processes use hidden windows.

No Aider adapter/orchestrator code or Dental target code changed. No paid provider, dependency version change, retry increase, custom recovery catalogue, broad refactor, promotion bypass, CI activation, force operation or automatic merge was introduced.

## Aider boundary review matrix

| Surface | Evidence / conclusion |
|---|---|
| CLI pinned 0.86.2 | Real installed version/help contract and pip check PASS; adapter command reviewed against launcher flag list |
| workspace / tool-home | Disposable copies; separate HOME/USERPROFILE; explicit config/env/history/model metadata routing; 16 executed adapter tests |
| Normal/hidden unauthorized files | Workspace scan rejects unauthorized files including hidden files; no tool-file exception |
| Read-only / path alias / escape | Input scope resolution, alias rejection and before/after read-only comparison reviewed and tested |
| Deletion / non-UTF8 / process / timeout | Governed EditorAdapterError/EditorResult paths; exit 124 timeout, bounded output; executed regressions |
| Inherited environment | Minimal allowlist; API/provider credentials absent; explicit loopback Ollama URL; tested |
| Model / paid-provider path | Adapter normalizes to Ollama transports, local metadata; local provider routes and zero-spend evidence tested; no real paid API/model invocation |
| Egress claim | Proxy guard is best-effort application control, not firewall or hostile-process containment |
| Generic vs editor timeout | 60-second generic default vs 300-second editor default; API bounds and propagation tested |
| All four Aider phases | Exactly one `_run_aider_editor` implementation used for initial edit, pre-write correction, failed-test repair/correction and semantic repair |
| Governed writes | Candidate import/pre-write checks precede ToolGateway; deterministic tests, bounded repair, independent semantic Reviewer and Security remain in place |
| Source / promotion | Existing API/orchestrator/promotion regressions verify source unchanged before explicit human approval |

## Lifecycle review matrix

| Surface | Evidence / conclusion |
|---|---|
| POST /v1/runs | Existing actual HTTP tests verify 202 + run_id before a blocked worker completes |
| One active run | Local instance Lock; added repair/decision exclusion and reservation-release tests |
| Durable status | Atomic replace; queue/start/failure tests; effective status follows terminal summary after decisions |
| Completion ordering | Added partial-summary regression; live worker cannot be mistaken for terminal completion |
| Worker exceptions | Terminal FAILED with error; corrupt-status regression; no claim that persistent disk failure can be repaired in memory |
| API restart | Existing INTERRUPTED recovery test and added completed-summary precedence test |
| Browser refresh | Executable callback test reproduces and fixes credential loss after hash removal |
| Polling | One status request on terminal; loads evidence for READY_FOR_DECISION, FAILED and INTERRUPTED |
| Artifacts / decisions | Full suite includes human repairs, exact local promotion, source-integrity checks and API compatibility |
| Human repair | Existing synchronous HTTP 201 contract preserved; serialized with other operations. Child repair refresh recovery is not claimed |
| Product autonomy | Fixes reduce connection/debug work, but Dental end-to-end autonomy remains unproven |

## Canonical memory sync

Updated PROJECT_STATE.md, ROADMAP.md, DECISIONS.md (D-024 merged/accepted; D-025 proposed correction), HANDOVER_CURRENT.md, AGENTS.md, MANIFEST.md, README.md and the prior audit's follow-up pointer. Older dated evidence is explicitly superseded, not deleted. One current next action replaces obsolete PR #64 review and direct-Dental instructions.

ADR-002 now states **implemented on main, comparative acceptance criterion not yet evidenced**. Merged integration is proven; the original comparative failure-reduction requirement is not inferred from green regressions.

## Open PR hygiene

Read-only GitHub inventory on 2026-10-08: **16 pre-existing open PRs**. Recommendations below are not closure authorization. No old PR was closed, merged, rebased or force-updated.

| PR | Recommendation | Reason |
|---|---|---|
| [#4](https://github.com/pierluigiavvanzo-creator/forgelab/pull/4) | NEEDS PRODUCT OWNER DECISION | Historical dashboard guide: retain only useful instructions after reconciling current launcher/lifecycle. |
| [#21](https://github.com/pierluigiavvanzo-creator/forgelab/pull/21) | NEEDS PRODUCT OWNER DECISION | Commercial strategy choice; technical stabilization provides no new paying-ICP evidence. |
| [#35](https://github.com/pierluigiavvanzo-creator/forgelab/pull/35) | FROZEN | Old repeat-limit sampler proposal; do not change provider/retry behavior without new evidence. |
| [#36](https://github.com/pierluigiavvanzo-creator/forgelab/pull/36) | SUPERSEDED / CANDIDATE TO CLOSE | Already marked SUPERSEDED; pre-reset documentation would reintroduce stale state. |
| [#37](https://github.com/pierluigiavvanzo-creator/forgelab/pull/37) | FROZEN | Custom failure-envelope stack; retain for reference, not wholesale integration into Aider path. |
| [#38](https://github.com/pierluigiavvanzo-creator/forgelab/pull/38) | FROZEN | Legacy custom pre-write schema recovery; current Aider correction is centralized. |
| [#39](https://github.com/pierluigiavvanzo-creator/forgelab/pull/39) | SUPERSEDED / CANDIDATE TO CLOSE | Current API already normalizes the supported py -3.11 test command to its interpreter; avoid widening the executable allowlist. |
| [#40](https://github.com/pierluigiavvanzo-creator/forgelab/pull/40) | FROZEN | Old retry-profile/grammar relaxation; no new proof justifies importing it. |
| [#41](https://github.com/pierluigiavvanzo-creator/forgelab/pull/41) | FROZEN | Custom semantic test-correction schema in frozen stack; reconcile only if a new blocker requires it. |
| [#42](https://github.com/pierluigiavvanzo-creator/forgelab/pull/42) | SUPERSEDED / CANDIDATE TO CLOSE | Already marked SUPERSEDED; current handover and this audit replace its checkpoint. |
| [#43](https://github.com/pierluigiavvanzo-creator/forgelab/pull/43) | FROZEN | Changes semantic correction eligibility after test repair; preserve current bounded budgets. |
| [#44](https://github.com/pierluigiavvanzo-creator/forgelab/pull/44) | FROZEN | Source-based f-string recovery is part of superseded custom editor chain. |
| [#45](https://github.com/pierluigiavvanzo-creator/forgelab/pull/45) | FROZEN | Potentially reusable compile validation, but stacked candidate must not be merged wholesale; requires a separately proven blocker. |
| [#46](https://github.com/pierluigiavvanzo-creator/forgelab/pull/46) | FROZEN | Combines custom semantic schema and f-string restoration from frozen stack. |
| [#47](https://github.com/pierluigiavvanzo-creator/forgelab/pull/47) | FROZEN | F-string quote normalization belongs to frozen custom recovery architecture. |
| [#48](https://github.com/pierluigiavvanzo-creator/forgelab/pull/48) | FROZEN | Unterminated-string restoration belongs to frozen custom recovery architecture. |

## Residual risks

- Main still contains the reproduced lifecycle defects until the single correction is explicitly reviewed and merged.
- Windows readiness was tested on isolated ports; normal 5173 remains occupied. Browser launch and visual product acceptance were not part of the executed launcher segment.
- Python 3.14 exposes two interpreter-dependent test fixtures; launcher Python 3.11.9 is the validated runtime.
- Proxy egress control is best-effort; transitive dependencies are fingerprinted, not fully reproducible from a committed lock.
- No remote CI. Two dashboard exhaustive-deps warnings remain.
- One-active-run exclusion is per API process, suitable for the existing single local server; multi-process ownership is not provided.
- Human-requested repairs keep their existing synchronous response/refresh limitations; no claim extends top-level async recovery to them.
- orchestrator.py and page.tsx remain concentration risks; no speculative decomposition was undertaken.
- Dental Golden Path and commercial C1–C3 evidence remain outstanding.

## Single next action

**Review the single PR from `fix/post-pr64-run-lifecycle-stabilization`.** Do not run Dental on current canonical main. No recommendation for a new Dental run is issued in this report; that requires integrated stabilization PASS first.

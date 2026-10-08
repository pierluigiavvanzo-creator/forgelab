# ForgeLab — Aider Integration Stabilization Audit

**Date:** 2026-10-07  
**Classification:** A — Product Critical  
**Scope:** reusable editor boundary + Aider runtime contract + API/dashboard lifecycle required to operate long local-editor runs  
**Baseline main:** `59aa35b15a86bd527cc1fc75df5863673ed8b811` (merge PR #63)  
**Candidate branch:** `mvp1-aider-integration-stabilization-gate`  
**Golden Path:** Dental Quote #1  
**Commercial evidence level:** C0 — product capability validation, not market validation

## Follow-up — 2026-10-08

PR #64 is merged. This document preserves the pre-merge audit, not current validation status. Actual Windows execution and demonstrated post-merge lifecycle defects are recorded in [the follow-up audit](FORGELAB_POST_PR64_VERIFICATION_2026-10-08.md). Its current decision supersedes the historical next-action text below.

## 1. Decision

The sequence PR #60–#63 showed that ForgeLab was using the real Dental Golden Path to discover integration-edge failures that should have been covered inside the reusable-editor component.

This audit therefore changes the validation method:

```text
OLD
Dental real run
  -> discover one editor/integration edge
  -> smallest repair
  -> another Dental run

NEW
Aider component audit
  -> bounded failure taxonomy
  -> focused regression matrix
  -> launcher-enforced stabilization gate
  -> exactly one unchanged Dental validation run
```

No further Dental run is authorized until the focused stabilization gate passes on the local Windows runtime.

## 2. Real evidence that triggered this audit

The following failures are real product-run evidence, not hypothetical cases.

### PR #60 / run `run-a949ce0afbb9`

Failure class:

`CROSS_PHASE_TIMEOUT_COUPLING`

Observed:

- generic test/provider timeout and Aider subprocess timeout shared the same 60-second budget;
- initial pre-write correction terminated with `exit=124`, `timed_out=True`.

Remediation already merged:

- generic/test/provider timeout: default 60 seconds;
- reusable editor timeout: default 300 seconds, bounded 60..600.

### Post-PR60 submission

Failure class:

`EDITOR_RESULT_LIFECYCLE_ERROR`

Observed:

`UnboundLocalError: cannot access local variable 'editor_result' where it is not associated with a value`

Root cause:

Aider process/sandbox errors were classified as candidate-format errors, and recovery attempted to use a candidate that did not exist.

Remediation already merged in PR #61:

- distinct `AIEditorExecutionError`;
- governed `EditorFailure.json`;
- no false candidate correction when no `EditorResult` exists.

### PR #61 / run `run-0a7fb9e16cf5`

Failure class:

`TOOL_HOME_AND_PRODUCT_WORKSPACE_COLLISION`

Observed tool-owned files incorrectly classified as target scope expansion:

- `.aider/analytics.json`;
- `.aider/caches/model_prices_and_context_window.json`;
- `.aider/installs.json`.

Remediation already merged in PR #62:

```text
temporary sandbox/
├── workspace/     # target/read-only files only
└── tool-home/     # HOME, USERPROFILE, Aider state/config
```

The workspace scanner remains strict.

### PR #62 / run `run-f564070471df`

Failure class:

`CWD_RELATIVE_AIDER_HISTORY_FILE`

Observed:

`.aider.chat.history.md`

Aider's history path is independently configurable and was still defaulting to the current working directory.

Remediation already merged in PR #63:

- `--chat-history-file <tool-home>/.aider.chat.history.md`;
- `--input-history-file <tool-home>/.aider.input.history`.

## 3. External reusable-component audit

ForgeLab pins:

`aider-chat==0.86.2`

The stabilization work was checked against the Aider 0.86.2 CLI/source contract rather than assuming current-version behavior.

Primary external references:

1. Aider v0.86.2 argument definitions  
   https://raw.githubusercontent.com/Aider-AI/aider/v0.86.2/aider/args.py

2. Aider v0.86.2 model-information implementation  
   https://raw.githubusercontent.com/Aider-AI/aider/v0.86.2/aider/models.py

3. Aider configuration/options reference  
   https://aider.chat/docs/config/options.html

4. Aider Ollama integration reference  
   https://aider.chat/docs/llms/ollama.html

Relevant verified integration points include:

- explicit model metadata file;
- model/API timeout;
- repo-map token budget;
- chat/input history locations;
- Git/Gitignore controls;
- auto-test/auto-lint controls;
- file watching;
- prompt cache/history restore;
- notifications/URL detection;
- model warning/settings checks;
- update checks;
- analytics disablement;
- local Ollama model addressing.

The Aider model-information implementation also contains a remote model-metadata refresh path. ForgeLab therefore does not rely on `--no-check-update` as a complete network boundary.

## 4. Hardening implemented in this stabilization candidate

### 4.1 One reusable-editor execution boundary

Before this candidate, the orchestrator repeated Aider process/error handling in four paths:

1. initial implementation;
2. initial pre-write correction;
3. deterministic-test repair;
4. semantic-review repair.

The candidate centralizes these calls in:

`_run_aider_editor(...)`

All four phases now share:

- executable resolution;
- adapter invocation;
- editor timeout contract;
- `EditorAdapterError -> AIEditorExecutionError`;
- non-zero exit handling;
- timeout handling;
- bounded stdout/stderr failure evidence;
- phase attribution.

This removes future drift between repair paths.

### 4.2 Deterministic Aider CLI profile

The candidate explicitly configures the local editor instead of relying on Aider defaults.

Key controls include:

- `--model ollama_chat/...`;
- `--timeout <editor timeout>`;
- `--map-tokens 0`;
- `--no-git`;
- `--no-gitignore`;
- `--no-add-gitignore-files`;
- `--no-auto-commits`;
- `--no-dirty-commits`;
- `--no-auto-lint`;
- `--no-auto-test`;
- `--no-watch-files`;
- `--no-cache-prompts`;
- `--no-restore-chat-history`;
- `--no-suggest-shell-commands`;
- `--no-notifications`;
- `--no-detect-urls`;
- `--no-pretty`;
- `--no-stream`;
- `--no-show-model-warnings`;
- `--no-check-model-accepts-settings`;
- `--analytics-disable`;
- `--no-check-update`;
- `--no-show-release-notes`;
- explicit config/env/model-metadata/message/history files under `tool-home`.

Repo-map is disabled because ForgeLab already exposes at most 1–3 authorized writable files plus governed context. In this boundary it adds integration surface without product value.

### 4.3 Local model metadata

ForgeLab writes a run-local Aider model metadata file inside `tool-home` identifying the selected `ollama_chat` model as a chat model.

It deliberately does **not** invent token limits, prices or model capabilities that ForgeLab has not measured.

### 4.4 Environment isolation

The previous deny-list approach was rejected during self-review because an unknown credential name could escape the list.

The candidate now uses a minimal safe inherited-environment allow-list.

Aider receives only necessary process/runtime variables plus explicit ForgeLab values:

- isolated `HOME`;
- isolated `USERPROFILE`;
- analytics disabled;
- explicit loopback Ollama endpoint;
- explicit proxy/NO_PROXY policy.

Credentials such as ForgeLab API token, GitHub tokens, cloud credentials, database URLs, Python virtual-environment overrides and arbitrary process secrets are not inherited.

### 4.5 Loopback-only local model endpoint

`FORGELAB_OLLAMA_URL` is validated before Aider launch.

Allowed hosts:

- `127.0.0.1`;
- `localhost`;
- `::1`.

Embedded URL credentials are rejected.

### 4.6 Best-effort Aider subprocess egress guard

The Aider subprocess environment is configured with:

- HTTP/HTTPS/ALL proxy directed to an intentionally unavailable loopback endpoint;
- `NO_PROXY` limited to loopback hosts.

Purpose:

- preserve Ollama loopback access;
- fail ordinary proxy-aware external HTTP attempts.

Important limitation:

This is **not an OS firewall or kernel network sandbox**. A dependency that deliberately ignores proxy environment variables could still attempt external network access. This remains a residual risk and is recorded as such rather than being represented as absolute network isolation.

### 4.7 Filesystem failure normalization

The adapter now governs additional predictable failures:

- authorized file deleted inside sandbox;
- non-UTF-8 authorized text;
- generic subprocess OS launch error;
- timeout output returned as bytes;
- invalid editor timeout;
- aliasing multiple authorized paths to the same resolved source file.

These become deterministic ForgeLab errors rather than escaping as unrelated Python exceptions.

## 5. Runtime evidence contract

For Aider runs, candidate evidence records:

- editor timeout;
- editor engine;
- integration contract version;
- tool-state policy;
- local model metadata policy;
- minimal environment policy;
- loopback network scope;
- external-network policy;
- subprocess egress-guard type;
- reusable editor call count;
- zero ChatGPT assistance in target-product run.

`SecurityReport.json` now distinguishes local loopback network use from external-network permission instead of reporting all network activity as absent.

## 6. Long-run lifecycle stabilization

Aider can legitimately use materially longer bounded execution windows than deterministic tests.

The pre-candidate API performed:

`POST /v1/runs -> entire pipeline -> response`

Therefore the dashboard could not know the run id or distinguish processing from a hung request.

The candidate changes the lifecycle to:

```text
POST /v1/runs
   -> 202 Accepted + run_id
   -> QUEUED
   -> RUNNING
   -> GET /v1/runs/{run_id}/status polling
   -> READY_FOR_DECISION | CLOSED | FAILED | INTERRUPTED
   -> load final artifacts
```

Boundedness:

- only one top-level run may be active at once;
- concurrent submission returns HTTP 409;
- `RunStatus.json` is written atomically;
- browser refresh reconnects to an active run and resumes polling;
- API restart converts an unfinished persisted run to `INTERRUPTED`;
- if a terminal `RunSummary.json` already exists, that summary takes precedence over a stale transient status.

No uncontrolled parallel agent execution is introduced.

## 7. Reproducibility / launcher preflight

The launcher still pins:

`aider-chat==0.86.2`

It now additionally verifies before starting the product runtime:

1. Aider reports the expected version;
2. every CLI flag required by ForgeLab's integration contract exists;
3. `pip check` passes in the isolated Aider virtual environment;
4. `pip freeze` is captured to `.forgelab/runtime/aider-freeze.txt`;
5. a SHA-256 fingerprint of that dependency snapshot is stored in runtime metadata;
6. the focused Aider stabilization test set passes.

Focused launcher gate:

- `test_editor_adapter.py`;
- `test_orchestrator.py`;
- `test_api.py`;
- `test_dashboard_run_form_feedback.py`.

If any gate fails, ForgeLab startup stops before Dental is used as a target-product test.

Residual reproducibility risk:

Only the top-level Aider package is pinned today; transitive versions are fingerprinted, not fully locked by a committed lockfile. The fingerprint makes drift visible without silently introducing an unverified dependency lock in this stabilization PR.

## 8. Failure matrix

| Class | Expected contract | Coverage state |
|---|---|---|
| Aider executable missing | governed editor failure | covered |
| Aider OS execution denied/error | governed editor failure | added |
| CLI contract drift | launcher blocks startup | added |
| dependency incompatibility | `pip check` blocks startup | added |
| transitive dependency drift | runtime fingerprint changes | added |
| external Ollama URL | rejected before launch | added |
| inherited credentials | not passed to Aider | strengthened |
| Aider HOME metadata | isolated in `tool-home` | covered |
| chat history | routed to `tool-home` | covered |
| input history | routed to `tool-home` | covered |
| model metadata | local explicit file | added |
| repo-map | disabled | added |
| unauthorized normal file | blocked | covered |
| unauthorized hidden file | blocked | covered |
| read-only mutation | blocked | covered |
| authorized file deletion | governed error | added |
| non-UTF-8 authorized target | governed error | added |
| invalid editor timeout | rejected | added |
| subprocess timeout | exit 124 + evidence | strengthened |
| non-zero Aider exit | governed + stdout/stderr | covered/centralized |
| no-op candidate | bounded candidate recovery | existing |
| invalid Python candidate | one bounded pre-write correction | existing |
| failed deterministic test | one bounded repair | existing |
| invalid failed-test repair | governed stop/correction contract | existing |
| semantic review fail | bounded semantic repair | existing |
| semantic repair failure | governed stop | existing |
| all gates pass | `READY_FOR_DECISION` | existing integration test |
| concurrent new run | HTTP 409 | added |
| long run | immediate 202 + status polling | added |
| browser refresh during run | resume polling | added |
| API restart during run | durable `INTERRUPTED` or terminal summary | added |
| source repository before approval | unchanged | existing |
| paid provider use | prohibited / EUR 0 path | existing |

"Coverage state" means regression/preflight coverage exists in the candidate. It does **not** mean the candidate has already passed on the user's current Windows runtime.

## 9. What this PR intentionally does not do

This stabilization candidate does not:

- add Dental-specific implementation logic;
- increase the top-level repair cap;
- add retries to hide failures;
- introduce a paid provider;
- expand writable scope;
- allow Aider Git operations;
- let Aider run its own tests or lint;
- auto-promote a target candidate;
- merge or push target-product code automatically;
- claim absolute OS-level network isolation;
- silently pin unverified transitive dependency versions.

## 10. Validation truth at PR creation

There is currently no GitHub Actions workflow attached to this repository state.

Therefore:

- no remote CI PASS is claimed;
- no local Windows PASS is claimed before the user synchronizes the candidate;
- regression code and launcher preflight are present;
- the first post-merge launcher execution is the required environment-specific stabilization gate.

This distinction is mandatory: code coverage added is not the same thing as executed evidence.

## 11. Exit gate

The next real Dental run is allowed only after all of the following occur:

1. this single stabilization PR is reviewed and merged;
2. local ForgeLab is synchronized to the new canonical main;
3. `Start-ForgeLab.ps1` completes;
4. launcher reports `[PASS] Aider stabilization gate`;
5. dashboard/API readiness and stability window pass;
6. active runtime SHA matches the merged stabilization SHA.

Then perform exactly one unchanged Dental Quote run from the dashboard.

### PASS path

```text
launcher stabilization PASS
  -> one Dental run
  -> Aider
  -> pre-write
  -> deterministic tests
  -> bounded repair if needed
  -> Reviewer
  -> Security
  -> READY_FOR_DECISION
  -> Product Owner approval
  -> local promotion
  -> visible usability check
```

### FAIL path

If the focused launcher gate fails, do not run Dental.

If the launcher gate passes but Dental still closes, the new blocker must be treated as evidence against the product/integration behavior, not as an invitation to return automatically to a one-PR-per-symptom loop.

## 12. Strategic value

Expected product/economic contribution:

- reduces Product Owner debugging time;
- moves predictable integration failures into automated preflight;
- protects the Golden Path from tool-internal state;
- improves trust in zero-spend local execution;
- makes long-running work observable instead of appearing frozen;
- lowers the cost of reusing Aider in future ForgeLab-generated products;
- creates a reusable stabilized editor boundary rather than Dental-specific repair logic.

This is a product-enabling milestone, not infrastructure for its own sake.

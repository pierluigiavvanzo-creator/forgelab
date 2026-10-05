# ForgeLab MVP Recovery Architecture Audit — 2026-10-05

## Executive decision

ForgeLab has accumulated meaningful governance, isolation, review and evidence capabilities, but the recent Dental Quote cycle shows a product-process regression:

- Product Owner effort has increased instead of decreased;
- the dashboard has been bypassed by repeated PowerShell/CLI runs;
- the local Developer path is unstable under `qwen2.5-coder:7b`;
- custom recovery logic has expanded rapidly inside `orchestrator.py`;
- the active runtime truth is spread across a long stacked PR chain instead of canonical `main`;
- the current work risks overfitting to one Golden Path application.

Decision:

1. FREEZE runtime PRs #37–#48. Do not merge or extend them while this reset is active.
2. STOP asking the Product Owner to run repetitive PowerShell validation loops.
3. KEEP ForgeLab as the control plane.
4. KEEP dashboard, API, state machine, isolated workspace, ToolGateway, tests, independent Reviewer, Security, evidence, usage metering and human promotion gate.
5. REFACTOR the Developer editing boundary.
6. BENCHMARK a reusable code-editing engine before more custom recovery logic.
7. ADOPT Aider only as the first bounded editor-engine experiment, not as a replacement for ForgeLab.
8. REJECT Continue for the current MVP path because its own current README states that the repository is no longer actively maintained.
9. DEFER OpenHands SDK and Cline as broader agent-runtime replacements because they overlap with ForgeLab's already-built control-plane responsibilities.
10. Return Golden Path validation to the dashboard after the editor adapter experiment.

No runtime code is changed by this audit.

---

## 1. Baseline product contract

The original ForgeLab product contract requires:

- Product Owner = approver/final usability tester, not routine debugger;
- bounded autonomous implementation/diagnosis/repair;
- dashboard-visible plan, changes, tests, risk, model usage and decision;
- Product Owner completes ordinary runs without terminal use;
- deterministic verification outside the model;
- repository-first evaluation before substantial custom implementation;
- human-gated promotion.

Primary metric:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / PRODUCT OWNER TIME`

Near-term product KPI:

`USER_TIME_SAVED_PER_SUCCESSFUL_RUN`

Therefore repeated manual PowerShell execution by the Product Owner is itself a product failure signal.

---

## 2. What has genuinely improved

### KEEP — governance and safe failure

Recent real runs show that ForgeLab increasingly fails in a governed way instead of crashing or contaminating the source repository.

Validated strengths:

- isolated execution;
- allowed-path enforcement;
- bounded repair attempts;
- deterministic test execution;
- independent semantic review;
- security review;
- usage/cost evidence;
- terminal failure artifacts;
- source repository remaining clean after failed runs;
- explicit human promotion gate.

This work is reusable and should be preserved.

### KEEP — independent semantic review

The Reviewer repeatedly blocked candidates whose deterministic tests passed but whose user-visible behavior still failed the Product Owner objective.

That is an important product differentiator and should remain independent from the Developer implementation mechanism.

### KEEP — dashboard/API capability

The dashboard already calls the real API:

- create run;
- load run artifacts;
- request repair;
- submit decisions;
- execute promotion through the API.

The dashboard is not the main technical blocker. The recent development process bypassed it because candidate runtime code lived on unmerged PR heads.

---

## 3. Where the process regressed

### 3.1 Product Owner became the test harness

The Product Owner has repeatedly been asked to:

- checkout exact candidate SHAs;
- run validation harnesses;
- launch unchanged Golden Path reruns;
- collect result bundles;
- upload result bundles to ChatGPT.

This violates the Product Owner contract and increases `user touches / run`.

### 3.2 Stacked PR chain became the practical source of truth

Canonical `main` is currently at:

`5f83844a36063722c2979dae19576d57c0f06c5a`

while runtime experiments continue through PR #48.

Open stack at audit time:

- #37 unexpected run failure envelope;
- #38 prewrite single schema;
- #39 Windows `py` test runner;
- #40 Ollama repeat-limit recovery profile;
- #41 semantic test-correction schema;
- #43 post-test-repair semantic correction;
- #44 deterministic f-string source stabilization;
- #45 Python compile pre-write gate;
- #46 semantic repair schema + f-string stabilization;
- #47 f-string subscript normalization;
- #48 unterminated source-string stabilization.

This is too much unresolved runtime behavior to keep stacking safely.

### 3.3 Orchestrator concentration

From the PR #34 merged baseline to PR #48 candidate:

- `src/forgelab/orchestrator.py`: +672 / -75 lines;
- `tests/test_orchestrator.py`: +1674 / -618 lines;
- 33 commits ahead of the PR #34 merge baseline.

Current line counts:

- `orchestrator.py` on main: about 5,345 lines;
- PR #48 candidate: about 5,942 lines;
- `test_orchestrator.py` on main: about 4,439 lines;
- PR #48 candidate: about 5,495 lines.

The Developer/edit/recovery logic is becoming a monolithic exception catalogue.

### 3.4 Recovery-overfitting pattern

Observed custom recovery classes include:

- invalid exact `old_text` reference;
- snippet-to-full-file recovery;
- structured schema fallback;
- provider repeat-limit handling;
- semantic repair schema fallback;
- Python f-string restoration;
- Python compile validation;
- dictionary-subscript quote normalization;
- unterminated normal-string restoration.

Each individual fix is defensible, but the sequence indicates the wrong abstraction boundary.

Root diagnosis:

`CUSTOM_LLM_EDIT_PROTOCOL_IS_BECOMING_THE_PRODUCT_BOTTLENECK`

---

## 4. Local model diagnosis

Current zero-cost Developer path uses:

`Ollama + qwen2.5-coder:7b`

Real-run evidence shows repeated failures in:

- exact source referencing;
- structured patch contracts;
- complete-file regeneration;
- quoting/f-string syntax;
- repeat-limit behavior;
- preserving unchanged UI code.

This does not mean the model is useless. It means the current contract asks too much of it at once:

`reason about requirements + choose edits + serialize strict JSON + reproduce complete files correctly`

The architecture should reduce the model's responsibility before increasing model cost.

Hardware constraint from the existing ForgeLab workstation also limits easy escalation to the large local models now recommended by some agent frameworks. Therefore the next move should be editor-engine reuse, not simply “use a much larger model”.

---

## 5. REUSE-FIRST benchmark

### Evaluation criteria

Candidates were compared on:

1. commercial-compatible license;
2. active maintenance;
3. local/Ollama support;
4. bounded/headless operation;
5. mature code-edit handling;
6. ability to preserve ForgeLab governance;
7. integration cost into the Python control plane;
8. overlap with existing ForgeLab responsibilities.

### 5.1 Aider

Repository: `Aider-AI/aider`  
License: Apache-2.0  
Language: Python  
Local models: Ollama supported  
Scripting: CLI and Python available  
Edit formats: whole, diff, diff-fenced, udiff, editor-diff, editor-whole  
Architect/editor separation: supported  
Git auto-commit: can be disabled

Strengths:

- narrow fit to the actual weak point: code editing;
- mature edit-format handling;
- supports local Ollama;
- can operate on explicit file lists;
- CLI is scriptable for one-shot tasks;
- auto commits can be disabled;
- Python implementation reduces integration friction.

Important caveat:

Aider's own documentation says its Python scripting API is not officially supported for backwards compatibility.

Decision:

`BENCHMARKED -> ADOPTED FOR BOUNDED EXPERIMENT`

Integration preference:

Use the CLI as the initial adapter boundary, not the unsupported Python API.

### 5.2 OpenHands Software Agent SDK

Repository: `OpenHands/software-agent-sdk`  
License: MIT  
Language: Python  
Current activity: active  
Interfaces: Python, TypeScript, REST  
Capabilities: agents, tools, workspaces, terminal, file editor, server  
Local LLMs: supported, including Ollama

Strengths:

- production-oriented agent SDK;
- strong workspace/tool abstraction;
- local or ephemeral execution;
- programmatic API;
- active project.

Weakness for current need:

It duplicates large parts of ForgeLab:

- agent runtime;
- workspaces;
- tools;
- conversation lifecycle;
- server/client infrastructure.

Decision:

`BENCHMARKED -> REJECTED FOR CURRENT EDITOR-SWAP MVP`

Revisit only if ForgeLab later decides to replace its broader agent runtime.

### 5.3 Cline

Repository: `cline/cline`  
License: Apache-2.0  
Language: TypeScript  
Current activity: active  
Interfaces: SDK, CLI, desktop, IDE  
Headless operation: supported  
Local models: Ollama / LM Studio supported

Strengths:

- mature coding-agent behavior;
- headless JSON/automation path;
- SDK available;
- checkpoints/diffs;
- local models supported.

Weakness for current need:

- Node/TypeScript integration boundary into a Python control plane;
- broad overlap with planning/agent/tool lifecycle;
- larger adoption surface than a narrow editor replacement.

Decision:

`BENCHMARKED -> REJECTED FOR CURRENT EDITOR-SWAP MVP`

Keep as a future full-agent-runtime benchmark candidate.

### 5.4 Continue

Repository: `continuedev/continue`  
License: Apache-2.0  
Language: TypeScript

Current README explicitly states that the repository is no longer actively maintained and that 2.0.0 is the final release.

Decision:

`BENCHMARKED -> REJECTED`

Reason: maintenance risk for a new core dependency.

---

## 6. Recommended target architecture

ForgeLab remains the product and control plane.

```text
DASHBOARD
   |
   v
LOCAL API
   |
   v
FORGELAB ORCHESTRATOR
   |
   +--> Planner / acceptance contract
   |
   +--> EditorAdapter
          |
          +--> AiderCliAdapter  [experiment]
          |
          v
      EDITOR SANDBOX
      - only authorized writable files
      - bounded read-only context
      - no direct protected repo write
      - no auto commit
   |
   v
VALIDATED EDIT RESULT
   |
   +--> scope validation
   +--> compile/lint
   +--> deterministic tests
   |
   v
TOOLGATEWAY APPLY TO ISOLATED WORKSPACE
   |
   v
TEST -> REVIEW -> SECURITY -> READY_FOR_DECISION
   |
   v
DASHBOARD HUMAN GATE
```

Critical governance rule:

The external editor must not become the authority for repository writes.

The editor sandbox produces candidate file content. ForgeLab validates it, computes the authorized change set, and the existing ToolGateway remains responsible for applying the validated change to the governed isolated workspace.

---

## 7. KEEP / REFACTOR / REPLACE / FREEZE

| Area | Decision | Reason |
|---|---|---|
| Dashboard | KEEP | Already connected to real API and required by product contract |
| API | KEEP | Correct control-plane boundary |
| State machine | KEEP | Valuable governed lifecycle |
| Isolated workspace | KEEP | Proven safety value |
| ToolGateway | KEEP | Must remain authoritative write boundary |
| Test runner | KEEP | Deterministic external evidence |
| Reviewer | KEEP | Repeatedly caught semantic incompleteness |
| Security review | KEEP | Required promotion gate |
| Usage ledger | KEEP | Zero-cost and future budget governance |
| Planner acceptance contract | KEEP | Correctly improved requirement propagation |
| `orchestrator.py` monolith | REFACTOR | Too many responsibilities and recovery branches |
| Custom JSON edit protocol | REPLACE/REDUCE | Main instability source |
| String/f-string special-case recovery | FREEZE | Do not add more cases pending editor benchmark |
| PR #37–#48 runtime stack | FREEZE | Too much unresolved stacked behavior |
| PR #36 docs sync | SUPERSEDE | State is obsolete |
| PR #42 old handover consolidation | SUPERSEDE | New reset handover becomes authoritative candidate |
| PowerShell Product Owner loop | STOP | Violates MVP usability/autonomy contract |

---

## 8. Minimum experiment before any further runtime build

Experiment name:

`EDITOR_ENGINE_BAKEOFF_01`

Input:

Same Dental Quote baseline and exact same Product Owner objective.

Candidates:

A. current custom ForgeLab editor from merged `main`;  
B. Aider CLI adapter in editor sandbox using the same local Ollama model.

No change to:

- Planner;
- test command;
- Reviewer;
- Security;
- human gate;
- repair cap;
- Product Owner objective.

Measure:

- candidate generated successfully;
- compile-valid before tests;
- deterministic test result;
- semantic review result;
- number of model calls;
- number of repair attempts;
- wall-clock time;
- Product Owner touches;
- unauthorized path changes;
- malformed edit events;
- final usable-output status.

Acceptance rule for Aider adapter:

Adopt only if it materially reduces malformed-edit/recovery failures without weakening ForgeLab governance.

Do not require Dental Quote final PASS on the first adapter experiment; first prove that the edit boundary is more reliable.

---

## 9. Model policy during the bakeoff

Phase 1:

Use the existing `qwen2.5-coder:7b` for both editor candidates so the experiment isolates the editing engine.

Phase 2 only if both editors fail materially:

Benchmark one stronger local model that fits the actual workstation constraints.

Do not introduce a paid API simply to rescue the MVP without explicit Product Owner approval.

---

## 10. PR consolidation strategy

Do not merge PR #37–#48 one by one.

After the editor bakeoff:

1. identify which runtime behaviors remain generally necessary;
2. recreate only those behaviors on a fresh branch from canonical `main`;
3. split responsibilities out of `orchestrator.py`;
4. close/supersede obsolete stacked PRs;
5. run the dashboard Golden Path against the consolidated candidate;
6. require decision-ready evidence before merge.

The expected consolidated code shape should introduce explicit modules such as:

- `editor_adapter.py`;
- `prewrite_validation.py`;
- `repair_policy.py`;

instead of adding additional special cases directly to `orchestrator.py`.

---

## 11. Dashboard-first recovery gate

The MVP recovery is not complete until the Product Owner journey is again:

1. run `Start-ForgeLab.ps1` once to start local services;
2. open dashboard;
3. enter/select project and objective;
4. click Run;
5. ForgeLab performs implementation/test/review autonomously;
6. dashboard displays decision-ready result;
7. Product Owner chooses Approve / Reject / Repair.

PowerShell may remain:

- installation/bootstrap;
- service startup;
- exceptional developer diagnostics.

It must not remain the repeated Product Owner execution interface.

---

## 12. Current verdict

ForgeLab should continue.

The project is not failing because the control-plane concept is wrong.

The project is stalled because the Developer editing boundary is too fragile and the debugging method transferred too much work to the Product Owner.

Next action:

`IMPLEMENT_EDITOR_ADAPTER_BAKEOFF_HARNESS_WITHOUT_CHANGING_GOLDEN_PATH_BEHAVIOR`

Owner:

ForgeLab development process, not Product Owner manual QA.

No further Dental Quote PowerShell rerun should be requested until this architecture-reset gate is completed.

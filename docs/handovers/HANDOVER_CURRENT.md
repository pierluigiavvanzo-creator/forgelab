# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-10-05  
**Checkpoint:** EditorAdapter bakeoff harness ready  
**Status:** PRE-MVP / PR #50 OPEN / HUMAN MERGE GATE

## 1. Strategic decision

ForgeLab remains the product.

It is a governed multi-agent software-development control plane, not a coding CLI and not a collection of prompts.

Canonical product workflow:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED REPAIR -> REVIEW -> SECURITY -> READY_FOR_DECISION -> HUMAN APPROVAL -> PROMOTION`

Primary metric:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / PRODUCT OWNER TIME`

Product Owner contract:

- strategic decision maker;
- merge/promotion approver;
- final usability tester;
- not routine debugger;
- not repetitive QA;
- not log transporter;
- not retry orchestrator;
- not operator of repeated PowerShell validation loops.

No Work or Codex is required for this project workflow.

---

## 2. Canonical repository

Repository:

`pierluigiavvanzo-creator/forgelab`

Canonical branch:

`main`

Canonical main HEAD at this checkpoint:

`8b67b98c61d6bd90af839d1cad185f05454a2e66`

This is the merge of PR #49 architecture reset.

The long runtime experiment chain after PR #34 is **not canonical**.

---

## 3. Why the process was reset

Recent Dental Quote work improved safe failure handling but did not improve the primary product metric enough.

Observed process regression:

- repeated Product Owner PowerShell reruns;
- dashboard bypassed during candidate validation;
- many stacked runtime PRs;
- repeated malformed custom LLM edit outputs;
- increasing recovery special cases inside `orchestrator.py`;
- practical source of truth drifting from `main` to stacked branches;
- risk of overfitting to Dental Quote.

Architecture audit:

`docs/audits/FORGELAB_MVP_RECOVERY_ARCHITECTURE_AUDIT_2026-10-05.md`

ADR candidate:

`docs/decisions/ADR-002-editor-adapter-boundary.md`

Root diagnosis:

`CUSTOM_LLM_EDIT_PROTOCOL_IS_BECOMING_THE_PRODUCT_BOTTLENECK`

---

## 4. What is preserved

KEEP:

- dashboard;
- local authenticated API;
- Planner acceptance contract;
- agent role contracts;
- state machine;
- isolated workspace;
- ToolGateway;
- deterministic test runner;
- independent semantic Reviewer;
- Security review;
- evidence/artifact store;
- usage/cost ledger;
- bounded repair policy;
- explicit human promotion gate.

These components are not the primary current blocker.

---

## 5. What is frozen

Runtime PRs:

- #37
- #38
- #39
- #40
- #41
- #43
- #44
- #45
- #46
- #47
- #48

Decision:

`FREEZE / DO NOT MERGE / DO NOT EXTEND`

until the editor bakeoff is complete.

Documentation PRs #36 and #42 are superseded by the architecture-reset documentation candidate.

Do not merge the stacked runtime chain one-by-one.

---

## 6. Evidence behind the reset

From the PR #34 merged baseline to the PR #48 experiment:

- 33 commits ahead;
- `orchestrator.py`: +672 / -75 lines;
- `test_orchestrator.py`: +1674 / -618 lines.

Approximate file sizes at audit:

- main `orchestrator.py`: 5,345 lines;
- PR #48 `orchestrator.py`: 5,942 lines;
- main `test_orchestrator.py`: 4,439 lines;
- PR #48 `test_orchestrator.py`: 5,495 lines.

Repeated real failure categories:

- exact `old_text` mismatch;
- schema mismatch;
- full-file recovery failure;
- Ollama repeat limit;
- semantic repair schema loss;
- malformed f-string;
- compile-only Python syntax error;
- escaped subscript quote error;
- unterminated normal string.

This is evidence that the LLM editing boundary needs replacement/refactoring rather than more special-case recovery.

---

## 7. REUSE-FIRST benchmark result

### Aider

Status:

`BENCHMARKED -> ADOPTED FOR BOUNDED EXPERIMENT`

Use only as an editor-engine candidate.

Reasons:

- Apache-2.0;
- Python;
- local Ollama support;
- mature edit formats;
- one-shot scripting;
- explicit file scope;
- auto commits can be disabled.

Integration boundary:

Prefer CLI for the experiment because Aider documents its Python API as not officially stable.

### OpenHands Software Agent SDK

Status:

`BENCHMARKED -> REJECTED FOR CURRENT NARROW EDITOR SWAP`

Reason:

Strong and active, but duplicates agent runtime, workspaces, tools, server/client and other control-plane responsibilities already present in ForgeLab.

Revisit only for a broader runtime replacement.

### Cline

Status:

`BENCHMARKED -> REJECTED FOR CURRENT NARROW EDITOR SWAP`

Reason:

Strong active SDK/CLI and local-model support, but larger TypeScript/Node integration surface and substantial overlap with existing ForgeLab agent/tool lifecycle.

### Continue

Status:

`BENCHMARKED -> REJECTED`

Reason:

Current README states that the repository is no longer actively maintained.

---

## 8. Target editor architecture

```text
Dashboard
  -> Local API
  -> ForgeLab Orchestrator
  -> Planner / Acceptance Contract
  -> EditorAdapter
       -> AiderCliAdapter [experiment]
       -> restricted editor sandbox
  -> candidate file set
  -> deterministic scope + compile/lint validation
  -> ToolGateway apply to isolated workspace
  -> tests
  -> independent Reviewer
  -> Security
  -> READY_FOR_DECISION
  -> Dashboard human gate
```

ToolGateway remains the authoritative apply boundary.

Aider must not write directly to canonical/protected source.

---

## 9. Editor sandbox rules

The experiment must:

- expose only authorized writable files;
- provide only bounded necessary read-only context;
- disable Aider auto commits;
- not install dependencies in the target project;
- not expand write scope;
- not push or merge;
- run under the existing local zero-cost provider policy;
- return candidate file content/diff to ForgeLab;
- require ForgeLab deterministic validation before ToolGateway apply.

---

## 10. EDITOR_ENGINE_BAKEOFF_01

Compare:

A. current custom editor from canonical merged `main`;  
B. Aider CLI adapter.

Hold constant:

- same Dental Quote baseline;
- same objective;
- same authorized files;
- same `qwen2.5-coder:7b`;
- same Planner acceptance criteria;
- same deterministic tests;
- same Reviewer;
- same Security;
- same repair cap;
- provider cost EUR 0.

Metrics:

- successful candidate generation;
- compile-valid candidate;
- malformed edit events;
- deterministic test result;
- semantic review result;
- model-call count;
- repair count;
- wall-clock time;
- unauthorized path changes;
- Product Owner touches;
- usable-output state.

Why the model stays unchanged in phase 1:

The first experiment must isolate whether the editing engine, not the model, is responsible for a meaningful portion of the instability.

Only if both editor paths remain poor should a stronger local model be benchmarked.

---

## 11. Workstation constraint

Known local ForgeLab workstation:

- NVIDIA GeForce RTX 4050 Laptop GPU;
- about 6 GB VRAM;
- about 15.7 GB system RAM;
- current local model `qwen2.5-coder:7b` works through Ollama at EUR 0.

This hardware makes a simple jump to very large local agentic models unattractive.

Therefore:

`EDITOR ENGINE FIRST -> MODEL BENCHMARK SECOND`

---

## 12. Consolidation rule

After the editor bakeoff:

1. identify general runtime behaviors worth keeping;
2. do not merge #37–#48 as a chain;
3. create a fresh consolidation branch from canonical `main`;
4. split editor/prewrite/repair responsibilities out of the orchestrator;
5. integrate only evidence-backed behavior;
6. validate through dashboard;
7. only then request Product Owner merge approval.

Suggested module boundaries:

- `editor_adapter.py`;
- `prewrite_validation.py`;
- `repair_policy.py`.

---

## 13. Dashboard-first product gate

MVP validation resumes only when the ordinary Product Owner journey is:

1. start local ForgeLab services once;
2. open dashboard;
3. select/register project;
4. enter objective;
5. click Run;
6. ForgeLab works without manual retry orchestration;
7. dashboard presents plan, changes, tests, risk, usage and decision;
8. Product Owner chooses Approve / Reject / Repair.

PowerShell is permitted for:

- bootstrap;
- service startup;
- exceptional developer diagnostics.

It must not be the repeated Product Owner workflow.

---

## 14. Editor bakeoff harness candidate

PR:

`#50 — MVP Recovery: add bounded reusable editor bakeoff harness`

Branch:

`mvp-recovery-editor-adapter-bakeoff`

Initial PR head:

`1c57fe83f1dd96f57a74c6458bef8865720f8a6b`

The PR remains subject to live HEAD verification before merge because documentation commits may advance the branch after PR creation.

Candidate scope:

- new `EditorAdapter` boundary;
- `AiderCliAdapter` restricted to disposable copies of authorized files;
- no Aider write access to the governed workspace;
- no Aider package dependency added to ForgeLab;
- no `orchestrator.py` modification;
- no dashboard/API/Golden Path integration yet;
- paid-provider API keys stripped from the Aider subprocess environment;
- read-only mutation, path escape and unauthorized file creation rejected;
- deterministic compile/test/scope/security evaluator;
- machine-readable `EDITOR_ENGINE_BAKEOFF_01` artifact;
- experimental CLI entry point only.

Independent focused verification performed against the exact candidate module contents:

- editor adapter tests: 5 / 5 PASS;
- bakeoff evaluator tests: 5 / 5 PASS;
- combined focused verification: 10 / 10 PASS;
- `editor_adapter.py`: compile PASS;
- `editor_bakeoff.py`: compile PASS;
- modified `cli.py`: compile PASS.

Important limitation:

No real Aider + Ollama Dental Quote run has been performed yet. This PR proves the safety/evaluation boundary, not Aider superiority or Golden Path success.

Human gate:

`APPROVE_MERGE_PR50 | REJECT_PR50 | REQUEST_CHANGES`

After approved merge, proceed autonomously to the real bounded Aider/Ollama editor experiment without returning to the repetitive Product Owner PowerShell loop.

---

## 14. Commercial status

Commercial evidence:

`C0 — Hypothesis`

No market-validation claim.

Current objective remains technical/product validation of a genuinely usable software factory before customer validation.

---

## 15. Single next action

`HUMAN_REVIEW_EDITOR_ADAPTER_BAKEOFF_HARNESS_PR50`

Product Owner decision required:

- approve merge;
- reject;
- request changes.

No local command or PowerShell action is required from the Product Owner.

---

## 16. Resume protocol

At the start of the next session:

1. read `AGENTS_MASTER.md`;
2. read `MANIFEST.md`;
3. read `PROJECT_STATE.md`;
4. read `ROADMAP.md`;
5. read `DECISIONS.md`;
6. read this handover;
7. read the architecture-reset audit;
8. read ADR-002;
9. verify canonical `main`;
10. verify PR #50 live HEAD/state/checks;
11. if PR #50 is not merged, stop at the human merge gate;
12. after explicit merge approval, execute the real bounded Aider/Ollama editor experiment.

Do not resume PR #48 testing and do not ask the Product Owner for a PowerShell rerun.

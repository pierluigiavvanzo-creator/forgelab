# Project State

## Current milestone

M8.6 Multi-file AI Developer — PASS end-to-end.

Checkpoint date: 2026-09-21.

## Current product capability

ForgeLab is a local-first multi-agent software development control plane that can:

- receive an objective from the Product Owner through the local dashboard;
- route local AI work through Ollama using `qwen2.5-coder:7b` at provider cost EUR 0;
- create a bounded execution plan;
- authorize one to three explicit target files for AI Developer runs;
- require machine-structured AI changes for each authorized file;
- reject unauthorized path expansion before deterministic application;
- apply edits only through ToolGateway inside an isolated workspace/worktree;
- run deterministic acceptance tests;
- run an independent AI Reviewer;
- stop material runs at `READY_FOR_DECISION`;
- require one explicit human decision before promotion;
- promote the reviewed patch to a dedicated local branch;
- rerun deterministic tests before creating one local commit;
- preserve the source checkout HEAD and main branch during governed promotion;
- execute no automatic push, merge, or force operation;
- persist promotion evidence in `PromotionResult.json`.

## Verified M8.3-M8.6 capabilities

### M8.3A — Local AI Runtime

PASS.

- Ollama local runtime.
- Model: `qwen2.5-coder:7b`.
- Provider alias: `ollama`.
- Provider cost: EUR 0.

### M8.3B — Router + Orchestrator local AI

PASS.

### M8.3C — Dashboard local-AI integration

PASS.

### M8.4A — Objective-only AI Developer backend

PASS.

### M8.4B — AI Developer dashboard mode

PASS.

### M8.4B.1 — Windows `py -3.11` UX normalization

PASS.

### M8.5 — Human-approved local promotion

PASS.

Promotion remains local-only and governed by explicit Product Owner approval.

### M8.5.1 — UTF-8 Git diff capture/promotion hotfix

PASS.

Git textual output used for patch capture/promotion is decoded explicitly as UTF-8 and the BOM regression remains covered by the promotion regression suite.

### M8.6 — Multi-file AI Developer

PASS end-to-end.

Validated browser-created run:

- run id: `run-c0dcc3b62f29`;
- authorized/changed paths: `calculator.py`, `test_calculator.py`;
- deterministic tests: PASS;
- repair attempts: 0;
- independent reviewer completed;
- human gate: APPROVED;
- promotion branch: `forgelab/promote/run-c0dcc3b62f29`;
- promotion commit: `9da496665cef92c8079e10a1a252e9872ffc4c40`;
- reviewed source base HEAD: `c52bfdf2648d5bef70b0a6f01fd9287a05f92dba`;
- promoted patch SHA-256: `c887c5524b56a21b81bf4fd8429ea6686264ce19cd1afcca6e4518da9176e2c3`;
- source HEAD unchanged: true;
- source main untouched: true;
- push executed: false;
- merge executed: false;
- force operations executed: false.

## Preserved earlier platform capabilities

- Domain contracts for projects, runs, tasks, evidence, findings, usage, and gates.
- Canonical run state machine with invalid-transition rejection.
- JSON artifact persistence and deterministic smoke flow.
- Real Git worktree execution with bounded edits and deterministic tests.
- Deterministic scope review and detection of common secrets in added lines.
- PM, Developer, Tester, Reviewer, conditional Security/Documentation, and failure-triggered Support roles.
- Bounded hypothesis-driven repair infrastructure with attempt caps and evidence history.
- S0-S4 task classification and provider-neutral model routing.
- Repository-backed project memory and selective context bundles.
- Role-to-tool permission enforcement and audited ToolGateway actions.
- Network default-deny / explicit allowlist controls where configured.
- Local Product Owner dashboard with Plan, Changes, Tests, Risk, Model Usage, and Decision panels.
- Evidence-backed KPI aggregation, local queue/cache/scheduler/metering capabilities, and package-integrity checks.

## Intentionally not implemented / not authorized

- automatic push to remote repositories;
- automatic merge to protected branches;
- force operations;
- production remote deployment from AI Developer runs;
- arbitrary repository-wide AI edits;
- unbounded multi-file scope;
- distributed broker/horizontal worker production infrastructure;
- production billing provider integration.

## Current decision

Repository files remain the source of truth.

AI Developer may operate on one to three explicitly authorized files. ToolGateway and deterministic tests remain authoritative. Multi-file capability does not expand permissions beyond the declared allowed path set. Promotion remains a separate, one-shot human-approved local operation.

The next product gap is not broader write access. It is bounded AI-assisted repair when an `ai_generate` run fails deterministic tests, while preserving the same authorized path set and all M8.5/M8.6 governance guarantees.

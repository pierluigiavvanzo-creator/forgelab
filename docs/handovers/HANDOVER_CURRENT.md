# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-09-21  
**Checkpoint milestone:** M8.6  
**Status:** PASS / bounded multi-file AI Developer validated end-to-end

## 1. Mission

ForgeLab is a local-first multi-agent software development control plane.

Primary product metric:

`ECONOMIC VALUE × USABLE PRODUCT VALUE / USER TIME`

Operating preference:

- work in normal ChatGPT chat + local PowerShell;
- do not use ChatGPT Work or Codex;
- bounded diagnostics and bounded repairs;
- preserve backups before material changes;
- verify current source before every new patch;
- Product Owner intervenes only at material human gates.

## 2. Local environment

ForgeLab root:

`C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`

Dashboard:

`http://127.0.0.1:5173`

API:

`http://127.0.0.1:8765`

Canonical launcher:

`Start-ForgeLab.ps1`

Local AI runtime:

- Ollama 0.34.2;
- `qwen2.5-coder:7b`;
- provider alias: `ollama`;
- provider cost: EUR 0.

## 3. Milestone state

### M8.3A — Local AI Runtime

PASS.

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

Preserve:

- explicit human approval before promotion;
- reviewed base HEAD check;
- source cleanliness checks inside the promotion contract;
- dedicated local promotion branch;
- isolated temporary worktree;
- already-reviewed diff as promotion input;
- deterministic tests before commit;
- source checkout not used as the promotion worktree;
- no direct-main write;
- no automatic push;
- no automatic merge;
- no force operations;
- one-shot approval semantics;
- `PromotionResult.json` evidence.

### M8.5.1 — UTF-8 Git diff capture/promotion hotfix

PASS.

Preserve explicit UTF-8 handling on Git textual output and the BOM regression
coverage.

### M8.6 — Multi-file AI Developer

PASS end-to-end.

Implemented:

- `ai_generate` supports one to three explicitly authorized files;
- multi-file AI output is machine-structured;
- every proposed path is validated independently;
- duplicate or unauthorized paths are rejected;
- path expansion outside the authorized set is rejected before write;
- ToolGateway remains the authoritative deterministic write boundary;
- deterministic tests remain authoritative;
- independent review remains mandatory;
- M8.5 promotion path is reused rather than duplicated;
- single-file AI Developer behavior remains supported.

## 4. M8.6 local validation

The governed local installer completed with:

- orchestrator regression: PASS;
- API regression: PASS;
- M8.5 promotion regression: PASS;
- governance regression: PASS;
- dashboard production build: PASS;
- deterministic smoke: PASS.

An initial dashboard build attempt failed with Windows `EPERM` because
`dashboard\dist` was locked by an active ForgeLab Node/Vinext process.
The installer rolled the M8.6 source patch back successfully. A bounded repair
stopped only ForgeLab dashboard Node processes, removed the generated `dist`
output, and reran the installer. Final local code validation: PASS.

## 5. M8.6 live browser acceptance

Run:

`run-c0dcc3b62f29`

Source repository:

`C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1\.forgelab\demo-repositories\m8-4a-ai-developer-20260920_150750`

Objective required exactly two authorized files:

- `calculator.py`
- `test_calculator.py`

Pre-gate evidence:

- status: `READY_FOR_DECISION`;
- both authorized files shown as changed;
- no third changed file shown;
- deterministic test: PASS;
- repair attempts: 0;
- Project Manager, Developer, Tester, and Reviewer completed;
- Product Owner gate required.

The Product Owner approved the run once.

Final state:

`DONE`

## 6. Promotion evidence

`PromotionResult.json` for `run-c0dcc3b62f29` records:

- actor: Product Owner;
- changed paths: `calculator.py`, `test_calculator.py`;
- promotion branch: `forgelab/promote/run-c0dcc3b62f29`;
- promotion commit: `9da496665cef92c8079e10a1a252e9872ffc4c40`;
- source base HEAD: `c52bfdf2648d5bef70b0a6f01fd9287a05f92dba`;
- source branch: `main`;
- patch SHA-256: `c887c5524b56a21b81bf4fd8429ea6686264ce19cd1afcca6e4518da9176e2c3`;
- tests: PASS;
- source HEAD unchanged: true;
- source main untouched: true;
- push executed: false;
- merge executed: false;
- force operations executed: false.

Do not infer additional evidence fields that are not present in this
`PromotionResult.json`.

## 7. Closeout changes

M8.6 closeout aligns the dashboard labels with the actual capability:

- `M8.4 AI Developer` → `M8.6 Multi-file AI Developer`;
- `RUN CONTROL - MILESTONE 8.4` → `RUN CONTROL - MILESTONE 8.6`;
- `NEW RUN - M8.4` → `NEW RUN - M8.6`.

Canonical memory is also updated:

- `PROJECT_STATE.md`;
- `ROADMAP.md`;
- `DECISIONS.md` with D-012;
- `docs/M8_6_ACCEPTANCE_REPORT.md`;
- `docs/handovers/HANDOVER_CURRENT.md`.

## 8. Current security / governance guarantees

Preserve:

- execution changes occur in isolated workspace/worktree;
- source repository remains unchanged during execution;
- model proposals do not bypass ToolGateway;
- ToolGateway/policy remain authoritative;
- deterministic tests remain authoritative;
- material runs stop at `READY_FOR_DECISION`;
- promotion requires explicit human approval;
- promotion is local-only;
- no direct main write;
- no automatic push;
- no automatic merge;
- no force operations;
- stale/consumed approval is not reused;
- allowed paths remain explicit and bounded;
- multi-file capability must never imply repository-wide write authority.

## 9. Current product capability

ForgeLab can now execute:

objective
→ AI Project Manager
→ AI Developer
→ one to three bounded authorized files
→ structured multi-file patch
→ deterministic ToolGateway application in isolation
→ deterministic tests
→ independent AI Reviewer
→ human gate
→ governed local promotion
→ dedicated local branch
→ deterministic re-test
→ local commit
→ `PromotionResult.json`

This is a real multi-file development workflow, not a multi-prompt façade.

## 10. Known product gap

The existing repair loop does not yet provide a full AI-generated repair path
for failed `ai_generate` runs. In the current orchestrator, a failed AI-generated
candidate with no deterministic `initial_new_text` repair candidate stops for
human repair rather than asking Developer for a new bounded AI patch.

This is the next high-value robustness gap.

## 11. SINGLE NEXT ACTION

### M8.7 — Bounded AI Developer repair for `ai_generate`

**Classification:** A / B — Product reliability and autonomy

Objective:

extend the hypothesis-driven repair loop to AI Developer runs so a deterministic
test failure can trigger one or more bounded AI-assisted repair attempts within
the already-authorized file set.

Required scope:

- use the existing `max_repair_attempts` budget;
- Support must produce a new evidence-backed failure hypothesis before each
  repair attempt;
- Developer may generate a new patch only for the original authorized paths;
- no path expansion;
- no increase beyond the 1–3 file authorization cap;
- ToolGateway remains the only write boundary;
- deterministic tests rerun after every repair;
- repeated identical repair without new evidence is prohibited;
- independent review remains mandatory after tests pass;
- material run still stops at `READY_FOR_DECISION`;
- M8.5 local promotion and one-shot human approval remain unchanged;
- no automatic push, merge, force, or direct-main write.

Do not start by adding repository-wide autonomous repair.

## 12. Acceptance target for M8.7

A browser-created AI Developer run should be able to:

1. receive an objective requiring two authorized files;
2. generate a first bounded multi-file candidate;
3. fail a deterministic acceptance test;
4. enter DIAGNOSING;
5. produce a Support hypothesis tied to the failed test evidence;
6. enter REPAIRING;
7. generate a second bounded AI patch using only the same authorized files;
8. reject any repair path expansion;
9. rerun deterministic tests;
10. reach PASS within the configured repair cap;
11. run independent review;
12. reach `READY_FOR_DECISION`;
13. receive one explicit Product Owner approval;
14. promote through the unchanged M8.5 local promotion path;
15. execute no automatic push, merge, or force operation.

## 13. Do not regress

- deterministic mode;
- existing AI-assisted mode;
- AI Developer single-file mode;
- M8.6 multi-file mode;
- local zero-provider-cost path;
- S0 deterministic tools;
- bounded scope;
- exact authorized-path enforcement;
- deterministic tests;
- independent review;
- human gate;
- loopback API;
- loopback Ollama;
- no direct main write;
- no automatic push;
- no automatic merge;
- no force operations;
- M8.5.1 UTF-8/BOM handling.

## 14. Next-chat bootstrap instruction

Use:

`Continua ForgeLab dal checkpoint HANDOVER_CURRENT_FORGELAB_M8_6.md. Non usare Work o Codex. Lavora in chat + PowerShell locale. Considera M8.6 PASS end-to-end. Verifica comunque i sorgenti locali prima di modificare codice. Non rifare milestone già PASS. Esegui esclusivamente la SINGLE NEXT ACTION: M8.7 Bounded AI Developer repair for ai_generate. Preserva allowed_paths bounded 1-3 file, ToolGateway, test deterministici, independent review, human gate, one-shot local promotion, zero direct-main write, zero automatic push/merge/force e il fix UTF-8/BOM M8.5.1.`

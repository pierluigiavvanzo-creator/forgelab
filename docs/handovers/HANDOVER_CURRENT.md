# ForgeLab — HANDOVER_CURRENT

**Checkpoint date:** 2026-09-30  
**Checkpoint:** stabilization publication candidate / Software Factory Golden Path focus  
**Status:** PRE-MVP; stabilization reviewed, merge not authorized

## 1. Strategic decision

ForgeLab is the primary product. It must take a Product Owner objective and create, test, repair, review and prepare usable software without depending on ChatGPT chat as the orchestration layer.

Canonical workflow:

`OBJECTIVE -> PROJECT/REPO CONTEXT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED REPAIR -> REVIEW -> WORKING PREVIEW -> HUMAN APPROVAL -> PROMOTION`

Provider remains replaceable; current zero-cost local path is Ollama.

Primary metric: `ECONOMIC VALUE × USABLE PRODUCT VALUE / USER TIME`.

## 2. Canonical repository

Repository: `pierluigiavvanzo-creator/forgelab`

Canonical branch: `main`

Verified pre-stabilization `main`: `20c3c2565c6ce066520b8ce831b13640858cde2b` (merge of PR #17).

Stabilization branch: `mvp1-stabilization-cleanup`

Local worktree: `C:\\Users\\NITRO\\source\\FORGELAB_MVP1_STABILIZATION_CLEANUP`

## 3. Product Owner contract

Preserve Product Owner as approver/final usability tester; no routine debugging, QA, log transport or retry orchestration. Preserve isolated workspaces, ToolGateway authoritative writes, explicit scope, deterministic tests/retests, bounded repair, structured contracts, independent review/security, exact reviewed-diff promotion, no force/rebase and explicit human promotion gate. ForgeLab runtime must not auto-push or auto-merge.

Operating preference: normal ChatGPT chat for development assistance, Windows PowerShell only when necessary, no Work, no Codex.

## 4. Reviewed stabilization change

Exact reviewed local code scope:

- 68 deletions;
- 4 modified existing files;
- 72 tracked files total;
- 19 insertions;
- 7,633 deletions;
- no untracked files in final precommit review.

Removed: non-authoritative `.forgelab/quality-gates.yaml`, unused scale module/test, unused D1/Drizzle starter files, unused ChatGPT-auth starter, mobile hook and 57 unused dashboard UI component files.

Modified:

- `dashboard/vite.config.ts` — removed untracked `./build/sites-vite-plugin` dependency;
- `tests/test_api.py` — aligned two stale reviewer fixtures to structured semantic-review PASS contract;
- `tests/test_config.py` — removed stale quality-gates expectation;
- `tests/test_package_integrity.py` — removed stale quality-gates package requirement.

Not modified intentionally: core orchestrator, ToolGateway, PolicyEngine safety boundary, repair budget, semantic review runtime, Product Owner gate, promotion logic, runner, smoke behavior, telemetry, npm dependency list/lockfile.

## 5. Validation evidence

- API integration tests: 12/12 PASS;
- full Python regression: 106/106 PASS;
- dashboard production build: PASS, Product Owner-confirmed.

Dashboard PASS is not yet a persisted GitHub CI artifact. Do not repeat diagnostics absent new evidence.

## 6. Golden Path milestone

Next phase: `FORGELAB MVP-1 SOFTWARE FACTORY GOLDEN PATH`.

Required journey:

`PRODUCT OBJECTIVE -> CREATE/SELECT PROJECT -> PLAN -> IMPLEMENT -> TEST -> BOUNDED AUTO-REPAIR -> RETEST -> REQUIREMENT REVIEW -> WORKING PREVIEW -> PRODUCT OWNER APPROVAL -> PROMOTABLE PRODUCT`

## 7. Golden Path 1 — Dental Quote

Target: `C:\\Users\\NITRO\\source\\FORGELAB_MVP1_DENTAL_QUOTE`

Objective: add support for three treatments, automatic subtotals, percentage discount and final total; validate inputs; modify only necessary files; add tests; do not change dependencies/configuration unless necessary and explicitly justified.

Authorized files: `quote_calculator.py`, `test_quote_calculator.py`.

Test command: `py -3.11 -m unittest discover -v`.

Dental Quote is a crash test of ForgeLab. PASS requires a genuinely correct usable app without ChatGPT manually orchestrating routine repair/debug steps.

## 8. Out of scope until Golden Path PASS

Do not prioritize multi-tenancy, billing, advanced scaling, deployment platform expansion, paid-provider expansion, new agent roles, broad observability, new configuration frameworks, unrelated refactors or architecture work without a demonstrated Golden Path blocker.

## 9. Generality proof after Dental Quote PASS

1. Dental Quote — calculator/business logic.
2. Small CRUD SaaS — records/users/workflow.
3. Automation/reporting tool — ingest -> transform -> report.

Success means the same ForgeLab workflow works across all three categories without being hardcoded for the first.

## 10. Current gate

The stabilization publication candidate is ready for GitHub PR review.

Do not merge without explicit Product Owner approval.

After approved merge, immediately run Dental Quote Golden Path end-to-end and fix only blockers that prevent the product journey.

## 11. New-chat startup

Use GitHub as source of truth; verify `main`; read `MANIFEST.md`, `AGENTS.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `docs/handovers/HANDOVER_CURRENT.md`; verify whether the stabilization PR merged; do not use Work or Codex; do not repeat captured diagnostics.

## 12. Single next action

Review stabilization PR and CI. Stop before merge for explicit Product Owner approval.

---

## Commercial roadmap override — 2026-10-01

Shared governance now prioritizes market evidence over additional internal technical milestones.

**Current commercial evidence:** `C0 — Hypothesis`.

The stabilization PR and one fresh Dental Quote Golden Path run remain the immediate prerequisite because they create a measurable demo asset. After that PASS:

`STOP INTERNAL EXPANSION -> SELECT NARROW BUYER/JOB -> REAL EXTERNAL BRIEF -> WORKING PREVIEW -> BUYER FEEDBACK -> PAID PILOT/LOI SIGNAL`

Do not continue to a second generic benchmark application, new agents, platform breadth or infrastructure work by default.

The next commercial action is:

`FORGELAB_C1_OUTPUT_FIRST_BUYER_VALIDATION`

The first market test should validate a bounded **software outcome produced by ForgeLab**. Whether ForgeLab itself should later be sold as a standalone control-plane product remains a commercial hypothesis, not a settled fact.

No external offer, pricing commitment or customer communication is authorized by this documentation update.


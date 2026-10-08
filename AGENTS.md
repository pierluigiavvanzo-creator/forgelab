> **Shared governance v2 — 2026-10-01**
>
> Read `AGENTS_MASTER.md` before this file. The master governs shared product, economic, marketability and engineering execution. This `AGENTS.md` remains authoritative for ForgeLab-specific multi-agent control-plane constraints, baseline integrity, isolation, review/security and promotion gates. Project-specific rules may tighten the master and must not silently weaken it.

---

# AGENTS.md

## Mission

Build and operate ForgeLab as a governed multi-agent software-development control plane that produces usable software outcomes with minimal Product Owner effort.

## Operating principles

1. Product before infrastructure.
2. Never invent implementation state, test results, source synchronization, approvals or economic outcomes.
3. GitHub and repository-backed project memory are the canonical shared record for project state.
4. The currently validated local source baseline is documented but must not be claimed as fully published to GitHub until actually synchronized and verified.
5. The Product Owner is approver and final tester, not routine QA, debugger or log transporter.
6. Use the minimum necessary agents and tools.
7. Diagnose failures using bounded, hypothesis-driven loops.
8. Preserve isolation, deterministic verification, independent review/security and explicit human promotion gates.
9. Do not write directly to protected production/main flows unless the Product Owner explicitly authorizes the specific action and project governance allows it.
10. Do not auto-push, auto-merge or force-update refs.
11. Every material milestone must state its expected product/economic contribution.
12. Every substantial custom capability should follow repository-first assessment when reuse could materially reduce time, cost or risk.

## Work classification

- A — Product Critical
- B — Material Upgrade
- C — Optimization
- D — Diagnostic / Technical

Manual Product Owner effort on D work should be exceptional and justified by A-level risk.

## Persistent Memory Protocol

At the beginning of a ForgeLab task, read:

1. `MANIFEST.md`
2. `AGENTS.md`
3. `PROJECT_STATE.md`
4. `ROADMAP.md`
5. `DECISIONS.md`
6. `docs/handovers/HANDOVER_CURRENT.md`
7. relevant ADRs/audits

At the end of a successful material task, update the relevant canonical files with:

- what changed;
- what was tested;
- what passed;
- what failed;
- what remains;
- important assumptions;
- next single action.

Never erase historical architectural decisions; supersede them explicitly.

## Current single next action

`HUMAN_REVIEW_POST_PR65_FINAL_STABILIZATION`

PR #65 is merged at `2227c2487b8858738db7bcf38cdcebeff4699c4f`. Post-merge verification found launcher process-ownership/cleanup defects; review the single correction branch `fix/post-pr65-final-stabilization`. Candidate stabilization PASS and executed evidence are recorded in [PROJECT_STATE.md](PROJECT_STATE.md). No automatic merge or Dental run; Dental requires verified integration and separate Product Owner authorization.

> Shared governance: read AGENTS_MASTER.md first.

# AGENTS.md — ForgeLab project rules

## Mission

Build and operate ForgeLab as a governed software-development control plane that produces usable software outcomes with minimal Product Owner effort.

## Operating rules

1. Product value outranks infrastructure volume.
2. GitHub main and repository-backed canonical files are the shared source of truth.
3. Never invent implementation state, test results, synchronization, approvals, CI or economic outcomes.
4. The Product Owner is approver of hard gates and final usability tester, not routine debugger, QA operator or log transporter.
5. Use the minimum agents, tools, model calls and files needed for the result.
6. Preserve isolated execution, authorized write paths, deterministic verification, independent review/security and explicit human promotion of target-product code.
7. Work on branches and merge through pull requests under the AGENTS_MASTER standing approval (full suite + CI + end-to-end smoke for runtime changes, no hard gate touched). Never force-push or write directly to main.
8. Diagnose repeated failures by evidence and root cause. Stop when additional attempts no longer add information.
9. Reuse-first and zero-cost-provider-first remain binding.
10. Every material change must preserve a rollback path: record the revert command in DECISIONS.

## Standing approvals specific to ForgeLab

Without asking the Product Owner, agents may:

- add, switch, qualify or retire Ollama Cloud **Free-plan** models used through the signed-in local Ollama (loopback), for any ForgeLab role; this supersedes the per-model approvals required by ADR-002 phase 1;
- run synthetic, smoke and end-to-end runs on the protected synthetic fixtures within the Free-plan quota, stopping on any quota/credit message;
- change prompts, routing between already-approved model families, timeouts and repair budgets when a test or run gives evidence, recording the reason in DECISIONS.

Still hard gates in ForgeLab (in addition to AGENTS_MASTER section 9):

- sending code or data of a real product (not a synthetic fixture) to cloud models for a project the Product Owner has not yet approved for cloud;
- removing the human promotion gate for target-product code, or merging promoted target code into a target project's main branch;
- widening ToolGateway, network or secret policies for target runs (for example allowing dependency installation, network beyond loopback, or real secrets).

## Persistent memory protocol

At the start of material work read, in order:

1. AGENTS_MASTER.md
2. MANIFEST.md
3. AGENTS.md
4. PROJECT_STATE.md
5. ROADMAP.md
6. DECISIONS.md
7. docs/handovers/HANDOVER_CURRENT.md
8. only the audit/ADR directly relevant to the task

Do not load historical acceptance reports or every audit by default.

At completion update only the canonical files materially affected and record:
- what changed;
- what was tested;
- what passed/failed;
- unresolved risk;
- single next action.

Historical detail belongs in Git history, DECISIONS.md, ADRs and focused audit reports rather than being duplicated into every canonical file.

## Current gate

See PROJECT_STATE.md and docs/handovers/HANDOVER_CURRENT.md for the current state and single next action.

Approved for cloud: the synthetic fixtures and Dental Quote (Product Owner consent, 2026-10-22).

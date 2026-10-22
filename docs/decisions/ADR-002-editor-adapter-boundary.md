# ADR-002 — Separate ForgeLab governance from the code-editing engine

**Date:** 2026-10-05  
**Status:** Aider boundary implemented; qualified cloud routing proposed for review (2026-10-21); original comparative acceptance criterion not yet evidenced
**Class:** A — Product Critical

## Status clarification — 2026-10-08

Merged PRs #50–#64 and D-023 establish actual use of the Aider boundary, including all four editor phases. The executed adapter/orchestrator tests support integration, but do not prove the comparative failure-reduction criterion below. That historical acceptance condition is retained; Golden Path #1 is still NOT PASS. See [post-merge evidence](../audits/FORGELAB_POST_PR64_VERIFICATION_2026-10-08.md).

## Editor-model decision — 2026-10-21

Aider remains the editing engine. PO approved `gpt-oss:120b-cloud` primary and `gemma4:31b-cloud` alternative, each qualified 2/2 in [PR #73](https://github.com/pierluigiavvanzo-creator/forgelab/pull/73). This supersedes the earlier proposal to retain a local fallback: qwen2.5-coder:7b is excluded from every Aider editor phase. The immutable validated editor configuration is independent of S1/S2, including correction subpaths previously routed directly to S2. No automatic or silent transition from Aider to the legacy custom engine is permitted.

Use only signed-in local Ollama via the preserved loopback guard. Primary model unavailable (404/410, retired/not found) permits the alternative once within the original deadline. Quota/credit/billing/402/429 stops the run as EDITOR_CLOUD_QUOTA_STOP without switching; both unavailable stops as EDITOR_MODEL_UNAVAILABLE. Record model, reason and stop/switch evidence. No direct cloud API/key or new provider. EUR 0, no billing changes or upgrades.

Only synthetic data is authorized for this implementation/smoke. Dental source transfer remains undecided: no Dental execution, promotion or merge in this task. Non-editor planner/reviewer/Support routes and deterministic Security remain unchanged. The separately selected legacy custom engine is outside this Aider migration and is never an automatic fallback.

Aider version, edit format/flags, existing timeout ceilings, repair budgets, deterministic verification and human promotion are unchanged. Evidence: [routing audit](../audits/FORGELAB_CLOUD_EDITOR_ROUTING_2026-10-21.md). The one synthetic integration smoke passes; this does not establish live non-editor quality, Dental readiness or account quota.

## Reviewer cloud decision — 2026-10-22

This supersedes the prior unchanged-reviewer restriction. The PO accepts the risk of moving REVIEWER immediately without separate qualification rounds: gemma4:31b-cloud primary, gpt-oss:120b-cloud alternative only for 404/410/retirement/not-found, marked **reduced independence** from the gpt-oss editor. No local reviewer fallback. Quota/credit/billing/402/429 stops without switching. A dedicated REVIEWER policy leaves Planner/S1 and Support/S2 on qwen2.5-coder:7b and leaves the Aider editor chain unchanged.

Reuse the existing provider error classifier, loopback guard, PR #78 context sizing/truncation checks and explicit strict reviewer JSON contract. Record model/attempts/reasons in UsageReport and reviewer artifacts. Only signed-in http://127.0.0.1:11434, EUR 0, synthetic data; no credits/payment/upgrade, Dental, promotion or service restart. Engine/version/flags/timeouts/budgets/human approval unchanged.

Verification is exactly one real production run with the clean product objective and max_repair_attempts=1; only a failure solely from invalid/wrong Gemma review permits one gpt-oss-primary repeat. Merge is authorized only on READY_FOR_DECISION + generated-test exit 0 + independent 6/6 + no false blocking reviewer finding, with human approval pending.

Actual delivery: 213 tests PASS; single run FAIL because editor/Support repair introduced erroneous rounding to satisfy an incorrect generated test; Gemma correctly blocked it. Independent acceptance 2/6 test methods. No conditional repeat and **no merge**. At that Task E checkpoint the cloud reviewer implementation remained on its branch. PR #79 was subsequently merged; Task F starts from main c4ff897. [Audit](../audits/FORGELAB_CLOUD_REVIEWER_ROUTE_2026-10-22.md).

## Shared Reviewer/Support cloud policy — 2026-10-22

PO Task F supersedes the local Support restriction above. REVIEWER and SUPPORT now use the same validated policy: gemma4:31b-cloud primary, gpt-oss:120b-cloud only on model unavailability, with reduced-independence evidence. No local model, no quota-triggered switch, no generic S1/S2 retries. Quota/credit/billing/402/429 stops with a role-specific reason. Planner remains local S1; Aider/editor chain, loopback restriction, EUR 0 and strict review validation remain unchanged. Only synthetic data is authorized.

Generated tests are not an oracle: Support and all repair/correction prompts must recompute expectations from objective and inputs, repair an incorrect test while preserving coverage, and reject assertion-fitting implementation logic. Support receives complete authorized candidate files and PM contract via the existing bounded readers. This is a prompt/evidence safeguard, not a guarantee of LLM reasoning correctness.

The single authorized production run (max_repair_attempts=2, one used) PASS: READY_FOR_DECISION, generated tests 11/11 exit 0, independent acceptance 6/6, no reviewer findings, human gate PENDING. 216 Python tests PASS. Cloud 22,562 tokens; no second run, Dental, promotion, purchases or service restart. Merge condition met. [Task F audit](../audits/FORGELAB_CLOUD_SUPPORT_TEST_ORACLE_2026-10-22.md). PO must inspect account usage before any further real workload decision; broader reliability remains unverified.

## Planner cloud and user-visible acceptance — 2026-10-22

Task G supersedes the local Planner restriction. PROJECT_MANAGER uses the same validated cloud policy as REVIEWER/SUPPORT: Gemma primary, gpt-oss alternative only on unavailability, quota/billing STOP, no local fallback. Actual planning model and attempts are recorded; planning failures close the run before implementation with role-specific evidence. Aider remains the editor with its existing chain/flags/timeouts. Only signed-in loopback Ollama, EUR 0.

The PO explicitly limited Task G to the Aider path after clarification: the separately selected legacy custom editor and its S1/S2 routes remain unchanged. All LLM roles on the Aider path now use cloud models; this is not a claim that the legacy custom engine no longer uses local inference.

Planner must preserve every user-facing objective capability through the existing GUI/CLI/web interface and state explicit acceptance criteria. If the planner contract narrows the Objective, the Objective prevails in review: backend-only inaccessible capability is PARTIAL and overall FAIL. This is a prompt-level safeguard, not proof of semantic reliability. Scope limits must be disclosed, never silently substituted for the objective.

37 focused tests and 218 full-suite tests PASS. No real inference/E2E run authorized or performed in Task G; Dental repository/promotion branch untouched. Merge conditional on suite and GitHub checks. PO performs the next dashboard Dental verification; Golden Path points 5/8 are not declared satisfied. No service restart or promotion by this task.

## Context

ForgeLab's current control plane provides valuable governance: planning, isolated workspaces, deterministic testing, bounded repair, independent review, security evidence and human-gated promotion.

However, repeated Dental Quote runs exposed instability in the custom LLM-to-edit contract. The runtime has accumulated many special-case recoveries for structured output, source references, whole-file regeneration and Python quoting/syntax.

The Product Owner has also been pulled into repetitive PowerShell validation loops, which conflicts with the product contract.

Repository-first governance requires evaluating mature reuse before adding more custom editing logic.

## Decision

ForgeLab remains the control plane.

Introduce an explicit `EditorAdapter` boundary between planning and governed repository writes.

The first reuse experiment will use Aider through its scriptable CLI because it:

- supports local Ollama models;
- provides mature code edit formats;
- can be scoped to explicit files;
- can disable automatic git commits;
- can run one-shot scripted edits;
- is Apache-2.0 licensed;
- does not require replacing ForgeLab's planner, test, review, security or human gate.

The Aider experiment must run in an editor sandbox rather than directly modifying the governed workspace.

Flow:

```text
Planner
  -> EditorAdapter
  -> editor sandbox
  -> candidate files
  -> ForgeLab deterministic validation
  -> ToolGateway apply
  -> tests/review/security
```

ToolGateway remains the authoritative boundary that applies validated changes to the isolated ForgeLab workspace.

## Rejected alternatives for this MVP boundary

### OpenHands Software Agent SDK

Rejected for the narrow editor experiment because it would duplicate agent runtime, tool, workspace and server responsibilities already present in ForgeLab.

May be reconsidered only for a broader runtime replacement.

### Cline SDK / CLI

Rejected for the narrow editor experiment because it introduces a TypeScript/Node integration surface and overlaps substantially with the agent/tool lifecycle.

May be reconsidered for a broader runtime replacement.

### Continue

Rejected because the current project README states the repository is no longer actively maintained.

## Consequences

Positive:

- reduces custom parsing/edit-format responsibility;
- gives the local model a narrower task;
- preserves ForgeLab governance;
- allows apples-to-apples benchmarking;
- reduces incentive to add more syntax/string special cases.

Negative:

- introduces one external dependency for the experiment;
- Aider's Python API is not a stable compatibility surface, therefore the initial integration must use the CLI;
- edit sandbox/result import must be designed carefully to preserve ToolGateway authority.

## Guardrails

- no auto commit from the external editor;
- no direct write to protected/canonical source;
- only authorized writable files exposed to the editor sandbox;
- no dependency installation inside the target project;
- editor model exception approved 2026-10-21: only the qualified cloud chain below; no new provider or paid expansion;
- same objective, tests, Reviewer and repair cap as the existing Golden Path;
- no paid API without explicit Product Owner approval;
- experiment must record comparative metrics.

## Exit criteria

ADR becomes Accepted only after `EDITOR_ENGINE_BAKEOFF_01` demonstrates that the adapter reduces edit/recovery failures without weakening scope, deterministic verification, review, security or human control.

If it does not, reject Aider and preserve the `EditorAdapter` abstraction for the next candidate.

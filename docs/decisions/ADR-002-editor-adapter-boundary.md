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

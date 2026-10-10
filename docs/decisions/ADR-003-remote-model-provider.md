# ADR-003 — Optional remote model provider (Anthropic)

**Status:** Proposed — the default route is unchanged until the qualification gate passes
**Date:** 2026-10-10

## Context

Every local model tested on the 16 GB / RTX 4050 machine failed the semantic-repair qualification gate (`qwen2.5-coder:7b` and `:14b` 0/2, four 3–4B candidates 0/2), and the 14B run left 0.26 GiB of free RAM. The small-model search concluded that a more capable inference backend is needed. The Product Owner approved a paid backend limited to a few euros per month.

## Decision

Add `anthropic` as a second, opt-in provider. Nothing changes unless a routing file names it.

- **Router calls** (`AnthropicProvider`, official `anthropic` SDK): plan, review and structured repair. Cost is computed from the route's `pricing` and bounded by `max_call_cost` and the new top-level `run_budget`.
- **Editor calls** (Aider): the sandbox passes only `ANTHROPIC_API_KEY` and lets only `api.anthropic.com` bypass the blocked proxy. The local path still strips every provider key and stays loopback-only.
- **Accounting:** the editor's reported session cost is written to the run ledger; if it reports none, the full route reservation is charged. A provider rejection (Aider exits 0) fails the phase instead of looking like a no-op.
- **Config lookup:** without `FORGELAB_ROUTING_CONFIG`, the checkout's `.forgelab/routing.yaml` is used when the current folder has none, so ForgeLab can be launched from any folder.

`.forgelab/routing.cloud.yaml` is the candidate configuration: S1/S2 on `claude-haiku-5-5` ($0.10 / $0.50 per million tokens), `max_call_cost` $0.05, `run_budget` $1.00. Prices are copied from the provider's list on 2026-10-10 and must be kept current.

## How to qualify it

```powershell
py -3.11 -m pip install anthropic
$env:ANTHROPIC_API_KEY = "<key from the Anthropic Console, with a monthly spend limit>"
$env:FORGELAB_ROUTING_CONFIG = ".forgelab\routing.cloud.yaml"
.\Start-ForgeLab.ps1
```

Then follow `ROADMAP.md` unchanged: two independent runs of the synthetic semantic-repair fixture, 2/2 PASS required, and only after that the Dental Golden Path. Promote the cloud routes into `routing.yaml` only if the gate passes.

## Not verified yet

- No real inference was executed: there is no API key on the machine. Verified so far: 192 unit tests, and a real Aider 0.86.2 call with an invalid key that reached the API and was rejected with `authentication_error`.
- Aider 0.86.2 predates the current Claude models. `use_temperature: false` is set because they reject non-default sampling parameters; other incompatibilities can only surface in the qualification run.
- Router-call schemas are sent without length/size keywords (`minLength`, `minItems`, …); ForgeLab's own validators still enforce them.

## Consequences

- Source excerpts in prompts leave the machine when a cloud route is selected. Do not use it for repositories that must stay local.
- Spend is capped three times: provider-side monthly limit, `max_call_cost` per call, `run_budget` per run.
- S3/S4 remain on the unconfigured `premium` placeholder.

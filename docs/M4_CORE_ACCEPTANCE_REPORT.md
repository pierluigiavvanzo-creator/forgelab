# M4 Core Acceptance Report

Date: 2026-09-18.

## Outcome

M4 Core establishes model routing and economic controls without making an
external LLM call. It separates task classification, route policy, provider
adapters, usage accounting, budget enforcement, and benchmark scoring.

## Acceptance evidence

| Scenario | Result | Enforced behavior |
| --- | --- | --- |
| Deterministic task | PASS | S0 selected and every provider call rejected |
| Low-risk contextual task | PASS | S1 route selected |
| Local implementation | PASS | S2 route selected |
| Architecture or broad change | PASS | S3 route selected |
| Security or high-impact task | PASS | S4 and human review selected |
| Budget below route reservation | PASS | Call blocked before provider invocation |
| Transient provider failure | PASS | Retry bounded and each attempt recorded |
| Provider returns actual cost | PASS | Actual cost overrides configured estimate |
| No actual cost and no pricing | PASS | Usage is rejected rather than recorded as zero |
| Benchmark task set | PASS | Quality rate and total cost are reported |

## Remaining M4 exit gate

Full M4 completion requires at least two deliberately configured live routes or
models to run the same benchmark set. The comparison must record output quality,
token use, actual or current configured cost, latency, retry rate, and any
provider-specific data or lock-in constraint. No credential is stored in the
repository or passed through an agent prompt.

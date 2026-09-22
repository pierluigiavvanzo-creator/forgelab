# Reuse Benchmark M0

Review date: 2026-09-18.

| Candidate | Category | License signal | Maturity signal | M0 decision | Reason |
| --- | --- | --- | --- | --- | --- |
| LangGraph | Orchestration | MIT | Durable execution, human in loop, memory, active repository | BENCHMARKED DEFER | Strong fit, but unnecessary for contract-only M0; test in M1 |
| OpenAI Agents SDK Python | Agent runtime | MIT | Maintained lightweight multi-agent SDK | BENCHMARKED DEFER | Candidate adapter for M1; keep provider boundary portable |
| Microsoft AutoGen | Agent runtime | MIT code | Official repository states maintenance mode | REJECTED | New projects are directed to Microsoft Agent Framework |
| Daytona | Sandbox | Repository available | Secure elastic infrastructure for AI-generated code | DISCOVERED | Cloud sandbox is premature; benchmark after local worktree M1 |
| LiteLLM | Model gateway | Repository available | Multi-provider gateway with cost tracking and routing | DISCOVERED | Relevant to M4, not M0 |
| Langfuse | Observability | Repository available | Open-source traces, evals, and observability | DISCOVERED | Relevant after real LLM calls exist |

Sources:

- https://github.com/langchain-ai/langgraph
- https://github.com/openai/openai-agents-python
- https://github.com/microsoft/autogen
- https://github.com/daytonaio/daytona
- https://github.com/BerriAI/litellm
- https://github.com/langfuse/langfuse

No candidate is marked ADOPTED or USED. M0 does not integrate an external
runtime. Before M1 adoption, record version, license file, maintenance cadence,
security posture, integration cost, portability, and a measured scenario result.


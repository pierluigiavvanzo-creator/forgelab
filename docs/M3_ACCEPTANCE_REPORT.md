# M3 Acceptance Report

Date: 2026-09-18.

## Outcome

M3 implements artifact-coupled multi-agent orchestration without introducing an
LLM framework. Project Manager, Developer, Tester, and Reviewer cooperate using
`AgentTask` and `AgentResult` contracts. Security and Documentation are selected
only when request risk or file type requires them. Support appears only after a
test failure.

## Acceptance evidence

| Scenario | Result | Evidence |
| --- | --- | --- |
| Normal code change | PASS | Four minimum roles reach READY_FOR_DECISION |
| Per-task isolation | PASS | Each task has its own AgentResult JSON path |
| Dependency integrity | PASS | Unknown dependencies and cycles are rejected |
| Sensitive work | PASS | Security role selected by risk or path |
| Documentation change | PASS | Documentation role selected by file type |
| Initial implementation fails | PASS | Support records explicit hypothesis |
| Bounded repair | PASS | One configured repair produces failed then passing evidence |
| Repair accounting | PASS | Attempts recorded in plan, evidence, and summary |
| Source protection | PASS | All execution remains in detached worktree |

## Framework decision

The direct orchestrator is the control benchmark, not the final claim that a
framework is unnecessary. LangGraph and OpenAI Agents SDK remain benchmark
candidates. Adoption requires running identical scenarios and comparing code
complexity, recovery behavior, observability, portability, cost, and latency.

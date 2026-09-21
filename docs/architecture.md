# ForgeLab Architecture M0

ForgeLab separates a control plane from execution backends. M0 implements the
portable core: domain contracts, transition policy, artifact persistence, and
configuration. The `Runner` used by the smoke flow is deterministic and does
not execute untrusted code.

The `IsolatedWorkspace` boundary now uses detached Git worktrees. Agent
runtimes must consume `AgentTask` and return
`AgentResult`; they must not own run state, promotion, or evidence policy.

M1 uses a deterministic exact-text developer adapter and an allowlisted Python
test runner. This intentionally narrow slice proves the isolation and evidence
pipeline before natural-language planning or arbitrary tools are introduced.

Promotion remains outside execution workers. A later promote service may act
only when required evidence exists and a `GateDecision` records approval.

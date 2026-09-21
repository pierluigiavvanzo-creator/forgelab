# Decisions

## D-001 Stable contracts before framework adoption

Date: 2026-09-18

Decision: Implement M0 with the Python standard library and stable JSON
contracts. Defer orchestration-framework adoption until M1 benchmarking.

Reason: The control-plane contracts must remain portable across agent runtimes,
LLM providers, execution backends, and user interfaces.

Status: Accepted.

## D-002 Configuration format

Date: 2026-09-18

Decision: Store initial `.yaml` configuration as JSON-compatible YAML 1.2.

Reason: This preserves the specified filenames while allowing deterministic
parsing without a runtime YAML dependency in M0.

Status: Accepted for M0; revisit if human-authored YAML features become useful.

## D-003 Patch artifact before promotion

Date: 2026-09-18

Decision: M1 removes the temporary worktree after verification and persists the
candidate change as `Changes.patch`. It never commits or applies the change to
the source repository.

Reason: This proves isolated execution while keeping promotion as a distinct,
auditable M2 capability guarded by human approval.

Status: Accepted.

## D-011 Local dashboard integration preserves the promotion boundary

Date: 2026-09-19

Decision: Package the Control Plane source with ForgeLab and expose run evidence
through a bearer-authenticated API that binds only to loopback. Dashboard gate
actions write `GateDecision.staged.json`; they never call the promotion service.

Reason: M8 was not reproducible from its ZIP because hidden configuration and
dashboard source were absent. A local connection makes the product usable while
preserving the existing human-controlled promotion boundary.

Status: Accepted.

## D-004 Transactional local promotion

Date: 2026-09-18

Decision: An approved M2 patch may be applied to the reviewed repository working
tree only if HEAD, cleanliness, evidence, review, security, and scope still
match. Tests run again after application. A failed test reverses the patch and
moves the run to repair.

Reason: This creates a useful human-controlled promotion capability without
prematurely granting commit, push, merge, or remote-provider authority.

Status: Accepted.

## D-005 Direct orchestrator as framework benchmark

Date: 2026-09-18

Decision: M3 implements a dependency-checked direct orchestrator with structured
task contracts and per-task results. Security and Documentation are conditional;
Support is instantiated only after a failed test.

Reason: This produces a measurable baseline before adding LangGraph, OpenAI
Agents SDK, or another runtime. Framework adoption must improve capability,
reliability, or development cost without taking ownership of ForgeLab policy.

Status: Accepted.

## D-006 No invented model economics

Date: 2026-09-18

Decision: M4 routes contain configurable provider and model aliases but no
invented token prices. A call is allowed only when the provider returns actual
cost or explicit current pricing is configured. Each route reserves a maximum
call cost before invocation.

Reason: Cost routing is unreliable if model prices are stale, assumed, or
silently treated as zero. A live benchmark requires deliberate provider setup.

Status: Accepted.

## D-007 Deterministic repository memory first

Date: 2026-09-18

Decision: M5 indexes only named canonical repository sources, hashes every
document, always includes mandatory rules and current state when the budget
allows, and selects additional documents by deterministic lexical relevance.

Reason: This produces auditable context selection without a vector database,
embedding cost, hidden retrieval state, or full-repository disclosure. Semantic
retrieval can be benchmarked later if measured recall is insufficient.

Status: Accepted.

## D-008 All agent tools pass through policy gateway

Date: 2026-09-18

Decision: Agent implementations cannot call repository edit or test execution
helpers directly. They must use a gateway that validates role, tool, scope, and
relevant resource policy and records hashed arguments and outcome.

Reason: Policy stored only in configuration is advisory. Enforcement must sit
on the execution boundary, and audit records must remain useful without leaking
command arguments or secret values.

Status: Accepted.

## D-009 Dashboard decisions are staged, not silently promoted

Date: 2026-09-18

Decision: The M7 dashboard may prepare run requests and record Product Owner
gate decisions, but it must not claim to execute a repository promotion until
an authenticated ForgeLab API is connected. Imported evidence remains local to
the browser and decisions are exported as explicit JSON artifacts.

Reason: A useful no-terminal interface can be delivered without weakening the
M2 promotion boundary or inventing a backend connection that does not exist.

Status: Accepted.

## D-010 Scale only behind measured and portable boundaries

Date: 2026-09-18

Decision: M8 begins with evidence-backed KPI collection and stdlib-only local
implementations of the queue, cache, parallel scheduler, and usage meter. Every
stateful lookup is tenant-scoped. Queue work is idempotent, leased, and bounded
by a retry cap. External brokers, managed databases, and billing providers are
deferred until observed demand or cost justifies their integration.

Reason: The specification classifies M8 as an optimization milestone and
requires metrics before scale investment. Stable interfaces preserve a path to
replace SQLite and in-process execution without coupling domain contracts to a
provider.

Status: Accepted.

## D-012 Bounded multi-file AI Developer reuses existing governance boundaries

Date: 2026-09-21

Decision: AI Developer may propose changes to one to three explicitly authorized
files. Multi-file generation uses a machine-structured change list in which
every changed path is independently validated against the authorized path set.
ToolGateway remains the only deterministic write boundary. M8.5 local promotion
is reused unchanged rather than introducing a second promotion mechanism.

Reason: The product needs cross-file implementation capability, but repository-
wide autonomous editing would increase risk without adding proportional product
value. Reusing the existing ToolGateway, deterministic tests, independent review,
human gate, and local promotion path minimizes architectural change while
preserving auditable scope control.

Status: Accepted and validated by M8.6 end-to-end run
`run-c0dcc3b62f29`.


# ForgeLab M8.1

M8.1 repairs the portable distribution: canonical configuration and the
Control Plane source are included, the dashboard can read local run evidence
through a loopback-only authenticated API, and Windows users can validate or
start the product with a single PowerShell command.

```powershell
.\bootstrap.ps1
.\Start-ForgeLab.ps1
```

The first command verifies the complete package. The second starts the local
API and dashboard; its ephemeral token is transferred in the browser URL
fragment and removed by the dashboard after connection.

ForgeLab is a control plane for auditable software work. M1 adds a real,
single-agent isolated runner to the M0 contracts. It accepts a bounded change
request, modifies only a temporary Git worktree, executes an allowlisted test
command, captures a patch, and stops at the human promotion gate.

M2 adds deterministic scope and secret review plus a human decision command.
An approval applies the reviewed patch only when the target repository is still
clean and at the reviewed commit, reruns tests, and rolls back on failure.

M3 adds structured multi-agent orchestration. The direct baseline selects the
minimum applicable roles, executes a dependency graph, stores one result per
task, and uses a bounded diagnostic and repair loop when tests fail.

M4 Core adds deterministic S0-S4 classification, provider-neutral model routes,
budget reservation, bounded retry, token and cost accounting, and a comparable
quality/cost benchmark harness. Live providers remain intentionally unconfigured.

M5 adds repository-backed project memory. Each orchestrated run records a hash
manifest of canonical sources and a query-specific context bundle constrained by
an explicit character budget.

M6 adds enforced tool governance. Repository edits and tests pass through a
role-aware gateway that applies scope, network, dependency, secret, and
destructive-action policies and produces a redacted audit artifact.

M7 adds the private ForgeLab Control Plane for Product Owners. It exposes the
run plan, changes, tests, risk, model usage, decision gate, evidence bundle, and
project memory without requiring terminal access. Until the authenticated API
milestone, the dashboard imports run artifacts locally and exports auditable
`RunRequest.json` and `GateDecision.json` files.

M8 Core adds the measured scale boundary: evidence-backed KPI aggregation,
tenant-isolated durable queue and cache, bounded parallel DAG execution, and an
append-only usage ledger with enforceable run cost caps. The implementation is
stdlib-only and keeps queue, cache, scheduler, and metering interfaces portable.

Inspect current product KPIs from recorded runs:

```bash
PYTHONPATH=src python -m forgelab metrics --runs .forgelab/runs
```

## Run the verified smoke flow

```bash
PYTHONPATH=src python -m forgelab smoke --output .forgelab/runs
python -m unittest discover -s tests -v
```

The smoke command creates a complete synthetic run without calling an LLM or
modifying a repository. It verifies the run state machine and emits:

- `ExecutionPlan.json`
- `AgentResult.json`
- `TestEvidence.json`
- `ReviewReport.json`
- `SecurityReport.json`
- `UsageReport.json`
- `RunSummary.json`
- `GateDecision.json`

The `run` command adds a Git worktree execution path while the deterministic
`smoke` command remains available for contract verification.

## Run an isolated change

Create a request JSON:

```json
{
  "repository": "/absolute/path/to/clean/git/repository",
  "objective": "Fix calculator addition",
  "change": {
    "operation": "replace_text",
    "path": "calculator.py",
    "old": "return a - b",
    "new": "return a + b"
  },
  "test_command": ["python", "-m", "unittest", "discover", "-v"],
  "timeout_seconds": 60
}
```

Then run:

```bash
PYTHONPATH=src python -m forgelab run --request request.json --output .forgelab/runs
```

The source repository must be clean. M1 leaves it unchanged and writes the
candidate change to `Changes.patch` beside the structured run reports.

Review the run artifacts, then record one decision:

```bash
PYTHONPATH=src python -m forgelab decide \
  --run-dir .forgelab/runs/run-123 \
  --repository /absolute/path/to/repository \
  --actor "Product Owner" \
  --decision approve
```

`reject` closes the run without changing the repository. `repair` returns it to
the repair state. `approve` applies the patch to the working tree only after all
quality gates pass; M2 does not create a commit or push a branch.

## Run the structured multi-agent baseline

Use the same request shape as M1 and optionally add `risk`,
`max_repair_attempts`, and `change.initial_new` for a controlled repair
benchmark:

```bash
PYTHONPATH=src python -m forgelab orchestrate \
  --request request.json \
  --output .forgelab/runs
```

Every task writes `tasks/<task_id>/AgentResult.json`. The aggregate plan records
the selected roles, dependency edges, limits, and selection reason.

## Inspect a route without calling a model

Create a task profile such as:

```json
{"implementation": true, "cross_component_count": 2}
```

Then run:

```bash
PYTHONPATH=src python -m forgelab route --profile profile.json
```

The command reports the S0-S4 class, provider slot, model alias, retry limit,
maximum reserved call cost, and human-review requirement. It never calls a
provider.

## Build and select project memory

```bash
PYTHONPATH=src python -m forgelab memory-snapshot \
  --root /path/to/project --output MemorySnapshot.json

PYTHONPATH=src python -m forgelab memory-select \
  --root /path/to/project --query "authentication decision" \
  --max-chars 20000 --output ContextBundle.json
```

Canonical sources include root project rules and state, architecture, contracts,
ADRs, current handover, and acceptance reports. Symlinks, oversized files, path
escapes, and likely embedded secrets are rejected.

## Current boundary

Implemented: contracts, validation, transition rules, JSON artifact store,
default policies, project memory, deterministic smoke run, isolated Git
worktree, one exact-text edit operation, bounded Python test execution, patch
capture, and integrity verification of the source repository.
M2 also implements deterministic review, secret scanning, persistent human gate
decisions, stale-base protection, post-promotion tests, and rollback.
M3 implements PM, Developer, Tester, Reviewer, conditional Security and
Documentation roles, and on-demand Support during repair.
M4 Core implements provider adapters as a protocol, route configuration, usage
ledger, budget enforcement, retry evidence, pricing validation, and benchmarks.
M5 implements memory discovery, content hashes, deterministic manifests,
relevance selection, mandatory context, and per-run memory artifacts.
M6 implements role permissions, path scope enforcement, network default-deny,
secret handles, dependency evidence, destructive gates, and tool audit.
M7 implements the Product Owner dashboard, local evidence import, run-request
preparation, gate-decision capture, evidence inspection, and project memory.
M8 Core implements KPI measurement, tenant isolation, idempotent leased work,
bounded retry, cache expiry, parallel dependency layers, and usage cost caps.

Not yet implemented: natural-language planning, LLM provider integration,
container/cloud sandbox, authenticated dashboard API, LLM-backed repair, commit/PR creation,
remote promotion, distributed task queue, live provider adapters, or live
quality/cost benchmarks. Production billing and horizontal workers remain
deferred until demand metrics justify them. Semantic retrieval is also deferred until
measured against the deterministic selector.

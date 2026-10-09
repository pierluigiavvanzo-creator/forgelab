# ForgeLab

ForgeLab is a governed software-development control plane.

Core workflow:

Objective → repository context → plan → isolated implementation → deterministic tests → bounded repair → independent review → security → READY_FOR_DECISION → Product Owner approval → exact reviewed promotion.

## Status

PRE-MVP / Golden Path validation active.

ForgeLab has a substantial technical control plane, but the first real external-product Golden Path (Dental Quote) is still NOT PASS. Technical test success must not be reported as product or market validation.

Canonical project state:
- PROJECT_STATE.md
- ROADMAP.md
- DECISIONS.md
- docs/handovers/HANDOVER_CURRENT.md

## Local stack

- Windows 11
- Python 3.11+
- Node >= 22.13
- pnpm 11.25.0
- Aider 0.86.2 in an isolated local tool environment
- Ollama on loopback
- dashboard + authenticated local API

Start:

    .\Start-ForgeLab.ps1

Default endpoints:
- API: http://127.0.0.1:8765
- dashboard: http://127.0.0.1:5173

The launcher generates an authenticated dashboard URL and performs the focused stabilization/readiness checks before reporting ready.

## Validation

Full Python regression:

    py -3.11 -m unittest discover -s tests -p "test*.py" -v

Repository validation helper:

    .\Validate-ForgeLab.ps1

Dashboard lifecycle:

    node dashboard\scripts\test-run-lifecycle.mjs

Dashboard production build:

    cd dashboard
    corepack pnpm install --frozen-lockfile
    corepack pnpm run build

The launcher intentionally executes a focused Python subset; its 108 Python checks are not the full suite.

## Governance

Read AGENTS_MASTER.md and AGENTS.md before material repository changes.

Key rules:
- GitHub main is canonical shared source;
- reuse first;
- zero-cost API/token first;
- execution agents do not write directly to protected source;
- writes remain scope-bounded;
- deterministic verification precedes acceptance;
- Reviewer and Security remain independent gates;
- promotion requires explicit Product Owner approval;
- no automatic merge or unapproved paid fallback.

## Repository hygiene

Generated/runtime state is ignored:
- .forgelab/runs
- .forgelab/runtime
- .forgelab/tools
- dashboard/node_modules
- dashboard/dist
- dashboard/.wrangler
- dashboard/.sites-runtime

These local directories can outweigh the tracked repository by orders of magnitude and must be measured separately when auditing local disk usage.

Historical implementation detail belongs in Git history, DECISIONS.md, ADRs and focused audit reports rather than being copied indefinitely into every canonical file.

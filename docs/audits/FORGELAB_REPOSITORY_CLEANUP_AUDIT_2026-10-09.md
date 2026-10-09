# ForgeLab repository cleanup audit — 2026-10-09

## Scope

Repository:
pierluigiavvanzo-creator/forgelab

Baseline main:
1d7024f46d03709587913b3e4905d0b324ae7f40

Work class:
C — optimization / bounded technical cleanup.

Goal:
reduce live-tree weight, obsolete surfaces and repeated canonical history without changing production behavior or erasing Git history.

No merge is authorized by this audit.

## Baseline tracked size

Recursive Git tree on main:

- tracked blobs: 125
- tracked bytes: 1,613,850 B (~1.54 MiB)
- GitHub repository metadata size observed during audit: 1,367 KiB
- exact duplicate blob SHA groups: 0

Tracked bytes by top-level area:

| Area | Bytes |
| --- | ---: |
| dashboard | 522,972 |
| src | 373,726 |
| tests | 349,230 |
| docs | 174,525 |
| PROJECT_STATE.md | 57,840 |
| AGENTS_MASTER.md | 43,449 |
| DECISIONS.md | 38,318 |
| Start-ForgeLab.ps1 | 17,794 |
| MANIFEST.md | 9,425 |
| ROADMAP.md | 8,733 |

Largest individual tracked files:

| File | Bytes |
| --- | ---: |
| dashboard/pnpm-lock.yaml | 342,352 |
| src/forgelab/orchestrator.py | 210,032 |
| tests/test_orchestrator.py | 198,129 |
| dashboard/app/page.tsx | 82,427 |
| PROJECT_STATE.md | 57,840 |
| tests/test_api.py | 50,207 |
| src/forgelab/api.py | 48,448 |
| AGENTS_MASTER.md | 43,449 |
| DECISIONS.md | 38,318 |
| tests/test_editor_adapter.py | 33,135 |
| docs/handovers/HANDOVER_CURRENT.md | 31,435 |

The 342 KB pnpm lockfile is large but required for deterministic dependency resolution and is retained.

## Baseline test inventory

Static count of Python test_* definitions on main:

| File | Tests |
| --- | ---: |
| tests/test_orchestrator.py | 51 |
| tests/test_api.py | 26 |
| tests/test_editor_adapter.py | 20 |
| tests/test_model_router.py | 16 |
| tests/test_dashboard_run_form_feedback.py | 11 |
| tests/test_governance.py | 9 |
| tests/test_promote.py | 8 |
| tests/test_memory.py | 6 |
| tests/test_ollama_provider.py | 6 |
| tests/test_editor_bakeoff.py | 5 |
| tests/test_dashboard_gate_evidence.py | 3 |
| tests/test_dashboard_human_repair.py | 3 |
| tests/test_runner.py | 3 |
| tests/test_domain.py | 2 |
| tests/test_package_integrity.py | 2 |
| tests/test_patch_artifact_bytes.py | 2 |
| tests/test_quality.py | 2 |
| tests/test_state_machine.py | 2 |
| tests/test_config.py | 1 |
| tests/test_smoke.py | 1 |
| tests/test_telemetry.py | 1 |

Totals:
- Python test files: 21
- Python tests: 180
- Python test source lines: 10,713
- Python test tracked bytes: 349,230
- Node dashboard lifecycle tests: 4
- named test/check cases: 184

Start-ForgeLab.ps1 runs a focused stabilization subset:
- test_editor_adapter: 20
- test_orchestrator: 51
- test_api: 26
- test_dashboard_run_form_feedback: 11
- focused Python total: 108
- Node lifecycle: 4

Therefore prior 108-test launcher reports are not full-suite counts.

## High-confidence removable material

### Dashboard starter residue

Removed:
- dashboard/README.md
- dashboard/SITE_SOURCE.md
- dashboard/public/file.svg
- dashboard/public/globe.svg
- dashboard/public/window.svg

Reason:
generic starter documentation/assets are not part of current ForgeLab UI. The active layout references favicon.svg, which is retained.

### Obsolete npm installation path

Removed:
- dashboard/scripts/install-ci.sh
- dashboard/scripts/install-ci.mjs

Reason:
pnpm 11.25.0 is the canonical package manager. package.json install:ci points to install-pnpm.sh and Start-ForgeLab.ps1 uses corepack pnpm install --frozen-lockfile. The removed npm installer expected package-lock.json, which is absent.

Retained:
- install-pnpm.sh
- pnpm-install.mjs
- sites-env.sh/.mjs
- run-framework.mjs
- build-verified.sh
- pnpm-lock.yaml

### Completed editor bakeoff surface

Removed:
- src/forgelab/editor_bakeoff.py
- tests/test_editor_bakeoff.py
- docs/experiments/EDITOR_ENGINE_BAKEOFF_01.md
- editor-bakeoff CLI import/subcommand/handler

Reason:
the experiment served the architecture reset that selected Aider. Aider is now integrated into the real runtime. The historical decision remains available through ADR/audits/Git history.

### Unused benchmark module

Removed:
- src/forgelab/benchmark.py

Reason:
no active CLI path or production import uses this generic benchmark helper.

### Historical milestone acceptance reports

Removed from current tree:
M1, M2, M3, M4 core, M5, M6, M7, M8, M8.1 and M8.6 acceptance reports.

Reason:
they are historical milestone snapshots, are not referenced by current canonical project files, and remain recoverable from Git history. Current validated constraints are retained in MANIFEST/DECISIONS/ADRs/audits.

## Canonical-document compaction

PROJECT_STATE.md and HANDOVER_CURRENT.md had become cumulative historical logs rather than current-state documents. They duplicated large amounts of audit and decision history and contained stale merge instructions.

This cleanup replaces repeated historical sections with:
- current product state;
- material merged protections;
- current blocker;
- test/size baseline;
- explicit pointers to focused audits and Git history.

ROADMAP.md, README.md and AGENTS.md are likewise aligned to current state.

DECISIONS.md and AGENTS_MASTER.md are deliberately retained because they are the durable decision/governance record.

## Material not removed

### pnpm-lock.yaml

Retained because deterministic frontend dependency resolution depends on it.

### Current root-cause audits / ADRs

Retained because they document active architectural protections and the reasoning behind PR #68/#69/#70.

### Runtime code and core tests

No production orchestrator/API/editor/provider/security/promotion module is removed by the cleanup.

### Dashboard direct dependencies

package.json appears to retain multiple starter-era direct dependencies not referenced by the current dashboard source. They may dominate local node_modules weight, but removing them safely requires regeneration of pnpm-lock.yaml plus a clean production build. This audit does not guess-edit the lockfile. Treat dependency slimming as a separate validated optimization only if local disk/startup cost justifies it.

## Local disk versus tracked repository

GitHub tree size does not include ignored local state.

Potentially much larger local paths include:
- dashboard/node_modules
- dashboard/dist
- dashboard/.wrangler
- dashboard/.sites-runtime
- .forgelab/tools/aider-0.86.2
- .forgelab/runs
- .forgelab/runtime
- Ollama model storage outside the repository

Do not delete .forgelab/runs/runtime while a run is active or when evidence is still required. Do not delete the pinned Aider toolchain if the next launch would simply reinstall it.

A separate local disk audit is required to report actual on-disk GB.

## Expected test inventory after cleanup

Removing tests/test_editor_bakeoff.py removes 5 experiment-only tests.

Expected after cleanup:
- Python test files: 20
- Python tests: 175
- Node lifecycle tests: 4
- named test/check cases: 179

The focused 108-test launcher subset is unchanged because test_editor_bakeoff.py was not part of that subset.

## Validation required before merge

Because GitHub has no active remote CI workflow for this repository, cleanup must not be called PASS until a clean Windows checkout/branch executes:

1. py -3.11 -m unittest discover -s tests -p "test*.py" -v
2. node dashboard/scripts/test-run-lifecycle.mjs
3. corepack pnpm install --frozen-lockfile
4. corepack pnpm run build
5. launcher readiness/stability or equivalent bounded smoke

Expected:
- 175 Python tests discovered and PASS;
- 4 dashboard lifecycle tests PASS;
- production dashboard build PASS;
- no missing import/CLI regression;
- source tree clean after tests.

## Decision

Cleanup candidate: REVIEW REQUIRED.

It removes high-confidence obsolete/current-tree material while preserving historical recoverability in Git.

It must not be merged until validation evidence is attached and Product Owner explicitly approves.

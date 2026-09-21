# Roadmap

| Milestone | Status | Exit condition |
| --- | --- | --- |
| M0 Repo and contracts | Implemented | Contracts validate and smoke CLI emits mandatory artifacts |
| M1 Isolated runner | Implemented | Demo repository is modified only in an isolated Git worktree, tested, and reported |
| M2 Quality and promote gate | Implemented | Target cannot change without recorded approval and post-promotion verification |
| M3 Multi-agent orchestration | Implemented | PM, Developer, Tester, and Reviewer cooperate through structured artifacts |
| M4 Model router | Core implemented | Provider-neutral routing, budget controls, and benchmark harness available |
| M5 Project memory | Implemented | Context is reconstructed from canonical repository state |
| M6 Security governance | Implemented | Tool, secret, network, dependency, and destructive-action policies are enforced |
| M7 Product dashboard | Implemented | Product Owner can inspect evidence and operate governed local runs |
| M8 Optimization and scale | Core implemented | KPI, bounded DAG scheduling, tenant-isolated cache/queue, and metering verified |
| M8.1 Package repair | Implemented | Package contains config, dashboard source, local API, startup flow, and integrity checks |
| M8.3A Local AI Runtime | PASS | Ollama local runtime available with `qwen2.5-coder:7b` |
| M8.3B Router + Orchestrator local AI | PASS | Local AI can be routed through the governed orchestrator |
| M8.3C Dashboard local-AI integration | PASS | Dashboard can start and inspect local-AI runs |
| M8.4A Objective-only AI Developer backend | PASS | Objective can generate a bounded structured single-file patch |
| M8.4B AI Developer dashboard mode | PASS | Product Owner can create AI Developer runs from the browser |
| M8.4B.1 Windows Python UX normalization | PASS | Windows `py -3.11` path works in the supported local flow |
| M8.5 Human-approved local promotion | PASS | Explicit approval promotes reviewed patch to a dedicated local branch and commit |
| M8.5.1 UTF-8/BOM promotion hotfix | PASS | UTF-8/BOM patch capture and promotion regression passes |
| M8.6 Multi-file AI Developer | PASS | Browser run modifies 2 authorized files, tests/review pass, human-approved local promotion creates one commit with no push/merge |

## Single next action

### M8.7 — Bounded AI Developer repair for `ai_generate`

Extend the existing hypothesis-driven repair path so an AI Developer run whose deterministic test fails can perform a bounded AI-assisted repair without expanding the authorized file set.

Exit target:

- initial AI-generated 2-file patch reaches a deterministic test failure;
- Support produces a new evidence-backed hypothesis;
- Developer receives at most the configured bounded repair budget;
- repair proposal may touch only the original authorized paths;
- unauthorized path expansion is rejected;
- deterministic tests rerun and become authoritative;
- independent review remains mandatory;
- run stops at `READY_FOR_DECISION`;
- promotion remains one-shot human-approved, local-only, with no automatic push/merge/force.

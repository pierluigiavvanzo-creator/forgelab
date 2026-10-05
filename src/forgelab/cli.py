from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .smoke import run_smoke
from .runner import RunRequest, run_isolated
from .promote import decide
from .orchestrator import MultiAgentRequest, run_multi_agent
from .model_router import TaskProfile, classify, load_routes
from .memory import ProjectMemory, write_json
from .telemetry import collect_kpis
from .api import serve
from .editor_bakeoff import EditorBakeoffRequest, run_editor_bakeoff


def main() -> int:
    parser = argparse.ArgumentParser(prog="forgelab")
    sub = parser.add_subparsers(dest="command", required=True)
    smoke = sub.add_parser("smoke", help="run the deterministic M0 smoke flow")
    smoke.add_argument("--output", type=Path, default=Path(".forgelab/runs"))
    run = sub.add_parser("run", help="run an M1 change in an isolated Git worktree")
    run.add_argument("--request", type=Path, required=True)
    run.add_argument("--output", type=Path, default=Path(".forgelab/runs"))
    gate = sub.add_parser("decide", help="record a human gate decision and optionally promote")
    gate.add_argument("--run-dir", type=Path, required=True)
    gate.add_argument("--repository", type=Path, required=True)
    gate.add_argument("--actor", required=True)
    gate.add_argument("--decision", choices=("approve", "reject", "repair"), required=True)
    orchestrate = sub.add_parser("orchestrate", help="run the M3 structured multi-agent baseline")
    orchestrate.add_argument("--request", type=Path, required=True)
    orchestrate.add_argument("--output", type=Path, default=Path(".forgelab/runs"))
    route = sub.add_parser("route", help="classify a task and inspect its configured model route")
    route.add_argument("--profile", type=Path, required=True)
    route.add_argument("--config", type=Path, default=Path(".forgelab/routing.yaml"))
    memory_snapshot = sub.add_parser("memory-snapshot", help="index canonical repository memory")
    memory_snapshot.add_argument("--root", type=Path, required=True)
    memory_snapshot.add_argument("--output", type=Path, required=True)
    memory_select = sub.add_parser("memory-select", help="select relevant canonical context")
    memory_select.add_argument("--root", type=Path, required=True)
    memory_select.add_argument("--query", required=True)
    memory_select.add_argument("--max-chars", type=int, default=20000)
    memory_select.add_argument("--output", type=Path, required=True)
    metrics = sub.add_parser("metrics", help="aggregate evidence-backed product KPIs")
    metrics.add_argument("--runs", type=Path, default=Path(".forgelab/runs"))
    metrics.add_argument("--output", type=Path)
    api = sub.add_parser("api", help="serve run evidence to the local Control Plane")
    api.add_argument("--runs", type=Path, default=Path(".forgelab/runs"))
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8765)
    api.add_argument("--allowed-origin", default="http://localhost:5173")
    api.add_argument("--token-env", default="FORGELAB_API_TOKEN")
    editor_bakeoff = sub.add_parser(
        "editor-bakeoff",
        help="run the bounded reusable-editor experiment",
    )
    editor_bakeoff.add_argument("--request", type=Path, required=True)
    editor_bakeoff.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "smoke":
        print(run_smoke(args.output))
        return 0
    if args.command == "run":
        print(run_isolated(RunRequest.from_json(args.request), args.output))
        return 0
    if args.command == "decide":
        result = decide(args.run_dir, args.repository, args.actor, args.decision)
        print(f"{result['status']}: {result['decision']}")
        return 0
    if args.command == "orchestrate":
        print(run_multi_agent(MultiAgentRequest.from_json(args.request), args.output))
        return 0
    if args.command == "route":
        profile = TaskProfile(**json.loads(args.profile.read_text(encoding="utf-8")))
        task_class = classify(profile)
        selected = load_routes(args.config)[task_class]
        print(json.dumps({
            "task_class": task_class.value, "provider": selected.provider,
            "model": selected.model, "max_retries": selected.max_retries,
            "max_call_cost": str(selected.max_call_cost),
            "human_review_required": selected.human_review_required,
        }, indent=2))
        return 0
    if args.command == "memory-snapshot":
        write_json(args.output, ProjectMemory(args.root).snapshot())
        print(args.output)
        return 0
    if args.command == "memory-select":
        write_json(args.output, ProjectMemory(args.root).select(args.query, args.max_chars))
        print(args.output)
        return 0
    if args.command == "metrics":
        report = collect_kpis(args.runs)
        if args.output:
            write_json(args.output, report)
            print(args.output)
        else:
            print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "api":
        token = os.environ.get(args.token_env)
        if not token:
            parser.error(f"environment variable {args.token_env} is required")
        serve(args.runs, token, args.allowed_origin, args.host, args.port)
        return 0
    if args.command == "editor-bakeoff":
        report = run_editor_bakeoff(
            EditorBakeoffRequest.from_json(args.request),
            args.output,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

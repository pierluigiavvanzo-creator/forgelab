from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_kpis(run_root: Path) -> dict[str, Any]:
    """Aggregate only evidence-backed fields; unavailable KPIs stay explicit."""
    runs=[]
    for summary_path in sorted(run_root.glob("*/RunSummary.json")):
        run_dir=summary_path.parent
        try:
            summary=_read(summary_path); usage=_read(run_dir/"UsageReport.json"); gate=_read(run_dir/"GateDecision.json")
        except (OSError, json.JSONDecodeError):
            continue
        runs.append((summary,usage,gate))
    total=len(runs); done=sum(1 for s,_,_ in runs if s.get("status")=="DONE")
    decision_ready=sum(1 for s,_,_ in runs if s.get("status") in {"READY_FOR_DECISION","DONE"})
    repairs=[int(s.get("repair_attempts",0)) for s,_,_ in runs]
    repair_runs=sum(1 for x in repairs if x>0)
    premium_cost=sum(float(u.get("premium_cost",0) or 0) for _,u,_ in runs)
    total_cost=sum(float(u.get("actual_cost",u.get("estimated_cost",0)) or 0) for _,u,_ in runs)
    human_touches=sum(1 for _,_,g in runs if g.get("decision") not in {None,"PENDING","REPAIR"})
    return {
        "run_count":total,
        "run_success_rate":done/total if total else None,
        "decision_ready_rate":decision_ready/total if total else None,
        "user_touches_per_run":human_touches/total if total else None,
        "premium_cost_share":premium_cost/total_cost if total_cost else 0.0,
        "repair_run_rate":repair_runs/total if total else None,
        "average_repair_attempts":sum(repairs)/total if total else None,
        "total_recorded_cost":total_cost,
        "unavailable":{"time_to_usable_output":"timestamps not yet complete","reuse_ratio":"benchmark adoption events not yet emitted","escape_defects":"post-promotion incident feed not connected","economic_contribution":"requires Product Owner attribution"},
    }

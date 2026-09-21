from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


MANDATORY_ARTIFACTS = (
    "ExecutionPlan.json",
    "AgentResult.json",
    "TestEvidence.json",
    "ReviewReport.json",
    "SecurityReport.json",
    "UsageReport.json",
    "RunSummary.json",
    "GateDecision.json",
)

OPTIONAL_ARTIFACTS = ("Changes.patch",)
OPTIONAL_JSON_ARTIFACTS = ("MemorySnapshot.json", "ContextBundle.json", "ToolAudit.json", "PromotionResult.json")


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self, name: str, payload: dict[str, Any]) -> Path:
        if name not in MANDATORY_ARTIFACTS:
            raise ValueError(f"unsupported artifact: {name}")
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / name
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(target)
        return target

    def write_text(self, name: str, content: str) -> Path:
        if name not in OPTIONAL_ARTIFACTS:
            raise ValueError(f"unsupported text artifact: {name}")
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / name
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_bytes(content.encode("utf-8"))
        temporary.replace(target)
        return target

    def write_optional_json(self, name: str, payload: dict[str, Any]) -> Path:
        if name not in OPTIONAL_JSON_ARTIFACTS and name not in {"AIPlan.json", "AIDiagnostics.json", "AIReview.json", "AIDeveloperPatch.json"}:
            raise ValueError(f"unsupported optional JSON artifact: {name}")
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / name
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(target)
        return target

    def missing(self) -> list[str]:
        return [name for name in MANDATORY_ARTIFACTS if not (self.root / name).is_file()]

    def write_task_result(self, task_id: str, payload: dict[str, Any]) -> Path:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", task_id):
            raise ValueError("invalid task id")
        target = self.root / "tasks" / task_id / "AgentResult.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(target)
        return target

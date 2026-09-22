from __future__ import annotations

from dataclasses import dataclass

from .model_router import ModelRouter, TaskClass


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    task_class: TaskClass
    prompt: str
    expected_substring: str
    agent_role: str = "BENCHMARK"


def run_benchmark(router: ModelRouter, cases: list[BenchmarkCase]) -> dict[str, object]:
    results = []
    for case in cases:
        response = router.execute(
            case.task_class, case.prompt, case.case_id, case.agent_role,
            "Fixed benchmark route for comparable quality and cost measurement",
        )
        passed = case.expected_substring in response.text
        results.append({"case_id": case.case_id, "passed": passed, "output": response.text})
    passed_count = sum(item["passed"] for item in results)
    return {
        "cases": len(cases), "passed": passed_count,
        "quality_rate": passed_count / len(cases) if cases else 0.0,
        "cost": str(router.ledger.spent), "results": results,
    }

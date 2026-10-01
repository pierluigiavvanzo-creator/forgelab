import json
from decimal import Decimal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from forgelab.domain import Role
from forgelab.model_router import ProviderResponse
from forgelab.orchestrator import MultiAgentRequest, TaskGraphError, run_multi_agent, select_roles, validate_task_graph
from forgelab.promote import decide


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return result.stdout.strip()


def make_demo(root: Path) -> Path:
    repo = root / "demo"
    repo.mkdir()
    (repo / "calculator.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    (repo / "test_calculator.py").write_text(
        "import unittest\nfrom calculator import add\n\n"
        "class T(unittest.TestCase):\n    def test_add(self): self.assertEqual(add(2, 3), 5)\n",
        encoding="utf-8",
    )
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@local", "commit", "-m", "demo"],
        check=True, capture_output=True,
    )
    return repo




def make_multi_demo(root: Path) -> Path:
    repo = root / "multi-demo"
    repo.mkdir()
    (repo / "calculator.py").write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )
    (repo / "operation.py").write_text(
        'OPERATION = "subtract"\n',
        encoding="utf-8",
    )
    (repo / "test_calculator.py").write_text(
        "import unittest\n"
        "from calculator import add\n"
        "from operation import OPERATION\n\n"
        "class T(unittest.TestCase):\n"
        "    def test_add(self): self.assertEqual(add(2, 3), 5)\n"
        '    def test_operation(self): self.assertEqual(OPERATION, "add")\n',
        encoding="utf-8",
    )
    git(repo, "init", "-b", "main")
    git(repo, "add", ".")
    subprocess.run(
        [
            "git", "-C", str(repo),
            "-c", "user.name=Test",
            "-c", "user.email=test@local",
            "commit", "-m", "multi-demo",
        ],
        check=True,
        capture_output=True,
    )
    return repo

def request(repo: Path, **overrides) -> MultiAgentRequest:
    values = {
        "repository": repo, "objective": "Fix addition", "target_path": "calculator.py",
        "old_text": "return a - b", "new_text": "return a + b",
        "test_command": [sys.executable, "-m", "unittest", "discover", "-v"],
    }
    values.update(overrides)
    return MultiAgentRequest(**values)



def ai_plan(
    acceptance_criteria: list[str] | None = None,
) -> str:
    criteria = acceptance_criteria or [
        "Implement the requested objective.",
        "Add or update deterministic tests for the requested behavior.",
    ]
    return json.dumps({
        "schema_version": "1.0",
        "intended_outcome": "Deliver the requested bounded change.",
        "execution_steps": [
            "Inspect authorized files.",
            "Implement the smallest sufficient change.",
            "Run deterministic tests.",
        ],
        "acceptance_criteria": criteria,
        "principal_risks": [
            "Do not expand authorized write scope.",
        ],
    })


def semantic_review_pass() -> str:
    return json.dumps({
        "schema_version": "1.0",
        "status": "PASS",
        "summary": "All explicit objective requirements are evidenced.",
        "requirements": [
            {
                "requirement": "Requested objective is implemented",
                "status": "SATISFIED",
                "evidence": "Patch and tests provide direct evidence",
            },
        ],
        "findings": [],
    })


def semantic_review_fail(
    requirement: str,
    description: str,
) -> str:
    return json.dumps({
        "schema_version": "1.0",
        "status": "FAIL",
        "summary": "The candidate misses required behavior.",
        "requirements": [
            {
                "requirement": requirement,
                "status": "MISSING",
                "evidence": description,
            },
        ],
        "findings": [
            {
                "severity": "BLOCKER",
                "category": "objective_coverage",
                "description": description,
            },
        ],
    })


def add_m88_context(repo: Path, marker: str = "M88_SHARED_CONTEXT_MARKER") -> None:
    (repo / "AGENTS.md").write_text(
        f"# Rules\n{marker}\nRead context; do not expand write scope.\n",
        encoding="utf-8",
    )
    (repo / "PROJECT_STATE.md").write_text(
        "# State\nAddition policy is active.\n",
        encoding="utf-8",
    )
    (repo / "operation_policy.py").write_text(
        'ADD_OPERATION = "addition"\nARITHMETIC_OPERATOR = "+"\n',
        encoding="utf-8",
    )
    runtime = repo / ".forgelab" / "runtime"
    runtime.mkdir(parents=True)
    (runtime / "operation_runtime.txt").write_text(
        "operation policy runtime content must never enter model context\n",
        encoding="utf-8",
    )
    notes = repo / "notes"
    notes.mkdir()
    (notes / "operation_secret.txt").write_text(
        'operation policy api_key="abcdefghijklmnop1234"\n',
        encoding="utf-8",
    )
    git(repo, "add", ".")
    subprocess.run(
        [
            "git", "-C", str(repo),
            "-c", "user.name=Test",
            "-c", "user.email=test@local",
            "commit", "-m", "add m8.8 context",
        ],
        check=True,
        capture_output=True,
    )


class MultiAgentTests(unittest.TestCase):
    def test_cyclic_task_graph_is_rejected(self):
        tasks = [
            {"task_id": "a", "dependencies": ["b"]},
            {"task_id": "b", "dependencies": ["a"]},
        ]
        with self.assertRaises(TaskGraphError):
            validate_task_graph(tasks)

    def test_unknown_dependency_is_rejected(self):
        with self.assertRaises(TaskGraphError):
            validate_task_graph([{"task_id": "a", "dependencies": ["missing"]}])

    def test_minimum_roles_complete_through_structured_results(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)
            run_dir = run_multi_agent(request(repo), root / "runs")
            summary = json.loads((run_dir / "RunSummary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "READY_FOR_DECISION")
            self.assertEqual(summary["selected_roles"], ["PROJECT_MANAGER", "DEVELOPER", "TESTER", "REVIEWER"])
            for task_id in ("plan", "implement", "test", "review"):
                self.assertTrue((run_dir / "tasks" / task_id / "AgentResult.json").is_file())
            usage = json.loads((run_dir / "UsageReport.json").read_text(encoding="utf-8"))
            self.assertEqual(usage["llm_calls"], 0)
            self.assertTrue(all(item["task_class"] == "S0" for item in usage["routing_decisions"]))
            self.assertTrue((run_dir / "MemorySnapshot.json").is_file())
            self.assertTrue((run_dir / "ContextBundle.json").is_file())
            audit = json.loads((run_dir / "ToolAudit.json").read_text(encoding="utf-8"))
            self.assertEqual(audit["denied_count"], 0)
            self.assertGreaterEqual(audit["event_count"], 2)
            self.assertEqual(git(repo, "status", "--porcelain"), "")

    def test_failed_candidate_uses_one_hypothesis_driven_repair(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)
            run_dir = run_multi_agent(request(repo, initial_new_text="return a * b"), root / "runs")
            summary = json.loads((run_dir / "RunSummary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "READY_FOR_DECISION")
            self.assertEqual(summary["repair_attempts"], 1)
            self.assertIn("SUPPORT", summary["selected_roles"])
            self.assertTrue((run_dir / "tasks" / "support-1" / "AgentResult.json").is_file())
            evidence = json.loads((run_dir / "TestEvidence.json").read_text(encoding="utf-8"))
            self.assertEqual([item["exit_status"] for item in evidence["evidence"] if item["check_type"] == "tests"], [1, 0])

    def test_m88_repository_context_is_bounded_read_only_and_does_not_expand_write_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)
            add_m88_context(repo)

            developer_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a + b",
                "summary": "Apply addition policy",
            })
            scripted = [
                ProviderResponse(ai_plan(), 10, 5, actual_cost=Decimal("0")),
                ProviderResponse(developer_patch, 30, 20, actual_cost=Decimal("0")),
                ProviderResponse(semantic_review_pass(), 12, 6, actual_cost=Decimal("0")),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective="Fix addition using operation policy",
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=0,
                    ),
                    root / "runs",
                )

            context = json.loads(
                (run_dir / "ContextBundle.json").read_text(encoding="utf-8")
            )
            plan = json.loads(
                (run_dir / "ExecutionPlan.json").read_text(encoding="utf-8")
            )
            developer = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(encoding="utf-8")
            )

            self.assertEqual(context["mode"], "read_only")
            self.assertFalse(context["write_scope_expansion"])
            self.assertLessEqual(context["used_chars"], context["max_chars"])
            self.assertLessEqual(context["repository_document_count"], 8)
            self.assertIn("AGENTS.md", context["selected_paths"])
            self.assertIn("PROJECT_STATE.md", context["selected_paths"])
            self.assertIn("operation_policy.py", context["selected_paths"])
            self.assertNotIn("calculator.py", context["selected_paths"])
            self.assertNotIn(".forgelab/runtime/operation_runtime.txt", context["selected_paths"])
            self.assertNotIn("notes/operation_secret.txt", context["selected_paths"])
            self.assertGreaterEqual(context["excluded_summary"]["potential_secret"], 1)

            self.assertEqual(plan["allowed_paths"], ["calculator.py"])
            implement = next(task for task in plan["tasks"] if task["task_id"] == "implement")
            self.assertEqual(implement["scope"]["allowed_paths"], ["calculator.py"])
            self.assertEqual(
                implement["inputs"]["relevant_context"],
                {
                    "artifact_ref": "ContextBundle.json",
                    "mode": "read_only",
                    "write_scope_expansion": False,
                },
            )
            self.assertEqual(
                developer["context_selection_sha256"],
                context["selection_sha256"],
            )

            prompts = [call.args[1] for call in invoke.call_args_list]
            self.assertIn("M88_SHARED_CONTEXT_MARKER", prompts[0])
            self.assertIn("M88_SHARED_CONTEXT_MARKER", prompts[1])
            self.assertIn("operation_policy.py", prompts[1])
            self.assertNotIn("operation_runtime.txt", prompts[1])
            self.assertNotIn("abcdefghijklmnop1234", prompts[1])
            self.assertEqual(git(repo, "status", "--porcelain"), "")


    def test_security_role_is_selected_only_for_sensitive_work(self):
        normal = request(Path("/tmp/repo"))
        high = request(Path("/tmp/repo"), risk="high")
        self.assertNotIn(Role.SECURITY, select_roles(normal))
        self.assertIn(Role.SECURITY, select_roles(high))

    def test_documentation_role_is_selected_by_file_type(self):
        docs = request(Path("/tmp/repo"), target_path="README.md")
        self.assertIn(Role.DOCUMENTATION, select_roles(docs))

    def test_m3_candidate_remains_compatible_with_m2_human_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)
            run_dir = run_multi_agent(request(repo), root / "runs")
            source_head = git(repo, "rev-parse", "HEAD")
            result = decide(run_dir, repo, "Sergio", "approve")
            self.assertEqual(result["status"], "DONE")
            self.assertEqual(git(repo, "branch", "--show-current"), "main")
            self.assertEqual(git(repo, "rev-parse", "HEAD"), source_head)
            branch = f"forgelab/promote/{run_dir.name}"
            self.assertIn("return a + b", git(repo, "show", f"{branch}:calculator.py"))



    def test_request_json_accepts_utf8_bom(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)
            request_path = root / "request.json"

            payload = {
                "repository": str(repo),
                "objective": "Fix addition",
                "change": {
                    "operation": "replace_text",
                    "path": "calculator.py",
                    "old": "return a - b",
                    "new": "return a + b",
                },
                "test_command": [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ],
            }

            request_path.write_text(
                json.dumps(payload),
                encoding="utf-8-sig",
            )

            parsed = MultiAgentRequest.from_json(request_path)

            self.assertEqual(parsed.repository, repo)
            self.assertEqual(parsed.target_path, "calculator.py")
            self.assertEqual(parsed.old_text, "return a - b")
            self.assertEqual(parsed.new_text, "return a + b")


    def test_live_ai_mode_uses_real_router_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ):
                run_dir = run_multi_agent(
                    request(
                        repo,
                        ai_mode=True,
                    ),
                    root / "runs",
                )

            usage = json.loads(
                (
                    run_dir /
                    "UsageReport.json"
                ).read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                usage["runtime"],
                "hybrid_local_ai",
            )

            self.assertEqual(
                usage["llm_calls"],
                2,
            )

            self.assertEqual(
                usage["spent"],
                "0",
            )

            self.assertTrue(
                (
                    run_dir /
                    "AIPlan.json"
                ).is_file()
            )

            self.assertTrue(
                (
                    run_dir /
                    "AIReview.json"
                ).is_file()
            )

            self.assertEqual(
                git(
                    repo,
                    "status",
                    "--porcelain",
                ),
                "",
            )



    def test_ai_developer_generates_patch_without_user_solution(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            developer_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a + b",
                "summary": "Fix addition implementation",
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    developer_patch,
                    30,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ):
                run_dir = run_multi_agent(
                    request(
                        repo,
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        ai_mode=False,
                        max_repair_attempts=0,
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (
                    run_dir /
                    "RunSummary.json"
                ).read_text(
                    encoding="utf-8"
                )
            )

            usage = json.loads(
                (
                    run_dir /
                    "UsageReport.json"
                ).read_text(
                    encoding="utf-8"
                )
            )

            generated = json.loads(
                (
                    run_dir /
                    "AIDeveloperPatch.json"
                ).read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )

            self.assertEqual(
                summary["change_operation"],
                "ai_generate",
            )

            self.assertEqual(
                usage["llm_calls"],
                3,
            )

            self.assertEqual(
                generated["path"],
                "calculator.py",
            )

            self.assertEqual(
                generated["old_text"],
                "return a - b",
            )

            self.assertEqual(
                generated["new_text"],
                "return a + b",
            )

            self.assertEqual(
                git(
                    repo,
                    "status",
                    "--porcelain",
                ),
                "",
            )

            self.assertIn(
                "return a - b",
                (
                    repo /
                    "calculator.py"
                ).read_text(
                    encoding="utf-8"
                ),
            )


    def test_ai_developer_composes_disjoint_same_file_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            same_file_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Document and fix calculator",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "def add(a, b):\n",
                        "new_text": (
                            "def add(a, b):\n"
                            "    \"\"\"Add two numbers.\"\"\"\n"
                        ),
                        "summary": "Document add",
                    },
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a + b",
                        "summary": "Fix addition",
                    },
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    same_file_patch,
                    40,
                    25,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix addition and document the function; "
                            "tests need no edit"
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=0,
                        allowed_paths=(
                            "calculator.py",
                            "test_calculator.py",
                        ),
                    ),
                    root / "runs",
                )

            generated = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            implement = json.loads(
                (
                    run_dir /
                    "tasks" /
                    "implement" /
                    "AgentResult.json"
                ).read_text(
                    encoding="utf-8"
                )
            )
            review = json.loads(
                (run_dir / "ReviewReport.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                generated["validated_change_count"],
                1,
            )
            self.assertEqual(
                len(generated["changes"]),
                1,
            )
            self.assertEqual(
                generated["changes"][0]["path"],
                "calculator.py",
            )
            self.assertIn(
                "\"\"\"Add two numbers.\"\"\"",
                generated["changes"][0]["new_text"],
            )
            self.assertIn(
                "return a + b",
                generated["changes"][0]["new_text"],
            )
            self.assertEqual(
                implement["changed_artifacts"],
                ["calculator.py"],
            )
            self.assertEqual(
                review["changed_paths"],
                ["calculator.py"],
            )
            self.assertEqual(
                len(invoke.call_args_list),
                3,
            )

            developer_format = (
                invoke.call_args_list[1].args[3]
            )
            self.assertEqual(
                developer_format["properties"]["changes"]
                ["minItems"],
                1,
            )
            self.assertEqual(
                developer_format["properties"]["changes"]
                ["maxItems"],
                8,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )


    def test_ai_developer_rejects_overlapping_same_file_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            overlapping_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Conflicting calculator edits",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": (
                            "def add(a, b):\n"
                            "    return a - b"
                        ),
                        "new_text": (
                            "def add(a, b):\n"
                            "    return a + b"
                        ),
                        "summary": "Replace whole function body",
                    },
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a + b",
                        "summary": "Replace nested return",
                    },
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    overlapping_patch,
                    40,
                    25,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    overlapping_patch,
                    40,
                    25,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                with self.assertRaises(ValueError):
                    run_multi_agent(
                        request(
                            repo,
                            objective="Fix addition",
                            operation="ai_generate",
                            old_text="",
                            new_text="",
                            max_repair_attempts=0,
                            allowed_paths=(
                                "calculator.py",
                                "test_calculator.py",
                            ),
                        ),
                        root / "runs",
                    )

            self.assertEqual(
                len(invoke.call_args_list),
                3,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(
                    encoding="utf-8"
                ),
            )


    def test_ai_developer_multifile_scope_normalizes_flat_single_change(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            flat_change = json.dumps({
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a + b",
                "summary": "Fix addition implementation",
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    flat_change,
                    30,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix calculator addition; change tests "
                            "only if they actually need modification"
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=0,
                        allowed_paths=(
                            "calculator.py",
                            "test_calculator.py",
                        ),
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            generated = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            implement = json.loads(
                (
                    run_dir /
                    "tasks" /
                    "implement" /
                    "AgentResult.json"
                ).read_text(
                    encoding="utf-8"
                )
            )
            review = json.loads(
                (run_dir / "ReviewReport.json").read_text(
                    encoding="utf-8"
                )
            )
            plan = json.loads(
                (run_dir / "ExecutionPlan.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )
            self.assertEqual(
                plan["allowed_paths"],
                [
                    "calculator.py",
                    "test_calculator.py",
                ],
            )
            self.assertEqual(
                generated["schema_version"],
                "2.0",
            )
            self.assertEqual(
                generated["validated_change_count"],
                1,
            )
            self.assertEqual(
                [
                    item["path"]
                    for item in generated["changes"]
                ],
                ["calculator.py"],
            )
            self.assertEqual(
                implement["changed_artifacts"],
                ["calculator.py"],
            )
            self.assertEqual(
                review["changed_paths"],
                ["calculator.py"],
            )
            self.assertEqual(
                len(invoke.call_args_list),
                3,
            )

            developer_format = (
                invoke.call_args_list[1].args[3]
            )
            self.assertEqual(
                developer_format["properties"]["changes"]
                ["minItems"],
                1,
            )
            self.assertEqual(
                developer_format["properties"]["changes"]
                ["maxItems"],
                8,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )


    def test_ai_developer_repairs_invalid_multifile_format_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)

            invalid_format = json.dumps({
                "summary": "Missing required contract fields",
            })

            corrected_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Fix addition and operation metadata",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a + b",
                        "summary": "Fix addition implementation",
                    },
                    {
                        "path": "operation.py",
                        "old_text": 'OPERATION = "subtract"',
                        "new_text": 'OPERATION = "add"',
                        "summary": "Align operation metadata",
                    },
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    invalid_format,
                    20,
                    10,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    corrected_patch,
                    50,
                    30,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix calculator addition and align "
                            "operation metadata"
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=0,
                        allowed_paths=(
                            "calculator.py",
                            "operation.py",
                        ),
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            generated = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            usage = json.loads(
                (run_dir / "UsageReport.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )
            self.assertEqual(
                generated["prewrite_repair_attempts"],
                1,
            )
            self.assertEqual(
                generated["format_repair_attempts"],
                1,
            )
            self.assertEqual(
                generated["reference_repair_attempts"],
                0,
            )
            self.assertEqual(
                generated["validated_change_count"],
                2,
            )
            self.assertEqual(
                usage["llm_calls"],
                4,
            )
            self.assertEqual(
                len(invoke.call_args_list),
                4,
            )

            developer_format = (
                invoke.call_args_list[1].args[3]
            )
            retry_format = (
                invoke.call_args_list[2].args[3]
            )

            self.assertEqual(
                developer_format,
                retry_format,
            )
            self.assertEqual(
                set(developer_format["required"]),
                {
                    "schema_version",
                    "summary",
                    "changes",
                },
            )

            changes_format = (
                developer_format["properties"]["changes"]
            )
            self.assertEqual(
                changes_format["minItems"],
                1,
            )
            self.assertEqual(
                changes_format["maxItems"],
                8,
            )
            self.assertEqual(
                set(
                    changes_format["items"]
                    ["properties"]["path"]["enum"]
                ),
                {
                    "calculator.py",
                    "operation.py",
                },
            )

            repair_prompt = invoke.call_args_list[2].args[1]
            self.assertIn(
                "ONE bounded pre-write repair attempt",
                repair_prompt,
            )
            self.assertIn(
                "missing fields: changes, schema_version",
                repair_prompt,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )


    def test_ai_developer_repairs_old_text_reference_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)

            invalid_reference = json.dumps({
                "schema_version": "2.0",
                "summary": "Use stale candidate text",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a * b",
                        "new_text": "return a + b",
                        "summary": "Fix addition",
                    },
                    {
                        "path": "operation.py",
                        "old_text": 'OPERATION = "subtract"',
                        "new_text": 'OPERATION = "add"',
                        "summary": "Align metadata",
                    },
                ],
            })

            corrected_patch = json.dumps({
                "schema_version": "2.1",
                "summary": "Fix addition and metadata",
                "files": [
                    {
                        "path": "calculator.py",
                        "new_text": (
                            "def add(a, b):\n"
                            "    return a + b\n"
                        ),
                        "summary": "Fix addition",
                    },
                    {
                        "path": "operation.py",
                        "new_text": 'OPERATION = "add"\n',
                        "summary": "Align metadata",
                    },
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    invalid_reference,
                    40,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    corrected_patch,
                    50,
                    30,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix calculator addition and align "
                            "operation metadata"
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=0,
                        allowed_paths=(
                            "calculator.py",
                            "operation.py",
                        ),
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            generated = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            usage = json.loads(
                (run_dir / "UsageReport.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )
            self.assertEqual(
                generated["prewrite_repair_attempts"],
                1,
            )
            self.assertEqual(
                generated["format_repair_attempts"],
                0,
            )
            self.assertEqual(
                generated["reference_repair_attempts"],
                1,
            )
            self.assertEqual(
                generated["validated_change_count"],
                2,
            )
            self.assertEqual(
                usage["llm_calls"],
                4,
            )
            self.assertEqual(
                len(invoke.call_args_list),
                4,
            )

            retry_prompt = invoke.call_args_list[2].args[1]

            self.assertIn(
                "old_text must occur exactly once in "
                "calculator.py; found 0",
                retry_prompt,
            )
            self.assertIn(
                "REFERENCE RECOVERY MODE",
                retry_prompt,
            )
            self.assertIn(
                "COMPLETE replacement file content",
                retry_prompt,
            )

            retry_format = (
                invoke.call_args_list[2].args[3]
            )
            self.assertEqual(
                retry_format["properties"]["schema_version"]
                ["enum"],
                ["2.1"],
            )
            file_properties = (
                retry_format["properties"]["files"]["items"]
                ["properties"]
            )
            self.assertNotIn(
                "old_text",
                file_properties,
            )
            self.assertIn(
                "new_text",
                file_properties,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )


    def test_semantic_review_failure_uses_bounded_repair_and_rereview(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            initial_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a + b",
                "summary": "Fix addition only",
            })

            semantic_repair = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": (
                    "def add(a, b):\n"
                    "    return a + b\n"
                ),
                "new_text": (
                    "def add(a, b):\n"
                    "    if a is None or b is None:\n"
                    "        raise ValueError(\"inputs are required\")\n"
                    "    return a + b\n"
                ),
                "summary": "Add the missing input validation",
            })

            plan_marker = (
                "PLAN_CONTRACT_REJECT_NONE_INPUTS"
            )

            scripted = [
                ProviderResponse(
                    ai_plan([
                        "Fix addition.",
                        plan_marker,
                    ]),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    initial_patch,
                    30,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_fail(
                        "Reject None inputs",
                        (
                            "The patch fixes addition but does not "
                            "implement the required None validation."
                        ),
                    ),
                    25,
                    15,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_repair,
                    45,
                    30,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    25,
                    15,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix addition and reject None inputs."
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=1,
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            review = json.loads(
                (run_dir / "ReviewReport.json").read_text(
                    encoding="utf-8"
                )
            )
            ai_review = json.loads(
                (run_dir / "AIReview.json").read_text(
                    encoding="utf-8"
                )
            )
            ai_plan_artifact = json.loads(
                (run_dir / "AIPlan.json").read_text(
                    encoding="utf-8"
                )
            )
            execution_plan = json.loads(
                (run_dir / "ExecutionPlan.json").read_text(
                    encoding="utf-8"
                )
            )
            developer = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence = json.loads(
                (run_dir / "TestEvidence.json").read_text(
                    encoding="utf-8"
                )
            )
            usage = json.loads(
                (run_dir / "UsageReport.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )
            self.assertEqual(
                summary["repair_attempts"],
                1,
            )
            self.assertEqual(
                review["status"],
                "PASS",
            )
            self.assertEqual(
                review["semantic_status"],
                "PASS",
            )
            self.assertEqual(
                review["review_round"],
                1,
            )
            self.assertEqual(
                len(ai_review["attempts"]),
                2,
            )
            self.assertEqual(
                ai_review["attempts"][0]["status"],
                "FAIL",
            )
            self.assertEqual(
                ai_review["attempts"][1]["status"],
                "PASS",
            )
            self.assertEqual(
                developer["repair_attempts"][0]["cause"],
                "semantic_review",
            )
            self.assertEqual(
                [
                    item["exit_status"]
                    for item in evidence["evidence"]
                    if item["check_type"] == "tests"
                ],
                [0, 0],
            )
            self.assertEqual(
                usage["llm_calls"],
                5,
            )
            self.assertEqual(
                len(invoke.call_args_list),
                5,
            )

            planner_schema = (
                invoke.call_args_list[0]
                .args[3]
            )
            self.assertIn(
                "acceptance_criteria",
                planner_schema["required"],
            )
            self.assertIn(
                plan_marker,
                ai_plan_artifact[
                    "acceptance_criteria"
                ],
            )

            implement_task = next(
                item
                for item in execution_plan["tasks"]
                if item["task_id"] == "implement"
            )
            self.assertIn(
                plan_marker,
                implement_task[
                    "acceptance_criteria"
                ],
            )

            developer_prompt = (
                invoke.call_args_list[1].args[1]
            )
            first_reviewer_prompt = (
                invoke.call_args_list[2].args[1]
            )
            semantic_repair_prompt = (
                invoke.call_args_list[3].args[1]
            )
            second_reviewer_prompt = (
                invoke.call_args_list[4].args[1]
            )

            self.assertIn(plan_marker, developer_prompt)
            self.assertIn(
                plan_marker,
                semantic_repair_prompt,
            )
            self.assertNotIn(
                plan_marker,
                first_reviewer_prompt,
            )
            self.assertNotIn(
                plan_marker,
                second_reviewer_prompt,
            )

            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )


    def test_semantic_review_failure_blocks_gate_when_repair_budget_is_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            initial_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a + b",
                "summary": "Fix addition only",
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    initial_patch,
                    30,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_fail(
                        "Reject None inputs",
                        (
                            "Required None validation is absent "
                            "from both implementation and tests."
                        ),
                    ),
                    25,
                    15,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix addition and reject None inputs."
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=0,
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            review = json.loads(
                (run_dir / "ReviewReport.json").read_text(
                    encoding="utf-8"
                )
            )
            gate = json.loads(
                (run_dir / "GateDecision.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "REVIEW",
            )
            self.assertEqual(
                review["status"],
                "FAIL",
            )
            self.assertEqual(
                review["semantic_status"],
                "FAIL",
            )
            self.assertEqual(
                gate["decision"],
                "REPAIR",
            )
            self.assertEqual(
                len(invoke.call_args_list),
                3,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )


    def test_ai_developer_rejects_path_expansion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            invalid_patch = json.dumps({
                "schema_version": "1.0",
                "path": "../outside.py",
                "old_text": "return a - b",
                "new_text": "return a + b",
                "summary": "Unsafe expansion",
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    invalid_patch,
                    20,
                    10,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                with self.assertRaises(
                    ValueError
                ):
                    run_multi_agent(
                        request(
                            repo,
                            operation="ai_generate",
                            old_text="",
                            new_text="",
                            max_repair_attempts=0,
                        ),
                        root / "runs",
                    )

            self.assertEqual(
                len(invoke.call_args_list),
                2,
            )
            self.assertEqual(
                git(
                    repo,
                    "status",
                    "--porcelain",
                ),
                "",
            )


    def test_ai_developer_multi_file_generates_exact_reviewed_diff_and_promotes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)

            developer_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Fix addition behavior and operation metadata",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a + b",
                        "summary": "Fix addition implementation",
                    },
                    {
                        "path": "operation.py",
                        "old_text": 'OPERATION = "subtract"',
                        "new_text": 'OPERATION = "add"',
                        "summary": "Align operation metadata",
                    },
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    developer_patch,
                    50,
                    30,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ):
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix calculator addition and align "
                            "operation metadata"
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        ai_mode=False,
                        max_repair_attempts=0,
                        allowed_paths=(
                            "calculator.py",
                            "operation.py",
                        ),
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            generated = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            review = json.loads(
                (run_dir / "ReviewReport.json").read_text(
                    encoding="utf-8"
                )
            )
            plan = json.loads(
                (run_dir / "ExecutionPlan.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )
            self.assertEqual(
                summary["changes"],
                ["calculator.py", "operation.py"],
            )
            self.assertEqual(
                generated["schema_version"],
                "2.0",
            )
            self.assertEqual(
                generated["validated_change_count"],
                2,
            )
            self.assertEqual(
                review["changed_paths"],
                ["calculator.py", "operation.py"],
            )
            self.assertEqual(
                plan["allowed_paths"],
                ["calculator.py", "operation.py"],
            )
            self.assertTrue(
                all(
                    task["scope"]["allowed_paths"]
                    == ["calculator.py", "operation.py"]
                    for task in plan["tasks"]
                    if task["task_id"] in {
                        "plan", "implement", "test", "review"
                    }
                )
            )

            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertIn(
                'OPERATION = "subtract"',
                (repo / "operation.py").read_text(
                    encoding="utf-8"
                ),
            )

            source_head = git(
                repo,
                "rev-parse",
                "HEAD",
            )

            result = decide(
                run_dir,
                repo,
                "Product Owner",
                "approve",
            )

            self.assertEqual(
                result["status"],
                "DONE",
            )
            self.assertEqual(
                git(repo, "rev-parse", "HEAD"),
                source_head,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )

            branch = (
                f"forgelab/promote/{run_dir.name}"
            )

            self.assertIn(
                "return a + b",
                git(
                    repo,
                    "show",
                    f"{branch}:calculator.py",
                ),
            )
            self.assertIn(
                'OPERATION = "add"',
                git(
                    repo,
                    "show",
                    f"{branch}:operation.py",
                ),
            )


    def test_ai_developer_multi_file_rejects_unauthorized_path(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)

            invalid_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Unsafe path expansion",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a + b",
                        "summary": "Fix addition",
                    },
                    {
                        "path": "../outside.py",
                        "old_text": "old",
                        "new_text": "new",
                        "summary": "Unsafe expansion",
                    },
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    invalid_patch,
                    30,
                    20,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ):
                with self.assertRaises(ValueError):
                    run_multi_agent(
                        request(
                            repo,
                            operation="ai_generate",
                            old_text="",
                            new_text="",
                            max_repair_attempts=0,
                            allowed_paths=(
                                "calculator.py",
                                "operation.py",
                            ),
                        ),
                        root / "runs",
                    )

            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )



    def test_ai_developer_failed_candidate_uses_bounded_ai_repair(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)
            add_m88_context(repo)

            initial_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a * b",
                "summary": "Initial candidate",
            })
            repair_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a * b",
                "new_text": "return a + b",
                "summary": "Repair failed addition behavior",
            })

            scripted = [
                ProviderResponse(ai_plan(), 10, 5, actual_cost=Decimal("0")),
                ProviderResponse(initial_patch, 30, 20, actual_cost=Decimal("0")),
                ProviderResponse(
                    "The failed test shows multiplication where addition is required.",
                    20,
                    10,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(repair_patch, 30, 20, actual_cost=Decimal("0")),
                ProviderResponse(semantic_review_pass(), 12, 6, actual_cost=Decimal("0")),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=1,
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(encoding="utf-8")
            )
            evidence = json.loads(
                (run_dir / "TestEvidence.json").read_text(encoding="utf-8")
            )
            diagnostics = json.loads(
                (run_dir / "AIDiagnostics.json").read_text(encoding="utf-8")
            )
            developer = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(encoding="utf-8")
            )
            usage = json.loads(
                (run_dir / "UsageReport.json").read_text(encoding="utf-8")
            )

            self.assertEqual(summary["status"], "READY_FOR_DECISION")
            self.assertEqual(summary["repair_attempts"], 1)
            self.assertIn("SUPPORT", summary["selected_roles"])
            self.assertEqual(
                [
                    item["exit_status"]
                    for item in evidence["evidence"]
                    if item["check_type"] == "tests"
                ],
                [1, 0],
            )
            self.assertEqual(
                diagnostics["attempts"][0]["test_evidence_ref"],
                "ev-test-0",
            )
            self.assertEqual(
                developer["repair_attempts"][0]["changed_paths"],
                ["calculator.py"],
            )
            self.assertEqual(
                developer["repair_attempts"][0]
                ["prewrite_correction_attempts"],
                0,
            )
            self.assertEqual(usage["llm_calls"], 5)
            self.assertTrue(
                (run_dir / "tasks" / "support-1" / "AgentResult.json").is_file()
            )
            self.assertTrue(
                (run_dir / "tasks" / "repair-1" / "AgentResult.json").is_file()
            )
            context = json.loads(
                (run_dir / "ContextBundle.json").read_text(encoding="utf-8")
            )
            prompts = [call.args[1] for call in invoke.call_args_list]
            self.assertIn("M88_SHARED_CONTEXT_MARKER", prompts[1])
            self.assertIn("M88_SHARED_CONTEXT_MARKER", prompts[2])
            self.assertIn("M88_SHARED_CONTEXT_MARKER", prompts[3])
            self.assertEqual(
                diagnostics["context_selection_sha256"],
                context["selection_sha256"],
            )
            self.assertEqual(
                developer["context_selection_sha256"],
                context["selection_sha256"],
            )
            self.assertEqual(git(repo, "status", "--porcelain"), "")
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(encoding="utf-8"),
            )


    def test_ai_developer_repair_recovers_stale_reference_with_full_file_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)

            initial_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Initial candidate leaves arithmetic wrong",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a * b",
                        "summary": "Incorrect arithmetic candidate",
                    },
                    {
                        "path": "operation.py",
                        "old_text": 'OPERATION = "subtract"',
                        "new_text": 'OPERATION = "add"',
                        "summary": "Correct operation metadata",
                    },
                ],
            })

            stale_repair = json.dumps({
                "schema_version": "2.0",
                "summary": "Use stale arithmetic anchor",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a / b",
                        "new_text": "return a + b",
                        "summary": "Attempt arithmetic repair",
                    }
                ],
            })

            full_file_recovery = json.dumps({
                "schema_version": "2.1",
                "summary": "Replace calculator from current source",
                "files": [
                    {
                        "path": "calculator.py",
                        "new_text": (
                            "def add(a, b):\n"
                            "    return a + b\n"
                        ),
                        "summary": "Correct arithmetic",
                    }
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    initial_patch,
                    50,
                    30,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    (
                        "The arithmetic test fails because "
                        "calculator.py multiplies instead of adds."
                    ),
                    20,
                    10,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    stale_repair,
                    35,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    full_file_recovery,
                    45,
                    25,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix calculator addition and align "
                            "operation metadata"
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=1,
                        allowed_paths=(
                            "calculator.py",
                            "operation.py",
                        ),
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence = json.loads(
                (run_dir / "TestEvidence.json").read_text(
                    encoding="utf-8"
                )
            )
            developer = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            usage = json.loads(
                (run_dir / "UsageReport.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )
            self.assertEqual(
                summary["repair_attempts"],
                1,
            )
            self.assertEqual(
                [
                    item["exit_status"]
                    for item in evidence["evidence"]
                    if item["check_type"] == "tests"
                ],
                [1, 0],
            )
            self.assertEqual(
                developer["repair_attempts"][0]
                ["prewrite_correction_attempts"],
                1,
            )
            self.assertEqual(
                developer["repair_attempts"][0]
                ["patch"]["schema_version"],
                "2.0",
            )
            self.assertEqual(
                developer["repair_attempts"][0]
                ["patch"]["changes"][0]["old_text"],
                (
                    "def add(a, b):\n"
                    "    return a * b\n"
                ),
            )
            self.assertEqual(
                usage["llm_calls"],
                6,
            )
            self.assertEqual(
                len(invoke.call_args_list),
                6,
            )

            prewrite_prompt = (
                invoke.call_args_list[4].args[1]
            )
            self.assertIn(
                "old_text must occur exactly once in "
                "calculator.py; found 0",
                prewrite_prompt,
            )
            self.assertIn(
                "REFERENCE RECOVERY MODE",
                prewrite_prompt,
            )

            prewrite_format = (
                invoke.call_args_list[4].args[3]
            )
            self.assertEqual(
                prewrite_format["properties"]["schema_version"]
                ["enum"],
                ["2.1"],
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(
                    encoding="utf-8"
                ),
            )


    def test_ai_developer_repair_corrects_invalid_python_syntax_prewrite_once(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)

            initial_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Initial candidate leaves arithmetic wrong",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a * b",
                        "summary": "Incorrect arithmetic candidate",
                    },
                    {
                        "path": "operation.py",
                        "old_text": 'OPERATION = "subtract"',
                        "new_text": 'OPERATION = "add"',
                        "summary": "Correct operation metadata",
                    },
                ],
            })

            invalid_repair = json.dumps({
                "schema_version": "2.0",
                "summary": "Malformed Python repair",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a * b",
                        "new_text": "if True:\nreturn a + b",
                        "summary": "Attempt arithmetic repair",
                    }
                ],
            })

            corrected_repair = json.dumps({
                "schema_version": "2.0",
                "summary": "Syntactically valid arithmetic repair",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a * b",
                        "new_text": "return a + b",
                        "summary": "Correct arithmetic",
                    }
                ],
            })

            scripted = [
                ProviderResponse(
                    ai_plan(),
                    10,
                    5,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    initial_patch,
                    50,
                    30,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    (
                        "The arithmetic assertion fails because "
                        "calculator.py multiplies instead of adds."
                    ),
                    20,
                    10,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    invalid_repair,
                    35,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    corrected_repair,
                    35,
                    20,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(
                    semantic_review_pass(),
                    12,
                    6,
                    actual_cost=Decimal("0"),
                ),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective=(
                            "Fix calculator addition and align "
                            "operation metadata"
                        ),
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=1,
                        allowed_paths=(
                            "calculator.py",
                            "operation.py",
                        ),
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(
                    encoding="utf-8"
                )
            )
            evidence = json.loads(
                (run_dir / "TestEvidence.json").read_text(
                    encoding="utf-8"
                )
            )
            developer = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(
                    encoding="utf-8"
                )
            )
            usage = json.loads(
                (run_dir / "UsageReport.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                summary["status"],
                "READY_FOR_DECISION",
            )
            self.assertEqual(
                summary["repair_attempts"],
                1,
            )
            self.assertEqual(
                [
                    item["exit_status"]
                    for item in evidence["evidence"]
                    if item["check_type"] == "tests"
                ],
                [1, 0],
            )
            self.assertEqual(
                developer["repair_attempts"][0]
                ["prewrite_correction_attempts"],
                1,
            )
            self.assertEqual(
                developer["repair_attempts"][0]
                ["changed_paths"],
                ["calculator.py"],
            )
            self.assertEqual(
                usage["llm_calls"],
                6,
            )
            self.assertEqual(
                len(invoke.call_args_list),
                6,
            )

            prewrite_prompt = (
                invoke.call_args_list[4].args[1]
            )
            self.assertIn(
                "failed deterministic",
                prewrite_prompt,
            )
            self.assertIn(
                "Python candidate does not parse",
                prewrite_prompt,
            )
            self.assertIn(
                "ONE bounded pre-write correction",
                prewrite_prompt,
            )
            self.assertEqual(
                git(repo, "status", "--porcelain"),
                "",
            )
            self.assertIn(
                "return a - b",
                (repo / "calculator.py").read_text(
                    encoding="utf-8"
                ),
            )


    def test_ai_developer_multi_file_repair_can_change_authorized_subset(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)

            initial_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Initial two-file candidate",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a - b",
                        "new_text": "return a * b",
                        "summary": "Incorrect arithmetic candidate",
                    },
                    {
                        "path": "operation.py",
                        "old_text": 'OPERATION = "subtract"',
                        "new_text": 'OPERATION = "add"',
                        "summary": "Correct metadata candidate",
                    },
                ],
            })
            repair_patch = json.dumps({
                "schema_version": "2.0",
                "summary": "Repair arithmetic only",
                "changes": [
                    {
                        "path": "calculator.py",
                        "old_text": "return a * b",
                        "new_text": "return a + b",
                        "summary": "Correct arithmetic after failed test",
                    }
                ],
            })

            scripted = [
                ProviderResponse(ai_plan(), 10, 5, actual_cost=Decimal("0")),
                ProviderResponse(initial_patch, 50, 30, actual_cost=Decimal("0")),
                ProviderResponse(
                    "Only calculator.py contradicts the failed arithmetic assertion; operation.py already passes.",
                    20,
                    10,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(repair_patch, 35, 20, actual_cost=Decimal("0")),
                ProviderResponse(semantic_review_pass(), 12, 6, actual_cost=Decimal("0")),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ) as invoke:
                run_dir = run_multi_agent(
                    request(
                        repo,
                        objective="Fix calculator addition and align operation metadata",
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=1,
                        allowed_paths=("calculator.py", "operation.py"),
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(encoding="utf-8")
            )
            plan = json.loads(
                (run_dir / "ExecutionPlan.json").read_text(encoding="utf-8")
            )
            developer = json.loads(
                (run_dir / "AIDeveloperPatch.json").read_text(encoding="utf-8")
            )
            repair_result = json.loads(
                (run_dir / "tasks" / "repair-1" / "AgentResult.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(summary["status"], "READY_FOR_DECISION")
            self.assertEqual(summary["repair_attempts"], 1)
            self.assertEqual(
                plan["allowed_paths"],
                ["calculator.py", "operation.py"],
            )
            repair_task = next(
                task for task in plan["tasks"] if task["task_id"] == "repair-1"
            )
            self.assertEqual(
                repair_task["scope"]["allowed_paths"],
                ["calculator.py", "operation.py"],
            )
            self.assertEqual(
                repair_result["changed_artifacts"],
                ["calculator.py"],
            )
            self.assertEqual(
                developer["repair_attempts"][0]["patch"]["changes"][0]["path"],
                "calculator.py",
            )
            self.assertEqual(
                summary["changes"],
                ["calculator.py", "operation.py"],
            )

            initial_format = (
                invoke.call_args_list[1].args[3]
            )
            repair_format = (
                invoke.call_args_list[3].args[3]
            )

            self.assertEqual(
                initial_format["properties"]["changes"]
                ["minItems"],
                1,
            )
            self.assertEqual(
                repair_format["properties"]["changes"]
                ["minItems"],
                1,
            )
            self.assertEqual(
                repair_format["properties"]["changes"]
                ["maxItems"],
                8,
            )
            self.assertEqual(
                set(
                    repair_format["properties"]["changes"]
                    ["items"]["properties"]["path"]["enum"]
                ),
                {
                    "calculator.py",
                    "operation.py",
                },
            )
            self.assertEqual(git(repo, "status", "--porcelain"), "")


    def test_ai_developer_repair_rejects_path_expansion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            initial_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a * b",
                "summary": "Initial candidate",
            })
            invalid_repair = json.dumps({
                "schema_version": "1.0",
                "path": "../outside.py",
                "old_text": "old",
                "new_text": "new",
                "summary": "Attempted scope expansion",
            })

            scripted = [
                ProviderResponse(ai_plan(), 10, 5, actual_cost=Decimal("0")),
                ProviderResponse(initial_patch, 30, 20, actual_cost=Decimal("0")),
                ProviderResponse(
                    "The arithmetic implementation still violates the failed addition assertion.",
                    20,
                    10,
                    actual_cost=Decimal("0"),
                ),
                ProviderResponse(invalid_repair, 30, 20, actual_cost=Decimal("0")),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ):
                with self.assertRaises(ValueError):
                    run_multi_agent(
                        request(
                            repo,
                            operation="ai_generate",
                            old_text="",
                            new_text="",
                            max_repair_attempts=1,
                        ),
                        root / "runs",
                    )

            self.assertEqual(git(repo, "status", "--porcelain"), "")
            self.assertFalse((root / "outside.py").exists())


    def test_ai_developer_repeated_diagnostic_hypothesis_stops_second_repair(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_demo(root)

            initial_patch = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a - b",
                "new_text": "return a * b",
                "summary": "Initial candidate",
            })
            first_repair = json.dumps({
                "schema_version": "1.0",
                "path": "calculator.py",
                "old_text": "return a * b",
                "new_text": "return a / b",
                "summary": "First bounded repair candidate",
            })
            repeated_hypothesis = (
                "The arithmetic operator is inconsistent with the failed addition assertion."
            )

            scripted = [
                ProviderResponse(ai_plan(), 10, 5, actual_cost=Decimal("0")),
                ProviderResponse(initial_patch, 30, 20, actual_cost=Decimal("0")),
                ProviderResponse(repeated_hypothesis, 20, 10, actual_cost=Decimal("0")),
                ProviderResponse(first_repair, 30, 20, actual_cost=Decimal("0")),
                ProviderResponse(repeated_hypothesis, 20, 10, actual_cost=Decimal("0")),
            ]

            with patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ):
                run_dir = run_multi_agent(
                    request(
                        repo,
                        operation="ai_generate",
                        old_text="",
                        new_text="",
                        max_repair_attempts=2,
                    ),
                    root / "runs",
                )

            summary = json.loads(
                (run_dir / "RunSummary.json").read_text(encoding="utf-8")
            )
            diagnostics = json.loads(
                (run_dir / "AIDiagnostics.json").read_text(encoding="utf-8")
            )
            support_two = json.loads(
                (run_dir / "tasks" / "support-2" / "AgentResult.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(summary["status"], "DIAGNOSING")
            self.assertEqual(summary["tests"], "FAIL")
            self.assertEqual(summary["repair_attempts"], 1)
            self.assertEqual(len(diagnostics["attempts"]), 2)
            self.assertEqual(
                [item["test_evidence_ref"] for item in diagnostics["attempts"]],
                ["ev-test-0", "ev-test-1"],
            )
            self.assertEqual(support_two["status"], "FAIL")
            self.assertFalse((run_dir / "tasks" / "repair-2").exists())
            self.assertEqual(git(repo, "status", "--porcelain"), "")


    def test_ai_generate_request_json_accepts_two_authorized_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            repo = make_multi_demo(root)
            request_path = root / "request.json"

            payload = {
                "repository": str(repo),
                "objective": "Fix bounded multi-file behavior",
                "change": {
                    "operation": "ai_generate",
                    "paths": [
                        "calculator.py",
                        "operation.py",
                    ],
                },
                "test_command": [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ],
            }

            request_path.write_text(
                json.dumps(payload),
                encoding="utf-8-sig",
            )

            parsed = MultiAgentRequest.from_json(
                request_path
            )

            self.assertEqual(
                parsed.target_path,
                "calculator.py",
            )
            self.assertEqual(
                parsed.target_paths,
                (
                    "calculator.py",
                    "operation.py",
                ),
            )


if __name__ == "__main__":
    unittest.main()

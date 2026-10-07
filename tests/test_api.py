import json
from decimal import Decimal
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from forgelab.api import ApiError, make_server
from forgelab.editor_adapter import EditorResult
from forgelab.model_router import ProviderResponse
from forgelab.runner import RunRequest, run_isolated


TOKEN = "test-token-with-at-least-24-characters"


def ai_plan() -> str:
    return json.dumps({
        "schema_version": "1.0",
        "intended_outcome": "Deliver the requested bounded change.",
        "execution_steps": [
            "Inspect authorized files.",
            "Implement the requested behavior.",
            "Run deterministic tests.",
        ],
        "acceptance_criteria": [
            "Implement the requested objective.",
            "Tests cover the requested behavior.",
        ],
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


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)

        self.run = self.root / "run-test123"
        self.run.mkdir()

        (self.run / "RunSummary.json").write_text(
            json.dumps({
                "run_id": "run-test123",
                "status": "READY_FOR_DECISION",
                "created_at": "2026-09-19T00:00:00+00:00",
                "decision": "Human gate pending",
            }),
            encoding="utf-8",
        )

        (self.run / "TestEvidence.json").write_text(
            json.dumps({"status": "PASS"}),
            encoding="utf-8",
        )

        (self.run / "Changes.patch").write_text(
            "diff --git a/a.py b/a.py\n"
            "--- a/a.py\n"
            "+++ b/a.py\n"
            "@@ -1 +1 @@\n"
            "-OLD\n"
            "+NEW\n",
            encoding="utf-8",
        )

        self.server = make_server(
            self.root,
            TOKEN,
            "http://localhost:5173",
            port=0,
        )

        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )

        self.thread.start()

        self.base = (
            f"http://127.0.0.1:"
            f"{self.server.server_port}"
        )

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.folder.cleanup()

    def request(
        self,
        path,
        method="GET",
        payload=None,
        token=TOKEN,
        origin="http://localhost:5173",
    ):
        body = (
            None
            if payload is None
            else json.dumps(payload).encode("utf-8")
        )

        headers = {
            "Origin": origin,
        }

        if token:
            headers["Authorization"] = (
                f"Bearer {token}"
            )

        if body:
            headers["Content-Type"] = (
                "application/json"
            )

        return urlopen(
            Request(
                self.base + path,
                data=body,
                headers=headers,
                method=method,
            ),
            timeout=15,
        )

    def make_demo_repo(self) -> Path:
        repo = self.root / "dashboard-demo"
        repo.mkdir()

        (repo / "calculator.py").write_text(
            "def add(a, b):\n"
            "    return a - b\n",
            encoding="utf-8",
        )

        (
            repo / "test_calculator.py"
        ).write_text(
            "import unittest\n"
            "from calculator import add\n\n"
            "class CalculatorTests(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n",
            encoding="utf-8",
        )

        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "init",
                "-b",
                "main",
            ],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "add",
                ".",
            ],
            check=True,
            capture_output=True,
        )

        subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "-c",
                "user.name=ForgeLab Test",
                "-c",
                "user.email=forgelab-test@local",
                "commit",
                "-m",
                "demo",
            ],
            check=True,
            capture_output=True,
        )

        return repo

    def test_health_is_available_without_token(self):
        with self.request(
            "/health",
            token=None,
        ) as response:
            self.assertEqual(
                response.status,
                200,
            )

    def test_health_reports_active_runtime_sha(self):
        with patch.dict(
            "os.environ",
            {
                "FORGELAB_RUNTIME_SHA":
                    "abc123runtime",
            },
            clear=False,
        ):
            with self.request(
                "/health",
                token=None,
            ) as response:
                payload = json.load(response)

        self.assertEqual(
            payload["runtime_sha"],
            "abc123runtime",
        )

    def test_run_listing_requires_bearer_token(self):
        with self.assertRaises(HTTPError) as denied:
            self.request(
                "/v1/runs",
                token=None,
            )

        self.assertEqual(
            denied.exception.code,
            401,
        )

        with self.request(
            "/v1/runs"
        ) as response:
            payload = json.load(response)

        self.assertEqual(
            payload["runs"][0]["run_id"],
            "run-test123",
        )

    def test_artifacts_are_returned_from_allowlist(self):
        (self.run / "private.txt").write_text(
            "not exposed",
            encoding="utf-8",
        )

        with self.request(
            "/v1/runs/run-test123/artifacts"
        ) as response:
            payload = json.load(response)

        self.assertIn(
            "RunSummary.json",
            payload["artifacts"],
        )

        self.assertNotIn(
            "private.txt",
            payload["artifacts"],
        )

        self.assertEqual(
            payload["artifacts"]["Changes.patch"]["text"],
            "diff --git a/a.py b/a.py\n"
            "--- a/a.py\n"
            "+++ b/a.py\n"
            "@@ -1 +1 @@\n"
            "-OLD\n"
            "+NEW\n",
        )

    def test_terminal_failure_artifacts_are_exposed(self):
        prewrite = {
            "reason":
                "PREWRITE_RECOVERY_EXHAUSTED",
            "phase":
                "test_failure_repair",
            "final_error":
                "invalid repair candidate",
        }
        editor = {
            "reason":
                "EDITOR_EXECUTION_FAILED",
            "phase":
                "implementation",
            "final_error":
                "Aider sandbox contract failed",
        }
        provider = {
            "reason":
                "PROVIDER_TRANSIENT_RETRY_EXHAUSTED",
            "phase":
                "review",
            "final_error":
                "provider timeout",
        }

        (
            self.run /
            "PrewriteRecoveryFailure.json"
        ).write_text(
            json.dumps(prewrite),
            encoding="utf-8",
        )
        (
            self.run /
            "EditorFailure.json"
        ).write_text(
            json.dumps(editor),
            encoding="utf-8",
        )
        (
            self.run /
            "ProviderFailure.json"
        ).write_text(
            json.dumps(provider),
            encoding="utf-8",
        )

        with self.request(
            "/v1/runs/run-test123/artifacts"
        ) as response:
            payload = json.load(response)

        self.assertEqual(
            payload["artifacts"][
                "PrewriteRecoveryFailure.json"
            ]["reason"],
            "PREWRITE_RECOVERY_EXHAUSTED",
        )
        self.assertEqual(
            payload["artifacts"][
                "EditorFailure.json"
            ]["reason"],
            "EDITOR_EXECUTION_FAILED",
        )
        self.assertEqual(
            payload["artifacts"][
                "ProviderFailure.json"
            ]["final_error"],
            "provider timeout",
        )

    def test_human_repair_creates_bounded_child_run(self):
        repo = self.make_demo_repo()

        (self.run / "ExecutionPlan.json").write_text(
            json.dumps({
                "run_id": "run-test123",
                "objective": (
                    "Add complete calculator behavior"
                ),
                "repository": str(repo.resolve()),
                "selected_roles": [
                    "PROJECT_MANAGER",
                    "DEVELOPER",
                    "TESTER",
                    "REVIEWER",
                ],
                "max_repair_attempts": 1,
                "test_command": [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ],
                "change_operation": "ai_generate",
                "allowed_paths": [
                    "calculator.py",
                    "test_calculator.py",
                ],
                "timeout_seconds": 60,
                "editor_timeout_seconds": 420,
            }),
            encoding="utf-8",
        )

        (self.run / "GateDecision.json").write_text(
            json.dumps({
                "gate_type": "G3_PROMOTE",
                "actor": "SYSTEM",
                "decision": "PENDING",
                "scope": "Review candidate",
                "timestamp": (
                    "2026-09-29T00:00:00+00:00"
                ),
            }),
            encoding="utf-8",
        )

        captured = {}

        def fake_run(request, runs_root):
            captured["request"] = request
            child = runs_root / "run-child456"
            child.mkdir()

            (child / "RunSummary.json").write_text(
                json.dumps({
                    "run_id": "run-child456",
                    "status": "READY_FOR_DECISION",
                    "decision": "Human gate pending",
                    "created_at": (
                        "2026-09-29T00:01:00+00:00"
                    ),
                }),
                encoding="utf-8",
            )

            return child

        feedback = (
            "The prior candidate is incomplete: "
            "implement every original requirement."
        )

        with patch(
            "forgelab.api.run_multi_agent",
            side_effect=fake_run,
        ):
            with self.request(
                "/v1/runs/run-test123/repairs",
                "POST",
                {
                    "actor": "Product Owner",
                    "feedback": feedback,
                },
            ) as response:
                self.assertEqual(
                    response.status,
                    201,
                )
                payload = json.load(response)

        self.assertEqual(
            payload["run_id"],
            "run-child456",
        )
        self.assertEqual(
            payload["parent_run_id"],
            "run-test123",
        )
        self.assertEqual(
            payload["decision"],
            "REPAIR",
        )

        request = captured["request"]

        self.assertEqual(
            request.repository,
            repo.resolve(),
        )
        self.assertEqual(
            request.allowed_paths,
            (
                "calculator.py",
                "test_calculator.py",
            ),
        )
        self.assertEqual(
            request.operation,
            "ai_generate",
        )
        self.assertEqual(
            request.max_repair_attempts,
            1,
        )
        self.assertEqual(
            request.timeout_seconds,
            60,
        )
        self.assertEqual(
            request.editor_timeout_seconds,
            420,
        )
        self.assertIn(
            feedback,
            request.objective,
        )

        parent_gate = json.loads(
            (self.run / "GateDecision.json").read_text(
                encoding="utf-8"
            )
        )
        parent_summary = json.loads(
            (self.run / "RunSummary.json").read_text(
                encoding="utf-8"
            )
        )
        parent_record = json.loads(
            (
                self.run /
                "HumanRepairRequest.json"
            ).read_text(
                encoding="utf-8"
            )
        )
        child_record = json.loads(
            (
                self.root /
                "run-child456" /
                "HumanRepairRequest.json"
            ).read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            parent_gate["decision"],
            "REPAIR",
        )
        self.assertEqual(
            parent_summary["status"],
            "REPAIRING",
        )
        self.assertEqual(
            parent_record["child_run_id"],
            "run-child456",
        )
        self.assertEqual(
            child_record["parent_run_id"],
            "run-test123",
        )
        self.assertEqual(
            child_record["feedback"],
            feedback,
        )


    def test_human_repair_accepts_already_recorded_repair_gate(self):
        repo = self.make_demo_repo()

        (self.run / "ExecutionPlan.json").write_text(
            json.dumps({
                "run_id": "run-test123",
                "objective": "Fix complete behavior",
                "repository": str(repo.resolve()),
                "selected_roles": [
                    "PROJECT_MANAGER",
                    "DEVELOPER",
                    "TESTER",
                    "REVIEWER",
                ],
                "max_repair_attempts": 1,
                "test_command": [
                    sys.executable,
                    "-m",
                    "unittest",
                    "discover",
                    "-v",
                ],
                "change_operation": "ai_generate",
                "allowed_paths": [
                    "calculator.py",
                ],
                "timeout_seconds": 60,
            }),
            encoding="utf-8",
        )

        (self.run / "GateDecision.json").write_text(
            json.dumps({
                "gate_type": "G3_PROMOTE",
                "actor": "Product Owner",
                "decision": "REPAIR",
                "scope": "Candidate patch not promoted",
                "timestamp": (
                    "2026-09-29T00:00:00+00:00"
                ),
            }),
            encoding="utf-8",
        )

        summary = json.loads(
            (self.run / "RunSummary.json").read_text(
                encoding="utf-8"
            )
        )
        summary["status"] = "REPAIRING"
        summary["decision"] = "REPAIR"
        (self.run / "RunSummary.json").write_text(
            json.dumps(summary),
            encoding="utf-8",
        )

        def fake_run(request, runs_root):
            child = runs_root / "run-child789"
            child.mkdir()
            (child / "RunSummary.json").write_text(
                json.dumps({
                    "run_id": "run-child789",
                    "status": "READY_FOR_DECISION",
                    "decision": "Human gate pending",
                }),
                encoding="utf-8",
            )
            return child

        with patch(
            "forgelab.api.run_multi_agent",
            side_effect=fake_run,
        ):
            with self.request(
                "/v1/runs/run-test123/repairs",
                "POST",
                {
                    "actor": "Product Owner",
                    "feedback": (
                        "Complete all missing requirements."
                    ),
                },
            ) as response:
                payload = json.load(response)

        self.assertEqual(
            payload["run_id"],
            "run-child789",
        )
        self.assertEqual(
            payload["decision"],
            "REPAIR",
        )


    def test_approval_promotes_to_local_branch_without_touching_main(self):
        repo = self.make_demo_repo()
        request = RunRequest(
            repository=repo,
            objective="Fix calculator addition",
            target_path="calculator.py",
            old_text="return a - b",
            new_text="return a + b",
            test_command=[
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-v",
            ],
        )
        run_dir = run_isolated(request, self.root)
        source_head = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        with self.request(
            f"/v1/runs/{run_dir.name}/decisions",
            "POST",
            {
                "decision": "approve",
                "actor": "Product Owner",
            },
        ) as response:
            payload = json.load(response)

        self.assertEqual(payload["decision"], "APPROVE")
        self.assertTrue(payload["promotion_executed"])
        self.assertEqual(payload["status"], "DONE")
        self.assertTrue(payload["promotion_branch"].startswith("forgelab/promote/"))
        self.assertTrue(payload["commit"])

        current_head = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        current_branch = subprocess.run(
            ["git", "-C", str(repo), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        promoted_file = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "show",
                f"{payload['promotion_branch']}:calculator.py",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        self.assertEqual(current_head, source_head)
        self.assertEqual(current_branch, "main")
        self.assertIn("return a - b", (repo / "calculator.py").read_text(encoding="utf-8"))
        self.assertIn("return a + b", promoted_file)
        self.assertTrue((run_dir / "GateDecision.staged.json").is_file())
        self.assertTrue((run_dir / "PromotionResult.json").is_file())

        with self.assertRaises(HTTPError) as second:
            self.request(
                f"/v1/runs/{run_dir.name}/decisions",
                "POST",
                {
                    "decision": "approve",
                    "actor": "Product Owner",
                },
            )
        self.assertEqual(second.exception.code, 400)

    def test_create_run_executes_multi_agent_pipeline(self):
        repo = self.make_demo_repo()

        request_payload = {
            "repository": str(repo.resolve()),
            "objective": (
                "Fix calculator addition "
                "from the Control Plane API"
            ),
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
            "timeout_seconds": 60,
            "risk": "normal",
            "max_repair_attempts": 1,
        }

        with self.request(
            "/v1/runs",
            "POST",
            request_payload,
        ) as response:
            self.assertEqual(
                response.status,
                201,
            )
            created = json.load(response)

        run_id = created["run_id"]

        self.assertTrue(
            run_id.startswith("run-")
        )

        self.assertEqual(
            created["status"],
            "READY_FOR_DECISION",
        )

        run_dir = self.root / run_id

        self.assertTrue(
            (run_dir / "RunSummary.json").is_file()
        )

        self.assertTrue(
            (run_dir / "ExecutionPlan.json").is_file()
        )

        self.assertTrue(
            (run_dir / "TestEvidence.json").is_file()
        )

        source = (
            repo / "calculator.py"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "return a - b",
            source,
        )

        git_status = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "status",
                "--porcelain",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        self.assertEqual(
            git_status,
            "",
        )

    def test_create_run_accepts_ai_generate_without_old_new(self):
        repo = self.make_demo_repo()

        generated_patch = json.dumps({
            "schema_version": "1.0",
            "path": "calculator.py",
            "old_text": "return a - b",
            "new_text": "return a + b",
            "summary": "Fix calculator addition",
        })

        scripted = [
            ProviderResponse(
                ai_plan(),
                10,
                5,
                actual_cost=Decimal("0"),
            ),
            ProviderResponse(
                generated_patch,
                30,
                20,
                actual_cost=Decimal("0"),
            ),
            ProviderResponse(
                semantic_review_pass(),
                10,
                5,
                actual_cost=Decimal("0"),
            ),
        ]

        request_payload = {
            "repository":
                str(repo.resolve()),
            "objective":
                "Fix calculator addition "
                "without user-supplied patch",
            "change": {
                "operation":
                    "ai_generate",
                "path":
                    "calculator.py",
            },
            "test_command": [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-v",
            ],
            "timeout_seconds": 60,
            "risk": "normal",
            "max_repair_attempts": 0,
        }

        with patch(
            "forgelab.orchestrator.OllamaProvider.invoke",
            side_effect=scripted,
        ):
            with self.request(
                "/v1/runs",
                "POST",
                request_payload,
            ) as response:

                self.assertEqual(
                    response.status,
                    201,
                )

                created = json.load(
                    response
                )

        self.assertEqual(
            created["operation"],
            "ai_generate",
        )

        run_dir = (
            self.root /
            created["run_id"]
        )

        self.assertTrue(
            (
                run_dir /
                "AIDeveloperPatch.json"
            ).is_file()
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
            usage["llm_calls"],
            3,
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


    def test_create_run_accepts_reuse_first_aider_engine(self):
        repo = self.make_demo_repo()

        scripted = [
            ProviderResponse(
                ai_plan(),
                10,
                5,
                actual_cost=Decimal("0"),
            ),
            ProviderResponse(
                semantic_review_pass(),
                10,
                5,
                actual_cost=Decimal("0"),
            ),
        ]

        editor_result = EditorResult(
            engine="aider-cli",
            files={
                "calculator.py": (
                    "def add(a, b):\n"
                    "    return a + b\n"
                ),
            },
            changed_paths=("calculator.py",),
            stdout="aider local edit complete",
            stderr="",
            exit_status=0,
            timed_out=False,
            duration_ms=20,
            command=(
                "aider",
                "--model",
                "ollama_chat/qwen2.5-coder:7b",
            ),
        )

        request_payload = {
            "repository": str(repo.resolve()),
            "objective": (
                "Fix calculator addition "
                "using the reusable editor"
            ),
            "change": {
                "operation": "ai_generate",
                "path": "calculator.py",
            },
            "editor_engine": "aider",
            "test_command": [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-v",
            ],
            "timeout_seconds": 60,
            "risk": "normal",
            "max_repair_attempts": 0,
        }

        with (
            patch(
                "forgelab.orchestrator.OllamaProvider.invoke",
                side_effect=scripted,
            ),
            patch(
                "forgelab.orchestrator.AiderCliAdapter.run",
                return_value=editor_result,
            ),
        ):
            with self.request(
                "/v1/runs",
                "POST",
                request_payload,
            ) as response:
                self.assertEqual(response.status, 201)
                created = json.load(response)

        self.assertEqual(
            created["editor_engine"],
            "aider",
        )

        run_dir = self.root / created["run_id"]
        summary = json.loads(
            (run_dir / "RunSummary.json").read_text(
                encoding="utf-8"
            )
        )
        usage = json.loads(
            (run_dir / "UsageReport.json").read_text(
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
            summary["editor_engine"],
            "aider",
        )
        self.assertEqual(
            summary[
                "chatgpt_assistance_in_target_product_run"
            ],
            0,
        )
        self.assertEqual(
            plan["editor_engine"],
            "aider",
        )
        self.assertEqual(
            plan["timeout_seconds"],
            60,
        )
        self.assertEqual(
            plan["editor_timeout_seconds"],
            300,
        )
        self.assertEqual(
            usage["reusable_editor_calls"],
            1,
        )
        self.assertEqual(
            usage["spent"],
            "0",
        )


    def test_create_run_accepts_ai_generate_with_two_authorized_paths(self):
        repo = self.make_demo_repo()

        (repo / "operation.py").write_text(
            'OPERATION = "subtract"\n',
            encoding="utf-8",
        )
        (repo / "test_operation.py").write_text(
            "import unittest\n"
            "from operation import OPERATION\n\n"
            "class OperationTests(unittest.TestCase):\n"
            '    def test_operation(self): self.assertEqual(OPERATION, "add")\n',
            encoding="utf-8",
        )

        subprocess.run(
            ["git", "-C", str(repo), "add", "."],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git", "-C", str(repo),
                "-c", "user.name=ForgeLab Test",
                "-c", "user.email=forgelab-test@local",
                "commit", "-m", "multi-file fixture",
            ],
            check=True,
            capture_output=True,
        )

        generated_patch = json.dumps({
            "schema_version": "2.0",
            "summary": "Fix calculator and metadata",
            "changes": [
                {
                    "path": "calculator.py",
                    "old_text": "return a - b",
                    "new_text": "return a + b",
                    "summary": "Fix addition",
                },
                {
                    "path": "operation.py",
                    "old_text": 'OPERATION = "subtract"',
                    "new_text": 'OPERATION = "add"',
                    "summary": "Fix operation metadata",
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
                generated_patch,
                50,
                30,
                actual_cost=Decimal("0"),
            ),
            ProviderResponse(
                semantic_review_pass(),
                10,
                5,
                actual_cost=Decimal("0"),
            ),
        ]

        request_payload = {
            "repository": str(repo.resolve()),
            "objective": (
                "Fix calculator addition and "
                "operation metadata"
            ),
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
            "timeout_seconds": 60,
            "risk": "normal",
            "max_repair_attempts": 0,
        }

        with patch(
            "forgelab.orchestrator.OllamaProvider.invoke",
            side_effect=scripted,
        ):
            with self.request(
                "/v1/runs",
                "POST",
                request_payload,
            ) as response:
                self.assertEqual(
                    response.status,
                    201,
                )
                created = json.load(response)

        self.assertEqual(
            created["allowed_paths"],
            [
                "calculator.py",
                "operation.py",
            ],
        )

        run_dir = self.root / created["run_id"]
        summary = json.loads(
            (run_dir / "RunSummary.json").read_text(
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
            [
                "calculator.py",
                "operation.py",
            ],
        )
        self.assertEqual(
            plan["allowed_paths"],
            [
                "calculator.py",
                "operation.py",
            ],
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


    def test_create_run_rejects_more_than_three_ai_paths(self):
        repo = self.make_demo_repo()

        for index in range(4):
            (repo / f"extra_{index}.py").write_text(
                f"VALUE = {index}\n",
                encoding="utf-8",
            )

        request_payload = {
            "repository": str(repo.resolve()),
            "objective": "Reject unbounded AI file scope",
            "change": {
                "operation": "ai_generate",
                "paths": [
                    "extra_0.py",
                    "extra_1.py",
                    "extra_2.py",
                    "extra_3.py",
                ],
            },
            "test_command": [
                sys.executable,
                "-m",
                "unittest",
            ],
        }

        with self.assertRaises(HTTPError) as denied:
            self.request(
                "/v1/runs",
                "POST",
                request_payload,
            )

        self.assertEqual(
            denied.exception.code,
            400,
        )


    def test_create_run_rejects_target_path_escape(self):
        repo = self.make_demo_repo()

        request_payload = {
            "repository": str(repo.resolve()),
            "objective": (
                "Reject unsafe target path "
                "outside repository"
            ),
            "change": {
                "operation": "replace_text",
                "path": "../outside.py",
                "old": "old",
                "new": "new",
            },
            "test_command": [
                sys.executable,
                "-m",
                "unittest",
            ],
        }

        with self.assertRaises(HTTPError) as denied:
            self.request(
                "/v1/runs",
                "POST",
                request_payload,
            )

        self.assertEqual(
            denied.exception.code,
            400,
        )

    def test_non_loopback_binding_is_rejected(self):
        with self.assertRaises(ApiError):
            make_server(
                self.root,
                TOKEN,
                "http://localhost:5173",
                host="0.0.0.0",
                port=0,
            )


if __name__ == "__main__":
    unittest.main()

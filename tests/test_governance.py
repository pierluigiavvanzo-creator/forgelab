import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from forgelab.domain import Role
from forgelab.governance import PolicyEngine, PolicyViolation, ToolGateway


class GovernanceTests(unittest.TestCase):
    def test_role_cannot_use_unassigned_tool(self):
        gateway = ToolGateway(PolicyEngine())
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(PolicyViolation):
                gateway.run_test(Role.DEVELOPER, Path(folder), ["python", "-V"], 10)
        self.assertEqual(gateway.report()["denied_count"], 1)

    def test_edit_outside_task_scope_is_denied_before_write(self):
        gateway = ToolGateway(PolicyEngine())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "file.py").write_text("old", encoding="utf-8")
            with self.assertRaises(PolicyViolation):
                gateway.edit_text(Role.DEVELOPER, root, {"other.py"}, "file.py", "old", "new")
            self.assertEqual((root / "file.py").read_text(encoding="utf-8"), "old")

    def test_authorized_tool_failure_is_audited(self):
        gateway = ToolGateway(PolicyEngine())
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "file.py").write_text("actual", encoding="utf-8")
            with self.assertRaises(Exception):
                gateway.edit_text(Role.DEVELOPER, root, {"file.py"}, "file.py", "missing", "new")
        self.assertEqual(gateway.report()["events"][0]["outcome"], "ERROR")

    def test_network_is_default_deny_and_allowlist_is_exactly_enforced(self):
        denied = ToolGateway(PolicyEngine())
        with self.assertRaises(PolicyViolation):
            denied.authorize_network(Role.SECURITY, "api.example.com")
        allowed = ToolGateway(PolicyEngine(network_allowlist={"*.example.com"}))
        allowed.authorize_network(Role.SECURITY, "api.example.com")
        self.assertEqual(allowed.report()["denied_count"], 0)

    def test_dependency_requires_license_provenance_and_security_review(self):
        gateway = ToolGateway(PolicyEngine())
        with self.assertRaises(PolicyViolation):
            gateway.authorize_dependency(Role.SECURITY, "package", "MIT", None, "pass")
        gateway.authorize_dependency(Role.SECURITY, "package", "MIT", "official registry", "pass")

    def test_destructive_action_requires_role_permission_and_approved_gate(self):
        gateway = ToolGateway(PolicyEngine())
        with self.assertRaises(PolicyViolation):
            gateway.authorize_destructive(Role.DEVELOPER, "delete branch", None)
        gateway.authorize_destructive(Role.DEVELOPER, "delete branch", "APPROVE")
        with self.assertRaises(PolicyViolation):
            gateway.authorize_destructive(Role.TESTER, "delete branch", "APPROVE")

    def test_secret_value_is_passed_only_to_callback_and_never_audited(self):
        role_tools = {role: set(tools) for role, tools in PolicyEngine().role_tools.items()}
        role_secrets = {role: set() for role in Role}
        role_secrets[Role.SECURITY] = {"TEST_SECRET"}
        gateway = ToolGateway(PolicyEngine(role_tools=role_tools, role_secrets=role_secrets))
        with patch.dict("os.environ", {"TEST_SECRET": "super-sensitive-value"}):
            length = gateway.use_secret(Role.SECURITY, "TEST_SECRET", len)
        self.assertEqual(length, len("super-sensitive-value"))
        serialized = json.dumps(gateway.report())
        self.assertNotIn("super-sensitive-value", serialized)
        self.assertIn("TEST_SECRET", serialized)

    def test_audit_hashes_arguments_instead_of_storing_them(self):
        gateway = ToolGateway(PolicyEngine())
        with tempfile.TemporaryDirectory() as folder:
            result = gateway.run_test(Role.TESTER, Path(folder), ["python", "-c", "print('private argument')"], 10)
        self.assertEqual(result.exit_status, 0)
        report = gateway.report()
        self.assertEqual(len(report["events"][0]["arguments_sha256"]), 64)
        self.assertNotIn("private argument", json.dumps(report))


if __name__ == "__main__":
    unittest.main()

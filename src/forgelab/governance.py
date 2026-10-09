from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, TypeVar

from .domain import Role
from .tools import CommandEvidence, replace_text, run_bounded
from .quality import review_patch


class PolicyViolation(PermissionError):
    pass


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    role: str
    tool: str
    target: str
    arguments_sha256: str
    decision: str
    reason: str
    outcome: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


DEFAULT_TOOLS = {
    Role.ARCHITECT: {"repo_read", "dependency_graph"},
    Role.PROJECT_MANAGER: {"repo_read", "state_read"},
    Role.DEVELOPER: {"repo_read", "repo_edit", "shell_bounded", "destructive"},
    Role.TESTER: {"repo_read", "test_runner"},
    Role.REVIEWER: {"repo_read", "git_diff", "static_analysis"},
    Role.SECURITY: {"repo_read", "dependency_scan", "policy_check", "secret_tool", "network"},
    Role.DOCUMENTATION: {"docs_read", "docs_edit"},
    Role.SUPPORT: {"repo_read", "logs_read", "health_check"},
}


class PolicyEngine:
    def __init__(self, role_tools: dict[Role, set[str]] | None = None,
                 role_secrets: dict[Role, set[str]] | None = None,
                 network_allowlist: set[str] | None = None,
                 destructive_requires_gate: bool = True) -> None:
        self.role_tools = role_tools or {role: set(tools) for role, tools in DEFAULT_TOOLS.items()}
        self.role_secrets = role_secrets or {role: set() for role in Role}
        self.network_allowlist = network_allowlist or set()
        self.destructive_requires_gate = destructive_requires_gate

    @classmethod
    def from_directory(cls, directory: Path) -> "PolicyEngine":
        agents = json.loads((directory / "agents.yaml").read_text(encoding="utf-8"))
        policy = json.loads((directory / "policy.yaml").read_text(encoding="utf-8"))
        role_tools = {Role(name): set(config.get("allowed_tools", [])) for name, config in agents["roles"].items()}
        role_secrets = {Role(name): set(config.get("allowed_secrets", [])) for name, config in agents["roles"].items()}
        return cls(role_tools, role_secrets, set(policy.get("network_allowlist", [])), bool(policy.get("destructive_actions_require_gate", True)))

    def tool(self, role: Role, tool: str) -> PolicyDecision:
        if tool not in self.role_tools.get(role, set()):
            return PolicyDecision(False, f"{role.value} is not allowed to use {tool}")
        return PolicyDecision(True, "tool allowed for role")

    def path(self, relative_path: str, allowed_paths: set[str]) -> PolicyDecision:
        path = Path(relative_path)
        if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
            return PolicyDecision(False, "path is absolute, escapes scope, or enters .git")
        if relative_path not in allowed_paths:
            return PolicyDecision(False, "path is outside task scope")
        return PolicyDecision(True, "path is within task scope")

    def network(self, host: str) -> PolicyDecision:
        if any(fnmatch.fnmatchcase(host, pattern) for pattern in self.network_allowlist):
            return PolicyDecision(True, "host is allowlisted")
        return PolicyDecision(False, "network default deny")

    def secret(self, role: Role, name: str) -> PolicyDecision:
        if name in self.role_secrets.get(role, set()):
            return PolicyDecision(True, "secret handle allowed for role")
        return PolicyDecision(False, "secret is not allowed for role")

    def dependency(self, license_name: str | None, provenance: str | None,
                   security_review: str | None) -> PolicyDecision:
        missing = [name for name, value in {
            "license": license_name, "provenance": provenance, "security_review": security_review,
        }.items() if not value]
        if missing:
            return PolicyDecision(False, f"dependency evidence missing: {missing}")
        return PolicyDecision(True, "dependency evidence complete")

    def destructive(self, gate_decision: str | None) -> PolicyDecision:
        if self.destructive_requires_gate and gate_decision != "APPROVE":
            return PolicyDecision(False, "destructive action requires an approved gate")
        return PolicyDecision(True, "destructive action gate approved")


T = TypeVar("T")


class ToolGateway:
    def __init__(self, engine: PolicyEngine) -> None:
        self.engine = engine
        self.events: list[AuditEvent] = []

    @staticmethod
    def _hash(arguments: object) -> str:
        encoded = json.dumps(arguments, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _record(self, role: Role, tool: str, target: str, arguments: object,
                decision: PolicyDecision, outcome: str) -> None:
        self.events.append(AuditEvent(
            datetime.now(timezone.utc).isoformat(), role.value, tool, target,
            self._hash(arguments), "ALLOW" if decision.allowed else "DENY",
            decision.reason, outcome,
        ))

    def _require(self, role: Role, tool: str, target: str, arguments: object,
                 *decisions: PolicyDecision) -> None:
        denied = next((decision for decision in decisions if not decision.allowed), None)
        if denied:
            self._record(role, tool, target, arguments, denied, "BLOCKED")
            raise PolicyViolation(denied.reason)

    def edit_text(self, role: Role, workspace: Path, allowed_paths: set[str],
                  relative_path: str, old: str, new: str) -> Path:
        tool_decision = self.engine.tool(role, "repo_edit")
        path_decision = self.engine.path(relative_path, allowed_paths)
        arguments = {"path": relative_path, "old_length": len(old), "new_length": len(new)}
        self._require(role, "repo_edit", relative_path, arguments, tool_decision, path_decision)
        try:
            target = replace_text(workspace, relative_path, old, new)
        except Exception:
            self._record(role, "repo_edit", relative_path, arguments, PolicyDecision(True, "policies passed; tool failed"), "ERROR")
            raise
        self._record(role, "repo_edit", relative_path, arguments, PolicyDecision(True, "all policies passed"), "SUCCESS")
        return target

    def apply_candidate_patch(self, role: Role, workspace: Path,
                              allowed_paths: set[str], patch: str) -> None:
        """Materialize an existing text candidate inside its authorized workspace."""
        review = review_patch(patch, allowed_paths)
        headers = {f"diff --git a/{path} b/{path}" for path in allowed_paths}
        unsupported = ("rename ", "copy ", "new file mode ", "deleted file mode ",
                       "old mode ", "new mode ", "GIT binary patch", "Binary files ")
        valid = review["status"] == "PASS" and all(
            (not line.startswith("diff --git ") or line in headers)
            and (not line.startswith("--- ") or line[4:] in {f"a/{path}" for path in allowed_paths})
            and (not line.startswith("+++ ") or line[4:] in {f"b/{path}" for path in allowed_paths})
            and not line.startswith(unsupported)
            for line in patch.splitlines()
        )
        arguments = {"patch_sha256": hashlib.sha256(patch.encode("utf-8")).hexdigest()}
        self._require(role, "repo_edit", "parent-candidate", arguments,
                      self.engine.tool(role, "repo_edit"),
                      PolicyDecision(valid, "parent candidate must modify authorized text files only"),
                      *(self.engine.path(path, allowed_paths) for path in review["changed_paths"]))
        try:
            for flags in (("--check",), ()):
                result = subprocess.run(
                    ["git", "-C", str(workspace), "apply", *flags, "-"],
                    input=patch, capture_output=True, text=True, encoding="utf-8",
                    timeout=30, check=False,
                )
                if result.returncode:
                    raise ValueError("parent candidate patch does not apply: " + result.stderr.strip()[:1000])
        except Exception:
            self._record(role, "repo_edit", "parent-candidate", arguments,
                         PolicyDecision(True, "policies passed; tool failed"), "ERROR")
            raise
        self._record(role, "repo_edit", "parent-candidate", arguments,
                     PolicyDecision(True, "all policies passed"), "SUCCESS")

    def run_test(self, role: Role, workspace: Path, command: list[str], timeout: int) -> CommandEvidence:
        decision = self.engine.tool(role, "test_runner")
        arguments = {"executable": Path(command[0]).name if command else "", "argument_count": max(len(command) - 1, 0), "timeout": timeout}
        self._require(role, "test_runner", str(workspace), arguments, decision)
        result = run_bounded(command, workspace, timeout)
        self._record(role, "test_runner", str(workspace), arguments, PolicyDecision(True, "all policies passed"), f"EXIT_{result.exit_status}")
        return result

    def authorize_network(self, role: Role, host: str) -> None:
        tool_decision = self.engine.tool(role, "network")
        network_decision = self.engine.network(host)
        self._require(role, "network", host, {"host": host}, tool_decision, network_decision)
        self._record(role, "network", host, {"host": host}, PolicyDecision(True, "all policies passed"), "AUTHORIZED")

    def authorize_dependency(self, role: Role, name: str, license_name: str | None,
                             provenance: str | None, security_review: str | None) -> None:
        tool_decision = self.engine.tool(role, "dependency_scan")
        dependency_decision = self.engine.dependency(license_name, provenance, security_review)
        arguments = {"name": name, "license": license_name, "provenance": provenance, "security_review": security_review}
        self._require(role, "dependency_scan", name, arguments, tool_decision, dependency_decision)
        self._record(role, "dependency_scan", name, arguments, PolicyDecision(True, "all policies passed"), "AUTHORIZED")

    def authorize_destructive(self, role: Role, action: str, gate_decision: str | None) -> None:
        tool_decision = self.engine.tool(role, "destructive")
        gate = self.engine.destructive(gate_decision)
        self._require(role, "destructive", action, {"gate_decision": gate_decision}, tool_decision, gate)
        self._record(role, "destructive", action, {"gate_decision": gate_decision}, PolicyDecision(True, "all policies passed"), "AUTHORIZED")

    def use_secret(self, role: Role, name: str, callback: Callable[[str], T]) -> T:
        tool_decision = self.engine.tool(role, "secret_tool")
        secret_decision = self.engine.secret(role, name)
        self._require(role, "secret_tool", name, {"secret_name": name}, tool_decision, secret_decision)
        value = os.environ.get(name)
        if value is None:
            missing = PolicyDecision(False, "authorized secret is not present in environment")
            self._record(role, "secret_tool", name, {"secret_name": name}, missing, "BLOCKED")
            raise PolicyViolation(missing.reason)
        try:
            result = callback(value)
        except Exception:
            self._record(role, "secret_tool", name, {"secret_name": name}, PolicyDecision(True, "secret passed directly to tool"), "ERROR")
            raise
        self._record(role, "secret_tool", name, {"secret_name": name}, PolicyDecision(True, "secret passed directly to tool"), "SUCCESS")
        return result

    def report(self) -> dict[str, object]:
        return {
            "event_count": len(self.events),
            "denied_count": sum(event.decision == "DENY" for event in self.events),
            "events": [event.to_dict() for event in self.events],
        }

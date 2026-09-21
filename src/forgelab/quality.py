from __future__ import annotations

import re


def changed_paths(patch: str) -> set[str]:
    paths: set[str] = set()
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            paths.add(line[6:])
    return paths


def review_patch(patch: str, allowed_paths: set[str]) -> dict[str, object]:
    findings: list[dict[str, str]] = []
    actual = changed_paths(patch)
    if not patch.strip():
        findings.append({"severity": "BLOCKER", "category": "empty_diff", "description": "Patch is empty"})
    unexpected = actual - allowed_paths
    if unexpected:
        findings.append({
            "severity": "BLOCKER", "category": "scope",
            "description": f"Patch changes paths outside scope: {sorted(unexpected)}",
        })
    if not actual:
        findings.append({"severity": "BLOCKER", "category": "scope", "description": "No changed path found"})
    return {"status": "PASS" if not findings else "FAIL", "changed_paths": sorted(actual), "findings": findings}


SECRET_PATTERNS = (
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(r"(?i)(?:api[_-]?key|secret|token)\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}"),
)


def security_review_patch(patch: str) -> dict[str, object]:
    added = "\n".join(line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++"))
    findings = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(added):
            findings.append({
                "severity": "BLOCKER", "category": "secret",
                "description": "Potential secret or private key introduced by patch",
            })
            break
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}

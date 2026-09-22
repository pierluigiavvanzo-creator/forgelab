import json
import unittest
from pathlib import Path


class PackageIntegrityTests(unittest.TestCase):
    def test_required_runtime_files_are_packaged(self):
        root = Path(__file__).parents[1]
        required = [
            ".forgelab/agents.yaml",
            ".forgelab/policy.yaml",
            ".forgelab/routing.yaml",
            ".forgelab/quality-gates.yaml",
            "bootstrap.ps1",
            "Start-ForgeLab.ps1",
            "dashboard/package.json",
            "dashboard/pnpm-lock.yaml",
            "dashboard/app/page.tsx",
            "dashboard/app/globals.css",
            "dashboard/public/favicon.svg",
        ]
        missing = [name for name in required if not (root / name).is_file()]
        self.assertEqual(missing, [])

    def test_dashboard_and_core_versions_are_aligned(self):
        root = Path(__file__).parents[1]
        project = (root / "pyproject.toml").read_text(encoding="utf-8")
        package = json.loads((root / "dashboard/package.json").read_text(encoding="utf-8"))
        self.assertIn('version = "0.9.1"', project)
        self.assertEqual(package["version"], "0.9.1")


if __name__ == "__main__":
    unittest.main()

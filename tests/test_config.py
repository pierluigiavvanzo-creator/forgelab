import json
import unittest
from pathlib import Path


class ConfigurationTests(unittest.TestCase):
    def test_json_compatible_yaml_files_are_parseable(self):
        root = Path(__file__).parents[1] / ".forgelab"
        expected_versions = {"agents.yaml": 2, "policy.yaml": 2, "routing.yaml": 2}
        for name in ("agents.yaml", "policy.yaml", "routing.yaml"):
            with self.subTest(name=name):
                payload = json.loads((root / name).read_text(encoding="utf-8"))
                self.assertEqual(payload["version"], expected_versions[name])


if __name__ == "__main__":
    unittest.main()

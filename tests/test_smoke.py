import json
import tempfile
import unittest
from pathlib import Path

from forgelab.artifacts import ArtifactStore
from forgelab.smoke import run_smoke


class SmokeTests(unittest.TestCase):
    def test_smoke_emits_complete_decision_ready_run(self):
        with tempfile.TemporaryDirectory() as folder:
            run_dir = run_smoke(Path(folder))
            self.assertEqual(ArtifactStore(run_dir).missing(), [])
            summary = json.loads((run_dir / "RunSummary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "READY_FOR_DECISION")
            self.assertEqual(summary["decision"], "Human gate pending")


if __name__ == "__main__":
    unittest.main()


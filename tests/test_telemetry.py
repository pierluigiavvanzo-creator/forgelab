import json
import tempfile
import unittest
from pathlib import Path

from forgelab.telemetry import collect_kpis


class TelemetryTests(unittest.TestCase):
    def test_metrics_are_derived_from_artifacts_and_gaps_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for i,(status,repair,cost,premium,decision) in enumerate([
                ("DONE",1,1.0,.5,"APPROVE"),("READY_FOR_DECISION",0,0.0,0,"PENDING")
            ]):
                run=root/f"r{i}"; run.mkdir()
                (run/"RunSummary.json").write_text(json.dumps({"status":status,"repair_attempts":repair}))
                (run/"UsageReport.json").write_text(json.dumps({"actual_cost":cost,"premium_cost":premium}))
                (run/"GateDecision.json").write_text(json.dumps({"decision":decision}))
            kpi=collect_kpis(root)
            self.assertEqual(kpi["run_count"],2); self.assertEqual(kpi["run_success_rate"],.5)
            self.assertEqual(kpi["decision_ready_rate"],1); self.assertEqual(kpi["premium_cost_share"],.5)
            self.assertIn("economic_contribution",kpi["unavailable"])


if __name__=="__main__": unittest.main()

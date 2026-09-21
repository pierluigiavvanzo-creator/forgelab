import unittest

from forgelab.domain import AgentResult, ContractError, ResultStatus, Scope


class ContractTests(unittest.TestCase):
    def test_scope_rejects_overlap(self):
        with self.assertRaises(ContractError):
            Scope(["src"], ["src"]).validate()

    def test_pass_requires_evidence(self):
        result = AgentResult(ResultStatus.PASS, "done", [], [], [], [], "stop")
        with self.assertRaises(ContractError):
            result.validate()


if __name__ == "__main__":
    unittest.main()


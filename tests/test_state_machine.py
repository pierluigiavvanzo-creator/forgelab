import unittest

from forgelab.domain import RunStatus
from forgelab.state_machine import InvalidTransition, RunStateMachine


class StateMachineTests(unittest.TestCase):
    def test_direct_promotion_is_blocked(self):
        machine = RunStateMachine()
        with self.assertRaises(InvalidTransition):
            machine.transition(RunStatus.PROMOTE)

    def test_bounded_repair_path_is_valid(self):
        machine = RunStateMachine()
        for state in (RunStatus.PRECHECK, RunStatus.PLANNED, RunStatus.ISOLATED,
                      RunStatus.IMPLEMENTING, RunStatus.TESTING, RunStatus.DIAGNOSING,
                      RunStatus.REPAIRING, RunStatus.TESTING):
            machine.transition(state)
        self.assertEqual(machine.status, RunStatus.TESTING)


if __name__ == "__main__":
    unittest.main()


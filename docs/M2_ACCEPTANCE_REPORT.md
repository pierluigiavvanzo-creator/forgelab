# M2 Acceptance Report

Date: 2026-09-18.

## Outcome

M2 converts the pending promotion gate into an enforced human decision. A
candidate can be approved, rejected, or returned for repair. Approval is bound
to the exact repository path, reviewed commit, planned paths, passing tests,
review report, security report, and stored patch.

## Acceptance evidence

| Scenario | Result | Enforced behavior |
| --- | --- | --- |
| Human approves valid candidate | PASS | Patch applied, tests rerun, run reaches DONE |
| Human rejects candidate | PASS | Run closes and repository remains unchanged |
| Human requests repair | PASS | Run returns to REPAIRING without promotion |
| Repository changed after review | PASS | Approval is blocked before patch application |
| Patch changes path outside plan | PASS | Deterministic review blocks the run |
| Patch introduces common secret pattern | PASS | Security report blocks the run |
| Post-promotion test fails | PASS | Patch is reversed and gate records REPAIR |
| System tries to self-approve | PASS | Non-system human actor is mandatory |

## Promotion boundary

M2 applies a verified patch to a local working tree. It does not commit, push,
open a pull request, merge, deploy, or bypass repository-provider protections.
Those operations require their own explicit policy and external-action gate.

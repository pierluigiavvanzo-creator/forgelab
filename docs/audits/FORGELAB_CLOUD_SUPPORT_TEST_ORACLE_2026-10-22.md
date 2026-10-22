# ForgeLab — Cloud Support and generated-test repair guard — 2026-10-22

## Result and scope

**PASS on the single authorized synthetic end-to-end gate.** Base main `c4ff897` includes merged PR #79; implementation branch `codex/cloud-support-test-oracle`. This Class A change addresses the incorrect local Support diagnosis that caused the PR #79 candidate to round totals to tens to satisfy a wrong generated assertion. Product value: remove that observed repair failure path while preserving independent verification and human promotion.

The PO authorizes SUPPORT and REVIEWER to share one cloud policy: `gemma4:31b-cloud` primary, `gpt-oss:120b-cloud` alternative only on unavailability, recorded as reduced independence. Quota/credit/billing/402/429 stops, never local. Planner remains S1/local `qwen2.5-coder:7b`; Aider's editor chain remains gpt-oss then Gemma. Only signed-in loopback Ollama, EUR 0 and synthetic data. No Dental, purchases, promotion or service restart. Merge is authorized by the passing gate, not by the unit suite alone.

## Bounded implementation / reuse

- Generalized PR #79's reviewer route into `execute_cloud_role`, one validated configuration and role-aware errors/UsageRecords. Generic SUPPORT calls bypass S2's local retry route. The reviewer wrapper delegates to the same implementation; no duplicate fallback policy. `SupportFailure.json` records terminal reason and attempts, alongside the existing reviewer artifact. The prior Task E-only gpt-oss-primary override is not an accepted configuration for this shared chain.
- Reused PR #75's provider-error classifier, PR #78 context sizing/truncation checks, strict reviewer schema, loopback guard, Aider engine/version/whole-format/flags and timeout ceilings. No dependencies added; routing.yaml and Planner policy unchanged.
- A shared prompt rule appears in Support and all eight repair/correction builders, including prewrite and semantic paths. Generated tests are not an oracle: recompute expectations from objective and inputs, fix an incorrect TEST, preserve coverage, and never introduce objective-unrelated rounding/bucketing solely to satisfy an assertion.
- Support previously saw test logs but not complete current candidate files. It now receives the authorized implementation/tests and PM acceptance contract using the existing scoped read helper and its file/total size limits. This supplies the evidence needed to apply the rule.
- Launcher/dashboard now describe cloud Reviewer/Support and local Planner. Existing running services were not restarted.

## Automated verification

Focused routing/STOP suite: **31 PASS** (3.044 s); focused production Support and Aider repair paths: **3 PASS** (3.333 s). Full Python suite: **216 PASS** (78.897 s), `python -m unittest discover -s tests -q` under the existing Aider Python environment, `PYTHONPATH=src;tests`.

Coverage includes primary Support routing; unchanged local Planner; 404/410/retired/not-found switch once; quota precedence and stop on either model; both unavailable; no local fallback; provider transient stop; successful text not parsed as provider errors; approved configuration validation; production Support quota artifact/closed run; complete candidate context and rule in actual Support/repair prompts; rule presence in every correction builder. No real inference in unit tests. No additional full-suite run after documentation-only changes.

## Exactly one real end-to-end run

Production entry point: `run_multi_agent`, run `cloud-support-1`; fresh protected inventory repository. No mocked planner/reviewer/support/editor responses, no dashboard token. Observation wrappers only call/return the real implementations and capture evidence.

- Objective SHA-256: `ebb6eb21a7293a6850eece17653625f949067ffdfeafb90cf8cada10446ba5f0` (clean first paragraph, no stale blocking review).
- Protected `inventory_app.py`: `6c381b013d1f1f7f14612dc5a9ddb4c59a03ef3179172cd411e90a36a3315b7b`.
- Protected `test_inventory_app.py`: `15250df0fdfead0261a98aacee5fb0416fbf6091653230bfe40e4e1d101a8061`.
- Request `max_repair_attempts=2`; actual repairs **1**, Aider calls **2**, both exit 0, no timeout. Request defaults and production ceilings unchanged; no external retries or second run.
- Duration **120.063 s**. Final **READY_FOR_DECISION**, generated tests **11/11**, child exit **0**, independent acceptance **6/6**, zero failures/errors. Gemma's strict review **PASS**, findings empty; code inspection confirms exact-three validation, sum of subtotals and aggregate discount. No blocking finding contradicted by code.
- Human gate remains **PENDING**, no approval/promotion. Protected fixture and synthetic source repository unchanged. Ollama log window complete; no truncation warning.

Phase history: RECEIVED → PRECHECK → PLANNED → ISOLATED → IMPLEMENTING → TESTING → DIAGNOSING → REPAIRING → TESTING → SMOKE_TEST → REVIEW → SECURITY_CHECK → READY_FOR_DECISION.

| Role/call | Model | Input tokens | Output tokens | Latency |
|---|---|---:|---:|---:|
| Planner | qwen2.5-coder:7b local | 1,284 | 679 | 44.407 s |
| Editor initial | gpt-oss:120b-cloud | captured in local completion log | captured in local completion log | 19.733 s |
| Support | gemma4:31b-cloud | 4,635 | 506 | 2.109 s |
| Editor repair | gpt-oss:120b-cloud | captured in local completion log | captured in local completion log | 49.780 s |
| Reviewer | gemma4:31b-cloud | 4,716 | 955 | 2.952 s |

Combined editor usage: **7,366 input + 4,384 output**. Total cloud usage **22,562 tokens** (16,717 input + 5,845 output); local Planner **1,963 tokens**. All cloud role attempts used the primary; no fallback/quota error observed. Cost ledger **EUR 0**, no purchase or billing action. Account-side usage/debits cannot be independently read by this task.

### What the repair actually did

Initial generated tests had one error: `test_current_single_entry_point` called the CLI with one item and expected a stdout error/normal return, but `argparse.error()` raises `SystemExit(2)`. Support traced the actual input and exception path, recognized correct exact-three implementation behavior, and proposed `assertRaises(SystemExit)` in the TEST. The editor changed only `test_inventory_app.py`; the implementation is byte-identical between the two editor results. No rounding-to-tens or other assertion-fitting implementation was added. The new tests use aggregate 50/discounted 45; the independent checker separately verifies aggregate 45/final 40.5, count rejection, invalid inputs, helper compatibility and discount boundaries.

## Evidence, limits and delivery

Local ignored evidence: `.forgelab/runtime/semantic-completion-audit/cloud-support-production-2026-10-22/`: `python-suite.txt`, service snapshots, `run-1/request.json`, `objective.txt`, `observations.jsonl`, editor results, `cloud-completions.jsonl`, `postcheck.json`, `ollama.log`, resource samples, production artifacts under `run-1/runs/cloud-support-1/`, and independent checker/candidate under `run-1/acceptance/`. The checker reconstructs the final production Changes.patch and reuses the existing six-case acceptance harness without altering assertions. No model calls in postcheck.

Ollama 0.40.4 reachable. Service listener PIDs unchanged before/after: Ollama 1980, ForgeLab API 62456, dashboard 62440. Minimum observed free physical RAM: 1.691 GiB (sampled, not a continuous bound). Runtime evidence is ignored and excluded from the PR; no credentials were accessed or added.

**VERIFIED:** bounded code/test changes, actual cloud Support and Reviewer, one successful synthetic run, independent 6/6, pending human gate, unchanged services/source, EUR 0 ledger. **NOT VERIFIED:** general reliability, guaranteed prevention of future fit-the-test reasoning, the exact previous arithmetic failure reproduced under the new model, live fallback/quota behavior (unit tested only), remaining Free-plan capacity, Dental transfer/readiness, or updated behavior in already-running services. Support and Reviewer share a model family; independence is from the gpt-oss editor, not from each other. Prompt instructions reduce the observed risk; deterministic tests and independent review remain essential.

Delivery: one code + documentation PR from `codex/cloud-support-test-oracle`; merge authorized because the full requested gate passes. No second run. Rollback: revert this change set (or its merge commit), retaining prior PR #79 behavior and evidence; do not alter runtime candidates.

**Single next action:** PO reads the Ollama session/weekly usage page to assess remaining Free-plan capacity before authorizing any further real workload. Dental remains separately undecided.

# DECISIONS.md

## D-001 — Product before infrastructure

**Date:** 2026-09-22
**Status:** Accepted

ForgeLab development is frozen at the infrastructure layer unless a real MVP test exposes a concrete product blocker.

Reason: the project has accumulated substantial technical capability, but usable product value must now be demonstrated through a real external-application workflow.

---

## D-002 — MVP status

**Date:** 2026-09-22
**Status:** Accepted

ForgeLab is classified as:

**PRE-MVP / technically capable**

It must not be called MVP-complete until all five MVP gates pass on a real external application:

1. usability;
2. autonomy;
3. real output;
4. quality;
5. human control.

---

## D-003 — Product Owner role

**Date:** 2026-09-22
**Status:** Accepted

The Product Owner is approver and final usability tester.

Routine use must not require the Product Owner to act as repetitive QA, debugger, log transporter, retry orchestrator or executor of long micro-command sequences.

---

## D-004 — Canonical M8.9 baseline

**Date:** 2026-09-22
**Status:** Accepted

The validated ForgeLab M8.9 baseline is:

- commit `58d22eeca66c27871738c04c6d850c59efabf115`
- tree `63b6c91427edb19cd038cf557904451dfc08a947`
- 168 tracked canonical files
- canonical manifest SHA-256 `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3`

This record documents the validated source state at M8.9 acceptance.

---

## D-005 — Initial GitHub repository role

**Date:** 2026-09-22
**Status:** Superseded by D-007

The repository `pierluigiavvanzo-creator/forgelab` was initially established as shared remote project/governance memory before the full validated source was synchronized.

This decision is preserved as historical context and is superseded by D-007 after successful source synchronization and local alignment.

---

## D-006 — Repository-first

**Date:** 2026-09-22
**Status:** Accepted

Before substantial custom development, evaluate mature reuse candidates when reuse could materially reduce time, cost or risk.

Track candidates through:

`DISCOVERED -> BENCHMARKED -> ADOPTED | REJECTED -> INTEGRATED -> USED`

Discovery alone does not count as reuse.

This rule must not become an excuse to delay MVP validation when the current system can already perform the required product test.

---

## D-007 — GitHub main is canonical shared source of truth

**Date:** 2026-09-22
**Status:** Accepted

The validated M8.9 source baseline was published to `baseline/m8.9-local`, integrated with canonical governance on `integration/m8.9-code-plus-governance`, and merged through PR #2.

PR #2 merge commit:

`9560729bfc9f27422d92d20d8fb43db5886a1cba`

Decision:

- GitHub `pierluigiavvanzo-creator/forgelab` on `main` is the canonical shared source of truth for ForgeLab code and governance;
- the local checkout tracks that history;
- no force or rebase is used for synchronization;
- future material changes continue to follow governed branch/review/approval discipline.

---

## D-008 — ForgeLab is the primary software factory; Golden Path outranks infrastructure

**Date:** 2026-09-30
**Status:** Accepted

ForgeLab is the primary product: a provider-replaceable software/product creation platform that must own the workflow from Product Owner objective through planning, implementation, deterministic verification, bounded repair, independent review, working preview and explicit human promotion.

Decision:

- do not use ChatGPT chat as ForgeLab's orchestration layer;
- prefer the local zero-cost Ollama path where practical while keeping the provider replaceable;
- prioritize product-level Golden Path failures over generic infrastructure or refactor work;
- after Dental Quote PASS, validate generality on a small CRUD SaaS and an automation/reporting tool;
- defer multi-tenancy, billing, advanced scaling, broad observability, paid-provider expansion and unrelated architecture work until product evidence requires them;
- preserve explicit Product Owner approval before promotion.

Rationale:

The primary risk is no longer lack of infrastructure. It is failure to convert an objective into a genuinely usable software product with low Product Owner effort.

---

## D-009 — Project Manager acceptance contract must govern implementation

**Date:** 2026-10-01
**Status:** Accepted — PR #20 merged 2026-10-01

Evidence:

Dental Quote run `run-6a0c2c512498` passed deterministic tests after a bounded repair but failed independent semantic review because the generated application did not satisfy the complete three-treatment objective.

Root cause:

The Project Manager produced a plan, but the Developer did not consume that plan or its acceptance criteria before implementation.

Decision candidate:

- Project Manager output must be structured, not advisory free text;
- explicit Product Owner obligations must be decomposed into binding `acceptance_criteria`;
- quantitative requirements such as exact counts, "three", "each", "all", percentages and limits must be preserved;
- the Project Manager must not invent new product scope;
- Developer and bounded repair paths must consume the same acceptance contract;
- independent Reviewer must continue evaluating the original Product Owner objective rather than inheriting the PM contract as truth;
- existing isolation, ToolGateway, test, repair-budget and human-promotion controls remain unchanged.

Rationale:

A multi-agent plan that is stored but not consumed does not govern execution. Propagating the acceptance contract closes that gap without adding agents, dependencies or infrastructure.


---

## D-010 — End-to-end acceptance and grounded reviewer evidence

**Date:** 2026-10-01
**Status:** Proposed in PR #22; becomes Accepted only if PR #22 is explicitly approved and merged

Evidence:

Dental Quote rerun `run-c135dcec0887` after PR #20 showed that structured PM acceptance criteria materially improved Developer output, but the generated application still stopped at helper/backend coverage while the existing Tkinter interface remained a one-treatment workflow. The Reviewer blocked promotion correctly, yet described present-but-incomplete implementation/tests as absent.

Decision candidate:

- Project Manager may inspect the complete authorized target files as bounded read-only planning context;
- when an existing user-facing interface or entry point is inside authorized scope, Developer must wire user-visible requirements through it;
- helper/backend functions alone do not satisfy an end-to-end user-visible requirement;
- Developer must self-check every acceptance criterion against implementation and tests before returning;
- Reviewer must inspect complete final authorized candidate files in addition to patch and deterministic test evidence;
- Reviewer must distinguish absent behavior from partially implemented or insufficiently evidenced behavior;
- Reviewer remains independent and continues to judge the original Product Owner objective rather than inheriting PM conclusions;
- existing isolation, ToolGateway, repair budget, deterministic test gate and human promotion gate remain unchanged.

Rationale:

The next product risk is not planning availability but incomplete vertical-slice execution and imprecise semantic evidence. The smallest safe correction is to make planning file-aware, implementation explicitly end-to-end, and review grounded in the complete candidate state.

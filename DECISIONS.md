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

The local ForgeLab `main` was then fast-forwarded to the same GitHub `main` commit and verified clean.

Decision:

- GitHub `pierluigiavvanzo-creator/forgelab` on `main` is the canonical shared source of truth for ForgeLab code and governance;
- the local checkout tracks that history;
- no force or rebase was used for synchronization;
- future material changes continue to follow governed branch/review/approval discipline.

This synchronization does not change product status: ForgeLab remains PRE-MVP until the real application MVP gates pass.

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

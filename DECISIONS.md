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

## D-004 — Canonical local baseline

**Date:** 2026-09-22  
**Status:** Accepted

The validated local ForgeLab baseline is:

- commit `58d22eeca66c27871738c04c6d850c59efabf115`
- tree `63b6c91427edb19cd038cf557904451dfc08a947`
- 168 tracked canonical files
- manifest SHA-256 `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3b`

This record documents the validated local source state.

---

## D-005 — GitHub repository role

**Date:** 2026-09-22  
**Status:** Accepted

The repository `pierluigiavvanzo-creator/forgelab` is established as the shared remote project/governance memory.

Until the local 168-file source baseline is explicitly synchronized and verified, GitHub must not be described as containing the complete validated ForgeLab implementation.

---

## D-006 — Repository-first

**Date:** 2026-09-22  
**Status:** Accepted

Before substantial custom development, evaluate mature reuse candidates when reuse could materially reduce time, cost or risk.

Track candidates through:

`DISCOVERED -> BENCHMARKED -> ADOPTED | REJECTED -> INTEGRATED -> USED`

Discovery alone does not count as reuse.

This rule must not become an excuse to delay MVP validation when the current system can already perform the required product test.

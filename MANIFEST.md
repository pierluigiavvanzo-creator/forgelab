# MANIFEST.md — ForgeLab

**Version:** 1.0-MVP  
**Date:** 2026-09-22  
**Status:** Pre-MVP / MVP validation active

## 1. Mission

ForgeLab is a governed multi-agent software-development control plane.

It converts a Product Owner objective into a software-development run that can:

- understand project memory and relevant repository context;
- plan work;
- select the minimum necessary agents;
- implement changes in an isolated workspace;
- use deterministic tools for writes, tests and evidence;
- diagnose and repair failures within bounded limits;
- perform independent review and security checks;
- present a decision-ready result;
- promote only after explicit human approval.

ForgeLab is not successful because it has many agents or many tests. ForgeLab is successful when it produces usable software outcomes with low Product Owner effort.

## 2. Strategic objective

Every material ForgeLab capability must contribute measurably to the broader goal of creating EUR 2,000,000 of additional economic value within five years.

ForgeLab may contribute through:

- developer time saved;
- reduced software-development cost;
- reusable IP;
- faster creation of monetizable applications;
- direct SaaS/licensing revenue;
- increased throughput across other portfolio projects.

No monetary value may be claimed without measured evidence.

## 3. Primary metric

`ECONOMIC VALUE × USABLE PRODUCT VALUE / USER TIME`

Do not optimize for lines of code, agent count, token count, test count, architecture complexity or number of milestones.

## 4. Product Owner contract

The user is:

- Product Owner;
- approver;
- final usability tester.

The user is not normally:

- QA operator;
- debugger;
- log transporter;
- dataset annotator;
- retry orchestrator;
- executor of long command sequences.

A workflow that routinely requires those behaviors is a product defect.

## 5. Product workflow

`OBJECTIVE`
→ `PROJECT/REPO CONTEXT`
→ `PLAN`
→ `AGENT SELECTION`
→ `ISOLATED IMPLEMENTATION`
→ `DETERMINISTIC TEST`
→ `BOUNDED DIAGNOSIS/REPAIR IF NEEDED`
→ `SMOKE`
→ `INDEPENDENT REVIEW`
→ `SECURITY`
→ `READY_FOR_DECISION`
→ `APPROVE | REJECT | REPAIR`
→ `EXACT REVIEWED PROMOTION`
→ `VERIFIED USABLE OUTPUT`

## 6. Agent roles

Available specialized roles:

- Architect
- Project Manager
- Developer
- Tester
- Reviewer
- Security
- Documentation
- Support

Agents are roles, not mandatory always-on processes. Use only the minimum roles required by the task.

## 7. Non-negotiable governance

Preserve:

- isolated workspace/worktree execution;
- no direct-main writes by execution agents;
- explicit allowed write paths;
- ToolGateway as authoritative write boundary;
- deterministic external verification;
- bounded repair attempts;
- evidence-backed diagnostics;
- independent review;
- security checks;
- explicit Product Owner promotion gate;
- exact reviewed-diff promotion;
- no automatic push;
- no automatic merge;
- no force operations;
- consumed/stale approvals cannot be reused;
- secret filtering;
- read-only repository context cannot expand write scope;
- UTF-8/BOM and Windows LF/CRLF-safe behavior.

## 8. Repository-first policy

Before material custom development, assess mature external candidates when reuse could materially reduce time, cost or risk.

For each candidate record:

- license/terms;
- maintenance status;
- maturity/adoption;
- compatibility;
- security/privacy;
- integration cost;
- lock-in;
- commercial suitability.

Lifecycle:

`DISCOVERED -> BENCHMARKED -> ADOPTED | REJECTED -> INTEGRATED -> USED`

A candidate counts as reuse only at `USED`.

Repository-first work must be proportional: it must not delay a real MVP when the missing capability already exists and works.

## 9. Work classification

Every significant work item is classified:

- **A — Product Critical**
- **B — Material Upgrade**
- **C — Optimization**
- **D — Diagnostic / Technical**

User manual effort on D work is exceptional and justified only by material A-level risk.

## 10. Current validated technical baseline

Current local ForgeLab baseline:

- root: `C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`
- canonical Git branch: `main`
- baseline commit: `58d22eeca66c27871738c04c6d850c59efabf115`
- baseline tree: `63b6c91427edb19cd038cf557904451dfc08a947`
- tracked canonical files: 168
- manifest SHA-256: `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3b`
- regression tests: 88 PASS
- API `/health`: HTTP 200
- dashboard `/`: HTTP 200
- Git remotes: 0 at checkpoint
- remote publication: none at checkpoint

Validated capabilities include:

- single- and multi-file bounded AI development;
- deterministic testing;
- bounded repair;
- read-only repository context selection;
- independent review/security;
- human-approved exact promotion.

## 11. Current product status

**PRE-MVP**

Technical capability is substantial.

The project must not claim MVP completion until a real external application completes the user-facing workflow with minimal Product Owner intervention.

Infrastructure expansion is frozen except when required by a concrete failed MVP gate.

## 12. MVP-1

### Name

`FORGELAB_MVP_1_REAL_APPLICATION_TEST`

### Objective

Prove ForgeLab can modify a real small application from the dashboard and deliver a verified usable result.

### Recommended task

Use a small external application such as a Dental Quote Calculator.

Example objective:

> Add support for three treatments, automatic subtotals, percentage discount and final total. Validate inputs. Modify only necessary files. Add tests. Do not change dependencies or configuration unless necessary and explicitly justified.

### Required Product Owner journey

1. Open dashboard.
2. Select/register target project.
3. Enter objective.
4. Run.
5. Inspect decision-ready output.
6. APPROVE / REJECT / REPAIR.
7. If approved, verify the promoted application works.

## 13. MVP gates

ForgeLab MVP-1 is PASS only when all five pass:

### G1 — Usability

The Product Owner can initiate the run from the dashboard.

### G2 — Autonomy

No ordinary manual debugging, log transport or retry orchestration.

### G3 — Real output

The target application visibly implements the requested behavior.

### G4 — Quality

Required tests, review and security checks pass.

### G5 — Human control

Nothing is promoted before explicit Product Owner approval.

## 14. Failure rule

If MVP-1 fails:

- identify the single blocking product gap;
- do not create a broad infrastructure milestone;
- make the smallest safe correction;
- rerun the same MVP scenario.

Do not compensate for poor UX with more manual PowerShell instructions.

## 15. Minimum product KPIs

Measure for every real run:

- run success rate;
- user touches per run;
- Product Owner active minutes;
- time to usable output;
- repair efficiency;
- LLM/provider cost;
- escape defects;
- reusable component ratio;
- estimated time/cost saved.

Primary MVP economic KPI:

`USER_TIME_SAVED_PER_SUCCESSFUL_RUN`

## 16. Product Definition of Done

A ForgeLab capability is DONE only when:

- it produces a usable output;
- required evidence exists;
- unresolved blockers do not remain;
- the change stays within authorized scope;
- project memory remains coherent;
- Product Owner intervention is appropriate to the risk;
- the result improves usable product value, economic potential, necessary reliability, or user-time reduction.

Green tests alone are not sufficient.

## 17. Current priority

**A — Product Critical**

`FORGELAB_MVP_1_REAL_APPLICATION_TEST`

Do not prioritize remote publication, advanced observability, scale, multi-tenancy or billing before MVP evidence unless they are proven blockers.

## 18. Source of truth

Canonical project memory should remain repository-backed:

- `MANIFEST.md`
- `AGENTS.md`
- `PROJECT_STATE.md`
- `ROADMAP.md`
- `DECISIONS.md`
- `docs/handovers/HANDOVER_CURRENT.md`
- relevant ADRs
- `.forgelab` policy/config files

A new session must be able to reconstruct what is known, decided, tested and next without depending on chat history.

## 19. Reporting format

Every material milestone closes with:

### IMPORTANZA
Class and expected value.

### RISULTATO / DECISIONE
What changed and evidence.

### BLOCCO
Only real blockers/gates.

### PROSSIMO PASSO
One preferred next action with owner.

## 20. Immediate next action

`FORGELAB_MVP_1_REAL_APPLICATION_TEST`

No further infrastructure work unless the MVP test supplies concrete evidence that it is required.

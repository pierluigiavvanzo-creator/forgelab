# ForgeLab Agent Rules

Read `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, relevant ADRs, and the
files under `.forgelab/` before changing the project.

Work in this order: precheck, isolate, implement, test, diagnose, repair,
smoke test, report. Keep repair loops bounded and form a new hypothesis before
repeating a failed check.

Do not write to a protected branch, expose secrets to prompts, bypass a gate,
expand scope silently, or treat model claims as test evidence.

Every completed task must update canonical project state when the material
state changed. Report importance, result, blockers, and one next action.


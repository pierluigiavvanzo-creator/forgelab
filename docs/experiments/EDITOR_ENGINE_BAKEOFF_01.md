# EDITOR_ENGINE_BAKEOFF_01

**Date:** 2026-10-05  
**Status:** Harness candidate ready / real Aider-Ollama execution not yet run  
**Class:** A — Product Critical

## Purpose

Test whether a mature reusable code-editing engine can reduce the malformed-edit
failures seen in the custom ForgeLab LLM-to-edit boundary without weakening
ForgeLab governance.

This experiment does not replace ForgeLab and does not modify the normal
Golden Path yet.

## Candidate boundary

```text
ForgeLab experiment harness
  -> EditorAdapter
  -> Aider CLI
  -> disposable editor sandbox
  -> candidate file contents
  -> Python compile gate
  -> deterministic test command
  -> deterministic scope review
  -> deterministic security review
  -> machine-readable EditorBakeoff report
```

The governed source repository is never passed to Aider as its working
directory.

## Safety controls

The Aider adapter:

- copies only explicitly authorized writable files;
- may copy explicit bounded read-only context files;
- runs with `--no-git`;
- disables auto commits, auto lint, auto tests and shell suggestions;
- disables analytics, update checks and release-note checks;
- overrides HOME/USERPROFILE to the disposable sandbox;
- strips known paid-provider API keys and inherited `AIDER_*` settings;
- rejects read-only file modification;
- rejects creation of non-hidden source files outside the visible authorized
  set;
- never writes the governed ForgeLab workspace;
- returns candidate file contents for ForgeLab-side validation.

No Aider dependency is added to ForgeLab's runtime package in this candidate.

## Deterministic validation

The harness:

1. rejects returned/changed paths outside the authorized set;
2. compiles every Python candidate with `compile(..., "exec")`;
3. creates a unified patch against the source repository;
4. runs existing deterministic scope review;
5. runs existing deterministic security review;
6. applies candidate files only to a disposable test copy of the repository;
7. runs only a bounded Python test command;
8. writes a machine-readable report.

Semantic LLM review is deliberately deferred in this first boundary experiment,
as required by ADR-002. The first question is whether the edit boundary itself
is materially more reliable.

## Focused verification completed

Executed independently against the exact candidate module contents:

- editor adapter tests: 5 / 5 PASS;
- bakeoff evaluator tests: 5 / 5 PASS;
- combined focused suite: 10 / 10 PASS;
- `editor_adapter.py`: Python compile PASS;
- `editor_bakeoff.py`: Python compile PASS;
- modified `cli.py`: Python compile PASS.

Covered behaviors:

- source repository remains unchanged;
- read-only mutation is rejected;
- path traversal is rejected;
- new source-file creation is rejected;
- paid-provider keys and inherited Aider settings are stripped;
- compile-invalid Python is stopped before tests;
- good candidate reaches deterministic tests;
- out-of-scope returned files are rejected;
- machine-readable report is produced;
- Windows `py -3.11` test command is normalized for the experiment.

## Not yet claimed

This candidate does **not** claim:

- Aider is better than the current ForgeLab editor;
- Dental Quote succeeds;
- semantic acceptance succeeds;
- Aider is installed on the Product Owner workstation;
- Aider should become a permanent dependency;
- ADR-002 is Accepted.

Those require real comparative evidence after this harness is reviewed and
merged.

## Next step after merge

Run the bounded Aider/Ollama editor experiment on the unchanged Dental Quote
baseline and compare its edit-boundary evidence with the existing custom
ForgeLab path.

Only after comparative evidence should ForgeLab choose:

`ADOPT AIDER ADAPTER | REJECT AIDER | BENCHMARK NEXT EDITOR`

No Product Owner PowerShell debug loop is part of this experiment.

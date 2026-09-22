# M1 Acceptance Report

Date: 2026-09-18.

## Outcome

M1 provides an end-to-end isolated runner for a bounded software change. The
integration test initializes a clean Git repository containing a failing
calculator implementation, creates a detached worktree, changes subtraction to
addition, runs the repository test suite, captures the resulting patch, removes
the worktree, and proves that the source repository HEAD and files are unchanged.

## Acceptance evidence

| Criterion | Result | Evidence |
| --- | --- | --- |
| Source must be a clean Git repository | PASS | Dirty repositories are rejected by `IsolatedWorkspace.create` |
| Work occurs outside source checkout | PASS | Git detached worktree in a unique temporary directory |
| Edit is path bounded | PASS | Absolute paths, `.git`, and workspace escapes are rejected |
| Test command is bounded | PASS | No shell; executable allowlist; timeout; captured output and status |
| Candidate survives worktree cleanup | PASS | Binary-capable `Changes.patch` artifact |
| Main/source remains unchanged | PASS | HEAD and porcelain status checked before cleanup |
| Human gate remains mandatory | PASS | Run ends at `READY_FOR_DECISION` with `PENDING` gate |
| External model cost | PASS | Zero LLM calls and zero estimated cost |

## Limitation

M1 supports one `replace_text` operation and Python test commands. This is a
deliberate product slice, not a general code-writing agent. M2 must implement
review and approved patch promotion before use on valuable repositories.

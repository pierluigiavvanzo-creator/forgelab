# Local Source Baseline

**Checkpoint:** M8.9 technical acceptance
**Date:** 2026-09-22

## Validated M8.9 source

- root at acceptance: `C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`
- branch at acceptance: `main`
- baseline commit: `58d22eeca66c27871738c04c6d850c59efabf115`
- baseline tree: `63b6c91427edb19cd038cf557904451dfc08a947`
- tracked canonical files: 168
- canonical manifest SHA-256: `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3`

## Acceptance evidence

- 88 regression tests PASS;
- Python unittest exit code 0;
- API `/health`: HTTP 200;
- dashboard `/`: HTTP 200;
- protected unauthenticated API behavior: HTTP 401;
- HEAD/tree unchanged after validation;
- working tree clean.

## Synchronization completion

The historical M8.9 baseline was subsequently synchronized to GitHub and integrated with canonical governance:

- `baseline/m8.9-local` -> `58d22eeca66c27871738c04c6d850c59efabf115`;
- integration branch `integration/m8.9-code-plus-governance`;
- integration commit `8dfd9c81a9c8b1c17ef16833beaef7cc437c46a4`;
- PR #2 merged into `main`;
- merge commit `9560729bfc9f27422d92d20d8fb43db5886a1cba`;
- local `main` fast-forwarded to the same GitHub `main` commit and verified clean;
- no force push or rebase used.

This file records the historical M8.9 acceptance baseline. GitHub `pierluigiavvanzo-creator/forgelab` on `main` is now the canonical shared source of truth for ongoing ForgeLab code and governance.

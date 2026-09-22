# Local Source Baseline

**Checkpoint:** M8.9 technical acceptance  
**Date:** 2026-09-22

## Validated local source

- root: `C:\Users\NITRO\source\FORGELAB_M8_1_v0.9.1`
- branch: `main`
- commit: `58d22eeca66c27871738c04c6d850c59efabf115`
- tree: `63b6c91427edb19cd038cf557904451dfc08a947`
- tracked canonical files: 168
- canonical manifest SHA-256: `62bade56363d082d2f183e5f33706d96e360bacdec890a6b8102d96b9bee0f3b`

## Acceptance evidence

- 88 regression tests PASS;
- Python unittest exit code 0;
- API `/health`: HTTP 200;
- dashboard `/`: HTTP 200;
- protected unauthenticated API behavior: HTTP 401;
- HEAD/tree unchanged after validation;
- working tree clean;
- no remote/push/merge/force/publication at checkpoint.

## Remote synchronization warning

This document records a **local validated baseline**.

It does not prove that the complete local source is present in this GitHub repository.

The GitHub remote must be treated as governance/project memory until a separate source-sync verification explicitly compares remote contents against this baseline.

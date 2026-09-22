# M8.1 Package Repair Acceptance Report

Date: 2026-09-19

## Outcome

M8.1 repairs the incomplete M8 distribution and turns the separate dashboard
into a reproducible local Control Plane package.

## Accepted capabilities

- All four canonical `.forgelab` configuration files are present in the package.
- The complete dashboard source is packaged with the Python control-plane core.
- A local API exposes an allowlist of run artifacts and stages gate decisions.
- The API requires a bearer token, enforces an exact browser origin, and binds
  only to loopback addresses.
- Staged decisions explicitly record `promotion_executed: false`.
- `bootstrap.ps1` validates Python, runs the complete suite, executes smoke, and
  reports evidence-backed metrics.
- `Start-ForgeLab.ps1` launches API and dashboard and passes the ephemeral token
  through a URL fragment that the dashboard removes immediately.
- Package-integrity tests prevent recurrence of the missing-config and empty-
  dashboard defects.

## Boundary

M8.1 does not add a production remote API, live LLM provider, automatic commit,
push, merge, or promotion. The authenticated connection is deliberately local.

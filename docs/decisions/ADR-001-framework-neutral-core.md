# ADR 001 Framework Neutral Core

## Status

Accepted.

## Context

ForgeLab needs durable state, human gates, isolated workspaces, structured
evidence, and replaceable model providers. Agent frameworks differ in runtime
model and deployment assumptions.

## Decision

Domain contracts and orchestration state belong to ForgeLab. Framework adapters
may implement planning or agent execution but may not redefine persistence,
evidence, permissions, or promotion rules.

## Consequences

M0 has no agent-framework runtime dependency. M1 must compare at least one
framework adapter with a minimal direct adapter against the same acceptance
scenario.


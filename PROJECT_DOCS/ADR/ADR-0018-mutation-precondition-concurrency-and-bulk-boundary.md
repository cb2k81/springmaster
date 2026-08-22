---
documentId: ADR-0018
title: Mutation Precondition, Concurrency and Bulk Boundary
documentType: adr
status: accepted
authority: normative
scopeLevel: ecosystem
scopePaths:
  - springmaster/standards
appliesTo:
  - springmaster
  - generated-projects
owner: springmaster-maintainers
createdAt: 2026-08-20
validFrom: 2026-08-20
lastReviewedAt: 2026-08-20
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-003
---
# ADR-0018 Mutation Precondition, Concurrency and Bulk Boundary

## Context

Optimistic locking is established, while cross-application contracts need explicit precondition, history, projection, consistency and bulk classifications without turning application-specific locking or background processing into generic runtime law.

## Decision

1. Preconditions are exactly `NONE`, `EXPECTED_VERSION`, `EXPECTED_VERSION_SET`, `SNAPSHOT_TOKEN` and `ETAG`. A business/body version conflict returns `409`; a violated `If-Match` returns `412`; a missing mandatory HTTP precondition returns `428`.
2. Optimistic locking remains the baseline. `PESSIMISTIC` and `MIXED` are additive use-case strategies. Pessimistic and mixed operations still expose a version token where mutation safety requires it. Concrete lock order is application-specific.
3. Transaction scopes are exactly `SINGLE_AGGREGATE`, `AGGREGATE_GRAPH` and `MULTI_AGGREGATE`.
4. History models are exactly `NONE`, `ROOT_VERSION`, `PLAN_SNAPSHOT`, `APPEND_ONLY` and `TEMPORAL_RELATION`. Temporal context is explicit. A projection is a read contract with a declared response schema and is never a mutable entity. Append-only resources reject standard update/delete mutations.
5. Composite Command, Backend Bulk Command, GWC Batch and Background Job are distinct. A bulk contract defines Selection, Atomicity, Execution, Target Authorization, Non-Disclosure, Idempotency, Limits, Outcomes and Result Delivery. Query selection is frozen before execution. `202` is allowed only with observable status and result contracts. Generic HTTP `207` is not used.
6. Sprint 003 defines and qualifies these contracts but does not add a generic history, multi-aggregate lock, bulk, job, export, aggregation, delta or workspace runtime.

## Consequences

Snapshot tokens require a declared producer. Target-sensitive selection requires target context and execution-time authorization. Non-disclosure is explicit. Synchronous and asynchronous outcomes remain contract-specific rather than hidden behind a generic runtime.

## Verification

Schema fixtures cover each allowed value and negative boundary. Runtime evidence is limited to explicitly `REFERENCE_IMPLEMENTED` targets and the Team-Membership candidate/reference slice.

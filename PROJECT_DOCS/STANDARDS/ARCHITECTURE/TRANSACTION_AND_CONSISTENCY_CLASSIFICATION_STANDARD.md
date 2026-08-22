---
documentId: STD-ARCH-TRANSACTION-CONSISTENCY-001
title: Transaction and Consistency Classification Standard
documentType: standard
status: active
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
reviewBy: 2026-11-20
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-003
---
# Transaction and Consistency Classification Standard

Transaction scope is exactly `SINGLE_AGGREGATE`, `AGGREGATE_GRAPH` or `MULTI_AGGREGATE`. Consistency strategy is `OPTIMISTIC`, `PESSIMISTIC` or `MIXED`; optimistic locking remains the baseline and the other values are explicit use-case additions.

The application boundary owns the transaction. A command must declare enough scope and precondition semantics to explain its atomicity, but the contract never prescribes an application-specific lock order. Multi-aggregate and aggregate-graph declarations do not create a generic coordinator. External I/O and background execution remain separately designed boundaries.

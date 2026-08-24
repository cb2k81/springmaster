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
lastReviewedAt: 2026-08-24
reviewBy: 2026-11-20
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-003
---
# Transaction and Consistency Classification Standard

Transaction scope is exactly `SINGLE_AGGREGATE`, `AGGREGATE_GRAPH` or `MULTI_AGGREGATE`. Consistency strategy is `OPTIMISTIC`, `PESSIMISTIC` or `MIXED`; optimistic locking remains the baseline and the other values are explicit use-case additions.

The application boundary owns the transaction. A command must declare enough scope and precondition semantics to explain its atomicity, but the contract never prescribes an application-specific lock order. Multi-aggregate and aggregate-graph declarations do not create a generic coordinator. External I/O and background execution remain separately designed boundaries.

For a complex `AGGREGATE_GRAPH` or `MULTI_AGGREGATE` mutation, the application applies this generic sequence where the concrete invariant requires locking:

1. perform any advisory preflight without treating it as execution authorization;
2. discover the relevant graph and determine the complete lock request set before mutation;
3. order that set by an application-defined canonical order and acquire the required locks;
4. after locking, revalidate graph membership, ownership, target/data scope, security and all expected versions;
5. revalidate business policies, then mutate atomically within the application-owned write transaction;
6. flush and prove version progress where the operation contract requires it; and
7. persist ledger, evidence or events in the same transaction only where their contract requires atomicity with the mutation.

If post-lock revalidation shows that the graph changed and would require a differently ordered late lock, execution fails closed or uses an explicitly designed retry. It does not opportunistically acquire that lock out of canonical order.

`OPTIMISTIC` remains the default. `PESSIMISTIC` and `MIXED` are added only for concrete concurrency invariants. Lock order, lock phases, aggregate ordering, database lock modes, retry policy and isolation level remain application-specific; this standard defines no generic coordinator or lock manager.

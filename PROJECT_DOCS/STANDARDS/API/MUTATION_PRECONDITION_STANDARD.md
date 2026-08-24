---
documentId: STD-API-MUTATION-PRECONDITION-001
title: Mutation Precondition Standard
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
# Mutation Precondition Standard

Allowed preconditions are `NONE`, `EXPECTED_VERSION`, `EXPECTED_VERSION_SET`, `SNAPSHOT_TOKEN` and `ETAG`.

`EXPECTED_VERSION` and `EXPECTED_VERSION_SET` are business/body tokens. Their request and conflict outcomes are distinct:

| Condition | Required outcome |
|---|---:|
| mandatory body expected-version token missing | invalid request or validation (`400`) |
| body expected-version token malformed or negative | invalid request or validation (`400`) |
| supplied body expected-version token stale or mismatching | conflict (`409`) |
| supplied `If-Match` precondition violated | precondition failed (`412`) |
| mandatory `If-Match` header missing | precondition required (`428`) |

`ETAG` alone binds `If-Match`; body tokens must not be reinterpreted as headers. `SNAPSHOT_TOKEN` requires an identified producer and binds selection/temporal context to the evaluated snapshot. `NONE` cannot be used to conceal an otherwise mandatory optimistic-lock token.

Prechecks are advisory and execution re-checks the precondition. Pessimistic or mixed locking does not remove version-token obligations. For `EXPECTED_VERSION_SET`, the application validates every required member after acquiring any required locks; the classification does not create a generic coordinator. Tokens are opaque; callers may compare or return them but may not derive business meaning.

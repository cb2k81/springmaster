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
lastReviewedAt: 2026-08-20
reviewBy: 2026-11-20
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-003
---
# Mutation Precondition Standard

Allowed preconditions are `NONE`, `EXPECTED_VERSION`, `EXPECTED_VERSION_SET`, `SNAPSHOT_TOKEN` and `ETAG`.

`EXPECTED_VERSION` and `EXPECTED_VERSION_SET` are business/body tokens; conflicts return `409`. `ETAG` binds `If-Match`; a violated value returns `412`, while a missing mandatory header returns `428`. `SNAPSHOT_TOKEN` requires an identified producer and binds selection/temporal context to the evaluated snapshot. `NONE` cannot be used to conceal an otherwise mandatory optimistic-lock token.

Prechecks are advisory and execution re-checks the precondition. Pessimistic or mixed locking does not remove version-token obligations. Tokens are opaque; callers may compare or return them but may not derive business meaning.

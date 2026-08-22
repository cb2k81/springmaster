---
documentId: STD-ARCH-RESOURCE-HISTORY-PROJECTION-001
title: Resource History and Projection Standard
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
# Resource History and Projection Standard

Resource Semantics is the sole additional source beside profiled OpenAPI. History is exactly `NONE`, `ROOT_VERSION`, `PLAN_SNAPSHOT`, `APPEND_ONLY` or `TEMPORAL_RELATION`.

Temporal operations declare their temporal context. `PLAN_SNAPSHOT` and snapshot-token consumers identify the producer. `APPEND_ONLY` forbids ordinary update and delete operations; corrections use a separately defined append command. A projection declares its response schema, is read-only, and is never treated as an entity mutation target. Resource keys and relationships are stable public semantics, not table or entity names.

This standard models contracts only. It creates no generic history engine and does not copy Personnel lock phases or Contacts implementation details into universal rules.

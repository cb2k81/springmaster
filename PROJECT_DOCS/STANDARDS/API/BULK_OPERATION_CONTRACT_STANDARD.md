---
documentId: STD-API-BULK-001
title: Bulk Operation Contract Standard
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
# Bulk Operation Contract Standard

A Backend Bulk Command is not a Composite Command, GWC Batch or Background Job. Each bulk profile declares:

- selection mode (`EXPLICIT_TARGETS`, `QUERY_SNAPSHOT` or `SELECTION_TOKEN`) and, for query selection, a freeze/snapshot rule;
- atomicity (`ALL_OR_NOTHING`, `PER_TARGET` or `PER_CHUNK`) and execution (`SYNCHRONOUS` or `ASYNCHRONOUS`);
- target authorization with execution-time re-check and an explicit non-disclosure policy;
- idempotency, limits, outcome vocabulary and result delivery (`INLINE`, `PAGED`, `ARTIFACT` or an observable status resource);
- precondition handling for all selected targets.

An asynchronous command returns `202` only when a status operation and result-delivery contract are observable. A synchronous contract returns its defined aggregate result and never generic `207`. GWC may orchestrate multiple calls, but that client batch is not backend atomicity. Sprint 003 supplies contracts and synthetic oracles only; it supplies no generic bulk/job runtime.

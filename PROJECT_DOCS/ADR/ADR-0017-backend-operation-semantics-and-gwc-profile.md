---
documentId: ADR-0017
title: Backend Operation Semantics and GWC Profile
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
# ADR-0017 Backend Operation Semantics and GWC Profile

## Context

The existing endpoint, command, relationship, precheck, security and error contracts remain authoritative but lack one stable, machine-readable operation identity and a non-competing binding for UI specifications. Generated applications must not become a source of API semantics.

## Decision

1. `operationKey` is the stable domain and generator identity. `operationId` is the technical OpenAPI identity. The technical tuple is HTTP method, normalized path and `operationId`.
2. `operationKind` is exactly `QUERY`, `COMMAND`, `PRECHECK` or `CAPABILITY_EVALUATION`. `operationRoles` contains zero or more values from `ENTITY_LIST`, `ENTITY_DETAIL`, `ENTITY_CREATE`, `ENTITY_UPDATE`, `ENTITY_DELETE`, `REFERENCE_LOOKUP`, `RELATION_LIST`, `CANDIDATE_LIST`, `OVERVIEW_LIST`, `HISTORY_LIST`, `PROJECTION_READ`, `TEMPORAL_READ`, `BULK_COMMAND`, `BULK_STATUS`, `EXPORT`, `AGGREGATION`, `DELTA_READ`. `WORKSPACE` is neither a kind nor a role.
3. Profiled OpenAPI is the canonical public API boundary. It uses exactly one additive namespaced extension container, `x-cocondo-operation-profile`. Existing unprofiled operations retain their behavior and OpenAPI representation.
4. The Java registry is an opt-in authoring mechanism. The Operation Catalog is derived deterministically from profiled OpenAPI and accepted contracts. Resource Semantics is the sole additional source for resource/history/projection semantics. Application UI Spec expresses UI/business consumption intent. Canonical IR is a normalized generator projection. Generated applications are never normative.
5. Backend effects expose only affected `resourceKeys`. Refresh, reload, dirty state, stale response and workspace behavior belong to the Application UI Spec/GWC.
6. Application UI Spec 1.2 adds `operationKey` as its primary semantic reference. Method, path and `operationId` remain technical verification and v1.1 legacy bindings. A deterministic alias mapping preserves v1.1. Workspace remains a GWC pattern, never a backend operation profile.

## Consequences and boundary

Operation keys and technical identities fail closed on duplicates. Security, resource and precondition profiles are explicit where used. No UI reload graph, Workspace runtime or managed-project migration is introduced. Existing APIs are not forced to opt in.

## Verification

The seven Sprint-003 schemas, positive and negative fixtures, deterministic catalog/export tool, OpenAPI runtime tests and Team-Membership reference slice are the qualification evidence. New diagnostics begin report-only under ADR-0006.

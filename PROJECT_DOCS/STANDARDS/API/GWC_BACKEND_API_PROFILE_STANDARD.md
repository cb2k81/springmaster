---
documentId: STD-API-GWC-BACKEND-PROFILE-001
title: GWC Backend API Profile Standard
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
# GWC Backend API Profile Standard

ADR-0017 is the decision authority. A profiled OpenAPI operation has one unique `operationKey`, one technical `operationId`, one allowed `operationKind`, zero or more allowed `operationRoles`, an explicit security contract and optional precondition, resource and effects bindings. All additions live under `x-cocondo-operation-profile`; parallel semantic extensions are forbidden.

Profiled OpenAPI is public truth. The registry only authors profiles; catalog and Canonical IR are derived. Resource Semantics is the only additional resource-semantic source. Generated output is evidence, not authority. Unprofiled operations are unchanged.

Backend effects contain only `affectedResourceKeys`. UI refresh/reload graphs, stale-response handling, dirty state and workspace state belong to Application UI Spec/GWC. `WORKSPACE` is forbidden as backend kind or role.

Application UI Spec 1.2 uses `operationKey` as primary reference and retains method/path/operationId for verification. A v1.1 binding maps the canonical technical tuple deterministically to the 1.2 `operationKey`; an unresolved or ambiguous alias fails closed. This is additive and cannot make `operationKey` mandatory in a v1.1 document.


# ADR-0005: Security and Permission Boundary

## Status

Accepted

## Date

2026-06-30

## Context

Springmaster is the master/reference project for reusable backend foundation, tooling, standards, conventions, reference implementations and verifiable quality gates.

Patch `000052_springmaster_security_permission_boundary_standard` defined the documentation-first security and permission boundary. Later patches accepted adjacent decisions:

- `ADR-0002` defines the public API boundary, endpoint vocabulary, DTO boundary, error contract and first-slice status-code defaults.
- `ADR-0003` defines controller, service, use-case, repository, mapper and transaction placement.
- `ADR-0004` defines persistence identity, audit-field ownership and repository boundary.
- `ADR-0006` defines report-only versus strict gate execution.
- `ADR-0007` defines Catalog-demo canonicalization states and evidence requirements.

Security remains the missing decision source for endpoint classification, permission naming, role mapping, authorization placement, current-user/capability contracts and `documented-deferred-security` evidence.

Catalog-demo may start with a minimal or deferred security implementation, but it must not normalize unclassified or accidentally public management APIs as Springmaster reference behavior.

Existing applications such as IDM, Personnel, Contacts and Orders remain comparison inputs only. This ADR does not authorize security migration, target-project remediation or target-project delivery.

## Decision

Springmaster accepts the security and permission boundary defined by `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md` as the canonical decision baseline for new Springmaster reference APIs and later generated project templates.

The accepted decision is:

1. **Secure-by-default endpoint classification**
   - Every endpoint in a new Springmaster reference API has an explicit classification: `public`, `authenticated`, `management`, `technical` or `system`.
   - Missing classification for an application resource means `management`.
   - `public` and `technical` endpoints are exceptions and must be explicitly documented.
   - Catalog-demo must document classification for every CatalogItem endpoint before a slice may become `canonical-reference-slice`.

2. **Management APIs require permissions**
   - Management endpoints require operation-level permission checks.
   - Read, create, update, delete, delete-multiple, search, options, lifecycle commands and relationship commands may require distinct permissions.
   - Read permission does not imply write, delete, lifecycle or relationship-command permission.
   - Frontend navigation or UI hiding is never sufficient authorization evidence.

3. **Permission naming**
   - Canonical permission names use the shape `<domain>:<resource>:<operation>`.
   - Segments use lowercase ASCII words; hyphens are allowed inside multi-word operation names.
   - Permission operations describe domain capabilities, not controller classes, Java method names, Spring route names or role names.
   - `admin` is a role-name candidate, not a permission operation.
   - Wildcard permissions are not canonical unless a later ADR accepts their syntax and matching semantics.

4. **Catalog-demo first permission vocabulary**
   - The first CatalogItem permission vocabulary is:
     - `catalog:item:read` for list/detail and normal read-only search;
     - `catalog:item:create` for create;
     - `catalog:item:update` for full update;
     - `catalog:item:delete` for single delete;
     - `catalog:item:delete-multiple` when delete-multiple is introduced;
     - `catalog:item:read-options` when `/options` exposes bounded selector data that needs a distinct permission;
     - `catalog:item:<transition>` for future lifecycle transitions.
   - A later Catalog-demo implementation may use `catalog:item:search` only when search behavior becomes semantically broader than normal read access and the permission catalog documents the difference.

5. **Roles aggregate permissions**
   - Application logic checks permissions wherever possible, not role names.
   - Roles are deterministic collections of permissions.
   - Demo roles may be introduced for testability, but role names must not become domain logic.
   - Role-to-permission mappings require tests once implemented.

6. **Authorization placement**
   - Authorization for reusable operations belongs at the application operation boundary: `QueryService`, `CommandService`, `ResourceService` or `UseCaseHandler`.
   - Controllers may have coarse HTTP access checks, but controller-only authorization is not the canonical protection point for reusable management operations.
   - Repositories, entities and mappers must not own authorization decisions.
   - Complex authorization that depends on domain state belongs in an application-layer authorization collaborator or policy service, not in long controller SpEL expressions.

7. **`@PreAuthorize` and permission catalog**
   - `@PreAuthorize` is allowed when it checks permissions deliberately.
   - Repeated string literals are acceptable only for an early candidate slice; canonical code should move toward permission constants or a permission catalog.
   - A later Java patch may introduce a Springmaster permission catalog, annotations, method-security helpers or a permission evaluator. This ADR does not create those Java types.

8. **Current-user and capability contracts**
   - Current-user and capability endpoints are authenticated endpoints, not public management bypasses.
   - Capability responses expose stable effective capabilities relevant to UI behavior, not raw tokens or implementation-specific claims.
   - Current-user responses must not expose secrets, credential material or unrestricted token contents.
   - UI capability data supplements server-side checks; it does not replace them.

9. **Audit-current-user boundary**
   - Audit fields are not client input.
   - Audit infrastructure requires a deterministic current-user provider once audited writes are implemented.
   - Background jobs and platform update tasks require a documented system-principal decision before writing audited entities.
   - Exact current-user provider implementation remains deferred to a later code/observability/security implementation patch.

10. **Catalog-demo security modes**
    - A Catalog-demo slice may use `documented-deferred-security` only when endpoint classifications, intended permissions, planned role mapping, deferred tests and rationale are documented in the readiness summary.
    - A slice may use `implemented-management-security` when authentication, permission checks, positive and negative tests and role mapping are implemented.
    - A slice with no security classification may not become canonical.

11. **Error behavior**
    - Missing or invalid authentication maps to `401 UNAUTHORIZED` using the API error contract.
    - Authenticated but unauthorized access maps to `403 FORBIDDEN` using the API error contract.
    - Data-scope concealment with `404 NOT_FOUND` is not decided here and requires a later data-scope or tenant ADR.

12. **Gate strategy**
    - Report-only security diagnostics may use ADR-0005 as `ruleSource` for endpoint classification, permission naming, controller/service authorization-placement hints, capability endpoint shape and deferred-security evidence.
    - Strict security gates require implementation evidence, Catalog-demo proof, security fixtures and explicit strict promotion under ADR-0006.

## Consequences

- New Springmaster reference APIs are secure-by-default at the contract level.
- Catalog-demo can proceed with a deliberately deferred security mode, but the deferral must be visible and cannot be mistaken for canonical unprotected management behavior.
- Security-related gate tooling can now start as report-only diagnostics against an accepted rule source.
- Strict security enforcement remains blocked until Java implementation, fixtures, tests and Catalog-demo evidence exist.
- Existing target projects are not changed, supplied or remediated by this ADR.

## Alternatives rejected

### Treat security as a later implementation detail

Rejected. Endpoint classification and permission vocabulary affect API contracts, UI behavior, tests, OpenAPI expectations and gate design. Leaving security implicit would make Catalog-demo an unsafe reference.

### Authorize only at controllers

Rejected. Controller-only authorization is too fragile for reusable application operations, test fixtures and future generated code. The canonical protection point is the application operation boundary.

### Check role names in business logic

Rejected. Roles are deployment or application policy aggregates. Permissions are the stable operation capabilities that application code and tests should reason about.

### Make every authenticated endpoint a management endpoint

Rejected. Current-user, capability and selected bounded reference data can be authenticated without operation-specific permission when they do not expose management data or mutate shared state.

### Implement JWT, role persistence and security fixtures in this ADR patch

Rejected. This is a documentation-only architecture decision. Concrete implementation belongs to later code/test patches.

## Gate impact

ADR-0005 unlocks report-only G4 security diagnostics for:

- missing endpoint classification;
- management endpoints without an obvious service/use-case authorization plan;
- non-canonical permission names;
- role-name checks in places where permission checks are expected;
- missing documented-deferred-security evidence for Catalog-demo candidate slices;
- current-user/capability DTO contract risks.

Strict G4 gates remain deferred until:

1. a security implementation exists in Catalog-demo;
2. positive and negative security tests exist;
3. permission catalog behavior is implemented and tested;
4. findings have stable false-positive behavior;
5. a later patch explicitly promotes selected rules under ADR-0006.

## References

- `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md`
- `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md`
- `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md`
- `PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md`
- `PROJECT_DOCS/ADR/ADR-0006-verification-and-gate-strategy.md`
- `PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md`

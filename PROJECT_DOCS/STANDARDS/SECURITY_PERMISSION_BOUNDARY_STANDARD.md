# Security and Permission Boundary Standard

## Purpose

This standard defines the canonical Springmaster security and permission boundary rules before `Catalog-demo` becomes the canonical reference implementation.

It converts the security findings from IDM and Personnel into Springmaster-owned rules for:

* public, authenticated and management endpoint classification;
* permission naming;
* role-to-permission mapping;
* authorization placement;
* `@PreAuthorize` usage;
* current-user and capability endpoints;
* audit-current-user interaction;
* test and future gate expectations.

The standard is documentation-first. It does not introduce Java security configuration, authentication providers, JWT parsing, method-security code, test fixtures, role tables, migrations, Maven dependencies or target-project changes. Since `000066_springmaster_adr_0005_security_and_permission_boundary`, its foundational decisions are backed by accepted `ADR-0005`.

## Scope

This standard applies to new Springmaster reference APIs, `Catalog-demo` and later projects generated from or supplied by Springmaster.

It does not require immediate changes in IDM, Personnel, Contacts, Orders or other existing applications. Existing applications remain comparison inputs until Catalog-demo proves the standard and the gate concept.

## Design principle

Springmaster management APIs are secure by default.

The default rule is:

* an endpoint is protected unless explicitly documented as public or technical;
* a management operation has a named permission;
* authorization is checked at the application operation boundary, not only at the HTTP adapter;
* role-to-permission mapping is explicit and testable;
* current-user and capability responses expose stable client-facing authorization information without leaking internal token implementation details.

Catalog-demo may start with a minimal security model, but it must not normalize unprotected management endpoints as the canonical Springmaster pattern.

## Endpoint security classification

Every endpoint in a Springmaster reference API must be assigned one of the following classifications.

| Classification | Meaning | Default authorization rule |
|---|---|---|
| `public` | can be called without authentication | must be explicitly allow-listed |
| `authenticated` | any authenticated user may call it | requires valid principal, no operation-specific permission |
| `management` | UI/backend management operation | requires operation-specific permission |
| `technical` | health, build info, OpenAPI docs, internal diagnostics or tool endpoint | requires explicit technical policy |
| `system` | called by trusted internal jobs or platform integration | requires dedicated system-authentication decision |

Public and technical endpoints must be documented. A missing classification means `management` for application resources.

## Public endpoint rule

Public endpoints are exceptions.

Allowed examples:

* login or token exchange endpoint when the application owns authentication;
* public health readiness endpoint when infrastructure requires it;
* static or generated OpenAPI documentation only when the deployment explicitly allows it;
* an explicitly documented public lookup endpoint.

Rules:

* public endpoints must be allow-listed in configuration or code;
* public endpoints must not expose management data by accident;
* public endpoints must not rely on hidden frontend-only checks;
* public endpoints must still follow API error and DTO standards;
* public endpoints must be covered by tests that prove access is allowed without authentication and forbidden operations remain protected.

## Authenticated endpoint rule

Authenticated endpoints require a valid principal but no operation-specific permission.

Allowed examples:

* current-user profile;
* current-user capability summary;
* own session or token introspection information;
* bounded reference data that is safe for every authenticated user.

Rules:

* authenticated endpoints must not mutate shared business state unless a specific ADR allows it;
* authenticated endpoints must not expose global management data;
* any endpoint that reads or writes domain resources for multiple users, tenants or departments is usually `management`, not merely `authenticated`.

## Management endpoint rule

Management endpoints are the default for Springmaster resource APIs.

Rules:

* every management endpoint requires an operation-level permission;
* list, detail, create, update, delete, delete-multiple, search, options, state commands and relationship commands may require different permissions;
* read permissions do not imply write permissions;
* delete permissions do not imply archive/deactivate permissions unless the role mapping explicitly says so;
* assignment/relationship operations require their own permission when they change authorization-relevant or lifecycle-relevant state;
* permission checks must be testable independently from frontend navigation.

## Permission naming standard

Permission names must be stable, explicit and operation-oriented.

Canonical shape:

```text
<domain>:<resource>:<operation>
```

Examples for `Catalog-demo`:

| Operation | Permission |
|---|---|
| list catalog items | `catalog:item:read` |
| detail catalog item | `catalog:item:read` |
| create catalog item | `catalog:item:create` |
| update catalog item | `catalog:item:update` |
| single delete catalog item | `catalog:item:delete` |
| delete multiple catalog items | `catalog:item:delete-multiple` |
| search catalog items | `catalog:item:search` or `catalog:item:read` when search is only a read variant |
| options endpoint | `catalog:item:read-options` or `catalog:item:read` when options contain no sensitive data |
| state transition | `catalog:item:<transition>` |

Rules:

* permission names use lowercase ASCII words separated by `:` and `-`;
* domain and resource segments are singular conceptual names;
* operation names reflect business capability, not Java method names;
* no permission name may be derived from a controller class name by convention alone;
* `admin` is a role name candidate, not a permission operation;
* wildcard permissions are not canonical for Springmaster reference APIs unless a later ADR defines them;
* permission names must be documented in a permission catalog before Catalog-demo makes them canonical.

## Role-to-permission mapping

Roles are collections of permissions. Permissions are operation capabilities.

Rules:

* application logic checks permissions, not role names, wherever possible;
* role-to-permission mapping must be deterministic and testable;
* default demo roles must be intentionally small and named for their purpose;
* role names must not be hard-coded inside domain logic;
* a role may aggregate permissions across resources, but the permissions remain explicit;
* changes to role mappings require tests that prove expected access and denial behavior.

Recommended minimum Catalog-demo role set when security is introduced:

| Role | Purpose |
|---|---|
| `CATALOG_VIEWER` | read list/detail/options/search data |
| `CATALOG_EDITOR` | create and update catalog items in addition to read permissions |
| `CATALOG_MANAGER` | delete and lifecycle/relationship commands in addition to editor permissions |

The exact role names may change, but the mapping behavior must be explicit.

## Authorization placement

Authorization for reusable operations belongs at the application boundary.

Canonical placement:

| Layer | Authorization role |
|---|---|
| Controller | optional coarse HTTP gate and endpoint classification |
| QueryService | read-operation authorization |
| CommandService | write-operation authorization |
| UseCaseHandler | operation-specific authorization for granular commands |
| DomainService | may enforce domain rules but should not depend on HTTP/security framework details unless it is an application entry point |
| Repository | no authorization logic except query scoping passed from authorized application layer |

Rules:

* controller-only authorization is insufficient for reusable management operations;
* service/use-case authorization is the canonical protection point;
* repositories must not decide whether a principal is allowed to perform an operation;
* domain entities must not call security context APIs;
* authorization failures map to the API error contract as `403 FORBIDDEN`;
* missing or invalid authentication maps to `401 UNAUTHORIZED`.

## `@PreAuthorize` rule

`@PreAuthorize` is allowed, but its use must be deliberate.

Recommended usage:

* use `@PreAuthorize("hasAuthority('<permission>')")` or an equivalent central permission evaluator on query services, command services and use-case handlers;
* use controller-level `@PreAuthorize` only for coarse HTTP access or when the controller method is the only entry point and the operation is not reusable;
* prefer permission constants over repeated string literals once a Java permission catalog exists;
* do not hide complex business authorization inside long SpEL expressions;
* move complex checks into an authorization collaborator or policy service when they require domain state.

A later code patch may introduce a Springmaster permission catalog, constants, annotations or a permission evaluator. This documentation patch does not create those Java types.

## Current-user and capability endpoints

Springmaster should support a stable current-user/capability pattern when management UIs need it.

Canonical endpoint candidates:

| Endpoint | Classification | Purpose |
|---|---|---|
| `GET /api/<domain>/current-user` | authenticated | identity summary relevant to the app |
| `GET /api/<domain>/capabilities` | authenticated | effective app capabilities/permissions relevant to UI behavior |
| `GET /api/<domain>/reference-data` | authenticated or management | bounded selector/reference data when resource-specific `/options` is insufficient |

Rules:

* capability responses expose effective capabilities, not raw tokens;
* capability names should be derived from permission names or a stable UI capability map;
* current-user responses must not expose secrets, credential material or implementation-specific token claims;
* current-user and capability endpoints must be bounded and cache-conscious;
* UI convenience must not replace server-side permission checks.

## Audit-current-user boundary

The domain/persistence standard defines technical audit fields. This standard defines the security-side expectation.

Rules:

* audit infrastructure needs a deterministic current-user provider;
* absence of an authenticated user must map to a documented technical/system user when audit fields are required;
* controller input must not set `createdBy`, `lastModifiedBy`, `createdAt` or `lastModifiedAt`;
* service/use-case tests should be able to set a test principal deterministically;
* background jobs and platform update tasks need a separate system-principal decision before they write audited entities.

This patch does not implement the current-user provider. It defines the required boundary.

## Tenant, organization and data-scope boundary

IDM and Personnel show that permissions alone are often insufficient for real management applications.

Springmaster distinguishes:

| Concept | Meaning |
|---|---|
| permission | capability to perform an operation |
| role | aggregate of permissions |
| principal | authenticated actor |
| data scope | subset of data the principal may access |
| tenant/organization scope | structural boundary for data access |

Rules:

* operation permission does not automatically grant access to every row;
* data-scope filtering belongs in query/command services or dedicated authorization policies;
* tenant/organization scoping must not be implemented as ad-hoc controller filters;
* Catalog-demo may defer tenant/data-scope support, but the deferral must be explicit.

## Error behavior

Security errors follow the API error contract.

| Case | Status | Error type |
|---|---|---|
| missing authentication | `401` | `UNAUTHORIZED` |
| invalid/expired token | `401` | `UNAUTHORIZED` |
| authenticated but permission missing | `403` | `FORBIDDEN` |
| authenticated but outside data scope | `403` or domain-specific not-found decision | `FORBIDDEN` or `NOT_FOUND` according to later data-scope ADR |
| CSRF/session failure where applicable | `401` or `403` | explicit mapped error type |

For data-scope failures, Springmaster must later decide whether to conceal existence with `404` for selected resources. Catalog-demo must not invent that policy implicitly.

## Test standard

Security behavior must be tested at multiple levels once implementation begins.

Required test categories for a secured reference API:

* unauthenticated request is rejected for management endpoints;
* authenticated request without permission returns `403`;
* authenticated request with permission succeeds;
* role-to-permission mapping grants the intended permissions;
* role-to-permission mapping does not grant unintended permissions;
* current-user/capability endpoints return bounded, stable DTOs;
* write operations verify authorization at service/use-case level;
* OpenAPI documentation does not imply public access unless the endpoint is public.

MockMvc tests are appropriate for HTTP behavior. Service/use-case tests are appropriate for operation-level authorization. Role-mapping tests are appropriate for permission-catalog correctness.

## Catalog-demo readiness rule

Catalog-demo must not become canonical with accidental security behavior.

Before the first secured CatalogItem API becomes the reference, Catalog-demo must explicitly decide:

* whether the first slice is intentionally unsecured as a temporary local demo slice;
* if unsecured, which document marks security as deferred and prevents target-project delivery;
* when security is enabled, which permissions protect list/detail/create/update/delete/search/options;
* whether delete-multiple receives a separate permission;
* where `@PreAuthorize` or equivalent authorization lives;
* how role-to-permission mapping is represented and tested;
* how current-user and capability endpoints are shaped;
* how audit-current-user information is supplied;
* whether tenant/data-scope support is deferred.

A canonical management API slice should include at least one positive and one negative security test once security is introduced.

## Future gates

The following gates should be considered after the documentation standard is stable:

| Gate | Purpose |
|---|---|
| Endpoint classification scan | report controllers without public/authenticated/management/technical classification |
| Management endpoint authorization scan | fail if management controller methods have no service/use-case authorization path |
| `@PreAuthorize` permission-string scan | detect unknown or non-canonical permission names |
| Permission catalog consistency test | verify every documented permission exists in code and every code permission is documented |
| Role mapping test helper | verify expected role-to-permission assignments |
| MockMvc security template | assert unauthenticated, forbidden and allowed cases for endpoint groups |
| Capability response test helper | verify effective capabilities are stable and bounded |
| Audit principal test helper | verify createdBy/lastModifiedBy behavior under authenticated and system principals |
| Optional ArchUnit rules | enforce controller/service/repository/security dependency boundaries |

## Deferred decisions

The following topics are intentionally not finalized here:

* concrete Spring Security configuration;
* JWT claim mapping;
* session versus bearer-token behavior;
* CSRF policy;
* password/login implementation;
* permission catalog Java type;
* custom method-security annotation;
* permission evaluator implementation;
* role persistence schema;
* tenant/data-scope implementation;
* current-user provider implementation;
* test fixture implementation;
* migration of IDM or Personnel security code;
* delivery of security code to existing target projects.

These require later ADRs, standards or code patches.


## Command and relationship permissions since 000053

Patch `000053_springmaster_command_relationship_endpoint_standard` specializes permission naming for commands and relationship operations.

Command and relationship permissions still follow `<domain>:<resource>:<operation>`. The operation part should match the public domain command such as `activate`, `delete-multiple`, `assign`, `remove`, `replace` or a more specific domain verb. The resource part is the aggregate or management boundary that owns the operation.

## ADR-0005 acceptance since 000066

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts `PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md`.

Accepted implications for this standard:

- endpoint classification is mandatory for new reference APIs and Catalog-demo candidate slices;
- unclassified application-resource endpoints are treated as `management`;
- permission naming uses `<domain>:<resource>:<operation>`;
- Catalog-demo first-slice permissions use `catalog:item:read`, `catalog:item:create`, `catalog:item:update`, `catalog:item:delete`, optional `catalog:item:delete-multiple`, optional `catalog:item:read-options` and future `catalog:item:<transition>`;
- authorization belongs at application operation boundaries, with controller checks allowed only as coarse HTTP gates;
- `documented-deferred-security` is allowed only with endpoint classification, intended permissions, planned role mapping, deferred tests and rationale;
- report-only security diagnostics may use ADR-0005 as the rule source;
- strict security gates remain deferred until implementation evidence and explicit ADR-0006 promotion exist.




## Command precheck boundary since 000082

Patch `000082_springmaster_command_precheck_capability_standard` adds the command-precheck standard and accepts ADR-0011.

Command prechecks are related to security and policy, but they do not replace authorization or command execution validation.

Rules:

* a management command precheck is itself a management endpoint unless explicitly classified otherwise;
* missing authentication maps to `401`;
* missing operation permission maps to `403`;
* an authenticated actor with the required operation permission may still receive `200` with `executable: false` when a concrete target is blocked by policy, state, dependency, validation or data-scope rules;
* the executing command endpoint must enforce the same policy again;
* precheck and execution handlers must share the same backend policy/guard collaborator;
* frontend command-control state must not become the only place where actor/target policy is defined.

List and bulk controls are not required to perform per-item prechecks. Backend execution remains responsible for rejecting forbidden, stale, unknown or policy-blocked items according to the command/bulk endpoint contract.

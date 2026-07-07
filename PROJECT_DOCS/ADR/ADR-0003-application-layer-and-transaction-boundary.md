# ADR-0003: Application Layer and Transaction Boundary

## Status

Accepted

## Date

2026-06-30

## Context

Springmaster is being developed as the master/reference project for reusable backend foundation, tooling, standards, conventions, reference implementations and verifiable quality gates.

Patch `000050_springmaster_controller_service_usecase_transaction_standard` defined the documentation-first controller, service, use-case and transaction standard. Later API, DTO, error, mapping, security-placement and gate-strategy standards refined the surrounding boundaries.

The real-app forensics from IDM and Personnel showed that working applications can drift into different shapes: controller-centric orchestration, direct service CRUD, richer use-case operations, nested relationship commands and different transaction-placement habits. Springmaster needs a single architecture decision before Catalog-demo becomes canonical and before Java boundary gates inspect controller/service/transaction behavior.

Accepted `ADR-0002` defines public API boundaries. Accepted `ADR-0006` defines verification and gate execution modes. This ADR defines the application-layer and transaction boundary that sits between HTTP controllers, domain behavior and persistence access.

## Decision

Springmaster accepts the application-layer and transaction boundary described below as canonical for new Springmaster reference APIs, Catalog-demo slices and future generated project templates.

### Controller boundary

Controllers are HTTP boundary adapters.

A controller may:

- expose canonical endpoint paths, HTTP methods, status codes and headers;
- bind path variables, query parameters and request bodies;
- activate boundary validation through `@Valid`, `@Validated` or an equivalent boundary mechanism;
- call the selected application-service, query-service, command-service or use-case boundary;
- return DTOs, response envelopes or `ResponseEntity` with API DTO bodies.

A controller must not:

- access repositories or `EntityManager` directly;
- own transaction demarcation;
- contain business invariants, lifecycle decisions or persistence decisions;
- perform reusable authorization as the only protection for a management operation;
- expose entities, aggregates, Spring Data `Pageable`, `Page<DTO>` or `Slice<DTO>` as public API contracts;
- construct ad-hoc error bodies instead of using the canonical error mapping layer.

### Application service shape

Springmaster does not mandate one service class pattern for every resource. It mandates an explicit application-layer choice.

| Situation | Accepted owner |
|---|---|
| Small CRUD-like management resource | `ResourceService` or clearly named query/command services |
| List/detail read model | `QueryService` |
| Create/update/delete command | `CommandService` or use-case handler |
| Operation-specific command, relationship, assignment or state transition | use-case handler or dedicated command service method |
| Complex aggregate invariant | command service/use-case handler coordinating domain model and domain services |
| Reusable domain behavior independent of HTTP | domain model method or `DomainService` |
| Persistence access | repository behind service/use-case boundary only |

The service shape may evolve as the resource becomes more complex. A simple `ResourceService` is accepted for a first slice only when it still respects transaction, validation, error, repository and DTO boundaries.

### Query and command separation

New reference APIs should separate read and write responsibilities when a resource is more than trivial.

- `QueryService` owns list, detail, option/reference-data and search behavior.
- `CommandService` owns create, update, delete, delete-multiple and state-changing behavior.
- Use-case handlers own operations that deserve independent testing, permission checks, transaction policy or error mapping.
- Domain services own reusable domain rules, not HTTP orchestration.

This is not a CQRS-framework requirement. It is a structural convention for clarity, testability, gateability and future target comparison.

### Transaction ownership

Transactions belong to the application boundary, not to HTTP controllers.

Accepted transaction rules:

- controllers must not be annotated with `@Transactional`;
- repository access must happen inside a service, query-service, command-service or use-case boundary;
- write operations must have an explicit write transaction policy at service/use-case level;
- read operations may use `@Transactional(readOnly = true)` when JPA consistency, lazy loading, repeatable read behavior or projection assembly requires it;
- one HTTP command should map to one business transaction unless a later ADR defines async, saga, outbox or long-running-command behavior;
- domain conflicts, validation failures, not-found cases and optimistic-locking conflicts must reach the global error mapping layer in canonical form;
- long-running external I/O must not be performed inside a database transaction unless a specific integration ADR allows it;
- code must not rely on private self-invocation for Spring proxy transaction semantics.

An explicit transaction policy may be method-level or class-level when the class has homogeneous behavior. Mixed query/command classes must avoid ambiguous class-level transaction semantics.

### Repository boundary

Repositories are persistence adapters. They are not API collaborators.

Accepted repository rules:

- controllers must not inject repositories;
- controllers must not inject or call `EntityManager`;
- repositories must not return public API response envelopes;
- repository method names may use internal Java vocabulary such as `findBy...`, but that vocabulary must not leak into public endpoint paths or operation names;
- services/use cases convert persistence results into DTOs, read models, command results or domain results.

### Mapper boundary

Mappers are layer-conversion collaborators.

Mappers must not:

- access repositories or `EntityManager`;
- call external clients;
- own transaction demarcation;
- perform authorization checks;
- decide lifecycle transitions or business invariants.

Manual mappers and MapStruct-style mappers are both allowed when they follow the mapping standard. Complex read-model assembly belongs in query/application services with explicit mapper collaboration, not in controllers.

### Security placement relationship

`ADR-0005` will own the full security and permission model. Until it is accepted, this ADR fixes the placement rule:

- controller-level security may be used as a coarse HTTP gate;
- reusable management operations require authorization at query-service, command-service or use-case boundary, or an explicitly approved equivalent;
- permission naming, role-to-permission mapping and capability/current-user endpoints remain owned by the security standard and future ADR-0005.

### Error boundary relationship

Application services and use cases should throw or return domain/application errors that the global error layer maps to the API error contract from ADR-0002.

Controllers and services must not hide domain conflicts, validation failures, not-found cases or authorization failures behind generic `500` responses.

## Scope

This ADR applies to:

- new Springmaster reference APIs;
- Catalog-demo application-layer and transaction design;
- generated project templates when templates start producing management APIs;
- future Java boundary gates and report-only diagnostics;
- future read-only target-project comparison.

This ADR does not require immediate changes to IDM, Personnel, Contacts, Orders or other existing target projects. Existing projects remain comparison inputs until Catalog-demo proves the pattern and target delivery is explicitly authorized.

## Affected standards

This ADR accepts and consolidates the architectural decisions from:

- `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md` for mapper-boundary placement
- `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md` for authorization-placement relationship only
- `PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md` for controller DTO-boundary interaction
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md` and `PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md` for error-boundary interaction
- `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md` for future Java boundary gates

This ADR depends on:

- `ADR-0002-api-boundary-and-endpoint-contract.md` for public API and DTO boundary decisions;
- `ADR-0006-verification-and-gate-strategy.md` for gate modes, severities, reports and strict-promotion rules.

It does not replace future ADRs for persistence identity, security/permission catalog, Catalog-demo canonicalization, async/outbox patterns, configuration/runtime profiles, database migrations or observability.

## Considered alternatives

### Put orchestration and transaction handling in controllers

Rejected. It couples HTTP adapters to business and persistence concerns, makes reuse harder and prevents reliable Java boundary gates.

### Allow controllers to inject repositories for simple CRUD

Rejected for Springmaster reference APIs. It looks efficient for trivial resources but leaks persistence concerns into the API layer and makes later command, authorization and transaction policies inconsistent.

### Mandate full CQRS and use-case handlers for every operation

Rejected. Springmaster needs strong boundaries without unnecessary ceremony. Simple resources may start with a resource service or small query/command services as long as the boundary rules are met.

### Use one generic service pattern for all resources

Rejected. IDM, Personnel and future reference domains have different operation complexity. The decision must allow a deliberate resource/query/command/use-case choice while keeping gateable rules.

### Make ArchUnit strict immediately

Rejected. ADR-0006 requires report-only first and strict promotion only after stable implementation and evidence. Reflection scans or ArchUnit may be introduced later, but this ADR itself does not implement gates.

### Keep authorization only at controller annotations

Rejected for reusable management operations. Controller-level checks are useful as a coarse gate, but operation authorization must live at the reusable application boundary or an approved equivalent once ADR-0005 finalizes the permission model.

## Consequences

Positive consequences:

- Catalog-demo can implement a realistic `CatalogItem` slice without copying accidental IDM or Personnel patterns.
- Java boundary gates have an accepted rule source for controller transaction scans, controller repository scans and service transaction-policy diagnostics.
- Application code remains reusable outside HTTP controllers.
- API error and DTO contracts remain aligned with ADR-0002.
- Future target comparison can distinguish legacy tolerance from Springmaster reference violations.

Costs and constraints:

- Developers must choose and document the application-layer shape deliberately.
- Simple CRUD code may require an additional service/use-case boundary even when direct repository access would be shorter.
- Strict Java boundary gates still need implementation evidence and Catalog-demo proof before they may fail builds.
- Security placement is only partially decided here; permission naming and role mapping still require ADR-0005.

## Gate implications

This ADR enables report-only Java boundary diagnostics for:

- controllers annotated with `@Transactional`;
- controller injection of repositories or `EntityManager`;
- public controller signatures exposing entities, aggregates, `Pageable`, `Page<DTO>` or `Slice<DTO>`;
- missing explicit transaction policy on command services or use-case handlers;
- mapper classes that inject repositories or own transactions;
- obvious service-shape ambiguity where a controller directly combines query, command and persistence responsibilities.

Strict gates are not enabled merely by this ADR. Strict promotion requires:

1. ADR-0006 mode and report semantics;
2. stable gate implementation and tests;
3. Catalog-demo evidence;
4. deterministic pass/fail criteria;
5. a later patch that marks the specific rule strict-ready.

## Exceptions and deferrals

Allowed exceptions and deferrals:

- A simple `ResourceService` may own both read and write operations for a small first slice when it has explicit transaction policy and no controller/repository leakage.
- Read-only transaction annotations are optional when no transactional consistency, lazy loading or projection assembly requires them.
- Class-level `@Transactional` is allowed for homogeneous services. Mixed query/command services should prefer method-level policy or a service split.
- Security permission names, role mapping, current-user/capability contracts and security gates remain deferred to ADR-0005.
- Persistence identity, optimistic locking details and repository base-class strategy remain deferred to ADR-0004.
- Catalog-demo canonicalization evidence remains deferred to ADR-0007.
- Async, outbox, saga and long-running-command transaction patterns require a later ADR before becoming reference behavior.
- Existing target-project deviations are tolerated in read-only comparison until a later delivery workflow is explicitly approved.

## Supersession

This ADR does not supersede prior accepted ADRs.

It accepts the architecture decision behind `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md` and narrows it into an ADR-backed baseline for new Springmaster reference work.

It is complemented by:

- `ADR-0002-api-boundary-and-endpoint-contract.md`
- `ADR-0006-verification-and-gate-strategy.md`

Future ADRs may narrow related areas:

- ADR-0004 for persistence identity and DomainEntity strategy;
- ADR-0005 for security and permission boundary;
- ADR-0007 for Catalog-demo canonicalization.

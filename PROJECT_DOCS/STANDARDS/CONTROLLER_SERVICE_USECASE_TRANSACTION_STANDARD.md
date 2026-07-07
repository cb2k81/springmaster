# Controller, Service, UseCase and Transaction Standard

## Purpose

This standard defines the canonical Springmaster layering rules for new reference APIs before `Catalog-demo` becomes the canonical implementation.

It turns the real-app findings from IDM and Personnel into a Springmaster-owned rule set for:

* controller responsibility;
* service style selection;
* query versus command separation;
* use-case handler usage;
* transaction ownership;
* security-check placement;
* repository and mapper boundaries;
* test and future gate expectations.

The standard is documentation-first. It does not change Java code, Maven configuration, tools, templates or existing target projects.

## Scope

This standard applies to new Springmaster reference APIs and to future projects generated from or supplied by Springmaster.

It does not require immediate changes in IDM, Personnel, Contacts, Orders or other existing applications. Existing applications remain comparison inputs until Catalog-demo proves the standard and the gate concept.

## Design principle

Springmaster does not force a single service style for every resource.

The required rule is explicit selection of the correct application shape:

| Situation | Canonical style |
|---|---|
| Simple CRUD-like management resource | `Controller -> ResourceService` or `Controller -> CommandService/QueryService` |
| UI-facing list/detail API with read models | `Controller -> QueryService` |
| Mutating business operation | `Controller -> CommandService` or `Controller -> UseCaseHandler` |
| Granular permission/assignment/relationship operation | `Controller -> UseCaseHandler` or dedicated command service method |
| Complex aggregate with invariants | `Controller -> CommandService -> DomainService/Aggregate` |
| Reusable domain rule independent of HTTP | `DomainService` or domain model method |
| Persistence access | Repository behind service/use-case boundary only |

The public HTTP contract is governed by the API standards. The internal service shape is governed by this standard.

## Controller responsibility

Controllers are HTTP boundary adapters.

A controller may:

* expose canonical endpoint paths and HTTP methods;
* bind path variables, query parameters and request bodies;
* activate API-boundary validation through `@Valid` or validated query DTOs;
* translate HTTP boundary input into DTOs, command objects or query objects;
* call exactly the appropriate application service, query service, command service or use-case handler;
* choose HTTP status codes and headers when this is part of the API contract;
* return the response DTO or a `ResponseEntity` containing the response DTO.

A controller must not:

* access repositories directly;
* contain business rules or persistence decisions;
* own transaction demarcation;
* expose JPA entities or domain aggregates as public request/response bodies;
* expose Spring Data `Pageable`, `Page<DTO>` or `Slice<DTO>` in new reference APIs;
* perform authorization as the only protection when the same operation is callable outside the controller;
* create local ad-hoc error bodies;
* hide domain conflicts, validation failures or not-found cases behind generic `500` responses.

## Service style selection

### Simple resource service

A simple resource service is acceptable when the resource is small, does not have complex lifecycle commands and does not require many independently secured operations.

Example responsibility shape:

* `list(query)`;
* `getById(id)` or `getRequiredByExternalId(id)`;
* `create(createCommand)`;
* `update(id, updateCommand)`;
* `delete(id)`.

The service still owns transaction demarcation and repository access.

### Query service

A query service owns read-oriented application behavior.

A query service should be used when:

* read models differ from write models;
* the API has paging, sorting, filtering or search semantics;
* multiple repositories or projections are involved;
* read-side authorization or tenant/context restrictions are required;
* UI lists need stable response DTOs.

Query services should use read-only transaction demarcation when repository access requires transactional consistency.

### Command service

A command service owns state-changing application behavior.

A command service should be used when:

* validation beyond API-boundary validation is required;
* a business invariant must be checked;
* several repositories or domain services participate;
* a conflict, lifecycle transition or optimistic-locking case can occur;
* an operation must be authorized at business-operation level.

Command services own write transaction demarcation.

### UseCaseHandler or CommandHandler

A use-case handler is preferred when one operation deserves an independently testable and independently secured unit.

Typical cases:

* assignment/unassignment;
* delete-multiple;
* state transition;
* import/export command;
* cross-aggregate command;
* operation-specific permission checks;
* operation-specific validation and error mapping.

Use-case handlers may internally call domain services and repositories. They still must respect transaction and security rules.

### Domain service

A domain service owns reusable domain behavior that is not HTTP-specific and not merely orchestration.

A domain service must not depend on Spring MVC types, request/response DTOs, `ResponseEntity`, servlet objects or controller annotations.

Domain services may be transactional only when they are used as application-service entry points. If they are internal collaborators, the transaction is usually owned by the surrounding command service or use-case handler.

## Query and command separation

New reference APIs must separate read and write concerns when the resource is more than trivial.

| Concern | Preferred owner |
|---|---|
| Paged list | Query service |
| Detail read | Query service or resource service |
| Bounded options/reference data | Query service |
| Complex search | Query service, using a search DTO/query object |
| Create | Command service or use-case handler |
| Full update | Command service or use-case handler |
| Patch/partial update | Command service or use-case handler |
| Single delete | Command service or use-case handler |
| Delete multiple | Use-case handler or command service command method |
| Assignment/relationship command | Use-case handler or command service |
| State transition | Use-case handler or command service |

The separation does not require a CQRS framework. It is a structural convention for clarity, testability and future gates.

## Transaction ownership

Transactions belong to the application service, command service, query service or use-case handler boundary, not to the controller.

Canonical rules:

* controllers must not be annotated with `@Transactional`;
* repository access must happen inside a service or use-case boundary;
* write operations must have an explicit write transaction at service/use-case level;
* read operations may use `@Transactional(readOnly = true)` where JPA consistency, lazy loading or repeatable read behavior is needed;
* one HTTP command should map to one business transaction unless an ADR explicitly defines a saga/outbox/async pattern;
* domain exceptions and optimistic-locking conflicts must be allowed to reach the global error mapping layer;
* long-running external I/O should not be performed inside a database transaction unless a specific integration ADR allows it;
* nested private method calls must not rely on Spring proxy transaction semantics.

## Security boundary

The full permission model is defined by a later security/permission standard. Until then, this standard defines the placement rule.

Authorization for business operations must live at the application-service, command-service, query-service or use-case boundary when the operation can be reused outside the HTTP controller.

Controller-level security may be used as a coarse HTTP gate, but it must not be the only protection for reusable application operations.

Recommended default:

* public or technical endpoints are explicitly documented;
* UI-facing management APIs require an operation-level permission;
* query and command services use method-level security or a dedicated authorization collaborator;
* tests verify denied access for at least representative query and command operations;
* permission names and role mappings are deferred to the dedicated security/permission standard.

## Repository boundary

Repositories are persistence adapters, not API collaborators.

Rules:

* controllers must not inject repositories;
* controllers must not call `EntityManager`;
* controllers must not construct JPA queries;
* repositories must not return public API response wrappers;
* repository methods may return entities, projections or persistence-oriented types;
* service/use-case layers convert persistence results into API-facing DTOs, read models or application results.

## Mapper boundary

Mappers convert between layers. They do not own business decisions.

Rules:

* controllers may use a mapper for simple inbound/outbound translation;
* services may use mappers for read-model and DTO assembly when the DTO is part of the application contract;
* mappers must not access repositories;
* mappers must not perform authorization checks;
* mappers must not decide lifecycle transitions;
* complex projections may use manual mappers, while simple mappings may use MapStruct or other explicit mapping support once a mapping standard exists.

## Error boundary

Controllers and services must rely on the canonical API error contract.

Rules:

* controllers must not return local ad-hoc `Map<String, Object>` error bodies;
* boundary validation failures are mapped to the standard validation error response;
* not-found cases must map to the standard not-found response;
* conflicts and domain invariant violations must map to the standard conflict or validation response according to the error contract;
* unexpected technical errors must map to the standard internal error response with `errorId`.

## Naming conventions

The following names are canonical candidates for new reference APIs.

| Type | Naming |
|---|---|
| Controller | `<Resource>Controller` |
| Resource service | `<Resource>Service` only for simple resources |
| Query service | `<Resource>QueryService` |
| Command service | `<Resource>CommandService` |
| Use-case handler | `<Verb><Resource>Handler` or `<Resource><CommandName>Handler` |
| Domain service | `<DomainConcept>DomainService` |
| Command object | `<Resource><CommandName>CommandDTO` at API boundary, internal command object if needed |
| Query object | `<Resource>QueryDTO` or internal query object |

Internal Java methods may use `findBy...` where an optional result is intentional. Public API operation names and paths must still follow the endpoint contract standard and must not expose ambiguous `findOne`, `findFirst` or `findLast` vocabulary.

## Spring Boot adaptation

Springmaster follows Spring Boot conventions only where they support the platform architecture.

Accepted Spring Boot-aligned practices:

* constructor injection for required collaborators;
* one clear application root package with intentional subpackages;
* controllers as MVC adapters;
* Bean Validation at the HTTP boundary;
* method-level transaction demarcation in Spring-managed services;
* MockMvc and integration tests for controller behavior.

Adapted Springmaster rules:

* package boundaries must reflect Core, app, domain and API ownership, not only generic Spring examples;
* transaction and security placement must follow reusable application-operation boundaries;
* endpoint naming must follow Springmaster API standards, not repository method names;
* generated OpenAPI shape and future gates are part of the architecture, not optional documentation.

## Catalog-demo readiness rule

Catalog-demo must not introduce a controller/service pattern that contradicts this standard.

The first canonical `CatalogItem` API must demonstrate at least:

* a thin controller;
* no controller-level transaction demarcation;
* no controller repository injection;
* DTO boundary validation;
* query behavior behind a query service or simple resource service;
* create/update/delete behavior behind a command service or simple resource service;
* standard error behavior through the global error contract;
* tests that verify positive and negative behavior without coupling to repository internals.

If Catalog-demo starts with a simple resource service, the decision must remain explicit and must not prevent later split into query and command services when complexity increases.

## Future gates

The following gates should be considered after the documentation standard is stable:

| Gate | Purpose |
|---|---|
| Controller transaction scan | fail if a controller is annotated with `@Transactional` |
| Controller repository scan | fail if a controller injects a repository or `EntityManager` |
| Controller boundary scan | fail if controllers expose entities, `Pageable`, `Page<DTO>` or `Slice<DTO>` in new reference APIs |
| Service transaction scan | verify command services/use-case handlers have explicit transaction policy |
| Security placement scan | verify management operations have operation-level authorization once permission standard exists |
| MockMvc contract tests | verify HTTP status, validation and error behavior |
| OpenAPI contract tests | verify path, request/response schema and status-code contract |
| Optional ArchUnit rule set | enforce package dependencies and forbidden controller dependencies |

## Deferred decisions

The following topics are intentionally not finalized here:

* permission naming and role mapping;
* exact method-security annotation style;
* mapping standard and MapStruct adoption rule;
* domain entity/persistence base class strategy;
* metadata, tags and reference-data persistence model;
* async, outbox and long-running command transaction patterns;
* exact Java interfaces for resource/query/command services.

These must be defined in later standards or ADRs before Catalog-demo uses them as canonical patterns.

## Security standard integration since 000052

Patch `000052_springmaster_security_permission_boundary_standard` resolves the previously deferred permission model at documentation level.

This controller/service/use-case standard remains responsible for placement: reusable management operations are authorized at query-service, command-service or use-case-handler boundaries. The security/permission standard is responsible for endpoint classification, permission naming, role-to-permission mapping, current-user/capability endpoints and later security gates.

Catalog-demo must satisfy both standards before any secured CatalogItem API becomes canonical.

## Mapping standard integration since 000054

Patch `000054_springmaster_mapping_standard` resolves the previously deferred mapping standard at documentation level.

This controller/service/use-case standard remains responsible for selecting the application flow and transaction boundary. The mapping standard is responsible for DTO, command, read-model, entity, option, relationship and command-result mapping rules. Controllers must not contain substantial mapping logic, and mappers must not contain repository access, transactions, authorization checks or business decisions.

Catalog-demo must satisfy both standards before any CatalogItem API slice becomes canonical.

## ADR-0003 acceptance since 000063

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts this standard as an architecture decision under `PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md`.

Consequences:

- controller, service, use-case, repository, mapper and transaction-placement rules are now ADR-backed for new Springmaster reference APIs;
- Catalog-demo implementation work must treat thin controllers, service/use-case transaction ownership and repository isolation as reference requirements;
- report-only Java boundary diagnostics may reference ADR-0003 as their rule source;
- strict Java boundary gates still require Catalog-demo evidence, stable implementation and explicit strict promotion under ADR-0006.


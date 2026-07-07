# Domain Entity and Persistence Standard

## Purpose

This standard defines the canonical Springmaster foundation rules for domain entities, persistence identity, repositories, auditing, optimistic locking, metadata, tags and business keys before `Catalog-demo` becomes the canonical reference implementation.

The standard turns the persistence findings from the current Springmaster Core, IDM and Personnel comparisons into a documentation-level rule set. It does not introduce Java code, Maven dependencies, database migrations, repository interfaces or target-project changes.

## Scope

This standard applies to new Springmaster reference APIs, the future `Catalog-demo` project and later projects generated from or supplied by Springmaster.

It does not require immediate changes in IDM, Personnel, Contacts, Orders or other existing applications. Existing applications remain comparison inputs until Catalog-demo proves the standard and the gate concept.

## Current foundation

The current Springmaster Core already contains a minimal persistence-oriented foundation under `de.cocondo.system`:

| Type or concept | Current role |
|---|---|
| `DomainEntity` | `@MappedSuperclass` with string `id`, `persistenceVersion`, tags and audit fields |
| `Auditable` | audit-field contract |
| `AuditingEntityListener` | JPA listener for technical audit timestamps/users |
| `DomainEntityListener` | JPA listener that protects against missing IDs before persistence |
| `Range` | embeddable validity range |
| `DomainEntityService` | factory/helper support for entities with generated IDs |
| `TagService` | collection-based tag helper |
| DTO metadata contracts | DTO-level metadata shape without a persistence model |

This foundation is intentionally smaller than the IDM legacy core. In particular, Springmaster has not adopted IDM's `DomainEntity` as a concrete `@Entity` hierarchy and has not adopted KeyValuePair metadata persistence or NumberSequence persistence yet.

## Design principle

Springmaster separates three identities:

| Identity | Purpose | Standard decision |
|---|---|---|
| Persistence identity | technical database identity | currently represented by `DomainEntity.id` as a string JPA `@Id` |
| Public API identity | externally visible resource identifier | opaque string identifier exposed as `id` in API DTOs |
| Business key | domain-facing number/code such as SKU, personnel number or organisation code | explicit resource field, not a replacement for `id` |

The current foundation allows the same opaque string to serve as persistence identity and public API identity. A later ADR may introduce a separate surrogate internal database ID for specific applications, but Catalog-demo must not invent that split implicitly.

## DomainEntity rule

New Springmaster reference entities should extend the Core `DomainEntity` only when they participate in the shared persistence and API identity model.

Canonical rules:

* `DomainEntity` remains a `@MappedSuperclass` in the current foundation.
* Concrete domain classes own their JPA `@Entity` annotation and table mapping.
* The inherited `id` is an opaque string identifier.
* Application code must not parse, encode or infer business semantics from `id`.
* API clients must treat `id` as opaque.
* Domain behavior belongs in the entity, domain service or command service, not in JPA listeners.
* Entity constructors may establish local invariants, but cross-aggregate rules belong outside the entity.
* Entities must not be used as public controller request or response types.

The Core `DomainEntity` is not a universal requirement for every future persistence type. Join tables, technical outbox rows, audit records or read-model projections may require separate persistence types and must be decided explicitly.

## ID generation

ID generation must be explicit and testable.

Canonical rules:

* New reference code should prefer the Springmaster `IdGeneratorService` when creating aggregate roots through services or factories.
* Direct UUID creation inside domain constructors remains a current fallback, not the preferred reference pattern for new service-created aggregates.
* A persisted entity must never reach `@PrePersist` with a missing ID.
* ID generators must remain fachfrei and must not depend on a concrete domain, database table or HTTP request.
* Public APIs must not accept client-generated resource IDs unless a dedicated standard or ADR permits it for a specific import or synchronization case.

Catalog-demo should demonstrate service-owned ID creation so that the later Core can decide whether `DomainEntity` constructor fallback stays, is deprecated or is reserved for test-only/simple cases.

## External ID and business key rule

External API IDs are opaque strings. Business keys are domain fields.

Rules:

* `GET /api/<domain>/<resources>/{id}` uses the opaque API ID.
* Alternative lookups use the endpoint contract standard, for example `GET /api/<domain>/<resources>/by-<key>/{value}`.
* A business key such as `sku`, `number`, `code` or `externalReference` must be modeled as an explicit field with unique constraints when uniqueness is required.
* A business key must not silently become the technical JPA `@Id` without an ADR.
* A business key may be immutable after creation if the domain requires it; the DTO/update standard must make this visible.
* Error behavior for duplicate business keys follows the API error contract and usually maps to `409` conflict.

## Repository boundary

Repositories are persistence adapters behind the application layer.

Canonical rules:

* Controllers must not inject repositories or `EntityManager`.
* Application services, command services, query services or use-case handlers own repository usage.
* Repositories must not expose API response wrappers such as `PagedResponseDTO`.
* Repositories may return entities, persistence projections or read-model projections.
* Repository method names are internal Java vocabulary and must not define public endpoint vocabulary.
* Public API lookups must be explicitly named in the API standard even when the repository method is `findBy...`.
* Repository interfaces belong to the application/domain persistence package of the concrete project, not automatically to the Springmaster Core.

A reusable Core repository base interface may be introduced later only after Catalog-demo proves a stable need.

## Transaction and persistence boundary

Persistence work must be performed inside the controller/service/use-case/transaction standard.

Rules:

* write operations must be transactional at command-service or use-case level;
* read operations may use `readOnly` transactions when JPA consistency or lazy loading requires it;
* one HTTP command usually maps to one business transaction;
* domain exceptions and optimistic-locking exceptions must flow to the global error mapping layer;
* repository flush timing must not be used as the only place where business validation happens;
* long-running external I/O inside a database transaction requires a later integration/outbox/async standard.

## Auditing standard

Springmaster distinguishes technical audit fields from business history.

Canonical audit fields:

* `createdBy`;
* `createdAt`;
* `lastModifiedBy`;
* `lastModifiedAt`.

Rules:

* audit fields are maintained by infrastructure or service-level context, not by arbitrary controller input;
* API clients should not be allowed to set audit fields through create/update DTOs;
* response DTOs may expose audit information when the API contract requires it;
* absence of an authenticated user must have a deterministic system-user or technical-user strategy before production use;
* business lifecycle history, audit logs and event streams are separate patterns and are not covered by these four audit fields.

The current Core listener is a foundation. A later security/permission/current-user standard must define how authenticated user information reaches audit infrastructure.

## Optimistic locking standard

`persistenceVersion` is the canonical technical optimistic-locking field in the current foundation.

Rules:

* persisted aggregate roots should use an optimistic-locking version field;
* update and delete commands for mutable resources should define whether the version is required, optional or deferred;
* stale updates must not be reported as generic internal errors;
* optimistic-locking conflicts should map to the API error contract as conflict errors;
* the public DTO name for the version must remain stable if exposed.

Catalog-demo should include an update path that makes the optimistic-locking decision explicit before the pattern becomes canonical.

## Delete and lifecycle persistence rule

The endpoint standard defines HTTP delete shapes. This standard defines persistence implications.

Rules:

* hard delete is acceptable only when the resource has no retention, audit, historical reporting or referential-integrity requirement that forbids it;
* soft delete, archive and deactivate are domain/lifecycle concepts and must be modeled as commands or state transitions, not disguised as generic delete;
* delete-multiple must be transactional and must define partial-success behavior before implementation;
* deletion must respect optimistic-locking and authorization decisions where applicable;
* database cascades must not be the only documented business rule for aggregate deletion.

Catalog-demo may start with hard delete only if the demo resource is intentionally simple and the decision is recorded.

## Metadata, tags and key-value data

Springmaster currently supports tags and DTO-level metadata contracts, but it does not yet define a canonical persistent metadata model.

Current decision:

* tags are supported as simple labels on `DomainEntity`;
* DTO metadata contracts are available;
* persistent KeyValuePair metadata is deferred;
* IDM-style `KeyValuePair` JPA persistence must not be copied into Springmaster without a dedicated metadata persistence ADR;
* `Metadata` must not become an uncontrolled escape hatch for fields that belong to the domain model.

Rules for future metadata:

* typed domain fields are preferred over dynamic key-value fields;
* metadata keys require ownership, naming and validation rules;
* metadata persistence requires explicit table, lifecycle, migration and query decisions;
* API exposure of metadata must follow DTO and error standards;
* UI-readiness must define which metadata is listable, filterable, editable or read-only.

## NumberSequence and generated business numbers

Number sequences are fachfrei but not persistence-light.

Current decision:

* NumberSequence is not part of the current canonical Core runtime;
* business numbers are not the same as `DomainEntity.id`;
* Catalog-demo must not invent a sequence implementation inside the domain slice.

Before a reusable NumberSequence Core feature is introduced, Springmaster needs decisions for:

* table/schema naming;
* locking and concurrency semantics;
* transaction boundary;
* gap handling;
* reset/scoping rules;
* repository/runtime dependencies;
* Liquibase/change-management ownership;
* test strategy under concurrent access.

Until then, demo resources may use manually supplied or simple deterministic business keys only when the standard explicitly documents them.

## Table and schema rule

Concrete applications own concrete entity table names and database migrations.

Rules:

* Core may define mapped-superclass fields and embeddables;
* concrete domain entities define their own tables;
* a reusable Core entity with its own table requires a dedicated ADR and migration policy;
* schema/table names must be deterministic and stable once a reference project exposes them;
* generated demo migrations must not be copied from IDM or Personnel without abstraction.

## Catalog-demo readiness rule

Catalog-demo must not introduce persistence behavior that contradicts this standard.

Before the first canonical `CatalogItem` persistence slice becomes the reference, it must explicitly decide:

* whether `CatalogItem` extends Core `DomainEntity`;
* how the opaque `id` is generated;
* whether `CatalogItem` has a business key such as `sku`;
* whether `sku` is unique and immutable;
* whether `persistenceVersion` is exposed or required for update/delete;
* whether delete is hard delete, archive or deactivate;
* whether tags are supported in the first slice;
* whether metadata is deferred;
* whether NumberSequence is deferred;
* which repository package and test style are canonical.

The first slice may intentionally defer some concerns, but each deferral must be visible in the documentation and tests.

## Future gates

The following gates should be considered after the documentation standard is stable:

| Gate | Purpose |
|---|---|
| Entity boundary scan | fail if controllers expose JPA entities as request or response types |
| DomainEntity extension scan | report entities that should or should not extend Core `DomainEntity` |
| Repository boundary scan | fail if controllers inject repositories or `EntityManager` |
| Transaction scan | verify write services/use cases have explicit transaction policy |
| Optimistic-locking scan | verify mutable aggregate roots have a version strategy |
| DTO/OpenAPI ID scan | verify API IDs are strings and business keys are separate fields |
| Metadata usage scan | report dynamic metadata usage before the metadata ADR exists |
| Delete behavior tests | verify hard delete, archive or deactivate semantics are explicit |
| Persistence integration tests | verify repository behavior, unique constraints and optimistic-locking conflicts |
| Optional ArchUnit rules | enforce package boundaries and forbidden dependencies |

## Deferred decisions

The following topics are intentionally not finalized here:

* a separate internal surrogate database ID;
* a Core repository base interface;
* a persistent KeyValuePair metadata model;
* NumberSequence implementation;
* soft-delete base class;
* audit-current-user provider;
* outbox/event persistence;
* multi-tenancy fields;
* reusable Liquibase schema fragments;
* exact ArchUnit rule implementation;
* migration of existing IDM or Personnel entities.

These require later standards, ADRs or code patches before they become part of the canonical Springmaster implementation.

## Security standard integration since 000052

Patch `000052_springmaster_security_permission_boundary_standard` defines the security-side current-user expectation for audit fields.

This persistence standard remains responsible for the meaning of `createdBy`, `createdAt`, `lastModifiedBy` and `lastModifiedAt`. The security/permission standard is responsible for the current-user provider boundary, authenticated versus system principals and testability of audit-current-user behavior.

The current-user provider itself remains a later code decision.

## Mapping standard integration since 000054

Patch `000054_springmaster_mapping_standard` defines how persisted entities, business keys, optimistic-lock fields, audit fields, metadata, tags and relationship summaries are translated into public DTO roles.

This persistence standard remains responsible for the entity, repository and persistence identity rules. The mapping standard is responsible for ensuring those persistence types are not exposed as public API models and that mapper code does not trigger hidden persistence access or lazy-loading side effects.




## ADR-0004 acceptance since 000064

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts `PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md`.

ADR-backed clarifications:

* `DomainEntity` remains the mapped-superclass default for standard aggregate roots in new Springmaster reference APIs.
* The default model uses an opaque string `id` as persistence identity and public API identity.
* Business keys remain explicit domain fields and must not silently become JPA IDs.
* Internal surrogate IDs are exceptions that require explicit documented criteria and must not leak into normal public API contracts.
* `persistenceVersion` is the canonical optimistic-locking field in the current foundation.
* Technical audit fields remain distinct from business history and client input.
* Repository access remains behind application-service or use-case boundaries.
* Persistent metadata, NumberSequence, soft-delete base classes, outbox/event persistence, multi-tenancy fields and Core repository base interfaces remain deferred.

Gate impact:

* Report-only persistence identity diagnostics may reference ADR-0004.
* Strict persistence gates require implementation evidence, Catalog-demo proof and explicit strict promotion under ADR-0006.


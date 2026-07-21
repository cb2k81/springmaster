# ADR-0004: Persistence Identity and DomainEntity Strategy

## Status

Accepted

## Date

2026-06-30

## Context

Springmaster contains a small persistence-oriented Core foundation under `de.cocondo.system`. The current Core includes `DomainEntity` as a `@MappedSuperclass`, a string `id`, `persistenceVersion`, audit fields, tags, entity listeners, ID generation support and basic helper services.

Patch `000051_springmaster_domain_entity_persistence_standard` documented the initial persistence standard. The later ADR and standards work clarified surrounding boundaries:

- `ADR-0002` defines public API IDs, DTO boundaries, endpoint vocabulary, error behavior and first-slice status-code rules.
- `ADR-0003` defines application-layer, repository and transaction boundaries.
- `ADR-0006` defines gate modes, severity vocabulary, report structure and strict-promotion rules.

Springmaster now needs an accepted architecture decision for persistence identity before Catalog-demo can become a canonical reference and before persistence-related Java diagnostics or gates are implemented. Existing IDM and Personnel patterns are useful comparison inputs, but Springmaster must not silently copy IDM-style concrete entity hierarchies, dynamic metadata persistence or business-number strategies into the reference foundation.

## Decision

Springmaster accepts the following persistence identity and `DomainEntity` strategy as canonical for new Springmaster reference APIs, Catalog-demo slices and future generated project templates.

### Identity model

Springmaster separates three identity concepts:

| Identity | Meaning | Accepted default |
|---|---|---|
| Persistence identity | technical JPA/database identity | `DomainEntity.id` as opaque string `@Id` for standard aggregate roots |
| Public API identity | externally visible resource identifier | opaque string `id` in DTOs and path variables |
| Business key | domain-facing code, number or reference such as `sku`, `number`, `code` | explicit domain field with explicit uniqueness and mutability rules |

For the default Springmaster reference model, the same opaque string may serve as persistence identity and public API identity. Code must not parse, encode, sort by, or infer business semantics from that value.

A separate internal surrogate database ID is not the default. It requires an explicit ADR, project-local decision record or generated-project option before it becomes reference behavior.

### DomainEntity default

`DomainEntity` remains a Core `@MappedSuperclass` foundation, not a concrete root entity hierarchy.

Accepted rules:

- concrete domain entities own their own `@Entity` annotation and table mapping;
- standard aggregate roots should extend Core `DomainEntity` when they participate in the shared identity, optimistic-locking and audit model;
- entities must not be used as public controller request or response types;
- domain behavior belongs in the entity, a domain service, command service or use-case handler, not in JPA listeners;
- join tables, outbox rows, audit-log rows, read-model projections, import staging rows and technical integration rows are not automatically `DomainEntity` types.

Catalog-demo `CatalogItem` should use `DomainEntity` for the canonical first persistence slice unless a later ADR explicitly selects a different identity model.

### ID generation

ID generation must be explicit and testable.

Accepted rules:

- application services, command services, factories or use-case handlers should create aggregate IDs through the Springmaster `IdGeneratorService` or an equivalent accepted ID-generation boundary;
- direct UUID generation inside domain constructors remains tolerated as a foundation fallback, but it is not the preferred reference pattern for new service-created aggregate roots;
- persisted aggregate roots must have an ID before `@PrePersist`;
- public create APIs must not accept client-chosen resource IDs unless an import, synchronization or external-system ADR explicitly permits it;
- ID generators must remain fachfrei and must not depend on concrete domain tables, HTTP requests or target-project-specific naming.

### Business keys

Business keys are domain facts, not persistence IDs.

Accepted rules:

- a business key such as `sku`, `number`, `code`, `externalReference` or `personnelNumber` is modeled as an explicit field;
- uniqueness must be enforced in application validation and persistence constraints when the business key is unique;
- mutability must be visible in create/update DTOs and command behavior;
- duplicate business keys map to the canonical API conflict behavior from ADR-0002;
- business keys may have alternative lookup endpoints such as `/by-<key>/{value}` when ADR-0002 endpoint rules are met;
- a business key must not silently become the technical JPA `@Id` for new reference APIs.

Catalog-demo should use `sku` as the first explicit business-key example if the first slice needs a domain-facing lookup or uniqueness rule.

### Internal surrogate ID exception criteria

A separate internal surrogate ID may be acceptable only when the reason is explicit.

Allowed criteria include:

- legacy database compatibility where an existing numeric primary key cannot be changed;
- high-volume persistence or indexing constraints that require an internal database key while preserving an opaque public ID;
- integration with an external system that mandates a stable public identifier separate from the local row key;
- multi-tenant or sharded storage strategies that require a composite or internal physical key;
- migration scenarios where public IDs must remain stable while internal persistence identity changes.

When an internal surrogate ID is used, public API contracts must still expose only the opaque public ID unless a dedicated administration or migration API explicitly says otherwise. Numeric internal IDs must not leak into normal management API paths, DTOs or OpenAPI schemas.

### Optimistic locking

`persistenceVersion` is the canonical technical optimistic-locking field in the current Springmaster foundation.

Accepted rules:

- mutable aggregate roots should have a version strategy;
- update and delete commands must explicitly state whether the version is required, optional or deferred;
- stale updates or stale deletes must map to the canonical conflict behavior from ADR-0002 and must not become generic `500` responses;
- if `persistenceVersion` is exposed in DTOs, the public DTO property name remains stable;
- first-slice Catalog-demo may defer client-supplied version enforcement only when the deferral is documented in readiness docs and tests.

### Audit fields

Springmaster distinguishes technical audit fields from business history.

Accepted technical audit fields are:

- `createdBy`;
- `createdAt`;
- `lastModifiedBy`;
- `lastModifiedAt`.

Audit fields are maintained by infrastructure or service-level context. API clients must not set them through create/update DTOs. Business lifecycle history, event streams, audit logs and reporting histories are separate patterns and are not introduced by this ADR.

Current-user propagation into audit infrastructure remains related to the future security/permission ADR and observability work. Until then, reference code must use deterministic system-user or test-user behavior rather than silent nulls or request-body supplied audit values.

### Repository boundary

Repositories are persistence adapters behind the application layer.

Accepted rules:

- controllers must not inject repositories or `EntityManager`;
- query services, command services, resource services or use-case handlers own repository access;
- repositories must not expose API response wrappers such as `PagedResponseDTO`;
- repository method names may use internal Java vocabulary such as `findBy...`, but public endpoint vocabulary is governed by ADR-0002;
- repository interfaces belong to the concrete application/domain persistence package unless a later Core repository-base ADR introduces reusable repository contracts.

This ADR does not introduce a Springmaster Core repository base interface.

### Delete and lifecycle persistence

HTTP delete shape is governed by ADR-0002. Persistence lifecycle semantics must be explicit.

Accepted rules:

- hard delete is acceptable for a simple demo resource when retention, audit history and reporting requirements do not require a lifecycle state;
- archive, deactivate, soft-delete and restore are domain/lifecycle commands, not disguised generic deletes;
- delete-multiple requires explicit transaction and partial-success semantics before becoming canonical;
- database cascades must not be the only documented business rule for aggregate deletion.

### Deferred persistence features

The following features are not canonical reference behavior yet:

- persistent dynamic `KeyValuePair` metadata;
- reusable NumberSequence persistence;
- soft-delete base classes;
- outbox/event persistence;
- multi-tenancy persistence fields;
- reusable Liquibase schema fragments;
- Core repository base interfaces;
- migration of IDM or Personnel persistence models into Springmaster.

They require later standards, ADRs or code patches before they become part of the canonical implementation.

## Scope

This ADR applies to:

- new Springmaster reference APIs;
- Catalog-demo persistence slices;
- future generated project templates when they produce persisted management resources;
- report-only persistence identity diagnostics;
- future read-only target-project comparison.

This ADR does not require immediate changes to IDM, Personnel, Contacts, Orders or other existing target projects. Existing projects remain comparison inputs until Catalog-demo proves the pattern and target delivery is explicitly authorized.

## Affected standards

This ADR accepts and consolidates the architectural decisions from:

- `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/EXTERNAL_ID_OPENAPI_BOUNDARY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md` for opaque ID lookup paths
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md` and `PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md` for conflict/error behavior
- `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md` for transaction ownership
- `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md` for entity-to-DTO boundary mapping

This ADR depends on:

- `ADR-0002-api-boundary-and-endpoint-contract.md` for public API and DTO identity exposure;
- `ADR-0003-application-layer-and-transaction-boundary.md` for repository and transaction placement;
- `ADR-0006-verification-and-gate-strategy.md` for gate modes, severities, reports and strict-promotion rules.

It does not replace future ADRs for security/permission current-user propagation, Catalog-demo canonicalization, database migration/DBTool strategy, observability/tracing, outbox/event persistence or metadata persistence.

## Considered alternatives

### Copy IDM-style concrete entity hierarchy into Springmaster

Rejected. It would import application-specific legacy assumptions into the reference foundation and would make Catalog-demo canonical before Springmaster proves the abstraction.

### Use business keys as JPA IDs by default

Rejected. Business keys are domain-facing and may have their own mutability, formatting, import and conflict behavior. They must remain explicit domain fields unless a dedicated ADR approves an exception.

### Make numeric internal surrogate IDs the default

Rejected for the current foundation. Numeric internal IDs are valid in some architectures, but Springmaster already has a working opaque string identity model. A surrogate-ID split would add complexity and must be justified by explicit criteria.

### Avoid a shared DomainEntity foundation

Rejected for the standard aggregate-root case. The current Core foundation provides a compact shared identity, audit and version model. Avoiding it everywhere would reduce consistency and make persistence gates less useful.

### Introduce metadata, NumberSequence, soft-delete and outbox now

Rejected. These features are important but each carries schema, migration, transaction, concurrency and API implications. They need dedicated standards or ADRs before becoming reference behavior.

### Enable strict persistence gates immediately

Rejected. ADR-0006 requires report-only first, stable implementation evidence, Catalog-demo proof and explicit strict promotion before fail-build behavior.

## Consequences

Positive consequences:

- Catalog-demo can demonstrate a clear persistence identity pattern without copying target-project accidents.
- Public API identity remains stable and opaque.
- Business keys remain explicit and testable.
- Optimistic-locking and audit semantics are visible before implementation becomes canonical.
- Persistence-related gates have an accepted ADR rule source.

Costs and constraints:

- Some simple entities require explicit ID generation and version decisions even when ad-hoc UUID fields would be shorter.
- Internal surrogate-ID projects need an explicit exception decision.
- Metadata, NumberSequence and soft-delete remain unavailable as general reference behavior until later work.
- Strict persistence gates still require implementation evidence and Catalog-demo proof.

## Gate implications

This ADR enables report-only diagnostics for:

- entity classes that expose numeric public IDs for new reference APIs;
- controller signatures that expose JPA entities;
- aggregate roots missing an explicit ID generation path;
- mutable aggregate roots without a documented version strategy;
- business-key fields lacking documented uniqueness or mutability behavior;
- controllers injecting repositories or `EntityManager`, in combination with ADR-0003;
- use of dynamic metadata persistence before a metadata ADR exists;
- introduction of NumberSequence persistence before a sequence ADR exists.

Strict gates are not enabled merely by this ADR. Strict promotion requires:

1. ADR-0006 mode and report semantics;
2. stable gate implementation and tests;
3. Catalog-demo evidence;
4. deterministic pass/fail criteria;
5. a later patch that marks the specific rule strict-ready.

## Exceptions and deferrals

Allowed exceptions and deferrals:

- internal surrogate IDs may be used only with explicit documented criteria and without public API leakage;
- non-aggregate persistence types do not automatically extend `DomainEntity`;
- Catalog-demo may start with hard delete when the simple-resource decision is documented;
- client-supplied version enforcement may be deferred for the first Catalog-demo slice if tests and readiness docs make the deferral visible;
- current-user audit provider details remain deferred to security/observability work;
- existing target-project deviations remain tolerated in read-only comparison until a later delivery workflow is explicitly approved.

## Supersession

This ADR does not supersede prior accepted ADRs.

It accepts the architecture decision behind `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md` and narrows it into an ADR-backed baseline for new Springmaster reference work.

It is complemented by:

- `ADR-0002-api-boundary-and-endpoint-contract.md`
- `ADR-0003-application-layer-and-transaction-boundary.md`
- `ADR-0006-verification-and-gate-strategy.md`

Future ADRs may narrow related areas:

- ADR-0005 for security and permission boundary including current-user propagation;
- ADR-0007 for Catalog-demo canonicalization;
- ADR-0009 for database migration and DBTool strategy;
- ADR-0010 for observability and error trace strategy.

## Staged assigned-ID newness transition

The target newness model for assigned opaque IDs is accepted: a transient entity keeps a nullable `Long` optimistic-locking version, the first successful insert produces version `0`, and later updates increase the version monotonically. Spring Data `Persistable` is not introduced into the fachfrei Core.

This patch records the decision only. The existing in-memory CatalogItem runtime and its `0L` compatibility initializer remain unchanged until one atomic persistent-candidate patch can change the Core field, repository runtime, Liquibase schema and all affected tests together. A half-transition is an invalid baseline.

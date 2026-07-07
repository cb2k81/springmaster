# Mapping Standard

## Purpose

This standard defines the canonical Springmaster rules for mapping between API DTOs, application command/query objects, domain entities, persistence projections and reference-data representations before `Catalog-demo` becomes the canonical reference implementation.

The standard turns the real-app findings from IDM and Personnel into a Springmaster-owned rule set. It does not introduce Java code, MapStruct configuration, Maven dependencies, generated mappers, ArchUnit rules, target-project changes or Catalog-demo implementation changes.

## Scope

This standard applies to new Springmaster reference APIs, the future `Catalog-demo` project and later projects generated from or supplied by Springmaster.

It does not require immediate changes in IDM, Personnel, Contacts, Orders or other existing applications. Existing applications remain comparison inputs until Catalog-demo proves the standard and the gate concept.

## Design principle

Mapping is an application-boundary responsibility.

A mapper translates between already-defined models. It must not own business decisions, persistence loading, authorization, transaction handling or HTTP behavior.

Springmaster uses explicit mapping because the reference implementation must be readable, testable and gateable. The correct mapping style depends on the mapping complexity.

| Situation | Canonical mapping style |
|---|---|
| Simple field-to-field entity/DTO mapping | MapStruct is preferred when the project uses MapStruct |
| Complex read-model projection | Manual mapper or dedicated projection assembler is allowed |
| Command DTO to application command object | Manual constructor/factory or simple mapper is allowed |
| Relationship summary mapping | explicit mapper method, no implicit lazy-loading surprise |
| Metadata/audit mapping | explicit inclusion/exclusion decision per DTO role |
| Option/reference-data mapping | dedicated option/list-item mapper method |
| Mapping requiring repository lookup | not a mapper responsibility; service/use-case resolves dependencies first |

Springmaster does not blindly mandate MapStruct everywhere. The standard mandates explicit, deterministic and testable mapping.

## Mapper responsibilities

A mapper may:

* copy scalar fields between DTOs, command objects, read models and entities;
* transform value objects to their public DTO shape;
* create list-item, detail, option and command-result DTOs;
* flatten already-loaded relationship summaries into DTOs;
* map explicit metadata fields when the DTO role includes metadata;
* ignore or expose audit fields only according to the DTO standard;
* assemble response DTOs from values that have already been authorized and loaded by the application layer;
* use helper methods for null-safe value conversion, enum conversion and collection conversion.

A mapper must not:

* access repositories, `EntityManager`, external clients or other persistence infrastructure;
* start or require transactions;
* call services or use-case handlers;
* perform authorization or permission checks;
* generate resource IDs or business numbers;
* decide whether an operation is allowed;
* swallow domain conflicts or validation errors;
* create HTTP responses, status codes or error bodies;
* expose JPA entities through public API DTOs;
* rely on lazy loading that is not explicitly prepared by the service/query layer;
* encode business semantics into opaque IDs.

## Placement

Mapper classes belong below the application/domain boundary of the owning resource, not in controllers and not in the Core by default.

Canonical placement rules:

* Controller methods call services/use cases and return DTOs; they do not contain mapping logic beyond trivial request binding.
* Query services or command services decide which mapper method is appropriate for the response role.
* Domain entities do not know API DTOs.
* Core may provide generic helper types and test utilities later, but Core must not depend on application-specific DTOs.
* Mappers may be package-private when only one service needs them, or Spring beans when reuse/test isolation justifies injection.

## Naming conventions

Springmaster uses role-oriented mapper names.

| Mapper role | Naming convention | Purpose |
|---|---|---|
| General resource mapper | `<Resource>Mapper` | small resources with simple create/detail/list mapping |
| Read mapper | `<Resource>ReadMapper` | list/detail/read-model mapping |
| Command mapper | `<Resource>CommandMapper` | inbound DTO to command object mapping |
| Option mapper | `<Resource>OptionMapper` or method on read mapper | selector/reference-data DTO mapping |
| Relationship mapper | `<Resource>RelationshipMapper` | relationship summaries and assignment result mapping |
| Manual assembler | `<Resource>ResponseAssembler` | complex response composition from multiple prepared inputs |

A project may start with a single `<Resource>Mapper`. It should split the mapper when mapping responsibilities become independently testable or when read/command/relationship behavior diverges.

## MapStruct usage

MapStruct is preferred for straightforward structural mappings when the application already uses MapStruct or when the generated mapper improves consistency.

Canonical MapStruct rules for new Springmaster reference code:

* use strict unmapped-target handling where practical;
* keep mapping expressions simple and visible;
* avoid repository/service calls from mapper expressions;
* use explicit `@Mapping` rules when field names or semantics differ;
* ignore technical fields intentionally rather than accidentally;
* keep generated mappers in the application module, not in the Core;
* unit-test non-trivial mappings and every mapping with ignored or renamed fields.

MapStruct is not mandatory for:

* complex read models;
* projections assembled from multiple sources;
* command objects whose constructors enforce invariants;
* small mappings that are clearer as explicit constructors;
* mappings with security- or context-dependent visibility decisions.

When MapStruct is used for a public API DTO, unmapped fields must be treated as a review item. Silent field loss is not acceptable for reference APIs.

## Manual mapper usage

Manual mappers are canonical when they make the intent clearer than generated mapping.

Manual mapping is preferred for:

* complex list/detail read models;
* DTOs that intentionally hide audit, metadata or security-sensitive fields;
* relationship summaries with preloaded names, labels or counts;
* command result DTOs that combine IDs, versions and status information;
* projection DTOs not backed by a single aggregate root;
* conversions that need explicit null or enum handling.

Manual mappers must still be deterministic and testable. They must not become a place for business policy.

## DTO role mapping rules

Mapping must respect the DTO role taxonomy from `DTO_BOUNDARY_AND_VALIDATION_STANDARD.md`.

| DTO role | Mapping rule |
|---|---|
| `<Resource>CreateDTO` | mapped to create command/input; never directly exposed as entity constructor input from controller |
| `<Resource>UpdateDTO` | mapped to update command/input with path ID kept separate |
| `<Resource>PatchDTO` | mapped to patch command/input only when PATCH is explicitly supported |
| `<Resource><CommandName>CommandDTO` | mapped to command input; operation target ID usually comes from path, not body |
| `<Resource>SearchDTO` | mapped to search criteria object and validated before query execution |
| `<Resource>QueryDTO` | mapped from explicit query params or created by controller binding for read operations |
| `<Resource>DTO` | maps detail response, not persistence entity exposure |
| `<Resource>ListItemDTO` | maps table/list response with stable lightweight fields |
| `<Resource>OptionDTO` | maps bounded selector/reference-data response |
| `<Resource><CommandName>ResultDTO` | maps command result when `204 No Content` is not enough |

Path variables and authenticated principal information are not trusted from request bodies. The service or use-case combines path, principal and DTO-derived command input.

## Entity mapping rules

Entities are not public API models.

Canonical entity mapping rules:

* entity to response DTO mapping is allowed only inside application/query/service layer;
* create/update DTOs do not overwrite entity identity, audit fields or optimistic-lock fields unless a standard explicitly allows it;
* opaque `id` is copied as a string only when the response DTO exposes the resource ID;
* business keys such as `sku`, `number` or `code` are mapped as explicit fields;
* `persistenceVersion` may be exposed only when the API contract uses it for optimistic locking or diagnostics;
* deleted, archived or inactive lifecycle state must be mapped explicitly when visible to clients;
* entity collections must be mapped to response DTO collections, never returned directly.

A mapper must not parse or construct semantic information from opaque IDs.

## Relationship mapping

Relationship mapping must follow `COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md`.

Canonical rules:

* relationship read endpoints return DTOs that describe the relationship from the API perspective;
* relationship command endpoints use dedicated command DTOs and, where needed, command-result DTOs;
* relationship summaries must be prepared by query/service code before mapping;
* mappers must not trigger hidden lazy-loading cascades to discover relationship display fields;
* relationship DTOs should expose target IDs and stable display labels where needed by the UI;
* assignment result DTOs should include affected IDs, result status and conflict information only when the command contract requires a body.

## Metadata and audit mapping

Metadata, tags and audit fields require explicit visibility decisions.

Canonical rules:

* audit fields are not automatically exposed on every DTO;
* DTOs that expose audit fields must document the reason and field shape;
* metadata and tags are mapped only when the DTO role includes them;
* dynamic metadata persistence remains deferred by `DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`;
* mappers must not synthesize metadata semantics that are not present in the domain/application model.

## Validation and mapping boundary

Bean Validation belongs to the API boundary; domain invariants belong to the domain/application layer.

Mapping must happen only after boundary input has been validated. A mapper may perform mechanical null-safe conversion, but it must not replace validation or domain checks.

Examples:

* `@Valid @RequestBody CatalogItemCreateDTO` validates required inbound fields;
* the command service verifies uniqueness and business conflicts;
* the mapper copies validated scalar values into a create command or entity update method;
* errors are returned through `API_ERROR_CONTRACT_STANDARD.md`, not as mapper-specific exceptions unless translated by the application boundary.

## Transaction and security boundary

Mapping must not define transaction or security behavior.

Canonical rules:

* mapping occurs inside the service/use-case flow selected by `CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md`;
* authorization decisions follow `SECURITY_PERMISSION_BOUNDARY_STANDARD.md`;
* mapper output must not vary based on hidden permission checks inside the mapper;
* when field-level visibility is needed, the service/use-case must make the visibility decision and call an explicit mapper method for that response role.

## Catalog-demo readiness rule

Catalog-demo must not become canonical until the first persistent API slice demonstrates mapping intentionally.

The first CatalogItem reference slice must define:

* which mapper classes exist;
* whether MapStruct or manual mapping is used for the slice;
* how create/update DTOs map to command inputs;
* how entity/read-model data maps to detail DTO and list-item DTO;
* how option DTOs are mapped if `/options` exists;
* how audit, metadata, business key and optimistic-lock fields are included or deferred;
* which mapper tests prove the chosen mapping behavior;
* which later gates will prevent repository/service/security logic from entering mappers.

A minimal first slice may use a manual mapper, but the choice must be documented and must not contradict this standard.

## Future gates

The following gates should be considered after the documentation standard is stable:

| Gate | Purpose |
|---|---|
| Mapper dependency scan | fail if mapper classes inject repositories, `EntityManager`, services or external clients |
| Mapper transaction scan | fail if mapper classes or methods use `@Transactional` |
| Mapper security scan | fail if mapper classes own `@PreAuthorize`, role checks or permission checks |
| DTO/entity boundary scan | fail if controllers expose JPA entities or domain aggregates |
| Response role scan | verify list/detail/option/result DTO naming and usage in new reference APIs |
| MapStruct strictness scan | report generated mappers without strict unmapped-target policy where MapStruct is used |
| Lazy-loading risk review | report mapping methods that traverse relationships not prepared by query/service code |
| Mapping unit tests | verify renamed, ignored, metadata, audit and relationship fields |
| OpenAPI response-shape tests | verify mapped public DTO shape rather than internal entity shape |
| Optional ArchUnit rules | enforce mapper package dependencies and forbidden dependencies |

## Deferred decisions

The following topics are intentionally not finalized here:

* whether MapStruct becomes a template dependency for every generated project;
* a shared Core mapper interface;
* a shared Core mapper test utility;
* exact ArchUnit implementation;
* field-level security helper patterns;
* metadata DTO helper mapping;
* standardized command object classes separate from command DTOs;
* migration of IDM or Personnel mapper implementations.

These require later ADRs, code patches or gate patches before they become canonical implementation assets.

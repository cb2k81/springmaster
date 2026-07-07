# DTO Boundary and Validation Standard

## Status

Accepted as generic Springmaster API standard with patch `000049_springmaster_dto_boundary_and_validation_standard`.

## Purpose

Springmaster APIs must keep the external HTTP contract separate from internal domain, persistence and service models. DTO boundaries and validation rules are therefore not implementation details; they define what clients may send, what clients may receive and what OpenAPI can safely expose.

This standard converts the high-priority DTO and validation findings from `000047_springmaster_real_app_pattern_forensics` into concrete Springmaster rules before Catalog-demo becomes canonical. It is based on reusable patterns visible in IDM and Personnel, but it does not require or authorize changes to IDM, Personnel, Contacts, Orders or other existing target projects.

## Design principles

DTOs are the public API representation. Domain entities, JPA persistence types and framework convenience types are internal implementation details unless a later ADR explicitly defines a different public boundary for a special integration API.

Springmaster reference APIs must:

- expose only DTOs, scalar path variables and documented query parameters at the controller boundary,
- activate validation at the HTTP boundary before command handling starts,
- make required inbound fields visible in generated OpenAPI,
- keep server-managed fields out of inbound create/update DTOs unless an endpoint explicitly documents them as command inputs,
- keep Spring Data and JPA types out of public response contracts,
- distinguish request DTOs from response DTOs whenever requiredness, mutability or server-managed fields differ,
- define future gates that can reject accidental entity, `Pageable` or `Page<DTO>` leakage.

## Public controller boundary

New Springmaster reference controllers use DTOs at the HTTP boundary.

Allowed public controller inputs:

- `String` or other simple scalar path variables for opaque external IDs and lookup values,
- documented query parameters via explicit `@RequestParam` arguments,
- a dedicated query DTO when query complexity justifies grouping,
- a dedicated JSON request DTO for create, update, patch, command or search bodies.

Allowed public controller outputs:

- response DTOs,
- `PagedResponseDTO<T>` for paged collection responses,
- bounded option/reference DTO collections for selector endpoints,
- `ResponseEntity<Void>` or equivalent for successful bodyless operations such as delete,
- the canonical Springmaster API error response for failures as defined in `API_ERROR_CONTRACT_STANDARD.md`.

Not canonical for new Springmaster reference APIs:

- JPA entities as `@RequestBody`, response body or response list element,
- domain aggregates as public HTTP body types,
- repositories or persistence projections exposed directly as API models,
- `Pageable` as controller method parameter,
- `Page<DTO>` or `Slice<DTO>` as public API response body,
- untyped `Map<String, Object>` as request, response or error contract,
- framework-generated request/response shapes that cannot be verified in OpenAPI.

## DTO role taxonomy

Springmaster uses explicit DTO roles. Java class names may continue to use the established `DTO` suffix because the current Core and real-app code already use that vocabulary. The role must still be clear from the class name.

| Role | Naming convention | Direction | Purpose |
|---|---|---|---|
| Create request | `<Resource>CreateDTO` | inbound | full create command payload |
| Update request | `<Resource>UpdateDTO` | inbound | full replacement/update command payload |
| Patch request | `<Resource>PatchDTO` | inbound | partial update payload only when PATCH semantics are explicitly supported |
| Domain command | `<Resource><CommandName>CommandDTO` | inbound | non-CRUD command, state transition, assignment or bulk command |
| Search request | `<Resource>SearchDTO` | inbound | complex search body for `POST .../search` |
| Query DTO | `<Resource>QueryDTO` | inbound query | grouped query/filter parameters when explicit controller params become unwieldy |
| Detail response | `<Resource>DTO` or `<Resource>DetailDTO` | outbound | canonical detail representation |
| List item response | `<Resource>ListItemDTO` | outbound | paged-list row when it differs from detail |
| Option response | `<Resource>OptionDTO` | outbound | bounded selector/reference option |
| Generic page | `PagedResponseDTO<T>` | outbound | stable paged response envelope |

`Request` or `Response` suffixes are allowed only when an ADR or project convention intentionally chooses that vocabulary. For Springmaster's current foundation, `DTO` remains the canonical Java suffix and the role is encoded in the name segment before `DTO`.

## Create DTO rules

Create DTOs represent client-provided values required to create a new resource.

Create DTOs must not include server-managed fields by default:

- external id when the server generates it,
- internal id,
- audit timestamps,
- creator/updater fields,
- persistence version,
- metadata managed by a separate metadata endpoint,
- calculated display fields,
- permission/capability flags.

A create DTO may include a business key, code or number only when clients are allowed to provide that value. If the backend generates the value, the field belongs in the response DTO, not the create DTO.

Required create fields must be expressed with Bean Validation annotations and must be visible in OpenAPI as required schema properties.

## Update DTO rules

Update DTOs represent a documented update operation. The default Springmaster update shape is:

- external id in the path,
- mutable fields in the body,
- optional optimistic-lock or business-version field only when the endpoint contract explicitly requires it.

The body must not contain the path id by default. If a project intentionally duplicates the id in the body, the behavior for mismatch between path id and body id must be documented and tested.

Update DTO requiredness may differ from create DTO requiredness. If requiredness differs, create and update must use separate DTO classes.

`PATCH` is not the default update standard. Partial update is allowed only when a patch-specific DTO defines absent-versus-null semantics. A nullable field in a patch DTO must not accidentally mean both “leave unchanged” and “clear value”.

## Command DTO rules

Non-CRUD commands use dedicated command DTOs. A command DTO must express exactly the inputs required for the command and must not reuse broad update DTOs when the command has narrower semantics.

Examples:

- `CatalogItemArchiveCommandDTO`,
- `CatalogItemRestoreCommandDTO`,
- `CatalogItemDeleteMultipleCommandDTO`,
- `UserAssignRoleCommandDTO`,
- `OrganisationUnitMoveCommandDTO`.

Command DTOs must use Bean Validation for boundary constraints and must map domain conflicts to the standard error contract. Business-state rules belong in the domain or command service, not only in DTO annotations.

Delete-multiple follows the endpoint standard from `API_ENDPOINT_CONTRACT_STANDARD.md` and uses a command DTO under `POST .../commands/delete-multiple`. It must not use `DELETE` with a request body.

## Query and search DTO rules

Simple list/filter endpoints should prefer explicit controller query parameters because they produce clear OpenAPI contracts.

A query DTO is allowed when an endpoint has many optional filters or repeated related criteria. When a query DTO is used, it must still satisfy these rules:

- field names are public API names, not Java repository terms,
- validation constraints are applied to `page`, `size`, `sortBy`, `sortDir` and filters,
- unsupported `sortBy` fields fail with `400` and the standard error response,
- controller signatures must not expose `Pageable`,
- generated OpenAPI must show the public query parameters or schema clearly enough for client generation and UI review.

Complex search uses `POST .../search` with a dedicated search DTO when the search cannot be represented safely as bounded query parameters.

## Response DTO rules

Response DTOs represent server-owned state. They may contain server-generated fields that must never be accepted as create/update input.

A detail response DTO may include:

- opaque external id,
- business display fields,
- metadata intended for clients,
- audit fields when they are part of the public contract,
- version information when clients need it for optimistic locking,
- capability flags or links only when standardized for the endpoint.

A list-item DTO should be introduced when table/list representations need fewer or different fields than detail responses. This avoids turning every detail field into a list contract and keeps list endpoints stable for UI tables.

Paged collection responses must use `PagedResponseDTO<T>` or a later Springmaster-approved equivalent. New reference APIs must not expose `Page<DTO>` as the public response body.

## Validation activation

Every JSON request body that is validated at the boundary must activate validation in the controller method, typically by combining `@Valid` with `@RequestBody`.

Nested inbound DTOs must be annotated so recursive validation runs where nested fields are part of the contract.

For query parameters, validation must be activated through controller-level validation, explicit parameter constraints or a validated query DTO. Invalid query parameters must fail with `400` and the standard error response.

Required strings use a blank-rejecting constraint when blank text is not a valid business value. Required object, numeric, boolean, enum and date/time fields reject `null`. Required collections must define whether empty collections are allowed.

Validation groups are not the Springmaster default. They may be used only when they make the API contract clearer than separate DTO classes. Separate DTO classes remain preferred for create/update/command role separation.

## Boundary validation versus domain validation

Boundary validation checks whether the external request has a valid shape. It maps to `400` by default.

Domain validation checks business invariants after the request has been mapped into the application/domain model. It maps to `409` for conflicts or business-rule violations by default, unless a specific standard or ADR defines a different mapping.

DTO validation must not become the only place where domain invariants are enforced. Examples that usually belong outside DTO annotations include duplicate business keys, state transitions, permission-dependent rules, cross-aggregate checks and persistence concurrency conflicts.

## Mapping boundary

Controllers should not contain non-trivial mapping logic. Mapping from inbound DTOs to command/domain models and from domain/read models to response DTOs belongs in mappers, assemblers or application services.

Simple entity-to-DTO mappings may use MapStruct or hand-written mappers. MapStruct is preferred when it can be used with strict unmapped-target checking and without hiding domain decisions. Manual mapping is allowed for complex read models, projections and security/capability shaping.

Mappers must not perform repository lookups, authorization checks or command execution. Those decisions belong in services or handlers.

## OpenAPI contract

Generated OpenAPI is part of the DTO boundary.

Future OpenAPI gates should verify that:

- inbound DTO schemas show required properties for boundary-required fields,
- server-managed fields are not required inbound properties,
- response schemas use DTO names and do not expose entity names as public schema names,
- paged list responses use the Springmaster page envelope,
- invalid request bodies and invalid query parameters document `400` with the standard error schema,
- create/update/command operations document their request body schemas explicitly,
- single delete operations have no request body.

## Catalog-demo readiness rule

Catalog-demo must not become the canonical DTO/validation reference while its controllers expose ad-hoc DTO boundaries, local error maps or unvalidated create/update bodies as final behavior.

Before `CatalogItem` is accepted as the first canonical reference slice, it must demonstrate or explicitly defer under a named patch:

- create request DTO with Bean Validation and `@Valid @RequestBody`,
- update request DTO when update is introduced,
- response DTO separate from inbound DTOs,
- paged response DTO for collection lists,
- explicit query parameters or a validated query DTO,
- no entity exposure in controller request/response signatures,
- standard error response for validation failures,
- tests for at least one missing required field and one blank required string where applicable.

The existing internal CatalogItem seed is not a complete DTO/validation reference until these rules are implemented or explicitly deferred.

## Future gates

This standard should become enforceable through:

1. Reflection or ArchUnit checks that scan controller signatures and reject entity types, `Pageable`, `Page<DTO>` and untyped maps at the public boundary.
2. MockMvc tests that assert validation failures for missing, blank and malformed fields.
3. OpenAPI contract tests for required fields, request body schemas, response schemas and bodyless deletes.
4. Reusable Springmaster assertions for `PagedResponseDTO`, validation violations and error response shape.
5. Maven-bound quality gates once Catalog-demo demonstrates the patterns and the test helpers are stable.

Until these gates exist, this document is the authoritative DTO/validation boundary rule and Catalog-demo is the expected demonstrator.


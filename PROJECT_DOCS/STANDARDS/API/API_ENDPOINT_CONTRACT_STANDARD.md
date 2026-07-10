# API Endpoint Contract Standard

## Status

Accepted as generic Springmaster API endpoint standard with patch `000046_springmaster_api_endpoint_contract_standard`; query/reference-data vocabulary harmonized by patch `000058_springmaster_api_query_reference_data_consistency_standard`; complete result-set and `/all` export semantics amended by patch `000091_springmaster_list_query_export_all_contract`; optional count-only response semantics narrowed by patch `000098_springmaster_count_response_contract_candidate`.

## Purpose

This standard defines the canonical HTTP endpoint contracts that Springmaster reference implementations must use before Catalog-demo becomes the canonical demo application.

Patch `000045_springmaster_api_endpoint_contract_definition_backlog` documented the open endpoint questions. This document turns the core questions into a concrete baseline standard for new Springmaster APIs. Existing IDM, Personnel, Contacts, Orders or other target projects are not changed by this standard. They remain comparison inputs until Catalog-demo proves the standards and the gates are available.

## Design principles

Springmaster endpoint contracts are resource-oriented at the public API boundary and command-aware where state changes cannot be modeled as simple resource operations.

The public API must use domain and resource vocabulary. Java repository, stream or service helper names such as `findOne`, `findFirst`, `findLast`, `loadPage` or `findById` must not leak into public paths, operation IDs or UI-facing OpenAPI descriptions unless a project-specific ADR explicitly allows that vocabulary for a special integration API.

Endpoint contracts must be deterministic for generated OpenAPI, UI integration, tests and review gates. Ambiguous endpoint variants are not allowed to become accidental standards through Catalog-demo.

## Canonical resource path model

New Springmaster management APIs use the following canonical resource model:

| Concern | Canonical shape | Notes |
|---|---|---|
| Resource collection | `GET /api/<domain>/<resources>` | paged list for UI-capable tables |
| Complete result set | `GET /api/<domain>/<resources>/all` | unpaged complete result set for frontend export, backend batch and integration consumers |
| Count-only result | `GET /api/<domain>/<resources>/count` | optional count-only endpoint for badges, dashboards, preflights and batch decisions |
| Resource detail | `GET /api/<domain>/<resources>/{id}` | detail by opaque external string id |
| Create resource | `POST /api/<domain>/<resources>` | create a new canonical resource |
| Update resource | `PUT /api/<domain>/<resources>/{id}` | update/replace the resource identified by the path |
| Single delete | `DELETE /api/<domain>/<resources>/{id}` | bodyless delete by path identity |
| Bounded selection data | `GET /api/<domain>/<resources>/options` | small DTOs for selectors; not an unbounded table export |
| Unique alternate lookup | `GET /api/<domain>/<resources>/by-<key>/{value}` | only when the key is unique and documented |
| Current/latest semantic lookup | `GET /api/<domain>/<resources>/current` or `/latest` | only when the domain meaning is explicit and deterministic |
| Collection command | `POST /api/<domain>/<resources>/commands/<command>` | complex command with request DTO |
| Resource command | `POST` or `PUT /api/<domain>/<resources>/{id}/commands/<command>` | command verb depends on idempotency |
| Nested resource | `/api/<domain>/<parents>/{parentId}/<children>/{childId}` | parent and child identities must be explicit |

`/list` is not the canonical path for new Springmaster reference APIs. It may exist in existing applications or as a transitional compatibility path, but Catalog-demo must use the collection path for the canonical paged list.

`/all` is canonical only when it implements the Springmaster complete-result-set contract: same documented filters and sorting as the paged collection endpoint, no public `page`/`size` pagination, complete filtered and authorized result, and no silent truncation. Ambiguous, selector-like or undocumented `/all` endpoints remain non-canonical. A bounded selector endpoint uses `/options`; a richer bounded read-only reference-data endpoint may use `/reference-data` when an ADR defines the response shape.

## Paged list endpoint

A UI-capable management collection must provide a paged list endpoint when the collection can grow beyond a small bounded set.

Canonical endpoint:

`GET /api/<domain>/<resources>`

Canonical query parameters:

| Parameter | Required | Standard |
|---|---:|---|
| `page` | no | zero-based page index; default `0` |
| `size` | no | positive page size; must be capped; default is endpoint-specific |
| `sortBy` | no | external field name; must not expose database column names |
| `sortDir` | no | `asc` or `desc`; invalid values return `400` |
| endpoint filters | no | explicit documented filter names only |

List responses must use the Springmaster paging shape represented by `PagedResponseDTO<T>` or an equivalent DTO with the same external semantics: `items`, `page`, `size`, `totalElements` and `totalPages`.

Controllers must not expose raw Spring `Page<T>` or raw `Pageable` as the public OpenAPI contract for UI-ready management APIs. A controller may build an internal `Pageable`, but public query parameters must remain explicit and documented.

Invalid query values must return `400 Bad Request`. Unsupported `sortBy` fields, unsupported `sortDir` values, negative page values and page sizes above the configured maximum must not be silently ignored.


## Complete result-set endpoint

A management collection that is used for frontend export, backend batch processing or service-to-service integration must expose a complete-result-set access mode when consumers need the whole matching result without public API pagination.

Canonical endpoint for simple GET-queryable collections:

`GET /api/<domain>/<resources>/all`

Canonical query parameters:

| Parameter | Required | Standard |
|---|---:|---|
| `sortBy` | no | same public sort-field allowlist as the paged list |
| `sortDir` | no | same `asc`/`desc` semantics as the paged list |
| endpoint filters | no | same documented filter names and matching behavior as the paged list |

`page` and `size` are not part of the `/all` contract. The endpoint must not silently cap the result at the public maximum page size. Supplying `page` or `size` to `/all` should return `400 Bad Request` unless a project-specific ADR explicitly keeps those parameters as ignored compatibility vocabulary.

The endpoint returns all matching public list-item DTOs or a documented export DTO as a JSON array. Empty result sets return `200 OK` with `[]`.

The implementation may process data internally in chunks, streams, cursors or repository pages, but the public response must be complete. Operational failures must use the standard API error contract and must not be returned as partial success.

For complex search DTOs, the complete access mode is `POST /api/<domain>/<resources>/search/all` unless an ADR defines an asynchronous export/job resource.

## Count-only endpoint

A count-only endpoint is optional and must be introduced only when a consumer needs the number of matching objects without loading page data.

Canonical endpoint for simple GET-queryable collections:

`GET /api/<domain>/<resources>/count`

Canonical endpoint for complex search DTOs:

`POST /api/<domain>/<resources>/search/count`

The endpoint counts the same filtered and authorized result set as the paged list and `/all` endpoint. It accepts the same documented filters, but `page`, `size`, `sortBy` and `sortDir` are not part of the count semantics. New reference APIs should reject unsupported count query parameters with `400 Bad Request` unless an ADR documents ignored compatibility parameters.

The response shape follows `API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md`:

```json
{ "totalElements": 0 }
```

No matches return `200 OK` with `totalElements: 0`. Count endpoints must use the standard API error contract for invalid filters, unauthorized access and operational failures.

## Bounded options and reference-data endpoints

Springmaster separates management lists from bounded selector/reference endpoints.

Use `/options` when the endpoint returns a small bounded set for a UI selector, autocomplete seed, dropdown or simple relation picker. The response DTO should be intentionally small and must not be treated as a full table/list contract.

Use `/reference-data` only when the endpoint returns a stable read model that is broader than simple options and an ADR documents why the result set is bounded and cacheable.

Do not use `/options` or `/reference-data` as a hidden export endpoint. Complete management-result retrieval uses `/all` and must satisfy the complete-result-set contract.

## Detail by external id

Canonical endpoint:

`GET /api/<domain>/<resources>/{id}`

The `{id}` value is an opaque external string identifier. Consumers must not infer UUID semantics, database identity, numeric ordering or composite structure from the identifier.

Status behavior:

| Situation | Status |
|---|---:|
| known id | `200 OK` with response DTO |
| syntactically unacceptable path value | `400 Bad Request` when the API defines a syntax rule |
| syntactically acceptable but unknown id | `404 Not Found` |
| missing access rights | `403 Forbidden` |

Because external IDs are opaque strings, Springmaster should avoid unnecessary syntax validation. Domain-specific syntax checks belong only to alternate keys, not to generic external ids, unless an ADR defines the public id format.

## Unique alternate lookups

Alternate lookups are allowed only when the lookup key is unique by domain rule and persistence constraint or when duplicate handling is explicitly defined.

Canonical shape:

`GET /api/<domain>/<resources>/by-<key>/{value}`

Examples of acceptable semantics are `by-sku`, `by-number`, `by-code` or another domain-specific key. Generic public endpoints named `find`, `find-one`, `findBy`, `first` or `last` are not allowed for Springmaster management APIs.

Status behavior:

| Situation | Status |
|---|---:|
| exactly one match | `200 OK` |
| no match | `404 Not Found` |
| duplicate matches for a unique lookup | `409 Conflict` and a defect/gate finding |
| invalid key value | `400 Bad Request` |

When a lookup is not guaranteed to be unique, it must be modeled as a paged list filter or complex search, not as a detail-like endpoint.

## Current, latest, first and last retrieval

`current` and `latest` are allowed only when they are domain concepts with deterministic rules.

`first` and `last` are not allowed as generic public endpoint vocabulary. They are Java/repository vocabulary unless the domain explicitly names a concept that way and an ADR documents the ordering rule and tie-breaker.

Preferred patterns:

| Need | Public API pattern |
|---|---|
| current authenticated user's object | `GET /api/<domain>/<resources>/current` or a dedicated `/me` endpoint in an auth context |
| latest object by domain timestamp | `GET /api/<domain>/<resources>/latest` with documented ordering and tie-breaker |
| first result of a query | paged list with explicit filters, `sortBy`, `sortDir` and `size=1` |
| previous/next navigation | dedicated navigation endpoint only when the domain requires it |

Catalog-demo must not introduce `/first` or `/last` endpoints as generic reference patterns.

## Create endpoint

Canonical endpoint:

`POST /api/<domain>/<resources>`

Create requests must use a dedicated request DTO with Bean Validation for boundary-required fields. Server-managed fields such as external id, audit values and persistence version must not be required inbound fields.

Successful create behavior:

| Situation | Status | Body |
|---|---:|---|
| canonical resource created | `201 Created` | response DTO |
| canonical resource created and location is known | `201 Created` | response DTO plus `Location` header recommended |
| duplicate business key | `409 Conflict` | standard error body |
| invalid request | `400 Bad Request` | standard error body |

A create command that does not create a canonical resource must be documented as a command endpoint and may return `200 OK` or `204 No Content` according to the command contract.

## Update endpoint

Canonical endpoint:

`PUT /api/<domain>/<resources>/{id}`

The path id is authoritative. Request DTOs must not contain a conflicting id. If a request DTO includes an id for legacy or compatibility reasons, the controller must reject mismatches with `400 Bad Request`.

The default update result is `200 OK` with the updated response DTO. Since patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard`, this is also the mandatory first-slice Catalog-demo default. `204 No Content` is allowed only when the endpoint explicitly chooses no response body and clients do not need the updated representation; strict gates must treat it as an explicit exception, not as the first reference behavior.

Optimistic locking must be explicit. If a version/concurrency token is part of the API contract, the standard field name is `version` unless an existing project has a documented compatibility name. Version mismatch returns `409 Conflict`.

`PATCH` is not a default Springmaster reference pattern. Partial update endpoints require an ADR that defines null handling, omitted field handling, validation rules and OpenAPI schema behavior.

## Single delete endpoint

Canonical endpoint:

`DELETE /api/<domain>/<resources>/{id}`

Single deletes must not accept a request body. All information required to identify the target must be represented by the path or simple query parameters.

Status behavior:

| Situation | Status |
|---|---:|
| delete succeeds | `204 No Content` |
| unknown id | `404 Not Found` |
| invalid path or query parameter | `400 Bad Request` |
| conflict, active references or version mismatch | `409 Conflict` |
| unauthorized or forbidden | `401 Unauthorized` or `403 Forbidden` |

The default Springmaster contract is strict: a repeated delete after the resource is gone returns `404 Not Found`, not idempotent `204`, unless an endpoint-specific ADR chooses idempotent deletion for a concrete reason.

External `delete` means that the resource is no longer available through the normal detail/list API. Whether the persistence implementation performs hard delete, soft delete, archive, deactivate or anonymize is a domain decision and must be documented separately.

If a delete requires a complex command body, it is not a `DELETE` endpoint. It must be modeled as a command endpoint with `POST`.

## Delete-multiple endpoint

Bulk delete is a collection command, not a body-bearing `DELETE` workaround.

Canonical endpoint:

`POST /api/<domain>/<resources>/commands/delete-multiple`

The request DTO must contain opaque external string ids and must document whether duplicates are rejected or de-duplicated.

Recommended request shape:

| Field | Required | Meaning |
|---|---:|---|
| `ids` | yes | non-empty list of opaque external ids |
| `versionById` | no | optional concurrency token map when the domain requires it |
| `reason` | no | optional audit reason when required by domain policy |

Default behavior is atomic all-or-nothing for management APIs. If any item is invalid, not found, unauthorized or blocked by conflict, no item is deleted and the endpoint returns the appropriate error status.

Partial-success bulk delete is allowed only when the command result DTO explicitly reports item-level outcomes and the endpoint ADR explains why partial completion is acceptable.

Default status behavior:

| Situation | Status |
|---|---:|
| all requested resources deleted | `200 OK` with command result DTO |
| empty `ids` | `400 Bad Request` |
| any unknown id under atomic mode | `404 Not Found` |
| any conflict under atomic mode | `409 Conflict` |
| partial-success mode accepted | `200 OK` with item-level result DTO |

Catalog-demo does not need bulk delete in its first slice. If bulk delete is added later, it must use this command pattern.

## State-transition and resource command endpoints

A state transition is a command on an existing resource, for example activate, deactivate, archive, submit-for-review or approve.

Canonical endpoint pattern:

`PUT /api/<domain>/<resources>/{id}/commands/<command>` for idempotent transitions.

`POST /api/<domain>/<resources>/{id}/commands/<command>` for non-idempotent commands or commands that create a derived resource.

The command name must be domain vocabulary. It must not be a technical method name.

A state-transition command must document:

- whether it is idempotent,
- required request body or no-body behavior,
- success status and response body,
- invalid-state behavior,
- authorization behavior,
- audit/event expectations when applicable.

Legacy endpoint shapes such as `PUT /{id}/activate` are acceptable in existing projects, but Catalog-demo should use the `/commands/<command>` pattern when it introduces state transitions.

## Assignment and relationship endpoints

Relationship operations must make relationship identity explicit.

Canonical remove pattern for a specific relationship:

`DELETE /api/<domain>/<relation-context>/<parentResource>/{parentId}/<childResources>/{childId}`

The delete must be bodyless. Parent id and child id must be sufficient to identify the relationship. If the relationship has its own external id, the API may expose it as a relationship resource and delete that resource by id.

Adding a relationship normally uses `POST` to the relationship collection or a command endpoint with a dedicated request DTO. Bulk relationship changes must use `POST` commands and must not use body-bearing `DELETE`.

Patch `000053_springmaster_command_relationship_endpoint_standard` specializes these baseline rules for state transitions, relationship reads, add/remove assignments, bulk relationship commands, nested aggregate commands, command DTOs, permission mapping and future command gates. New Catalog-demo relationship or command endpoints must follow that specialized standard.

## Complex search endpoint

Simple search and filters belong on the paged collection list as explicit query parameters.

A complex search is allowed when the filter structure cannot be represented safely as simple query parameters.

Canonical endpoint:

`POST /api/<domain>/<resources>/search`

A search endpoint must be side-effect-free. It must use a dedicated search request DTO, support paging, return the standard paged response shape and be documented as query semantics despite using `POST` for payload complexity.

`POST /search` must not become a workaround for undocumented list filters. The search request DTO must be part of the OpenAPI contract and must have validation rules.

## Error and status-code matrix

Springmaster endpoint standards use the following baseline status matrix:

| Operation | Default success | Important client errors |
|---|---:|---|
| paged list | `200` | `400` invalid query, `403` forbidden |
| options/reference data | `200` | `400` invalid query, `403` forbidden |
| detail by id | `200` | `404` unknown id, `403` forbidden |
| alternate unique lookup | `200` | `400` invalid key, `404` no match, `409` duplicate |
| create | `201` | `400` invalid request, `409` duplicate/conflict |
| update | `200` with body | `400` invalid request/id mismatch, `404` unknown id, `409` version/conflict |
| single delete | `204` with no body | `400` invalid parameter, `404` unknown id, `409` conflict |
| delete-multiple | `200` with result DTO | `400` invalid request, `404` unknown id under atomic mode, `409` conflict |
| state command with meaningful result | `200` with result DTO or representation | `400`, `404`, `409` depending on command |
| state command with no useful result | `204` with no body | `400`, `404`, `409` depending on command |
| command that creates a resource | `201` | `400`, `404`, `409` depending on command |
| asynchronous command | `202` with status/job/operation DTO | `400`, `404`, `409` depending on command |
| complex search | `200` | `400` invalid search request |

The structured error body is standardized by `API_ERROR_CONTRACT_STANDARD.md` since patch `000048_springmaster_api_error_contract_standard`. Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` narrows the first-slice status defaults and clarifies `errorId`, `correlationId`, `traceId`, `messageKey`, `message` and `localMessage`. Catalog-demo must not introduce an incompatible local ad-hoc error format as the final reference pattern.

## OpenAPI and operationId contract

The generated OpenAPI contract must show the public endpoint contract, not internal implementation details.

Minimum operationId convention for new Springmaster APIs:

| Endpoint concern | OperationId pattern |
|---|---|
| paged list | `list<ResourcePlural>` |
| options | `list<ResourcePlural>Options` |
| complete result set | `listAll<ResourcePlural>` |
| detail | `get<ResourceSingular>ById` |
| alternate lookup | `get<ResourceSingular>By<Key>` |
| create | `create<ResourceSingular>` |
| update | `update<ResourceSingular>` |
| delete | `delete<ResourceSingular>` |
| delete-multiple | `deleteMultiple<ResourcePlural>` |
| state command | `<command><ResourceSingular>` |
| complex search | `search<ResourcePlural>` |

OpenAPI paths and operation IDs must not use `findOne`, `findFirst`, `findLast`, `loadPage`, repository method names, entity package names or persistence-only terminology.

## Catalog-demo readiness rule

Catalog-demo may implement `CatalogItem` only as a standard-conformant reference slice. Before the CatalogItem API is expanded, the implementation plan must verify these minimum endpoint decisions:

- paged list uses collection path and explicit query parameters,
- detail uses opaque external id in the path,
- create uses request DTO validation and returns canonical create status,
- update uses path identity and explicit version policy if needed,
- delete is bodyless and returns the standard status behavior,
- SKU or other business-key lookup is modeled as alternate lookup and not as resource identity unless decided explicitly,
- options/reference data is bounded and separated from management result-set retrieval, and any `/all` endpoint implements the complete-result-set contract,
- no public `findOne`, `findFirst` or `findLast` endpoint vocabulary is introduced,
- OpenAPI gates can later inspect the endpoint matrix,
- failure responses follow the standard API error contract.

## Future gates

This standard should become enforceable through:

1. OpenAPI path and operationId inspection.
2. OpenAPI delete-body absence checks.
3. OpenAPI query parameter and response schema checks for list endpoints.
4. MockMvc contract tests for the status-code matrix.
5. Reflection or ArchUnit checks that controllers do not expose persistence entities or raw `Pageable` as public contracts.
6. Review gates that compare Catalog-demo and later target-project APIs against this standard.

Until these gates exist, this document is the authoritative endpoint rule for new Springmaster reference implementation work.

## Non-goals

This standard does not change IDM, Personnel, Contacts, Orders or any other existing project.

This standard does not introduce Java interfaces, Maven plugins, ArchUnit rules or OpenAPI test utilities. Those belong to later implementation patches.

This standard does not require Catalog-demo to implement every operation immediately. It defines the contract that Catalog-demo must follow when each operation is introduced.

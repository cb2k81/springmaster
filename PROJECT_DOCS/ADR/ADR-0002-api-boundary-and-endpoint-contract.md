# ADR-0002: API Boundary and Endpoint Contract

## Status

Accepted

## Date

2026-06-30

## Context

Springmaster is the master/reference project for reusable backend foundation, tooling, standards, conventions, reference implementations and verifiable quality gates.

Patches `000044` through `000059` established documentation-first API standards for request validation, required fields, list/filter/query behavior, command HTTP semantics, external IDs, endpoint contracts, error responses, DTO boundaries, command/relationship endpoints, query/reference-data consistency and error/status-code consistency.

The real-app forensics from IDM and Personnel showed useful but different patterns:

- IDM contributes strong OpenAPI contract-test patterns, explicit query parameters, bodyless delete behavior and API-readiness discipline.
- Personnel contributes richer aggregate, command, lifecycle, capability and reference-data patterns.
- Existing apps remain comparison inputs only. They are not automatically remediated or supplied by Springmaster in this workstream.

Before Catalog-demo becomes canonical and before API contract gates become strict, the API boundary rules must be recorded as an accepted architecture decision rather than only as standards.

## Decision

Springmaster accepts the API boundary and endpoint contract defined by the affected standards listed below as the canonical baseline for new Springmaster reference APIs and future generated project templates.

The accepted decision is:

1. **Public API boundary**
   - HTTP controllers expose DTOs and API envelopes only.
   - JPA entities, domain aggregates, repositories, `EntityManager`, Spring Data `Pageable`, Spring Data `Page<DTO>` and internal Java repository vocabulary must not become public API contracts for new reference APIs.
   - Controllers are HTTP adapters. Business rules, persistence access, authorization decisions and transaction ownership are outside the controller boundary.

2. **Endpoint vocabulary**
   - Paged resource collection: `GET /api/<domain>/<resources>`.
   - Detail by opaque public ID: `GET /api/<domain>/<resources>/{id}`.
   - Alternative unique lookup: `GET /api/<domain>/<resources>/by-<key>/{value}` when the key is a stable business lookup and documented.
   - Create: `POST /api/<domain>/<resources>`.
   - Full update: `PUT /api/<domain>/<resources>/{id}`.
   - Bodyless single delete: `DELETE /api/<domain>/<resources>/{id}`.
   - Complex search: `POST /api/<domain>/<resources>/search` when query complexity no longer fits a stable GET query contract.
   - Bounded selector data: `GET /api/<domain>/<resources>/options`.
   - State, collection, nested aggregate and relationship operations use explicit command or relationship endpoint patterns from the command/relationship standard.

3. **Non-canonical API vocabulary**
   - Public `findOne`, `findFirst`, `findLast` and similar Java/repository terms are not canonical for Springmaster management APIs.
   - `/list` is not the canonical Springmaster collection endpoint for new reference APIs.
   - `/all` is not canonical for new Springmaster reference APIs and must not be introduced by Catalog-demo first slices.
   - `/reference-data` is allowed only with ADR-backed semantics or a later accepted standard that defines scope, caching, bounds, ownership and compatibility behavior.

4. **Query contract**
   - Canonical list query parameters for new reference APIs are `page`, `size`, `sortBy`, `sortDir` plus documented resource-specific filters.
   - `sort` is legacy/target-comparison vocabulary and must not be introduced by new Springmaster reference APIs.
   - Sort fields are API field names, not database column names or internal Java implementation details.

5. **DTO and validation boundary**
   - Inbound JSON request bodies that require validation must use `@Valid @RequestBody` or an equivalent validated boundary mechanism.
   - Create, update, patch, command, search/query, response, list-item, option and command-result DTO roles must be explicit in type names and API schemas.
   - Bean Validation expresses boundary-level required fields and simple constraints. Domain invariants remain in domain/application services.
   - Required fields must be visible in OpenAPI for validated request DTOs.

6. **Error contract**
   - Public API errors use the Springmaster error response contract.
   - `errorId` is required and identifies the concrete error occurrence.
   - `correlationId`, `traceId`, `messageKey` and `localMessage` are optional fields with the semantics defined in the error identity/status-code standard.
   - Validation errors use `violations` with stable field/parameter information.
   - Ad-hoc `Map<String,Object>` error bodies are not canonical reference behavior.

7. **Status-code defaults**
   - Create returns `201 Created`.
   - Full update returns `200 OK` with the updated DTO for the first canonical Catalog-demo slice.
   - Bodyless single delete returns `204 No Content`; deleting a non-existing resource returns `404 Not Found`.
   - Delete-multiple returns `200 OK` with a result DTO.
   - Commands return `200 OK` with a result DTO when a meaningful result exists, `204 No Content` only when no body is useful, and `201 Created` when the command creates a new addressable resource.
   - `202 Accepted` is allowed only when a status, job or operation resource exists.

8. **External IDs**
   - Public IDs are opaque string identifiers.
   - API clients must not derive persistence implementation details from ID format.
   - Business keys such as SKU, code or number are explicit domain fields and may be exposed through documented `by-<key>` lookups when appropriate.

## Scope

This ADR applies to:

- new Springmaster API standards and Catalog-demo reference APIs;
- generated project templates once templates begin producing management APIs;
- report-only and later strict API contract gates;
- future target-project comparison reports.

This ADR does not authorize automatic changes to IDM, Personnel, Contacts, Orders or other existing projects. Existing projects remain comparison inputs until Catalog-demo and the update workflow explicitly prove a safe delivery path.

## Affected standards

This ADR accepts and consolidates the architectural decisions from:

- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_HTTP_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/LIST_FILTER_QUERY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/REQUIRED_FIELDS_OPENAPI_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_REQUEST_VALIDATION_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/EXTERNAL_ID_OPENAPI_BOUNDARY_STANDARD.md`

This ADR narrows these standards where terminology differed: `sortBy` is canonical, `/all` is non-canonical for new reference APIs, and the first Catalog-demo update/delete/command status defaults are fixed as described above.

## Considered alternatives

### Keep IDM-style and Personnel-style endpoints side by side

Rejected for new Springmaster reference APIs. The real apps remain valuable comparison inputs, but Springmaster needs one canonical baseline for Catalog-demo and gate tooling.

### Use Spring Data `Pageable` and `Page<DTO>` directly in controllers

Rejected for public API boundaries. It leaks Spring Data implementation details into OpenAPI, can generate unstable parameter names and makes UI contracts less explicit. Spring Data can remain internal behind query services and mappers.

### Use `/list` and `/all` as canonical endpoint suffixes

Rejected for new reference APIs. A collection resource already represents the list. `/all` is ambiguous and can encourage unbounded APIs. Bounded selector use cases use `/options`; broader reference-data APIs require ADR-backed semantics.

### Allow `DELETE` with request body for single delete or bulk delete

Rejected. Body-bearing `DELETE` is not canonical. Structured input uses command endpoints with dedicated DTOs, usually `POST .../commands/delete-multiple` for bulk deletion.

### Expose Java method vocabulary such as `findOne` and `findFirst`

Rejected for public management APIs. Such terms belong to repository/service implementation language unless translated into precise domain semantics such as `current`, `latest`, `primary` or a documented `by-<key>` lookup.

### Use RFC 7807 `ProblemDetail` directly as the public contract

Deferred as an implementation option, not accepted as the public Springmaster contract. Springmaster keeps an explicit error body because the real apps require `errorId`, optional local messages and later correlation/audit semantics. A future implementation may adapt Spring `ProblemDetail` internally if it preserves the accepted public contract.

## Consequences

Positive consequences:

- Catalog-demo has a deterministic API contract target before its first canonical slice.
- API contract gates can check concrete endpoint, DTO, validation, error, query and status-code behavior.
- OpenAPI generated from Springmaster reference APIs should remain stable enough for UI and downstream API consumers.
- Existing real-app differences can be reported as comparison findings without becoming new Springmaster defaults.

Negative consequences and costs:

- Some existing app patterns will be classified as legacy, target-specific or comparison-only even when they are currently functional.
- Catalog-demo must replace or clearly mark older seed code before it can become canonical.
- Templates and future target-update tools must respect the stricter API vocabulary.
- More tests and gates are required before strict enforcement is safe.

## Gate implications

This ADR enables API-boundary rules to move from `needs-adr` to `ready-for-tooling` for report-only and later strict gates, subject to `ADR-0006 Verification and Gate Strategy`.

Gate candidates enabled by this ADR include:

- OpenAPI checks for canonical paths and methods;
- OpenAPI checks for absence of request bodies on single `DELETE` operations;
- OpenAPI checks for `page`, `size`, `sortBy`, `sortDir` and absence of canonical `/all` in new reference APIs;
- OpenAPI checks for DTO schemas and required fields;
- OpenAPI checks for standard error schema and status-code mappings;
- MockMvc checks for validation, not-found, conflict, delete and command behavior;
- reflection/classpath checks for no entity, no `Pageable` and no `Page<DTO>` at controller boundaries.

Strict enforcement still requires:

- `ADR-0006` for gate severity, report structure, Maven binding and fail/report-only behavior;
- a dedicated OpenAPI naming/schema standard or a later ADR/standard addendum for operationId, tag and schema naming strictness;
- Catalog-demo evidence before target-project comparison becomes binding.

## Exceptions and deferrals

Allowed exceptions and deferred topics:

- Existing IDM, Personnel, Contacts, Orders or other target projects may keep legacy API shapes until a later comparison/remediation workstream explicitly addresses them.
- `/reference-data` is deferred to ADR-backed semantics unless a later accepted standard defines it generally.
- Multi-sort, export endpoints, streaming endpoints, batch/async workflows beyond explicit `202 Accepted` status resources and broad reference-data caching are deferred.
- Security schemes, permission catalog and capability exposure are owned by ADR-0005 and related security standards.
- OperationId, tag, schema naming and security scheme naming remain a separate OpenAPI naming/schema gap.
- Persistence identity and internal surrogate-ID exceptions are owned by ADR-0004.

## Supersession

This ADR does not supersede earlier ADRs.

It promotes documentation-first API standards from patches `000044` through `000059` into an accepted architecture decision for new Springmaster reference APIs and future gate tooling.

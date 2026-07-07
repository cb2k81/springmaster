# API Error Identity and Statuscode Consistency Standard

## Status

Accepted as Springmaster API error identity and status-code consistency standard with patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard`.

## Purpose

Patch `000057_springmaster_standard_consistency_and_adr_gap_review` identified two P0 consistency gaps before API contract gate tooling can be implemented:

- `errorId`, `correlationId`, `traceId`, `messageKey`, `message` and `localMessage` were not separated precisely enough;
- update, delete, delete-multiple and command success statuses were too broad for the first Catalog-demo gates.

This standard resolves those gaps at Springmaster standard level. It does not introduce Java code, OpenAPI helpers, MockMvc tests, Maven profiles, Catalog-demo implementation or target-project changes.

## Scope

This standard applies to new Springmaster reference APIs and the future Catalog-demo canonical slice. Existing IDM, Personnel, Contacts, Orders and other target projects remain comparison inputs until Catalog-demo and the gate tooling prove the standard.

## Error identity vocabulary

Springmaster distinguishes these concepts. They must not be collapsed into one ambiguous field.

| Concept | Public body field | Required | Meaning |
|---|---|---:|---|
| Error occurrence id | `errorId` | yes | unique opaque id for this concrete error response; returned to clients and written to server logs |
| Request correlation id | `correlationId` | no | request/distributed correlation value when available from inbound headers, MDC or tracing infrastructure |
| Technical trace id | `traceId` | no | implementation- or tracing-system id; public exposure is optional and must not leak sensitive internals |
| Stable message key | `messageKey` | no | stable localization/UI key such as `catalog.item.validation.name.required` |
| Default message | `message` | yes | safe fallback message, stable enough for humans but not intended as machine contract |
| Localized message | `localMessage` | no | already localized or UI-facing message when localization is active |

### `errorId`

`errorId` is the canonical support handle for a single error occurrence. It is required in every Springmaster error body.

Rules:

- generate a new opaque value for each error response unless the request already carries a platform-approved error id;
- log the same `errorId` with the exception or handling event;
- do not encode user ids, tenant ids, stack frames, SQL state, table names or security-sensitive information;
- do not reuse `errorId` as permission id, resource id, request id or business key.

### `correlationId`

`correlationId` groups related work across a request or distributed call chain. It is optional in the public error body for now.

Rules:

- preserve an incoming approved correlation id when present;
- generate or attach one when the runtime infrastructure provides it;
- log it together with `errorId`;
- do not make Catalog-demo canonicality depend on distributed tracing infrastructure in the first slice.

### `traceId`

`traceId` is reserved for tracing frameworks and infrastructure. It is optional in the public body and may be omitted from Catalog-demo until observability standards are implemented.

Public `traceId` exposure requires that the value is opaque and safe for clients. If this cannot be guaranteed, keep it in logs only.

## Message fields

Springmaster separates machine-readable error classification from human-facing text.

| Field | Contract role |
|---|---|
| `errorType` | machine-readable API error category from the standard vocabulary |
| `messageKey` | optional stable UI/localization key |
| `message` | required safe default message |
| `localMessage` | optional localized or user-facing message |
| `violations[].code` | Bean Validation annotation, enum value or Springmaster validation code |
| `violations[].messageKey` | optional stable localization key for a violation |
| `violations[].message` | required safe violation message |

`message` and `localMessage` must not become machine contracts. Clients should use `errorType`, `messageKey`, `violations[].field` and `violations[].code` for deterministic behavior.

`messageKey` is optional because Springmaster has not yet introduced a full i18n/message-catalog standard. Once a backend exposes message keys, keys must remain stable across compatible versions.

## Canonical error body addendum

The canonical error body from `API_ERROR_CONTRACT_STANDARD.md` remains valid. This standard adds the following optional fields:

- `correlationId`;
- `traceId`;
- `messageKey`;
- `violations[].messageKey`.

The first Catalog-demo canonical slice must still include all required fields from `API_ERROR_CONTRACT_STANDARD.md` and must at least make `errorId` observable in the response and logs or documented test output.

## Baseline status-code defaults

Springmaster keeps the endpoint and command standards flexible for future projects, but the first Catalog-demo reference gates need deterministic defaults.

New Springmaster reference APIs use these defaults unless an accepted ADR documents a different contract.

| Operation | Default success status | Body expectation |
|---|---:|---|
| paged list | `200 OK` | `PagedResponseDTO<T>` |
| bounded options | `200 OK` | list or bounded option response DTO |
| detail by id | `200 OK` | detail response DTO |
| alternate unique lookup | `200 OK` | detail response DTO |
| create resource | `201 Created` | response DTO; `Location` header recommended when location is known |
| full update | `200 OK` | updated response DTO |
| single bodyless delete | `204 No Content` | no response body |
| delete multiple | `200 OK` | command result DTO |
| state command with meaningful result | `200 OK` | command result DTO or updated representation |
| state command with no useful result | `204 No Content` | no response body |
| command that creates a resource | `201 Created` | created resource or command result DTO; `Location` recommended when location is known |
| asynchronous command | `202 Accepted` | accepted/job/operation DTO with a deterministic status resource |
| complex search | `200 OK` | paged response DTO |

`204 No Content` for full update is not the first-slice Catalog-demo default. It is allowed only when an endpoint intentionally does not return the updated representation and the contract is documented.

`204 No Content` for delete-multiple is not the first Springmaster bulk default. Delete-multiple should return `200 OK` with a result DTO because bulk operations usually need deterministic client feedback.

`202 Accepted` is allowed only when the API exposes a deterministic follow-up status, job or operation resource. An endpoint must not return `202` merely to avoid deciding synchronous command behavior.

## Client-error defaults

Client error status codes remain aligned with the API error contract.

| Situation | Default status | Default `errorType` |
|---|---:|---|
| malformed JSON or unreadable body | `400` | `INVALID_REQUEST` |
| Bean Validation failure | `400` | `VALIDATION_FAILED` |
| invalid query/path parameter | `400` | `INVALID_REQUEST` |
| unsupported query parameter | `400` | `UNSUPPORTED_QUERY_PARAMETER` |
| unknown resource id or lookup key | `404` | `RESOURCE_NOT_FOUND` |
| repeated strict delete after resource is gone | `404` | `RESOURCE_NOT_FOUND` |
| duplicate business key | `409` | `CONFLICT` |
| optimistic-lock/version conflict | `409` | `CONFLICT` |
| invalid state transition | `409` | `BUSINESS_RULE_VIOLATION` |
| missing or invalid authentication | `401` | `UNAUTHORIZED` |
| missing permission | `403` | `FORBIDDEN` |
| unexpected technical failure | `500` | `INTERNAL_ERROR` |

`422 Unprocessable Entity` remains non-canonical for Springmaster reference APIs unless an ADR accepts it for a specific integration contract.

## Command-result defaults

Command result DTOs are required when a command has meaningful client-visible outcome, especially for:

- delete-multiple;
- partial-success modes;
- dry-run or preview commands;
- asynchronous commands;
- commands that create derived resources;
- commands that produce warnings, skipped items or item-level statuses.

A command result DTO should include only client-relevant state. It must not expose persistence exceptions, stack traces, SQL details or internal entity graphs.

## Catalog-demo readiness

The first canonical CatalogItem slice uses these deterministic defaults:

- create returns `201 Created` with response DTO and `Location` when practical;
- full update returns `200 OK` with updated response DTO;
- bodyless single delete returns `204 No Content` when successful and `404` when the resource is already absent;
- validation failures return `400` with required error fields and `violations`;
- duplicate `sku` or equivalent business key returns `409`;
- `errorId` is present in every error response;
- `messageKey`, `correlationId` and `traceId` may be deferred, but their absence must be explicit in the readiness summary.

## Gate implications

The first API contract gate tooling seed may now treat these rules as ready for implementation:

- required error body fields include `errorId`;
- optional error body fields are `correlationId`, `traceId`, `messageKey` and `localMessage`;
- validation violations may include `messageKey`;
- full update default is `200` with body for Catalog-demo;
- bodyless single delete default is `204` success and `404` after removal;
- delete-multiple default is `200` with result DTO when introduced;
- command `202` is valid only with status/job/operation contract.

## Non-goals

This standard does not implement the error DTOs, exception hierarchy, MDC handling, correlation-id filter, OpenAPI assertions, MockMvc helpers, ArchUnit checks, Catalog-demo controller behavior or target-project migrations.

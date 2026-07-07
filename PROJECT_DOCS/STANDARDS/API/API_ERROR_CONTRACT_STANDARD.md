# API Error Contract Standard

## Status

Accepted as generic Springmaster API error contract standard with patch `000048_springmaster_api_error_contract_standard`.

## Purpose

Springmaster APIs must expose deterministic, inspectable and supportable error responses. Error contracts are part of the public API boundary and must not be left to framework defaults or ad-hoc controller-local maps.

This standard defines the canonical error response shape, status mapping and future gate targets for Springmaster reference APIs. It is derived from the real-app comparison of IDM and Personnel, but it is not an instruction to change existing target projects. IDM, Personnel, Contacts, Orders and other existing projects remain comparison inputs until Catalog-demo demonstrates the standard and quality gates are available.

## Design principles

API errors must be stable for clients, useful for operations and safe for external consumers.

Springmaster keeps an explicit error envelope instead of blindly adopting a framework-native response shape as the public contract. Spring Framework `ProblemDetail` may be used internally as an implementation carrier or adapter, but Catalog-demo must expose the Springmaster error contract unless an ADR explicitly changes the public contract.

The public error contract must:

- use a stable machine-readable `errorType`,
- expose the HTTP `status`,
- provide a human-readable `message`,
- preserve operational traceability through `errorId`,
- include field-level diagnostics for request validation where available,
- avoid stack traces, persistence exceptions, class names and SQL details,
- remain deterministic in generated OpenAPI.

## Canonical error response

New Springmaster reference APIs use the following canonical error response body.

| Field | Required | Type | Meaning |
|---|---:|---|---|
| `timestamp` | yes | string | ISO-8601 timestamp when the error response was created |
| `status` | yes | number | HTTP status code |
| `error` | yes | string | HTTP reason phrase or stable status label |
| `errorType` | yes | string | machine-readable Springmaster error type |
| `message` | yes | string | safe human-readable default message |
| `messageKey` | no | string | stable localization/UI message key when available |
| `localMessage` | no | string | localized or user-facing message when available |
| `errorId` | yes | string | opaque unique identifier for this error occurrence |
| `correlationId` | no | string | request or distributed correlation id when available |
| `traceId` | no | string | technical trace id when safe and intentionally exposed |
| `path` | yes | string | request path that produced the error |
| `method` | yes | string | HTTP method that produced the error |
| `violations` | no | array | field, parameter or object validation diagnostics |

Example shape:

```json
{
  "timestamp": "2026-06-29T12:00:00Z",
  "status": 400,
  "error": "Bad Request",
  "errorType": "VALIDATION_FAILED",
  "message": "Request validation failed.",
  "messageKey": "springmaster.validation.failed",
  "localMessage": "Die Anfrage ist unvollständig oder ungültig.",
  "errorId": "err-opaque-id",
  "correlationId": "corr-opaque-id",
  "path": "/api/catalog/items",
  "method": "POST",
  "violations": [
    {
      "field": "name",
      "message": "must not be blank",
      "code": "NotBlank"
    }
  ]
}
```

`errorId` is not a security token and must not encode sensitive data. It is an opaque support identifier for this concrete error occurrence and must be correlated with server-side logs.

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` clarifies that `errorId`, `correlationId`, `traceId`, `messageKey`, `message` and `localMessage` are distinct concepts. `errorId` is required. `correlationId`, `traceId`, `messageKey` and `localMessage` are optional public fields unless a later observability or i18n standard makes them mandatory.

`message` is the safe default human-readable fallback. `messageKey` is the optional stable UI/localization key. `localMessage` is optional because not every backend slice needs localization at the beginning. Once a project exposes localized errors or message keys, field names and fallback behavior must remain stable.

## Violation item contract

Validation diagnostics use `violations` when a request body, query parameter, path variable or cross-field rule can be mapped to a specific contract element.

| Field | Required | Meaning |
|---|---:|---|
| `field` | no | request body field, query parameter or path variable name |
| `object` | no | request object name or command name when a field is not enough |
| `message` | yes | safe validation message |
| `code` | no | Bean Validation annotation, enum value or Springmaster validation code |
| `messageKey` | no | stable localization/UI message key for the violation |
| `rejectedValue` | no | sanitized rejected value only when safe to expose |

The response must not expose secrets, passwords, tokens, credential values or full object dumps as `rejectedValue`.

For invalid query parameters, `field` uses the public parameter name, for example `page`, `size`, `sortBy` or `sortDir`. The legacy name `sort` is not canonical for new Springmaster reference APIs.

## Standard error types

Springmaster reserves the following baseline `errorType` values for reference APIs.

| Error type | Default status | Meaning |
|---|---:|---|
| `VALIDATION_FAILED` | `400` | Bean Validation or request body validation failed |
| `INVALID_REQUEST` | `400` | malformed JSON, unreadable body, type mismatch or invalid path/query value |
| `UNSUPPORTED_QUERY_PARAMETER` | `400` | query parameter exists but is not supported by the endpoint contract |
| `RESOURCE_NOT_FOUND` | `404` | syntactically acceptable id or lookup key has no target resource |
| `CONFLICT` | `409` | duplicate business key, optimistic-lock conflict or invalid state transition |
| `UNAUTHORIZED` | `401` | authentication is missing or invalid |
| `FORBIDDEN` | `403` | authenticated principal lacks required permission |
| `BUSINESS_RULE_VIOLATION` | `409` by default | valid request violates a domain invariant or state rule |
| `INTERNAL_ERROR` | `500` | unexpected server-side failure |

Projects may define additional domain-specific error types only when an ADR documents the vocabulary and status mapping. Domain-specific values must not replace the baseline values for generic framework and boundary failures.

## Status-code mapping

New Springmaster reference APIs use the following mapping as default.

| Situation | Status | Default `errorType` |
|---|---:|---|
| JSON cannot be parsed | `400` | `INVALID_REQUEST` |
| request body violates Bean Validation | `400` | `VALIDATION_FAILED` |
| query parameter has invalid type or unsupported value | `400` | `INVALID_REQUEST` |
| unsupported query parameter | `400` | `UNSUPPORTED_QUERY_PARAMETER` |
| unsupported `sortBy` field or unsupported `sortDir` | `400` | `INVALID_REQUEST` |
| required path/query parameter missing | `400` | `INVALID_REQUEST` |
| opaque external id is syntactically accepted but unknown | `404` | `RESOURCE_NOT_FOUND` |
| alternate unique lookup has no match | `404` | `RESOURCE_NOT_FOUND` |
| alternate unique lookup returns duplicates | `409` | `CONFLICT` |
| duplicate business key on create or update | `409` | `CONFLICT` |
| optimistic-lock or version mismatch | `409` | `CONFLICT` |
| state transition not allowed in current state | `409` | `BUSINESS_RULE_VIOLATION` |
| authentication missing or invalid | `401` | `UNAUTHORIZED` |
| permission missing | `403` | `FORBIDDEN` |
| unexpected server failure | `500` | `INTERNAL_ERROR` |

`422 Unprocessable Entity` is not the Springmaster default. If a project wants to distinguish syntactically valid but semantically invalid commands with `422`, it needs an ADR and must explain how the distinction remains testable and useful for clients. The default Springmaster standard uses `400` for boundary validation and `409` for conflicting domain state.


## Error identity and status-code consistency since 000059

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` adds `API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md` as the canonical clarification for operational error identity and first-slice status-code defaults.

Key clarifications:

- `errorId` is required and identifies one concrete error occurrence;
- `correlationId` groups request or distributed work and is optional in the public body;
- `traceId` is technical tracing infrastructure and is optional/public only when safe;
- `messageKey` is an optional stable UI/localization key;
- `message` is the safe default message and must not be used as machine contract;
- `localMessage` is optional localized/user-facing text;
- `violations[].messageKey` may be used for field-level localization;
- full update defaults to `200 OK` with body for Catalog-demo;
- bodyless single delete defaults to `204 No Content` on success and `404` when already absent;
- delete-multiple defaults to `200 OK` with a result DTO when introduced.

## Boundary between validation and domain errors

Springmaster separates boundary validation from domain decisions.

Boundary validation checks the external request shape and maps to `400`. Examples are missing required fields, blank required strings, malformed JSON, invalid enum values, invalid query parameters and unsupported sort fields.

Domain errors happen after the request has a valid shape. Duplicate keys, optimistic-lock conflicts and invalid state transitions map to `409` by default. Unknown resources map to `404` when the id or lookup key is syntactically acceptable.

Controllers must not silently convert domain conflicts into `400`, and services must not throw generic runtime exceptions for expected client-facing domain failures.

## Implementation expectation

Reference APIs should use a global exception handling component for API errors. Controller-local `@ExceptionHandler` methods and ad-hoc `Map<String, Object>` error bodies are not canonical Springmaster patterns.

A Springmaster-compatible implementation may use:

- a reusable `ApiErrorResponse` DTO,
- a reusable `ApiViolationDTO`,
- a global `@ControllerAdvice` or equivalent Spring MVC error handler,
- typed exceptions for not-found, conflict and business-rule cases,
- a central error-id generator or request correlation adapter,
- optional `ProblemDetail` internally as long as the external body follows this standard.

The standard does not require these Java classes to exist yet. Their introduction belongs to a later Core or test-utility patch.

## OpenAPI contract

Generated OpenAPI must expose the canonical error response schema for common client error responses.

At minimum, future gates should verify that:

- `400`, `401`, `403`, `404`, `409` and `500` reference the standard error schema where applicable,
- validation-capable operations document `400`,
- detail/update/delete operations document `404`,
- create/update/command operations document `409` where conflict is possible,
- single delete operations remain bodyless and still document the standard error body for failures,
- the error schema includes `timestamp`, `status`, `error`, `errorType`, `message`, `errorId`, `path` and `method`;
- optional fields `messageKey`, `localMessage`, `correlationId`, `traceId` and `violations[].messageKey` are either documented or intentionally absent from the first slice.

## Catalog-demo readiness rule

Catalog-demo must not become the canonical API reference while it still exposes local ad-hoc error maps as final behavior.

Before CatalogItem is accepted as the API reference slice, the implementation plan must decide whether the first slice already implements the global error contract or whether the error contract is explicitly deferred to a named follow-up patch. If deferred, the CatalogItem API must not be presented as complete or canonical for error behavior.

The first complete CatalogItem controller reference must demonstrate at least:

- invalid create request returns `400` with the standard error body,
- invalid list query returns `400` with the standard error body,
- unknown id returns `404` with the standard error body,
- duplicate business key or equivalent conflict returns `409` with the standard error body if the domain supports such a rule,
- successful single delete remains bodyless while failure responses use the standard error body.

## Future gates

This standard should become enforceable through:

1. MockMvc integration tests for validation, not-found, conflict and unauthorized/forbidden scenarios.
2. OpenAPI contract tests for the shared error schema and response references.
3. Reflection or ArchUnit rules that reject controller-local `Map<String, Object>` error bodies in reference APIs.
4. Reusable Springmaster test helpers for asserting `errorType`, `status`, `path`, `method` and `violations`.
5. A later Maven-bound quality gate once the error DTO and OpenAPI generation strategy are stable.

Until those gates exist, this document is the authoritative rule and Catalog-demo is the expected demonstrator.

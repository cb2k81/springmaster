# CatalogItem Global API Error Handler Migration

Patch `000117_springmaster_catalogitem_global_api_error_handler_migration` migrates the CatalogItem candidate reference slice from controller-local API error handling to the System-Core global API error contract introduced by `000116`.

## Purpose

The CatalogItem slice must demonstrate that generated application slices do not need local error envelopes or controller-local `@ExceptionHandler` methods for standard API failures.

The migration proves that Demo controllers can rely on the Core-owned `GlobalApiExceptionHandler` while preserving the public error contract for validation, invalid requests, not-found and conflict responses.

## Runtime changes

The CatalogItem controller no longer declares local exception handlers. Standard errors are handled by the global Core advice:

```text
GlobalApiExceptionHandler
ApiErrorResponse
ApiViolationDTO
ApiErrorType
ApiErrorIdGenerator
```

The controller and service now raise Core-owned exceptions for standard resource failures:

```text
ResourceNotFoundException -> 404 RESOURCE_NOT_FOUND
EntityAlreadyExistsException -> 409 CONFLICT
IllegalArgumentException -> 400 INVALID_REQUEST
MethodArgumentNotValidException -> 400 VALIDATION_FAILED
```

CatalogItem-specific message keys are preserved where the domain owns the semantic detail:

```text
catalog.item.not-found
catalog.item.conflict
```

Generic boundary failures continue to use Core-owned message keys:

```text
springmaster.validation.failed
springmaster.request.invalid
```

## Removed local error boundary

The following CatalogItem-local error classes are no longer part of the runtime contract and are removed from the Demo slice:

```text
CatalogApiErrorResponse
CatalogApiViolation
CatalogItemNotFoundException
```

Generated slices must not introduce equivalent local error DTOs or local controller advice for standard failure classes. Domain-specific exceptions may still exist only when they carry domain semantics not covered by the Core exception vocabulary.

## Verification

The migration is verified by targeted tests for:

* validation failures with `VALIDATION_FAILED`;
* invalid query parameters with `INVALID_REQUEST`;
* unknown ID and alternate-key lookups with `RESOURCE_NOT_FOUND`;
* duplicate SKU creation with `CONFLICT`;
* correlation ID propagation through `X-Correlation-Id`;
* OpenAPI query-contract regression;
* source-based query report regression;
* full Maven regression.

## Boundaries

This patch does not introduce the Detail/Lookup contract report, the Write API contract report or the Request Validation/OpenAPI gate. Those remain follow-up roadmap items.

CatalogItem remains a candidate reference slice and is not promoted to canonical status by this migration.

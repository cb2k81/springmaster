# List, Filter and Query Standard

## Status

Accepted as generic Springmaster API standard with patch `000044_springmaster_api_standards_adr_extraction`; query naming and reference-data vocabulary harmonized by patch `000058_springmaster_api_query_reference_data_consistency_standard`.

## Purpose

Management UIs need predictable list APIs. Paging, sorting, filtering and bounded selector/reference-data endpoints must therefore follow a consistent contract instead of being designed separately per entity.

This standard extracts the reusable part of IDM list/filter/query ADR material. It does not define IDM-specific filters, role assignments, permission names or scope semantics.

## Standard

A UI-capable management API should provide a paged list endpoint for table views when the collection can grow beyond a small bounded set. The response contract should use the Springmaster/Core paging shape represented by `PagedResponseDTO`: `items`, `page`, `size`, `totalElements` and `totalPages`.

Paged endpoints use zero-based `page` numbers. `size` must be greater than zero and must be capped. The current Core support class `PagedQuerySupport` defines `MAX_PAGE_SIZE = 200`; reference implementations should use that limit unless a project explicitly documents a stricter domain limit.

Sorting must use stable external field names. API consumers must not be required to know database column names, entity internals or repository implementation details. Unsupported sort fields or unsupported sort directions must be rejected with `400 Bad Request` rather than ignored silently.

Filtering must be explicit. A filter parameter must have a documented name, type, matching behavior and null/empty behavior. Free-text search is allowed only when the endpoint documents which fields are searched and whether matching is exact, prefix-based, contains-based or normalized.

The standard query parameter names are:

| Parameter | Meaning |
|---|---|
| `page` | zero-based page index |
| `size` | requested page size within the configured maximum |
| `sortBy` | external sort field name |
| `sortDir` | `asc` or `desc`; blank or missing means default ascending where supported |
| documented filter names | endpoint-specific filters with stable external names |

Unbounded all-data endpoints are not canonical for new Springmaster management APIs. Small selector use cases use `/options`. Broader stable reference models may use `/reference-data` only when an ADR documents why the response is bounded, cacheable and not a management table/export substitute.

List endpoints must not leak persistence-specific query syntax. Complex domain searches may use an explicit search request object, but then the endpoint is a documented query command and not an accidental body-bearing `GET`.

## Endpoint shape guidance

The default collection shape is:

```text
GET /api/<domain>/<resources>
```

for paged lists with query parameters.

A bounded selector variant may use:

```text
GET /api/<domain>/<resources>/options
```

only when the endpoint returns intentionally small option DTOs for UI selector semantics. A broader bounded reference-data endpoint may use `/reference-data` only with ADR-backed semantics. `/all` is non-canonical for new Springmaster reference APIs and must not be introduced by Catalog-demo.

## Reference implementation expectation

Catalog-demo must first demonstrate the list contract with `CatalogItem`: a paged list for UI tables using `page`, `size`, `sortBy` and `sortDir`, and only if needed for a bounded selection scenario, a clearly documented `/options` endpoint. Catalog-demo must not introduce `/all` in the first canonical slice.

## Future gates

The intended enforcement path is:

1. Controller or integration tests for default paging, invalid page, invalid size, unsupported `sortBy` field and unsupported `sortDir`.
2. OpenAPI contract tests for canonical query parameter names and response schema shape.
3. Reusable test helpers for `PagedResponseDTO` assertions.
4. Optional ArchUnit or custom Java tests for use of the Springmaster paging support classes in management controllers.

Until automated gates exist, every new management list endpoint must be reviewed against this standard before it is treated as UI-ready.


# List, Filter and Query Standard

## Status

Accepted as generic Springmaster API standard with patch `000044_springmaster_api_standards_adr_extraction`; query naming and reference-data vocabulary harmonized by patch `000058_springmaster_api_query_reference_data_consistency_standard`; complete result-set and frontend export semantics amended by patch `000091_springmaster_list_query_export_all_contract`.

## Purpose

Management UIs need predictable list APIs. Paging, sorting, filtering, complete-result-set export access and bounded selector/reference-data endpoints must therefore follow a consistent contract instead of being designed separately per entity.

This standard extracts the reusable part of IDM list/filter/query ADR material. It does not define IDM-specific filters, role assignments, permission names or scope semantics.

## Standard

A UI-capable management API should provide a paged list endpoint for table views when the collection can grow beyond a small bounded set. The response contract should use the Springmaster/Core paging shape represented by `PagedResponseDTO`: `items`, `page`, `size`, `totalElements` and `totalPages`.

Paged endpoints use zero-based `page` numbers. `size` must be greater than zero and must be capped. The current Core support class `PagedQuerySupport` defines `MAX_PAGE_SIZE = 200`; reference implementations should use that limit unless a project explicitly documents a stricter domain limit.

A queryable management result set that is used by a frontend export, backend batch process or service-to-service integration should also expose a complete-result-set access mode. For simple GET-queryable collections this access mode is:

```text
GET /api/<domain>/<resources>/all
```

The `/all` endpoint is unpaged at the public API boundary. It accepts the same documented filters and the same `sortBy`/`sortDir` contract as the paged list, but it must not require or silently apply `page` or `size`. Implementations may process the data internally in chunks, cursors, streams or pages, but the public result must be the complete filtered and authorized result set.

Sorting must use stable external field names. API consumers must not be required to know database column names, entity internals or repository implementation details. Unsupported sort fields or unsupported sort directions must be rejected with `400 Bad Request` rather than ignored silently. Paged and complete result-set endpoints must use a deterministic default order and a stable tie-breaker so pagination and export do not drift across repeated reads.

Filtering must be explicit. A filter parameter must have a documented name, type, matching behavior and null/empty behavior. Free-text search is allowed only when the endpoint documents which fields are searched and whether matching is exact, prefix-based, contains-based or normalized.

The standard paged query parameter names are:

| Parameter | Meaning |
|---|---|
| `page` | zero-based page index |
| `size` | requested page size within the configured maximum |
| `sortBy` | external sort field name |
| `sortDir` | `asc` or `desc`; blank or missing means default ascending where supported |
| documented filter names | endpoint-specific filters with stable external names |

The standard complete-result-set query parameter names are:

| Parameter | Meaning |
|---|---|
| `sortBy` | same external sort field allowlist as the paged list |
| `sortDir` | same direction semantics as the paged list |
| documented filter names | same filter semantics as the paged list |

`page` and `size` are not part of the `/all` query contract. Supplying them should return `400 Bad Request` unless a project-specific ADR explicitly keeps them as ignored compatibility parameters.

List endpoints must not leak persistence-specific query syntax. Complex domain searches may use an explicit search request object, but then the endpoint is a documented query command and not an accidental body-bearing `GET`. The complete access mode for such searches is `POST /api/<domain>/<resources>/search/all` unless a project-specific ADR defines an asynchronous export/job resource.

## Endpoint shape guidance

The default collection shape is:

```text
GET /api/<domain>/<resources>
```

for paged lists with query parameters.

The complete result-set shape is:

```text
GET /api/<domain>/<resources>/all
```

for frontend export, backend batch and integration use cases that need the whole matching result set without public API pagination.

A bounded selector variant may use:

```text
GET /api/<domain>/<resources>/options
```

only when the endpoint returns intentionally small option DTOs for UI selector semantics. A broader bounded reference-data endpoint may use `/reference-data` only with ADR-backed semantics. `/all` must not be used for selector/reference-data semantics; it is reserved for complete result-set retrieval of a documented query.

## Empty, count and error behavior

A paged list with no matches returns `200 OK` with `items: []`, `totalElements: 0` and `totalPages: 0` or the documented zero-result page semantics.

A complete `/all` endpoint with no matches returns `200 OK` with `[]`.

Paged responses expose the filtered and authorized count through `totalElements`. Optional count-only endpoints may be introduced only when a use case needs a count without loading page data. Such endpoints must use the same filter, security and data-scope predicates as the paged and complete data endpoints. Sorting does not affect the count.

Invalid query values, unsupported sort fields, unsupported sort directions, invalid filter values and invalid pagination values must return the standard Springmaster API error body with `400 Bad Request`.

## Reference implementation expectation

Catalog-demo must first demonstrate the list contract with `CatalogItem`: a paged list for UI tables using `page`, `size`, `sortBy` and `sortDir`.

Before CatalogItem is promoted to a complete canonical export-ready reference slice, it must also demonstrate `GET /api/demo/catalog/items/all` with the same filter and sort contract as the paged list, complete-result semantics, empty-array behavior and standard query error responses.

Catalog-demo may additionally add `/options` only for a bounded selection scenario, with a clearly documented option DTO and without using options as an export substitute.

## Future gates

The intended enforcement path is:

1. Controller or integration tests for default paging, invalid page, invalid size, unsupported `sortBy` field and unsupported `sortDir`.
2. Controller or integration tests for `/all` with filters, sorting, empty results and invalid query values.
3. OpenAPI contract tests for canonical query parameter names and response schema shape.
4. OpenAPI checks that `/all` does not require or silently document `page`/`size` as public pagination controls.
5. Reusable test helpers for `PagedResponseDTO` assertions and future complete-result-set assertions.
6. Optional ArchUnit or custom Java tests for use of the Springmaster paging/query support classes in management controllers and services.

Until automated gates exist, every new management list endpoint and every complete-result-set endpoint must be reviewed against this standard before it is treated as UI-ready or export-ready.


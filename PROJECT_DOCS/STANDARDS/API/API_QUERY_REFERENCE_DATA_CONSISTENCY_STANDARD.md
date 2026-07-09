# API Query and Reference Data Consistency Standard

## Status

Accepted as generic Springmaster API consistency standard with patch `000058_springmaster_api_query_reference_data_consistency_standard`; complete result-set and `/all` export semantics amended by patch `000091_springmaster_list_query_export_all_contract`.

This document resolves the P0 query/reference-data consistency gaps recorded by `000057_springmaster_standard_consistency_and_adr_gap_review` and records the later clarification that `/all` is canonical when it is an explicit complete-result-set endpoint.

## Purpose

The earlier API standards were intentionally created before implementation gates. The consistency review found ambiguities that must be resolved before OpenAPI, MockMvc or Java-boundary gates can be implemented:

1. `sort` versus `sortBy` as the public list sorting parameter.
2. `/all` versus `/options` and ADR-backed `/reference-data` for unpaged access patterns.
3. frontend export and backend batch use cases that need the whole filtered result set without public API pagination.

This standard fixes those decisions for new Springmaster reference APIs and for Catalog-demo.

## Scope

This standard applies to new Springmaster reference APIs, Catalog-demo and future generated or reusable API contract gates.

It does not require immediate changes to IDM, Personnel, Contacts, Orders or any other existing target project. Existing projects remain read-only comparison inputs until Catalog-demo proves the standards and target-update governance allows delivery.

## Canonical query parameter vocabulary

New Springmaster UI-capable management list APIs use the following canonical public query parameter names:

| Parameter | Required | Semantics |
|---|---:|---|
| `page` | no | zero-based page index; default `0` unless the endpoint documents a stricter default |
| `size` | no | positive page size within the configured maximum |
| `sortBy` | no | stable external sort field name, never a database column or Java repository expression |
| `sortDir` | no | `asc` or `desc`; default is endpoint-specific and must be documented |
| documented filters | no | explicit endpoint-specific filter names with documented matching behavior |

`sortBy` is the canonical Springmaster name. The parameter name `sort` is not canonical for new Springmaster reference APIs.

## Legacy and target-comparison handling of `sort`

Existing applications may expose `sort`, Spring Data style `sort` expressions, controller-level `Pageable` parameters or other legacy vocabulary. Springmaster gates must treat those findings according to the gate context:

| Context | Handling |
|---|---|
| Catalog-demo reference API | `sort` is not allowed as the canonical parameter |
| new Springmaster-generated project | `sort` is not allowed as the canonical parameter |
| read-only target comparison | `sort` may be reported as compatibility/legacy finding |
| project-specific exception | requires an ADR or target-project compatibility note |

Gate implementations must not silently accept both `sort` and `sortBy` as equal canonical choices for new reference APIs, because doing so would weaken the reference contract.

## Sort field semantics

`sortBy` values use public external field names. They must not expose:

- database column names,
- JPA entity property paths,
- repository method fragments,
- Java getter names when those names differ from the public DTO field,
- composite expressions unless explicitly documented as public API values.

Each endpoint must define its allowed sort fields. Unsupported sort fields return `400 Bad Request` using the standard API error contract.

Sorting must be deterministic. Every paged list and every complete-result-set endpoint must define a default ordering and a stable tie-breaker so page boundaries, repeated reads and exports remain reproducible.

## Multi-sort policy

The default Springmaster reference contract supports one `sortBy` and one `sortDir` pair.

Multi-sort is deferred. A project that needs multi-sort must define an ADR before it becomes a reference pattern. That ADR must decide whether multi-sort is represented by repeated query parameters, a comma-separated expression or a search/request DTO.

Catalog-demo must not introduce multi-sort in the first canonical CatalogItem slice.

## Filter parameter semantics

Filter parameters must be explicit and stable. Each filter must document:

- public parameter name,
- value type,
- empty and missing behavior,
- matching mode,
- case-sensitivity or normalization rule,
- whether the filter is exact, prefix, contains, enum-based, date-based or range-based.

Ad-hoc repository query vocabulary must not leak into public filters.

Paged list, `/all` and count-only endpoints for the same result set must use the same filter semantics and the same security/data-scope predicates.

## Complete result-set endpoint: `/all`

Use `/all` when the API must return the complete matching management result set for frontend export, backend batch jobs or service-to-service integration consumers.

Canonical shape for simple GET-queryable collections:

```text
GET /api/<domain>/<resources>/all
```

The endpoint accepts the same documented filters, `sortBy` and `sortDir` semantics as the paged list. It does not accept public `page` or `size` pagination parameters.

The response is the full matching result set as public DTOs. Until Springmaster accepts a dedicated unpaged response envelope, the external shape is a JSON array of list/export DTOs. Empty results return `200 OK` with `[]`.

The endpoint must not silently truncate the result to a default or maximum page size. Implementations may internally chunk, stream or page through the data, but the public response must represent the complete filtered and authorized result.

For complex search DTOs, the complete result-set shape is:

```text
POST /api/<domain>/<resources>/search/all
```

unless a project-specific ADR defines an asynchronous export/job resource with equivalent query semantics.

## Bounded selector endpoint: `/options`

Use `/options` for small, bounded selection data intended for UI controls such as dropdowns, simple relation pickers, autocomplete seeds or selector lists.

Canonical shape:

```text
GET /api/<domain>/<resources>/options
```

The response should use intentionally small option DTOs, for example `<Resource>OptionDTO`, and should not be treated as a management table/list response.

`/options` endpoints must be bounded by design. The implementation may still use an internal maximum, query filter or stable ordering, but consumers must not treat `/options` as an export endpoint.

## Reference data endpoint: `/reference-data`

Use `/reference-data` only when the endpoint returns a stable read model that is broader than simple options and still operationally bounded.

Canonical shape when justified:

```text
GET /api/<domain>/<resources>/reference-data
```

A `/reference-data` endpoint requires an ADR or standard-specific decision that documents:

- why the result set is bounded,
- cacheability expectations,
- intended UI or integration use,
- DTO shape,
- sorting/default order,
- security classification,
- whether the response can change frequently,
- why `/options`, `/all` or the paged collection endpoint is insufficient.

Catalog-demo must not introduce `/reference-data` in the first CatalogItem slice unless a dedicated ADR is accepted first.

## Legacy and target-comparison handling of `/all`

Existing target projects may already expose `/all`. During read-only target comparison, such endpoints must be classified as one of:

| Classification | Meaning |
|---|---|
| `complete-result-set-contract` | satisfies the Springmaster `/all` standard: same filters/sort/security as paged list, complete result, no silent truncation |
| `legacy-compatible` | existing behavior retained before Springmaster delivery but not yet proven as complete-result-set contract |
| `adr-backed-exception` | intentionally retained by project ADR with different semantics |
| `needs-remediation` | should be changed when the project is later supplied by Springmaster |
| `not-assessed` | insufficient information to classify |

Gate tooling for Catalog-demo must fail only for ambiguous or non-contractual `/all` endpoints. A documented complete-result-set `/all` endpoint is canonical.

## Collection list versus complete/options/reference-data

| Use case | Canonical endpoint | Response shape |
|---|---|---|
| UI management table | `GET /api/<domain>/<resources>` | `PagedResponseDTO<<Resource>ListItemDTO>` or equivalent public paging shape |
| Complete result set for frontend export/batch/integration | `GET /api/<domain>/<resources>/all` | JSON array of `<Resource>ListItemDTO` or documented `<Resource>ExportDTO` |
| Detail view | `GET /api/<domain>/<resources>/{id}` | `<Resource>DTO` |
| Small selector/dropdown | `GET /api/<domain>/<resources>/options` | list of `<Resource>OptionDTO` or equivalent intentionally small DTO |
| Broader stable reference model | `GET /api/<domain>/<resources>/reference-data` only with ADR | ADR-defined DTO |
| Complex paged search | `POST /api/<domain>/<resources>/search` | paged search response with `totalElements` |
| Complex complete search/export | `POST /api/<domain>/<resources>/search/all` or ADR-backed job endpoint | complete result DTO array or job/status resource |

## Catalog-demo readiness rule

The first canonical CatalogItem slice must use:

- `GET /api/demo/catalog/items` for the paged list,
- query parameters `page`, `size`, `sortBy`, `sortDir` and documented filters only,
- `PagedResponseDTO<CatalogItemListItemDTO>` or an equivalent public paging shape,
- no controller-level `Pageable` exposure,
- no public `Page<CatalogItemDTO>` response,
- `GET /api/demo/catalog/items/all` before CatalogItem is promoted to a complete export-ready canonical reference slice,
- optional `GET /api/demo/catalog/items/options` only if an actual selector use case is documented,
- no `/reference-data` endpoint unless a dedicated ADR is accepted first.

## Gate implications

The first OpenAPI query gate must validate that Catalog-demo exposes `page`, `size`, `sortBy` and `sortDir` for paged management lists and does not expose generated `arg0`/`arg1` style parameters, public `Pageable` artifacts or `sort` as the canonical parameter.

The first `/all` gate must validate that:

- `/all` endpoints are paired with a paged collection or documented search endpoint,
- `/all` exposes the same documented filter and sort vocabulary as the paged endpoint,
- `/all` does not require `page` or `size`,
- `/all` responses use public DTO arrays or a future accepted Springmaster unpaged response shape,
- `/all` is not used as selector/reference-data vocabulary.

The first reference-data gate must validate that:

- `/options` is bounded and uses option DTOs,
- `/reference-data` is absent unless an ADR is linked,
- list endpoints return the paging shape rather than an unbounded array,
- complete-result-set endpoints are explicitly identifiable as `/all` or documented search/export/job endpoints.

## ADR impact

This standard resolves the `sort` versus `sortBy`, `/all` complete result-set, `/options` selector and `/reference-data` bounded reference-data vocabulary for new reference APIs.

It does not close the broader ADR backlog. The following topics still require ADRs or later standards before strict tooling can cover them:

- multi-sort,
- advanced search DTOs,
- asynchronous export/job endpoints,
- streaming response contracts,
- reference-data caching policy,
- API versioning,
- target-project exception handling.

# API Query and Reference Data Consistency Standard

## Status

Accepted as generic Springmaster API consistency standard with patch `000058_springmaster_api_query_reference_data_consistency_standard`.

This document resolves the P0 query/reference-data consistency gaps recorded by `000057_springmaster_standard_consistency_and_adr_gap_review`.

## Purpose

The earlier API standards were intentionally created before implementation gates. The consistency review found two blocking ambiguities that must be resolved before OpenAPI, MockMvc or Java-boundary gates can be implemented:

1. `sort` versus `sortBy` as the public list sorting parameter.
2. `/all` versus `/options` and ADR-backed `/reference-data` for bounded unpaged data.

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
- why `/options` or the paged collection endpoint is insufficient.

Catalog-demo must not introduce `/reference-data` in the first CatalogItem slice unless a dedicated ADR is accepted first.

## `/all` policy

`/all` is not canonical for new Springmaster reference APIs.

Do not introduce:

```text
GET /api/<domain>/<resources>/all
```

for new Catalog-demo or Springmaster-generated management APIs.

Existing target projects may still expose `/all`. During read-only target comparison, such endpoints must be classified as one of:

| Classification | Meaning |
|---|---|
| `legacy-compatible` | existing behavior retained before Springmaster delivery |
| `adr-backed-exception` | intentionally retained by project ADR |
| `needs-remediation` | should be changed when the project is later supplied by Springmaster |
| `not-assessed` | insufficient information to classify |

Gate tooling for Catalog-demo must fail if a new canonical management endpoint introduces `/all` without an explicit Springmaster ADR.

## Collection list versus options/reference-data

| Use case | Canonical endpoint | Response shape |
|---|---|---|
| UI management table | `GET /api/<domain>/<resources>` | `PagedResponseDTO<<Resource>ListItemDTO>` or equivalent public paging shape |
| Detail view | `GET /api/<domain>/<resources>/{id}` | `<Resource>DTO` |
| Small selector/dropdown | `GET /api/<domain>/<resources>/options` | list of `<Resource>OptionDTO` or equivalent intentionally small DTO |
| Broader stable reference model | `GET /api/<domain>/<resources>/reference-data` only with ADR | ADR-defined DTO |
| Export/all records | not part of first Springmaster reference API | deferred; requires separate export/reporting/batch decision |

## Catalog-demo readiness rule

The first canonical CatalogItem slice must use:

- `GET /api/demo/catalog/items` for the paged list,
- query parameters `page`, `size`, `sortBy`, `sortDir` and documented filters only,
- `PagedResponseDTO<CatalogItemListItemDTO>` or an equivalent public paging shape,
- no controller-level `Pageable` exposure,
- no public `Page<CatalogItemDTO>` response,
- no `/all` endpoint,
- optional `GET /api/demo/catalog/items/options` only if an actual selector use case is documented,
- no `/reference-data` endpoint unless a dedicated ADR is accepted first.

## Gate implications

The first OpenAPI query gate must validate that Catalog-demo exposes `page`, `size`, `sortBy` and `sortDir` for paged management lists and does not expose generated `arg0`/`arg1` style parameters, public `Pageable` artifacts or `sort` as the canonical parameter.

The first reference-data gate must validate that:

- `/all` is absent from new canonical APIs,
- `/options` is bounded and uses option DTOs,
- `/reference-data` is absent unless an ADR is linked,
- list endpoints return the paging shape rather than an unbounded array.

## ADR impact

This standard resolves the `sort` versus `sortBy` and `/all` versus `/options`/`/reference-data` P0 gaps for new reference APIs.

It does not close the broader ADR backlog. The following topics still require ADRs or later standards before strict tooling can cover them:

- multi-sort,
- advanced search DTOs,
- export endpoints,
- reference-data caching policy,
- API versioning,
- target-project exception handling.

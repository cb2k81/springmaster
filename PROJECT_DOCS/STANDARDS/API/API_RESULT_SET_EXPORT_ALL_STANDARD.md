# API Result-Set Export and `/all` Standard

## Status

Accepted as Springmaster API standard addendum with patch `000091_springmaster_list_query_export_all_contract`; count-only response shape narrowed by candidate patch `000098_springmaster_count_response_contract_candidate`.

This standard amends the earlier `/all` decision from `000058_springmaster_api_query_reference_data_consistency_standard` and `ADR-0002`. The old rejection still applies to ambiguous, undocumented, selector-like or accidentally unbounded `/all` endpoints. It does not apply to the explicit complete-result-set contract defined here.

## Purpose

Frontend table exports, backend batch jobs and service-to-service integrations need a way to retrieve the same result set that a paged UI list can show, but without public API pagination.

Springmaster therefore distinguishes four read patterns:

| Pattern | Endpoint family | Intended use |
|---|---|---|
| Paged management list | `GET /api/<domain>/<resources>` | UI tables, incremental browsing, normal list screens |
| Complete result set | `GET /api/<domain>/<resources>/all` | frontend export, backend batch/integration consumers, full filtered read |
| Bounded options | `GET /api/<domain>/<resources>/options` | small selector/dropdown/relation-picker data |
| ADR-backed reference data | `GET /api/<domain>/<resources>/reference-data` | stable bounded read model broader than options |

The complete-result-set endpoint is not a replacement for the paged list. It is the unpaged access mode of the same documented query model.

## Standard contract

Every queryable management result set that is intended for UI lists, frontend export or integration/batch consumption should define the query specification once and expose the required access modes explicitly.

For simple GET-queryable collections the canonical pair is:

```text
GET /api/<domain>/<resources>
GET /api/<domain>/<resources>/all
```

The paged endpoint accepts `page`, `size`, `sortBy`, `sortDir` and documented filters.

The `/all` endpoint accepts the same `sortBy`, `sortDir` and documented filters. It must not require `page` or `size`, and it must not silently apply the public page-size cap.

When a query is too complex for stable GET query parameters and uses a documented search request DTO, the canonical pair is:

```text
POST /api/<domain>/<resources>/search
POST /api/<domain>/<resources>/search/all
```

A project may use an ADR-backed export/job endpoint instead when synchronous complete retrieval is not operationally acceptable. Such a job endpoint must still preserve the same query semantics and must expose a status/result resource if it returns `202 Accepted`.

## Query equivalence

The paged and complete access modes must use the same query semantics.

| Aspect | Requirement |
|---|---|
| Filters | same public filter names, types, empty behavior and matching modes |
| Security | same authentication, permission and data-scope predicates unless an explicit stronger export permission is documented |
| Sort fields | same public `sortBy` allowlist |
| Sort direction | same `sortDir` semantics |
| Default order | same default sort order when no explicit sort is supplied |
| Tie-breaker | same deterministic tie-breaker so repeated reads are stable |
| Visibility | list and count must not include objects hidden by security/data-scope rules |

Sort does not change the count. Count, paged data and `/all` data must nevertheless be based on the same filtered and authorized result set.

## Complete result-set response

The synchronous `/all` response returns all matching items as public DTOs.

Until Springmaster accepts a dedicated unpaged response envelope in Core, the canonical external shape is a JSON array of public list/export DTOs:

```json
[]
```

A non-empty response uses the same public list-item DTO as the paged list unless the endpoint documents a dedicated export DTO. Export DTOs may include additional export-relevant public fields, but they must not expose entities, persistence fields or internal repository structure.

Empty complete result sets return `200 OK` with an empty array. They are not `404`.

The endpoint must not silently truncate data. If the server cannot complete the request because of an operational failure, timeout, overload or serialization problem, it must return the standard API error body and must not return a partial result as if it were complete.

## Implementation guidance

The `/all` contract is unpaged at the public API boundary. Implementations may still process the result internally in chunks, pages, streams or database cursors to avoid memory pressure. Such internal batching is invisible to the client and must not change the external result.

Recommended implementation properties:

- build the filter predicate once and reuse it for paged data, `/all` data and count;
- keep authorization and data-scope predicates in the query/application service boundary, not in the controller;
- avoid loading hidden rows and filtering them in memory;
- use deterministic sorting with a stable tie-breaker;
- prefer projection/list-item/export DTO queries for large result sets;
- keep controller method signatures explicit and avoid public `Pageable` exposure;
- measure and document operational expectations for potentially large synchronous exports.

## Count behavior

Paged responses expose `totalElements` and `totalPages` through `PagedResponseDTO`.

A separate count-only endpoint is optional and must be deliberately introduced only when a UI badge, tab, dashboard, preflight or batch process needs the count without loading page data:

```text
GET /api/<domain>/<resources>/count
```

For complex search DTOs the candidate endpoint is:

```text
POST /api/<domain>/<resources>/search/count
```

The count endpoint accepts the same documented filters as the paged list and `/all`. It does not expose `page`, `size`, `sortBy` or `sortDir` as count semantics, because pagination and sorting do not affect the number of matching rows. Supplying unsupported count query parameters should return `400 Bad Request` unless a project-specific ADR documents ignored compatibility parameters.

The count result shape follows `API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md`:

```json
{ "totalElements": 0 }
```

Springmaster Core may later introduce a reusable `CountResponseDTO` with this exact external shape. Until then, projects must not invent incompatible per-controller count envelopes.

## Error behavior

| Situation | Status |
|---|---:|
| no matching data | `200 OK` with `[]` for `/all`; `200 OK` with `items: []` for paged list |
| invalid page or size on paged list | `400 Bad Request` |
| `page` or `size` supplied to `/all` | `400 Bad Request` unless a project ADR explicitly treats them as ignored compatibility parameters |
| unsupported `sortBy` | `400 Bad Request` |
| unsupported `sortDir` | `400 Bad Request` |
| invalid filter value | `400 Bad Request` |
| unauthenticated | `401 Unauthorized` |
| authenticated but not permitted | `403 Forbidden` |
| operational failure while producing complete result | standard `500`/`503` error body; no partial success |

## Boundary to `/options` and `/reference-data`

`/all` is complete result-set retrieval for a management query. It may be large and is intended for export or batch/integration consumers.

`/options` is small, bounded selector data. It must not be used as a full export substitute.

`/reference-data` is a bounded, stable and ADR-backed read model. It must not be used as a hidden unbounded export endpoint.

## Catalog-demo expectation

Catalog-demo must keep the paged collection endpoint as the first proof of the list contract. Before CatalogItem is promoted to a complete canonical export-ready reference slice, it must also demonstrate the complete result-set access mode:

```text
GET /api/demo/catalog/items/all
```

The `/all` endpoint must reuse the CatalogItem filter/sort contract, return all matching `CatalogItemListItemDTO` or a documented export DTO, reject invalid filters/sort values with the standard error body and return `200 OK` with `[]` for empty results.

## Future gates

Report-only and later strict gates should check:

1. management collections have a paged endpoint before `/all` is treated as canonical;
2. `/all` endpoints do not expose `page` or `size` as required parameters;
3. `/all` endpoints expose the same documented filters and sort parameters as the paged list;
4. `/all` responses use public DTO arrays or a future accepted Springmaster unpaged envelope;
5. `/options` endpoints are not used as export substitutes;
6. count endpoints, when present, use the same filter/security predicate family;
7. OpenAPI does not document silent truncation or internal persistence/page types;
8. target projects with legacy `/all` endpoints are classified by whether they satisfy this complete-result-set contract.

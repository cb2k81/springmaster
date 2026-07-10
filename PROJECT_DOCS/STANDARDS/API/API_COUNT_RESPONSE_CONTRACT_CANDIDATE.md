# API Count Response Contract Candidate

## Status

Candidate Springmaster API standard since patch `000098_springmaster_count_response_contract_candidate`.

This document narrows the optional count-only endpoint that was introduced by `000091_springmaster_list_query_export_all_contract`. It is a candidate because the Core DTO and CatalogItem behavior reference are still deferred to follow-up patches.

## Purpose

Paged list responses already expose the count that a table needs through `PagedResponseDTO.totalElements`. Some consumers need only the number of matching objects without loading a page or complete result set, for example:

- dashboard counters;
- tab badges;
- preflight checks before batch processing;
- backend integration decisions;
- UI summaries where the list data is loaded later or not at all.

Springmaster therefore defines a narrow count-only contract that reuses the same query semantics as the corresponding list and complete-result-set endpoints without introducing a second filter model.

## Canonical endpoints

For simple GET-queryable management collections the candidate endpoint is:

```text
GET /api/<domain>/<resources>/count
```

The endpoint is optional. It should be implemented only when the application has a concrete count-only use case. A paged table that already loads `GET /api/<domain>/<resources>` normally uses `totalElements` from the paged response and does not need an additional request.

For complex search DTOs the candidate endpoint is:

```text
POST /api/<domain>/<resources>/search/count
```

A project must not introduce ad-hoc variants such as `/total`, `/size`, `/number`, `/amount`, `/count-all`, `/searchCount` or Java method vocabulary such as `countBy...` as public management API endpoints without an ADR.

## Query semantics

The count endpoint counts the same filtered and authorized result set that the data endpoints expose.

| Aspect | Candidate requirement |
|---|---|
| Filters | same documented filter names, types, matching behavior and empty/null semantics as the paged list and `/all` endpoint |
| Security | same authentication, permission and data-scope predicates unless an explicit stronger permission is documented |
| Sorting | not part of the count semantics; sort order does not change the number of matches |
| Pagination | not part of the count semantics; `page` and `size` are not accepted public controls |
| Visibility | hidden objects must not be counted |
| Consistency | data endpoint `totalElements`, `/all` result size and count endpoint result must describe the same predicate family |

New reference APIs should not expose `sortBy`, `sortDir`, `page` or `size` on count endpoints. Supplying these parameters should return `400 Bad Request` unless a project-specific ADR explicitly keeps them as ignored compatibility vocabulary.

## Response shape

The candidate external response shape is a JSON object with one required property:

```json
{
  "totalElements": 0
}
```

Rules:

- `totalElements` is required.
- `totalElements` is a non-negative integer number.
- the value is the count after filters, security and data-scope rules have been applied.
- no matching objects returns `200 OK` with `totalElements: 0`.
- new reference APIs must not use incompatible property names such as `count`, `total`, `totalCount`, `itemsCount` or `size` for the same meaning.

Springmaster Core should later provide a reusable `CountResponseDTO` with this exact external shape. Until that DTO exists, controllers may use an endpoint-local DTO only when it preserves this shape exactly and does not leak persistence types.

## Error behavior

| Situation | Status |
|---|---:|
| no matching data | `200 OK` with `totalElements: 0` |
| invalid filter value | `400 Bad Request` |
| unsupported count query parameter | `400 Bad Request` |
| unauthenticated | `401 Unauthorized` |
| authenticated but not permitted | `403 Forbidden` |
| operational failure | standard `5xx` API error response |

Count endpoints use the standard Springmaster API error body.

## Implementation guidance

Count implementation must be efficient and must not load the full result set only to compute its size.

Recommended implementation properties:

- build the filter/security/data-scope predicate once and reuse it for paged data, `/all` data and count;
- perform the count at repository/query level where persistence is involved;
- avoid in-memory post-filtering of data that the caller is not authorized to see;
- document any known count approximation, delay or eventual-consistency behavior explicitly; exact synchronous counts are the default expectation;
- avoid applying list projections, DTO mapping or export serialization for count-only calls.

## Catalog-demo evidence path

`CatalogItem` already demonstrates:

- paged list `totalElements`;
- complete-result-set `/all`;
- shared filter and sort semantics;
- empty result behavior.

A follow-up CatalogItem patch should add `GET /api/demo/catalog/items/count` and tests proving:

- unfiltered count;
- filtered count;
- zero-result count;
- invalid filter handling;
- absence/rejection of pagination and sort controls;
- alignment with paged `totalElements`.

Until that follow-up exists, this document is a candidate contract and not yet canonical Catalog-demo evidence.

## Gate candidates

Future report-only and strict gates should check:

1. count endpoint path shape when a count endpoint exists;
2. response schema contains required `totalElements`;
3. incompatible response property names are absent;
4. count endpoint does not expose public `page`/`size` controls;
5. count endpoint does not require or semantically depend on `sortBy`/`sortDir`;
6. MockMvc behavior tests prove filtered and zero-result counts;
7. count-only implementation does not bypass documented security classification.

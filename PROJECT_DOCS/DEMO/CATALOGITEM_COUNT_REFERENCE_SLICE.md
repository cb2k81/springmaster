# CatalogItem Count Reference Slice

## Purpose

Patch `000100_springmaster_catalogitem_count_reference_slice` turns the count-only contract candidate from `000098` and the Core `CountResponseDTO` from `000099` into executable CatalogItem candidate-slice evidence.

This remains candidate evidence. It does not promote CatalogItem to a canonical reference slice.

## Public contract

```text
GET /api/demo/catalog/items/count?sku=&name=
```

Response:

```json
{ "totalElements": 0 }
```

The endpoint exposes the same filter predicates as the paged list and `/all` endpoints:

| Filter | Semantics | Empty value |
|---|---|---|
| `sku` | exact case-insensitive business-key match | ignored |
| `name` | case-insensitive substring match | ignored |

## Non-count query parameters

The endpoint rejects `page`, `size`, `sortBy` and `sortDir`. They are intentionally not part of count semantics.

This keeps the count endpoint tied to the result-set predicate, not to presentation order or page slicing.

## Architecture evidence

- The controller remains a thin HTTP adapter.
- `CatalogItemService.count(...)` reuses the same filter predicate pipeline as `listPaged(...)` and `listAll(...)`.
- The response uses Core `CountResponseDTO`.
- No Spring Data `Pageable`, persistence entity or database column vocabulary is exposed at the HTTP boundary.

## Verification

Expected verification commands:

```text
mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest
mvn -B -ntp test
```

Covered scenarios:

- unfiltered count;
- filtered count by `sku`;
- filtered count by `name`;
- empty count with `totalElements: 0`;
- rejection of paging and sorting parameters on `/count`;
- existing list, `/all`, create, detail, update, delete and error scenarios remain covered.

## Remaining canonical blockers

CatalogItem remains blocked from canonical promotion by implemented management security, stale-version conflict qualification, production-like MariaDB evidence, strict gate promotion and target-project comparison/delivery.



## Interface-backed service contract since 000102

Patch `000102_springmaster_catalogitem_query_operations_interface_adoption` keeps the count HTTP contract unchanged and introduces `CatalogItemCountQuery` as the fachliche count-query type used by the Core `CountResultSetQuery` contract.

The count endpoint still accepts only `sku` and `name`; paging and sorting remain outside count semantics.


## Persistent count-query efficiency reference since 000105

CatalogItem is now a transactional JPA candidate slice. Its count endpoint delegates to a dedicated Criteria count query with the same filter predicates as paged list and `/all`.

Persistent CatalogItem work and generated applications must follow `PROJECT_DOCS/STANDARDS/API/JPA_COUNT_QUERY_EFFICIENCY_REFERENCE.md`: count must be computed through a repository/query-level count operation with the same filter, security and data-scope predicates, without loading the full result set just to call `.size()`.

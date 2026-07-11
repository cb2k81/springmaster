# CatalogItem List Query Export-All Reference Slice

## Purpose

Patch `000092_springmaster_catalogitem_list_query_export_all_reference_slice` turns the documented list-query/export-all contract into executable CatalogItem candidate-slice evidence. Patch `000094_springmaster_catalogitem_use_core_paged_query_sort_support` then aligns the candidate slice with the Core sort helper introduced by `000093`.

This document does not promote CatalogItem to `canonical-reference-slice`. It records the concrete implementation and verification evidence for the list-query and complete result-set part of the candidate slice.

## Implemented public contract

| Use case | Endpoint | Response | Contract evidence |
|---|---|---|---|
| Paged management list | `GET /api/demo/catalog/items?page=&size=&sortBy=&sortDir=&sku=&name=` | `PagedResponseDTO<CatalogItemListItemDTO>` | page/size validation, explicit sort allow-list, explicit filters, filtered `totalElements` |
| Complete result set | `GET /api/demo/catalog/items/all?sortBy=&sortDir=&sku=&name=` | `List<CatalogItemListItemDTO>` | same filter and sort pipeline, no public page/size, no silent public truncation |
| Count-only | `GET /api/demo/catalog/items/count?sku=&name=` | `CountResponseDTO` | same filter predicates, no page/size/sort semantics |

## Filter semantics

| Filter | Semantics | Empty value |
|---|---|---|
| `sku` | exact case-insensitive business-key match | ignored |
| `name` | case-insensitive substring match | ignored |

Filters are intentionally small. The goal is reference evidence for how fachliche filter criteria are defined explicitly, not a generic query language.

## Sort semantics

Allowed `sortBy` values:

- `sku`
- `name`

Allowed `sortDir` values:

- `asc`
- `desc`

Blank or missing `sortBy` defaults to `sku`; blank or missing `sortDir` defaults to ascending. The in-memory implementation applies a stable `id` tie-breaker after the requested public sort key.

Unsupported sort fields or sort directions return `400 Bad Request` through the standard demo error body. The implementation delegates this validation to Core `PagedQuerySupport.stableComparator(...)` rather than duplicating local sort resolution logic.

## Count and empty-result semantics

The paged endpoint computes `totalElements` from the filtered result set. `totalPages` is derived from the same filtered result set and the validated page size.

The count-only endpoint computes `totalElements` from the same filter predicates used by paged list and `/all`. It exposes only `sku` and `name`; `page`, `size`, `sortBy` and `sortDir` are rejected because they are not count semantics.

Empty result sets are successful query results:

- paged list: `200 OK` with `items: []`, `totalElements: 0`, `totalPages: 0`
- `/all`: `200 OK` with `[]`
- `/count`: `200 OK` with `{ "totalElements": 0 }`

## Architecture constraints

- The controller remains a thin HTTP adapter.
- The service owns the candidate query pipeline.
- The same service-side filter/sort pipeline feeds paged and `/all` responses.
- Core `PagedQuerySupport` is reused for paging validation, sort-direction validation, sort allow-list resolution, default-sort handling and stable tie-breaker comparator construction.
- No Spring Data `Pageable`, `Page<DTO>`, persistence entity or database column vocabulary is exposed at the HTTP boundary.
- `/all` is not a legacy synonym for `/list`; it is a complete result-set contract for export, batch and integration consumers.

## Core sort-support adoption

`CatalogItemService` uses `PagedQuerySupport.stableComparator(...)` for the in-memory candidate query pipeline. The fachliche service still owns its allowed public sort fields and the field-specific comparators, but Core owns the reusable mechanics:

- default `sortBy` resolution;
- `sortDir` parsing;
- sort allow-list rejection;
- stable tie-breaker composition.

This keeps Core free of CatalogItem domain knowledge while proving that generated or handwritten fachliche slices can consume the same query infrastructure.

## Verification evidence

Expected tests for this patch:

```text
mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest
mvn -B -ntp test
```

Covered scenarios:

- paged list with filtered `totalElements`;
- `/all` with same filters and sorting;
- `/count` with the same filters and no paging or sorting semantics;
- empty paged and `/all` result sets;
- invalid page, size, sortBy and sortDir requests;
- existing create/detail/update/delete/error behavior remains covered.

## Remaining canonical blockers

This patch only closes the list-query/export-all reference-slice gap. CatalogItem remains blocked from canonical promotion by the already documented open items, especially durable persistence, Liquibase evidence, implemented management security, OpenAPI evidence, strict gate promotion and target-project comparison/delivery.



## Interface-backed service contract since 000102

Patch `000102_springmaster_catalogitem_query_operations_interface_adoption` keeps the public list, `/all` and `/count` HTTP contracts unchanged, but routes the service boundary through CatalogItem-owned query records:

```text
CatalogItemPagedQuery
CatalogItemAllQuery
CatalogItemCountQuery
```

`CatalogItemService` implements the Core `ResultSetQueryOperations` composite contract with these query types. This makes the query operations type-checkable at the Java service/application boundary without introducing generic Spring-MVC controller inheritance.

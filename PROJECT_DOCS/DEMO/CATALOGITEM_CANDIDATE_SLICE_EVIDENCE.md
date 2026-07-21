# CatalogItem Candidate Slice Evidence

## Purpose

Patch `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation` promotes the Springmaster Catalog-demo `CatalogItem` implementation from `legacy-demo-seed` toward the first `candidate-reference-slice` foundation.

This evidence file records what the slice demonstrates and what remains deferred. It does not declare Catalog-demo or CatalogItem as `canonical-reference-slice`.

## Slice state

| Field | Value |
|---|---|
| Slice | `CatalogItem` |
| State | `candidate-reference-slice` |
| Patch | `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation` |
| Canonical status | not canonical |
| Target comparison | blocked |
| Target delivery | blocked |

The previous implementation state remains relevant only as historical `legacy-demo-seed` context. The current claim is limited to a candidate slice foundation that can be validated by tests and report-only gates.

## Implemented endpoint contract

| Operation | Method and path | Status evidence | Notes |
|---|---|---:|---|
| Paged list | `GET /api/demo/catalog/items?page=&size=&sortBy=&sortDir=&sku=&name=` | `200` / `400` | Returns `PagedResponseDTO<CatalogItemListItemDTO>` with filtered `totalElements`. |
| Complete result set | `GET /api/demo/catalog/items/all?sortBy=&sortDir=&sku=&name=` | `200` / `400` | Returns all matching `CatalogItemListItemDTO` rows without public `page`/`size` truncation. |
| Count-only | `GET /api/demo/catalog/items/count?sku=&name=` | `200` / `400` | Returns `CountResponseDTO` with `totalElements` for the same filter predicates; rejects paging and sorting parameters. |
| Detail by opaque ID | `GET /api/demo/catalog/items/{id}` | `200` / `404` | Public resource identity is `id`. |
| Lookup by SKU | `GET /api/demo/catalog/items/by-sku/{sku}` | `200` / `404` | `sku` remains an explicit business key. |
| Create | `POST /api/demo/catalog/items` | `201` | `Location` points to `/{id}`, not `/{sku}`. |
| Full update | `PUT /api/demo/catalog/items/{id}` | `200` / `404` | SKU is immutable in the first candidate foundation. |
| Single delete | `DELETE /api/demo/catalog/items/{id}` | `204` / `404` | Bodyless single delete. |

Out of scope for this slice: `/list`, public `findOne`/`findFirst`/`findLast`, body-bearing single `DELETE`, delete-multiple, complex search with request body, relationship endpoints, lifecycle commands, `/reference-data`, and `/options`.

## DTO evidence

| DTO | Status | Purpose |
|---|---|---|
| `CatalogItemCreateDTO` | implemented | Create request boundary with Bean Validation constraints. |
| `CatalogItemUpdateDTO` | implemented | Full update request boundary with Bean Validation constraints. |
| `CatalogItemDTO` | implemented | Detail/create/update response. |
| `CatalogItemListItemDTO` | implemented | Paged list item and complete result-set row response. |
| `CountResponseDTO` | implemented | Core count-only response with `totalElements`. |
| `CatalogApiErrorResponse` | implemented | Demo-local standard error body evidence. |
| `CatalogApiViolation` | implemented | Field-level validation violation evidence. |
| `CatalogItemOptionDTO` | deferred | No bounded selector use case in this slice. |
| `CatalogItemSearchDTO` | deferred | Complex search out of scope. |
| `CatalogItemDeleteMultipleCommandDTO` | deferred | Bulk delete out of scope. |

## Query evidence

The paged list endpoint exposes the canonical public query vocabulary:

- `page`;
- `size`;
- `sortBy`;
- `sortDir`;
- explicit filter `sku`;
- explicit filter `name`.

The complete result-set endpoint `/all` exposes the same filter and sort vocabulary but intentionally does not expose public `page` or `size` parameters. It is the CatalogItem reference evidence for frontend export, backend batch and service-to-service consumers that need all matching rows.

The count-only endpoint `/count` exposes only filter parameters (`sku`, `name`) and returns `CountResponseDTO` with `totalElements`. It intentionally rejects `page`, `size`, `sortBy` and `sortDir`, because sorting and pagination are not part of count semantics.

Filter semantics:

| Filter | Semantics | Empty value |
|---|---|---|
| `sku` | exact case-insensitive business-key match | ignored |
| `name` | case-insensitive substring match | ignored |

The first candidate sort allow-list is intentionally small:

- `sku`;
- `name`.

Unsupported `sortBy` and unsupported `sortDir` values produce `400 Bad Request` with standard error-body evidence. Invalid `page` or `size` values on the paged endpoint also produce `400 Bad Request`.

List and `/all` use the same in-memory query pipeline for filters and sorting. Sort allow-list resolution, default-sort handling, sort direction parsing and tie-breaker composition are delegated to Core `PagedQuerySupport.stableComparator(...)`. The paged response uses the filtered result size for `totalElements` and `totalPages`. Empty matching result sets return `200 OK` with `items: []`, `totalElements: 0`, `totalPages: 0`; `/all` returns `200 OK` with an empty JSON array.

## Identity evidence

| Concept | Candidate evidence |
|---|---|
| Public identity | opaque string `id` from `DomainEntity` |
| Business key | `sku` |
| Detail path | `/{id}` |
| Business-key lookup | `/by-sku/{sku}` |
| Create location | `Location: /api/demo/catalog/items/{id}` |
| SKU mutability | immutable after create in this slice |

The current implementation is a transactional JPA candidate. It demonstrates durable persistence and public identity semantics but remains non-canonical until security and the remaining qualification gates are closed.

## Validation evidence

The public request boundary uses Bean Validation on create and update DTOs. Controller tests cover invalid create payloads, invalid sort fields, duplicate SKU conflicts, unknown IDs and unknown SKU lookups.

Manual validation remains as internal service/domain guard for direct service use. It is not the only public request-boundary evidence.

## Error evidence

The candidate foundation introduces a demo-local standard error response with at least:

- `timestamp`;
- `status`;
- `error`;
- `errorType`;
- `message`;
- `errorId`;
- `path`;
- `method`;
- optional `messageKey`;
- `violations` for field-level validation errors.

Covered scenarios:

| Scenario | Status | Error type |
|---|---:|---|
| invalid request body | `400` | `VALIDATION_FAILED` |
| invalid list query | `400` | `INVALID_REQUEST` |
| unknown resource ID | `404` | `RESOURCE_NOT_FOUND` |
| unknown SKU lookup | `404` | `RESOURCE_NOT_FOUND` |
| duplicate SKU | `409` | `CONFLICT` |

`correlationId`, `traceId` and `localMessage` are deferred for the candidate foundation and remain part of later observability/error-handling work.

## Application-layer and mapping evidence

The controller remains a thin HTTP adapter:

- no repository injection;
- no `EntityManager` injection;
- no transaction demarcation;
- no target-project access;
- delegates business-key normalization, conflict checks, paging, update and delete behavior to `CatalogItemService`.

The mapper stays deterministic:

- no repository dependency;
- no service dependency;
- no authorization dependency;
- no transaction dependency.

## Security evidence

The first candidate foundation uses `documented-deferred-security`.

Endpoint classification: `management`.

Intended permission vocabulary:

| Operation | Permission |
|---|---|
| list/detail/by-sku | `catalog:item:read` |
| create | `catalog:item:create` |
| update | `catalog:item:update` |
| delete | `catalog:item:delete` |

Security enforcement is not implemented in this patch. Strict security gates remain blocked until `implemented-management-security` evidence and fixtures exist.

## Gate evidence

The candidate foundation must be validated with:

- `mvn -q test`;
- `mvn -q -Pspringmaster-gates-report test`;
- one report-only gate smoke run;
- full ZIP export and export hygiene check.

Report-only findings may remain. They must not be promoted to strict by this patch.

## Remaining deferrals before canonical-reference-slice

- durable persistence/JPA repository evidence;
- Liquibase/DB migration evidence;
- implemented management security;
- OpenAPI operationId/tag/schema evidence;
- strict gate promotion;
- Catalog-demo canonical readiness review;
- target-project comparison;
- target-project delivery.

## Forensic review status after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` confirms this file as valid candidate evidence, not canonical evidence.

Review outcome:

- `CatalogItem` is a `candidate-reference-slice foundation`;
- Catalog-demo is not canonical;
- report-only findings decreased from `12` to `9` after the candidate implementation;
- the remaining G4 security warning and G5 manual-review finding are expected;
- G5 still reports legacy state because the source-based gate heuristic has not yet learned to read this evidence file as candidate state;
- request DTO exposure of the persistence-facing `Range` embeddable and direct service update validation asymmetry must be fixed before canonical promotion.

Next recommended patch: `000074_springmaster_catalog_demo_candidate_slice_alignment`.



## Gate alignment status after 000074

Patch `000074_springmaster_catalog_demo_candidate_slice_alignment` adds machine-readable evidence beside this Markdown document:

```text
PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json
```

Schema marker:

```text
springmaster.catalog-demo.candidate-evidence.v1
```

The report-only G5 readiness heuristic now reads that JSON evidence before falling back to historical `legacy-demo-seed` markers in the readiness plan. The current deterministic state is:

- `sliceState`: `candidate-reference-slice`;
- `canonicalState`: `not-canonical`;
- `securityMode`: `documented-deferred-security`;
- target comparison and target delivery remain blocked.

Expected report-only findings after `000074`: `8` total, with no `SM-G5-CATALOG-READINESS-EVIDENCE` manual-review finding while the candidate evidence remains present and classifiable.

## DTO/validation cleanup status after 000075

Patch `000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup` closes the DTO-boundary and service-validation cleanup items recorded by the forensic review.

Current evidence:

- public create/update request DTOs no longer expose the persistence-facing `Range` embeddable;
- `CatalogItemAvailabilityDTO` is the public nested availability request shape;
- `CatalogItemMapper` owns conversion from public availability DTO to internal `Range`;
- `CatalogItemValidator` validates create and update requests symmetrically at the service boundary;
- invalid availability ordering is covered by Bean Validation and service validation;
- unpaged `CatalogItemService.list()` legacy helper has been removed.

Expected report-only findings remain `8`: six positive G0 rule-source findings, one positive create-status finding and one expected G4 deferred-security warning.

## List query export/all reference status after 000092

Patch `000092_springmaster_catalogitem_list_query_export_all_reference_slice` implements the documented list-query/export-all contract in the `CatalogItem` candidate slice.

Current evidence:

- paged list and `/all` share one service-side filter/sort pipeline;
- public filters are explicit and documented (`sku`, `name`);
- paged list keeps `totalElements` and `totalPages` consistent with the filtered result set;
- `/all` returns the complete matching result set without public `page`/`size` parameters;
- empty paged and `/all` responses are covered;
- invalid paging and sort direction requests are covered by standard error-body tests;
- `PagedQuerySupport` is reused for paging validation, sort-direction validation, sort allow-list resolution, default-sort handling and stable tie-breaker comparator construction.

The slice remains `candidate-reference-slice`, not canonical. Remaining canonical blockers are unchanged unless closed by a later patch.


## Core sort-support adoption after 000094

Patch `000094_springmaster_catalogitem_use_core_paged_query_sort_support` removes the remaining demo-local sort resolution helpers from `CatalogItemService` and routes the candidate query pipeline through Core `PagedQuerySupport.stableComparator(...)`.

Current evidence:

- CatalogItem defines only its allowed public sort fields and field comparators (`sku`, `name`);
- Core resolves blank/missing `sortBy` to the default field;
- Core validates unsupported sort fields and sort directions;
- Core composes the stable `id` tie-breaker;
- paged list and `/all` continue to share the same filter/sort pipeline;
- service tests cover default sort behavior and descending all-result sorting.

The slice remains `candidate-reference-slice`, not canonical. Remaining canonical blockers are unchanged unless closed by a later patch.



## Query-Operations-Interface adoption after 000102

Patch `000102_springmaster_catalogitem_query_operations_interface_adoption` adapts the Core query-operations contract from `000101` in the CatalogItem candidate slice.

Current evidence:

- `CatalogItemService` implements `ResultSetQueryOperations<CatalogItemPagedQuery, CatalogItemAllQuery, CatalogItemCountQuery, CatalogItemListItemDTO>`;
- the fachliche query records remain in the Demo slice and are not moved into Core;
- `CatalogItemController` remains an explicit Spring MVC adapter and does not inherit generic controller mappings;
- paged list, `/all` and `/count` delegate through typed query records;
- the existing filter, sort, count and error semantics remain unchanged;
- `CatalogItemServiceTest` covers the interface-backed service contract directly.

The slice remains `candidate-reference-slice`, not canonical. Remaining canonical blockers are unchanged unless closed by a later patch.

## Persistent candidate runtime

Patch `000163_springmaster_catalogitem_persistent_candidate_runtime` replaces the in-memory maps with a transactional JPA runtime.

Current evidence:

- Spring Data CRUD repository plus a dedicated Criteria-based query repository;
- Liquibase-owned `demo_catalog_item` and tag tables;
- isolated H2 database names per Spring test ApplicationContext, with a two-context Liquibase regression test;
- shared predicates for paged, `/all` and `/count` operations;
- boundary validation of page, size, sort field, sort direction and offset overflow before JPA invocation;
- assigned opaque IDs with `persistenceVersion` lifecycle `null -> 0 -> 1`;
- create, reload, update, delete, query and OpenAPI regression coverage.

The slice remains `candidate-reference-slice`. Management security, stale-version conflict qualification, production-like MariaDB tests, strict-gate promotion and canonicalization remain deferred.

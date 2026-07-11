# CatalogItem Query Operations Interface Adoption

## Purpose

Patch `000102_springmaster_catalogitem_query_operations_interface_adoption` adapts the Core query-operations contract from `000101` in the CatalogItem candidate slice.

The goal is not to introduce generic Spring-MVC controller inheritance. The goal is to prove that a fachlicher service slice can expose the canonical query operations through typed Java contracts while keeping HTTP, security and OpenAPI details explicit at the controller boundary.

## Adopted Core contract

`CatalogItemService` implements:

```java
ResultSetQueryOperations<
        CatalogItemPagedQuery,
        CatalogItemAllQuery,
        CatalogItemCountQuery,
        CatalogItemListItemDTO>
```

The Core interfaces remain fachfrei. The concrete query types are owned by the demo slice:

```text
CatalogItemPagedQuery
CatalogItemAllQuery
CatalogItemCountQuery
```

## Query type ownership

| Query type | Operation | Contains |
|---|---|---|
| `CatalogItemPagedQuery` | paged list | `page`, `size`, `sortBy`, `sortDir`, `sku`, `name` |
| `CatalogItemAllQuery` | complete result set | `sortBy`, `sortDir`, `sku`, `name` |
| `CatalogItemCountQuery` | count-only | `sku`, `name` |

This mirrors the public HTTP contract:

- paged list allows paging, sorting and filters;
- `/all` allows sorting and filters but no paging;
- `/count` allows only count-relevant filters.

## Controller boundary

`CatalogItemController` remains an explicit Spring MVC adapter:

```text
GET /api/demo/catalog/items
GET /api/demo/catalog/items/all
GET /api/demo/catalog/items/count
```

It still owns request parameter mapping, HTTP paths and count-query-parameter rejection. The controller delegates to typed fachliche query records before calling the service.

## Service boundary

`CatalogItemService` keeps compatibility helper overloads for existing callers, but the canonical service/application contract is now the query-record based interface implementation.

The same internal predicate and sort pipeline remains in use:

- paged list and `/all` share sorting and filtering;
- count-only shares the same filter predicates;
- Core `PagedQuerySupport` still owns sort allow-list/default/tie-breaker mechanics.

## Verification

Expected verification commands:

```text
mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest
mvn -B -ntp test
```

Covered scenarios:

- service implements `ResultSetQueryOperations` with CatalogItem-owned query types;
- typed query operations return the same paged, all and count semantics as the HTTP-oriented helper overloads;
- existing list, `/all`, `/count`, create, detail, update, delete and error scenarios remain covered.

## Remaining canonical blockers

CatalogItem remains a `candidate-reference-slice`. This patch closes the interface-adoption evidence gap, not the remaining canonical blockers: durable persistence, Liquibase evidence, implemented management security, OpenAPI evidence, strict gate promotion and target-project comparison/delivery.

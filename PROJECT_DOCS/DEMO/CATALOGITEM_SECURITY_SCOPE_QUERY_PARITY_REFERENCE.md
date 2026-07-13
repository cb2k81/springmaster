# CatalogItem Security/Data-Scope Query Parity Reference

## Status

Candidate reference evidence since `000114_springmaster_query_security_scope_parity_reference`.

## Purpose

This document closes the remaining Query/List/All/Count maturity gap for security and data-scope parity.

The CatalogItem runtime is still intentionally lightweight, but the reference slice now demonstrates the required rule for secured resource queries:

```text
paged list, /all and /count must evaluate the same operation permission and data-scope predicate family before paging, sorting or DTO mapping is applied.
```

## Added reference types

| Type | Purpose |
|---|---|
| `CatalogItemQueryScope` | Framework-free resolved read permission and data-scope value object. |
| `CatalogItemScopedQueryReference` | Reference implementation proving same permission/data-scope predicate family for paged list, `/all` and `/count`. |
| `CatalogItemScopedQueryReferenceTest` | Behavioral parity tests for scoped list/all/count and denied read permission. |

## Permission evidence

The reference uses the canonical Catalog-demo read permission:

```text
catalog:item:read
```

A missing read permission stops every read query operation before rows or counts are returned.

This is intentionally modeled as a reference-level `SecurityException` instead of a Spring Security dependency. A future secured runtime slice may map the same semantic condition to `403 FORBIDDEN` through the API error contract.

## Data-scope evidence

`CatalogItemQueryScope` models a deterministic `allowedSkus` scope.

Examples:

```java
CatalogItemQueryScope.unrestrictedRead();
CatalogItemQueryScope.restrictedRead(Set.of("SKU-1", "SKU-3"));
CatalogItemQueryScope.denied();
```

The concrete SKU scope is only a compact reference predicate. Generated or target applications may use tenant, organization, ownership, app-scope, role-scope or assignment-scope predicates instead. The invariant is that all read query forms reuse the same resolved scope.

## Shared predicate family

`CatalogItemScopedQueryReference` uses one private matcher for all query operations:

```java
matchingScopedItems(source, sku, name, scope)
```

The method applies, in this order:

1. read-permission check;
2. data-scope visibility check;
3. business filter `sku`;
4. business filter `name`.

Operation-specific behavior happens only after that shared matcher:

| Operation | Additional behavior after shared matcher |
|---|---|
| paged list | stable sort, page window, DTO mapping and page metadata |
| `/all` | stable sort and DTO mapping, no paging |
| `/count` | count-only result, no sort, no paging, no DTO mapping requirement |

## Tests

`CatalogItemScopedQueryReferenceTest` proves:

* paged list, `/all` and `/count` return the same visible subset when a read scope is restricted;
* `/count` does not bypass data scope when no business filter is provided;
* denied read permission fails all three query operations consistently.

## Relationship to persistent JPA reference

Patch `000113` added the durable JPA count reference. This patch does not replace it.

The persistent rule remains:

* `count` must be repository/query-level count;
* count must not materialize entities or DTOs;
* count must not apply paging or sorting.

The security/data-scope rule added here is complementary:

* the same resolved authorization/data-scope predicates must be part of list, `/all` and `/count`;
* repository implementations must receive those predicates from the authorized application/query boundary;
* repositories must not invent authorization decisions.

## Remaining status

This patch completes the planned five-step Query/List/All/Count maturity track on reference level.

CatalogItem remains a candidate reference slice until a separate canonical-promotion decision explicitly marks it canonical and confirms all ADR and target-project comparison requirements.

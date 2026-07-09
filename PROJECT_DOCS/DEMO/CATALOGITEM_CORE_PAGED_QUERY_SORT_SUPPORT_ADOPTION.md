# CatalogItem Core Paged Query Sort Support Adoption

## Purpose

Patch `000094_springmaster_catalogitem_use_core_paged_query_sort_support` aligns the CatalogItem candidate slice with the Core query-sort helper introduced by `000093_springmaster_paged_query_support_sort_allowlist_tiebreaker`.

The patch is intentionally demo-scoped. It does not change the public HTTP contract from `000092`; it proves that the documented and implemented list-query/export-all behavior can consume the reusable Core helper.

## Implementation decision

`CatalogItemService` keeps domain-specific query knowledge local to the demo slice:

- allowed public sort fields: `sku`, `name`;
- field-specific comparators for `CatalogItem`;
- default sort field: `sku`;
- stable tie-breaker: opaque public `id`.

Core `PagedQuerySupport.stableComparator(...)` now owns the reusable mechanics:

- blank or missing `sortBy` resolves to the default field;
- unsupported `sortBy` is rejected through the common `IllegalArgumentException` path;
- blank or missing `sortDir` resolves to ascending;
- unsupported `sortDir` is rejected;
- the stable tie-breaker is appended after the primary comparator.

## Contract preservation

The public endpoints remain unchanged:

```text
GET /api/demo/catalog/items?page=&size=&sortBy=&sortDir=&sku=&name=
GET /api/demo/catalog/items/all?sortBy=&sortDir=&sku=&name=
```

Paged list and `/all` still share the same service-side filter/sort pipeline. `/all` remains unpaged at the public boundary and returns the complete matching result set.

## Verification

The patch keeps the existing CatalogItem query tests and adds service-level evidence for Core-backed default and descending sort behavior. The expected verification commands are:

```text
mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest
mvn -B -ntp test
```

## Canonical status

This patch strengthens the candidate slice but does not promote it to canonical. Remaining canonical blockers are unchanged: durable persistence, Liquibase evidence, implemented management security, OpenAPI operation evidence, strict gate promotion, target-project comparison and target-project delivery.

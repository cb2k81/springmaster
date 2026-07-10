# 000100 springmaster_catalogitem_count_reference_slice

Scope: demo

## Summary

Adds CatalogItem candidate-slice evidence for the count-only API contract.

## Changes

- Adds `GET /api/demo/catalog/items/count`.
- Returns Core `CountResponseDTO`.
- Reuses the same filter predicates as paged list and `/all`.
- Rejects paging and sorting query parameters on `/count`.
- Adds service and controller tests for unfiltered, filtered, empty and invalid count queries.
- Updates CatalogItem evidence documentation.

## Verification

- `mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest`
- `mvn -B -ntp test`
- Full ZIP export

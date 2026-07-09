# 000092 springmaster_catalogitem_list_query_export_all_reference_slice

## Scope

`demo`

## Summary

Implements executable CatalogItem candidate-slice evidence for the documented list-query/export-all contract.

## Changes

- Added `GET /api/demo/catalog/items/all` for complete result-set access.
- Added explicit `sku` and `name` filters to the paged list endpoint.
- Reused the same service-side filter/sort pipeline for paged and `/all` queries.
- Kept `totalElements` and `totalPages` consistent with the filtered result set.
- Reused `PagedQuerySupport` for paging and sort-direction validation.
- Added controller and service tests for filtered lists, `/all`, empty results and invalid paging/sort requests.
- Updated CatalogItem candidate evidence and added a dedicated reference-slice note.

## Verification

Required because this is a code patch:

```text
mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest
mvn -B -ntp test
./bin/export.sh full --zip
```

## Notes

CatalogItem remains a `candidate-reference-slice`, not a canonical reference slice. This patch only closes the list-query/export-all part of the candidate evidence.

# Changelog 000109_springmaster_query_openapi_contract_evidence

## Scope

`root`

## Summary

Adds runtime-generated OpenAPI evidence for the CatalogItem query-contract reference slice.

## Changes

- Adds `CatalogItemOpenApiQueryContractTest`.
- Verifies `/v3/api-docs` exposes the CatalogItem paged list, `/all` and `/count` operations.
- Verifies list query parameters: `page`, `size`, `sortBy`, `sortDir`, `sku`, `name`.
- Verifies `/all` query parameters: `sortBy`, `sortDir`, `sku`, `name` and no paging parameters.
- Verifies `/count` query parameters: `sku`, `name` only.
- Verifies `/count` exposes `CountResponseDTO.totalElements` in OpenAPI.
- Documents the OpenAPI query-contract evidence standard.

## Verification

- live-baseline preflight
- patch dry-run
- patch apply
- latest patch identity check
- targeted Maven test `CatalogItemOpenApiQueryContractTest`
- full Maven test
- git diff check
- full zip export

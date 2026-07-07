# Changelog: 000058_springmaster_api_query_reference_data_consistency_standard

## Type

Documentation-only.

## Summary

Resolves the first P0 consistency gap from the 000057 standard review before API contract gate tooling is implemented.

## Changes

* Added `PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md`.
* Harmonized list/query documentation to use `sortBy` as the canonical public sort field parameter.
* Marked `sort` as legacy/target-comparison vocabulary rather than a Catalog-demo or new-reference API standard.
* Harmonized `/all`, `/options` and `/reference-data` semantics across API, Demo, ADR-gap and consistency-review documentation.
* Updated Catalog-demo readiness so the first CatalogItem slice must not introduce `/all` and must use `sortBy`/`sortDir`.
* Updated version metadata to `PLATFORM_VERSION=0.13.19-foundation` and `PLATFORM_STATE_PATCH=000058_springmaster_api_query_reference_data_consistency_standard`.

## Validation

No Maven test is required because no Java, Maven, Tooling, Template, Demo implementation or target-project files are changed.

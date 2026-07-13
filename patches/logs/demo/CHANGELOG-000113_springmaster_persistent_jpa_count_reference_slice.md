# 000113 Springmaster Persistent JPA Count Reference Slice

Scope: `demo`

## Summary

Adds a CatalogItem persistent JPA query reference for paged list, complete result set and count-only operations.

## Changes

* Added `CatalogItemJpaQueryReference` using JPA Criteria queries.
* Added source-based regression tests for dedicated count-query semantics and shared predicate usage.
* Added Demo documentation for the persistent count reference slice.
* Updated Demo README and platform version metadata.

## Verification intent

* `CatalogItemJpaQueryReferenceTest`
* `CatalogItemOpenApiQueryContractTest`
* `SpringmasterQueryContractReportTest`
* full Maven test
* query-contract report smoke run
* `git diff --check`
* full export

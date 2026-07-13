# Changelog: 000114_springmaster_query_security_scope_parity_reference

## Scope

`demo`

## Summary

Adds CatalogItem security/data-scope query parity reference evidence for paged list, `/all` and `/count`.

## Changes

* Added `CatalogItemQueryScope` with `catalog:item:read` and deterministic `allowedSkus` scope modeling.
* Added `CatalogItemScopedQueryReference` as a framework-free reference showing one shared matcher for permission, data scope and business filters.
* Added `CatalogItemScopedQueryReferenceTest` for behavioral parity and denied-read checks.
* Documented completion of the five-step Query/List/All/Count maturity track at candidate-reference level.

## Verification

* live-baseline preflight
* patch dry-run and apply
* security scope source guard
* targeted `CatalogItemScopedQueryReferenceTest`
* targeted `CatalogItemJpaQueryReferenceTest`
* targeted `CatalogItemOpenApiQueryContractTest`
* targeted `SpringmasterQueryContractReportTest`
* full Maven test
* git diff check
* full export

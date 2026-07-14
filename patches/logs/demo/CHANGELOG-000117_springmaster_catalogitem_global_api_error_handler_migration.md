# Changelog: 000117_springmaster_catalogitem_global_api_error_handler_migration

Scope: `demo`

## Summary

Migrates the CatalogItem candidate reference slice to the Core-owned global API error handler introduced in `000116`.

## Changes

* Removed CatalogItem controller-local `@ExceptionHandler` methods.
* Replaced CatalogItem-local not-found exception usage with `ResourceNotFoundException`.
* Preserved CatalogItem domain message keys for not-found and duplicate-SKU conflicts.
* Removed local CatalogItem error DTOs and local not-found exception from the Demo slice.
* Added CatalogItem migration documentation.
* Extended CatalogItem controller regression tests with global handler message-key and correlation-ID evidence.

## Verification

Expected runner verification:

* live-baseline preflight;
* patch dry-run;
* patch apply;
* global error handler migration source guard;
* `CatalogItemControllerTest`;
* `CatalogItemOpenApiQueryContractTest`;
* `SpringmasterQueryContractReportTest`;
* full Maven test;
* `git diff --check`;
* full ZIP export.

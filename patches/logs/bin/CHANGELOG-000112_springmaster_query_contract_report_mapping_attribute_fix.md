# 000112_springmaster_query_contract_report_mapping_attribute_fix

Scope: bin

## Summary

Repair the query contract report source parser so Spring MVC mapping annotations using named attributes are resolved correctly.

The OpenAPI media-type repair changed CatalogItem query endpoint annotations from direct literal mappings to forms such as `@GetMapping(path = "/all", produces = MediaType.APPLICATION_JSON_VALUE)`. The report tooling must treat `path` and `value` attributes as the canonical mapping suffix instead of reporting `/all` and `/count` as the controller base path.

## Verification

- live-baseline preflight against the current applied `000111` state
- patch dry-run
- patch apply
- query-contract report smoke run with deterministic timestamp
- targeted Maven test `CatalogItemOpenApiQueryContractTest`
- targeted Maven test `SpringmasterQueryContractReportTest`
- full Maven test
- git diff check
- full export

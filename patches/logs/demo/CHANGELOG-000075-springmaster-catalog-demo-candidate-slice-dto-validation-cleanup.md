# 000075 - springmaster_catalog_demo_candidate_slice_dto_validation_cleanup

## Scope

Demo-code cleanup for the Springmaster Catalog-demo `CatalogItem` candidate-reference-slice.

## Changes

- Added `CatalogItemAvailabilityDTO` as public nested request DTO.
- Removed public request DTO dependency on persistence-facing `Range`.
- Kept `Range` internal to entity/persistence mapping only.
- Added update validation symmetry in `CatalogItemService` and `CatalogItemValidator`.
- Removed unpaged `CatalogItemService.list()` helper.
- Extended mapper, validator, service and controller tests.
- Updated candidate evidence, readiness documentation and version policy.

## Validation expectation

- `mvn -q test`
- `mvn -q -Pspringmaster-gates-report test`
- report-only gate smoke with expected `8` findings
- full ZIP export and export hygiene check

## Version

- `PLATFORM_VERSION=0.13.36-foundation`
- `PLATFORM_DEMO_VERSION=0.2.3`
- `PLATFORM_STATE_PATCH=000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup`

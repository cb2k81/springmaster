# CHANGELOG 000072 - springmaster catalog demo catalogitem candidate slice foundation

## Scope

Demo code.

## Type

Code-/Demo-Patch.

## Summary

Introduces the first executable Springmaster Catalog-demo `CatalogItem` `candidate-reference-slice` foundation.

## Added

- `CatalogItemUpdateDTO` for full update requests.
- `CatalogItemListItemDTO` for paged list responses.
- Demo-local standard error response DTOs:
  - `CatalogApiErrorResponse`
  - `CatalogApiViolation`
- `CatalogItemNotFoundException` for resource lookup failures.
- `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md`.

## Changed

- `CatalogItemController` now exposes:
  - `GET /api/demo/catalog/items?page=&size=&sortBy=&sortDir=`;
  - `GET /api/demo/catalog/items/{id}`;
  - `GET /api/demo/catalog/items/by-sku/{sku}`;
  - `POST /api/demo/catalog/items` with `Location` based on opaque `id`;
  - `PUT /api/demo/catalog/items/{id}`;
  - bodyless `DELETE /api/demo/catalog/items/{id}`.
- `CatalogItemCreateDTO` now carries Bean Validation annotations.
- `CatalogItemDTO` now exposes `persistenceVersion` evidence.
- `CatalogItemMapper` maps detail, list-item and update shapes.
- `CatalogItemService` keeps in-memory storage behind service boundaries and indexes by opaque `id` and business key `sku`.
- Demo/API tests cover the candidate endpoint, DTO, validation, error, status-code, update and delete behavior.
- Demo/readiness/tooling/planning documentation records the candidate-slice evidence and remaining deferrals.

## Validation expectation

This patch requires technical validation:

- shell/Python syntax checks for existing tooling;
- `mvn -q test`;
- `mvn -q -Pspringmaster-gates-report test`;
- report-only gate smoke;
- full ZIP export and export hygiene.

## Version

- `PLATFORM_VERSION=0.13.33-foundation`
- `PLATFORM_DEMO_VERSION=0.2.2`
- `PLATFORM_STATE_PATCH=000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation`

# CatalogItem Detail/Lookup Contract Report Reference

## Purpose

Patch `000118_springmaster_detail_lookup_contract_report` adds the first report-only Detail/Lookup contract evidence for the CatalogItem candidate reference slice.

This closes the read-by-one gap left after Query/List/All/Count and Global API Error Contract maturity.

## Covered endpoints

```text
GET /api/demo/catalog/items/{id}
GET /api/demo/catalog/items/by-sku/{sku}
```

## Evidence

The CatalogItem reference demonstrates:

* canonical opaque-id detail lookup through `/{id}`;
* unique business-key lookup through `/by-sku/{sku}`;
* `CatalogItemDTO` response evidence;
* `404 RESOURCE_NOT_FOUND` through the global Core error handler;
* CatalogItem-specific message key `catalog.item.not-found`;
* create `Location` header compatibility with the detail endpoint;
* OpenAPI route and path-variable evidence;
* deterministic report output with zero findings.

## Boundaries

This patch does not introduce Write API gates, request-validation/OpenAPI required-field gates, command endpoint gates or strict gate promotion.

The report remains report-only. It is intended to make the current reference state machine-readable before the next Write API contract patch.

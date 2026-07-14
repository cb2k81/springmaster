# Detail/Lookup Contract Gate Report

## Purpose

The Detail/Lookup Contract Gate Report defines the report-only validation model for single-resource detail endpoints and unique alternate-key lookup endpoints.

It complements the existing Query Contract Gate Report. Query covers collection access through paged list, `/all` and `/count`. Detail/Lookup covers direct object access after navigation, create-location follow-up, reload/deep-link use cases and business-key lookup use cases.

## Canonical endpoint family

For management APIs the canonical read-by-one family is:

```text
GET /api/<domain>/<resources>/{id}
GET /api/<domain>/<resources>/by-<key>/{value}
```

Rules:

* `/{id}` uses the public opaque external resource id.
* `/by-<key>/{value}` is allowed only for a unique alternate key.
* The public contract must not use `findOne`, `findFirst`, `findAny` or repository vocabulary.
* Unknown ids and unknown alternate keys must return the global API error envelope with `404 RESOURCE_NOT_FOUND`.
* A create response `Location` header must point to the canonical detail endpoint.
* Violated alternate-key uniqueness is a conflict condition and must be represented as `409 CONFLICT` when a persistent runtime can observe that state.

## Report-only mode

The MVP report is intentionally report-only. It creates a deterministic JSON artifact, but does not yet fail the build outside the targeted regression tests.

Default output:

```text
reports/api/detail-lookup-contract-gate-report.json
```

Schema version:

```text
springmaster.detail-lookup-contract-gate-report.v1
```

## Finding families

| Finding id | Severity | Meaning |
|---|---|---|
| `DTL-GATE-001` | error | Required source, test or standard input is missing. |
| `DTL-DETAIL-001` | error | Canonical detail endpoint path or `id` path variable is missing. |
| `DTL-DETAIL-002` | warning | Detail endpoint lacks DTO response evidence. |
| `DTL-LOOKUP-001` | error | Canonical alternate-key lookup path or path variable is missing. |
| `DTL-LOOKUP-002` | warning | Alternate-key lookup lacks DTO response evidence. |
| `DTL-NOTFOUND-001` | error | Not-found behavior does not show global `RESOURCE_NOT_FOUND` evidence. |
| `DTL-SERVICE-001` | error | Service-level `findById` evidence is missing. |
| `DTL-SERVICE-002` | error | Service-level unique alternate-key lookup evidence is missing. |
| `DTL-MOCKMVC-001` | warning | MockMvc evidence for positive or negative detail/lookup behavior is missing. |
| `DTL-OPENAPI-001` | warning | OpenAPI evidence for detail/lookup routes is missing. |

## CatalogItem reference evidence

The CatalogItem candidate reference slice is the first golden reference for the report:

```text
GET /api/demo/catalog/items/{id}
GET /api/demo/catalog/items/by-sku/{sku}
```

The current reference evidence includes:

* source-based detail and alternate-key path analysis;
* service-level `Optional<CatalogItemDTO>` lookup evidence;
* unique SKU lookup evidence through the service SKU index;
* global `ResourceNotFoundException` handling with `catalog.item.not-found`;
* MockMvc evidence for positive id lookup, positive SKU lookup, id not-found, SKU not-found and create-Location detail follow-up;
* OpenAPI evidence for route presence, path variables and response schemas;
* deterministic golden JSON fixture for the report output.

## Promotion rules

The report can be promoted from report-only to strict gate only after the following conditions hold:

* at least Detail/Lookup and Write reports exist with golden fixtures;
* generated-slice adoption criteria are defined;
* current reference projects have a migration path for report findings;
* non-CatalogItem resources can either pass the same scanner or are explicitly out of scope.

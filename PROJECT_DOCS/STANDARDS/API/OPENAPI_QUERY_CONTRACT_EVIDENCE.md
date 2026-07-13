# OpenAPI Query Contract Evidence

Reference evidence since patch `000109_springmaster_query_openapi_contract_evidence`.

This document defines the Springmaster OpenAPI evidence expectations for query-style management resources. It complements the source-based Query Contract Report from `000107`/`000108` with a runtime-generated OpenAPI proof for the CatalogItem candidate reference slice.

## Purpose

The OpenAPI evidence exists to verify that the public HTTP contract exposes the same query vocabulary that the Java source and query report claim:

```text
GET /api/<domain>/<resources>
GET /api/<domain>/<resources>/all
GET /api/<domain>/<resources>/count
```

The evidence is especially relevant for generated applications because OpenAPI is the external contract consumed by clients, frontends, SDKs and documentation tooling.

## CatalogItem evidence target

The first evidence target is the CatalogItem candidate reference slice:

```text
GET /api/demo/catalog/items
GET /api/demo/catalog/items/all
GET /api/demo/catalog/items/count
```

The Spring Boot test `CatalogItemOpenApiQueryContractTest` loads `/api-docs` through MockMvc and asserts the generated OpenAPI document. The configured Springmaster OpenAPI JSON endpoint is `/api-docs` because `src/main/resources/application.yml` sets `springdoc.api-docs.path=/api-docs`; the Springdoc default `/v3/api-docs` is not the project-local contract.

## Required query parameter evidence

The paged list operation must expose the canonical paging, sorting and filter vocabulary:

```text
page
size
sortBy
sortDir
sku
name
```

The complete-result-set `/all` operation must expose sorting and the same business filter family without paging semantics:

```text
sortBy
sortDir
sku
name
```

The count-only operation must expose only the shared business filter family:

```text
sku
name
```

The count-only operation must not expose:

```text
page
size
sortBy
sortDir
arg0
arg1
```

## Required response evidence

Each query operation must expose an `application/json` response schema in the OpenAPI document.

The count-only operation must expose the Springmaster count response contract:

```text
CountResponseDTO.totalElements
```

The test intentionally asserts the `CountResponseDTO` schema reference and the `totalElements` property because this is the smallest stable OpenAPI proof for `/count` parity.

## Boundaries

This evidence does not replace runtime behavior tests. MockMvc tests still prove status codes, response bodies, filtered totals and invalid-parameter behavior.

This evidence also does not promote strict target-project enforcement yet. It is a deterministic reference proof for Springmaster and a prerequisite for later generated-application comparison.

## Relationship to query report

The Query Contract Report remains source-based in its current MVP. OpenAPI evidence is separate so that failures can distinguish between:

- Java source/query-operation drift;
- generated OpenAPI drift;
- runtime behavior drift.

Future report versions may ingest OpenAPI directly. Until then, this test is the canonical OpenAPI proof for the CatalogItem query-contract reference slice.

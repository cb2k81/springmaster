# Changelog 000111 - CatalogItem OpenAPI JSON Media Type Fix

## Ziel

Repariert die OpenAPI-Query-Contract-Evidenz nach `000109`/`000110`, indem die CatalogItem Query-Endpunkte explizit `application/json` als Response-Media-Type deklarieren.

## Änderungen

- `CatalogItemController` deklariert `produces = MediaType.APPLICATION_JSON_VALUE` für:
  - `GET /api/demo/catalog/items`
  - `GET /api/demo/catalog/items/all`
  - `GET /api/demo/catalog/items/count`

## Verifikation

- Live-Baseline-Hash-Preflight gegen den angewendeten Stand nach `000110`.
- Dry-run und Apply über Patchsystem.
- Query Contract Report Smoke.
- Targeted OpenAPI Query Contract Test.
- Targeted Query Report Fixture Test.
- Full Maven Test.
- `git diff --check`.
- Full ZIP Export.

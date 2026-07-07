# Demo Catalog API Controller

Patch `000020_springmaster_demo_catalog_api_controller` ergänzt die erste REST-API für die Demo-Domäne `catalog`.

## Ziel

Die Demo-Domäne soll nicht nur durch Unit-Tests, sondern auch über eine Spring-Web-API verwendbar sein. Dadurch wird die Kombination aus App-Scan, Demo-Service, DTOs, Core-Validierung und Fehlerabbildung im Masterprojekt realistisch geprüft.

## API

Basis-Pfad:

```text
/api/demo/catalog/items
```

Endpunkte:

| Methode | Pfad | Bedeutung |
|---|---|---|
| `GET` | `/api/demo/catalog/items` | listet alle Demo-Katalogeinträge |
| `POST` | `/api/demo/catalog/items` | erzeugt einen neuen Demo-Katalogeintrag |
| `GET` | `/api/demo/catalog/items/{sku}` | sucht einen Demo-Katalogeintrag per SKU |

## Fehlerabbildung

| Ursache | HTTP-Status | Fehlercode |
|---|---:|---|
| Core-/Demo-Validierungsfehler | `400` | `VALIDATION_FAILED` |
| bereits vorhandene SKU | `409` | `ENTITY_ALREADY_EXISTS` |
| unbekannte SKU | `404` | kein Body |

## Bewusste Abgrenzung

Dieser Patch ergänzt keine Persistenz-Runtime:

* kein Spring Data JPA
* keine Repository-Schicht
* keine DataSource-Konfiguration
* keine Liquibase-Demo-Tabelle

Die API verwendet weiterhin den bewusst einfachen In-Memory-Service `CatalogItemService`.

## Tests

`CatalogItemControllerTest` prüft:

* Listen vorhandener Katalogeinträge
* Erzeugen per `POST`
* Suchen per SKU
* `404` für unbekannte SKU
* `400` bei Validierungsfehlern
* `409` bei Duplicate-SKU

## Fix in 000021

Patch `000021_springmaster_demo_catalog_api_pathvariable_fix` korrigiert die Pfadvariablenbindung in `CatalogItemController`.

Der Endpunkt `GET /api/demo/catalog/items/{sku}` verwendet nun explizit `@PathVariable("sku")`. Dadurch ist die Controller-Methode nicht mehr davon abhängig, dass Java-Parameter-Namen über Compiler-Metadaten verfügbar sind.


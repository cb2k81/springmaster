# 000021 - springmaster demo catalog api pathvariable fix

## Scope

`demo`

## Motivation

Patch `000020_springmaster_demo_catalog_api_controller` wurde angewendet, die Maven-Pflichtvalidierung zeigte jedoch Fehler in `CatalogItemControllerTest` für `GET /api/demo/catalog/items/{sku}`.

Spring konnte den Namen der Pfadvariable nicht aus Parameter-Metadaten ableiten.

## Änderungen

* `CatalogItemController.findBySku(...)` bindet die Pfadvariable nun explizit mit `@PathVariable("sku")`.
* Demo-Version wird auf `0.2.1` erhöht.
* Gesamtversion wird auf `0.5.1-foundation` erhöht.
* Demo- und Versionierungsdokumentation wurden aktualisiert.

## Validierung

Für diesen Patch ist `mvn test` verpflichtend, da Java-Code betroffen ist.

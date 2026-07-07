# CHANGELOG 000019 – Springmaster Demo Catalog Validation Fix

## Zweck

Behebt die Validierungsfehler aus dem ersten Demo-Catalog-Code-Slice `000017`.

Die Patchnummer `000018` ist im lokalen Patch-Archiv bereits durch eine unveränderte Wiederanwendung des `000017`-Archivs belegt. Der eigentliche Fix wird daher als `000019` geliefert.

## Änderungen

* `CatalogItemService` verwendet in der Duplicate-SKU-Fehlermeldung den fachlichen Begriff `SKU`.
* `CatalogItemServiceSpringContextTest` lädt `SpringmasterApplication` explizit.
* `platform/versions/platform.env` wird auf `PLATFORM_VERSION=0.4.1-foundation` und `PLATFORM_DEMO_VERSION=0.1.1` aktualisiert.
* Demo- und Versionierungsdokumentation werden um den Validierungsfix ergänzt.

## Validierung

Dieser Patch ist ein Code-Fix-Patch. `mvn test` ist verpflichtend.

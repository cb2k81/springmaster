# Changelog 000017 – Springmaster Demo Catalog Basic Domain

## Zweck

Einführung der ersten minimalen Demo-Domäne `catalog` unter `de.cocondo.platform.demo.catalog`.

## Änderungen

* Neue Demo-Domain-Klasse `CatalogItem` auf Basis von `DomainEntity`.
* Neue Create-/Output-DTOs.
* Neuer Mapper, Validator und In-Memory-Service.
* Tests für Domain, Validator, Mapper, Service und Spring-Component-Scan.
* Neue Demo-Dokumentation unter `PROJECT_DOCS/DEMO/**`.
* Erhöhung von `PLATFORM_DEMO_VERSION` auf `0.1.0`.
* Erhöhung von `PLATFORM_VERSION` auf `0.4.0-foundation`.

## Bewusste Abgrenzung

* Keine Spring-Data-JPA-Repositories.
* Keine DataSource-Konfiguration.
* Keine Liquibase-Demo-Changesets.
* Kein REST-Controller.
* Keine Zielprojekt-Update-Mechanik.

## Validierung

Pflichtvalidierung für diesen Code-Patch:

```bash
mvn test
```

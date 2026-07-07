# 000020 - Springmaster Demo Catalog API Controller

## Typ

Demo-Code-Patch.

## Änderungen

* ergänzt `CatalogItemController` unter `de.cocondo.platform.demo.catalog.api`
* ergänzt Controller-Tests mit MockMvc
* dokumentiert die Demo-Catalog-REST-API
* erhöht `PLATFORM_VERSION` auf `0.5.0-foundation`
* erhöht `PLATFORM_DEMO_VERSION` auf `0.2.0`
* setzt `PLATFORM_STATE_PATCH` auf `000020_springmaster_demo_catalog_api_controller`

## Bewusste Abgrenzung

* keine Spring-Data-JPA-Aktivierung
* keine Repository-Schicht
* keine DataSource-Konfiguration
* keine Liquibase-Demo-Tabelle
* keine Target-Update-Mechanik

## Validierung

Pflichtvalidierung nach Anwendung:

```bash
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
mvn -q test
./bin/export.sh full --zip
```

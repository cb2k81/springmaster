# 000039 - Springmaster Core DTO/List/Metadata Foundation

## Scope

core

## Ziel

Erster Code-Slice aus der IDM-System-Core-Gap-Inventarisierung nach `000038`.

## Änderungen

- DTO-Verträge und DTO-Implementierungen unter `de.cocondo.system.dto` ergänzt.
- Metadata-DTO/Payload-Verträge unter `de.cocondo.system.entity.metadata` ergänzt.
- Paging-Support und PagedResponse-Factory unter `de.cocondo.system.list` ergänzt.
- `DomainMetadataSupportMapper` als dependency-armer Metadata-Mapper und Erweiterungspunkt ergänzt.
- `spring-data-commons` als minimale Dependency für `Page`/`Sort` ergänzt.
- Core-Dokumentation, Gap-Inventar und Version Policy aktualisiert.
- Unit-Tests für DTO-, Metadata-, Paging- und Mapper-Verträge ergänzt.

## Bewusst nicht enthalten

- Keine IDM-Zielprojektänderung.
- Keine Migration von IDM-Imports.
- Keine Löschung von `de.cocondo.app.system/**`.
- Keine Security/JWT-Übernahme.
- Keine HTTP/Web-Konfiguration.
- Keine Event-Persistenz.
- Keine Repositories.
- Keine Liquibase-/Schemaänderungen.
- Keine persistenznahen Metadata-Entities oder Services.

## Validierung

Erforderlich beim Anwenden:

```bash
mvn test
./bin/export.sh full --zip
```

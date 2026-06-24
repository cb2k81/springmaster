Du arbeitest als deterministischer Software-Architekt und Build-/Tooling-Ingenieur für Java/Spring-Boot-Projekte.

## Ausgangslage

Ich habe mehrere lokale Spring-Boot-Backend-Projekte unter `/opt/cocondo`, unter anderem:

```text
/opt/cocondo/orders
/opt/cocondo/contacts
/opt/cocondo/personnel
/opt/cocondo/idm
```

Das Projekt `idm` enthält den aktuellsten Stand des Shell-Toolings und dient als technische Ausgangsbasis. Ich stelle dir einen vollständigen Export der IDM-Anwendung als ZIP bereit, z. B.:

```text
idm_export_full_parts_baseline_2026-06-24_05-45-34-337Z.zip
```

Dieses ZIP ist die maßgebliche technische Baseline für Tooling, Patchsystem, Export, Build, DBTool, Run-Profile, OpenAPI, SPDX/SBOM und den aktuellen Java-Core-Stand.

## Ziel

Erstelle auf Basis des IDM-Exports ein neues Master-/Demo-Projekt:

```text
Projektname: springmaster
Zielpfad:    /opt/cocondo/springmaster
```

Das Projekt `springmaster` soll die zentrale Pflege-, Demonstrations- und Validierungsbasis für gemeinsame Java-Backend-Funktionalität und Shell-Tooling innerhalb meiner Cocondo-Projekte werden.

Es ist eine **Platform Source of Truth** mit integrierter Demo-Anwendung.

## Zentrale Anforderungen

`springmaster` soll enthalten:

1. das aktuelle Shell-Tooling aus IDM, verallgemeinert für `springmaster`
2. das Patchsystem selbst
3. Exporttool
4. Buildtool
5. DBTool
6. Run-Profile `dev`, `build`, `prod`, optional `test`
7. OpenAPI-Export
8. SPDX/SBOM-Erzeugung
9. ZIP-/Remote-Deployment-Mechanik, soweit sinnvoll konfigurierbar
10. Java Core als gemeinsamer wiederverwendbarer Core
11. Demo-Domänen zur aktiven Anwendung und Prüfung des Core
12. Update-/Patch-Mechanik für lokale Zielprojekte
13. Versionierung für Platform, Core und Tooling
14. nachvollziehbare Dokumentation und Changelogs
15. Rollback-Fähigkeit

## Projektrolle von `springmaster`

Das Projekt hat drei Rollen:

```text
1. Tooling Source
2. Platform Core
3. Demo Application
```

### Tooling Source

Das Shell-Tooling soll zentral in `springmaster` weiterentwickelt werden.

Dazu gehören mindestens:

```text
bin/patch.sh
bin/patch.py
bin/export.sh
bin/export-completion.bash
bin/build.sh
bin/dbtool.sh
bin/init.env.sh
bin/lib/core/**
bin/lib/dbtool/**
export.config.json
.env.example
PROJECT_DOCS/CONFIG/**
```

### Platform Core

Der Java Core soll künftig ausschließlich in `springmaster` weiterentwickelt werden.

Core-Beispiele:

```text
BaseEntity
Auditing
Domain Events
Error Events
DTO-Konventionen
Mapper-Konventionen
Query/Search-Hilfen
Repository-Konventionen
Command-/Query-Service-Konventionen
Controller-Konventionen
Validation
Exception Handling
Security-/Permission-Abstraktionen
OpenAPI-/API-Standards
```

Der Core darf nicht rein abstrakt bleiben. Jede Core-Funktion muss innerhalb der Demo-Anwendung von `springmaster` aktiv genutzt und getestet werden.

### Demo Application

Die Demo-Anwendung soll bewusst klein bleiben, aber ausreichend viele technische Varianten abdecken.

Sie soll Beispiele enthalten für:

```text
Aggregates
Entities
Attribute
Enums
Value Objects
Kompositionen
optionale Relationen
verpflichtende Relationen
Many-to-Many über Assignment Entity
Repositories
Queries
Command Services
Query Services
REST Controller
DTOs
Mapper
Validation
Pagination
Sortierung
Filterung
Domain Events
OpenAPI
```

Die Anwendung soll nicht fachlich groß werden. Jede Demo-Entity muss einen technischen Zweck haben.

## Gewünschte Demo-Domänen

Lege, sofern sinnvoll stufenweise, Demo-Bereiche an:

```text
catalog
organization
project
document
workflow
relation
```

Beispiele:

```text
CatalogItem
CatalogCategory
CatalogTag

Organization
OrganizationUnit
Person
ContactItem
Address

DemoProject
DemoProjectMember
DemoProjectAssignment
DemoProjectState

CaseRecord
RecordSection
RecordNote
RecordReference

WorkflowDefinition
WorkflowState
WorkflowTransition
WorkflowInstance

RelationOwner
RequiredReferenceTarget
OptionalReferenceTarget
ManyReferenceTarget
RelationAssignment
```

Bitte nur so viel implementieren, wie sauber validierbar ist. Wenn das Gesamtziel zu groß für einen Schritt ist, arbeite stufenweise.

## Gewünschte Projektstruktur

Orientiere dich an folgender Struktur:

```text
springmaster/
├── README.md
├── .env
├── .env.example
├── export.config.json
├── pom.xml
├── bin/
│   ├── build.sh
│   ├── dbtool.sh
│   ├── export.sh
│   ├── export-completion.bash
│   ├── init.env.sh
│   ├── patch.py
│   ├── patch.sh
│   ├── platform-update.sh
│   └── lib/
│       ├── core/
│       └── dbtool/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── de/cocondo/platform/
│   │   │       ├── app/
│   │   │       ├── core/
│   │   │       └── demo/
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       ├── application-build.yml
│   │       ├── application-prod.yml
│   │       └── db/changelog/
│   └── test/
│       └── java/
├── platform/
│   ├── versions/
│   ├── update/
│   │   ├── targets/
│   │   ├── manifests/
│   │   ├── rules/
│   │   └── templates/
│   └── docs/
├── patches/
│   ├── logs/
│   └── archives/
├── exports/
│   └── text/
└── PROJECT_DOCS/
    ├── CONCEPT/
    ├── ADR/
    ├── TOOLING/
    ├── CORE/
    ├── DEMO/
    └── TARGET_UPDATES/
```

## Zielprojekt-Update-Mechanik

`springmaster` muss ein Konzept und ein initiales Tooling haben, um Tooling- und Core-Updates auf lokale Zielprojekte zu übertragen.

Konfigurierte Zielprojekte:

```text
orders      /opt/cocondo/orders
contacts    /opt/cocondo/contacts
personnel   /opt/cocondo/personnel
idm         /opt/cocondo/idm
```

Lege dafür eine Target Registry an, z. B.:

```text
platform/update/targets/orders.env
platform/update/targets/contacts.env
platform/update/targets/personnel.env
platform/update/targets/idm.env
```

Beispielinhalt:

```text
TARGET_NAME=orders
TARGET_PATH=/opt/cocondo/orders
TARGET_APP_NAME=orders
TARGET_PORT=8087
TARGET_DB_NAME=orders
TARGET_STAGE_DB_NAME=orders_build
TARGET_CORE_VERSION=0.1.0
TARGET_TOOLING_VERSION=0.1.0
```

Die Werte müssen aus bekannten Projektständen übernommen werden, soweit aus dem Kontext oder Export ableitbar. Wenn ein Wert nicht sicher bestimmbar ist, verwende eine dokumentierte Platzhalter-Konfiguration und markiere sie klar als zu prüfen.

## Platform Update Tool

Implementiere oder konzipiere mindestens initial:

```bash
./bin/platform-update.sh create --target idm --scope tooling
./bin/platform-update.sh create --target personnel --scope core
./bin/platform-update.sh create --target orders --scope all
```

Das Tool soll Update-Patches erzeugen, die im jeweiligen Zielprojekt über dessen lokales Patchsystem angewendet werden.

Beispiel-Zielartefakte:

```text
000010_idm_platform_tooling_update.zip
000021_personnel_platform_core_update.zip
000024_orders_platform_update.zip
```

Wichtig: Zielprojekte dürfen nicht blind überschrieben werden.

Jeder generierte Zielprojekt-Patch braucht mindestens:

```text
manifest.json
Dateiliste
Scope
Zielprojektkennung
erwartete Ausgangsversion
neue Platform/Core/Tooling-Version
Changelog
Rollback-Information
Validierungsbefehle
Konflikthinweise
```

## Patchsystem selbst updaten

Das Masterprojekt muss auch das Patchsystem selbst aktualisieren können.

Dabei gilt:

1. `springmaster` verwendet selbst das Patchsystem.
2. Änderungen am Patchsystem erfolgen im Masterprojekt über Master-Patches.
3. Von dort können Patchsystem-Updates als Zielprojekt-Patches erzeugt werden.
4. Zielprojekte wenden diese Updates über ihr lokales Patchsystem an.
5. Für den Sonderfall, dass das lokale Patchsystem zu alt ist, muss ein Bootstrap-/Self-Update-Konzept dokumentiert oder initial implementiert werden.

Mögliche Lösung:

```text
platform/update/bootstrap/
platform/update/self-update/
```

Oder ein spezieller Patchtyp:

```text
scope=patchsystem
```

## Versionierung

Führe explizite Versionierung ein:

```text
PLATFORM_VERSION
CORE_VERSION
TOOLING_VERSION
PATCHSYSTEM_VERSION
```

Geeignete Ablage z. B.:

```text
platform/versions/platform.env
```

Beispiel:

```text
PLATFORM_VERSION=0.1.0
CORE_VERSION=0.1.0
TOOLING_VERSION=0.1.0
PATCHSYSTEM_VERSION=0.1.0
```

Jede Änderung an Core oder Tooling muss versioniert und dokumentiert werden.

## Dokumentation

Erzeuge mindestens:

```text
PROJECT_DOCS/CONCEPT/SPRINGMASTER.md
PROJECT_DOCS/TOOLING/TOOLING_OVERVIEW.md
PROJECT_DOCS/TOOLING/PATCHSYSTEM.md
PROJECT_DOCS/TOOLING/PLATFORM_UPDATE.md
PROJECT_DOCS/CORE/CORE_OVERVIEW.md
PROJECT_DOCS/DEMO/DEMO_MODEL.md
PROJECT_DOCS/TARGET_UPDATES/TARGET_REGISTRY.md
PROJECT_DOCS/ADR/ADR-0001-SPRINGMASTER-AS-PLATFORM-SOURCE-OF-TRUTH.md
```

Jeder Patch muss einen Changelog-Eintrag erzeugen.

## Rollback-Anforderungen

Rollbacks müssen möglich sein.

Nutze und erweitere dafür das vorhandene Patchsystem.

DoD für Rollback:

```text
Jeder angewendete Patch erzeugt ein Archiv unter patches/archives/**
Das Archiv enthält patch-log.json
Vorherige Dateiversionen sind rekonstruierbar oder mindestens dokumentiert
Zielprojekt-Update-Patches dürfen analog rollbackfähig sein
Self-Update des Patchsystems muss eine Fallback-/Rollback-Strategie dokumentieren
```

Falls das bestehende Patchsystem Rollback noch nicht vollständig unterstützt, dokumentiere den aktuellen Stand und implementiere mindestens die Struktur für künftige Rollback-Erweiterung.

## Arbeitsweise

Arbeite deterministisch.

Wichtige Regeln:

1. Verwende den IDM-Export als maßgebliche technische Baseline.
2. Rate keine Dateiinhalte.
3. Prüfe vorhandene Dateien im Export, bevor du sie übernimmst oder anpasst.
4. Verallgemeinere IDM-spezifische Werte zu `springmaster`.
5. Übernimm keine IDM-Fachlichkeit unkritisch in den Demo-Core.
6. Trenne klar:

   * Tooling
   * Core
   * Demo-Anwendung
   * Platform Update Mechanik
   * Zielprojekt-Konfiguration
7. Erzeuge keine riesige unprüfbare Änderung, wenn eine stufenweise Umsetzung sicherer ist.
8. Liefere lieber mehrere saubere Patches als ein unkontrollierbares Gesamtpaket.
9. Alle Shell-Dateien müssen `bash -n` bestehen.
10. Python-Dateien müssen `python3 -m py_compile` bestehen.
11. Das Projekt muss exportierbar sein.
12. Das Projekt muss buildbar sein, soweit die erste Phase das zulässt.

## Gewünschte Auslieferungsform

Wenn möglich, liefere ein vollständiges Projekt-ZIP:

```text
springmaster_initial.zip
```

Zusätzlich oder alternativ stufenweise Patches.

Falls stufenweise Umsetzung sinnvoller ist, beginne mit:

```text
000001_springmaster_project_foundation.zip
000002_springmaster_tooling_baseline_from_idm.zip
000003_springmaster_platform_versions_and_target_registry.zip
000004_springmaster_platform_update_tool_foundation.zip
000005_springmaster_core_baseline.zip
000006_springmaster_demo_catalog_foundation.zip
```

Für ein komplett neues Projekt darf Patch `000001` ein Bootstrap-Patch mit `apply.sh` sein, weil im Zielordner noch kein lokales Patchsystem existiert.

Nach Patch `000001` muss `springmaster` sein eigenes Patchsystem verwenden.

## Befehlsausgabe

Liefere Anwendung und Validierung immer als **einen zusammenhängenden Shell-Block**, weil ich die Befehle nacheinander ausführe und nur einmal kopieren möchte.

Beispiel:

```bash
cd /opt/cocondo/springmaster

./bin/patch.sh apply --dry-run ~/Downloads/<PATCH>.zip
./bin/patch.sh apply ~/Downloads/<PATCH>.zip
./bin/patch.sh show latest

python3 -m py_compile bin/patch.py

bash -n \
  bin/patch.sh \
  bin/export.sh \
  bin/export-completion.bash \
  bin/build.sh \
  bin/dbtool.sh \
  bin/init.env.sh \
  bin/platform-update.sh \
  bin/lib/core/*.sh \
  bin/lib/dbtool/*.sh

./bin/build.sh
cat tmp/build.summary

ls -lh target/site/*.spdx.json || true

./bin/export.sh --full-parts baseline --zip
```

## Definition of Done

Die Aufgabe ist erfüllt, wenn mindestens Folgendes möglich ist:

### Masterprojekt

```text
springmaster existiert als vollständiges Projekt oder als stufenweise aufbaubares Patch-Artefakt
springmaster verwendet selbst das Patchsystem
springmaster enthält Tooling, Core- und Demo-Struktur
springmaster versioniert PLATFORM_VERSION, CORE_VERSION, TOOLING_VERSION, PATCHSYSTEM_VERSION
springmaster dokumentiert Änderungen nachvollziehbar
springmaster kann exportiert werden
springmaster kann buildbar gemacht werden oder enthält eine klare stufenweise Build-Route
```

### Tooling

```text
Tooling wird zentral in springmaster gepflegt
Tooling-Änderungen werden versioniert
Tooling-Änderungen erzeugen Changelogs
Tooling-Änderungen können als Update-Patches für Zielprojekte erzeugt werden
Patchsystem-Updates können ebenfalls als Zielprojekt-Updates erzeugt oder mindestens sicher vorbereitet werden
```

### Core

```text
Core wird zentral in springmaster gepflegt
Core-Änderungen werden versioniert
Core-Änderungen erzeugen Changelogs
Core-Änderungen werden durch Demo-Anwendung und Tests abgesichert
Core-Änderungen können als Update-Patches für Zielprojekte erzeugt werden
```

### Zielprojekte

```text
orders, contacts, personnel und idm sind als Zielprojekte konfigurierbar
Für jedes Zielprojekt können Update-Patches erzeugt werden
Update-Patches werden über das lokale Patchsystem des Zielprojekts angewendet
Update-Patches enthalten Manifest, Changelog, Versionen und Validierungsbefehle
Kein Zielprojekt wird blind überschrieben
Zielprojekt-spezifische Konfiguration bleibt erhalten
```

### Rollback

```text
Master-Patches sind nachvollziehbar und rollbackfähig vorbereitet
Zielprojekt-Update-Patches sind nachvollziehbar und rollbackfähig vorbereitet
Patchsystem-Self-Updates haben eine dokumentierte Fallback-/Rollback-Strategie
```

## Erste Aufgabe

1. Analysiere den bereitgestellten IDM-Export.
2. Identifiziere alle für `springmaster` relevanten Tooling-, Build-, DBTool-, Export-, Patch- und Core-Bestandteile.
3. Erstelle einen deterministischen Umsetzungsplan.
4. Entscheide, ob ein vollständiges ZIP in einem Schritt realistisch ist oder ob stufenweise Patches sicherer sind.
5. Liefere danach die ersten Artefakte:

   * entweder `springmaster_initial.zip`
   * oder mindestens `000001_springmaster_project_foundation.zip`
6. Gib die Anwendung und Validierung in einem zusammenhängenden Shell-Block aus.
7. Dokumentiere klar, was bereits erfüllt ist und was in Folgepatches kommt.


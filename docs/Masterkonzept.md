# Cocondo Java Platform – Konzept für Master-/Demo-Projekt inkl. Tooling

## 1. Zielsetzung

Das Projekt `springmaster` ist die zentrale Pflege-, Demonstrations- und Validierungsbasis für gemeinsame Java-Backend-Funktionalität und Shell-Tooling innerhalb der Cocondo-Projektlandschaft.

Es dient als kanonische Quelle für:

* gemeinsames Shell-Tooling
* Patchsystem
* Export-/Build-/DBTool-Mechanik
* gemeinsame Spring-Boot-Core-Bausteine
* wiederverwendbare Java-Basisklassen
* Standardmuster für Aggregates, Entities, Attribute, Relationen, Repositories, Queries und API-Endpunkte
* Demos zur fachlichen und technischen Validierung des Core
* Generierung von Update-Patches für lokale Zielprojekte

Das Masterprojekt ist kein reines Demo-Projekt und kein reines Library-Projekt. Es ist eine **Platform Source of Truth** mit integrierter Demo-Anwendung.

## 2. Grundprinzip

Das Projekt wird selbst wie ein produktives Backend-Projekt behandelt:

* Es verwendet das gleiche Patchsystem wie die Zielprojekte.
* Jede Änderung erfolgt über nachvollziehbare Patches.
* Jede Änderung erzeugt Changelogs.
* Tooling-Änderungen werden zuerst im Masterprojekt entwickelt und validiert.
* Java-Core-Änderungen werden zuerst im Masterprojekt entwickelt und durch Demo-Use-Cases getestet.
* Zielprojekte übernehmen Änderungen nicht direkt per Copy/Paste, sondern über generierte, prüfbare Update-Patches.

## 3. Abgrenzung

### 3.1 Das Projekt ist

* zentrale Pflegebasis für Tooling
* zentrale Pflegebasis für Java Core
* technische Demo-Anwendung
* Integrations- und Regressionstest-Projekt
* Referenz für neue Backend-Projekte
* Generator für Zielprojekt-Update-Patches

### 3.2 Das Projekt ist nicht

* ein weiteres fachliches Produktivsystem
* ein Sammelbecken beliebiger Experimente
* ein Ersatz für spätere Maven-Artefakt-Versionierung
* ein Mechanismus für blinde Synchronisation
* ein Grund, projektspezifische Anpassungen in Zielprojekten zu überschreiben

## 4. Vorgeschlagener Projektname

Empfohlener Name:

```text
springmaster
```

Alternativen:

```text
cocondo-platform
cocondo-backend-platform
cocondo-spring-platform
```

Empfehlung: `springmaster`, da das Projekt sowohl Spring-Boot-Core als auch Shell-Tooling für Java-Backend-Projekte umfasst.

## 5. Zielverzeichnis

Lokaler Projektordner:

```text
/opt/cocondo/springmaster
```

Bestehende Zielprojekte bleiben unverändert in ihren Anwendungsordnern, z. B.:

```text
/opt/cocondo/orders
/opt/cocondo/contacts
/opt/cocondo/personnel
/opt/cocondo/idm
```

## 6. Architekturrolle des Masterprojekts

Das Masterprojekt hat drei Rollen:

```text
1. Platform Core
2. Tooling Source
3. Demo Application
```

### 6.1 Platform Core

Der Platform Core enthält gemeinsame Java-Bausteine, die langfristig in mehreren Projekten verwendet werden sollen.

Beispiele:

* Basisklassen für Entities
* Audit-Funktionalität
* Domain Events
* Error Events
* DTO-/Mapper-Konventionen
* Query-/Search-Bausteine
* Permission-/Security-Abstraktionen
* Repository-Konventionen
* Controller-Konventionen
* Validation-/Exception-Handling
* OpenAPI-/API-Standardisierung

### 6.2 Tooling Source

Das Tooling umfasst gemeinsame Shell- und Python-Werkzeuge:

* `bin/patch.sh`
* `bin/patch.py`
* `bin/export.sh`
* `bin/build.sh`
* `bin/dbtool.sh`
* `bin/init.env.sh`
* `bin/lib/core/**`
* `bin/lib/dbtool/**`
* Completion-Skripte
* Export-Konfiguration
* Build-Konventionen
* DBTool-Konventionen
* Projekt-Update-Mechanik

### 6.3 Demo Application

Die Demo-Anwendung ist eine bewusst kleine, aber fachlich ausreichend strukturierte Spring-Boot-Anwendung. Sie verwendet die Core-Bausteine aktiv, damit diese nicht abstrakt und ungetestet bleiben.

Die Demo-Anwendung enthält Beispiele für:

* einfache Entities
* Aggregates mit Komposition
* Referenzen zwischen Aggregates
* optionale und verpflichtende Relationen
* Value Objects
* Enums
* Auditing
* Domain Events
* Repositories
* Query Services
* Command Services
* REST APIs
* DTOs
* Mapper
* Validation
* Pagination
* Sortierung
* Filterung
* Fuzzy-/Suchmuster
* Permission-Prüfungen
* OpenAPI-Erzeugung

### 6.4 Project Skeleton / Template Source

Das Masterprojekt enthält zusätzlich einen kanonischen Templatebereich für neue Backend-Projekte. Dieser Templatebereich beschreibt und versioniert das Projektskelett, aus dem spätere lokale Zielprojekte deterministisch erzeugt werden können.

Ziele des Templatebereichs:

* neue Projekte nicht mehr manuell oder per ad-hoc-Kopie anlegen
* Bootstrap-Dateien als wiederverwendbare Vorlage im Masterprojekt pflegen
* Tooling, Projektstruktur, Basis-Konfiguration und minimale Spring-Boot-App konsistent erzeugen
* Projektanlage später über ein Tool wie `bin/project-new.sh` ausführbar machen
* die spätere Trennung zwischen Projekt-Skeleton, Tooling-Updates und Core-Updates vorbereiten

Der Templatebereich ist zunächst bewusst deklarativ. Die automatische Projektanlage wird erst umgesetzt, wenn Templateinhalt, Tokenmodell und Validierungsstrategie separat geplant und getestet wurden.

Der initiale Templatebereich liegt unter:

```text
PROJECT_DOCS/TEMPLATES/project-skeleton/
```

Diese Lage ist für die Startphase gewählt, weil der aktuelle Patch-Scope `docs` damit ohne Änderung am Patchsystem angewendet werden kann. Eine spätere operative Verschiebung oder Spiegelung nach `platform/templates/project-skeleton/` bleibt möglich und muss dann als eigener Plattform-/Tooling-Patch erfolgen.

## 7. Projektstruktur

Vorgeschlagene Struktur:

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
│   └── lib/
│       ├── core/
│       └── dbtool/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── de/cocondo/platform/
│   │   │       ├── core/
│   │   │       ├── demo/
│   │   │       └── app/
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       ├── application-build.yml
│   │       ├── application-prod.yml
│   │       └── db/changelog/
│   └── test/
│       └── java/
├── platform/
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
    ├── TEMPLATES/
    └── PLANNING/
```

## 8. Paketstruktur Java

Vorgeschlagene Java-Paketstruktur:

```text
de.cocondo.platform
├── app
│   ├── MainApplicationRunner
│   └── config
├── core
│   ├── domain
│   ├── dto
│   ├── event
│   ├── exception
│   ├── mapper
│   ├── persistence
│   ├── query
│   ├── security
│   ├── service
│   └── web
└── demo
    ├── catalog
    ├── document
    ├── project
    ├── organization
    ├── workflow
    └── relation
```

Die Trennung ist wesentlich:

```text
core  = wiederverwendbare Plattformbausteine
demo  = konkrete Anwendung dieser Bausteine
app   = Spring-Boot-Anwendungsstart und Infrastrukturkonfiguration
```

## 9. Demo-Domänenmodell

Die Demo-Anwendung soll klein bleiben, aber unterschiedliche technische Muster abdecken.

### 9.1 Demo-Bereich: Catalog

Zweck: einfache Entities, Stammdaten, Lookups.

Beispiele:

```text
CatalogItem
CatalogCategory
CatalogTag
```

Abgedeckte Muster:

* einfache Entity
* Enum-Attribute
* eindeutige technische Schlüssel
* Aktiv/Inaktiv-Status
* einfache Listen- und Detail-Endpoints
* einfache Repository-Queries
* Sortierung und Pagination

### 9.2 Demo-Bereich: Organization

Zweck: Relationen zwischen eigenständigen Aggregates.

Beispiele:

```text
Organization
OrganizationUnit
Person
ContactItem
Address
```

Abgedeckte Muster:

* Aggregate Root
* Child Entities
* One-to-Many-Komposition
* optionale Relationen
* Adressmodell
* Kontaktkanäle
* Sortierung innerhalb einer Collection
* DTO-Mapping für verschachtelte Strukturen

### 9.3 Demo-Bereich: Project

Zweck: fachliches Aggregate mit Status, Verantwortlichkeiten und Relationen.

Beispiele:

```text
DemoProject
DemoProjectMember
DemoProjectAssignment
DemoProjectState
```

Abgedeckte Muster:

* fachliches Aggregate
* State Enum
* Relation zu Person
* Relation zu OrganizationUnit
* Command Service
* Query Service
* Statuswechsel
* Domain Events
* Validierung von Transitionen

### 9.4 Demo-Bereich: Document

Zweck: Akten-/Dokument-nahe Struktur ohne echte Dokumentenverwaltung zu groß zu machen.

Beispiele:

```text
CaseRecord
RecordSection
RecordNote
RecordReference
```

Abgedeckte Muster:

* tieferes Aggregate
* Komposition
* fachliche Nummern
* referenzierte Objekte
* Textfelder
* Historisierung light
* API für verschachtelte Ressourcen

### 9.5 Demo-Bereich: Workflow

Zweck: technische Validierung von Status-/Transition-Konzepten.

Beispiele:

```text
WorkflowDefinition
WorkflowState
WorkflowTransition
WorkflowInstance
```

Abgedeckte Muster:

* generische Strukturen
* Many-to-One
* fachliche Constraints
* Transition-Validierung
* Query für erlaubte Aktionen

### 9.6 Demo-Bereich: Relation Lab

Zweck: gezielter Test unterschiedlicher Relationstypen.

Beispiele:

```text
RelationOwner
RequiredReferenceTarget
OptionalReferenceTarget
ManyReferenceTarget
RelationAssignment
```

Abgedeckte Muster:

* verpflichtende Referenz
* optionale Referenz
* Many-to-Many über Assignment Entity
* Löschen mit Restrict
* Löschen mit Cascade
* orphanRemoval
* Lazy/Eager-Verhalten
* DTO-Ausgabe von Referenzen

## 10. Demo-Größenbegrenzung

Die Demo-Anwendung darf nicht zu groß werden. Sie soll nicht jede reale Fachlichkeit vollständig nachbilden.

Regeln:

* Jedes Demo-Aggregate muss einen technischen Zweck haben.
* Keine Demo-Entity ohne Core-Testnutzen.
* Keine vollständigen Produktivprozesse.
* Keine UI.
* Keine externe Integration als Pflichtbestandteil.
* Keine fachliche Komplexität ohne Architekturwert.
* Jede Demo-Funktion muss testbar sein.

Zielgröße:

```text
ca. 20–35 Entities insgesamt
ca. 8–12 Aggregate Roots
ca. 8–15 REST Controller
ca. 80–150 Tests
```

## 11. Core-Entwicklung im Masterprojekt

Core-Änderungen werden ausschließlich im Masterprojekt entwickelt.

Ablauf:

```text
1. Core-Anforderung definieren
2. Demo-Anwendungsfall auswählen oder ergänzen
3. Core-Code ändern
4. Demo-Code nutzt Core-Feature
5. Tests ergänzen
6. Build ausführen
7. Patch dokumentieren
8. Update-Patches für Zielprojekte erzeugen
```

Core-Code darf nicht isoliert ohne Demo-Anwendung weiterentwickelt werden. Jede Core-Funktion benötigt mindestens einen konkreten Anwendungsfall im Masterprojekt.

## 12. Versionierung des Core

Kurzfristig wird der Core im Masterprojekt versioniert und per Update-Patch in Zielprojekte übertragen.

Jede Core-Änderung erhält:

```text
Core-Version
Patch-ID
Changelog
Migrationshinweis
Kompatibilitätsbewertung
betroffene Zielprojekte
```

Beispiel:

```text
CORE_VERSION=0.3.0
TOOLING_VERSION=0.5.0
PLATFORM_VERSION=0.5.0
```

Mittelfristig soll der Core als internes Maven-Artefakt vorbereitet werden, auch wenn er weiterhin im Masterprojekt gepflegt wird.

## 13. Tooling-Versionierung

Das Tooling erhält eine eigene Version:

```text
TOOLING_VERSION=0.1.0
```

Versionierte Bestandteile:

* Patchsystem
* Exporttool
* Buildtool
* DBTool
* Env-Initialisierung
* Shell-Bibliotheken
* Update-Mechanik
* Completion
* Dokumentation

Jede Tooling-Änderung wird im Masterprojekt gepatcht und dokumentiert.

## 14. Platform-Version

Die Platform-Version bündelt Core und Tooling:

```text
PLATFORM_VERSION=0.1.0
CORE_VERSION=0.1.0
TOOLING_VERSION=0.1.0
```

Die Platform-Version beschreibt den Gesamtstand des Masterprojekts.

## 15. Patchsystem im Masterprojekt

Das Masterprojekt verwendet das gleiche Patchsystem wie die Zielprojekte.

Pflichtbestandteile:

```text
bin/patch.sh
bin/patch.py
patches/logs/**
patches/archives/**
```

Jede Änderung im Masterprojekt erfolgt über einen Patch.

Patch-Scope-Beispiele:

```text
root
tooling
core
demo
resources
tests
docs
db
platform-update
```

Beispiel-Patch-IDs:

```text
000001_platform_tooling_foundation
000002_platform_demo_domain_catalog
000003_platform_core_audit_baseline
000004_platform_dbtool_target_update_support
000005_platform_core_relation_model
```

## 16. Dokumentationspflicht

Jeder Patch erzeugt einen Changelog-Eintrag.

Zusätzlich sind ADRs erforderlich bei:

* neuer Core-Abstraktion
* Änderung an Entity-Basisklassen
* Änderung an Repository-Konventionen
* Änderung am Patchsystem
* Änderung am DBTool
* Änderung am Buildprozess
* Änderung am Updateprozess für Zielprojekte
* Einführung einer neuen Demo-Domäne
* Änderung an Versionierungsregeln

Dokumentationsstruktur:

```text
PROJECT_DOCS/
├── CONCEPT/
│   └── SPRINGMASTER.md
├── ADR/
├── CORE/
├── TOOLING/
├── DEMO/
├── TEMPLATES/
├── PLANNING/
└── TARGET_UPDATES/
```

## 17. Update-Konzept für Zielprojekte

Das Masterprojekt erzeugt Update-Patches für Zielprojekte.

Zielprojekte:

```text
orders
contacts
personnel
idm
```

Spätere Zielprojekte können ergänzt werden.

### 17.1 Zielprojekt-Registry

Das Masterprojekt pflegt eine Registry lokaler Zielprojekte:

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

### 17.2 Update-Patch-Erzeugung

Das Masterprojekt stellt ein Tool bereit:

```bash
./bin/platform-update.sh create --target idm --scope tooling
./bin/platform-update.sh create --target personnel --scope core
./bin/platform-update.sh create --target orders --scope all
```

Ergebnis:

```text
000010_idm_platform_tooling_update.zip
000021_personnel_platform_core_update.zip
000024_orders_platform_update.zip
```

### 17.3 Update-Patch-Anwendung im Zielprojekt

Zielprojekte wenden Updates über ihr eigenes Patchsystem an:

```bash
cd /opt/cocondo/idm

./bin/patch.sh apply --dry-run ~/Downloads/000010_idm_platform_tooling_update.zip
./bin/patch.sh apply ~/Downloads/000010_idm_platform_tooling_update.zip
./bin/patch.sh show latest
```

### 17.4 Kein blindes Überschreiben

Update-Patches dürfen nicht blind kopieren.

Erforderlich:

* Manifest
* Dateiliste
* Scope
* erwartete Ausgangsversion
* Zielprojektkennung
* Konfliktprüfung
* Dry-run
* Changelog
* Rollback-Archiv
* Validierungsbefehle

## 18. Tooling-Update-Scope

Tooling-Updates betreffen typischerweise:

```text
bin/**
export.config.json
.env.example
PROJECT_DOCS/CONFIG/**
patches/logs/**
```

Nicht automatisch betroffen:

```text
src/main/java/**
src/main/resources/application-*.yml
src/main/resources/db/changelog/**
```

Ausnahmen müssen explizit dokumentiert werden.

## 19. Core-Update-Scope

Core-Updates betreffen typischerweise:

```text
src/main/java/de/cocondo/platform/core/**
src/test/java/de/cocondo/platform/core/**
```

In Zielprojekten kann der Pfad abweichen. Deshalb benötigt der Update-Generator Mapping-Regeln.

Beispiel:

```text
Master:
  src/main/java/de/cocondo/platform/core/domain/BaseEntity.java

Target:
  src/main/java/de/cocondo/app/system/domain/BaseEntity.java
```

Diese Zuordnung darf nicht implizit geraten werden. Sie muss in Update-Regeln gepflegt werden.

## 20. Demo-Code wird nicht in Zielprojekte übertragen

Demo-Code dient nur zur Validierung im Masterprojekt.

Er wird nicht automatisch in Zielprojekte übertragen.

Ausnahme: bewusst generierte Beispiel- oder Starter-Projekte.

## 21. Build-Konzept

Das Masterprojekt verwendet den gleichen Buildstandard wie die Zielprojekte.

Build-Ziele:

* Maven Package
* Tests
* Spring-Boot-Repackage
* Liquibase Stage Update
* Liquibase Validate
* Stage Status
* Dev-Schema-Reconcile
* Dev/Stage-Diff
* OpenAPI Export
* SPDX/SBOM
* ZIP-Erstellung
* optional Remote Upload
* Export

Build-Profil:

```text
build
```

OpenAPI-Pfad:

```text
/api-docs
```

## 22. DBTool-Konzept

Das DBTool unterstützt:

* Dev DB
* Stage DB
* Build DB
* Baseline-Reparatur
* Stage-Rebuild
* Validate
* Status
* Diff
* unprivileged connection shortcut
* sudo nur bei fehlender DB oder fehlenden Grants

Pflichtkommandos:

```bash
./bin/dbtool.sh env
./bin/dbtool.sh status
./bin/dbtool.sh rebuild-dev
./bin/dbtool.sh rebuild-stage
./bin/dbtool.sh update-stage
./bin/dbtool.sh validate-stage
```

## 23. Project-New-Konzept

Neue Backend-Projekte sollen perspektivisch nicht durch manuelles Kopieren entstehen, sondern durch ein Master-Tool auf Basis des versionierten Project Skeletons.

Vorgesehener Aufruf:

```bash
./bin/project-new.sh \
  --name example \
  --path /opt/cocondo/example \
  --group-id de.cocondo.example \
  --base-package de.cocondo.example \
  --port 8090 \
  --db-name example
```

Die Projektanlage muss folgende Eigenschaften erfüllen:

* kein Überschreiben vorhandener abweichender Dateien ohne explizite Freigabe
* reproduzierbare Token-Ersetzung
* erzeugtes Projekt enthält Patchsystem, Exporttool, DBTool-Basis und minimale App
* erzeugtes Projekt ist unmittelbar mit `mvn test` validierbar
* erzeugtes Projekt enthält eine `.env.example`, aber keine automatisch befüllte produktive `.env`
* Projektanlage erzeugt einen nachvollziehbaren Bootstrap-/Erzeugungsnachweis

Die Umsetzung von `bin/project-new.sh` erfolgt nicht im initialen Template-Patch, sondern in einem eigenen späteren Tooling-Schritt.

## 24. Umsetzungsplanung und Verifikation

Die Umsetzung des Masterkonzepts erfolgt sequenziell über geplante, überprüfbare Schritte. Nach Anlage des Templatebereichs wird ein Umsetzungsplan gepflegt, der Phasen, Patch-Ziele, erwartete Ergebnisse und Verifikationskommandos festlegt.

Der initiale Plan liegt unter:

```text
PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md
```

Jeder weitere Umsetzungsschritt muss mindestens definieren:

* Ziel und Scope
* betroffene Projektbereiche
* ausgeschlossene Änderungen
* erwartete Dateien oder Artefakte
* Validierungsbefehle
* Abbruchkriterien

Standard-Verifikation nach jedem Patch:

```bash
./bin/patch.sh show latest
./bin/export.sh full --zip
mvn test
```

Bei Tooling-, DB-, Build-, Core- oder Demo-Änderungen sind zusätzliche spezifische Tests aufzunehmen.


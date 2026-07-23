# Project Skeleton Template

Dieser Ordner enthält das initiale Projektskelett für neue Cocondo Java-Backend-Projekte.

## Status

```text
STATUS=PROJECT_NEW_GOVERNANCE_HARNESS_FOUNDATION
AUTOMATIC_GENERATION=IMPLEMENTED_CONSERVATIVE
```

Der Templatebereich ist weiterhin bewusst klein gehalten. Ab Patch `000005` kann `bin/project-new.sh` daraus neue lokale Projekte erzeugen.

## Ziel

Das Skeleton stellt die Dateien bereit, die ein neues Projekt unmittelbar projektfähig machen:

* Maven-/Spring-Boot-Basis
* minimale Anwendung
* Export-Grundkonfiguration
* DBTool-Grundkonfiguration
* `.env.example`
* minimale V2-Dokumentationsstruktur mit Index
* lokaler Governance-Adoption und maschinenlesbaren Ausgangsständen
* report-only Documentation-, Directory- und Sprint-Harness
* Versionierungs- und Bootstrap-Nachweis

Das operative Tool ergänzt zusätzlich die aus dem Masterstand übernommenen Tooling-Dateien:

* Patchsystem
* Exporttool
* DBTool
* Buildtool
* projektlokaler Tooling-Selfcheck
* Governance-Gates, Contracts, Fixtures und freigegebene Templates

## Tokenmodell

Die Template-Dateien verwenden Platzhalter. Beispiele:

```text
__PROJECT_NAME__
__ARTIFACT_ID__
__GROUP_ID__
__BASE_PACKAGE__
__BASE_PACKAGE_PATH__
__APPLICATION_CLASS__
__HTTP_PORT__
__DB_NAME__
__STAGE_DB_NAME__
__PLATFORM_VERSION__
__CORE_VERSION__
__TOOLING_VERSION__
```

Die Token-Ersetzung erfolgt ausschließlich über `bin/project-new.sh`.

## Sicherheitsregeln

* Zielverzeichnisse müssen leer sein oder dürfen noch nicht existieren.
* Bestehende nicht-leere Zielverzeichnisse werden nicht überschrieben.
* `--dry-run` zeigt den Schreibplan ohne Dateierzeugung.
* Es wird keine produktive `.env` erzeugt.
* Der erzeugte Bootstrap wird im Zielprojekt dokumentiert.

## Abgrenzung

Nicht Bestandteil der Project-New-Foundation:

* keine Core-Migration
* keine Demo-Domäne
* keine Zielprojekt-Update-Erzeugung
* keine automatische Aufnahme des erzeugten Projekts in die Target Registry

## Component Scan

Das Application-Template scannt zwei Namespace-Wurzeln:

```java
@SpringBootApplication(scanBasePackages = {
        "__BASE_PACKAGE__",
        "de.cocondo.system"
})
```

Damit bleiben neu erzeugte Anwendungen unabhängig in ihrem eigenen Package, können aber den verteilbaren Core unter `de.cocondo.system` ohne zusätzliche App-Anpassung nutzen.


## Service Slice Abgrenzung seit 000077

Das Project Skeleton bleibt auch nach der Instantiation Acceptance bewusst fachfrei. Es erzeugt keine Aggregate-, Controller-, DTO-, Mapper-, Service- oder Repository-Struktur für eine konkrete Domäne.

Der spätere generated service slice ist eine zweite, separat zu validierende Stufe. Die Anforderungen dazu stehen in:

```text
PROJECT_DOCS/TOOLING/GENERATED_SERVICE_SLICE_READINESS_PLAN.md
```

Dadurch bleibt ein neu erzeugtes Projekt sauber und minimal, während fachliche Slice-Erzeugung, Core-Verteilung und Evidence nicht implizit in die Projektanlage gemischt werden.

## Governance-Harness seit 000174

Das Skeleton bleibt fachfrei, erzeugt aber nun eine eigenständig prüfbare Governance-Baseline. Die vollständigen Springmaster-Governance-Dokumente und Standards werden nicht kopiert. Stattdessen werden lokal materialisiert:

- ein projektspezifisches `AGENTS.md`,
- Dokumentationsindex und Governance-Adoption,
- Adoption-, Deviation-, Risiko- und Managed-State-Records,
- Documentation-, Directory- und Sprint-Contracts,
- report-only Gates und deren Fixtures,
- allgemeine Dokument- und Sprint-Templates.

Der Generator passt ausschließlich projektbezogene Werte an. Kanonische Schema-IDs und Fixture-Verträge bleiben unverändert. Ein frisches Projekt muss alle drei Governance-Gates sowie den lokalen Tooling-Selfcheck ohne manuelle Nacharbeit bestehen.

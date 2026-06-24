# Project Skeleton Template

Dieser Ordner enthält das initiale Projektskelett für neue Cocondo Java-Backend-Projekte.

## Status

```text
STATUS=PLANNED_TEMPLATE_BASELINE
AUTOMATIC_GENERATION=NOT_IMPLEMENTED
```

Der Templatebereich ist im ersten Schritt bewusst deklarativ angelegt. Die tatsächliche Projektanlage über ein Tool wie `bin/project-new.sh` wird erst in einem späteren Tooling-Patch umgesetzt.

## Ziel

Das Skeleton soll künftig die Dateien bereitstellen, die ein neues Projekt unmittelbar projektfähig machen:

* Maven-/Spring-Boot-Basis
* minimale Anwendung
* Patchsystem
* Export-Grundkonfiguration
* DBTool-Grundkonfiguration
* `.env.example`
* minimale Dokumentationsstruktur
* Versionierungs- und Registry-Anbindung

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

Die Token-Ersetzung darf später ausschließlich über das Projektanlage-Tool erfolgen. Manuelle Ersetzung ist für produktive Projektanlage nicht vorgesehen.

## Abgrenzung

Nicht Bestandteil dieses ersten Template-Patches:

* keine automatische Projektanlage
* kein `bin/project-new.sh`
* keine Core-Migration
* keine Demo-Domäne
* keine Zielprojekt-Update-Erzeugung
* keine Änderung am Patchsystem

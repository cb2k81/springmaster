# Project Skeleton Template

Dieser Ordner enthält das initiale Projektskelett für neue Cocondo Java-Backend-Projekte.

## Status

```text
STATUS=PROJECT_NEW_FOUNDATION
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
* minimale Dokumentationsstruktur
* Versionierungs- und Bootstrap-Nachweis

Das operative Tool ergänzt zusätzlich die aus dem Masterstand übernommenen Tooling-Dateien:

* Patchsystem
* Exporttool
* DBTool
* Buildtool
* Tooling-Selfcheck

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

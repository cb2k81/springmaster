# Changelog – 000013 springmaster project state review and version policy

## Typ

Project-State-/Versionierungs-/Rollback-Policy-Patch.

## Änderungen

* ergänzt ein Review des erreichten Projektstands nach Patch `000012`
* dokumentiert eine verbindliche Versionierungsregel für Platform, Core, Tooling, Templates, Demo und Platform-Update
* dokumentiert die Abgrenzung zwischen Full-Parts-Baseline-Exporten und lokalen Rollback-Archiven
* setzt initiale Foundation-Versionen in `platform/versions/platform.env`
* bereinigt den Umsetzungsplan nach `000012` und stellt den nächsten Code-Schritt auf `000014`
* aktualisiert das Masterkonzept zu Versionierung und Rollback-Archiven

## Nicht enthalten

* keine Java-Code-Änderung
* keine Maven-Dependency-Änderung
* keine Shell-/Python-Tooling-Änderung
* keine DB-/Liquibase-Änderung
* keine Demo-Domäne
* keine Target-Update-Implementierung

## Validierung

Der Patch ändert Dokumentation und `platform/versions/platform.env`. Es wird kein Maven-Test ausgeführt.

Pflichtprüfungen:

* Dry-run
* Apply
* Patch-Log-Prüfung
* Prüfung der Versionsdatei
* Inhaltsprüfung der neuen Policy-Dokumente
* Full-ZIP-Export
* Full-Parts-Baseline-Export

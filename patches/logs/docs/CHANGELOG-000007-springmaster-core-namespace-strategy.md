# Changelog – 000007 springmaster core namespace strategy

## Scope

`docs`

## Änderungen

* Core-Namespace-Strategie verbindlich dokumentiert.
* Zielnamespace für den wiederverwendbaren Core von `de.cocondo.platform.core` auf `de.cocondo.system` korrigiert.
* Masterkonzept, Core-README, Migrationsregeln und Umsetzungsplan angepasst.
* Core-Kandidatenmanifest auf die korrigierte Zielwurzel `src/main/java/de/cocondo/system` aktualisiert.

## Nicht enthalten

* keine Java-Code-Migration
* keine Maven-Dependency-Änderung
* keine Demo-Domäne
* keine Target-Update-Implementierung

## Validierung

Vorgesehen:

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
./bin/patch.sh show latest
python3 -m json.tool PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_CLASSIFICATION.json >/dev/null
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
```

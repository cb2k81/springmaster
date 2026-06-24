# CHANGELOG 000003 – springmaster tooling baseline from idm

## Scope

`tooling`

## Änderungen

* Gemeinsame Shell-Helfer unter `bin/lib/core/**` ergänzt.
* DBTool in modulare Bibliotheken unter `bin/lib/dbtool/**` überführt.
* `bin/dbtool.sh` von Bootstrap-Status zu Liquibase-/MariaDB-fähigem Tool erweitert.
* `bin/export.sh` um `--list` und `--full-parts <splitProfile>` ergänzt.
* `export.config.json` um Profile für `templates`, `planning`, `target-registry` und `platform-update` ergänzt.
* `bin/patch.py` um zusätzliche Scopes für spätere Template-, Planungs- und Plattform-Update-Patches erweitert.
* `bin/build.sh` als lokal-first Buildtool stabilisiert.
* `bin/tooling-selfcheck.sh` als deterministische Tooling-Prüfung ergänzt.
* Tooling-Dokumentation unter `PROJECT_DOCS/TOOLING/**` aktualisiert.

## Nicht geändert

* Kein Java-Core.
* Keine Demo-Domäne.
* Keine IDM-Fachlichkeit.
* Kein aktiver Zielprojekt-Updategenerator.

## Pflichtprüfung

```bash
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
mvn test
```

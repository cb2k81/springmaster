# Tooling Baseline 000003

## Ziel

Patch `000003_springmaster_tooling_baseline_from_idm` stabilisiert das Bootstrap-Tooling und bereitet spätere deterministische Umsetzungsschritte vor.

## Enthaltene Bereiche

* gemeinsame Shell-Helfer unter `bin/lib/core/**`
* DBTool-Bibliothek unter `bin/lib/dbtool/**`
* erweiterter Export mit Split-Exporten
* erweitertes Patch-Scope-Modell
* lokales Buildtool mit Runtime-ZIP
* `bin/tooling-selfcheck.sh` als verifizierbarer Tooling-Test

## Nicht enthalten

* keine Java-Core-Migration
* keine IDM-Fachdomäne
* keine automatische Projektanlage
* kein Zielprojekt-Updategenerator

## Pflichtprüfung

```bash
./bin/tooling-selfcheck.sh
mvn test
```

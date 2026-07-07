# Changelog 000009 – Springmaster Core Scope Alignment

## Zweck

Richtet die technischen Scope-Regeln des Patchsystems und des Exporttools auf die in Patch `000007` entschiedene Core-Namespace-Strategie aus.

## Änderungen

* `bin/patch.py`: Scope `core` erlaubt künftig `src/main/java/de/cocondo/system/**` und `src/test/java/de/cocondo/system/**`.
* `export.config.json`: Exportprofil `core` verwendet dieselben kanonischen Core-Pfade.
* `PROJECT_DOCS/TOOLING/PATCH_SYSTEM.md`: Core-Scope-Ausrichtung dokumentiert.
* `PROJECT_DOCS/TOOLING/TOOLING_BASELINE.md`: Tooling-Änderung dokumentiert.
* `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md`: Umsetzungsstand und nächster Core-Schritt aktualisiert.

## Nicht enthalten

* Keine Java-Code-Migration.
* Keine Maven-Konfigurationsänderung.
* Keine Ressourcenänderung.
* Keine Demo-Domäne.
* Keine Zielprojekt-Aktualisierung.

## Validierung

Tooling-/Root-Scope-Patch ohne Java-, Build- oder Ressourcenänderung:

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
./bin/patch.sh show latest
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
```

Kein `mvn test`, weil keine Java- oder Build-Konfigurationsdateien geändert werden.

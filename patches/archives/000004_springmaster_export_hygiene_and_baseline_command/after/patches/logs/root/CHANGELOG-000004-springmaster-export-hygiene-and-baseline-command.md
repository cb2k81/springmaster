# CHANGELOG 000004 – springmaster export hygiene and baseline command

## Scope

`root`

## Änderungen

* Ergänzt `export.config.json` um Ausschlüsse für Python-Cache-Dateien und lokale Tool-Caches.
* Ergänzt `.gitignore` um dieselben lokalen Cache-Artefakte.
* Entfernt das versehentlich exportierte erzeugte Artefakt `bin/__pycache__/patch.cpython-312.pyc`.
* Ergänzt `PROJECT_DOCS/TOOLING/EXPORT_TOOL.md` um den verbindlichen Baseline-Export nach Patches.
* Aktualisiert `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md` um den erreichten Tooling-Stand und den Standard-Kommandoabschluss.

## Auswirkungen

* Künftige Exporte enthalten keine Python-Bytecode-Cache-Dateien mehr.
* Künftige Kommando-Stacks enden mit einem Full-ZIP-Export und einem Full-Parts-Baseline-Export.
* Keine Änderung am Java-Code.
* Keine Änderung am DB-Schema.
* Keine automatische Projektanlage.

## Pflichtprüfung

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
```

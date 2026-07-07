# CHANGELOG 000010 - springmaster core basic types foundation

## Scope

core

## Änderungen

- erster dependency-armer Core-Code-Slice unter `de.cocondo.system` angelegt
- fachfreie DTO-, Entity-, Validation-, Exception- und ID-Contract-Typen übernommen
- Unit-Tests für die neuen Core-Basistypen ergänzt
- Core-Dokumentation aktualisiert

## Validierung

Dieser Patch ist ein Code-Patch. Erwartete Validierung:

```bash
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
```

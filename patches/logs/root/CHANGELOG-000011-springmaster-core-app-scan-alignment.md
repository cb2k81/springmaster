# Changelog 000011 - springmaster core app scan alignment

## Scope

root

## Typ

Code-/Template-Patch

## Änderungen

- richtet `SpringmasterApplication` auf explizites Scannen von `de.cocondo.platform` und `de.cocondo.system` aus
- ergänzt einen Test für die Scan-Konfiguration
- richtet das Project-Skeleton-Application-Template auf `__BASE_PACKAGE__` und `de.cocondo.system` aus
- dokumentiert die Core-App-Scan-Strategie
- aktualisiert Template-Manifest und Umsetzungsplan

## Validierung

- Patch-Dry-run
- Patch-Apply
- Shell-/Python-Syntaxprüfung
- Tooling-Selfcheck
- `mvn test`
- Project-New Dry-run und Sample-Erzeugung
- `mvn test` im erzeugten Sample-Projekt
- Full- und Full-Parts-Baseline-Export

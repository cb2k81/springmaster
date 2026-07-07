# CHANGELOG 000038 - springmaster core idm system gap inventory

## Scope

`root` / documentation-only analysis.

## Änderungen

- Ergänzt die verbindliche Gap-Inventarisierung zwischen IDM-Alt-Core `de.cocondo.app.system` und Springmaster-Core `de.cocondo.system`.
- Ergänzt eine maschinenlesbare Inventarisierung mit Counts, Slices, externen Importnutzungen und Deletion-Gates.
- Dokumentiert die beschlossene Zielrichtung: Springmaster-Core in IDM behalten, Core-Tests mitführen, IDM-Core-Masterdokumentation später reduzieren, Alt-Core nach Abdeckung entfernen.
- Aktualisiert Core-README und Version Policy.

## Nicht enthalten

- Keine Java-Codeänderungen.
- Keine Maven-/Build-Konfigurationsänderungen.
- Keine IDM-Zielprojektänderung.
- Keine Migration und keine Löschung von `de.cocondo.app.system/**`.

## Validierung

- JSON-Inventar syntaktisch validierbar.
- Patch-Dry-run/Apply gegen aktuelle Springmaster-Baseline.
- Reguläre Export-Hygiene bleibt gewahrt.

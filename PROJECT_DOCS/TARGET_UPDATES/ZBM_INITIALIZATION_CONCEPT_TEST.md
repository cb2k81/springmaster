# ZBM Initialization Concept Test

Patch: `000080_springmaster_generated_service_slice_blueprint_spec`

> Historical evidence: This document records the initialization concept state from patch `000080`. It is not the current ZBM lifecycle or baseline. The current Springmaster descriptor and the first fachlicher pilot boundary are documented in `TARGET_REGISTRY.md` and `ZBM_GENERATED_SLICE_PILOT_PLAN.md`.


## Zweck

Dieses Dokument beschreibt den ersten kontrollierten Praxistest des Springmaster-Initialisierungskonzepts am Zielprojekt `zbm`.

Der Test erzeugt oder validiert ein neues technisches Java-Backend-Skeleton unter `/opt/cocondo/zbm`. Er beliefert keine laufenden Projekte und verwendet kein Platform-Update-`target-apply`.

## Rahmen

```text
Target:        zbm
Target path:   /opt/cocondo/zbm
Base package:  de.cocondo.zbm
Lifecycle:     initialization
```

## Testumfang

Der Test prüft:

1. Target-Descriptor `zbm` ist vorhanden und steht auf `INITIALIZATION_CANDIDATE`.
2. IDM und Personnel bleiben `DEFERRED_EXISTING_PROJECT_NO_DELIVERY`.
3. `project-new` erzeugt ein technisches ZBM-Skeleton oder erkennt ein bereits vorhandenes gültiges Skeleton.
4. Das Zielprojekt enthält Patch-, Export-, Build- und DBTooling.
5. `mvn test` ist im Zielprojekt grün.
6. Das Zielprojekt erzeugt einen Full-ZIP-Export.

## Schutzregeln

* Ein nicht-leeres Zielverzeichnis wird nicht überschrieben.
* Ist `/opt/cocondo/zbm` bereits vorhanden, wird nur validiert, wenn es wie ein Springmaster-generiertes Backend aussieht.
* Es wird keine lokale `.env` erzeugt.
* DBTool-Status darf keine destruktiven Operationen ausführen.
* Bestehende Projekte werden nicht verändert.

## Erwartetes Ergebnis

```text
DONE: zbm initialization concept test
Export: /opt/cocondo/zbm/exports/text/zbm_export_full_....zip
```

Der erfolgreiche Test ist die operative Bestätigung, dass die Initialisierungsschicht funktioniert. Fachliche Slice-Generierung ist danach ein eigener Schritt.

# 000022 - Springmaster Patch Accept Verify Workflow

## Kategorie

Tooling / Patchsystem / Abnahme-Workflow

## Änderungen

* `./bin/patch.sh accept <patch.zip>` eingeführt.
* `./bin/patch.sh verify <patch-ref>` eingeführt.
* Strukturierte Abnahme-Logs unter `patches/logs/accept/<patch-id>/` eingeführt.
* Kompakte Fehlerzusammenfassung für fehlgeschlagene Abnahmen ergänzt.
* Versionierung auf `PLATFORM_VERSION=0.6.0-foundation` und `PLATFORM_TOOLING_VERSION=0.3.0` erhöht.
* Tooling-Dokumentation und Validierungsrichtlinie aktualisiert.

## Validierung

Dieser Patch ändert das Patchsystem selbst. Pflichtprüfung:

* Shell-Syntaxprüfung
* Python-Kompilierung
* Tooling-Selfcheck
* testweise `accept`/`verify` nach Anwendung
* Full-ZIP-Export

Ein Maven-Test ist für diesen Patch nicht erforderlich, weil kein Java-Code und keine Build-Konfiguration geändert wird.

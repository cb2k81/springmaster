# 000166 — Export lifecycle, checksum and archive contract

## Anlass

Der Springmaster-Full-Export erzeugte zwar ZIP-interne Metadaten, ließ aber das ungepackte Exportverzeichnis parallel zum ZIP bestehen. Eine portable ZIP-Checksumme fehlte. Mehrere aktuelle Exporte lagen nebeneinander unter `exports/text/`, sodass Explorer- oder Dateisortierung zur versehentlichen Auswahl einer veralteten Baseline führen konnte.

## Änderungen

- Jeder ZIP-Export erzeugt `<export>.zip.sha256` im portablen `sha256sum -c`-Format.
- Textdarstellung, Profil-Metadaten, Closure-Evidence und Full-Parts-Index bleiben Mitglieder des ZIP.
- Das temporäre ungepackte Staging-Verzeichnis wird nach ZIP- und Checksum-Prüfung entfernt.
- Vorherige projektbezogene Exportartefakte werden als Set nach `exports/text/Archiv/` verschoben.
- Im aktuellen Ausgabeordner verbleiben genau das aktuelle ZIP und dessen Checksumme; fremde Dateien bleiben unberührt.
- `export.sh --current` liefert den eindeutigen aktuellen Export ohne Sortierannahmen.
- Baseline-Exporte verlangen einen sauberen Git-Working-Tree und prüfen, dass sich HEAD, Branch und Dirty-Status während der Erzeugung nicht verändern.
- `--allow-dirty` bleibt eine explizite, nicht kanonische Forensik-Ausnahme und wird in `sourceGit.dirty` dokumentiert.
- Der Integritätscheck verlangt standardmäßig die Checksum-Sidecar-Datei; historische Exporte benötigen ausdrücklich `--allow-missing-checksum`.
- Eine neue Lifecycle-Integration-Fixture prüft Veröffentlichung, Archivierung, ZIP-Inhalt, Checksumme, Git-Cleanliness, Dirty-Ausnahme und Schutz fremder Dateien.
- Tooling-Selfcheck, Completion, ADR, AGENTS und Exportdokumentation werden auf den neuen Vertrag ausgerichtet.

## Git- und Patch-Zusammenspiel

- Git bleibt die dauerhafte Wahrheit; die Exportmetadaten binden den Export an den tatsächlichen Live-Commit.
- Der kanonische Patchworkflow verwendet `accept --no-export --commit` und erzeugt einen Handoff-Export anschließend explizit aus dem akzeptierten sauberen Live-Checkout.
- Keine Exportauswahl über `ls -t`, Dateiexplorer-Sortierung oder manuelle Kopie temporärer Worktree-Exporte.
- Exportartefakte bleiben unter `exports/` und werden nicht committed.

## Effizienz und Fehlervermeidung

- Gepackte Daten werden nicht zusätzlich ungepackt aufbewahrt.
- Alte Exporte stören die aktuelle Auswahl nicht mehr und werden ohne erneute Kompression verschoben.
- Die Lifecycle-Prüfung ist auf das projektbezogene Exportpräfix begrenzt; fremde Dateien werden weder gescannt noch verschoben.
- Quellhashes bleiben Raw-Byte-basiert. Es findet keine Whitespace-, Zeilenenden- oder Formatnormalisierung der Quelldateien statt.

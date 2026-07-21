# Export Tool

## Zweck

Das Exporttool erzeugt deterministische Textexporte des aktuellen Projekts. Diese Exporte sind die primäre Grundlage für Review, Folgepatches, Handoff, Audit und spätere Zielprojekt-Updates.

Ein ZIP-Export ist ein abgeschlossenes Artefaktset. Im aktuellen Exportverzeichnis verbleiben nur:

```text
<export>.zip
<export>.zip.sha256
```

Die Textdarstellung, die Metadatei und bei Full-Parts-Exports die `export.index.json` liegen ausschließlich im ZIP. Das temporäre, ungepackte Staging-Verzeichnis wird nach erfolgreicher ZIP- und Checksum-Prüfung entfernt.

## Kommandos

```bash
./bin/export.sh --list
./bin/export.sh --current
./bin/export.sh full
./bin/export.sh full --zip
./bin/export.sh tooling
./bin/export.sh --full-parts baseline --zip
```

`--current` liefert den einzigen aktuell veröffentlichten Exportpfad. Eine Ermittlung über Dateisortierung, Explorer-Reihenfolge oder `ls -t` ist nicht erforderlich und nicht zulässig.

## Git-Baseline

Reguläre Baseline-Exporte verlangen ein verfügbares Git-Repository und einen sauberen Working Tree. Die Metadaten enthalten den Git-HEAD, den Branch und den Dirty-Status. Vor der Veröffentlichung wird geprüft, dass sich der Git-Zustand während des Exports nicht geändert hat.

Ein bewusst nicht kanonischer Arbeitsstand kann ausschließlich explizit exportiert werden:

```bash
./bin/export.sh full --zip --allow-dirty
```

Ein solcher Export dokumentiert `sourceGit.dirty=true` und ist keine freigegebene Baseline für einen Folgepatch.

## Checksumme

Jeder ZIP-Export erzeugt eine portable SHA-256-Sidecar-Datei:

```text
<sha256>  <zip-basename>
```

Prüfung:

```bash
cd exports/text
sha256sum -c <export>.zip.sha256
```

Der integrierte Export-Integritätscheck prüft die Sidecar-Datei standardmäßig zusätzlich zu ZIP-CRC, Metadaten, Raw-Byte-Dateimanifest und optionaler Closure-Evidence:

```bash
python3 bin/export-integrity-check.py <export>.zip --source-root .
```

Nur für historische ZIPs vor Einführung des Checksum-Vertrags ist explizit zulässig:

```bash
python3 bin/export-integrity-check.py <legacy-export>.zip --allow-missing-checksum
```

## Lifecycle und Archivierung

Ein neuer Export wird zunächst vollständig in einem versteckten Staging-Verzeichnis erzeugt. ZIP-Struktur und Checksumme werden geprüft, bevor der aktuelle Exportbestand verändert wird.

Bei erfolgreicher Veröffentlichung werden alle bisherigen projektbezogenen Exportartefakte aus `exports/text/` nach folgendem Verzeichnis verschoben:

```text
exports/text/Archiv/
```

Danach wird das neue, bereits geprüfte Artefaktset veröffentlicht. Fremde Dateien im Ausgabeordner werden nicht verschoben. Schlägt Erzeugung oder Prüfung fehl, bleibt der bisherige aktuelle Export unverändert.

Damit gilt:

- genau ein aktueller Export ist unmittelbar unter `exports/text/` sichtbar;
- alte Exporte liegen ausschließlich unter `exports/text/Archiv/`;
- eine falsche alphabetische oder zeitliche Sortierung im Dateiexplorer kann nicht zur Auswahl eines veralteten Exports führen;
- ZIP- und Checksum-Datei werden immer gemeinsam archiviert.

## Profile

Die Profile werden in `export.config.json` definiert. Wichtige Profile sind:

- `root`
- `docs`
- `patches`
- `tooling`
- `platform`
- `templates`
- `planning`
- `java`
- `resources`
- `tests`

## Split-Exporte

Split-Exporte werden über `splitProfiles` in `export.config.json` gesteuert:

```bash
./bin/export.sh --full-parts baseline --zip
./bin/export.sh --full-parts review --zip
./bin/export.sh --full-parts runtime --zip
```

Ein Full-Parts-ZIP enthält pro Profil eine Textdatei und Metadaten sowie eine gemeinsame `export.index.json`. Außerhalb des ZIP verbleiben nur ZIP und Checksumme.

## Ausschlüsse

Ausgeschlossen sind insbesondere lokale, temporäre oder erzeugte Artefakte:

- `target/**`
- `build/**`
- `tmp/**`
- `exports/**`
- `.git/**`
- `.env`
- `patches/archives/**`
- `platform/update/generated/**`
- `platform/update/manifests/**`
- `.idea/**`
- Python-Cache-Dateien wie `__pycache__/**`, `*.pyc` und `*.pyo`
- Tool-Cache-Verzeichnisse wie `.pytest_cache/**`, `.mypy_cache/**` und `.ruff_cache/**`
- Binär- und Archivdateien

## Baseline-Export nach Patches

Ein Full-Export ist kein Standardabschluss jeder Änderung. Nach einem ausdrücklich verlangten Handoff-, Release- oder Audit-Abschluss wird er nach erfolgreicher Patch-Acceptance auf dem sauberen Live-Git-Stand erzeugt:

```bash
./bin/export.sh full --zip
./bin/export.sh --current
```

Der kanonische Patchworkflow verwendet regelmäßig `patch.sh accept ... --no-export --commit` und erzeugt den finalen Export anschließend explizit. Damit wird der Export direkt aus dem akzeptierten Live-Commit erzeugt und nicht aus einem temporären Acceptance-Worktree übernommen.

## Baseline vs. Forensik

Der reguläre Full-ZIP-Export ist eine saubere Projektbaseline. Er ist nicht als vollständiger Arbeitsverzeichnisdump gedacht. Operative Artefakte aus Patch-Anwendung, Platform-Update-Planung, Build, temporären Läufen oder lokalen Archiven werden bewusst ausgeschlossen.

Für forensische Untersuchungen müssen separate Artefakte erzeugt werden, zum Beispiel ein bewusst gepackter Arbeitsbaum oder reine Dateilisten.

## Raw-byte integrity metadata

Full- und Split-Exporte verwenden Metadatenformat Version 2. Jede Profil-Metadatei enthält `fileManifest`-Einträge mit repositoryrelativem Pfad, Raw-Byte-Größe und SHA-256 der Quelldatei. `fileManifestSha256` schützt das kanonische Manifest selbst.

Die Textdarstellung ist nur für Review. Separatoren und Präsentations-Newlines dürfen niemals zur Rekonstruktion von `expectedBeforeSha256` verwendet werden. Folgepatches verwenden die Metadaten oder die Bytes des Live-Repositories.

Optionale Closure-Evidence kann ohne zweiten Export eingebettet werden:

```bash
./bin/export.sh full --zip --evidence <evidence.json>
```

Traversal verwirft statisch ausgeschlossene Runtime-Bäume wie `build/`, `target/`, `.git/`, `exports/` und `patches/logs/validation/`, bevor deren Dateien besucht werden. Das hält die Laufzeit nach wiederholten Prüfungen stabil und verhindert, dass aktive Runner-Logs den Raw-Byte-Snapshot verändern.

## Vertragsprüfungen

```bash
./bin/export-lifecycle-it.sh
./bin/export-integrity-it.sh
./bin/tooling-selfcheck.sh --export
```

Die Lifecycle-Fixture prüft insbesondere Git-Cleanliness, Checksumme, ZIP-interne Metadaten, Entfernung ungepackter Daten, Archivierung des vorherigen Artefaktsets, Eindeutigkeit von `--current` und den Schutz fremder Dateien.

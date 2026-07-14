# Export Tool

## Zweck

Das Exporttool erzeugt deterministische Textexporte des aktuellen Projekts. Diese Exporte sind die primäre Grundlage für Review, Folgepatches und spätere Zielprojekt-Updates.

## Kommandos

```bash
./bin/export.sh --list
./bin/export.sh full
./bin/export.sh full --zip
./bin/export.sh tooling
./bin/export.sh --full-parts baseline --zip
```

## Profile

Die Profile werden in `export.config.json` definiert. Wichtige Profile sind:

* `root`
* `docs`
* `patches`
* `tooling`
* `platform`
* `templates`
* `planning`
* `java`
* `resources`
* `tests`

## Split-Exporte

Split-Exporte werden über `splitProfiles` in `export.config.json` gesteuert:

```bash
./bin/export.sh --full-parts baseline --zip
./bin/export.sh --full-parts review --zip
./bin/export.sh --full-parts runtime --zip
```

Ein Split-Export erzeugt pro Profil eine Textdatei, Metadaten und eine `export.index.json`.

## Ausschlüsse

Ausgeschlossen sind insbesondere lokale, temporäre oder erzeugte Artefakte:

* `target/**`
* `build/**`
* `tmp/**`
* `exports/**`
* `.git/**`
* `.env`
* `patches/archives/**`
* `platform/update/generated/**`
* `platform/update/manifests/**`
* `.idea/**`
* Python-Cache-Dateien wie `__pycache__/**`, `*.pyc` und `*.pyo`
* Tool-Cache-Verzeichnisse wie `.pytest_cache/**`, `.mypy_cache/**` und `.ruff_cache/**`
* Binär-/Archivdateien

## Baseline-Export nach Patches

Nach jedem erfolgreich angewendeten Patch wird aktuell ein Full-ZIP-Export erzeugt und der erzeugte Exportpfad ausgegeben. Full-Parts-Baseline-Exporte bleiben möglich, werden aber nicht pauschal erzeugt, damit nicht unnötig Exportdaten anwachsen.

```bash
./bin/export.sh full --zip
ls -1t exports/text/*.zip | head -n 2
```

## Baseline vs. Forensik

Der reguläre Full-ZIP-Export ist eine saubere Projektbaseline. Er ist nicht als vollständiger Arbeitsverzeichnisdump gedacht. Operative Artefakte aus Patch-Anwendung, Platform-Update-Planung, Build, temporären Läufen oder lokalen Archiven werden bewusst ausgeschlossen.

Für forensische Untersuchungen müssen separate Artefakte erzeugt werden, z. B. ein bewusst gepackter Arbeitsbaum oder reine Dateilisten.

## Raw-byte integrity metadata since 000124

Full and split exports use metadata format version 2. Every profile metadata file contains `fileManifest` entries with the source-relative path, raw byte size and SHA-256 calculated directly from the repository file. `fileManifestSha256` protects the canonical manifest itself.

The text export is a review representation. Its separators and presentation newline must never be used to reconstruct `expectedBeforeSha256`. Follow-up patches use the metadata `fileManifest` or the live repository bytes.

Optional closure evidence can be embedded without a second export:

```bash
./bin/export.sh full --zip --evidence <evidence.json>
```

The resulting ZIP can be verified with:

```bash
python3 bin/export-integrity-check.py <export.zip> --source-root . --require-evidence
```

Traversal prunes statically excluded runtime trees such as `build/`, `target/`, `.git/`, `exports/` and `patches/logs/validation/` before visiting their files. This keeps export runtime stable after repeated validation runs and prevents active runner logs from invalidating the exported raw-byte snapshot.

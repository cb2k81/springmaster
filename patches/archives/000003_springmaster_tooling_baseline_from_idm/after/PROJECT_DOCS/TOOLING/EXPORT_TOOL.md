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
* `tmp/**`
* `exports/**`
* `.env`
* `patches/archives/**`
* `.idea/**`
* Binär-/Archivdateien

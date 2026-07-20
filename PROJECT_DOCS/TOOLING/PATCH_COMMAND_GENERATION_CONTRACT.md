# Patch Command Generation Contract

## Zweck

Dieses Dokument ist die verbindliche Kurzregel für künftig generierte Patch-Kommandos in Springmaster und in durch Springmaster belieferte Zielprojekte. Es bündelt die Regeln aus Patchsystem, Accept-/Verify-Workflow, Validierungspolitik, projektlokalen Scopes und Platform-Update-Dokumentation so, dass ChatGPT-/LLM-generierte Kommandos nicht mehr auf lange manuelle Apply-Blöcke oder pauschale Git-Kommandos zurückfallen.

Diese Datei ist die bevorzugte Referenz für neue Chats und Folgeaufträge:

```text
Lies und befolge PROJECT_DOCS/TOOLING/PATCH_COMMAND_GENERATION_CONTRACT.md.
```

## Verbindlicher Standard

Für neue Patches ist der Standardabschluss:

```bash
./bin/patch.sh accept <patch.zip> --commit
```

Wenn der Patch unmittelbar veröffentlicht werden soll und der Benutzer das ausdrücklich freigibt:

```bash
./bin/patch.sh accept <patch.zip> --commit --push
```

`--push` impliziert `--commit`. Ein Push darf niemals implizit durch normale Patch-Kommandos erfolgen.

## Preflight-Regel

Vor jedem Patch muss der Working Tree sauber sein:

```bash
git status --short
```

Die Ausgabe muss leer sein. Unabhängige Änderungen, alte Validierungsartefakte oder lokale Experimente müssen vor dem Patchabschluss entweder committed, verworfen oder bewusst aus dem Git-Tracking ausgeschlossen werden.

## Patch-Identität

Generierte Patch-ZIPs müssen Patch Manifest V2 verwenden. Die folgenden Werte müssen konsistent sein:

| Feld / Artefakt | Regel |
|---|---|
| `manifest.schemaVersion` | exakt `springmaster.patch-manifest.v2` |
| `manifest.artifactId` | neue kanonische lowercase UUID-URN für das immutable Artefakt |
| `manifest.id` | Kompatibilitätsalias, exakt identisch zu `manifest.patchId` |
| `manifest.patchId` | repository-lokaler Pflichtwert im Format `000000_name` |
| Archivname | exakt `<patchId>.zip` |
| `manifest.name` | muss dem Namensanteil der `patchId` entsprechen |
| Runner-Erwartung | muss dieselbe `patchId` und nach Möglichkeit dieselbe `artifactId` prüfen |

Runner dürfen nach dem Apply nicht nur `DONE` melden, sondern müssen `./bin/patch.sh show latest` gegen die erwartete lokale Patch-ID prüfen. Bei Abweichung ist der Lauf als fehlerhaft zu behandeln. Die globale `artifactId` darf nicht aus Patchnummer, Sprint, Datum oder Zielprojekt abgeleitet werden.

## Kein `git add .`

Generierte Kommandos dürfen für normale Patch-Abschlüsse niemals verwenden:

```bash
git add .
git add -A
git commit -am ...
```

Staging erfolgt ausschließlich durch das Patchsystem aus der Patch-Dateiliste. Dadurch werden keine fremden Änderungen, abgebrochenen Logs, lokalen Experimente, Exporte oder Build-Artefakte versehentlich in den Commit aufgenommen.

## Akzeptierte Standardkommandos

### Documentation-only

```bash
cd /opt/cocondo/<projekt>
git status --short
./bin/patch.sh accept /home/cb/Downloads/<patch>.zip --profile docs --commit
```

Kein Maven-Test, kein Build.

### Tooling-/Patchsystem-/Export-Patches

```bash
cd /opt/cocondo/<projekt>
git status --short
./bin/patch.sh accept /home/cb/Downloads/<patch>.zip --profile tooling --commit
```

Das Patchsystem führt Shell-/Python-Syntaxprüfung, Tooling-Selfcheck und Full-ZIP-Export aus. Ein Maven-Test wird nur ergänzt, wenn Java-Code, Tests, Build-Konfiguration oder Java-wirksame Templates betroffen sind.

### Java-/Test-/Build-Patches

```bash
cd /opt/cocondo/<projekt>
git status --short
./bin/patch.sh accept /home/cb/Downloads/<patch>.zip --profile code --commit
```

`mvn -q test` ist Pflicht. Im Profil `auto` wird der vollständige Maven-Test automatisch aktiviert, sobald Java-Code, Tests oder Build-Konfiguration betroffen sind.

### Erneute Validierung

```bash
./bin/patch.sh verify latest
```

Für Revalidierung mit Commit ist kein erneutes Apply zulässig. Ein Commit erfolgt nur bei einem `accept`-Lauf.

## Lange Abläufe

Lange inline Shell-Blöcke sollen nicht generiert werden. Für umfangreiche Prüfungen wird ein kleines versioniertes Runner-Skript verwendet, das nur einen kurzen Startbefehl benötigt und Statusdateien schreibt.

Der bevorzugte Start ist trotzdem kurz:

```bash
./bin/patch.sh accept <patch.zip> --background --wait --commit
```

Wenn ein Runner nötig ist, muss er:

1. keine Projektdateien vor `accept --commit` erzeugen, die den Git-Preflight verschmutzen,
2. `accept` mit passendem Profil aufrufen,
3. Status und Summary aus `patches/logs/accept/<patch-id>/` ausgeben,
4. den erzeugten Full-ZIP-Export nennen.

## Logs und Git-Hygiene

Laufzeitlogs aus `patches/logs/accept/**` und `patches/logs/validation/**` sind Diagnoseartefakte und gehören nicht pauschal in normale Patch-Commits. Patch-Changelogs unter den fachlichen Log-Scope-Verzeichnissen, z. B. `patches/logs/docs/CHANGELOG-*.md` oder `patches/logs/root/CHANGELOG-*.md`, bleiben patchrelevante Dateien.

Der Commit enthält nur:

```text
Patch-Dateien aus dem Manifest/Patch-Log
+ erlaubte Patch-Changelogs
+ erlaubte Patch-Metadaten
```

Nicht enthalten sein dürfen:

```text
exports/**
build/**
target/**
patches/runtime/**
patches/logs/accept/**
patches/logs/validation/**
fremde lokale Dateien
```

## Documentation-only-Definition

Ein Documentation-only-Patch darf nur Dokumentationsdateien und den zugehörigen Dokumentations-Changelog ändern, z. B.:

```text
PROJECT_DOCS/**
docs/**
patches/logs/docs/CHANGELOG-*.md
```

Sobald `src/**`, `pom.xml`, Build-Konfiguration, Tooling-Skripte oder DB-/Liquibase-Dateien betroffen sind, ist der Patch kein Documentation-only-Patch mehr.

## Platform-Update-Regel

Für Zielprojekte gilt:

```text
Springmaster erzeugt den Platform-/Tooling-/Core-Update-Patch.
Das Zielprojekt wendet diesen Patch lokal mit seinem eigenen Patchsystem an.
Das Zielprojekt erzeugt anschließend seinen eigenen Full-ZIP-Export.
```

Target-lokale Defaults und Parameter dürfen durch normale Tooling-Updates nicht überschrieben werden:

```text
.env
.env.example
export.config.json
PROJECT_DOCS/CONFIG/**
```

Solche Defaults werden nur über ein explizites Defaults-Profil oder einen bewusst reviewten Zielprojekt-Patch verändert.

## Scopes

Generierte Patches müssen den kleinstmöglichen korrekten Scope verwenden. `root` ist nur zulässig, wenn der Patch mehrere Top-Level-Bereiche oder Git-/Projekt-Metadaten betrifft und ein engerer Scope nicht korrekt wäre.

Projektlokale Zusatzscopes und Namespace-/DB-/Export-Parameter werden aus `.env.example` und `.env` gelesen. Sie dürfen nicht zentral in Springmaster hart kodiert werden.

## Baseline-Regel

Ein Patch wird immer gegen die zuletzt akzeptierte Baseline gebaut:

1. sauberer Git-Stand,
2. letzter Full-ZIP-Export,
3. aktueller `patch.sh show latest`-Stand.

Bei `BASELINE_CONFLICT` wird nicht forciert angewendet. Stattdessen wird ein neuer Patch gegen die tatsächliche aktuelle Baseline gebaut.

## Übergangsregel

Historische manuelle Apply-/Verify-Blöcke in älteren Dokumenten bleiben nur als Diagnose- und Fallback-Hinweise erhalten. Für neue generierte Kommandos ist dieses Dokument maßgeblich.

## Live-Baseline-Pflicht seit 000104

Vor Auslieferung eines generierten Patch-ZIPs muss der Ersteller die Baseline-Annahme gegen den echten Live-Dateistand prüfen:

```bash
./bin/patch.sh live-baseline <patch.zip>
./bin/patch.sh apply --dry-run <patch.zip>
```

Ein erfolgreiches Apply gegen eine rekonstruierte Export-Kopie ist nicht ausreichend, wenn die tatsächlichen Live-Hashes des Zielrepositories nicht geprüft wurden.

Für neue Patches ist `baseline.expectedBeforeSha256` vollständig zu pflegen:

* jeder geänderte oder gelöschte Pfad erhält den aktuellen SHA-256 des Live-Working-Trees,
* jede neue Datei erhält `null` beziehungsweise `missing`,
* Hash-Einträge ohne Patch-Operation sind unzulässig.

Der Standardabschluss über `accept` enthält diesen Guard automatisch. Manuelle Runner müssen ihn explizit vor dem Dry-run ausführen.

## Artifact preflight command contract since 000124

New patch delivery instructions must prefer:

```bash
./bin/patch.sh artifact-preflight <patch.zip>
```

over separate ad-hoc ZIP, live-hash, test-copy and EOF commands. The command output must preserve `ARTIFACT_PREFLIGHT=PASS`, source patch SHA-256, source Git `HEAD` and the JSON report path.

Patch generators must source `expectedBeforeSha256` from live repository bytes or from the export metadata `fileManifest`. They must never reconstruct baseline hashes from the text export body. Generated UTF-8 payload files must use LF, exactly one final newline, no additional EOF blank line and no trailing spaces or tabs.

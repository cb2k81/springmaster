# Patch Accept / Verify Workflow

## Zweck

Der Patch-Abnahme-Workflow reduziert lange manuelle Kommando-Stacks auf kurze, reproduzierbare Befehle.

Seit `000023_springmaster_patch_accept_workflow_hardening` ist der reine Patch-Accept bewusst kurz:

```bash
./bin/patch.sh accept <patch.zip>
```

Seit `000089_springmaster_patch_accept_git_commit_opt_in` kann der validierte Patch-Abschluss zusätzlich explizit in Git übernommen werden:

```bash
./bin/patch.sh accept <patch.zip> --commit
```

Für künftig generierte Patch-Kommandos ist der Command-Generation-Contract maßgeblich:

```text
PROJECT_DOCS/TOOLING/PATCH_COMMAND_GENERATION_CONTRACT.md
```

`accept` führt Dry-run, Apply, Tooling-Prüfung, automatisch passende Tests, einen zentralen Full-ZIP-Export und Summary-Erzeugung aus. Mit `--commit` wird danach nur die Patch-Dateiliste gestaged und committed; `git add .` bleibt verboten.

## Accept

Standard:

```bash
./bin/patch.sh accept <patch.zip>
```

`accept` führt aus:

1. Patch-ZIP lesen und Zielpfade klassifizieren
2. Validierungsprofil automatisch bestimmen
3. Dry-run
4. Apply
5. Anzeige des aktuellen Patchstands
6. Shell-/Python-Syntaxprüfung
7. Tooling-Selfcheck
8. gezielte Tests, falls `--test` angegeben ist
9. vollständiger Maven-Test, falls das Profil Code-/Test-/Build-Änderungen erkennt
10. Full-ZIP-Export
11. Summary-Erzeugung

## Verify

Standard:

```bash
./bin/patch.sh verify latest
```

`verify` führt die Validierung für einen bereits angewendeten Patch erneut aus. Es findet kein erneutes Apply statt. Das Profil wird aus den Pfaden des Patch-Logs abgeleitet.

## Automatische Profile

Das Standardprofil ist `auto`.

| Profil | Wirkung |
|---|---|
| `auto` | bestimmt anhand der Zielpfade, ob `mvn -q test` nötig ist |
| `code` | erzwingt vollständigen Maven-Test |
| `docs` | erzwingt keinen vollständigen Maven-Test |
| `tooling` | erzwingt keinen vollständigen Maven-Test, Tooling-Selfcheck bleibt aktiv |

Beispiele:

```bash
./bin/patch.sh accept <patch.zip> --profile code
./bin/patch.sh accept <patch.zip> --profile docs
./bin/patch.sh verify latest --profile tooling
```

## Manuelle Optionen

Gezielter Test zusätzlich zum automatischen Profil:

```bash
./bin/patch.sh accept <patch.zip> --test CatalogItemControllerTest
```

Vollständigen Test explizit erzwingen:

```bash
./bin/patch.sh accept <patch.zip> --full-test
```

Vollständigen Test explizit unterdrücken:

```bash
./bin/patch.sh accept <patch.zip> --no-full-test
```

Export unterdrücken:

```bash
./bin/patch.sh accept <patch.zip> --no-export
```

## Auto-Regeln

Ein vollständiger Maven-Test wird automatisch aktiviert, wenn der Patch mindestens einen dieser Bereiche betrifft:

```text
pom.xml
build.gradle
build.gradle.kts
settings.gradle
settings.gradle.kts
src/main/java/**
src/test/java/**
src/main/kotlin/**
src/test/kotlin/**
```

Der Full-ZIP-Export ist standardmäßig aktiv. Full-Parts-Baseline-Exporte werden nicht automatisch durch `accept` oder `verify` erzeugt.

## Logs

Die Logs liegen unter:

```text
patches/logs/accept/<patch-id>/
```

Typische Dateien:

```text
dry-run.log
apply.log
show.log
tooling.log
test-<selector>.log
full-test.log
export.log
summary.log
```

## Erfolgsfall

Terminalausgabe:

```text
Patch-Accept:
  Status:       SUCCESS
  Patch-ID:     000123_example
  Profile:      auto
  Full-Test:    True
  Export:       True
  Log:          /opt/cocondo/springmaster/patches/logs/accept/000123_example
  Export-Pfad:  /opt/cocondo/springmaster/exports/text/<export>.zip
```

## Fehlerfall

Im Fehlerfall zeigt das Kommando eine kompakte Fehlerzusammenfassung. Die vollständigen Details stehen in den Logdateien.

## Standardbefehle

Dokumentations-/Policy-Patch ohne Git-Abschluss:

```bash
./bin/patch.sh accept <patch.zip> --profile docs
```

Dokumentations-/Policy-Patch als künftiger Standard mit Git-Abschluss:

```bash
./bin/patch.sh accept <patch.zip> --profile docs --commit
```

Code-/Test-/Build-Patch ohne Git-Abschluss:

```bash
./bin/patch.sh accept <patch.zip> --profile code
```

Code-/Test-/Build-Patch als künftiger Standard mit Git-Abschluss:

```bash
./bin/patch.sh accept <patch.zip> --profile code --commit
```

Erneute Abnahme:

```bash
./bin/patch.sh verify latest
```


## Git-Commit als expliziter Accept-Schritt seit 000089

`accept` kann den validierten Patch-Abschluss optional direkt in Git übernehmen:

```bash
./bin/patch.sh accept <patch.zip> --commit
```

Der Git-Commit ist bewusst **nicht** Standard. Ohne `--commit` bleibt das bisherige Verhalten erhalten: Nach erfolgreichem Accept wird ein prüfbares `git-commit.sh` erzeugt.

Mit `--commit` gilt zusätzlich:

1. Das Projekt muss ein Git-Working-Tree sein.
2. Der Working Tree muss vor dem Patch sauber sein; fremde Änderungen führen zu `GIT_WORKTREE_DIRTY`.
3. Dry-run, Apply, `show latest`, Tooling-Prüfung, Tests und Export müssen erfolgreich sein.
4. Gestaged werden nur Dateien aus dem Patch-Log, niemals `git add .`.
5. Der Git-Index darf keine Dateien außerhalb der Patch-Dateiliste enthalten.
6. Commit-Status, Commit-Hash und optionaler Push-Status werden in `SUMMARY.txt` dokumentiert.

Optional kann nach erfolgreichem Commit gepusht werden:

```bash
./bin/patch.sh accept <patch.zip> --commit --push
```

`--push` impliziert `--commit`. Ein Push erfolgt niemals implizit ohne dieses Flag.

Empfohlene Standards:

```bash
# lokaler, validierter Patchabschluss mit Git-Commit
./bin/patch.sh accept <patch.zip> --background --wait --commit

# nur wenn der geprüfte Stand unmittelbar veröffentlicht werden soll
./bin/patch.sh accept <patch.zip> --background --wait --commit --push
```

## Export-Hygiene seit 000024

Seit `000024_springmaster_patch_accept_export_hygiene` ruft `accept`/`verify` den Tooling-Selfcheck intern mit `--no-export` auf.

Damit gilt:

* Der Tooling-Selfcheck prüft Shell, Python, Patch-Registry und DBTool weiterhin vollständig.
* Der Full-ZIP-Export wird nur noch im expliziten Export-Schritt von `accept`/`verify` erzeugt.
* Der Standardbefehl bleibt kurz:

```bash
./bin/patch.sh accept <patch.zip>
```

Standalone bleibt möglich:

```bash
./bin/tooling-selfcheck.sh
./bin/tooling-selfcheck.sh --no-export
```

## No-op Guard und erneutes Accept

Seit `000029_springmaster_patch_accept_noop_guard_and_state_alignment` prüft `accept` nach dem Dry-run, ob ein Patch überhaupt wirksame Änderungen enthält.

Verhalten:

* Wenn `new`, `modified` oder `deleted` größer als `0` sind, wird der Patch normal angewendet.
* Wenn keine wirksame Änderung vorhanden ist und ein bereits angewendeter Patch mit demselben Namen existiert, wird kein neuer Patch-Eintrag erzeugt. Die Abnahme endet mit `ALREADY_APPLIED`.
* Wenn keine wirksame Änderung vorhanden ist und kein bereits angewendeter Patch mit demselben Namen existiert, bricht `accept` mit `no-effective-change` ab.

Damit verbrauchen wiederholte Accept-Aufrufe keine neuen Patchnummern mehr.

## Projektlokale Scope-Erweiterungen seit 000030

`accept` und `verify` verwenden dieselben Scope-Regeln wie `apply`. Projektlokale Erweiterungen aus `.env` gelten daher auch für die automatische Abnahme.

Beispiel:

```env
PATCH_LOCAL_SCOPES=reporting
PATCH_SCOPE_REPORTING_PATHS=src/main/java/com/example/reporting/**;src/test/java/com/example/reporting/**
```

Danach kann ein Patch mit `manifest.scope=reporting` regulär über den Kurzmodus abgenommen werden:

```bash
./bin/patch.sh accept <patch.zip>
```



## Runtime-Härtung seit 000082

Der kompakte Standardbefehl bleibt gültig:

```bash
./bin/patch.sh accept <patch.zip>
```

Für lange Läufe, insbesondere bei Maven-, Export- oder Zielprojekt-Validierung, ist der robuste Standard:

```bash
./bin/patch.sh accept <patch.zip> --background --wait
```

`--background` startet den eigentlichen Lauf entkoppelt vom Terminal und schreibt die vollständige Ausgabe nach `run.log`. Die Konsole zeigt nur PID, Summary-Pfad, Logpfad und ein kompaktes `tail --pid=... -F ...`-Kommando. `--wait` sorgt dafür, dass parallele Patchläufe kontrolliert auf den projektlokalen Write-Lock warten, statt den Arbeitsbaum gleichzeitig zu verändern.

### Projektweiter Write-Lock

Mutierende Läufe sind pro Projektverzeichnis exklusiv. Der Lock liegt standardmäßig unter:

```text
patches/runtime/locks/project-write.lock
```

Der Lock umfasst den vollständigen Lauf: Dry-run, Apply, `show latest`, Tooling-Prüfung, optionale Tests, Export, Summary und Git-Commit-Skript. Direkte `apply`- und `rollback`-Aufrufe verwenden denselben Lock, sofern sie nicht als `--dry-run` ausgeführt werden.

Bei aktivem Lock bricht der Standardmodus mit `BUSY` ab und nennt Lock-Datei, Owner-PID, Owner-Kommando und Summary-Pfad. Mit `--wait` wartet der Lauf kontrolliert. Optional kann `--lock-timeout <seconds>` gesetzt werden.

### Projektlokale Runtime-Kommandos

Die Patch-Engine ist portable. Tests und Exporte werden nicht hart auf Springmaster verdrahtet, sondern können im Zielprojekt über `.env` konfiguriert werden:

```env
PATCH_LOCK_ROOT=patches/runtime/locks
PATCH_FULL_TEST_COMMAND=mvn -B -ntp test
PATCH_TEST_SELECTOR_COMMAND_TEMPLATE=mvn -B -ntp test -Dtest={test}
PATCH_EXPORT_COMMAND=./bin/export.sh full --zip
PATCH_TOOLING_SELFCHECK_COMMAND=./bin/tooling-selfcheck.sh --no-export
```

Für Zielprojekte mit anderen Buildsystemen dürfen diese Kommandos entsprechend angepasst werden. Die Patch-Engine orchestriert nur; Scopes, Tests und Exporte bleiben projektlokale Verantwortung.

### Summary- und Commit-Artefakte

Jeder Accept-/Verify-Lauf schreibt neben `summary.log` zusätzlich:

```text
SUMMARY.txt
STATUS.txt
git-commit.sh
```

`git-commit.sh` wird nach erfolgreichem Accept als prüfbarer Commit-Vorschlag erzeugt. Das Skript verwendet eine konkrete Dateiliste aus dem Patch-Log und niemals `git add .`. Seit `000084` prüft das Skript zusätzlich den bereits gestagten Git-Index vor dem eigenen `git add`: Sind dort Dateien vorgemerkt, die nicht zur Patch-Dateiliste gehören, bricht es mit `GIT_INDEX_DIRTY` ab. Dadurch können vorbereitete Änderungen aus parallelen Chats oder manuellen Arbeiten nicht versehentlich im Patch-Commit landen. Seit `000089` kann derselbe Guard mit `accept --commit` direkt ausgeführt werden; der Commit bleibt aber explizit opt-in.

## Baseline-Konflikte im Accept-Workflow seit 000085

Wenn ein Patch im Manifest `expectedBeforeSha256`-Preconditions enthält, prüft `accept` diese im Dry-run-Schritt. Bei Abweichungen endet der Lauf mit Fehlerstatus; Details stehen in `dry-run.log` und enthalten `BASELINE_CONFLICT` mit erwartetem und tatsächlichem SHA-256-Wert.

Typischer Fall:

```text
BASELINE_CONFLICT: Aktueller Dateistand passt nicht zum vom Patch erwarteten Vorzustand.
  bin/patch.py
    expectedBeforeSha256: ...
    actualSha256:         ...
```

Ein solcher Patch muss gegen die aktuelle Baseline neu erzeugt oder fachlich rebased werden. Ein erzwungenes Apply ohne passende Baseline ist nicht zulässig.

## Live-Baseline-Schritt seit 000104

Der `accept`-Workflow enthält seit `000104_springmaster_patch_baseline_live_hash_preflight_guard` vor dem Dry-run einen zusätzlichen Schritt:

```text
Patch live baseline preflight
```

Technisch entspricht er:

```bash
./bin/patch.sh live-baseline <patch.zip>
```

Schlägt dieser Schritt fehl, wurde der Patch nicht gegen den aktuellen Working Tree gebaut oder die Manifest-Hash-Abdeckung ist unvollständig. Der Patch darf dann nicht angewendet werden.

## Pre-delivery artifact qualification since 000124

`accept` remains the host-side apply and verification workflow. `artifact-preflight` is the earlier producer-side qualification boundary:

```text
artifact-preflight -> deliver -> accept/apply -> targeted tests -> full tests -> final export
```

Artifact preflight is non-mutating for the live repository and applies only in an isolated worktree. It does not replace host acceptance tests.

Final runners can provide a JSON file through `PATCH_EXPORT_EVIDENCE_FILE` or `export.sh --evidence`. The exporter embeds the prior-gate evidence and its digest together with `exportStatus=COMPLETE`, so one final export is sufficient and a transient runner `STATUS.txt` no longer needs to be interpreted as export completion evidence.
## Transactional acceptance

Effective `accept` runs in a detached Git worktree. The live repository receives the qualified commit and patch evidence only after all configured validation steps succeed. A failed validation must leave live `HEAD`, Working Tree and archive registry unchanged. See `PROJECT_DOCS/TOOLING/PATCH_TRANSACTIONAL_ACCEPTANCE.md`.

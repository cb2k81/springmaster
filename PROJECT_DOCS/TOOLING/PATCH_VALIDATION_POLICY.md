# Patch Validation Policy

## Zweck

## Patch-scoped whitespace and efficiency contract since 000164

Whitespace is a fail-closed correctness check, not a repository-wide formatting task. Acceptance checks only effective patch paths after apply, only staged patch paths before commit and the qualified commit once with `git show --check`. New files are exposed with intent-to-add inside the isolated worktree. Unrelated files are neither scanned repeatedly nor reformatted.

This keeps the gate deterministic and efficient while still rejecting trailing whitespace, conflict markers and malformed patches before live transfer. A whitespace failure is reported as an exact child step and does not mutate the live repository.

Run observation and diagnostics use `status`, `watch`, `wait`, `result` and `diagnose` from `PATCH_RUN_API.md`; full logs are not streamed into interactive terminals.


Diese Richtlinie definiert die Verifikation nach Patch-Typen. Sie verhindert unnötige Build- und Testläufe bei reinen Dokumentationsänderungen und stellt gleichzeitig sicher, dass Code- und Tooling-Änderungen ausreichend geprüft werden.

## Grundsatz

Die Validierung richtet sich nach dem tatsächlichen Patch-Inhalt, nicht allein nach der Patch-Nummer.

Jeder Patch wird mindestens mit Dry-run, Apply, Patch-Log und Full-ZIP-Export abgeschlossen. Build- und Testbefehle werden nur dort ausgeführt, wo sie zur geänderten Artefaktklasse passen. Full-Parts-Baseline-Exporte werden nur erzeugt, wenn sie für Review, Wiederherstellung oder explizite Baseline-Übergabe benötigt werden.

Seit `000140` gehört Patch Manifest V2 zur Mindestvalidierung. `schemaVersion`, globale `artifactId`, lokale `patchId`, Kompatibilitätsfeld `id`, Archivname und Runner-Erwartung müssen übereinstimmen. Ein neues Artefakt ohne kanonische UUID-URN, mit abweichendem Archivnamen oder mit einer im Repository bereits unter anderer `patchId` archivierten `artifactId` ist ungültig und darf weder per `apply` noch per `accept` verarbeitet werden. Historische V1-Archive bleiben lesbar.


## Command-Generation-Contract seit 000090

Für künftig generierte Kommandos ist zusätzlich verbindlich:

```text
PROJECT_DOCS/TOOLING/PATCH_COMMAND_GENERATION_CONTRACT.md
```

Neue generierte Patch-Abschlüsse verwenden `accept --commit`, nicht manuelle Apply-Blöcke und niemals `git add .`. Die in diesem Dokument enthaltenen manuellen Blöcke sind nur noch Fallback und Diagnosehilfe.

## Standardabnahme seit 000023

Der bevorzugte Standard für neue Patches ist der automatische Abnahme-Workflow:

```bash
./bin/patch.sh accept <patch.zip>
```

Das Profil `auto` ist Standard. Es aktiviert den vollständigen Maven-Test automatisch, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind. Für reine Dokumentations-, Planungs- oder Tooling-Patches wird kein Maven-Test ausgeführt, solange keine Java-/Build-Wirkung erkennbar ist.

Gezielte Tests können ergänzt werden:

```bash
./bin/patch.sh accept <patch.zip> --test <MavenTest>
```

Die automatische Entscheidung kann überschrieben werden:

```bash
./bin/patch.sh accept <patch.zip> --full-test
./bin/patch.sh accept <patch.zip> --no-full-test
./bin/patch.sh accept <patch.zip> --profile code
./bin/patch.sh accept <patch.zip> --profile docs
```

Bereits angewendete Patches werden ohne erneutes Apply validiert:

```bash
./bin/patch.sh verify latest
```

Der Full-ZIP-Export ist standardmäßig aktiv und kann mit `--no-export` abgeschaltet werden. Die Detailausgaben werden unter `patches/logs/accept/<patch-id>/` gespeichert. Die Terminalausgabe bleibt ausgabearm.

## Patch-Kategorien

| Kategorie | Typische Dateien | Build/Test-Regel |
|---|---|---|
| Documentation-only | `docs/**`, `PROJECT_DOCS/**`, `patches/logs/docs/**` | kein `mvn test`, kein `./bin/build.sh` |
| Planning-only | `PROJECT_DOCS/PLANNING/**`, `patches/logs/planning/**` | kein `mvn test`, kein `./bin/build.sh` |
| Template-only | `PROJECT_DOCS/TEMPLATES/**`, `platform/templates/**` | kein Master-`mvn test`; Template-Generator-Tests nur wenn Generator/Template-Erzeugung betroffen ist |
| Tooling | `bin/**`, `export.config.json`, Tooling-Dokumentation | Shell-/Python-Syntaxprüfung und `./bin/tooling-selfcheck.sh`; `mvn test` nur bei Build-/Projektstrukturwirkung |
| Java-Code | `src/main/java/**` | `mvn test` ist Pflicht |
| Tests | `src/test/**` | `mvn test` ist Pflicht |
| Build-Konfiguration | `pom.xml`, buildrelevante Ressourcen | `mvn test` und bei Bedarf `./bin/build.sh` sind Pflicht |
| DB/Liquibase | `src/main/resources/db/**` | `./bin/dbtool.sh validate-stage` oder begründete Ersatzprüfung; bei Java-Bezug zusätzlich `mvn test` |

## Documentation-only-Standard

Für neue generierte Kommandos ist der Standardabschluss:

```bash
cd /opt/cocondo/springmaster
git status --short
./bin/patch.sh accept <patch.zip> --profile docs --commit
```

Nicht ausführen:

```bash
mvn test
./bin/build.sh
git add .
```

Manuelle `apply --dry-run`-/`apply`-Blöcke bleiben nur Fallback und Diagnosehilfe, wenn `accept` nicht verfügbar ist.

## Code-Patch-Standard

Für Java-Code-, Test- oder Build-Konfigurationspatches ist der generierte Standardabschluss:

```bash
cd /opt/cocondo/springmaster
git status --short
./bin/patch.sh accept <patch.zip> --profile code --commit
```

`mvn -q test` ist dabei Pflicht und wird vom Profil `code` beziehungsweise im Profil `auto` durch Java-/Test-/Build-Zielpfade aktiviert. Je nach Inhalt kommen spezifische Prüfungen hinzu, z. B. DBTool-, Export-, OpenAPI- oder Project-New-Prüfungen.

## Tooling-Patch-Standard

Für Shell-/Python-/Export-/Patchsystem-Änderungen ist der generierte Standardabschluss:

```bash
cd /opt/cocondo/springmaster
git status --short
./bin/patch.sh accept <patch.zip> --profile tooling --commit
```

Das Patchsystem führt Shell-/Python-Syntaxprüfung, Tooling-Selfcheck und Full-ZIP-Export aus. `mvn -q test` wird bei Tooling-Patches nur ergänzt, wenn der Patch Build-Konfiguration, Projektstruktur, Template-Erzeugung mit Java-Projektwirkung oder Java-Code berührt.

## Abbruchregel

Wenn ein Patch nicht eindeutig einer Kategorie zugeordnet werden kann, gilt die strengere Validierungskategorie.

Wenn ein Documentation-only-Patch versehentlich Code-, Build-, Tooling- oder Ressourcenänderungen enthält, ist er kein Documentation-only-Patch und muss entsprechend neu klassifiziert oder abgebrochen werden.

## Core-Patches mit Build-Konfiguration

Core-Patches dürfen `pom.xml` nur dann ändern, wenn die Änderung unmittelbar für Core-Code oder dessen Tests erforderlich ist. Ein solcher Patch ist kein reiner Core-Code-Patch, sondern mindestens `Java-Code + Build-Konfiguration` beziehungsweise `Build-Konfiguration`.

Pflichtprüfung:

```bash
mvn test
```

Bei reinen Dependency-Vorbereitungen ohne Java-Code genügt zusätzlich zur Patch- und Tooling-Prüfung der Maven-Test als Build-Kompatibilitätsnachweis.

## Core-Patches mit Versionsdatei

Core-Code-Patches dürfen `platform/versions/platform.env` ändern, wenn die Änderung ausschließlich der nach `SPRINGMASTER_VERSION_POLICY.md` erforderlichen Core-Versionierung dient.

Validierung:

* `mvn test` ist Pflicht, sobald Java-Code oder Tests betroffen sind.
* Die Versionsdatei muss shell-kompatibel ladbar bleiben.
* Die geänderte Core-Version muss im Patch-Changelog erwähnt werden.
* Nicht betroffene Teilversionen dürfen nicht pauschal erhöht werden.

## Full-ZIP-Standard seit 000016

Der reguläre Abschluss eines Patch-Kommandostacks erzeugt aktuell nur einen Full-ZIP-Export.

```bash
./bin/export.sh full --zip
ls -1t exports/text/*_export_full_*.zip | head -n 1
```

Full-Parts-Baseline-Exporte bleiben möglich, werden aber nicht mehr pauschal erzeugt. Sie sind für gezielte Reviews oder explizite Baseline-Übergaben vorgesehen.

## Demo-Patches mit Versionsdatei

Demo-Patches dürfen `platform/versions/platform.env` ändern, wenn die Änderung ausschließlich der nach `SPRINGMASTER_VERSION_POLICY.md` erforderlichen Demo-Versionierung dient.

Validierung:

* `mvn test` ist Pflicht, sobald Java-Code oder Tests betroffen sind.
* Die Versionsdatei muss shell-kompatibel ladbar bleiben.
* Die geänderte Demo-Version muss im Patch-Changelog erwähnt werden.
* Nicht betroffene Teilversionen dürfen nicht pauschal erhöht werden.


## Übergangsregel

Die manuellen Standardblöcke in dieser Richtlinie bleiben als Fallback dokumentiert. Sobald `accept` oder `verify` verfügbar ist, ist die ausgabearme Abnahme über diese Kommandos vorzuziehen.

Beispiele:

```bash
./bin/patch.sh accept /home/cb/Downloads/000123_example.zip --export
./bin/patch.sh accept /home/cb/Downloads/000124_code_change.zip --full-test --export
./bin/patch.sh verify latest --full-test --export
```


## Tooling-Selfcheck seit 000023

Der Tooling-Selfcheck prüft weiterhin Patchsystem, Export und DBTool-Status, erzeugt aber im Standard nur noch einen Full-ZIP-Export. Full-Parts-Baseline-Exporte sind optional und werden nur noch explizit erzeugt.

## Patch-Accept-Standard seit 000024 / 000090

Der bevorzugte technische Accept bleibt ein einzelner ausgabearmer Befehl:

```bash
./bin/patch.sh accept <patch.zip>
```

Für neu generierte Patch-Abschlüsse mit Git-Integration gilt seit `000090`:

```bash
./bin/patch.sh accept <patch.zip> --commit
```

Die manuell dokumentierten Kommandoblöcke bleiben nur Fallback und Diagnosehilfe.

Export-Regel im Accept-/Verify-Workflow:

* `tooling-selfcheck.sh` wird intern mit `--no-export` ausgeführt.
* Der Full-ZIP-Export wird anschließend genau einmal im Workflow erzeugt, sofern `--no-export` nicht angegeben wurde.
* Für Java-/Test-/Build-Konfigurationsänderungen wird `mvn -q test` im Profil `auto` automatisch aktiviert.

## Platform-Update-Patches mit Versionsdatei

Platform-Update-Patches dürfen `platform/versions/platform.env` ändern, wenn die Änderung ausschließlich der nach `SPRINGMASTER_VERSION_POLICY.md` erforderlichen Platform-Update-Versionierung dient.

Validierung:

* Shell-Syntax und Python-Kompilierung bleiben Pflicht, sobald Tooling betroffen ist.
* `./bin/tooling-selfcheck.sh --no-export` ist im `accept`-/`verify`-Workflow Pflicht.
* `mvn -q test` ist nur Pflicht, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind.
* Nicht-invasive Zielprojekt-Update-Kommandos dürfen im Foundation-Stand keine Zielprojekte verändern.
* Reale Zielprojektänderungen über `target-apply` dürfen nur ausgeführt werden, wenn der Ziel-Deskriptor `TARGET_DELIVERY_ENABLED=true` enthält.


## Platform-Update-Generate-Patches

Für Patches, die `platform-update generate` erweitern, gilt:

* Shell-Syntaxprüfung für `bin/platform-update.sh` ist Pflicht.
* `./bin/platform-update.sh generate <target> --profile <profile> --dry-run` muss ohne Zielprojektänderung ausführbar sein.
* Eine reale Generierung darf nur unter `build/platform-update/generated/**` schreiben.
* Zielprojektpfade aus `TARGET_PATH` dürfen im Foundation-Stand nicht beschrieben werden.
* `mvn -q test` ist nur Pflicht, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind.

## No-op-Reaccepts

Ein `accept`-Lauf ohne wirksame Dateiveränderung darf keine neue Patchnummer erzeugen. Wenn der Patch bereits wirksam angewendet wurde, gilt der Reaccept als `ALREADY_APPLIED` und kann optional erneut Verifikation und Full-ZIP-Export ausführen.

Ist kein passender bereits angewendeter Patch vorhanden, muss der Lauf mit `no-effective-change` abbrechen.

## Projektlokale Scopes

Projektspezifische zusätzliche Scopes und Zusatzpfade werden in der lokalen `.env` des jeweiligen Projekts gepflegt. Sie werden nicht zentral in Springmaster verdrahtet.

Die Validierungskategorie richtet sich weiterhin nach den tatsächlichen Zielpfaden. Enthält ein lokaler Scope Java-Code, Tests oder Build-Konfiguration, aktiviert `accept` im Profil `auto` weiterhin den vollständigen Maven-Test.


## Platform-Update-Apply-Plan-Patches

Für Patches, die `platform-update apply-plan` erweitern, gilt:

* Shell-Syntaxprüfung für `bin/platform-update.sh` ist Pflicht.
* Die Erzeugung eines Apply-Plans muss ohne Zielprojektänderung ausführbar sein.
* Planartefakte dürfen nur unter `build/platform-update/manifests/**` erzeugt werden.
* Zielprojektpfade aus `TARGET_PATH` dürfen im Foundation-Stand nicht während der Planerzeugung beschrieben werden.
* `mvn -q test` ist nur Pflicht, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind.


## Platform-Update Target Compatibility

Für Platform-Update-Patches, die Target-Compatibility-Pläne erzeugen, gilt:

* Sie dürfen Zielprojekte nicht direkt verändern.
* Sie dürfen Compatibility-ZIPs nur unter `build/platform-update/generated/**` erzeugen.
* Sie dürfen Apply-/Compatibility-Artefakte nur unter `build/platform-update/manifests/**` erzeugen und keine ausführbaren Zieländerungs-Skripte erzeugen.
* Projektspezifische Zusatz-Scopes und Zusatzpfade müssen in der Zielprojekt-`.env` konfiguriert werden.
* `mvn -q test` ist nur erforderlich, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind.



## Target lifecycle and delivery guard since 000079

Für Target-Registry-/Platform-Update-Patches gilt zusätzlich:

* Der erste geplante Springmaster-belieferte Zielname ist `zbm`.
* Laufende Projekte wie `idm` und `personnel` müssen als nicht belieferbar dokumentiert bleiben, solange keine explizite Reclassification erfolgt.
* Initialisierung und Update müssen getrennt beschrieben werden. Initialisierung erzeugt ein neues Projekt; Updates übertragen später Core, Tools, Defaults oder Doku in ein akzeptiertes Ziel.
* `TARGET_DELIVERY_ENABLED=false` ist der sichere Default. Ein Patch darf diese Einstellung nur mit expliziter Begründung auf `true` setzen.
* Ein Platform-Update-Patch mit Shell-Änderungen muss mindestens `bash -n bin/platform-update.sh` validieren. Maven ist nur erforderlich, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind.



## Robuster Patch-Abnahmestandard seit 000082

Für alle Patches bleibt `accept` der bevorzugte Abschluss. Bei potenziell langen Validierungen ist der Standard:

```bash
cd /opt/cocondo/springmaster
./bin/patch.sh accept /home/cb/Downloads/<patch>.zip --background --wait
```

Der Lauf schreibt vollständige Logs und eine kompakte `SUMMARY.txt`. Die Konsole darf nicht mit Maven- oder Testausgaben geflutet werden. Maven-Standardkommandos verwenden künftig `-B -ntp`, sofern das jeweilige Projekt nichts anderes konfiguriert.

Manuelle Kommandoblöcke sind nur noch Diagnose- oder Fallbackpfad. Sie dürfen nicht als bevorzugter Standard verwendet werden, wenn `accept`/`verify` verfügbar ist.

## Rollback-Testpflicht für Patchsystem-Änderungen

Änderungen am Patchsystem müssen mindestens in einem Fixture-Projekt prüfen:

* Patch mit neuer Datei, geänderter Datei und gelöschter Datei anwenden.
* `rollback --dry-run latest` ausführen.
* `rollback latest` ausführen.
* prüfen, dass neue Dateien entfernt, geänderte Dateien zurückgesetzt und gelöschte Dateien wiederhergestellt werden.
* zweiten Rollback kontrolliert ablehnen.
* `show latest` muss den Status `rolled_back` anzeigen.

Rollback darf nicht parallel zu einem laufenden mutierenden Patchlauf ausgeführt werden. Der projektlokale Write-Lock ist daher auch für Rollback verpflichtend.

## Zielprojekt-Portabilität

Ein nach Zielprojekten deployedes Patchsystem muss dort konsistent mit lokalen Scopes, lokalen Tests, lokalen Logs, lokalem Lock und lokalem Export funktionieren. Springmaster darf keine projektspezifischen Zielprojekt-Scopes zentral hart kodieren. Zielprojekte definieren Abweichungen über `.env` und Scope-Konfiguration.

## Git-Index-Guard seit 000084

Der durch `patch.sh accept` erzeugte Git-Commit-Vorschlag darf nie fremde staged Änderungen übernehmen. Deshalb muss das generierte `git-commit.sh` vor dem eigenen `git add` den bestehenden Git-Index prüfen. Enthält der Index Dateien, die nicht in der patchbezogenen Dateiliste stehen, muss das Skript mit `GIT_INDEX_DIRTY` abbrechen.

Die Patchsystem-Integrationstests müssen dieses Szenario über ein Fixture-Projekt prüfen: Eine fremde Datei wird vor Ausführung des Commit-Skripts gestaged, das Commit-Skript wird gestartet und muss kontrolliert fehlschlagen, ohne patchbezogene Dateien zu stagen oder einen Commit zu erzeugen.


## Git-Commit-Opt-in seit 000089

Das Patchsystem darf Git-Commits automatisieren, aber nur als expliziten Accept-Schritt:

```bash
./bin/patch.sh accept <patch.zip> --commit
```

Verbindliche Regeln:

* `--commit` ist nur für `accept` zulässig, nicht für `verify` oder direktes `apply`.
* Vor dem mutierenden Lauf muss der Git-Working-Tree sauber sein; andernfalls Abbruch mit `GIT_WORKTREE_DIRTY`.
* Der Commit darf erst nach erfolgreichem Dry-run, Apply, Validierung und Export erfolgen.
* Staging erfolgt ausschließlich anhand der Patch-Log-Dateiliste.
* `git add .` bleibt verboten.
* `--push` ist ein eigenes Flag, impliziert `--commit` und darf niemals Standardverhalten sein.
* Commit-Status, Commit-Hash und Push-Status müssen im Accept-Summary dokumentiert werden.

Die Integrationstests müssen mindestens einen erfolgreichen `accept --commit` in einem Git-Fixture-Projekt prüfen.

## Baseline-Hash-Preconditions seit 000085

Patchsystem-Änderungen und andere Patches mit Kollisionsrisiko sollen den erwarteten Vorzustand der betroffenen Dateien im Manifest deklarieren. Das Patchsystem unterstützt dafür `expectedBeforeSha256`, `baseline.expectedBeforeSha256` und `baseline.expectedBefore`.

Die Prüfung ist Bestandteil von `apply --dry-run`, `apply` und damit auch von `accept`, weil `accept` den Dry-run vor dem Apply ausführt. Ein Konflikt muss mit `BASELINE_CONFLICT` abbrechen. Der Lauf darf keine Patchnummer verbrauchen und keine Dateien verändern.

Die Integrationstests des Patchsystems müssen mindestens einen Fixture-Fall enthalten, in dem ein Patch mit gültigem erwarteten SHA erzeugt wird, die Datei anschließend extern verändert wird und `apply --dry-run` den Patch kontrolliert ablehnt. Danach muss derselbe Patch gegen den erwarteten Vorzustand wieder erfolgreich im Dry-run laufen.

Baseline-Hash-Preconditions ersetzen nicht den projektweiten Write-Lock. Beide Schutzmechanismen sind komplementär: Locking verhindert gleichzeitige Mutationen, Hash-Preconditions verhindern stale sequentielle Patches.

## Live-Baseline-Hash-Preflight seit 000104

Die Mindestvalidierung eines neuen Patch-Abschlusses umfasst seit `000104` zusätzlich den Live-Baseline-Hash-Preflight:

```bash
./bin/patch.sh live-baseline <patch.zip>
```

Der Guard läuft im `accept`-Workflow vor dem normalen Dry-run. Er verhindert, dass ein Patch mit unvollständiger, veralteter oder nur gegen eine rekonstruierte Baseline geprüfter `expectedBeforeSha256`-Map akzeptiert wird.

Bei einem Fehler der Klassen `LIVE_BASELINE_HASH_MISSING`, `LIVE_BASELINE_HASH_INCOMPLETE`, `LIVE_BASELINE_HASH_UNSUPPORTED` oder `LIVE_BASELINE_HASH_MISMATCH` ist der Patch neu gegen den aktuellen Live-Stand zu erstellen. Ein Entfernen der Hash-Map ist keine zulässige Reparatur.

## Artifact qualification policy since 000124

A patch artifact is delivery-ready only after `patch.sh artifact-preflight` has passed against a clean committed baseline. The preflight must reject incomplete or mismatching live hashes, unchanged operations, CRLF, missing final LF, extra EOF blank lines and trailing spaces/tabs.

A passing reconstructed test directory is not sufficient unless the directory is a detached Git worktree at the same source `HEAD` and the complete live hash map has also passed. Hashes taken from the presentation text of a Full Text Export are forbidden. Only the raw-byte `fileManifest` values in export metadata format version 2 are authoritative.

The isolated qualification must prove exact operation scope, byte-identical applied payloads, `git diff --check` and one verified full export. `--no-export` is permitted only for focused fixture tests or when a later runner stage performs and verifies the single final export.

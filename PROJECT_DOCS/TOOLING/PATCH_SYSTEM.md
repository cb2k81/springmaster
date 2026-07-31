# Patch System

## Zweck

Das Patchsystem verarbeitet manifestbasierte Patch-ZIPs und protokolliert jede Anwendung unter `patches/archives/**`.

## Kanonische Run- und Git-Steuerung seit 000164

Die verbindliche Runtime-Schnittstelle ist in `PROJECT_DOCS/TOOLING/PATCH_RUN_API.md` definiert. Patchstarts, Statusabfragen und Diagnosen werden nicht mehr durch manuelle Prozesssuche oder Auswahl der zeitlich neuesten Summary gesteuert.

```bash
./bin/patch.sh accept <patch.zip> --background --wait-for-lock --no-export --commit --watch
./bin/patch.sh result --patch <patch-id> --format env
./bin/patch.sh diagnose <run-id>
./bin/patch.sh doctor
```

`accept` ist idempotent: ein bereits angewendetes Artefakt liefert `ALREADY_APPLIED`, ein aktiver identischer Run `ALREADY_RUNNING`. Ein späterer fehlgeschlagener redundanter Versuch kann einen kanonisch akzeptierten Git-Commit nicht auf `FAILED` zurückstufen. `verify` besitzt eigene Validation-Evidence und überschreibt keine Acceptance-Evidence.

Die Git-Transaktion vergleicht Patch-Log, qualifizierten Worktree-Commit und Live-Transferpfade exakt. Whitespace wird nur für betroffene Patchpfade geprüft; es gibt keine implizite Formatierung oder wiederholte Full-Repository-Scans.

## Kommandos

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
./bin/patch.sh accept <patch.zip> [--background] [--format human|env|json] [--watch] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export] [--commit] [--push]
./bin/patch.sh verify <patch-id|patch-number|latest> [--background] [--format human|env|json] [--watch] [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export]
./bin/patch.sh status [<run-or-patch-ref>|--patch <patch-id>] [--format human|env|json]
./bin/patch.sh watch [<run-or-patch-ref>|--patch <patch-id>] [--interval <seconds>] [--timeout <seconds>]
./bin/patch.sh wait [<run-or-patch-ref>|--patch <patch-id>] [--interval <seconds>] [--timeout <seconds>]
./bin/patch.sh result [<run-or-patch-ref>|--patch <patch-id>] [--format human|env|json]
./bin/patch.sh diagnose <run-id|patch-id|patch-number|latest> [--output <file>]
./bin/patch.sh doctor
./bin/patch.sh list
./bin/patch.sh show latest
./bin/patch.sh rollback --dry-run latest
./bin/patch.sh rollback latest
```


## Command-Generation-Contract seit 000090

Für künftig generierte Kommandos ist die zentrale Kurzregel verbindlich:

```text
PROJECT_DOCS/TOOLING/PATCH_COMMAND_GENERATION_CONTRACT.md
```

Neue Patch-Kommandos sollen grundsätzlich `accept --commit` verwenden, sofern das Projekt bereits die Git-Commit-Integration enthält und der Working Tree sauber ist. `git add .` und pauschale manuelle Commits sind für normale Patch-Abschlüsse nicht zulässig. Push erfolgt nur mit explizitem `--push` oder nach separater Benutzerfreigabe.

## Patch-Format

```text
manifest.json
files/**
logs/CHANGELOG-*.md
```

Optional:

```text
delete/**
```

## Patch Manifest V2 seit 000140

Neue Patch-ZIPs verwenden den Vertrag aus:

```text
PROJECT_DOCS/TOOLING/PATCH_MANIFEST_V2.md
```

Verbindliche Identitätsfelder sind:

```json
{
  "schemaVersion": "springmaster.patch-manifest.v2",
  "artifactId": "urn:uuid:<canonical-lowercase-uuid>",
  "id": "000140_example",
  "patchId": "000140_example",
  "name": "example"
}
```

`artifactId` identifiziert das unveränderliche Artefakt global und sequenzunabhängig. `patchId` steuert nur die lokale Apply-Reihenfolge und den Archivnamen. Innerhalb eines Repositories darf dieselbe `artifactId` nicht unter einer anderen `patchId` archiviert werden.

Historische V1-Archive bleiben für `list`, `show` und Rollback lesbar. Neue V1-Artefakte ohne Schema und globale Identität werden beim Live-Baseline- und Artifact-Preflight fail-closed abgelehnt. `manifest.id` bleibt vorerst als Kompatibilitätsalias erhalten und muss `manifest.patchId` entsprechen.

## Erweiterte Scopes seit 000003

Zusätzlich zu den Bootstrap-Scopes sind vorbereitet:

* `templates`
* `planning`
* `target-registry`
* `platform-update`

Damit können spätere Patches die Project-Skeleton-, Planungs- und Zielprojektbereiche ohne Umgehung des Patchsystems pflegen.

## Validierung nach Patch-Typ

Die Patch-Anwendung besteht immer aus Dry-run, Apply und Patch-Log-Prüfung. Die anschließende Verifikation richtet sich nach dem Patch-Inhalt.

Für reine Dokumentationspatches werden kein Maven-Test und kein Build ausgeführt. Für Code-, Test- und Build-Konfigurationspatches ist `mvn test` verpflichtend. Tooling-Patches benötigen Shell-/Python-Syntaxprüfung und den Tooling-Selfcheck; ein Maven-Test wird nur ergänzt, wenn der Patch Build-Konfiguration, Projektstruktur, Java-Code oder Template-Erzeugung mit Java-Projektwirkung betrifft.

Die verbindliche Detailregel steht in:

```text
PROJECT_DOCS/TOOLING/PATCH_VALIDATION_POLICY.md
```

## Core-Scope-Ausrichtung seit 000009

Der Patch-Scope `core` ist seit `000009_springmaster_core_scope_alignment` auf den kanonischen verteilbaren Core-Namespace ausgerichtet:

```text
pom.xml
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
PROJECT_DOCS/CORE/**
patches/logs/core/**
```

Core-Code unter `de.cocondo.platform.core` ist nicht zulässig. `de.cocondo.platform.*` bleibt der ausführbaren Springmaster-Anwendung und Demo-Code vorbehalten.

Seit `000012_springmaster_core_persistence_dependency_preparation` darf der Scope `core` zusätzlich `pom.xml` enthalten. Diese Öffnung ist ausschließlich für dependency-relevante Core-Patches vorgesehen. Sobald `pom.xml` betroffen ist, gilt der Patch validierungsseitig als Build-Konfigurationspatch und benötigt `mvn test`.

## Core-Scope und Versionsdatei

Seit Patch `000014_springmaster_core_version_scope_alignment` enthält der Scope `core` zusätzlich:

```text
platform/versions/platform.env
PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md
```

Grund ist die Versionierungspflicht für Core-Code- und Core-API-Änderungen. Ein Core-Patch darf dadurch die Core-Änderung und die zugehörige Versionserhöhung in einem atomaren Patch ausliefern.

Der Core-Scope darf dadurch nicht für allgemeine Platform-Änderungen missbraucht werden. Zulässig sind ausschließlich Versionsänderungen mit unmittelbarem Bezug zur Core-Änderung sowie begleitende Präzisierungen der Version Policy.

## Demo-Scope und Versionsdatei

Seit Patch `000016_springmaster_demo_version_scope_alignment` enthält der Scope `demo` zusätzlich:

```text
platform/versions/platform.env
PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md
```

Grund ist die Versionierungspflicht für Demo-Domänen. Ein Demo-Patch darf dadurch die Demo-Code-Änderung und die zugehörige Demo-Versionserhöhung in einem atomaren Patch ausliefern.

Der Demo-Scope bleibt auf `de.cocondo.platform.demo` begrenzt. Wiederverwendbarer Core-Code gehört weiterhin ausschließlich unter `de.cocondo.system`.


## Patch-Abnahme-Workflow seit 000022

Patch `000022_springmaster_patch_accept_verify_workflow` ergänzt zwei ausgabearme Standardkommandos für die tägliche Patch-Abnahme.

### `accept`

```bash
./bin/patch.sh accept <patch.zip> --full-test --export
```

Der Befehl kapselt:

* Dry-run
* Apply
* `show latest`
* Shell-/Python-Syntaxprüfung
* Tooling-Selfcheck
* optionale gezielte Maven-Tests per `--test`
* optionalen vollständigen Maven-Test per `--full-test`
* optionalen Full-ZIP-Export per `--export`
* strukturierte Logs und Summary

Die Detailausgaben landen unter:

```text
patches/logs/accept/<patch-id>/
```

Die Terminalausgabe bleibt bewusst kurz und enthält nur Status, Patch-ID, Logpfad und Exportpfad.

### `verify`

```bash
./bin/patch.sh verify latest --full-test --export
```

Der Befehl führt die Verifikation für einen bereits angewendeten Patch erneut aus, ohne den Patch nochmals anzuwenden.

Das ist vorgesehen für:

* nachträgliche Regressionstests
* erneute Exporterzeugung
* CI-/Terminal-Probleme
* erneute Abnahme nach Umgebungskorrekturen

### Gezielte Tests

```bash
./bin/patch.sh accept <patch.zip> --test CatalogItemControllerTest --export
```

`--test` führt aus:

```bash
mvn -q test -Dtest=<MavenTest>
```

Mehrere `--test`-Optionen sind zulässig.

### Fehlerzusammenfassung

Bei Fehlern erzeugt das Patchsystem eine kompakte Zusammenfassung in:

```text
patches/logs/accept/<patch-id>/summary.log
```

Gesucht wird unter anderem nach:

```text
ERROR
FAILURE
Exception
Caused by:
BUILD FAILURE
Failed to execute
```

Damit entfallen manuelle `tail`-/`grep`-/`tee`-Blöcke im Standardablauf.


## Accept-/Verify-Hardening seit 000023

Seit Patch `000023_springmaster_patch_accept_workflow_hardening` ist der kurze Standardbefehl ausreichend:

```bash
./bin/patch.sh accept <patch.zip>
```

Das Patchsystem ermittelt im Profil `auto` anhand der Zielpfade, ob ein vollständiger Maven-Test notwendig ist. Java-Code, Tests und Build-Konfiguration aktivieren automatisch `mvn -q test`. Dokumentations- und reine Tooling-Patches verzichten automatisch auf den Maven-Test.

Der Full-ZIP-Export ist standardmäßig aktiv. Er kann mit `--no-export` abgeschaltet werden. Full-Parts-Baseline-Exporte werden durch `accept` und `verify` nicht automatisch erzeugt.

## Platform-Update-Scope und Versionsdatei seit 000025

Der Patch-Scope `platform-update` unterstützt seit `000025_springmaster_platform_update_foundation` neben `bin/platform-update.sh`, `platform/update/**` und der Target-Update-Dokumentation auch:

```text
platform/versions/platform.env
PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md
```

Damit können spätere Platform-Update-Patches die nach Version Policy erforderliche `PLATFORM_UPDATE_VERSION` atomar mit der Tool-/Regeländerung aktualisieren.


## Platform-Update-Generate seit 000026

`bin/platform-update.sh generate` erzeugt aus einem Zielprojekt-Deskriptor ein target-lokales Plan-Patch-ZIP.

```bash
./bin/platform-update.sh generate zbm --profile core --dry-run
./bin/platform-update.sh generate zbm --profile core
```

Der generierte Patch verändert Zielprojekte nicht automatisch. Er wird unter `platform/update/generated/**` abgelegt und kann später manuell in einem Zielprojekt geprüft werden.

Der aktuelle Payload ist bewusst ein Dokumentations-Patch unter `PROJECT_DOCS/PLATFORM_UPDATES/**`; echte Core-/Tooling-Payload-Dateien folgen erst nach weiterer Mapping- und Scope-Validierung.

## No-op-Schutz im Accept-Workflow

`patch.sh accept` darf wiederholte Anwendungen desselben Patch-ZIPs nicht als neue fachliche Patches archivieren. Der Accept-Workflow wertet deshalb den Dry-run aus, bevor `apply` ausgeführt wird.

Ein Patch gilt als wirksam, wenn mindestens einer der folgenden Zähler größer als `0` ist:

```text
new
modified
deleted
```

Nur wirksame Patches werden angewendet und archiviert. Bereits angewendete No-op-Wiederholungen werden als `ALREADY_APPLIED` protokolliert.

## Projektlokale Scopes aus `.env` seit 000030

Seit `000030_springmaster_patch_project_local_scope_env` kann jedes Projekt das Patch-Scope-Modell lokal erweitern, ohne gemeinsame Springmaster-Scopes zentral zu verändern.

Bestehende Scopes können per `.env` zusätzliche Pfade erhalten:

```env
PATCH_SCOPE_DEMO_EXTRA_PATHS=src/main/java/com/example/demo/**;src/test/java/com/example/demo/**
```

Zusätzliche lokale Scopes werden ebenfalls in `.env` definiert:

```env
PATCH_LOCAL_SCOPES=reporting
PATCH_SCOPE_REPORTING_PATHS=src/main/java/com/example/reporting/**;src/test/java/com/example/reporting/**
PATCH_SCOPE_REPORTING_LOG_DIR=reporting
```

Details stehen in:

```text
PROJECT_DOCS/TOOLING/PATCH_PROJECT_LOCAL_SCOPES.md
```


## Platform-Update-Scope und Apply-Plan-Dokumente

Seit `000031_springmaster_platform_update_target_patch_apply_plan` umfasst der Standard-Scope `platform-update` auch die Platform-Update-spezifischen Dokumente `PROJECT_DOCS/TOOLING/PLATFORM_UPDATE*.md`. Dadurch können Generator-, Payload- und Apply-Plan-Dokumentation zusammen mit `bin/platform-update.sh` atomar gepflegt werden.





## Projektlokale Runtime-Sicherheit seit 000082

Das Patchsystem ist ab diesem Stand als portable Engine definiert. Springmaster pflegt die kanonische Implementierung, aber ein nach Zielprojekten deployedes Patchsystem muss im jeweiligen Projekt mit dessen lokalen Scopes, Tests, Exportprofilen und Policies funktionieren.

Mutierende Kommandos sind projektweit exklusiv:

```bash
./bin/patch.sh accept <patch.zip> --background --wait
./bin/patch.sh apply --wait <patch.zip>
./bin/patch.sh rollback --wait latest
```

Der lokale Write-Lock liegt standardmäßig unter `patches/runtime/locks/project-write.lock`. Er schützt insbesondere Patchnummern, Arbeitsbaum, Tests, Exporte, Rollbacks und Git-Abschluss vor parallelen KI-Chat-Läufen im selben Projektverzeichnis. Runtime-Locks sind Laufzeitartefakte und dürfen weder versioniert noch in Full-Exporte übernommen werden.

`accept` und `verify` können mit `--background` gestartet werden. `--format env|json` liefert die Run-ID maschinenlesbar, `--watch` verbindet Start und kompakte Beobachtung. Die vollständige Ausgabe bleibt in projektlokalen Logdateien; externe Startlogs, Run-ID-Dateien und Summary-Pointer sind nicht erforderlich und dürfen insbesondere nicht nach `~/Downloads` geschrieben werden.

Zielprojekte konfigurieren abweichende Runtime-Kommandos in ihrer lokalen `.env`, z. B. `PATCH_FULL_TEST_COMMAND`, `PATCH_EXPORT_COMMAND` und `PATCH_TOOLING_SELFCHECK_COMMAND`. Projektspezifische Scopes bleiben ebenfalls lokal über `PATCH_LOCAL_SCOPES` und `PATCH_SCOPE_<NAME>_PATHS` definiert.

Nach erfolgreichem Accept erzeugt das Patchsystem ein projektlokales `git-commit.sh` im Accept-Logverzeichnis. Dieses Skript staged ausschließlich patchbezogene Dateien aus dem Patch-Log und verwendet kein pauschales `git add .`. Seit `000084` ist zusätzlich ein Index-Guard verpflichtend: Das Commit-Skript darf nicht fortfahren, wenn bereits fremde Dateien im Git-Index vorgestaged sind. Der Lauf muss dann mit `GIT_INDEX_DIRTY` abbrechen und die fremden staged Dateien ausgeben.

Seit `000089` kann `accept` den Commit-Schritt mit `--commit` selbst ausführen. Dieser Modus ist explizit und nicht Standard. Vor dem Patch muss der Working Tree sauber sein; bei fremden Änderungen bricht der Lauf mit `GIT_WORKTREE_DIRTY` ab. Der Commit erfolgt erst nach erfolgreichem Dry-run, Apply, Validierung und Export. `--push` ist separat erforderlich und impliziert `--commit`; ohne `--push` wird niemals automatisch gepusht.

## Baseline-Hash-Konfliktprüfung seit 000085

Patch-ZIPs können im `manifest.json` einen erwarteten Vorzustand für betroffene Dateien deklarieren. Die Patch-Engine prüft diese Werte bereits im `apply --dry-run` und erneut vor dem mutierenden `apply`. Passt der aktuelle Dateistand nicht zum erwarteten Vorzustand, bricht der Lauf mit `BASELINE_CONFLICT` ab und verändert keine Dateien.

Unterstützte Manifest-Formate:

```json
{
  "scope": "tooling",
  "name": "example",
  "expectedBeforeSha256": {
    "bin/patch.py": "<sha256>",
    "PROJECT_DOCS/TOOLING/new-file.md": null
  }
}
```

Alternativ kann die Information unter `baseline.expectedBeforeSha256` oder als Liste unter `baseline.expectedBefore` stehen. Ein Wert `null`, `missing` oder `absent` bedeutet: Die Datei darf vor dem Patch noch nicht existieren.

Diese Prüfung ergänzt den projektweiten Write-Lock. Der Lock verhindert parallele Mutationen im selben Projektverzeichnis. Die Hash-Prüfung erkennt zusätzlich stale Patches, die zwar nacheinander ausgeführt werden, aber gegen eine ältere Baseline vorbereitet wurden.

## Live-Baseline-Preflight seit 000104

Patch `000104_springmaster_patch_baseline_live_hash_preflight_guard` ergänzt ein nicht-mutierendes Preflight-Kommando:

```bash
./bin/patch.sh live-baseline <patch.zip>
```

Das Kommando prüft die im Manifest hinterlegte `baseline.expectedBeforeSha256`-Map vollständig gegen den aktuellen Working Tree. Für jede Patch-Operation muss ein erwarteter Vorzustand eingetragen sein. Bei neuen Dateien ist der erwartete Wert `null` beziehungsweise `missing`.

`accept` führt diesen Guard automatisch vor `apply --dry-run` aus. Dadurch werden Patches, die gegen rekonstruierte oder veraltete Baselines gebaut wurden, in einem expliziten Schritt `live-baseline` abgelehnt.

Details stehen in:

```text
PROJECT_DOCS/TOOLING/PATCH_BASELINE_LIVE_HASH_PREFLIGHT_GUARD.md
```

## Patch Artifact Preflight since 000124

Before delivery, a finished patch ZIP can be qualified non-mutating against the exact committed baseline:

```bash
./bin/patch.sh artifact-preflight <patch.zip>
```

The command requires a clean Git working tree, complete live hashes and hygienic text payloads. It performs the live preflight and dry-run, applies the patch in an isolated detached Git worktree, verifies exact changed paths, payload bytes and Git executable classes (`100644`/`100755`), runs `git diff --check`, and by default creates and verifies one full ZIP export.

Full exports use metadata format version 2. `fileManifest` contains authoritative raw-byte `sizeBytes` and `sha256` values for every included source file. The rendered text export is a review representation and must not be used to calculate patch baseline hashes.

Details:

```text
PROJECT_DOCS/TOOLING/PATCH_ARTIFACT_PREFLIGHT_HARDENING.md
```

## Root-AGENTS-Scope seit 000136

Die Repository-Arbeitsanweisung `AGENTS.md` ist ein kontrollierter Patchpfad. Sie ist in den Scopes `root` und `docs` erlaubt. Dadurch kann die Arbeitsanweisung erst nach der expliziten Scope-Erweiterung als eigener, baselinegebundener Patch aufgenommen und später dokumentarisch gepflegt werden.

Die Scope-Erweiterung ist bewusst getrennt von der erstmaligen Anlage der Datei: Der alte Patch-Preflight muss Patch `000136` noch ohne einen zuvor unbekannten Rootpfad validieren können.
## Transactional acceptance

Effective `accept` runs in a detached Git worktree. The live repository receives the qualified commit and patch evidence only after all configured validation steps succeed. A failed validation must leave live `HEAD`, Working Tree and archive registry unchanged. See `PROJECT_DOCS/TOOLING/PATCH_TRANSACTIONAL_ACCEPTANCE.md`.
## Run-API-Cutover und historische Evidence

Seit Patch `000164_springmaster_patch_run_api_git_transaction_hardening` ist kanonische Acceptance-Evidence Bestandteil des verbindlichen Patchabschlusses. Der Doctor bewertet ältere angewendete Patcharchive ohne `accepted.json` als aggregierte historische Warnung. Für Patchnummern ab `000164` ist derselbe Zustand `APPLIED_WITHOUT_CANONICAL_ACCEPTANCE` ein Fehler.

Statusabfragen verwenden eine nicht leere Run-ID oder Patch-ID; `--patch <patch-id>` ist die explizite patchbezogene Form. Leere Referenzen werden abgelehnt und fallen nie auf das aktuelle Verzeichnis zurück. Jeder Run besitzt eine sanitierte `invocation.json` ohne absoluten Downloadpfad. Temporäre, zeitgestempelte Summary-Pfade sind keine stabilen Schnittstellen und dürfen insbesondere bei Selbstupdates nicht als dauerhafte Pointer verwendet werden. Die Statusauflösung liest die kanonische `accepted.json` und liefert Run-ID, Artifact-ID, Commit und Aktualisierungszeit auch dann, wenn der ursprüngliche Attempt-Pfad bereits entfernt oder kompaktiert wurde.


## Live-Umgebungsdiagnose vor extern vorbereiteten Patches

Extern vorbereitete Lieferungen dürfen eine Exportbaseline nicht als vollständige Live-Qualifikation darstellen. Vor der Konstruktion eines Patches mit repositoryweiter Governance-, Git- oder Toolingwirkung ist auf dem DEV-System ein rein lesender Diagnoseprozess auszuführen. Er muss mindestens committed HEAD, Working Tree, Linked Worktrees, aktive Toolkit-Version, Scopes, Validatoren, Manifestvertrag, Directory-Gate-Baseline und relevante getrackte/ignorierte Pfade erfassen.

Die Patchvorbereitung verwendet anschließend zwei getrennte Evidence-Stände:

- Baseline-Report auf dem unveränderten Integrations-HEAD,
- Kandidaten-Report nach der Änderung in einem dedizierten Worktree.

Die Qualifikation bewertet den semantischen Diff. Bereits vorhandene Findings dürfen nicht als durch den Kandidaten neu verursacht gelten; neue Regeln dürfen historischen Bestand aber auch nicht still pauschal freigeben. Sicher entfernbarer Runtime- und Generated-Bestand wird in einem eigenen Cleanup-Schnitt gelöscht.

Delivery-Wrapper müssen jeden Preflight-Schritt mit Status und Logpfad ausweisen. Bei einem Fehler sind die eigentliche Ursache und ein Diagnosearchiv unter `patches/work/` bereitzustellen. Eine fehlende Run-ID darf die vorherige Preflightursache nicht verdecken.

Statusbegriffe sind strikt zu verwenden: Producer- oder Exportprüfung ist keine Live-Qualifikation; `PASS` eines report-only Gates bedeutet zunächst nur erfolgreiche Ausführung. Null neue Findings, erfolgreiche Planung, Dry-run und Accept sind jeweils eigene Nachweise.

## Cocondo Patch Toolkit 1.1.1 activation

The canonical mutating workflow is now:

```bash
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
: "${COCONDO_WORKTREE_ROOT:?set a local worktree root}"
: "${COCONDO_ARTIFACT_ROOT:?set a local artifact root}"
WORKTREE="${COCONDO_WORKTREE_ROOT}/<name>"

git -C "$PROJECT_ROOT" worktree add "$WORKTREE" -b change/<name> main
cd "$WORKTREE"
./bin/cpatch workspace init --name <name> --scope <scope>
# implement and commit the bounded change
./bin/cpatch create --base <base-commit> --head HEAD \
  --scope <scope> --patch-id <local-id> --title "<title>" \
  --output "${COCONDO_ARTIFACT_ROOT}/<delivery-directory>"

cd "$PROJECT_ROOT"
./bin/cpatch plan <patch.zip>
./bin/process-ops.sh patch-dry-run <patch.zip>
# after explicit review
./bin/process-ops.sh patch-accept <patch.zip>
```

`cpatch` runs dry-run and acceptance through the same isolated qualification pipeline. Worktree and workspace binding are mandatory, `main` is the integration branch, effective path-derived validators cannot be downgraded, and disjoint integration progress triggers bounded full requalification.

The legacy `patch.sh` engine is no longer a live mutation path in the canonical Springmaster checkout. It remains available for historical `list`, `show`, `status`, `doctor`, diagnostics, verification, live-baseline, artifact-preflight and dry-run compatibility. Legacy `accept`, non-dry-run `apply` and non-dry-run `rollback` fail with `LEGACY_PATCH_MUTATION_DISABLED`.

The activation contract and its machine-readable evidence are validated by:

```bash
./bin/patch-toolkit-activation.sh --check
./bin/patch-toolkit-activation-it.sh
```

Both checks are part of `./bin/tooling-selfcheck.sh --no-export`.

## Process Operations refinement

Operational patch runs use the project-neutral process adapter rather than a second shell orchestrator:

```bash
./bin/process-ops.sh resolve
./bin/process-ops.sh patch-dry-run <patch.zip> --profile auto
./bin/process-ops.sh watch <run-id>
./bin/process-ops.sh result <run-id>
# after explicit review
./bin/process-ops.sh patch-accept <patch.zip> --profile auto
```

The adapter resolves the integration worktree from Git, delegates worker ownership directly to `cpatch`, stores operational pointers below the Git common directory and keeps default terminal output compact. Dry-run and accept are separate promotion decisions. External `nohup`, `setsid`, PID files and polling supervisors around a detached Toolkit run are non-canonical.

A caller may operate from a linked feature worktree. Mutation still checks the configured integration worktree, while observation never stages, resets or otherwise modifies the caller's worktree. Managed-project rollout remains blocked until the Springmaster pilot scenarios in the process-operations contract are complete.


## Exact split staging since 000194

Patch qualification must stage the manifest path set without weakening ignore protection. The Toolkit partitions the exact normalized manifest paths after apply:

- paths already present in the Git index are staged with `git add -u`; this includes modifications and deletions below directories that are ignored today,
- additions are staged separately with normal `git add` and without `--force`,
- both operations use NUL-separated literal pathspec input,
- the final staged path set must equal the manifest path set exactly.

A single `git add --all -- <manifest-paths>` call is prohibited. Git may stage a deleted tracked file below an ignored directory and still return a non-zero status, which makes the command unsuitable as the transactional staging primitive. Regression coverage must include ignored tracked deletions, rejected ignored additions, mixed changes, special filenames and path sets above 1,000 entries.

## Runtime archive audit after directory-governance adoption

Patch archives and acceptance/validation logs are local runtime evidence, not committed product source. Exact cleanup patches may remove their formerly tracked files while empty directory skeletons remain temporarily in a worktree. `patch-state-audit` ignores only such empty skeletons. As soon as a directory contains a file or symlink, the normal fail-closed archive contract applies and a missing or unreadable `patch-log.json` is blocking.


## Central writer and delivery hardening candidate

The current hardening candidate keeps `cpatch` as the only patch worker owner and extends `process-ops` as the single operator facade. Every patch start and every diagnostic, incident, handoff or delivery-preparation writer executes the same fail-closed workspace-start lifecycle. No writer creates `patches/work` implicitly.

External artifact configuration is not authorization. Relative artifact use requires an exact Git-common authorization record bound to the configured canonical directory, device and inode. Delivery preparation itself remains below the Git-common process state and does not require the external root.

Patch and delivery numbering is derived only from typed delivery directories, Toolkit run records and canonical acceptance records. Known historical metadata is counted without reserving an ID; unknown or unsafe inventory entries block. Legacy numeric-only run IDs reserve a number only through exact `cocondo.run-record.v1` patch-command evidence whose UUID and artifact filename reconstruct one canonical full patch ID. Exactly one `cocondo.patch-acceptance.v2` record is the canonical owner of its local number. A differently named terminal failed run under that accepted owner is retained as `IGNORE_AND_COUNT`; a delivery, non-failed run or second accepted owner with a different identity remains blocking. The current delivery exception is exact and single-use. These candidate semantics are not accepted until the complete candidate passes the canonical dry-run and separate accept.

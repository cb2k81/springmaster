# Patch System

## Zweck

Das Patchsystem verarbeitet manifestbasierte Patch-ZIPs und protokolliert jede Anwendung unter `patches/archives/**`.

## Kommandos

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
./bin/patch.sh accept <patch.zip> [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export] [--commit] [--push]
./bin/patch.sh verify <patch-id|patch-number|latest> [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export]
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

`accept` und `verify` können mit `--background` gestartet werden. Die vollständige Ausgabe landet in Logdateien, während die Konsole nur Status, PID, Summary, Logpfad und Folgekommando ausgibt.

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

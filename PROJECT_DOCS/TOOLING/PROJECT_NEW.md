# Project-New Tool

## Zweck

`bin/project-new.sh` erzeugt neue Cocondo Java-Backend-Projekte aus dem versionierten Springmaster Project Skeleton.

Das Tool ist konservativ ausgelegt: Ein bestehendes nicht-leeres Zielverzeichnis wird nicht überschrieben.

## Standardaufrufe

```bash
./bin/project-new.sh --help
./bin/project-new.sh create --dry-run --name sample --path /tmp/springmaster-sample
./bin/project-new.sh create --name sample --path /tmp/springmaster-sample
```

## Parameter

| Parameter | Pflicht | Bedeutung |
|---|---:|---|
| `--name` | ja | Projektname, z. B. `sample` |
| `--path` | ja | Zielpfad, muss leer oder noch nicht vorhanden sein |
| `--artifact-id` | nein | Maven `artifactId`, Default: `--name` |
| `--group-id` | nein | Maven `groupId`, Default: `de.cocondo.<name ohne Bindestriche>` |
| `--base-package` | nein | Java-Basispaket, Default: `groupId` |
| `--application-class` | nein | Spring-Boot-Application-Klasse, Default: `<NamePascalCase>Application` |
| `--port` | nein | HTTP-Port, Default: `8080` |
| `--db-name` | nein | Datenbankname, Default: Projektname mit `_` statt `-` |
| `--stage-db-name` | nein | Stage-/Build-Datenbankname, Default: `<db-name>_build` |

## Erzeugte Bestandteile

Das Zielprojekt enthält:

* Maven-/Spring-Boot-Basis
* minimale Application und `/api/platform/info`
* `.env.example`, aber keine `.env`
* `bin/patch.sh` / `bin/patch.py`
* `bin/patch-artifact-preflight.py` mit Integrationstest
* `bin/export.sh`
* `bin/export-integrity-check.py` mit Integrationstest
* `bin/dbtool.sh`
* `bin/build.sh`
* projektlokales `bin/tooling-selfcheck.sh`
* report-only Documentation-, Directory- und Sprint-Gates samt Contracts und Fixtures
* Governance-Adoption, leere Deviation-/Risikoausgangsstände und Managed State
* Sprint- und Governance-Dokumentvorlagen
* `platform/versions/platform.env`
* Bootstrap-Nachweis unter `PROJECT_DOCS/BOOTSTRAP/`
* registrierten Bootstrap-Eintrag unter `patches/archives/000001_project_new_bootstrap/`

## Verifikation eines erzeugten Projekts

```bash
cd /tmp/springmaster-sample
git init
git add -A
git commit -m 'bootstrap: project-new baseline'
./bin/patch.sh list
./bin/documentation-gate.sh --check-all
./bin/project-directory-gate.sh --profile generated-project --check-all
./bin/sprint-gate.sh --check-all
./bin/tooling-selfcheck.sh --no-export
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
./bin/dbtool.sh status
mvn test
```

## Abgrenzung

Das Tool erzeugt noch keine fachliche Demo-Domäne und überträgt keinen Platform Core. Diese Bestandteile folgen in separaten, validierten Patches.

## Instantiation Acceptance seit 000076

Patch `000076_springmaster_project_new_instantiation_acceptance_review` ergänzt einen reproduzierbaren Acceptance-Nachweis für `project-new.sh`.

Neuer Prüfbefehl:

```bash
./bin/project-new-acceptance.sh --skip-generated-maven-test
./bin/project-new-acceptance.sh --generated-maven-test
```

Der Acceptance-Lauf erzeugt ein Beispielprojekt unter `target/project-new-acceptance/sample-backend`, prüft Dry-run, Create, Patch-Bootstrap, vollständige Mitgabe des Artifact-Preflight- und Exportintegritäts-Toolings, Export samt Integritätsprüfung, DBTool-Status, Token-Rendering und optional `mvn test` im generierten Projekt.

Wichtig: Kopierte Tooling-Dateien werden jetzt so tokenisiert, dass DBTool-Defaults auch ohne `.env` sanitizierte Datenbanknamen verwenden. Für `sample-backend` wird beispielsweise `sample_backend` und `sample_backend_build` verwendet, nicht der hyphenated Projektname.


## Generated Service Slice Readiness seit 000077

Patch `000077_springmaster_generated_service_slice_readiness_plan` trennt die technische Projektanlage bewusst von der späteren fachlichen Slice-Erzeugung.

`project-new.sh` bleibt die konservative erste Stufe: Es erzeugt ein lauffähiges Backend-Skeleton mit Tooling, Patch-Bootstrap, Export und DBTool-Konfiguration. Ein fachlicher Aggregate-Slice wird nicht automatisch erzeugt.

Die zweite Stufe wird separat geplant:

```text
PROJECT_DOCS/TOOLING/GENERATED_SERVICE_SLICE_READINESS_PLAN.md
```

Dort werden Core-Verteilung, Slice-Blueprint, DTO-/Validation-/Error-Contract, Evidence und Acceptance-Kriterien für einen später generierten fachlichen Service-Slice festgelegt.




## Namespace- und Export-Kontrakt

`project-new` erzeugt `APP_EXPORT_PROJECT_KEY`, `APP_BASE_PACKAGE`, `APP_CORE_PACKAGE` und projektlokale Patch-Scopes in `.env.example`. Dadurch funktionieren Export, DBTool und Patchsystem auch ohne `.env` mit projektlokalen Defaults. Gemeinsame Tool-Updates müssen diese Werte referenzieren und dürfen sie im Profil `tooling` nicht überschreiben.

## Artifact-Preflight-Kompatibilität seit 000124

Project-New übernimmt die vollständige Laufzeitkette für `patch.sh artifact-preflight` und den Exportintegritätscheck. Dadurch referenzieren `patch.sh` und `tooling-selfcheck.sh` in einem neu erzeugten Projekt ausschließlich tatsächlich mitgelieferte Dateien. Die Instantiation Acceptance prüft diese Vollständigkeit sowie einen realen Full-ZIP-Export mit `EXPORT_INTEGRITY=PASS`.

Die maschinenlesbaren Schema-IDs der Tooling-Verträge bleiben bei der Projekttokenisierung kanonisch (`springmaster.*.v1`). Sie werden nicht auf den Projektnamen umgeschrieben, damit Exporte und Preflight-Reports zwischen Master- und Zielprojekten portabel validierbar bleiben.

## Patch Manifest V2 seit 000140

Der registrierte Bootstrap-Eintrag eines neu erzeugten Projekts verwendet `springmaster.patch-manifest.v2`. `project-new` erzeugt pro Projekt eine neue globale UUID-basierte `artifactId`; die lokale Bootstrap-`patchId` bleibt `000001_project_new_bootstrap`. Manifest und Bootstrap-Log müssen dieselbe globale Identität tragen.

## Lokaler Governance-Harness seit 000174

Patch `000174_springmaster_project_new_governance_harness` materialisiert einen minimalen, lokal ausführbaren Governance-Harness in jedes frisch erzeugte Projekt. Project-New kopiert dabei nicht die vollständige Springmaster-Governance. Es liefert ausschließlich die für die eigenständige Projektbaseline erforderlichen Verträge, Gates, Fixtures, Templates und projektspezifischen Nachweise.

Ein erzeugtes Projekt enthält insbesondere:

- `AGENTS.md` als lokalen Einstieg für menschliche, automatisierte und KI-gestützte Arbeit,
- einen V2-Dokumentationsindex,
- `GOVERNANCE_ADOPTION.md` und einen maschinenlesbaren Adoption Record,
- registrierte leere Deviation- und Risikoausgangsstände,
- einen initialen Managed State,
- Documentation-, Project-Directory- und Sprint-Contracts,
- report-only Gates für Dokumentation, Verzeichnisstruktur und Sprints,
- die zugehörigen 10, 17 und 21 Fixture-Szenarien,
- allgemeine Governance- und Sprint-Templates,
- einen projektlokalen Selfcheck, der ausschließlich mitgelieferte Werkzeuge aufruft.

Die kanonischen Schema-IDs bleiben unverändert `springmaster.*`. Projektname und lokale Scope-Werte werden nur an den dafür vorgesehenen Stellen materialisiert. Der Directory Contract verwendet im Fresh Project das Profil `generated-project`; die Directory Transition Baseline startet leer.

Die Instantiation Acceptance etabliert im erzeugten Projekt zunächst eine eigenständige lokale Git-Baseline. Anschließend prüft sie, dass das Fresh Project ohne manuelle Reparatur:

```bash
./bin/documentation-gate.sh --check-all
./bin/project-directory-gate.sh --profile generated-project --check-all
./bin/sprint-gate.sh --check-all
./bin/tooling-selfcheck.sh --no-export
```

besteht. Die Gates bleiben report-only, solange keine gesonderte Promotion nach Quality Gate Governance erfolgt.

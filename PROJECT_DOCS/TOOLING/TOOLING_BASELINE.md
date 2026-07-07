# Tooling Baseline 000003

## Ziel

Patch `000003_springmaster_tooling_baseline_from_idm` stabilisiert das Bootstrap-Tooling und bereitet spätere deterministische Umsetzungsschritte vor.

## Enthaltene Bereiche

* gemeinsame Shell-Helfer unter `bin/lib/core/**`
* DBTool-Bibliothek unter `bin/lib/dbtool/**`
* erweiterter Export mit Split-Exporten
* erweitertes Patch-Scope-Modell
* lokales Buildtool mit Runtime-ZIP
* `bin/tooling-selfcheck.sh` als verifizierbarer Tooling-Test

## Nicht enthalten

* keine Java-Core-Migration
* keine IDM-Fachdomäne
* keine automatische Projektanlage
* kein Zielprojekt-Updategenerator

## Pflichtprüfung

Für Tooling-Änderungen gilt grundsätzlich:

```bash
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
```

`mvn test` ist bei Tooling-Patches nur Pflicht, wenn der Patch Build-Konfiguration, Projektstruktur, Java-Code oder Template-Erzeugung mit Java-Projektwirkung betrifft.

## Core Scope Alignment 000009

Patch `000009_springmaster_core_scope_alignment` richtet die technischen Tooling-Regeln auf die Namespace-Entscheidung aus Patch `000007` aus.

Betroffen sind:

* `bin/patch.py`: Scope `core` erlaubt künftig `src/main/java/de/cocondo/system/**` und `src/test/java/de/cocondo/system/**`.
* `export.config.json`: Exportprofil `core` exportiert denselben kanonischen Core-Pfad.
* Dokumentation: Patchsystem und Umsetzungsplan benennen die korrigierte Scope-Regel.

Nicht betroffen sind Java-Code, Maven-Konfiguration, Ressourcen und Templates.

## Stand nach 000014

Patch `000014_springmaster_core_version_scope_alignment` erweitert die Scope-Regeln so, dass Core-Patches die zentrale Versionsdatei `platform/versions/platform.env` atomar mit der Core-Code-Änderung aktualisieren können.

Damit wird die Versionierungspflicht aus der Springmaster Version Policy technisch durch das Patchsystem unterstützt.

## Stand nach 000016

Patch `000016_springmaster_demo_version_scope_alignment` erweitert die Scope-Regeln so, dass Demo-Patches die zentrale Versionsdatei `platform/versions/platform.env` atomar mit der Demo-Code-Änderung aktualisieren können.

Außerdem wird der reguläre Kommandoabschluss auf einen Full-ZIP-Export begrenzt, um unnötige Exportdaten zu vermeiden. Full-Parts-Baseline-Exporte bleiben optional.

Versionierung:

```text
PLATFORM_VERSION=0.3.1-foundation
PLATFORM_TOOLING_VERSION=0.2.2
PLATFORM_BASELINE_KIND=full-zip
```


## Patch-Abnahme seit 000022

Das Tooling enthält seit `000022_springmaster_patch_accept_verify_workflow` einen standardisierten Abnahme-Workflow im Patchsystem.

Neue Kommandos:

```bash
./bin/patch.sh accept <patch.zip> [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export]
./bin/patch.sh verify <patch-id|patch-number|latest> [--profile auto|docs|tooling|code] [--test <MavenTest>] [--full-test|--no-full-test] [--export|--no-export]
```

Ziel ist die Ablösung langer manueller Kommando-Stacks durch kurze, reproduzierbare Abnahmekommandos mit dauerhaften Logs und kompakter Fehlerzusammenfassung.


## Stand nach 000023

Patch `000023_springmaster_patch_accept_workflow_hardening` reduziert den Standardbefehl weiter:

```bash
./bin/patch.sh accept <patch.zip>
./bin/patch.sh verify latest
```

Das Profil `auto` ist Standard. Es entscheidet anhand der geänderten Zielpfade, ob ein vollständiger Maven-Test auszuführen ist. Der Full-ZIP-Export ist standardmäßig aktiv.

Der Tooling-Selfcheck erzeugt seit diesem Stand nur noch einen Full-ZIP-Export. Full-Parts-Baseline-Exporte bleiben explizite Review-/Wiederherstellungsartefakte.

## Stand nach 000024

Patch `000024_springmaster_patch_accept_export_hygiene` härtet die Exportlogik des Abnahme-Workflows.

`accept` und `verify` rufen den Tooling-Selfcheck nun mit `--no-export` auf, damit der Workflow nicht zwei Full-ZIP-Exporte erzeugt. Standalone behält `./bin/tooling-selfcheck.sh` sein bisheriges Verhalten und kann mit `--no-export` explizit ausgabearm verwendet werden.

Der Standard für neue Patches bleibt:

```bash
./bin/patch.sh accept <patch.zip>
```

## Stand nach 000025

Patch `000025_springmaster_platform_update_foundation` operationalisiert den ersten konservativen Schritt der Zielprojekt-Update-Mechanik.

Neu ist ein nicht-invasiver Planungsmodus in `bin/platform-update.sh`:

```bash
./bin/platform-update.sh list
./bin/platform-update.sh show zbm
./bin/platform-update.sh validate all
./bin/platform-update.sh plan zbm --profile core
```

Der Patch erzeugt noch keine Zielprojekt-Patch-ZIPs und schreibt nicht in Zielpfade. Dadurch bleibt die Einführung der Target-Update-Mechanik deterministisch und risikoarm.


## Platform-Update-Generate seit 000026

Das Platform-Update-Tool besitzt jetzt neben `list`, `show`, `validate` und `plan` einen ersten `generate`-Befehl.

Der Befehl erzeugt target-lokale Plan-Patch-ZIPs, aber noch keine produktiven Update-Payloads. Damit wird das Patchformat für Zielprojektupdates früh validierbar, ohne Zielprojekte zu verändern.

## Stand 000029 – Accept No-op Guard

Patch `000029_springmaster_patch_accept_noop_guard_and_state_alignment` ergänzt den Accept-Workflow um einen No-op-Schutz und korrigiert den State-Pointer nach der tatsächlichen Anwendung des Platform-Update-Core-Payload-Mappings als `000028`.

Der Standardbefehl bleibt:

```bash
./bin/patch.sh accept <patch.zip>
```

## Stand nach 000030 – Projektlokale Patch-Scopes

Patch `000030_springmaster_patch_project_local_scope_env` ergänzt das Patchsystem um projektlokale Scope-Erweiterungen aus `.env`.

Damit bleibt Springmaster die gemeinsame Tooling-Basis, während Fachprojekte eigene Zusatzbereiche definieren können, ohne zentrale Scope-Tabellen zu verändern.


## Platform-Update Apply-Plan seit 000031

`bin/platform-update.sh` kann seit `000031_springmaster_platform_update_target_patch_apply_plan` für generierte Zielpatches einen Apply-Plan erzeugen. Der Befehl bleibt nicht-invasiv und schreibt standardmäßig nur unter `build/platform-update/manifests/**`.


## Stand nach 000033 – Target Compatibility Plan

Patch `000033_springmaster_platform_update_target_compatibility_plan` ergänzt `platform-update` um einen nicht-invasiven Kompatibilitätsplan für Zielprojekte, deren lokales Patchsystem generierte Springmaster-Patches noch nicht akzeptiert.

Der konkrete Auslöser war der Zielprojekt-Preflight-Befund:

```text
Unbekannter Patch-Scope im manifest.json: core
```

Der neue Befehl erzeugt ein Kompatibilitäts-ZIP und ein manuell zu prüfendes Skript, verändert das Zielprojekt aber nicht automatisch.

## Report-only Gate Tooling Seed 000068

Patch `000068_springmaster_report_only_gate_tooling_seed` adds standalone report-only gate tooling.

New commands:

```bash
./bin/springmaster-gates.sh report
./bin/springmaster-gates-selfcheck.sh
```

The selfcheck is part of the tooling validation baseline for future gate-tooling changes. It validates Python syntax, report generation, JSON parseability, non-empty findings, G0 rule-source coverage and at least one G1 diagnostic.

The first implementation is intentionally not Maven-bound and not strict. It produces diagnostics only under `target/springmaster-gates/**`.


## Report-only Gate Regression and Maven Profile 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` hardens the gate tooling introduced by patch 000068.

New tooling artifact:

```text
bin/springmaster-gates-regression.sh
```

New test artifact:

```text
src/test/java/de/cocondo/platform/tooling/SpringmasterGatesReportProfileTest.java
```

New Maven profile:

```text
springmaster-gates-report
```

The profile is intentionally report-only. It must not make rule findings strict. It fails only when the gate tool cannot execute or cannot produce a valid report.

## Report-only Gate Findings Baseline 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` adds a documentation-only review for the first report-only gate findings baseline.

The baseline keeps the existing tooling behavior unchanged. It records that the current report contains `12` expected findings with no `BLOCKER` and no `ERROR`. The findings are used as interpretation baseline for future Catalog-demo candidate work and gate evolution.

## Catalog-demo Candidate Slice Contract Plan 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` does not change gate tooling. It adds a documentation bridge from the report-only findings baseline to the first Catalog-demo candidate implementation patch.

Tooling impact:

- the current report-only findings remain accepted baseline diagnostics;
- no finding is promoted to strict;
- the gate runner behavior remains unchanged;
- future Catalog-demo code work should use the plan to prove that G1, G4 and G5 findings become better candidate evidence rather than accidental strict failures.

## Gate findings interpretation after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` keeps `PLATFORM_TOOLING_VERSION=0.3.9` unchanged.

No tool code changes are introduced. The review documents that the current gate runner still reports `9` findings after the CatalogItem candidate foundation and that G5 candidate detection should be improved in a later tooling/demo-alignment patch.



## Tooling baseline after 000074

Patch `000074_springmaster_catalog_demo_candidate_slice_alignment` raises the report-only gate tooling baseline to `PLATFORM_TOOLING_VERSION=0.3.10`.

Additional behavior:

- `input-manifest.json` contains `catalogDemoEvidence`;
- `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json` is recognized as machine-readable candidate evidence;
- G5 no longer reports manual review for a classifiable `candidate-reference-slice` that is explicitly `not-canonical`;
- regression and selfcheck scripts assert candidate evidence handling and continued target-scan exclusion.

## Project-New Instantiation Acceptance 000076

Patch `000076_springmaster_project_new_instantiation_acceptance_review` raises the tooling baseline to `PLATFORM_TOOLING_VERSION=0.3.11`.

New tooling artifact:

```text
bin/project-new-acceptance.sh
```

New test artifact:

```text
src/test/java/de/cocondo/platform/tooling/ProjectNewInstantiationAcceptanceTest.java
```

The acceptance proves that a generated Java backend skeleton can be created, bootstrapped, exported and checked with DBTool status. It also verifies that DBTool defaults in copied tooling are rendered with sanitized database identifiers.

The acceptance does not promote target delivery or strict gates. It remains a local Springmaster instantiation proof for new technical backend baselines.


## Generated Service Slice Readiness 000077

Patch `000077_springmaster_generated_service_slice_readiness_plan` does not change executable tooling and keeps `PLATFORM_TOOLING_VERSION=0.3.11`.

It documents the next layer above `project-new`: a later generated service slice must be planned separately from the technical skeleton. The plan records that Project-New remains conservative and that Core distribution, Slice Blueprint, Evidence and Acceptance criteria must be solved before Springmaster is treated as a fachlicher Service-Slice generator.



## Stand nach 000079 – ZBM Target Lifecycle Alignment

Patch `000079_springmaster_zbm_target_registry_and_lifecycle_alignment` richtet die Zielprojekt-Konfiguration auf den ersten geplanten Zielnamen `zbm` aus.

Ergänzt wurden:

* Target-Deskriptor `platform/update/targets/zbm.env` als `INITIALIZATION_CANDIDATE`.
* explizite Zurückstellung von `idm` und `personnel` als `DEFERRED_EXISTING_PROJECT_NO_DELIVERY`.
* Lifecycle-Felder für Initialisierung und Update (`TARGET_LIFECYCLE`, `TARGET_INITIALIZATION_ALLOWED`, `TARGET_UPDATE_ALLOWED`).
* Delivery-Guard `TARGET_DELIVERY_ENABLED`; `target-apply` bricht ohne `TARGET_DELIVERY_ENABLED=true` ab.
* Payload-Profil `defaults` für Baseline-Konfigurationsdefaults.

Damit bleibt die nächste Arbeit auf das sichere Generieren und Akzeptieren von `zbm` fokussiert. Laufende Projekte werden nicht nebenbei beliefert.

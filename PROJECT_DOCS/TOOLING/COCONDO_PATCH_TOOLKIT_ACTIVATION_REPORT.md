---
documentId: TOOL-PATCH-TOOLKIT-ACTIVATION-0001
title: Cocondo Patch Toolkit 1.1.1 Activation and Version Closure Report
documentType: report
status: final
authority: evidence
scopeLevel: component
scopePaths:
  - springmaster/standards/build-tooling
  - springmaster/release-versioning
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-23
validFrom: 2026-07-23
lastReviewedAt: 2026-07-23
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Cocondo Patch Toolkit 1.1.1 Activation and Version Closure Report

## 1. Entscheidung

Cocondo Patch Toolkit `1.1.1` ist der kanonische mutierende Patchpfad für Springmaster. Git bleibt die dauerhafte Repositoryhistorie. `bin/cpatch` erzeugt, qualifiziert und transferiert neue Patchartefakte aus gebundenen Git-Worktrees.

Die bisherige lokale Engine unter `bin/patch.sh` und `bin/patch.py` bleibt vorübergehend für historische Diagnose, Read-only-Auswertung, Artifact Preflight, Live-Baseline und Dry-run-Kompatibilität erhalten. Live-Mutation über `accept`, nicht-trockenen `apply` oder nicht-trockenen `rollback` ist nach diesem Cutover technisch mit `LEGACY_PATCH_MUTATION_DISABLED` gesperrt.

## 2. Installations- und Qualification Evidence

| Eigenschaft | Wert |
|---|---|
| Toolkit | `1.1.1` |
| Runtime SHA-256 | `c1bc3a77e557d1e45d2960be922d4bb8d1c12b65fe8fcd5cb093650246f43684` |
| Quellbaseline | `e46c51ba833103f3442b9ae85575d8a3de5dde0a` |
| qualifizierter Installationscommit | `873decb209b1e1f5cea6b1f6ffb20544f6ae8d96` |
| Full-Export | `springmaster_export_full_2026-07-23T19-03-30-885456Z.zip` |
| Export SHA-256 | `13a936462c4d85288a8c5c800338c936c0389759eb4f779ef3d887587ecd7050` |

Bestanden wurden Production Doctor, Patch Doctor, vollständige Scope-Klassifikation, Tooling Selfcheck, targeted/full/release Projektprofile und `mvn clean verify`. Der Integrationstransfer erfolgte als Fast-forward des zuvor qualifizierten Kandidatencommits. Der Main-Working-Tree blieb sauber.

Ein irrtümlich im Toolkit-Lockverzeichnis angelegter leerer manueller `flock` wurde vor der finalen Qualifikation entfernt. Der fehlgeschlagene Doctor-Lauf blieb als negative Evidence erhalten; die anschließenden Production-Doctor-Läufe waren `HEALTHY` ohne Findings.

Die maschinenlesbare, repositorylokale Evidence steht unter `src/test/resources/tooling/patch-toolkit-activation-v1/activation-evidence.json`.

## 3. Produktionsvertrag

- `CPATCH_REQUIRE_CLEAN_TREE=true`
- `CPATCH_COMMIT_ON_ACCEPT=true`
- `CPATCH_REQUIRE_WORKTREE=true`
- `CPATCH_REQUIRE_WORKSPACE_FOR_CREATE=true`
- `CPATCH_INTEGRATION_BRANCH=main`
- `bin/cpatch workspace ...` wird korrekt an den Top-Level-Workspace-Namespace der Runtime weitergeleitet
- normative Governance-, ADR-, Standard-, Sprint- und Indexänderungen erzwingen mindestens das Profil `full`
- Änderungen unter `platform/**` erzwingen das Profil `release`
- lokaler `patchId` ist Provenienz; globale Identität bleibt `artifactId` plus Artefakt-SHA-256
- kein impliziter Push und kein obligatorischer Export pro Patch

## 4. Version Closure

Der qualifizierte neue Tooling-, Governance- und Delivery-Surface ist ein kompatibler `minor`-Impact. Die Version Closure setzt deshalb:

| Dimension | Vorher | Nachher |
|---|---:|---:|
| `PLATFORM_VERSION` | `0.17.0-foundation` | `0.18.0-foundation` |
| `PLATFORM_TOOLING_VERSION` | `0.7.0` | `0.8.1` |
| Maven Snapshot | `0.17.0-foundation-SNAPSHOT` | `0.18.0-foundation-SNAPSHOT` |

Core-, Demo-, Template- und Platform-Update-Version bleiben unverändert. `PLATFORM_STATE_PATCH` verweist auf den aktivierenden Patch.

## 5. Verifikation und Rollback

`bin/patch-toolkit-activation.sh --check` prüft Runtime, Lockdatei, produktive ENV-Regeln, Versionsschluss, Evidence, kanonischen Entrypoint und Legacy-Status. Der Check und seine Negativfixture sind Bestandteil von `bin/tooling-selfcheck.sh`.

Ein Rollback des Aktivierungspatches erfolgt ausschließlich als Git-Revert über den kanonischen Toolkit-Pfad. Ein Reaktivieren der Legacy-Mutation benötigt einen eigenständigen akzeptierten Architektur- und Sicherheitsentscheid; das Entfernen des Guards allein ist nicht zulässig.

## 6. Prozessbetrieb und Working-Tree-Sicherheit

Der erste äußere Dry-run-Orchestrator wurde als nicht kanonisch verworfen: Sein Prozess konnte enden, während der detached Toolkit-Worker weiterlief, und sein Status blieb dadurch stale. Die kanonische Wahrheit war weiterhin der Toolkit-Runrecord.

Die korrigierte Aktivierung führt deshalb `bin/process-ops.sh` und ADR-0014 ein. Das Tool löst Git-Common-Directory und Integrations-Worktree dynamisch auf, delegiert Worker direkt an `cpatch` oder `crun`, trennt Dry-run und Accept und hält Observer terminal-sicher. Prozesszustand und Incidents liegen außerhalb des Working Trees.

Die projektneutrale Integration Fixture ist nach Patch `000182` hermetisch gegen systemweite und benutzerspezifische Git-Konfiguration, Templates, Hooks und experimentelle Ref-Storage-Defaults isoliert. Der reale Springmaster-Pilot wird nach dieser Korrektur erneut qualifiziert. Eine Propagation in gemanagte Projekte bleibt bis zum separaten Pilotabschluss `BLOCKED_PENDING_SPRINGMASTER_PILOT`.

## 7. Verbleibende Grenzen

- Kein automatischer Push.
- Kein globales Strict Enforcement der Governance-Regeln.
- Keine automatische Propagation in gemanagte Projekte.
- Kein automatisches Verketten von Dry-run und Accept.
- Legacy-Code bleibt bis zu einem späteren Retention- und Migrationsentscheid im Repository, aber nicht als mutierender Primärpfad.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-24 | - | final | Toolkit 1.1.1, Prozessbetriebsvertrag, Version Closure und kontrollierter Legacy-Cutover dokumentiert; Managed-Project-Rollout bleibt bis zum Pilotabschluss gesperrt. |
| 2026-07-24 | `0.8.0` | `0.8.1` | Git-Integration-Fixture hermetisch isoliert; Post-Accept-Qualifikation wird erneut ausgeführt. |

## 8. Springmaster process pilot closure and workspace hardening

Patch `000184_springmaster_codex_calibration_execution_task_semantic_hardening` completed the real Springmaster process pilot: canonical dry-run `run-20260727T084807Z-336bc56656e9`, acceptance `run-20260727T091140Z-1dd557514153`, accepted commit `e6d184c69d2616a02da499540a3be90f208e78be`, and live readiness completion `run-20260727T093113Z-0be8cada4b89` all finished successfully. The first postcheck correctly exposed missing external agent roots and was completed after explicit provisioning; it did not invalidate the accepted source patch.

The follow-up workspace contract introduces project-relative operator logs and a single-current-workflow `patches/work/` handoff area. This is not a second run-state store. Direct `cpatch` Run API use remains mandatory, while diagnostic upload bundles are derived from canonical evidence and excluded from Git and exports.

## 9. Operator-log history compatibility correction

Patch `000186_springmaster_patch_workflow_workspace_contract` completed its canonical dry-run and acceptance on the real Springmaster history. Acceptance run `run-20260727T120640Z-800d2ab4656d` committed `ef713cc73518da94419dfa342303df6847120420` after all syntax, targeted, full and release validators passed.

The first observer call after acceptance exposed a compatibility defect: the new process adapter rejected the entire shared operator-log root because Springmaster intentionally retains historical tracked validation evidence below `patches/logs/validation/`. The canonical acceptance remained successful; repeating it was neither required nor permitted.

Patch `000187_springmaster_operator_log_history_compatibility` narrows the fail-closed check to the exact generated run directory `<operator-log-root>/<patch-id>/<run-id>/`. Historical tracked sibling evidence is tolerated and left untouched. The current run directory must remain ignored and free of tracked content. Integration fixtures cover both the real-history compatibility case and the tracked-current-run collision case.

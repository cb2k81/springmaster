---
documentId: SPRINGMASTER-SPRINT-002-COMPLETION
title: Codex Calibration and Business Partner End-to-End Pilot – Completion Report
documentType: sprint-completion-report
status: draft
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-28
validFrom: null
lastReviewedAt: 2026-08-14
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-002
qualificationStatus: pending
closureStatus: open
closedAt: null
---

# Codex Calibration and Business Partner End-to-End Pilot – Completion Report

## Codex Cutover Acceptance – 2026-08-13

Cutover-Zwischenabschluss: M-002 und M-003 sind erfüllt. A002 wurde als fehlgeschlagener Calibration-Attempt unveränderlich geschlossen; der konkrete Change-Bundle-Read-Scope-Defekt wurde mit `000214_codex-host-change-bundle-read-scope-correction` kanonisch korrigiert. A003 wurde auf der korrigierten Baseline vollständig neu ausgeführt. Der erste Cutover-Recovery-Promotion-Kandidat wurde vor Commit und Artefakterzeugung fail-closed gestoppt, weil `codex-pilot-ready-it.sh` seine PROJECT_READY-Positive-Fixture implizit vom aktuellen Repository-Lifecycle erbte und deshalb auf einem bereits auf `PILOT_WRITE_READY` gesetzten Kandidaten deterministisch fehlschlug. Die Promotion macht diese Fixture lifecycle-neutral; der produktive Readiness-Vertrag selbst wird dadurch nicht abgeschwächt. Reale Host-Qualification, zwei qualifizierte und separat akzeptierte A003-Implementierungskalibrierungen (`000215_codex-calibration-implementation-1-a003`, `000216_codex-calibration-implementation-2-a003`), live verifizierte Confinement-Evidence `5765d4d07c4f2ed4a012c9be4a1e01981d570368f474f45baf5c506b95a988f8` und die separate Write-Promotion liegen vor. `PILOT_WRITE_READY`/`PROMOTED` ist damit für den Codex Cutover erreicht. Der Sprint als Ganzes bleibt wegen M-004 und M-005 offen; dieses Cutover-Ergebnis schließt weder den Business-Partner-End-to-End-Piloten noch Repeatability/V1.1/Closure vorzeitig.


## Ergebnisübersicht

Der Sprint ist aktiv. Dieses Dokument ist der vorbereitete dauerhafte Qualification- und Closure-Nachweis. Es wird erst nach vollständiger Bewertung der Kalibrierung, des Business-Partner-Piloten, der Repeatability und aller Stop- oder Deferral-Entscheidungen finalisiert.

## Anforderungen und Teilziele

| Bezug | Aktueller Zustand | Abschlussnachweis |
|---|---|---|
| CAP-REQ-001 / M-001 | erfüllt | Kanonische Zielquelle, aktiver Sprint-Harness, Index und Gate-Evidence |
| CAP-REQ-010 bis CAP-REQ-014 / Tooling-Härtung | erfüllt | `000201_springmaster_tooling_hardening_cut` akzeptiert; spätere Cutover-Härtungen einschließlich `000214_codex-host-change-bundle-read-scope-correction` sind kanonisch integriert. |
| CAP-REQ-002 bis CAP-REQ-004 / M-002 bis M-003 | erfüllt | A003 vollständig qualifiziert; zwei unabhängige Implementierungskalibrierungen als `000215` und `000216` separat akzeptiert; Confinement live verifiziert; Promotion `000218` akzeptiert; finale Readiness `CODEX_CUTOVER_ACCEPTED`. |
| CAP-REQ-005 bis CAP-REQ-007 / M-004 | ausstehend | Traceable Contract-Kette und Application-Acceptance |
| CAP-REQ-008 bis CAP-REQ-009 / M-005 | ausstehend | Drei Clean-Runs, V1.1-Evolution, Effizienz-, Debt- und Abschlussbewertung |

## Definition of Done und Qualification

Qualification-Status: `pending` für den Sprint als Ganzes.

Der Codex-Cutover-Anteil ist qualifiziert und promoviert: `PILOT_WRITE_READY`/`PROMOTED`, `WRITABLE_CODEX_AUTHORIZED=true`, finaler akzeptierter Cutover-HEAD `60c99cf05330806d2cf14efd50d70fa7f98adf74`. Diese Aussage schließt M-002 und M-003, aber nicht M-004/M-005 oder den Sprint insgesamt.

Die Definition of Done aus dem Sprint Brief wird bei Closure kriteriumsweise mit `erfüllt`, `deferiert` oder `blockiert` bewertet. Ein erfolgreicher Einzelrun, ein Fixture-Test oder der abgeschlossene Cutover ersetzt keine End-to-End-, Repeatability- und Closure-Evidence für die noch offenen Sprintziele.

## Akzeptierte Änderungen

Für den Sprint sind insbesondere folgende kanonische Änderungen relevant:

- `000201_springmaster_tooling_hardening_cut` – Tooling-Härtung;
- `000203_springmaster_codex_cutover_foundation` – repository-seitige Cutover-Foundation;
- `000214_codex-host-change-bundle-read-scope-correction` – Korrektur des Change-Bundle-Read-Scope-Vertrags;
- `000215_codex-calibration-implementation-1-a003` – erste unabhängige A003-Implementierungskalibrierung;
- `000216_codex-calibration-implementation-2-a003` – zweite unabhängige A003-Implementierungskalibrierung;
- `000218_codex-cutover-write-promotion` – separate Write-Promotion und finaler Cutover.
- `000219_patch-toolkit-python310-portability` – kompatibler Post-Cutover-Tooling-Patch für Python-3.10-Portabilität und Tooling `0.14.1`.

Die Versuche `000197` bis `000200` sowie A001/A002 bleiben historische Failure-/Incident-Evidence und werden ausdrücklich nicht als erfolgreiche Source-Änderungen oder wiederverwendbare Calibration-Invocations geführt.

## Dauerhafte Promotionen

Erreicht:

- allgemeine Projektziele aus historischem Sprintkontext in eine aktive kanonische Zielquelle;
- Codex-Pilot-Lifecycle durch `000218_codex-cutover-write-promotion` auf `PILOT_WRITE_READY`/`PROMOTED`; `WRITABLE_CODEX_AUTHORIZED=true`.

Noch offen und nur evidence-basiert zu entscheiden:

- dauerhafte Agenten-, Generator-, UI-Schema- oder GWC-Verträge aus dem Business-Partner-Pilot;
- Generalisierungsentscheidung für Project-New oder gemanagte Projekte;
- spätere Promotion zu `PILOT_COMPLETED` im Rahmen der Sprint-Closure.

## Offene Findings, Risiken und Schulden

- Die erste reale Post-Cutover-Feature-Umsetzung mit Codex ist noch nicht als M-004-Evidence vorhanden.
- End-to-End-Contract-Kette und disposable Application fehlen.
- Repeatability, V1.1 und Effizienzvergleich fehlen.
- Legacy-/Toolkit-Scope-Konfigurationsdrift ist bei einer späteren Toolingänderung zu konsolidieren.
- Sprint-Closure und eine mögliche Generalisierung auf weitere Projekte bleiben ausdrücklich offen.

## Temporäre Dokumente

| Pfad | Entscheidung | Ziel oder Begründung |
|---|---|---|
| SOLUTION_PLAN.md | aggregate | Relevante dauerhafte Entscheidungen werden bei Closure in ADRs, Governance, Standards, Contracts oder diesen Report promoviert. |
| STATUS.md | discard | Der finale Zustand wird vollständig in diesem Completion Report aggregiert. |

## SemVer- und Releasebewertung

Die aktuelle Post-Cutover-Versionswahrheit ist Platform `0.24.0-foundation`, Tooling `0.14.2`, Maven `0.24.0-foundation-SNAPSHOT`, Toolkit `1.1.5` und State Patch `000222_patch-toolkit-staged-path-parity`. `000222` korrigiert die rename-sensitive Staged-Path-Inventarisierung als kompatiblen Tooling-Patch und lässt die exakte Manifestparität unverändert verpflichtend. Der fehlgeschlagene `000221`-Dry-run bleibt Failure-Evidence; diese Source-Änderung behauptet weder dessen Erfolg noch Acceptance.

## Nicht erreichte Ziele und Folgebedarf

M-004 und M-005 sind noch nicht erreicht. Als Nächstes wird der Business-Partner-End-to-End-Pilot in kleine deterministische Codex-Pilot-Tasks zerlegt und von Fachkonzept/Acceptance Contract über canonical intent, Generated-Slice-Spec, IR, Application UI Spec und GWC Implementation Manifest bis zur disposable Application qualifiziert. Danach folgen Repeatability, V1.1-Evolution, Effizienz-/Debt-Bewertung und Sprint-Closure.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | draft | Dauerhaften Completion- und Qualification-Nachweis für den aktiven Sprint vorbereitet. |
| 2026-07-30 | draft | draft | Tooling-Härtung als offene Qualification-Voraussetzung und `000197` bis `000200` als nicht akzeptierte Incident-Evidence ergänzt. |
| 2026-07-30 | draft | draft | Candidate `000201` als implementiert, live inventarisiert und versiongeschlossen dokumentiert; vollständige Qualification, Accept und Post-Accept-Evidence bleiben offen. |
| 2026-07-31 | draft | draft | Acceptance von `000201` übernommen; `000203` als qualifizierter Candidate und Host-/Kalibrierungs-Evidence als nächste Abschlussgrenze dokumentiert. |
| 2026-08-01 | draft | draft | Acceptance von `000203` übernommen; Post-Accept-Live-Readiness, Host-Qualification und plan-gebundene Kalibrierung als nächste Abschlussgrenze dokumentiert. |
| 2026-08-13 | draft | draft | M-002/M-003 durch A003, zwei getrennte Calibration-Accepts, Confinement-Evidence und Promotion `000218` qualifiziert; Cutover abgeschlossen, M-004/M-005 und Sprint-Closure bleiben offen. |
| 2026-08-14 | draft | draft | Post-Cutover-Tooling-Portabilität mit `000219_patch-toolkit-python310-portability` geschlossen; Tooling-Wahrheit dieses Schritts `0.14.1`/Toolkit `1.1.4`; M-004 bleibt der nächste fachliche Slice. |
| 2026-08-14 | draft | draft | Rename-sensitive Staged-Path-Inventarisierung mit `000222_patch-toolkit-staged-path-parity` korrigiert; aktuelle Tooling-Wahrheit `0.14.2`/Toolkit `1.1.5`; Sprint 003 bleibt inaktiv. |

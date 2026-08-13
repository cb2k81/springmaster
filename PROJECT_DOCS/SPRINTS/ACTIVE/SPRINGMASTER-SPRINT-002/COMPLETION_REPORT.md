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
lastReviewedAt: 2026-08-13
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

Cutover-Zwischenabschluss: M-002 und M-003 sind erfüllt. A002 wurde als fehlgeschlagener Calibration-Attempt unveränderlich geschlossen; der konkrete Change-Bundle-Read-Scope-Defekt wurde mit `000214_codex-host-change-bundle-read-scope-correction` kanonisch korrigiert. A003 wurde auf der korrigierten Baseline vollständig neu ausgeführt. Der erste R5-Promotion-Kandidat wurde vor Commit und Artefakterzeugung fail-closed gestoppt, weil `codex-pilot-ready-it.sh` seine PROJECT_READY-Positive-Fixture implizit vom aktuellen Repository-Lifecycle erbte und deshalb auf einem bereits auf `PILOT_WRITE_READY` gesetzten Kandidaten deterministisch fehlschlug. Die Promotion macht diese Fixture lifecycle-neutral; der produktive Readiness-Vertrag selbst wird dadurch nicht abgeschwächt. Reale Host-Qualification, zwei qualifizierte und separat akzeptierte A003-Implementierungskalibrierungen (`000215_codex-calibration-implementation-1-a003`, `000216_codex-calibration-implementation-2-a003`), live verifizierte Confinement-Evidence `5765d4d07c4f2ed4a012c9be4a1e01981d570368f474f45baf5c506b95a988f8` und die separate Write-Promotion liegen vor. `PILOT_WRITE_READY`/`PROMOTED` ist damit für den Codex Cutover erreicht. Der Sprint als Ganzes bleibt wegen M-004 und M-005 offen; dieses Cutover-Ergebnis schließt weder den Business-Partner-End-to-End-Piloten noch Repeatability/V1.1/Closure vorzeitig.


## Ergebnisübersicht

Der Sprint ist aktiv. Dieses Dokument ist der vorbereitete dauerhafte Qualification- und Closure-Nachweis. Es wird erst nach vollständiger Bewertung der Kalibrierung, des Business-Partner-Piloten, der Repeatability und aller Stop- oder Deferral-Entscheidungen finalisiert.

## Anforderungen und Teilziele

| Bezug | Aktueller Zustand | Abschlussnachweis |
|---|---|---|
| CAP-REQ-001 / M-001 | erfüllt | Kanonische Zielquelle, aktiver Sprint-Harness, Index und Gate-Evidence |
| CAP-REQ-010 bis CAP-REQ-014 / Tooling-Härtung | erfüllt | `000201_springmaster_tooling_hardening_cut` wurde mit Acceptance-Run `run-20260731T073111Z-0e5f6316c4d3` akzeptiert; akzeptierter Commit ist `b48743512944e95b39231f685fe172fb93b5a015`. |
| CAP-REQ-002 bis CAP-REQ-004 / M-002 bis M-003 | in Arbeit | `000203` ist akzeptiert. Post-Accept-Live-Readiness, reale Host-Qualification, zwei akzeptierte Kalibrierungstasks und separate Promotion fehlen. |
| CAP-REQ-005 bis CAP-REQ-007 / M-004 | ausstehend | Traceable Contract-Kette und Application-Acceptance |
| CAP-REQ-008 bis CAP-REQ-009 / M-005 | ausstehend | Drei Clean-Runs, V1.1-Evolution, Effizienz-, Debt- und Abschlussbewertung |

## Definition of Done und Qualification

Qualification-Status: `pending`.

Die Tooling-Härtung `000201_springmaster_tooling_hardening_cut` und die Codex-Cutover-Foundation `000203_springmaster_codex_cutover_foundation` sind abgeschlossen und akzeptiert. Die formale Readiness bleibt `PROJECT_READY`; der nächste kontrollierte Abschnitt ist ausführbar. `WRITABLE_CODEX_AUTHORIZED=false` und `PILOT_WRITE_READY=false` gelten, bis Post-Accept-Live-Readiness, reale Host-Qualification, Kalibrierung und separate Promotion erfolgreich sind.

Die Definition of Done aus dem Sprint Brief wird bei Closure kriteriumsweise mit `erfüllt`, `deferiert` oder `blockiert` bewertet. Ein erfolgreicher Einzelrun, ein Fixture-Test oder eine statische Readiness-Aussage ersetzt keine reale Boundary-, Ergebnis- und Repeatability-Evidence.

## Akzeptierte Änderungen

Bisher zur Sprintinitialisierung vorgesehen:

- dauerhafte allgemeine Springmaster-Zielquelle;
- vollständiger aktiver Sprint-002-Vertrag;
- aktualisierter Documentation Index.

Weitere akzeptierte Änderungen werden commit-, artifact- und evidencegebunden ergänzt, nicht nur über lokale Patchnummern beschrieben. `000201_springmaster_tooling_hardening_cut` und `000203_springmaster_codex_cutover_foundation` sind akzeptiert. Die Versuche `000197` bis `000200` sind Incident-Evidence und werden ausdrücklich nicht als akzeptierte Änderungen geführt.

## Dauerhafte Promotionen

Bisherige Promotion: allgemeine Projektziele aus historischem Sprintkontext in eine aktive kanonische Zielquelle.

Noch offen:

- mögliche Promotion zu `PILOT_WRITE_READY`;
- dauerhafte Agenten-, Generator-, UI-Schema- oder GWC-Verträge aus dem Pilot;
- Generalisierungsentscheidung für Project-New oder gemanagte Projekte.

## Offene Findings, Risiken und Schulden

- Post-Accept-Live-Readiness gegen den akzeptierten Commit fehlt;
- reale Host-Inspection und Runtime-Denial-Probes auf dem DEV-System fehlen;
- Lifecycle-Autorisierung beliebiger Tasks vor `PILOT_WRITE_READY` benötigt weiterhin eine fail-closed Bindung an den materialisierten Calibration Plan;
- zwei unabhängige implementierende Kalibrierungsnachweise fehlen;
- End-to-End-Contract-Kette und disposable Application fehlen;
- Repeatability, V1.1 und Effizienzvergleich fehlen;
- Legacy-/Toolkit-Scope-Konfigurationsdrift ist bei einer späteren Toolingänderung zu konsolidieren.

## Temporäre Dokumente

| Pfad | Entscheidung | Ziel oder Begründung |
|---|---|---|
| SOLUTION_PLAN.md | aggregate | Relevante dauerhafte Entscheidungen werden bei Closure in ADRs, Governance, Standards, Contracts oder diesen Report promoviert. |
| STATUS.md | discard | Der finale Zustand wird vollständig in diesem Completion Report aggregiert. |

## SemVer- und Releasebewertung

Die akzeptierten Schnitte `000201` und `000203` setzen die aktuelle Versionswahrheit auf Platform `0.23.0-foundation`, Tooling `0.13.0` und State Patch `000203_springmaster_codex_cutover_foundation`. Core, Template, Demo und Platform Update bleiben unverändert. Die Stabilisierung führt keine weitere Release- oder Write-Promotion durch.

## Nicht erreichte Ziele und Folgebedarf

M-002, M-003, M-004 und M-005 sind noch nicht erreicht. Als Nächstes folgen Post-Accept-Live-Readiness, reale Host-Qualification und die Materialisierung des Calibration Task Packs gegen den akzeptierten Commit. Erst danach werden reale Codex-Aufrufe und die zwei getrennt akzeptierten Implementierungskalibrierungen durchgeführt.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | draft | Dauerhaften Completion- und Qualification-Nachweis für den aktiven Sprint vorbereitet. |
| 2026-07-30 | draft | draft | Tooling-Härtung als offene Qualification-Voraussetzung und `000197` bis `000200` als nicht akzeptierte Incident-Evidence ergänzt. |
| 2026-07-30 | draft | draft | Candidate `000201` als implementiert, live inventarisiert und versiongeschlossen dokumentiert; vollständige Qualification, Accept und Post-Accept-Evidence bleiben offen. |
| 2026-07-31 | draft | draft | Acceptance von `000201` übernommen; `000203` als qualifizierter Candidate und Host-/Kalibrierungs-Evidence als nächste Abschlussgrenze dokumentiert. |
| 2026-08-01 | draft | draft | Acceptance von `000203` übernommen; Post-Accept-Live-Readiness, Host-Qualification und plan-gebundene Kalibrierung als nächste Abschlussgrenze dokumentiert. |

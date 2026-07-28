---
documentId: SPRINGMASTER-SPRINT-002-STATUS
title: Codex Calibration and Business Partner End-to-End Pilot – Status
documentType: sprint-status
status: active
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-28
validFrom: 2026-07-28
lastReviewedAt: 2026-07-28
reviewBy: 2026-08-21
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-002
sprintPhase: slice-planning
overallStatus: active
lastDriftResult: none
lastDriftAt: 2026-07-28
expectedVersionImpact: minor
---

# Codex Calibration and Business Partner End-to-End Pilot – Status

## Aktueller Stand

Die dauerhafte Zielquelle und der vollständige aktive Sprintvertrag sind angelegt und auf die geprüfte Baseline `ac090009742845b466f306cd240f0c61c6d935a6` ausgerichtet. Der Projektzustand bleibt `PROJECT_READY`; der nächste erlaubte Schritt ist `CODEX_CALIBRATION`. Es besteht keine schreibende Codex-Freigabe.

Der verworfene frühere D3-Kandidat wird nicht weiterverwendet. Kalibrierungs-Tasks und Oracles müssen gegen den nach diesem Dokumentationsschnitt akzeptierten Live-Commit neu erzeugt werden.

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| M-001 | completed | Kanonische Zielquelle, vier aktive Sprintdokumente und Indexeinträge; Qualification durch Documentation Gate, Sprint Gate, Payload- und Patch-Preflight. |
| M-002 | planned | Neuer Task-/Oracle-Schnitt gegen die akzeptierte Post-000188-Baseline erforderlich. |
| M-003 | planned | Keine Codex-Ausführung und keine Write-Promotion im Initialisierungsschnitt. |
| M-004 | planned | Business-Partner-Fachkonzept und Acceptance Contract sind vorhanden; Contract-Kette und disposable App noch nicht ausgeführt. |
| M-005 | planned | Repeatability-, V1.1-, Effizienz- und Closure-Evidence stehen aus. |

## Blocker und Erkenntnisse

Aktuell besteht kein Projekt-Readiness-Blocker. Ausstehend ist jedoch die konkrete lokale Ausführungsreife des neu zu erzeugenden D3 Task Packs. Fehlende reale Runtime-Boundary-Evidence blockiert `PILOT_WRITE_READY` ausdrücklich.

Forensische Erkenntnis dieses Schnitts: Die fünf allgemeinen Projektziele waren bislang nur in einem archivierten Sprint Brief vollständig ausformuliert. Dadurch fehlte eine dauerhafte aktuelle Zielquelle. Außerdem existierte nach Closure von Sprint 001 kein aktiver Sprint-Harness für den Codex-Pilot.

## Drift-Bewertung

Ergebnis: `none`.

Der Sprint leitet sich direkt aus ADR-0015, AI Agent Development Governance, dem Zustand `PROJECT_READY` und dem eingefrorenen Business-Partner-Pilotinput ab. Scope und Promotionsgrenzen sind konsistent. Vor jedem neuen Slice sowie vor Write-Promotion, Qualification und Closure ist eine erneute Driftprüfung erforderlich.

## Risiken und technische Schulden

- Legacy-Read-only-Patchvalidatoren und die kanonische Toolkit-Scope-Registry verwenden unterschiedliche Konfigurationsquellen; dieser Patch nutzt den kanonischen Scope und spiegelt ihn für Legacy-Kompatibilitätsprüfungen explizit, ohne die Scopegrenzen zu erweitern.
- Die reale Codex-Runtime und deren Denial-Probes sind noch nicht als aktuelle Acceptance-Evidence vorhanden.
- Application UI Spec und GWC Implementation Manifest besitzen noch keinen in diesem Sprint qualifizierten End-to-End-Nachweis.
- Der Sprintzeitraum ist eine Steuerungsannahme; bei Überschreitung ist eine aktuelle Driftbewertung zwingend.

## Versionswirkung

Erwartet `minor`, sofern neue Tooling-, Generator- oder Pilotfähigkeiten qualifiziert aktiviert werden. Der aktuelle Dokumentationsschnitt setzt keine vorgezogene Version und ändert `PLATFORM_STATE_PATCH` nicht.

## Nächster kontrollierter Schritt

Ein neues immutable D3 Kalibrierungs-Task-Pack mit unabhängigen Oracles wird gegen den nach Annahme dieses Patches tatsächlichen Live-Commit erstellt. Vor dem ersten Codex-Aufruf werden Scope, externe Roots, Invocation, Runtime-Denial-Probes und Qualifikationskommandos vollständig preflighted.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | active | Erste kanonische Statusquelle für Sprint 002 angelegt; M-001 abgeschlossen, Kalibrierung noch nicht gestartet. |

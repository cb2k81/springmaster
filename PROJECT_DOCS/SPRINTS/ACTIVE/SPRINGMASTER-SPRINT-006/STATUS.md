---
documentId: SPRINGMASTER-SPRINT-006-STATUS
title: Governance & Tooling Simplification / Managed Project Recovery - Status
documentType: sprint-status
status: active
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-09-01
validFrom: 2026-09-01
lastReviewedAt: 2026-09-02
reviewBy: 2026-09-30
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-006
sprintPhase: execution
overallStatus: active
lastDriftResult: none
lastDriftAt: 2026-09-02
expectedVersionImpact: minor
currentMilestone: M-002
---

# Governance & Tooling Simplification / Managed Project Recovery - Status

## Aktueller Stand

Sprint 006 ist aktiv. ADR-0020 und GOAL-008 bilden die Enabling-Governance-Foundation. M-001 ist auf dem Trusted Host qualifiziert und über Delivery `000267_s006-p0-m001-maintenance-recovery` akzeptiert. Der anschließende Source-Review hat die Recovery-Semantik für isolierte Branches, blockierte Records und Evidence-Pflichtfelder nachgeschärft; diese Post-Accept-Findings sind im M-001-Closure-Schnitt geschlossen. Sprint-Closure wird ausdrücklich nicht behauptet; M-002 ist der nächste geplante Umsetzungsschnitt.

```text
OVERALL_STATUS=active
CURRENT_MILESTONE=M-002
SPRINT_PHASE=execution
LAST_DRIFT_RESULT=none
QUALIFICATION_STATUS=pending
CLOSURE_STATUS=open
M001_STATUS=completed
M001_ACCEPTANCE=accepted
M001_ACCEPTED_PATCH=000267_s006-p0-m001-maintenance-recovery
M001_TRUSTED_HOST_QUALIFICATION=passed
M001_POST_ACCEPT_REVIEW=closed
```

## Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Governance-/Tooling-Reibungsinventur und Recovery Contract | REQ-001..005 | Regelklassifikation, Feldbaseline, Recovery Contract und Self-Repair-Canary definiert | Contract/Validator/32 hermetische IT-Fälle + A002 Baseline + vollständige Trusted-Host-Matrix + akzeptierte Delivery 000267 + Post-Accept-Review-Closure | Springmaster | completed |
| M-002 | Kanonischer Producer, State Truth, Runner und Source-Diff | REQ-008..010, REQ-014..018 | Producer->Preflight PASS; State eindeutig; Runner/Scope-Fixtures PASS | Tooling Code + IT/Evidence | Springmaster | planned |
| M-003 | Engineering-/Delivery-Trennung und Progressive Qualification | REQ-006..007, REQ-011..013, REQ-019 | normaler Change ohne Vorab-cpatch; Delivery weiter fail-closed | Tooling/Governance + Regression | Springmaster | planned |
| M-004 | DEV-/Build-Portabilität und project-owned Tooling | REQ-020..025, REQ-028..029 | Fresh Checkout, Env/DB/Build und project-owned tooling qualifiziert | Managed-Project Fixtures + Host Tests | Springmaster | planned |
| M-005 | Personnel- und ZBM-Feldqualification | REQ-026..027 | zwei reale Canaries; Produktfehler weiter sichtbar; Reibung reduziert | Field Qualification Evidence | Trusted Host | planned |
| M-006 | Portable Managed Development Foundation | REQ-028..029, REQ-032 | Project Adapter + install/update/repair/rollback und isolierte Runs | Managed-Project Qualification | Springmaster | planned |
| M-007 | GWC Conformance Profile | REQ-030..031 | report-only GWC_CONFORMANT-Nachweis oder dokumentierte P2-Deferral | Contract/Gate Fixtures | Springmaster | planned |

## Abgeschlossene Teilziele

M-001 ist abgeschlossen. Der Recovery Contract bindet ADR-0020 an die bestehenden Change-/Risk-, Profile-, Execution-/Finding- und Completion-Vokabulare. Die Trusted-Host-Qualification lief mit der vollständigen Originalmatrix, der kanonische Dry Run war findings-frei und Delivery `000267_s006-p0-m001-maintenance-recovery` wurde akzeptiert. Der Post-Accept-Review schloss anschließend die semantischen Lücken für attached isolated branches, blockierte Recovery-Records, nicht-leere Baseline-/Worktree-Bindings und Qualification-Evidence.

## Aktives Teilziel

Kein M-002-Code ist durch den M-001-Closure-Schnitt vorweggenommen. M-002 ist der nächste geplante Umsetzungsschnitt und darf nun aus der sauberen akzeptierten M-001-Baseline gestartet werden.

## Blockierte Teilziele

Keine formal blockierten Teilziele. M-002 bis M-007 warten geplant auf die vorgelagerten Slices.

## Blocker und Erkenntnisse

- Personnel-P3 ist ein realer Produktfehler plus hohe operative Qualification-/Evidence-Kosten; beides wird getrennt bewertet.
- ZBM meldet wiederholte Patch-/Runner-/DEV-Setup-Reibung. Das Handoff ist Design Evidence; die konkrete aktuelle Live-Root-Cause bleibt bis zur Feldinventur offen.
- Die bisherigen S006-Aktivierungsversuche r2/r3/r4 gelten als zusätzliche Developer-Experience-Evidence: ein fragiler Textanker sowie manuell erzeugte, vom Sprint-Gate abgelehnte Statuswerte dürfen nicht zum zukünftigen Standardweg werden.
- Die immutable A002-Inventur klassifiziert die Producer-Lücke als Version-/Distribution-/Adoption-/Dokumentations-/DX-Drift und `TRUE_GAP_CURRENT=false`; ein neuer Producer ist deshalb ausdrücklich nicht Bestandteil von M-001.

## Drift-Bewertung

`lastDriftResult: none`. Die Aufnahme der konkretisierten ZBM-Anforderungen erweitert nicht den bestätigten Sprintzweck, sondern präzisiert die bereits priorisierte Governance-/Tooling-Simplification und Managed-Project-Recovery.

## Risiken und technische Schulden

- Safety darf durch Vereinfachung nicht erodieren.
- Producer und Validator dürfen keine zweite Vertragswahrheit entwickeln.
- Maintenance darf kein dauerhafter Bypass oder zweite übergroße Control Plane werden.
- Fresh-Checkout-/Env-Automation darf Secrets nicht beschädigen.
- Cross-Project-Canaries dürfen keine Runtime-Kopplung erzeugen.
- GWC P2 darf P0/P1 nicht verzögern.

## Versionswirkung

Erwartet: Tooling und Update jeweils mindestens `minor`, Foundation gegebenenfalls `minor`; konkrete Werte erst aus akzeptierten S006-Schnitten. Die Aktivierungsdokumentation allein erhöht keine Komponenten.

## Nächster kontrollierter Schritt

M-002 auf der sauberen akzeptierten M-001-Baseline starten. Dabei bleiben die in M-001 bestätigten Safety-/Recovery-Invarianten unverändert; insbesondere darf der Producer-/State-/Runner-Schnitt keine zweite Vertragswahrheit erzeugen.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-09-01 | planned | active | Sprint 006 nach akzeptierter Enabling-Governance-Foundation und konkretisierten Personnel-/ZBM-Feldanforderungen aktiviert. |
| 2026-09-02 | active | active | M-001-Implementierungskandidat samt Recovery Contract, Inventory und hermetischer Self-Repair-Canary materialisiert; Qualification und Acceptance bleiben offen. |
| 2026-09-02 | active | active | M-001 nach vollständiger Trusted-Host-Qualification und Acceptance 000267 abgeschlossen; Post-Accept-Review-Findings zum Recovery-Vertrag im Closure-Schnitt geschlossen, M-002 ist nächster geplanter Slice. |

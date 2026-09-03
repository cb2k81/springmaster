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
lastDriftResult: accepted
lastDriftAt: 2026-09-02
expectedVersionImpact: minor
currentMilestone: M-002
---

# Governance & Tooling Simplification / Managed Project Recovery - Status

## Aktueller Stand

Sprint 006 ist aktiv. ADR-0020 und GOAL-008 bilden die Enabling-Governance-Foundation. M-001 ist auf dem Trusted Host qualifiziert und über Delivery `000267_s006-p0-m001-maintenance-recovery` akzeptiert; die Post-Accept-Findings sind geschlossen. AMEND-001 übernimmt die Current-State-Rebaseline: Springmaster besitzt bereits den kanonischen `cpatch create`-Pfad, `TRUE_GAP_CURRENT=false` und `STATE_TRUTH_GAP_COUNT=0` sind die immutable A002-Ausgangsevidence. Sprint-Closure wird ausdrücklich nicht behauptet; der nächste kontrollierte Schritt ist `M-002-A001 Current-State Inventory`.

```text
OVERALL_STATUS=active
CURRENT_MILESTONE=M-002
SPRINT_PHASE=execution
LAST_DRIFT_RESULT=accepted
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
| M-002 | Current Tooling Convergence: Producer, State Truth, Runner und Source Diff | REQ-008..010, REQ-014..018 | M-002-A001 bestimmt `TRUE_GAP_CURRENT` je Teilproblem; nur nachgewiesene Gaps werden writable | Current-State Inventory + gezielte Evidence | Springmaster | planned |
| M-003 | Engineering/Delivery Separation, Progressive Qualification and Compatibility Lock | REQ-006..007, REQ-011..013, REQ-019, REQ-033..036 | Engineering ohne Vorab-cpatch; Delivery/Acceptance via cpatch; Non-Regression und Handoff report-only | Tooling/Governance + Compatibility Regression | Springmaster | planned |
| M-004 | Project-local DEV and Fresh-Checkout Portability | REQ-020..025, REQ-029, REQ-034 | Env/DB/Build/Fresh Checkout und installierte project-owned Tools/Contracts/Handoff ohne Nachbarcheckout | Project-local Fixtures + Host Tests | Springmaster | planned |
| M-005 | Personnel/ZBM Non-Regression Field Qualification | REQ-026..027, REQ-033 | Public Contracts/Compatibility Locks unverändert oder separat migriert; reale Canaries und weniger Reibung | Read-only Field Evidence + autorisierte Canary-Qualification | Trusted Host | planned |
| M-006 | Managed Project Adoption and Lifecycle | REQ-028..029, REQ-032..034 | Adapter, Adoption Record/Managed State, Compatibility Decision, Lifecycle und isolierte Runs | Managed-Project Qualification | Springmaster | planned |
| M-007 | GWC Cross-Repository Conformance and Adoption Evidence | REQ-030..031, REQ-034..036 | getrennte Conformance gegen aktuelle GWC-owned Contract-Version; P2/report-only, kein Productive Source Overwrite | Contract-/Compatibility-Fixtures + Field Evidence | Springmaster | planned |

## Abgeschlossene Teilziele

M-001 ist abgeschlossen. Der Recovery Contract bindet ADR-0020 an die bestehenden Change-/Risk-, Profile-, Execution-/Finding- und Completion-Vokabulare. Die Trusted-Host-Qualification lief mit der vollständigen Originalmatrix, der kanonische Dry Run war findings-frei und Delivery `000267_s006-p0-m001-maintenance-recovery` wurde akzeptiert. Der Post-Accept-Review schloss anschließend die semantischen Lücken für attached isolated branches, blockierte Recovery-Records, nicht-leere Baseline-/Worktree-Bindings und Qualification-Evidence.

## Aktives Teilziel

Kein M-002-Code ist durch M-001 oder AMEND-001 vorweggenommen. M-002 startet auf der sauberen akzeptierten M-001-Baseline mit `M-002-A001 Current-State Inventory`. Erst diese Inventur bestimmt `TRUE_GAP_CURRENT` je Teilproblem und leitet daraus konkrete writable Implementierungsslices ab.

## Blockierte Teilziele

Keine formal blockierten Teilziele. M-002 bis M-007 warten geplant auf die vorgelagerten Slices.

## Blocker und Erkenntnisse

- Personnel-P3 ist ein realer Produktfehler plus hohe operative Qualification-/Evidence-Kosten; beides wird getrennt bewertet.
- ZBM meldet wiederholte Patch-/Runner-/DEV-Setup-Reibung. Das Handoff ist Design Evidence; die konkrete aktuelle Live-Root-Cause bleibt bis zur Feldinventur offen.
- Die bisherigen S006-Aktivierungsversuche r2/r3/r4 gelten als zusätzliche Developer-Experience-Evidence: ein fragiler Textanker sowie manuell erzeugte, vom Sprint-Gate abgelehnte Statuswerte dürfen nicht zum zukünftigen Standardweg werden.
- Die immutable A002-Inventur klassifiziert den Producer-Befund als Version-/Distribution-/Adoption-/Dokumentations-/DX-Drift und `TRUE_GAP_CURRENT=false`; Springmaster besitzt bereits den kanonischen `cpatch create`-Pfad. M-002 darf deshalb keinen zweiten Producer bauen.
- `STATE_TRUTH_GAP_COUNT=0`; M-002 führt ohne neuen Current-State-Nachweis keinen zweiten State Store ein.
- Die aktuelle Springmaster-Capability-Evidence bezeichnet UI Spec 1.2 als synthetisch und erhebt keinen Current-Live-GWC-Anspruch.

## Drift-Bewertung

`lastDriftResult: accepted`. AMEND-001 übernimmt die materielle Scope-/Requirement-Rebaseline aus aktueller Repository- und A002-Evidence. Sprintziel, `CURRENT_MILESTONE=M-002`, M-001-Acceptance, Safety Invariants und Human-Accept-Grenzen bleiben unverändert.

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

`M-002-A001 Current-State Inventory` auf der sauberen akzeptierten M-001-Baseline ausführen. Erst diese Inventory bestimmt `TRUE_GAP_CURRENT` je Producer-, Model-, Caller-, Distribution-/Adoption-, State-, Runner- und Source-Diff-Teilproblem und daraus die konkreten writable Implementierungsslices. Sie darf weder einen zweiten Producer noch einen zweiten State Store voraussetzen.

## Amendments

- `AMEND-001` vom 2026-09-02: Scope-/Requirement-Rebaseline accepted; dauerhafte Begründung, alte/neue Aussage, Auswirkungen, Entscheidung und Freigaben stehen im Sprint Brief.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-09-01 | planned | active | Sprint 006 nach akzeptierter Enabling-Governance-Foundation und konkretisierten Personnel-/ZBM-Feldanforderungen aktiviert. |
| 2026-09-02 | active | active | M-001-Implementierungskandidat samt Recovery Contract, Inventory und hermetischer Self-Repair-Canary materialisiert; Qualification und Acceptance bleiben offen. |
| 2026-09-02 | active | active | M-001 nach vollständiger Trusted-Host-Qualification und Acceptance 000267 abgeschlossen; Post-Accept-Review-Findings zum Recovery-Vertrag im Closure-Schnitt geschlossen, M-002 ist nächster geplanter Slice. |
| 2026-09-02 | active | active | AMEND-001 accepted; M-002 bleibt aktuell und beginnt mit M-002-A001 Current-State Inventory, ohne M-002-Implementierung oder Sprint-Closure zu behaupten. |

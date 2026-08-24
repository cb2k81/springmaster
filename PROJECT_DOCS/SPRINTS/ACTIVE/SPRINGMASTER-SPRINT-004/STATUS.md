---
documentId: SPRINGMASTER-SPRINT-004-STATUS
title: Field-Proven Backend Contracts and Runtime Primitives - Status
documentType: sprint-status
status: active
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-22
validFrom: 2026-08-22
lastReviewedAt: 2026-08-24
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-004
sprintPhase: qualification
overallStatus: active
lastDriftResult: none
lastDriftAt: 2026-08-24
expectedVersionImpact: minor
---

# Field-Proven Backend Contracts and Runtime Primitives - Status

## Aktueller Stand

`S004-A002` ist im Task-Worktree implementiert. Die sieben Real-World-Cases sind source-bound als PASS abgebildet, die Business-Date- und Expected-Version-Core-Primitives sind implementiert, und der globale API-Adapter bildet stale Body-Versionen auf `409 / CONFLICT` ab. Die aktiven Precondition- und Transaction/Consistency-Standards enthalten die feldbewährten fachfreien Präzisierungen.

Personnel blieb ausschließlich immutable Prompt-Evidence. Der qualifizierte Referenzanker ist Commit `1094199a84aeb809865d2992ef2aab65d8488226`; alle durch den unqualifizierten Personnel-Patch `000249` veränderten Exportpfade sind in der maschinenlesbaren Evidence von positiver Acceptance Evidence ausgeschlossen.

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| M-001 | completed | RW-01 bis RW-07 sind in Sprint-004-Fixtures und Field-Evidence PASS; kein Contract Gap oder neuer Enumwert. |
| M-002 | completed | Frameworkfreie Business-Date-Boundary und Clock-Adapter mit deterministischen Tests. |
| M-003 | completed | Expected-Version-Guard, Conflict-Exception und globaler 409-Adapter mit Tests. |
| M-004 | completed | Generische komplexe Mutationssequenz normiert; Lockordnung und konkrete Mechanik bleiben application-specific. |
| M-005 | planned | Trusted-Host-Qualification, Version Truth und kanonische Closure stehen aus. |

## Blocker und Erkenntnisse

- Der bestehende Backend-Contract-Validator qualifiziert den Sprint-004-Index mit fünf erwartungskonformen positiven/negativen Fixtures.
- Maven-Qualification bleibt Trusted-Host-Aufgabe; im Agent-Sandbox war der konfigurierte Host-Cache nicht beschreibbar und der alternative Task-Temp-Cache wegen gesperrtem Netzwerk nicht befüllbar.
- Keine inhaltliche Blockade und kein allgemeiner Contract Gap ist bekannt.

## Drift-Bewertung

`lastDriftResult=none`. Implementierung, Fixtures und Evidence bleiben innerhalb der akzeptierten ADR-0017/0018-Wertebereiche. `WORKSPACE` bleibt außerhalb der Backend-Operation-Semantik; keine UI-Reload- oder Dirty-State-Semantik wurde in Backend Effects aufgenommen.

## Risiken und technische Schulden

- Risiko der Überabstraktion von Personnel-spezifischer Concurrency bleibt durch Stop-and-Replan und fachfreie Core-Grenzen kontrolliert.
- Die historische Sprint-003-Selbstauskunft ist ein hostseitiger Closure-/Baseline-Reconciliation-Punkt, kein S004-Codex-Produktziel.
- Bekannte Harness-Deferrals aus Sprint 003 bleiben außerhalb von Sprint 004.

## Versionswirkung

Erwartet: `PLATFORM_CORE_VERSION` minor und Foundation minor. Konkrete Versionswerte und `PLATFORM_STATE_PATCH` werden erst nach realer Qualification und finaler Patch-Provenienz geschlossen.

## Nächster kontrollierter Schritt

Trusted-Host-Qualification des nichtterminalen A002-Ergebnisses ausführen. Erst danach dürfen Version Truth, Acceptance und Sprint-Closure entschieden werden.

## A002 Handoff State

```text
S004_A002_IMPLEMENTATION=COMPLETE
S004_A002_POSTCHECK_EXPECTED=PASS
SPRINT004_PHASE=qualification
SPRINT004_OVERALL_STATUS=active
SPRINT004_QUALIFICATION=TRUSTED_HOST_PENDING
SPRINT004_CLOSURE=OPEN
SPRINT004_RESULT=NOT_YET_QUALIFIED
PERSONNEL_MUTATED=false
GWC_MUTATED=false
MANAGED_TARGET_MUTATED=false
HARNESS_CHANGED=false
```

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-22 | - | active | Sprintvertrag bestätigt; Execution wartet nur auf hostseitige Aktivierungsbindung und Task-Materialisierung. |
| 2026-08-24 | execution | qualification | A002-Implementierung und source-bound Field-Evidence vollständig; Trusted-Host-Qualification ausstehend. |

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
lastReviewedAt: 2026-08-22
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-004
sprintPhase: execution
overallStatus: active
lastDriftResult: none
lastDriftAt: 2026-08-22
expectedVersionImpact: minor
---

# Field-Proven Backend Contracts and Runtime Primitives - Status

## Aktueller Stand

Sprintziel, DoR, DoD, Nichtziele, Architekturleitplanken und der Single-Task-Zuschnitt `S004-A001` sind bestätigt. Vor der Codex-Invocation muss der Live-Checkout die hostseitige Sprint-Aktivierung enthalten; ein noch vorhandener stale Sprint-003-Active-/Closure-Zustand wird dabei ausschließlich gegen bereits akzeptierte Post-Sprint-003-Evidence reconciled, nicht erneut qualifiziert.

Personnel ist ausschließlich read-only Field-Evidence. Der qualifizierte Referenzanker ist Commit `1094199a84aeb809865d2992ef2aab65d8488226`; durch den unqualifizierten Personnel-Patch `000249` veränderte Exportpfade sind von positiver Acceptance Evidence ausgeschlossen.

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| M-001 | in-progress | Field-Qualification-Scope und immutable Personnel-000248-Evidence-Satz festgelegt; Umsetzung durch S004-A001 ausstehend. |
| M-002 | planned | Business-Date-Core wird in S004-A001 umgesetzt. |
| M-003 | planned | Expected-Version-Core und 409-Adapter werden in S004-A001 umgesetzt. |
| M-004 | planned | Concurrency-Contract-Härtung wird in S004-A001 umgesetzt. |
| M-005 | planned | Qualification und Closure bleiben Trusted-Host-Verantwortung nach A001. |

## Blocker und Erkenntnisse

- `SPRINT_BRIEF.md` muss gemäß Sprint Governance vor Execution aktiv sein; Sprint-004-Aktivierung ist daher hostseitige Vorbedingung und kein Codex-Arbeitsschritt.
- Der Task Contract wird erst nach dieser Aktivierung an den dann aktuellen sauberen Main-HEAD gebunden.
- Keine inhaltliche Blockade des Sprintziels ist bekannt.

## Drift-Bewertung

`lastDriftResult=none`. Der Personnel-Vergleich hat den zuvor diskutierten Lösungszuschnitt präzisiert, ohne Sprintziel, Nichtziele oder Architekturgrenzen nach der Bestätigung dieses Briefs zu verändern.

## Risiken und technische Schulden

- Risiko der Überabstraktion von Personnel-spezifischer Concurrency bleibt durch Stop-and-Replan und fachfreie Core-Grenzen kontrolliert.
- Die historische Sprint-003-Selbstauskunft ist ein hostseitiger Closure-/Baseline-Reconciliation-Punkt, kein S004-Codex-Produktziel.
- Bekannte Harness-Deferrals aus Sprint 003 bleiben außerhalb von Sprint 004.

## Versionswirkung

Erwartet: `PLATFORM_CORE_VERSION` minor und Foundation minor. Konkrete Versionswerte und `PLATFORM_STATE_PATCH` werden erst nach realer Qualification und finaler Patch-Provenienz geschlossen.

## Nächster kontrollierter Schritt

Hostseitige Sprint-Aktivierung gegen die akzeptierte Post-Sprint-003-Baseline abschließen, neuen Main-HEAD binden und danach genau `S004-A001` materialisieren und invoken.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-22 | - | active | Sprintvertrag bestätigt; Execution wartet nur auf hostseitige Aktivierungsbindung und Task-Materialisierung. |

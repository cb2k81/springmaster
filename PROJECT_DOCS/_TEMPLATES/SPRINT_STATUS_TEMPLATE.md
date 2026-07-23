---
documentId: DOC-TPL-0008
title: Sprint Status Template
documentType: guide
status: active
authority: informative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/documentation/templates
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-23
validFrom: 2026-07-23
lastReviewedAt: 2026-07-23
reviewBy: 2027-01-23
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Sprint Status Template

## Zweck

Vorlage für die einzige aktuelle Statusquelle eines aktiven Sprints.

## Vorlage

```yaml
---
documentId: <PROJECT>-SPRINT-<NNN>-STATUS
title: <Sprinttitel> – Status
documentType: sprint-status
status: planned
authority: evidence
scopeLevel: project
scopePaths:
  - <registrierter-scope>
appliesTo:
  - springmaster
owner: <owner>
createdAt: YYYY-MM-DD
validFrom: null
lastReviewedAt: null
reviewBy: YYYY-MM-DD
supersedes: []
supersededBy: null
temporary: true
sprintId: <PROJECT>-SPRINT-<NNN>
sprintPhase: problem-framing
overallStatus: planned
lastDriftResult: none
lastDriftAt: YYYY-MM-DD
expectedVersionImpact: none
---
```

# <Sprinttitel> – Status

## Aktueller Stand

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| M-001 | planned | <Evidence oder Blocker> |

## Blocker und Erkenntnisse

## Drift-Bewertung

## Risiken und technische Schulden

## Versionswirkung

## Nächster kontrollierter Schritt

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| YYYY-MM-DD | – | planned | Statusquelle angelegt |

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | - | active | Sprint-Harness-Template eingeführt |

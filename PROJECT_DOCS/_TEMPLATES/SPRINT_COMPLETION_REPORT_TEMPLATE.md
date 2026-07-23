---
documentId: DOC-TPL-0009
title: Sprint Completion Report Template
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

# Sprint Completion Report Template

## Zweck

Vorlage für den dauerhaften Abschluss- oder Abbruchnachweis eines Sprints.

## Vorlage

```yaml
---
documentId: <PROJECT>-SPRINT-<NNN>-COMPLETION
title: <Sprinttitel> – Completion Report
documentType: sprint-completion-report
status: draft
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
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: <PROJECT>-SPRINT-<NNN>
qualificationStatus: pending
closureStatus: open
closedAt: null
---
```

# <Sprinttitel> – Completion Report

## Ergebnisübersicht

## Anforderungen und Teilziele

## Definition of Done und Qualification

## Akzeptierte Änderungen

## Dauerhafte Promotionen

## Offene Findings, Risiken und Schulden

## Temporäre Dokumente

| Pfad | Entscheidung | Ziel oder Begründung |
|---|---|---|
| SOLUTION_PLAN.md | aggregate | <Ziel oder Begründung> |
| STATUS.md | discard | Endstand ist in diesem Report enthalten. |

## SemVer- und Releasebewertung

## Nicht erreichte Ziele und Folgebedarf

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| YYYY-MM-DD | – | draft | Completion Report angelegt |

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | - | active | Sprint-Harness-Template eingeführt |

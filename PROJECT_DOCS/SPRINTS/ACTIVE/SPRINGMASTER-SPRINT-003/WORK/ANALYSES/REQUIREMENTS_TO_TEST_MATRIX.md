---
documentId: SPRINGMASTER-SPRINT-003-M1-REQUIREMENT-TEST-MATRIX
title: Sprint 003 Requirements-to-Test Matrix
documentType: report
status: draft
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-15
validFrom: null
lastReviewedAt: 2026-08-15
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-003
---

# Sprint 003 Requirements-to-Test Matrix

## Statusregel

Jede Sprint-003-Anforderung besitzt genau eine Primaerzeile. `CANDIDATE_NOT_ACCEPTED` bezeichnet in diesem Worktree materialisierte, aber noch nicht trusted-operator-akzeptierte M1-Evidence. `PLANNED/NOT_YET_IMPLEMENTED` bezeichnet kuenftige Tests oder Reports und ist ausdruecklich kein Testpass.

| Requirement | Primary | Owner-Milestone | Primaerer Test oder Oracle | Status |
|---|---|---|---|---|
| `S003-REQ-001` | yes | M-001 | Baseline-/Anti-Drift-Report plus Sprint-/Index-Konsistenzpruefung | CANDIDATE_NOT_ACCEPTED |
| `S003-REQ-002` | yes | M-001 | Catalog-Invariant: exakt 27 IDs, Pflichtfelder und Reife-Allowlist | CANDIDATE_NOT_ACCEPTED |
| `S003-REQ-003` | yes | M-002 | positives/negatives Operationsidentitaets-Schema-Fixture | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-004` | yes | M-002 | Operationskind-/Rollen-Kombinationsfixtures | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-005` | yes | M-002 | bestehende Query-, Command-, Relationship- und Error-Regressionen plus Compatibility Report | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-006` | yes | M-002 | Security-/Relation-/Candidate-/Capability-Schemafixtures | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-007` | yes | M-002 | Personnel-/Contacts-Resource-, History- und Projection-Fixtures | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-008` | yes | M-002 | Precondition-Schemafixtures fuer alle akzeptierten Typen und Bindings | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-009` | yes | M-002 | Concurrency-Contract-Fixtures fuer Baseline und additive Strategien | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-010` | yes | M-002 | Transaction-Scope-Schemafixtures und spaetere Runtime-Tests | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-011` | yes | M-002 | synchrone/asynchrone Bulk-Contract-Fixtures | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-012` | yes | M-002 | Bulk-Matrix fuer Selection, Atomicity, Security, Preconditions, Idempotenz, Limits und Outcomes | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-013` | yes | M-002 | positive/negative Abgrenzungsfixtures Bulk/Composite/GWC Batch/Job | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-014` | yes | M-002 | Catalog-Deferral-Invariant fuer Job, Export, Delta und Aggregation | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-015` | yes | M-002 | Backend-Effects-/GWC-Refresh-/Workspace-Reload-Mappingfixtures | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-016` | yes | M-002 | Standard-Page-vs-Workspace-Negativfixture | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-017` | yes | M-002 | Application-UI-Spec-v1.1-Regression und vNext-Migrationsfixture | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-018` | yes | M-002 | Source-Authority- und Drift-Negativfixtures | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-019` | yes | M-004 | deterministischer Operation-Catalog-/Bundle-Zweitlauf und Hashvergleich | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-020` | yes | M-005 | opt-in OpenAPI-Runtime-Tests inklusive unprofilierter Negativ-/Regressionfaelle | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-021` | yes | M-005 | Team-Membership-Controller-, Service-, OpenAPI- und Capability-Tests | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-022` | yes | M-006 | read-only IDM-/Personnel-/Contacts-/Bulk-/GWC-Fixture-Suite | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-023` | yes | M-002 | Compatibility-Negativfixture gegen erzwungene Fachlogik-/Entity-/Tabellen-/Lock-Aenderung | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-024` | yes | M-003 | positives und negatives Fixture je akzeptierter normativer Regel | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-025` | yes | M-001 | Exact-path-, Front-Matter-, Sprint- und Documentation-Governance-Pruefung | CANDIDATE_NOT_ACCEPTED |
| `S003-REQ-026` | yes | M-006 | Cross-App Non-Contradiction Report mit Findingstatuspruefung | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-027` | yes | M-007 | Catalog-Diff-Negativtest gegen stilles Entfernen von Capability oder Deferral | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-028` | yes | M-007 | Folgesprint-Readiness-/Handoff-Contract-Pruefung | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-029` | yes | M-001 | agent-task Post-State-/Scope-Evidence aus dem autorisierten Harness | CANDIDATE_NOT_ACCEPTED |
| `S003-REQ-030` | yes | M-001 | Review der unveraenderten menschlichen Accept-/Promotion-/Versionierungsgrenzen | CANDIDATE_NOT_ACCEPTED |
| `S003-REQ-031` | yes | M-007 | Gate-Registry-Pruefung: neue Regeln report-only, keine implizite Strict-Promotion | PLANNED/NOT_YET_IMPLEMENTED |
| `S003-REQ-032` | yes | M-006 | Generated-Slice-V1-, GWC-v1.1- und bestehende OpenAPI-Regressionen | PLANNED/NOT_YET_IMPLEMENTED |

## Vollstaendigkeit und Evidence-Grenze

Die Matrix bindet `S003-REQ-001..032` ohne Luecke oder Doppel-Primary. Sie behauptet keinen bestandenen M2-M7-Test. Auch die M1-Zeilen bleiben bis trusted-operator Acceptance Kandidaten-Evidence; die spaetere Qualification muss konkrete Reports und Testergebnisse eintragen.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-15 | - | draft | Alle 32 Anforderungen an primaere M1- oder geplante Qualification-Oracles gebunden, ohne kuenftige Evidence als bestanden auszugeben. |

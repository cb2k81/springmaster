---
documentId: SPRINGMASTER-SPRINT-003-M1-NAMING-MATRIX
title: Sprint 003 M1 Naming Matrix
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

# Sprint 003 M1 Naming Matrix

## Zweck und Entscheidungsgrenze

Diese Matrix erfasst bestehende und im Zielbild vorgeschlagene Namen, ohne deren Semantik zu entscheiden. Die Spalte „M2-Kandidat“ ist weder Auswahl noch Contract. Alle Zeilen mit Status `OPEN_M2` gehoeren M-002; M1 erzeugt keine ADR, keinen Standard, kein Schema und keine Source-Authority-Entscheidung.

| Bereich | Aktuelle Namen oder Quellen | M2-Kandidat, nicht entschieden | Gap/Frage | Status | Owner |
|---|---|---|---|---|---|
| stabile Operationsidentitaet | OpenAPI `operationId`, Methode und Pfad; im Review-Zielbild `operationKey` | `operationKey` neben technischem `operationId` | Identitaet, Eindeutigkeit, Versionierung, Alias- und Verification-Regeln offen | OPEN_M2 | M-002 |
| Operationsklassifikation | Query, Command und Precheck in bestehenden Standards | `operationKind`, `operationRoles[]` | Kardinalitaet, Enum-Werte und Kombinationen offen | OPEN_M2 | M-002 |
| Source Authority | OpenAPI, Java-Authoring, UI Spec, Generated-Slice-IR und Review-Zielbild | Source-Authority-Matrix | Primaerquelle, Ableitungsrichtung und Driftregel je Feld offen | OPEN_M2 | M-002 |
| Ressourcenrollen | Entity/DTO/Relationship/Reference Data in bestehenden Quellen | Resource, Aggregate Root/Member, Version, Snapshot, Append-only, Ledger, Read Model, Projection | Rollen, Grenzen und Mehrfachklassifikation offen | OPEN_M2 | M-002 |
| Historie und Zeit | `persistenceVersion`; anwendungsspezifische History-Begriffe nur als Zielbildinput | History, Snapshot, Append-only, Ledger, Temporal | fachneutrale Semantik und Bindings offen | OPEN_M2 | M-002 |
| Projection | Query DTOs und Complete Result Sets | Projection/Read Model | Abgrenzung zu Entity Read, Paging, Filterung und Autorisierung offen | OPEN_M2 | M-002 |
| Mutation Precondition | `persistenceVersion`, Command-Validierung, HTTP-Fehlervertrag | Expected Version Set, Snapshot Token, ETag | Binding sowie 409/412/428-Abbildung offen | OPEN_M2 | M-002 |
| Consistency | Optimistic-Locking-Baseline | optimistic, pessimistic, mixed | Use-Case-Auswahl, Lock Set/Order und Transaktionsklassifikation offen | OPEN_M2 | M-002 |
| Mehrziel-Operationen | Relationship-Bulk-Regel, Commands und Prechecks | Bulk, Composite Command, GWC Batch, Background Job | Definition, Abgrenzung und Mapping offen | OPEN_M2 | M-002 |
| Bulk Selection | keine vollstaendige fachneutrale Baseline | explicit targets, query snapshot, selection token | Auswahlstabilitaet, Tokenbindung und Duplikate offen | OPEN_M2 | M-002 |
| Bulk Atomicity | vorhandene Default-Aussage „all-or-nothing“ fuer bisherigen Scope | all-or-nothing, per-target, per-chunk | zulaessige Modi und Transaktionswirkung offen | OPEN_M2 | M-002 |
| Bulk Security | bestehende Permission-/Precheck-Grenzen | authorization/non-disclosure profile | Sichtbarkeit, Ergebnisredaktion und erneute Mutationpruefung offen | OPEN_M2 | M-002 |
| Bulk Delivery | bestehende HTTP-Command-Status; kein vollstaendiger Async-Vertrag | idempotency, limits, outcomes, result delivery | Statusressource, Retention, Polling und Fehlerform offen | OPEN_M2 | M-002 |
| Backend Effects | keine akzeptierte fachneutrale Effect-Semantik | affected backend resources | Inhalt und Authority der Backend-Effects offen | OPEN_M2 | M-002 |
| GWC Reaktion | bestehende Generated-Slice-/GWC-Kompatibilitaetsinputs | refresh, workspace reload | Trennung von Backend Effects, Refresh und Workspace Reload offen | OPEN_M2 | M-002 |
| UI-Spec-Evolution | vorhandene Generated Slice V1 Evidence; Application UI Spec v1.1 als Kompatibilitaetsconstraint | vNext-Bindung | additive Erweiterung, neue Version oder Alias-/Migrationsform offen | OPEN_M2 | M-002 |

## Unveraenderte M1-Namen

Die Capability-IDs `CAP-API-001` bis `CAP-MIG-001`, die Requirement-IDs `S003-REQ-001` bis `S003-REQ-032` und die Milestone-IDs `M-001` bis `M-007` werden in M1 nur gebunden, nicht umbenannt. Reifegradnamen stammen aus dem bestehenden Zielbild und werden im Capability Catalog unveraendert verwendet.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-15 | - | draft | Aktuelle und vorgeschlagene Begriffe mit ausdruecklich offenen M2-Entscheidungen materialisiert. |

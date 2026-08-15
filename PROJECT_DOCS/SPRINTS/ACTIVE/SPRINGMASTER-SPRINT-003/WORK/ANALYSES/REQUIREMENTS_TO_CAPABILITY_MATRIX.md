---
documentId: SPRINGMASTER-SPRINT-003-M1-REQUIREMENT-CAPABILITY-MATRIX
title: Sprint 003 Requirements-to-Capability Matrix
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

# Sprint 003 Requirements-to-Capability Matrix

## Mappingregel

Jede Sprint-003-Anforderung besitzt genau eine Primaerzeile und genau eine primaere Capability aus dem M1-Catalog. Zusaetzliche Bezuege bleiben informativ. Der Owner ist genau eines der Milestones `M-001` bis `M-007`. Das Mapping entscheidet keine fuer M2 reservierte Semantik.

| Requirement | Primary | Primaere Capability | Weitere Capability-Bezuege | Owner-Milestone | M1-Bindung |
|---|---|---|---|---|---|
| `S003-REQ-001` | yes | `CAP-QUAL-001` | `CAP-TOOL-001` | M-001 | Zielbild, Sprintscope und Catalog-Pfad gebunden |
| `S003-REQ-002` | yes | `CAP-QUAL-001` | alle 27 Catalog-Capabilities | M-001 | deterministischer Catalog mit Ist-/Zielreife materialisiert |
| `S003-REQ-003` | yes | `CAP-API-001` | - | M-002 | Operationsidentitaet bleibt M2-offen |
| `S003-REQ-004` | yes | `CAP-API-001` | - | M-002 | Operationsklassifikation bleibt M2-offen |
| `S003-REQ-005` | yes | `CAP-API-002` | `CAP-API-003` | M-002 | bestehende API-Vertraege als KEEP klassifiziert |
| `S003-REQ-006` | yes | `CAP-API-004` | `CAP-API-003`, `CAP-BULK-003` | M-002 | fachneutrale Maschinenlesbarkeit zu entscheiden |
| `S003-REQ-007` | yes | `CAP-HIST-001` | `CAP-HIST-002`, `CAP-PROJ-001` | M-002 | Resource-/History-/Projection-Semantik offen |
| `S003-REQ-008` | yes | `CAP-CONC-001` | - | M-002 | Precondition-Set und Bindings offen |
| `S003-REQ-009` | yes | `CAP-CONC-002` | `CAP-CONC-001` | M-002 | Optimistic-Baseline bleibt erhalten; additive Strategien offen |
| `S003-REQ-010` | yes | `CAP-CONC-003` | `CAP-AGG-001` | M-002 | Transaction-Scope-Klassifikation offen |
| `S003-REQ-011` | yes | `CAP-BULK-001` | `CAP-BULK-002` | M-002 | synchroner/asynchroner Bulk-Vertrag offen |
| `S003-REQ-012` | yes | `CAP-BULK-003` | `CAP-BULK-001`, `CAP-BULK-002` | M-002 | Selection/Atomicity/Security/Delivery offen |
| `S003-REQ-013` | yes | `CAP-GWC-003` | `CAP-BULK-001`, `CAP-BULK-002`, `CAP-JOB-001` | M-002 | Abgrenzung und Mapping offen |
| `S003-REQ-014` | yes | `CAP-JOB-001` | `CAP-EXPORT-001`, `CAP-QUERY-003`, `CAP-AGG-001` | M-002 | Zielkapazitaeten sichtbar; Zielreife DEFINED |
| `S003-REQ-015` | yes | `CAP-GWC-001` | `CAP-WS-002` | M-002 | Backend Effects gegen GWC-Verantwortung offen |
| `S003-REQ-016` | yes | `CAP-WS-001` | `CAP-GWC-002` | M-002 | getrennte Patternfamilien als Gap gebunden |
| `S003-REQ-017` | yes | `CAP-GWC-001` | `CAP-API-001` | M-002 | v1.1-zu-vNext-Migrationsform offen |
| `S003-REQ-018` | yes | `CAP-TOOL-001` | `CAP-GWC-001` | M-002 | Source-Authority-Matrix offen |
| `S003-REQ-019` | yes | `CAP-TOOL-001` | `CAP-TOOL-002` | M-004 | Implementierung nach M-002/M-003 geplant |
| `S003-REQ-020` | yes | `CAP-API-001` | `CAP-API-002`, `CAP-API-003`, `CAP-API-004` | M-005 | opt-in Runtime geplant |
| `S003-REQ-021` | yes | `CAP-API-003` | `CAP-API-004` | M-005 | Team-Membership-Referenzslice geplant |
| `S003-REQ-022` | yes | `CAP-QUAL-001` | `CAP-GWC-002`, `CAP-WS-001` | M-006 | read-only Fixture-Qualification geplant |
| `S003-REQ-023` | yes | `CAP-MIG-001` | `CAP-API-003`, `CAP-CONC-003` | M-002 | Fachlogik-/Persistenzgrenze bleibt Constraint |
| `S003-REQ-024` | yes | `CAP-QUAL-001` | alle normativ angehobenen Capabilities | M-003 | positive/negative Oracles geplant |
| `S003-REQ-025` | yes | `CAP-QUAL-001` | `CAP-TOOL-001` | M-001 | 11-Pfad- und Governance-Scope gebunden |
| `S003-REQ-026` | yes | `CAP-QUAL-001` | alle Cross-App-Capabilities | M-006 | Non-Contradiction-Report geplant |
| `S003-REQ-027` | yes | `CAP-QUAL-001` | alle 27 Catalog-Capabilities | M-007 | Deferrals im Catalog sichtbar und nicht entfernbar zu halten |
| `S003-REQ-028` | yes | `CAP-AGG-001` | `CAP-CONC-002`, `CAP-CONC-003`, `CAP-WS-001` | M-007 | Folgesprint-Handoff geplant |
| `S003-REQ-029` | yes | `CAP-QUAL-001` | - | M-001 | task-contract- und harnessgebundene Ausfuehrung bestaetigt |
| `S003-REQ-030` | yes | `CAP-QUAL-001` | - | M-001 | menschliche Kontrollgrenzen unveraendert |
| `S003-REQ-031` | yes | `CAP-QUAL-001` | - | M-007 | report-only; keine Gate-Promotion in M1 |
| `S003-REQ-032` | yes | `CAP-QUAL-001` | `CAP-GWC-001`, `CAP-GWC-002`, `CAP-API-002` | M-006 | Regression und Rueckwaertskompatibilitaet geplant |

## Vollstaendigkeit

Die Matrix bindet den geschlossenen Bereich `S003-REQ-001..032` ohne Luecke oder Doppel-Primary. Alle genannten `CAP-*`-IDs existieren im M1-Catalog. Reife- oder Qualification-Erfolg wird durch dieses Mapping nicht behauptet.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-15 | - | draft | Alle 32 Anforderungen primaer an den 27-Capability-Catalog und M-001..M-007 gebunden. |

---
documentId: SPRINGMASTER-SPRINT-003-M1-PATTERN-MATRIX
title: Sprint 003 Cross-App Pattern Compatibility Matrix
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

# Sprint 003 Cross-App Pattern Compatibility Matrix

## Bewertungsgrenze

Die Matrix klassifiziert ausschliesslich vorhandene Springmaster-Quellen und Patterns. `KEEP`, `CLARIFY`, `GENERALIZE`, `EXTEND` und `DEFER` sind M1-Planungskategorien, keine Reifegrade oder Promotionsentscheidungen. Akzeptierte ADRs/Standards sind Authority; Code, Tests, Reports, Demo- und Generated-Slice-Artefakte sind Evidence. Ein `review`-Konzept oder ein Candidate Slice wird dadurch nicht normativ oder kanonisch.

| Quelle oder Pattern | Rolle | Klasse | M1-Befund | Owner |
|---|---|---|---|---|
| `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md` | akzeptierte normative Authority | KEEP | DTO-, Endpoint-, Query- und Error-Boundaries bleiben Grundlage; M2 darf sie nur additiv praezisieren. | M-002 |
| `PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md` | akzeptierte normative Authority | KEEP | Controller-, Service- und Transaktionsgrenzen bleiben bestehen. | M-002 |
| `PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md` | akzeptierte normative Authority | KEEP | `persistenceVersion` und die Optimistic-Locking-Basis bleiben erhalten; weitere Strategien sind noch nicht entschieden. | M-002 |
| `PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md` | akzeptierte normative Authority | KEEP | Permission- und Enforcement-Grenzen bleiben verbindlich; Capability-Metadaten duerfen Autorisierung nicht ersetzen. | M-002 |
| `PROJECT_DOCS/ADR/ADR-0011-command-precheck-and-capability-boundary.md` | akzeptierte normative Authority | KEEP | Precheck bleibt optionale Read-Time-Aussage mit erneuter Command-Pruefung. | M-002 |
| `PROJECT_DOCS/STANDARDS/API/LIST_FILTER_QUERY_STANDARD.md` | akzeptierte normative Authority | KEEP | Paging, Filter, Sortierung, `/all` und stabile Tie-Breaker sind kompatible Baseline fuer `CAP-API-002`. | M-005 |
| `PROJECT_DOCS/STANDARDS/API/COMMAND_HTTP_STANDARD.md` | akzeptierte normative Authority | KEEP | Bestehende Command- und HTTP-Semantik bleibt kompatibel. | M-002 |
| `PROJECT_DOCS/STANDARDS/API/COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md` | akzeptierte normative Authority | CLARIFY | Relationship- und bisherige Bulk-Grenzen bleiben erhalten; die weitergehende Bulk-Abgrenzung ist M2-offen. | M-002 |
| `PROJECT_DOCS/STANDARDS/API/COMMAND_PRECHECK_ENDPOINT_STANDARD.md` | akzeptierte normative Authority | GENERALIZE | Eignet sich als fachneutrale Basis fuer Capability/Precheck; Bulk- und Cross-App-Ausweitung benoetigt eine M2-Entscheidung. | M-002 |
| `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md` | akzeptierte normative Authority | KEEP | Der globale Fehlervertrag bleibt bestehen; 409/412/428-Zuordnung wird in M1 nicht entschieden. | M-002 |
| `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md` | normative Standard-Authority | KEEP | Management-Security bleibt Voraussetzung; dokumentierte Deferral-Evidence wird nicht als Implementierung umgedeutet. | M-005 |
| `PROJECT_DOCS/CONCEPT/CROSS_APP_BACKEND_GWC_TARGET_ARCHITECTURE_CONCEPT.md` | directive Zielbild im Status `review` | CLARIFY | 27 Capability-IDs und Zielraum bleiben erhalten; Detailvokabular und Authority-Aufteilung sind noch keine akzeptierte M2-Entscheidung. | M-002 |
| `src/main/java/de/cocondo/system/list/PagedQuerySupport.java` und Query-Core | Implementierungsevidence | KEEP | Belegt gemeinsam mit Tests `CAP-API-002=REFERENCE_IMPLEMENTED`, aber keine Cross-App- oder Canonical-Reife. | M-005 |
| `src/main/java/de/cocondo/platform/demo/catalog/**` | Candidate-Implementierungsevidence | EXTEND | CatalogItem belegt Query-/OpenAPI-Patterns; Security, Canonicalization und weitere Cross-App-Vertraege fehlen. Candidate bleibt not-canonical. | M-005 |
| `PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_CONTRACT.md` und vorhandene Generated-Slice-Fixtures | Tooling-/Fixture-Evidence | CLARIFY | V1-Kompatibilitaet ist zu erhalten; eine v1.1-zu-vNext-Migrationsform wird erst in M2 entschieden. | M-002 |
| Background Job, Export, Aggregation und Cursor/Delta | nur im Zielbild benannte Capabilities | DEFER | Sichtbar im Catalog auf `DEFINED`; normative Vertrage und Runtime liegen ausserhalb des Sprint-003-Zielreifegrads. | M-007 |
| Workspace Resource Store, Reload Graph, Mutation Coordinator und Dirty State | nur im Zielbild benannte Capabilities | DEFER | Sichtbar auf `DEFINED`; Workspace-Runtime und Folgesprint-Handoff bleiben offen. | M-007 |
| Operation Catalog, Manifest und Contract-Handoff | geplante Capability ohne Implementierungsevidence | EXTEND | Erst nach M2 Authority-/Schemaentscheidungen in M-003/M-004 implementierbar. | M-004 |

## Authority-vs-Evidence-Regel

Evidence kann die Umsetzbarkeit oder den Ist-Stand belegen, aber keine fehlende normative Entscheidung ersetzen. Umgekehrt begruendet ein akzeptierter Text ohne Implementierung und Qualification keinen Reifegrad `REFERENCE_IMPLEMENTED`, `CROSS_APP_QUALIFIED` oder `CANONICAL`. Diese M1-Matrix promoviert daher weder Catalog-demo noch Generated Slice V1, GWC-Patterns oder das Architecture Concept.

## Offene M2-Grenzen

Die Source-Authority-Matrix, Operationsbegriffe, Resource-/History-/Projection-Semantik, Preconditions und Konfliktabbildung, Consistency-Details, Bulk-Abgrenzung und -Vertrag, Backend Effects gegen GWC-Verantwortung sowie die UI-Spec-Migration bleiben `CLARIFY` oder `GENERALIZE`, bis M-002 sie in akzeptierten Quellen entscheidet.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-15 | - | draft | Bestehende Springmaster-Authority und Evidence fuer M1 ohne Pattern-Promotion klassifiziert. |

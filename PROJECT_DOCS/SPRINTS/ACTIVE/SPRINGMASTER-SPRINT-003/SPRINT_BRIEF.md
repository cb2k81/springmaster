---
documentId: SPRINGMASTER-SPRINT-003-BRIEF
title: Cross-App Backend Contract Foundation and GWC Readiness – Sprint Brief
documentType: sprint-brief
status: blocked
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-30
validFrom: null
lastReviewedAt: 2026-07-31
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-003
sprintStart: 2026-08-03
targetCompletion: 2026-08-31
---

# Cross-App Backend Contract Foundation and GWC Readiness – Sprint Brief

## Sprintziel

Springmaster schafft eine fachneutrale, contract-first Cross-App-Grundlage, mit der Backend-Fähigkeiten aus IDM, Personnel und Contacts einheitlich beschrieben, qualifiziert und für GWC über OpenAPI, Operation Catalog, Resource Semantics und versionierte UI-Spec-Bindings nutzbar gemacht werden können.

Der Sprint hebt nur ausreichend verstandene Fähigkeiten bis `REFERENCE_IMPLEMENTED` an. Komplexe Aggregate, gemischte Concurrency, Backend-Bulk-Orchestrierung, Background Jobs und Workspace Runtime bleiben sichtbar, aber bewusst auf `CONTRACTED` oder `DEFINED`, solange ihre Runtime-Oracles nicht belastbar geschlossen sind.

Der Sprint bleibt bis zur erfüllten Aktivierungsvoraussetzung blockiert. Es wird keine parallele schreibende Umsetzung in überlappenden Scopes begonnen.

## Strategischer Bezug

- Standardisierung aller Springmaster-gemanagten Java-Backends über zentrale Core-, Tooling-, Pattern- und Governance-Verträge.
- Einheitliche API-Anbindung im GWC über maschinenlesbare UI-Specs, Operation Catalogs und generierte Anwendungen.
- Erhalt der vollständigen fachlichen Anforderungen von IDM, Personnel, Contacts und GWC ohne app-spezifische Fachlogik im Springmaster-Core.
- Kontrollierte agentenbasierte Umsetzung ausschließlich über kleine, immutable Tasks, unabhängige Oracles und menschliche Integration.

Kanonische Quellen sind `PROJECT_DOCS/GOVERNANCE/SPRINGMASTER_PROJECT_GOALS.md` und `PROJECT_DOCS/CONCEPT/CROSS_APP_BACKEND_GWC_TARGET_ARCHITECTURE_CONCEPT.md`.

## Ausgangslage und Baseline

- Das Zielbild und der vollständige Solution Plan für Sprint 003 liegen vor.
- Bestehende CRUD-, Query-, Command-, Relationship-, Error-, Security-, Generated-Slice- und GWC-Verträge bleiben verbindlich.
- Springmaster enthält noch keine vollständige fachneutrale Contract-Familie für Operationsidentität, Resource Semantics, Preconditions, Backend Bulk, Operation Catalog und Cross-App-Handoff.
- IDM, Personnel, Contacts und GWC sind ausschließlich read-only Qualification- und Kompatibilitätsquellen.
- Die agentenbasierte Entwicklung bleibt bis zur separaten hostbezogenen Codex-Qualification und Promotion gesperrt.
- Sprint 003 darf erst aktiviert werden, wenn Sprint 002 qualifiziert abgeschlossen und archiviert ist oder ein akzeptiertes Sprint-002-Amendment disjunkte Scopes, Ownership und Evidence festlegt.

## Problemstellung und Stakeholder

Die vorhandenen Anwendungen besitzen funktionierende, aber teilweise unterschiedlich ausgedrückte Backend- und UI-Anbindungsanforderungen. Ohne ein gemeinsames fachneutrales Profil drohen parallele Standards, unvollständige Generatoren, app-spezifische Sonderfälle und Drift zwischen OpenAPI, GWC, Runtime und Governance.

Stakeholder sind Springmaster-Maintainer, Entwickler der gemanagten Backend-Projekte, GWC-Entwickler, Architektur- und Security-Reviewer sowie Betreiber der Agenten- und Patchprozesse.

## Anforderungen

Die verbindlichen Anforderungen `S003-REQ-001` bis `S003-REQ-032` sind im `SOLUTION_PLAN.md` vollständig definiert. Der Sprint Brief bindet sie in sieben messbare Ergebnisse:

1. Zielbild, Capability Catalog und Authority Matrix sind vollständig und widerspruchsfrei.
2. Operations-, Resource-, Precondition-, Bulk-, Concurrency- und GWC-Semantik ist normativ entschieden.
3. Maschinenlesbare Schemas, positive und negative Fixtures sowie stabile Diagnosecodes liegen vor.
4. Validator, Operation Catalog und reproduzierbarer Contract-Handoff sind deterministisch ausführbar.
5. Eine minimale opt-in OpenAPI-Runtime und ein Team-Membership-Referenzslice belegen die stabilen Patterns.
6. IDM, Personnel, Contacts, Bulk und GWC werden read-only und ohne widersprüchliche Findings qualifiziert.
7. Deferrals, Folgesprint-Handoff, SemVer und Abschlussentscheidungen sind vollständig evidence-basiert.

## Qualitätsanforderungen

- Keine neue Regel bricht bestehende V1-Verträge oder Application UI Spec v1.1.
- Jede normative Regel besitzt positive und negative automatisierte Evidence.
- Neue Gates beginnen `report-only`; Strict-Promotion erfolgt separat.
- Contract-Artefakte und ZIP-Handoffs sind bei identischem Input byteidentisch reproduzierbar.
- Keine fachliche Entity-, Tabellen-, Lock-Order- oder Security-Entscheidung wird aus einer einzelnen Anwendung verallgemeinert.
- Kein Managed Project wird zur Qualification mutiert.
- Keine Runtime-Reife wird ohne ausführbare Evidence behauptet.
- Agenten ändern niemals gleichzeitig Norm, Oracle, Runtime und Golden Output ohne getrennte menschliche Freigabe.

## In Scope

- Capability Catalog und Cross-App Authority Matrix;
- Operationsidentität, Operation Kind und Operation Roles;
- Resource Roles, History, Temporal Context und Projection Semantik;
- Preconditions, Transaction Scope, Consistency und Bulk-Profile;
- versionierte JSON-Schemas, Fixtures und Diagnosecodes;
- fachneutraler Validator, Operation Catalog und reproduzierbarer Contract-Handoff;
- minimale opt-in OpenAPI-Runtime;
- Team-Membership-Relation-/Candidate-Referenzslice;
- read-only Qualification gegen IDM, Personnel, Contacts, Generic Bulk und GWC;
- GWC-v1.1-/vNext-Kompatibilität und Generator-Handoff;
- Abschluss-, Deferral-, SemVer- und Folgesprint-Evidence.

## Out of Scope

- automatische Migration oder Mutation gemanagter Projekte;
- vollständige Runtime für komplexe Aggregate Graphs;
- persistente Bulk-Execution-, Retry-, Cancellation- oder Deadletter-Runtime;
- produktive Workspace Runtime;
- Ersatz der bestehenden API-Standards durch einen parallelen Standard;
- app-spezifische Fachlogik im Core;
- automatische Strict-Promotion;
- automatische oder globale Codex-Schreibfreigabe;
- unbeaufsichtigte Integration, Accept oder Push.

## Constraints und Abhängigkeiten

- Aktivierungsvoraussetzung aus dem Solution Plan bleibt verbindlich.
- Neue ADR-Nummern werden erst gegen die Live-Baseline vergeben.
- App- und GWC-Quellen bleiben read-only.
- Contract-, Runtime-, Oracle- und Promotion-Schnitte bleiben getrennt.
- `operationKey` wird additiv und versioniert eingeführt; `operationId` bleibt technische Identität.
- Optimistic Locking bleibt Baseline; weitere Strategien sind additive Use-Case-Entscheidungen.
- Codex-Implementierungstasks sind erst nach hostbezogener Confinement-Qualification zulässig.

## Risiken

- Ein zu breiter Schnitt könnte Normen, Schemas, Runtime und Oracles unreviewbar koppeln.
- Unvollständige Abstraktion könnte app-spezifische Sonderfälle in den Core ziehen.
- Zu frühe Runtime-Implementierung könnte nicht geschlossene Bulk-, History-, Concurrency- oder Workspace-Semantik vortäuschen.
- Parallel laufende Sprint-002- und Sprint-003-Arbeit könnte Scope- und Evidence-Ownership verletzen.
- Eine nicht deterministische Generator- oder Handoff-Kette würde den GWC-Cutover blockieren.

## Definition of Ready

- [x] Zielbild und übergeordnete Projektziele sind kanonisch dokumentiert.
- [x] Der Solution Plan enthält Anforderungen, Slices, Teststrategie und Stopkriterien.
- [x] Die erforderlichen Sprintdokumente sind vollständig angelegt und indexiert.
- [ ] Sprint 002 ist qualifiziert abgeschlossen und archiviert oder ein akzeptiertes Amendment definiert disjunkte Scopes und Ownership.
- [ ] Live-Baseline, Versionen, Capability-Reifegrade und relevante Cross-App-Verträge sind erneut verifiziert.
- [ ] Codex Write Readiness ist für gegebenenfalls agentenbasierte Implementierungstasks hostbezogen nachgewiesen.

## Definition of Done

- [ ] Alle Anforderungen `S003-REQ-001` bis `S003-REQ-032` sind erfüllt, deferiert oder blockiert bewertet.
- [ ] Alle Zielbild-Capabilities bleiben im Capability Catalog erhalten.
- [ ] Alle `CONTRACTED`-Fähigkeiten besitzen akzeptierte Standards sowie positive und negative Fixtures.
- [ ] Alle `REFERENCE_IMPLEMENTED`-Fähigkeiten besitzen ausführbare Evidence.
- [ ] Validator, Catalog und Contract-Handoff sind deterministisch und wiederholbar.
- [ ] IDM-, Personnel-, Contacts-, Bulk- und GWC-Fixtures validieren ohne `CONTRADICTORY`-Finding.
- [ ] Bestehende API-, Generated-Slice- und GWC-v1.1-Regressionen bleiben grün.
- [ ] Keine app-spezifische Fachlogik wurde in den Core übernommen.
- [ ] Deferrals besitzen Owner, Ziel-Sprint und Evidence-Bedarf.
- [ ] Completion Report, SemVer-Bewertung und Folgesprint-Handoff sind akzeptiert.

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Aktivierter, driftfreier Sprint-Harness mit Baseline und Capability-Scope | S003-REQ-001, S003-REQ-002, S003-REQ-025, S003-REQ-029, S003-REQ-030 | Aktivierungsvoraussetzung erfüllt; Sprint- und Documentation-Gates ohne Findings | Sprintdokumente, Baseline- und Anti-Drift-Report | springmaster-maintainers | blocked |
| M-002 | Akzeptierte ADRs und Standards für Operations-, Resource-, Precondition-, Concurrency-, Bulk- und GWC-Semantik | S003-REQ-003 bis S003-REQ-018, S003-REQ-023 | jeder Begriff besitzt genau eine normative Definition; keine akzeptierte ADR wird überschrieben | ADRs, Standards, Authority Matrix | springmaster-maintainers | planned |
| M-003 | Versionierte Schemas, positive/negative Fixtures und stabile Diagnosecodes | S003-REQ-019, S003-REQ-024, S003-REQ-027, S003-REQ-032 | Pflicht-Negativfälle scheitern deterministisch; positive Fixtures validieren | JSON-Schemas, Fixture-Familien, Contract-Tests | springmaster-maintainers | planned |
| M-004 | Fachneutraler Validator, Operation Catalog und reproduzierbarer Contract-Handoff | S003-REQ-019, S003-REQ-024, S003-REQ-026 | identischer Zweitlauf; unerwartete Datei blockiert; kein `CONTRADICTORY` | CLI-Reports, Catalog, Manifest, ZIP-Hashes | springmaster-maintainers | planned |
| M-005 | Minimale opt-in OpenAPI-Runtime und Team-Membership-Referenzslice | S003-REQ-020, S003-REQ-021, S003-REQ-023 | unprofilierte APIs unverändert; Relation-, Candidate- und Capability-Patterns ausführbar | Java-/OpenAPI-Tests, Referenzslice-Evidence | springmaster-maintainers | planned |
| M-006 | Cross-App- und GWC-Qualification gegen IDM, Personnel, Contacts, Bulk und Workspace | S003-REQ-022, S003-REQ-026, S003-REQ-032 | alle read-only Fixtures validieren; kein widersprüchliches Finding | Compatibility- und Non-Contradiction-Reports | springmaster-maintainers | planned |
| M-007 | Vollständige Qualification, Deferral-Schutz und Folgesprint-Handoff | S003-REQ-027, S003-REQ-028, S003-REQ-031 | Regressionen grün; Deferrals vollständig; Completion und Handoff akzeptiert | Full-Qualification, Completion Report, Readiness Report | springmaster-maintainers | planned |

## SemVer-Auswirkung

Erwartet wird mindestens ein kompatibler `minor`-Impact für Tooling. Core, Demo, Template und Foundation werden nur erhöht, wenn ein tatsächlich qualifizierter Slice ihre öffentliche oder ausführbare Capability erweitert. Ein reiner Contract-Entwurf rechtfertigt keine pauschale Versionserhöhung.

## Stop- und Abbruchkriterien

Der Sprint beziehungsweise ein Slice stoppt, wenn:

- die Aktivierungsvoraussetzung nicht erfüllt ist;
- eine akzeptierte ADR stillschweigend überschrieben werden müsste;
- ein neuer Primärbegriff ohne Zielbildänderung erforderlich wird;
- eine Anwendung nur durch Änderung ihrer Fachlogik repräsentierbar wäre;
- Optimistic Locking unbegründet aufgehoben würde;
- Bulk Atomicity, Autorisierung oder Non-Disclosure unklar bleibt;
- Workspace und Standard Page nicht sauber getrennt werden können;
- Application UI Spec v1.1 oder Generated Slice V1 brechen würde;
- der Contract-Handoff nicht deterministisch ist;
- ein Finding `CONTRADICTORY` bleibt;
- ein Gate im selben Schnitt unbegründet `strict` werden müsste;
- ein Managed Project zur Qualification mutiert werden müsste.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-30 | – | planned | Sprint Brief auf Basis des vollständigen Solution Plans angelegt. |
| 2026-07-31 | planned | blocked | Aktivierung bis zum qualifizierten Abschluss von Sprint 002 oder einem akzeptierten disjunkten Amendment gesperrt. |

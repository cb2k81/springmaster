# Finale Konsistenz- und Vollständigkeitsprüfung

## Cross-App Backend and GWC Target Architecture

## SPRINGMASTER-SPRINT-003

**Prüfergebnis:** `PASS_AFTER_MANDATORY_AMENDMENT`
**Architektonischer Grundkonflikt:** keiner
**Unverändert repository-fähig:** nein
**Nach den nachfolgenden Korrekturen repository-fähig:** ja

---

# 1. Gesamtbewertung

Das Konzept unterstützt die beiden übergeordneten Ziele grundsätzlich korrekt:

1. Springmaster zentralisiert fachneutralen Core, Tools, Patterns, Verträge, Governance und kontrollierte Managed-Project-Updates.
2. Backend-APIs werden so standardisiert, dass GWC sie über UI Specs und generierte Anwendungen deterministisch konsumieren kann.

Dabei wird richtigerweise nicht verlangt, dass alle Anwendungen dasselbe interne Fachmodell besitzen. Standardisiert werden:

* technische und fachliche Grenzen;
* API-Verträge;
* Security;
* Capabilities;
* Preconditions;
* Qualitätsanforderungen;
* Evidence;
* Contract-Handoffs;
* Generator- und GWC-Bindungen.

Die Fachlogik, Historisierung, Projektionsmodelle und notwendigen Transaktionsgrenzen verbleiben in den Anwendungen.

## Dies entspricht auch der ursprünglichen Empfehlung: Nicht ein vollständiger Backendumbau, sondern ein anwendungsübergreifendes API-Profil soll bestehende gute Strukturen vereinheitlichen und fehlende Semantik ergänzen.

# 2. Weiterhin gültige Architekturentscheidungen

Folgende Entscheidungen sind konsistent und bleiben bestehen:

* `operationKey` ist die stabile fachliche und generatorrelevante Identität.
* `operationId` bleibt eine technische OpenAPI-Identität.
* `operationKind` und `operationRoles[]` werden getrennt.
* Standard Pages und Workspaces bleiben verschiedene Patternfamilien.
* Backend Effects und UI- beziehungsweise Workspace-Reloads bleiben getrennte Verantwortungen.
* Public Preconditions und interne Locking-Verfahren werden getrennt.
* Optimistische, pessimistische und gemischte Konsistenzverfahren sind grundsätzlich zulässig.
* History, Snapshots, append-only Strukturen, Ledger, Read Models und Projections sind eigenständige Semantiken.
* Bulk Commands werden von Composite Commands und Background Jobs unterschieden.
* Capabilities steuern die UI-Projektion, ersetzen aber keine serverseitige Autorisierung.
* Cross-App-Fixtures schützen gegen eine unzulässige Vereinfachung auf IDM- oder CRUD-Niveau.
* Neue Gates starten `report-only`.
* Managed Projects werden in diesem Sprint nur read-only untersucht.

Die Workspace-Abgrenzung ist korrekt: Ein Workspace besitzt eigenen Kontext, Areas, Resource Store, Reload Graph, Mutation Coordinator und Dirty-State-Registry. Er ist keine vergrößerte Detailseite.

Ebenso richtig ist, Workspace-Specs nicht über den Standard-Page-Generator zu erzwingen. Sie benötigen eine eigene Canonical IR und müssen bei unvollständiger Semantik fail-closed bleiben.

---

# 3. Verbindliche Korrekturen am Konzept

## 3.1 Geltungsbereich präzisieren

Das Konzept ist das vollständige Zielbild für den Bereich:

```text
Backend-Architekturverträge
+ API-Standardisierung
+ GWC-Integration
+ Cross-App-Kompatibilität
```

Es ist jedoch nicht die alleinige Gesamtarchitektur für sämtliche Springmaster-Aufgaben.

Die übergeordnete kanonische Zielquelle bleibt:

```text
PROJECT_DOCS/GOVERNANCE/SPRINGMASTER_PROJECT_GOALS.md
```

Das Konzept muss deshalb ausdrücklich formulieren:

> Dieses Konzept operationalisiert die Springmaster-Projektziele für Backend-Patterns, API-Verträge und GWC-Integration. Es ersetzt nicht die übergeordneten Ziel- und Governance-Verträge für zentrale Core-Entwicklung, Tooling-Distribution, Project-New und Managed-Project-Updates.

Der Capability Catalog darf folglich nicht als Katalog aller Springmaster-Fähigkeiten bezeichnet werden, sondern als:

```text
Cross-App Backend and GWC Capability Catalog
```

## 3.2 Repository-Pfade korrigieren

Die bisher vorgeschlagenen Pfade widersprechen teilweise der bestehenden Springmaster-Struktur.

Korrekt sind:

```text
PROJECT_DOCS/CONCEPT/CROSS_APP_BACKEND_GWC_TARGET_ARCHITECTURE_CONCEPT.md
```

nicht:

```text
PROJECT_DOCS/CONCEPTS/...
```

Der Sprint liegt nach Aktivierung unter:

```text
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-003/
```

nicht unter:

```text
PROJECT_DOCS/OPERATIONAL/SPRINTS/...
```

Der Transaktions- und Konsistenzstandard soll die bestehende Struktur nutzen:

```text
PROJECT_DOCS/STANDARDS/ARCHITECTURE/
```

Es soll nicht ohne Not ein neuer Bereich `STANDARDS/PERSISTENCE/` eingeführt werden.

## 3.3 Maschinenlesbare Contract-Pfade korrigieren

Der Springmaster-Verzeichnisvertrag erlaubt unter `contracts/**` derzeit JSON-Artefakte.

Der Capability Catalog muss daher beispielsweise lauten:

```text
contracts/architecture/cross-app-backend-gwc-target-capabilities.v1.json
```

nicht:

```text
...capabilities.v1.yaml
```

Alternativ kann er unter einem ausdrücklich begründeten Governance-Unterpfad liegen. Entscheidend sind JSON-Format und eindeutige Ownership.

## 3.4 Dokumentmetadaten ergänzen

Konzept und Sprintdokumente benötigen die bestehende YAML-Frontmatter.

Das Konzept beginnt beispielsweise mit:

```yaml
---
documentId: DOC-CONCEPT-CROSS-APP-BACKEND-GWC-0001
title: Cross-App Backend and GWC Target Architecture
documentType: architecture-concept
status: review
authority: directive
scopeLevel: ecosystem
scopePaths:
  - springmaster/backend-contracts
  - managed-projects/backend
  - gwc/backend-bindings
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
  - gwc
owner: springmaster-maintainers
createdAt: 2026-07-30
validFrom: null
lastReviewedAt: 2026-07-30
reviewBy: 2026-08-30
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
```

`Proposed` ist für den Dokumenttyp kein gültiger Status. Vor Annahme gilt `review`, danach `active`.

Der Solution Plan benötigt analog:

```yaml
documentType: plan
status: review
authority: directive
temporary: true
sprintId: SPRINGMASTER-SPRINT-003
```

## 3.5 Bestehende Optimistic-Locking-Baseline erhalten

Springmaster besitzt bereits eine akzeptierte Persistence-Baseline mit `DomainEntity.persistenceVersion` als kanonischem optimistischem Versionsfeld für Standard-Aggregate.

Das neue Konzept darf diese Entscheidung nicht indirekt aufheben.

Die korrekte Formulierung lautet:

> Optimistic Locking bleibt die kanonische Baseline für reguläre Springmaster-Aggregate, soweit ADR-0004 und der Domain-Entity-Persistence-Standard gelten. Pessimistische oder gemischte Verfahren dürfen use-case-bezogen zusätzlich eingesetzt werden, wenn Aggregate Graphs, mehrere beteiligte Roots oder fachliche Invarianten dies erfordern.

Damit gilt:

```text
optimistic baseline
+ optional pessimistic synchronization
= MIXED consistency strategy
```

Pessimistisches Locking ist also keine konkurrierende globale Persistence-Strategie, sondern kann eine zusätzliche Synchronisationsmaßnahme innerhalb eines Use Cases sein.

`resourceRole: AGGREGATE_ROOT` darf weder eine konkrete Basisklasse noch eine bestimmte Locking-Strategie implizieren.

---

# 4. Verbindliche Korrekturen an der GWC-Bindung

## 4.1 Versionierter Übergang zu `operationKey`

Im aktuellen GWC-Zielmodell ist `operationKey` bereits als stabile Generatoridentität angelegt. Teile der bestehenden Application-UI-Spec-v1.1-Verträge arbeiten jedoch noch primär mit `operationId`, Methode und Pfad.

Deshalb ist ein versionierter Übergang erforderlich:

```text
Application UI Spec v1.1:
  operationId + method + path bleiben gültig

Application UI Spec vNext:
  operationKey wird primäre fachliche Referenz
  operationId + method + path bleiben Verification Tuple
```

Verbindliche Regeln:

* v1.1 wird nicht brechend verändert;
* `operationKey` wird über eine neue Spec-Version oder vollständig rückwärtskompatible Erweiterung eingeführt;
* eine Änderung der `operationId` benötigt eine explizite Alias- oder Migrationsentscheidung;
* Methode, Pfad und `operationId` bleiben technische Verifikationsmerkmale;
* bestehende IDM- und Personnel-Specs erhalten eine deterministische Migration.

## 4.2 Contract-Source-Ownership festlegen

Ohne diese Entscheidung könnten Java Registry, OpenAPI, Operation Catalog und UI Spec zu vier konkurrierenden Wahrheiten werden.

Die Authority Matrix muss lauten:

| Artefakt                      | Autorität                                                                   |
| ----------------------------- | --------------------------------------------------------------------------- |
| Java Registry oder Annotation | Implementierungs- und Authoringmechanismus                                  |
| generiertes OpenAPI           | kanonischer öffentlicher API-Boundary-Vertrag                               |
| Operation Catalog             | deterministisch aus dem OpenAPI-Profil abgeleitet                           |
| Resource Semantics            | Quelle nur für nicht vollständig in OpenAPI ausdrückbare Ressourcensemantik |
| Application UI Spec           | fachliche und UI-semantische Konsumabsicht                                  |
| Canonical IR                  | normalisierte Generatorprojektion                                           |
| Generated App                 | Ergebnis, niemals manuelle Primärquelle                                     |

Der Operation Catalog darf nicht unabhängig manuell gepflegt werden.

Wenn Resource Semantics öffentliche API-Felder wiederholt, müssen die Werte Referenzen oder exakt konsistenzgeprüfte Duplikate sein.

## 4.3 Mapping statt identischer Enums

Springmaster-Backendprofile und GWC-UI-Verträge dürfen unterschiedliche technische Repräsentationen besitzen.

Beispiel:

```text
Backend:
ROOT_VERSION

GWC:
rootVersion
```

oder:

```text
Backend:
LEDGER_ENTRY

GWC:
auditLedger
```

Erforderlich ist eine versionierte Mappingtabelle, keine erzwungene identische Schreibweise.

Dasselbe gilt für:

* `operationRoles`;
* GWC-`mappingUse`;
* History Models;
* Temporal Context;
* Bulk- und Batch-Begriffe.

---

# 5. Bulk-, Batch- und Background-Job-Abgrenzung

## 5.1 Drei verschiedene Konzepte

Das Zielbild muss drei Fähigkeiten trennen:

### Backend Bulk Command

Ein fachlich einheitlicher Command auf mehreren Zielen.

### GWC Batch Runtime

Eine clientseitige Ausführungs- und Koordinationsruntime, die Einzeloperationen oder eine Backend-Bulk-Operation aufrufen kann.

### Backend Background Job

Eine eigenständige länger laufende Verarbeitung mit Jobstatus, Fortschritt, Ergebnis und gegebenenfalls Cancellation.

Die vorhandene GWC Batch Runtime darf nicht durch eine zweite Bulk Runtime ersetzt werden. Sie erhält später eine Bindung an den standardisierten Backend-Bulk-Vertrag.

Dafür ist eine zusätzliche Zielkapazität erforderlich:

```text
CAP-JOB-001 – Background Job Lifecycle and Status Contract
```

Reifeziel in Sprint 003:

```text
DEFINED
```

Keine Runtime-Implementierung.

## 5.2 Bulk-HTTP-Semantik korrigieren

Der Bulk-Vertrag darf nicht pauschal `200` für jede synchrone Ausführung verlangen.

Korrekte Regel:

* `200`, wenn ein Ergebnis- oder Outcome-Dokument geliefert wird;
* `201`, wenn der Bulk-Command eine neue fachliche Ressource erzeugt und der bestehende Command-Standard dies vorsieht;
* `204`, wenn synchron erfolgreich und bewusst ohne Response Body;
* `202` bei akzeptierter asynchroner Ausführung;
* `409` bei fachlichem oder versionsbasiertem Gesamtkonflikt;
* `412` bei verletzter HTTP-Precondition, insbesondere `If-Match`;
* `428` kann für eine zwingend erforderliche, aber fehlende HTTP-Precondition verwendet werden.

Springmasters bestehende `409`-Semantik für bodybasierte Expected-Version-Konflikte bleibt bestehen.

## 5.3 Sicherheitsneutrale Item-Korrelation

Ein Bulk-Outcome darf keine nicht sichtbare Target-ID offenlegen.

Statt:

```text
targetKey
```

soll der Vertrag unterscheiden:

```text
itemKey
targetReference
```

Dabei gilt:

* `itemKey` ist ein vom Client gelieferter oder serverseitig sicher erzeugter Korrelationswert;
* `targetReference` wird nur ausgegeben, wenn der Actor das Ziel sehen darf;
* bei nicht sichtbaren Zielen wird ausschließlich ein nicht offenbarender Outcome zurückgegeben.

## 5.4 Asynchronen Bulk-Lifecycle ergänzen

Der bisherige Vertrag benötigt zusätzlich:

```text
statusOperationKey
resultOperationKey
statusVisibility
retentionUntil
resultDelivery
pollingPolicy
```

Zulässige Ergebnisformen:

```text
INLINE
PAGED
ARTIFACT
```

Weitere Regeln:

* Status- und Ergebnisoperationen werden erneut autorisiert;
* eine `202`-Antwort liefert eine Execution-ID und vorzugsweise eine Status-Location;
* Status- und Ergebnisdaten besitzen definierte Retention;
* große Einzeloutcome-Mengen dürfen nicht unbegrenzt inline geliefert werden;
* Cancellation wird nur deklariert, wenn sie fachlich und technisch sicher unterstützt wird;
* Selection Tokens und Query Snapshots besitzen Ablaufzeit und Kontextbindung.

---

# 6. Fehlende Zielkapazitäten

Das ursprüngliche Empfehlungsdokument nennt für große administrative Anwendungen neben Bulk ausdrücklich Exportoperationen, serverseitige Aggregationen, Cursor- oder Delta-Pagination sowie History- und Auditprojektionen.

History und Projections sind bereits berücksichtigt. Folgende Zielkapazitäten fehlen noch:

| Capability-ID    | Fähigkeit                         | Sprint-003-Ziel |
| ---------------- | --------------------------------- | --------------- |
| `CAP-EXPORT-001` | Standardisierte Exportoperationen | `DEFINED`       |
| `CAP-QUERY-003`  | Cursor- und Delta-Reads           | `DEFINED`       |
| `CAP-AGG-001`    | Serverseitige Aggregationen       | `DEFINED`       |
| `CAP-JOB-001`    | Background-Job-Lifecycle          | `DEFINED`       |

Diese Fähigkeiten werden nicht in Sprint 003 implementiert. Sie müssen aber im Zielbild und Capability Catalog sichtbar bleiben.

Target-aware Batch-Capability-Evaluation kann unter `CAP-API-004` geführt werden. Die Empfehlungen verlangen zu Recht, Read- und Mutation-Capabilities getrennt zu halten und objektabhängige Entscheidungen gesammelt auswerten zu können.

---

# 7. Ergänzungen am Sprintplan

Folgende Anforderungen sind hinzuzufügen:

| Requirement-ID | Ergänzung                                                                                                                                          |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `S003-REQ-025` | OpenAPI, Operation Catalog, Resource Semantics und UI Spec besitzen eine eindeutige Authority Matrix.                                              |
| `S003-REQ-026` | Application UI Spec v1.1 bleibt kompatibel; `operationKey` wird versioniert migriert.                                                              |
| `S003-REQ-027` | Die bestehende Springmaster-Optimistic-Locking-Baseline bleibt erhalten; pessimistische und gemischte Verfahren sind additive Use-Case-Strategien. |
| `S003-REQ-028` | Backend Bulk Command, GWC Batch Runtime und Background Job werden eindeutig getrennt und gemappt.                                                  |
| `S003-REQ-029` | Async Bulk besitzt Status-, Ergebnis-, Retention-, Autorisierungs- und Result-Delivery-Verträge.                                                   |
| `S003-REQ-030` | Bulk-Outcomes verwenden nicht offenbarende Item-Korrelation.                                                                                       |
| `S003-REQ-031` | Export, Aggregation, Cursor/Delta und Background Jobs bleiben als definierte Zielkapazitäten erhalten.                                             |
| `S003-REQ-032` | Alle neuen Dokument- und Contract-Pfade entsprechen der bestehenden Springmaster-Verzeichnis- und Dokumentationsgovernance.                        |

## Zusätzliche Fixtures

Erforderlich sind:

```text
GWC_APPLICATION_UI_SPEC_V1_1_COMPATIBILITY
GWC_OPERATION_KEY_VNEXT_MIGRATION
GWC_BATCH_RUNTIME_BACKEND_BULK_MAPPING
ASYNC_BULK_PAGED_RESULT
ASYNC_BULK_EXPIRED_RESULT
ASYNC_BULK_UNAUTHORIZED_STATUS
BULK_NON_DISCLOSING_OUTCOME
ETAG_412_PRECONDITION
MISSING_IF_MATCH_428
SPRINGMASTER_OPTIMISTIC_BASELINE_WITH_PESSIMISTIC_USE_CASE
```

## Zusätzliche Negativtests

* Operation Catalog wird unabhängig vom OpenAPI manuell verändert;
* v1.1-Spec wird ohne Versionserhöhung auf `operationKey` umgestellt;
* pessimistische Strategie entfernt den erforderlichen Root-Versionstoken;
* Bulk-Outcome offenbart eine unsichtbare Target-ID;
* asynchrone Statusoperation ist ohne Actor-Bindung abrufbar;
* große Outcomes werden unbegrenzt inline materialisiert;
* GWC Batch Runtime und Backend Background Job werden als identische Fähigkeit klassifiziert;
* Capability Catalog wird als YAML unter dem aktuellen Springmaster-`contracts`-Pfad abgelegt;
* Sprintplan liegt außerhalb von `PROJECT_DOCS/SPRINTS/ACTIVE`.

---

# 8. Sprintaktivierung

SPRINGMASTER-SPRINT-003 darf nicht einfach parallel zum bereits aktiven Sprint 002 aktiviert werden.

Vor Aktivierung ist zwingend genau eine Entscheidung erforderlich:

```text
SPRINT-002 abgeschlossen und archiviert
```

oder:

```text
akzeptiertes Sprint-002-Amendment
+ disjunkte Dateiscopes
+ eindeutige Contract-Ownership
+ getrennte Evidence
```

Diese Entscheidung gehört in die Definition of Ready und ist kein optionaler Planungshinweis.

---

# 9. Bewertung gegen die beiden Gesamtziele

## Ziel 1: Zentrale Standardisierung aller Backend-Anwendungen

**Bewertung nach Amendment:** erfüllt als tragfähiges Zielmodell.

Begründung:

* gemeinsame Core- und Vertragsgrundlagen bleiben zentral;
* Anwendungsspezifika werden nicht in den Core gezogen;
* Abweichungen können sichtbar und qualifiziert bleiben;
* IDM, Personnel und Contacts können trotz unterschiedlicher Modelle beschrieben werden;
* Managed-Project-Migration bleibt kontrolliert und nicht automatisch;
* das Konzept standardisiert Grenzen und Qualitätsanforderungen, nicht die Fachlogik.

Wichtig ist die Scopekorrektur: Das Backend-/GWC-Konzept operationalisiert einen Teil des Springmaster-Gesamtauftrags und ersetzt nicht die übergeordnete Projektzielquelle.

## Ziel 2: Einheitliche GWC-Anbindung über UI Specs und generierte Apps

**Bewertung nach Amendment:** erfüllt als tragfähiges Zielmodell.

Begründung:

* stabile `operationKey`-Bindung;
* maschinenlesbare Operation Roles;
* standardisierte Listen, Details, Relations, Candidates und Commands;
* History-, Projection- und Temporal-Semantik;
* Preconditions und Conflict UX;
* synchrone und asynchrone Bulk-Verträge;
* klare Security- und Capability-Metadaten;
* eindeutige Contract-Source-Ownership;
* versionierter Übergang bestehender UI Specs;
* separate Standard-Page- und Workspace-IR;
* deterministischer Contract-Handoff.

Die ursprüngliche Anforderung, unterschiedliche Apps nicht über identische Pfade, sondern über ein einheitliches semantisches und technisches API-Konzept anzubinden, bleibt vollständig gewahrt.

---

# 10. Finale Entscheidung

```text
ARCHITECTURAL_DIRECTION=PASS
CROSS_APP_DOMAIN_COMPATIBILITY=PASS
GWC_WORKSPACE_COMPATIBILITY=PASS
BULK_CONTRACT_DIRECTION=PASS_WITH_AMENDMENT

SPRINGMASTER_GOVERNANCE_CONSISTENCY=FAIL_BEFORE_PATH_AND_METADATA_FIX
SPRINGMASTER_PERSISTENCE_COMPATIBILITY=FAIL_BEFORE_BASELINE_CLARIFICATION
GWC_V1_1_COMPATIBILITY=FAIL_BEFORE_VERSIONED_MIGRATION
CONTRACT_SOURCE_OWNERSHIP=INCOMPLETE_BEFORE_AUTHORITY_MATRIX
ADVANCED_TARGET_CAPABILITIES=INCOMPLETE_BEFORE_CATALOG_EXTENSION

FINAL_STATUS=PASS_AFTER_MANDATORY_AMENDMENT
FUNDAMENTAL_REDIRECTION_REQUIRED=NO
APP_DOMAIN_MODEL_CHANGES_REQUIRED=NO
SPRINT_SCOPE_EXPANSION_TO_NEW_RUNTIME_REQUIRED=NO
```

Nach Umsetzung dieser Korrekturen bestehen keine bekannten neuen Widersprüche zwischen:

* den Springmaster-Projektzielen;
* der bestehenden Springmaster-Governance;
* den aktuellen Persistence-Grundlagen;
* IDM;
* Personnel;
* Contacts;
* GWC Standard Pages;
* GWC Workspaces;
* Backend Bulk Operations;
* späteren Background-Job-, Export-, Aggregations- und Delta-Read-Fähigkeiten.

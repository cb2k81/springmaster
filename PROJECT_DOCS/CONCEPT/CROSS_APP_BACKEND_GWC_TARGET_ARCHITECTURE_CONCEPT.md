---
documentId: DOC-CONCEPT-CROSS-APP-BACKEND-GWC-0001
title: Cross-App Backend and GWC Target Architecture
documentType: architecture-concept
status: review
authority: directive
scopeLevel: ecosystem
scopePaths:
  - springmaster/standards
  - springmaster/managed-projects
  - springmaster/engineering
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-30
validFrom: null
lastReviewedAt: 2026-07-31
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Cross-App Backend and GWC Target Architecture

## 1. Zweck und Geltungsbereich

Dieses Konzept operationalisiert die Springmaster-Projektziele für Backend-Patterns, API-Verträge und die deterministische GWC-Anbindung. Es ist das dauerhafte Zielbild für:

- Springmaster Core und wiederverwendbare Backend-Bausteine;
- zentrale Backend- und API-Standards;
- Contract-, Generator-, Prüf- und Migrationswerkzeuge;
- gemanagte Backend-Anwendungen;
- Application UI Specs und generierte GWC-Anwendungen;
- Standard Pages, Bulk Actions und Workspaces;
- Cross-App-Qualification und kontrollierte Adoption.

Das Konzept ersetzt nicht `PROJECT_DOCS/GOVERNANCE/SPRINGMASTER_PROJECT_GOALS.md`. Die dort definierten Projektziele bleiben die übergeordnete kanonische Zielquelle. Ebenso ersetzt dieses Konzept keine Governance für Core-Distribution, Project-New, Release, Versionierung, Managed-Project-Updates oder agentenbasierte Entwicklung. Es präzisiert deren fachneutralen Backend- und GWC-Anteil.

## 2. Übergeordnete Ziele

Das Zielbild dient zwei gleichrangigen Zielen:

1. Alle Backend-Anwendungen werden schrittweise über Springmaster standardisiert. Core, Tools, Patterns, Standards, Governance und kontrollierte Updateverfahren werden zentral entwickelt und verwaltet.
2. Backend-APIs werden so standardisiert, dass GWC sie über Application UI Specs und generierte Anwendungen auf einheitliche, deterministische Weise anbinden kann. Im Endausbau müssen die Verträge alle fachlich erforderlichen Strukturen der Anwendungen unterstützen.

Standardisierung bedeutet nicht, dass alle Anwendungen dasselbe interne Domainmodell, dieselben Tabellen oder dieselbe Locking-Strategie verwenden. Springmaster standardisiert Grenzen, Verträge, Qualitätsanforderungen und wiederverwendbare technische Muster. Die Fachlogik bleibt Anwendungseigentum.

## 3. Dokument- und Vertragsautorität

Die Autorität ist eindeutig gestaffelt:

1. `SPRINGMASTER_PROJECT_GOALS.md` definiert die übergeordneten Projektziele.
2. Dieses Konzept definiert das vollständige Backend- und GWC-Zielbild.
3. ADRs entscheiden konkrete Architekturfragen.
4. Standards definieren wiederverwendbare normative Detailregeln.
5. Maschinenlesbare Schemas und Catalogs materialisieren akzeptierte Standards.
6. Referenzimplementierungen belegen Umsetzbarkeit, sind aber erst nach Qualification kanonisch.
7. Sprint Brief und Solution Plan wählen eine begrenzte Teilmenge des Zielbilds aus.
8. Status- und Completion-Dokumente berichten Zustand und Evidence, definieren aber kein neues Zielbild.

Bei einem Widerspruch gilt fail-closed:

```text
STOP
-> Widerspruch klassifizieren
-> zuständige kanonische Quelle bestimmen
-> ADR oder Amendment erstellen
-> Konzept, Standard und Schema gemeinsam korrigieren
-> Cross-App-Fixtures aktualisieren
-> erst danach implementieren
```

Lokale Implementierungen, Generatoren oder Sprintpläne dürfen keinen Zielbildwiderspruch stillschweigend auflösen.

## 4. Architekturprinzipien

### 4.1 Fachlogik bleibt Anwendungseigentum

Springmaster besitzt keine anwendungsspezifischen Regeln für Stellenpläne, Positionen, Beschäftigungsverhältnisse, Kontakte, Adressen, Rollen, Scopes, Löschabhängigkeiten, fachliche Historisierung oder fachliche Sperrreihenfolgen.

### 4.2 Standardisierung der Grenze, nicht des Fachmodells

Springmaster standardisiert insbesondere:

- API- und DTO-Boundaries;
- Operationsidentität;
- Query-, Paging-, Sortier- und Filtersemantik;
- Fehlerverträge;
- Security, Visibility und Capabilities;
- Commands, Preconditions, Relations und Candidates;
- Bulk-, Export-, Aggregations- und Background-Job-Verträge;
- Transaktions- und Konsistenzklassifikation;
- Contract-Handoff, Tests, Evidence und Qualification.

### 4.3 Bestehende ausreichende Verträge bleiben erhalten

Die vorhandenen Springmaster-Verträge für CRUD, Listen, `/all`, `/count`, Detailresolver, Sortier-Allowlist, stabile Tie-Breaker, Commands, Relationships, Command Prechecks, Error Contract, opaque IDs, Servicegrenzen und Generated Slice V1 werden nicht ohne nachgewiesenen Widerspruch neu entworfen. Neue Profile ergänzen diese Verträge additiv.

### 4.4 Keine globale CRUD-Annahme

Nicht jede persistierte Klasse ist eine direkt mutierbare API-Ressource. Zulässige Ressourcenrollen sind mindestens:

```text
AGGREGATE_ROOT
AGGREGATE_MEMBER
VERSION_ENTITY
SNAPSHOT_ENTITY
APPEND_ONLY_RECORD
LEDGER_ENTRY
READ_MODEL
PROJECTION
REFERENCE_DATA
```

Die Rollen beschreiben Semantik und Grenzen. Sie erzwingen keine gemeinsame Java-Basisklasse oder Tabellenstruktur.

### 4.5 Composition over Specialization

Fachneutrale Core-Bausteine werden komponiert. App-spezifische Supercontroller, universelle Root-Aggregate oder Sonderframeworks werden vermieden.

### 4.6 Fail-closed

Unvollständige oder widersprüchliche Verträge werden nicht heuristisch ergänzt. Das gilt besonders für Security, Target Context, Candidate-Semantik, Preconditions, Bulk-Autorisierung, Workspace-Ressourcen, Reload-Abhängigkeiten und Operationsidentitäten.

## 5. Kanonische Operationssemantik

### 5.1 `operationKey`

`operationKey` ist die einzige stabile fachliche und generatorrelevante Operationsidentität.

Beispiele:

```text
personnel.staffing-plan.submit
contacts.location.hard-delete
idm.user-role-assignment.assign
```

Der Schlüssel ist unabhängig von Java-Klasse, Methodenname und Transportpfad. Er ist der primäre Bindungspunkt für Application UI Specs, GWC, Capabilities, Tests, Evidence und Generatoren.

### 5.2 `operationId`

`operationId` bleibt die technische OpenAPI-Identität. Sie ist innerhalb eines OpenAPI-Dokuments eindeutig und lesbar. Methode, Pfad und `operationId` bilden das technische Verification Tuple.

Konkurrierende Primärbegriffe wie `semanticOperationKey`, `functionalOperationId` oder `clientOperationKey` sind nicht zulässig.

### 5.3 Operation Kind

Jede profilierte Operation besitzt genau einen grundlegenden Typ:

```text
QUERY
COMMAND
PRECHECK
CAPABILITY_EVALUATION
```

### 5.4 Operation Roles

Eine Operation kann mehrere Rollen besitzen:

```text
ENTITY_LIST
ENTITY_DETAIL
ENTITY_CREATE
ENTITY_UPDATE
ENTITY_DELETE
REFERENCE_LOOKUP
RELATION_LIST
CANDIDATE_LIST
OVERVIEW_LIST
HISTORY_LIST
PROJECTION_READ
TEMPORAL_READ
BULK_COMMAND
BULK_STATUS
EXPORT
AGGREGATION
DELTA_READ
```

`WORKSPACE` ist weder Operation Kind noch Operation Role.

## 6. Backend Operation Profile

Eine für GWC oder Generatoren relevante Operation beschreibt mindestens die anwendbaren Felder:

```yaml
operationKey:
operationId:
method:
path:
operationKind:
operationRoles:
successStatus:
requestSchema:
responseSchema:
errorContract:
security:
precondition:
resourceSemantics:
affectedResourceKeys:
```

Das Profil ist additiv. Eine einfache CRUD-Operation darf weiterhin ausschließlich die bestehenden Springmaster-Standards verwenden, wenn keine zusätzliche GWC-Semantik benötigt wird.

## 7. Contract-Source-Ownership

Mehrere Artefakte dürfen keine konkurrierenden Wahrheiten bilden.

| Artefakt | Autorität |
|---|---|
| Java Registry oder Annotation | Implementierungs- und Authoringmechanismus |
| generiertes OpenAPI | kanonischer öffentlicher API-Boundary-Vertrag |
| Operation Catalog | deterministisch aus dem profilierten OpenAPI abgeleitet |
| Resource Semantics | Quelle nur für nicht vollständig in OpenAPI ausdrückbare Ressourcensemantik |
| Application UI Spec | fachliche und UI-semantische Konsumabsicht |
| Canonical IR | normalisierte Generatorprojektion |
| Generated App | Ergebnis, niemals manuelle Primärquelle |

Der Operation Catalog darf nicht unabhängig manuell gepflegt werden. Wiederholte öffentliche API-Werte müssen referenziert oder automatisch konsistenzgeprüft sein.

## 8. Security, Visibility und Capabilities

Maschinenlesbare Security-Metadaten umfassen mindestens:

```text
securityClassification
requiredPermission
targetType
targetSource
readVisibility
authorizationEnforcement
```

Capabilities dienen der UI-Projektion und Benutzerführung. Sie ersetzen niemals serverseitige Autorisierung, Target-Prüfung, Zustandsprüfung, Concurrency-Prüfung oder erneute Mutation-Validierung.

Read-, Create-, Update-, Delete-, Assign-, Unassign-, Bulk-, Export- und Workflow-Capabilities müssen unabhängig darstellbar sein. Objekt- oder targetabhängige Capabilities müssen gesammelt auswertbar sein, ohne N+1-Autorisierungszugriffe zu erzwingen.

## 9. Relations und Candidates

Relations beschreiben bestehende Beziehungen. Candidate-Operationen beschreiben mögliche Ziele für eine konkrete Beziehung oder Mutation.

Zulässige Selection-Semantik:

```text
VISIBLE_ONLY
SELECTABLE_IN_CONTEXT
ASSIGNABLE_AT_READ_TIME
```

Auch `ASSIGNABLE_AT_READ_TIME` ist nur eine Read-Time-Aussage. Die Mutation prüft alle fachlichen, sicherheitsbezogenen und concurrencyrelevanten Regeln erneut.

## 10. History, Temporal Context und Projections

Zulässige History-Modelle sind mindestens:

```text
NONE
ROOT_VERSION
PLAN_SNAPSHOT
APPEND_ONLY
TEMPORAL_RELATION
```

Zeitabhängige Operationen können einen expliziten Kontext besitzen:

```yaml
temporalContext:
  mode: VALID_ON
  parameter: validOn
```

oder:

```yaml
temporalContext:
  mode: PLAN_VARIANT
  parameters:
    - planId
    - variantId
```

Read Models und Projections sind eigenständige Read-Verträge. Sie dürfen mehrere Aggregate zusammenführen, berechnete Werte enthalten und eine eigene Paging-, Sortier- und Filtersemantik besitzen. Sie werden nicht als mutierbare Entities behandelt.

## 11. Mutation Preconditions und Concurrency

### 11.1 Öffentliche Preconditions

Zulässige Precondition-Typen sind mindestens:

```text
NONE
EXPECTED_VERSION
EXPECTED_VERSION_SET
SNAPSHOT_TOKEN
ETAG
```

Beispiele:

```yaml
precondition:
  type: EXPECTED_VERSION
  requestBinding: body.expectedVersion
  conflictStatus: 409
```

```yaml
precondition:
  type: SNAPSHOT_TOKEN
  requestBinding: body.snapshotToken
  producerOperationKey: contacts.location.hard-delete.preview
  conflictStatus: 409
```

HTTP-Preconditions wie `If-Match` können `412 Precondition Failed` und bei fehlender zwingender Precondition `428 Precondition Required` verwenden. Bodybasierte Expected-Version-Konflikte bleiben nach bestehendem Springmaster-Vertrag `409 Conflict`.

### 11.2 Optimistic-Locking-Baseline

Die bestehende Springmaster-Baseline mit `DomainEntity.persistenceVersion` bleibt für reguläre Aggregate kanonisch, soweit ADR-0004 und der Domain-Entity-Persistence-Standard gelten.

Pessimistische oder gemischte Verfahren sind additive Use-Case-Strategien. Sie dürfen eingesetzt werden, wenn Aggregate Graphs, mehrere beteiligte Roots oder fachliche Invarianten dies erfordern. Ein pessimistischer Use Case darf den erforderlichen Root-Versionstoken nicht unbegründet entfernen.

### 11.3 Interne Konsistenzklassifikation

```text
transactionScope:
  SINGLE_AGGREGATE
  AGGREGATE_GRAPH
  MULTI_AGGREGATE

consistencyStrategy:
  OPTIMISTIC
  PESSIMISTIC
  MIXED
```

Diese Klassifikation ist Architektur- und Evidence-Semantik, kein UI-Vertrag.

Use Cases mit mehreren pessimistischen Sperren müssen Sperrmenge, deterministische Reihenfolge, Transaktionsgrenze, erneute Validierung, Timeout-/Deadlock-Verhalten, Rollback-Atomizität und API-Fehlerabbildung nachweisen. Die konkrete fachliche Sperrreihenfolge bleibt Anwendungseigentum.

## 12. Backend Bulk Operation Contract

### 12.1 Definition und Abgrenzung

Ein Backend Bulk Command führt einen semantisch einheitlichen Command für mehrere fachliche Ziele aus.

Er ist zu unterscheiden von:

- einem Composite Command für einen fachlich atomaren Aggregate Graph;
- der GWC Batch Runtime als clientseitiger Ausführungs- und Koordinationsruntime;
- einem Backend Background Job mit eigenständigem Lifecycle.

Die vorhandene GWC Batch Runtime wird nicht ersetzt. Sie erhält eine standardisierte Bindung an Einzeloperationen oder Backend-Bulk-Operationen.

### 12.2 Auswahlmodi

```text
EXPLICIT_TARGETS
QUERY_SNAPSHOT
SELECTION_TOKEN
```

Irreversible Mutationen über eine nicht eingefrorene „alle aktuellen Treffer“-Menge sind nicht zulässig. Selection Tokens müssen zeitlich begrenzt, actor- und kontextgebunden sowie manipulationssicher sein.

### 12.3 Atomicity

```text
ALL_OR_NOTHING
PER_TARGET
PER_CHUNK
```

`ALL_OR_NOTHING` erfordert eine beherrschbare Sperr- und Transaktionsmenge. `PER_TARGET` macht Teilerfolg zum Bestandteil des Vertrages. `PER_CHUNK` garantiert Atomizität nur je Chunk.

### 12.4 Execution Mode

```text
SYNCHRONOUS
ASYNCHRONOUS
```

Asynchrone Bulk-Operationen besitzen mindestens:

```text
executionId
state
acceptedAt
statusOperationKey
resultOperationKey
statusVisibility
retentionUntil
resultDelivery
pollingPolicy
```

Zulässige Zustände:

```text
ACCEPTED
RUNNING
COMPLETED
COMPLETED_WITH_FAILURES
FAILED
CANCELLED
```

`CANCELLED` wird nur unterstützt, wenn Cancellation fachlich und technisch sicher ist.

Zulässige Ergebnisformen:

```text
INLINE
PAGED
ARTIFACT
```

Große Outcome-Mengen dürfen nicht unbegrenzt inline materialisiert werden. Status- und Ergebnisoperationen werden bei jedem Zugriff erneut autorisiert.

### 12.5 Autorisierung und Non-Disclosure

Bulk-Autorisierung erfolgt mindestens auf zwei Ebenen:

1. Berechtigung zur Bulk-Operation;
2. Autorisierung jedes einzelnen Ziels.

Nicht autorisierte oder unsichtbare Ziele dürfen nicht offengelegt werden. Outcomes unterscheiden:

```text
itemKey
optional targetReference
```

`itemKey` ist ein sicherer Korrelationswert. `targetReference` wird nur geliefert, wenn das Ziel sichtbar ist.

### 12.6 Preconditions, Idempotenz und Limits

Bulk-Operationen können globale und per-target Preconditions kombinieren.

Idempotenz wird explizit klassifiziert:

```text
IDEMPOTENT
IDEMPOTENCY_KEY_REQUIRED
NON_IDEMPOTENT
```

Ein Idempotency Key wird an Actor, `operationKey`, normalisierte Zielmenge, Commandparameter und fachlichen Kontext gebunden. Derselbe Key mit abweichendem Request wird abgelehnt.

Jede Bulk-Operation deklariert Grenzen wie `maxTargetCount`, `maxPayloadBytes`, `timeoutClass` und unterstützte Execution Modes. Unbegrenzte Bulk-Mutationen sind nicht zulässig.

### 12.7 Duplikate, Reihenfolge und Ergebnisse

```text
duplicateMode:
  REJECT_DUPLICATES
  DEDUPLICATE

outcomeOrder:
  REQUEST_ORDER
  CANONICAL_TARGET_ORDER
```

Interne Sperr- und Verarbeitungsreihenfolge darf abweichen, muss bei concurrencyrelevanten Abläufen deterministisch sein.

Ein Ergebnis enthält mindestens die anwendbaren Felder:

```text
operationKey
executionId
state
atomicity
requestedCount
acceptedCount
succeededCount
failedCount
skippedCount
outcomes
affectedResourceKeys
```

Outcome-Statuswerte:

```text
SUCCEEDED
FAILED
SKIPPED
NOT_DISCLOSED
```

### 12.8 HTTP-Semantik

- `200`, wenn ein synchrones Ergebnis- oder Outcome-Dokument geliefert wird;
- `201`, wenn eine neue fachliche Ressource entsteht und der bestehende Command-Standard dies vorsieht;
- `204`, wenn synchron erfolgreich und bewusst ohne Response Body;
- `202`, wenn eine asynchrone Ausführung akzeptiert wurde;
- `409`, bei fachlichem oder bodybasiertem Gesamtkonflikt;
- `412`, bei verletzter HTTP-Precondition;
- `428`, bei fehlender zwingender HTTP-Precondition.

Ein generischer Zwang zu HTTP `207 Multi-Status` wird nicht eingeführt.

## 13. Background Jobs, Export, Aggregationen und Delta Reads

Das Zielbild enthält zusätzlich folgende Fähigkeiten:

- Background-Job-Lifecycle mit Status, Progress, Ergebnis, Retention und optional sicherer Cancellation;
- standardisierte Exportoperationen mit synchroner oder asynchroner Ausführung und Artifact-Handoff;
- serverseitige Aggregationen für große administrative Sichten;
- Cursor- und Delta-Reads für große oder inkrementell aktualisierte Datenmengen.

Diese Fähigkeiten dürfen in späteren Sprints umgesetzt werden, bleiben aber im Capability Catalog sichtbar und dürfen nicht durch Bulk- oder Projection-Spezialfälle ersetzt werden.

## 14. Backend Effects und GWC-Verantwortung

Das Backend darf fachliche Auswirkungen deklarieren:

```yaml
affectedResourceKeys:
  - personnel.position-posts
  - personnel.staffing-plan:{planId}
```

Das Backend definiert keinen vollständigen UI-Reload-Graph.

Application UI Spec und GWC bestimmen:

- `refreshAfterSuccess`;
- betroffene Seiten oder Workspace Areas;
- aktive, verzögerte oder unterdrückte Reloads;
- Dirty-State-Verhalten;
- Request-Abbruch und Stale-Response-Schutz.

## 15. Application UI Spec und GWC

### 15.1 Versionierter Übergang zu `operationKey`

Application UI Spec v1.1 bleibt kompatibel und kann weiterhin `operationId`, Methode und Pfad als technische Bindung verwenden.

Eine neue Spec-Version oder vollständig rückwärtskompatible Erweiterung führt `operationKey` als primäre fachliche Referenz ein. `operationId`, Methode und Pfad bleiben Verification Tuple. Bestehende IDM- und Personnel-Specs benötigen eine deterministische Migration oder explizite Aliasentscheidung.

### 15.2 Mapping statt identischer Enums

Backendprofile und GWC-Verträge dürfen unterschiedliche technische Schreibweisen besitzen. Eine versionierte Mappingtabelle verbindet beispielsweise `ROOT_VERSION` mit einer GWC-Representation wie `rootVersion`. Identische Enum-Schreibweisen werden nicht erzwungen.

### 15.3 Standard Pages

Standard Pages decken begrenzte, wiederverwendbare Muster ab:

- Entity List und Detail;
- Create und Edit;
- Relation Grid und Candidate Assignment;
- History Presentation und Projection Read;
- Bulk Actions.

### 15.4 Workspaces

Ein Workspace ist eine eigene GWC-Patternfamilie mit:

- stabilem Workspace Key;
- Context Resolver;
- Root Resources und Areas;
- Resource Store;
- Request Keys, Abort und Stale-Response-Schutz;
- Mutation Coordinator;
- Dirty-State-Registry;
- Reload Graph;
- lokaler Navigation;
- eigenem Lifecycle;
- eigener Canonical IR.

Workspace-Specs werden nicht durch den Standard-Page-Generator erzwungen. Unvollständige Workspace-Semantik wird fail-closed abgelehnt.

## 16. Contract-Handoff

Ein vollständiges Contract-Paket umfasst langfristig:

```text
openapi.json
operation-catalog.json
resource-semantics.json
contract-manifest.json
SHA256SUMS
```

Optional:

```text
capability-catalog.json
bulk-operation-catalog.json
implementation-evidence.json
```

Anforderungen:

- versionierte Schemas;
- kanonische JSON-Ausgabe;
- stabile Sortierung;
- Provenance;
- SHA-256-Prüfung;
- reproduzierbares ZIP;
- fail-closed Driftprüfung;
- keine manuell gepflegte zweite Operationstabelle.

## 17. Managed-Project-Strategie

IDM, Personnel, Contacts und weitere Anwendungen werden sliceweise qualifiziert. Kein Big-Bang-Umbau ist vorgesehen.

Zulässige Bewertungen:

```text
CONFORMANT
CONFORMANT_WITH_MAPPING
LEGACY_COMPATIBLE
REQUIRES_ADAPTER
REQUIRES_MIGRATION
BLOCKED_BY_MISSING_PLATFORM_CAPABILITY
```

Eine Migration ist nicht erfolgreich, wenn sie Historie verliert, Transaktionsgrenzen aufbricht, Sperrsemantik abschwächt, Lifecycle-Zustände vereinfacht, Ledger entfernt, Projection Reads in Entity Reads zurückverwandelt oder Security verändert.

Dauerhafte Cross-App-Fixtures schützen mindestens:

```text
IDM_SCOPED_RELATION
PERSONNEL_TEMPORAL_AGGREGATE_GRAPH
CONTACTS_LIFECYCLE_AND_SNAPSHOT_TOKEN
GENERIC_BULK_COMMAND
GWC_STANDARD_PAGE_BINDING
GWC_WORKSPACE_BINDING
```

## 18. Zielkapazitäten

| Capability-ID | Zielkapazität |
|---|---|
| `CAP-API-001` | Stabile Operationsidentität |
| `CAP-API-002` | Query-, Paging-, Filter- und Sortierverträge |
| `CAP-API-003` | Command-, Relation- und Candidate-Verträge |
| `CAP-API-004` | Security- und Capability-Verträge |
| `CAP-CONC-001` | Mutation Preconditions |
| `CAP-CONC-002` | Optimistische, pessimistische und gemischte Konsistenz |
| `CAP-CONC-003` | Aggregate-Graph- und Multi-Aggregate-Transaktionen |
| `CAP-HIST-001` | Root-Version- und Snapshot-Modelle |
| `CAP-HIST-002` | Append-only-, Ledger- und Temporal-Modelle |
| `CAP-PROJ-001` | Read Models und Projections |
| `CAP-BULK-001` | Synchroner Bulk Command |
| `CAP-BULK-002` | Asynchroner Bulk Command |
| `CAP-BULK-003` | Bulk Precheck, Capability und Target Selection |
| `CAP-JOB-001` | Background-Job-Lifecycle und Statusvertrag |
| `CAP-EXPORT-001` | Standardisierte Exportoperationen |
| `CAP-QUERY-003` | Cursor- und Delta-Reads |
| `CAP-AGG-001` | Serverseitige Aggregationen |
| `CAP-GWC-001` | Application UI Spec Backend Binding |
| `CAP-GWC-002` | Standard Page Patterns |
| `CAP-GWC-003` | Bulk Actions und GWC Batch Mapping |
| `CAP-WS-001` | Workspace Contract und Canonical IR |
| `CAP-WS-002` | Resource Store und Reload Graph |
| `CAP-WS-003` | Mutation Coordinator und Dirty State |
| `CAP-TOOL-001` | Operation Catalog und Contract Manifest |
| `CAP-TOOL-002` | Deterministischer Contract-Handoff |
| `CAP-QUAL-001` | Cross-App-Qualification |
| `CAP-MIG-001` | Managed-Project-Migration |

Die IDs werden nach Aktivierung des maschinenlesbaren Catalogs nicht umnummeriert.

## 19. Reifegradmodell

Jede Capability besitzt genau einen Reifegrad:

```text
DEFINED
CONTRACTED
REFERENCE_IMPLEMENTED
CROSS_APP_QUALIFIED
CANONICAL
ROLLED_OUT
```

`CANONICAL` setzt mindestens eine akzeptierte normative Quelle, ausführbare Evidence und Cross-App-Qualification voraus. Ein einzelner Demo- oder Preview-Consumer reicht nicht aus.

## 20. Anti-Drift-Governance

Der aktuelle Reifegrad wird ausschließlich in einem maschinenlesbaren Cross-App Backend and GWC Capability Catalog geführt, vorgesehen unter:

```text
contracts/architecture/cross-app-backend-gwc-target-capabilities.v1.json
```

Der Catalog enthält mindestens:

```text
capabilityId
title
targetMaturity
currentMaturity
owner
normativeSources
schemas
referenceImplementations
qualificationFixtures
blockingGates
plannedSprint
knownDeferrals
```

Jede zielbildrelevante Sprintanforderung referenziert Capability-IDs, Zielreifegrad, Tests und Evidence. Eine deferierte Fähigkeit bleibt sichtbar und besitzt Owner, geplanten Sprint, Blocker und erforderliche Evidence.

Änderungen an Begriffen, Capability-IDs, Verantwortungsgrenzen oder öffentlichen Contract-Feldern benötigen gemeinsam:

1. ADR oder akzeptiertes Amendment;
2. Aktualisierung dieses Konzepts;
3. Versionierung der betroffenen Schemas;
4. Aktualisierung des Capability Catalogs;
5. Cross-App-Kompatibilitätsanalyse;
6. Fixture- und Regressionstests;
7. Migrations- oder Deprecation-Entscheidung.

Shadow Contracts, app-spezifische Core-Schemas, Generatorheuristiken ohne Standard und manuell gepflegte parallele Current-State-Tabellen sind nicht zulässig.

## 21. Test- und Evidence-Zielbild

Das vollständige Ziel benötigt:

- Unit-, Schema- und Contract-Tests;
- positive und negative Fixtures;
- OpenAPI-, Controller-, Service- und Repositorytests;
- Security- und Visibility-Tests;
- DB-Integration-, Concurrency-, Deadlock- und Timeout-Tests;
- Bulk-Partial-Success- und Rollbacktests;
- Determinismus- und Generator-Golden-Tests;
- GWC-Runtime-, Browser- und E2E-Tests;
- Cross-App-Qualification.

Jede normative Regel wird mit Capability, Requirement, Implementation, Test, Fixture, Gate und Evidence verbunden. Dokumentation allein ist kein Erfüllungsnachweis.

## 22. Umsetzungspfad

SPRINGMASTER-SPRINT-003 schafft Contract-, Tooling- und einfache Referenzgrundlagen. Komplexe Aggregate-, Concurrency- und Workspace-Runtimes werden vorbereitet, aber nicht vorgetäuscht.

Ein Folgesprint soll komplexe Aggregate Graphs, gemischte Concurrency, History, Projections und Workspace Foundation referenzimplementieren. Weitere Sprints qualifizieren Bulk Runtime, Background Jobs, Export, Aggregationen, Delta Reads und Managed-Project-Adoption.

## 23. Gesamtziel-Definition of Done

Das Gesamtziel ist erreicht, wenn:

- alle Zielkapazitäten mindestens `CANONICAL` sind;
- APIs, Preconditions, Bulk, Jobs, Export, Aggregation und Delta Reads maschinenlesbar beschrieben sind;
- komplexe Aggregate, Historien, Snapshots, Ledger und Projections referenzimplementiert sind;
- optimistische, pessimistische und gemischte Concurrency qualifiziert sind;
- Standard Pages und Workspaces getrennte kanonische Patternfamilien besitzen;
- GWC keine Pfad- oder Quellcodeheuristiken benötigt;
- IDM, Personnel und Contacts ohne Verlust ihrer Fachlogik abbildbar sind;
- Contract-Handoffs reproduzierbar und driftfrei sind;
- Blocking Gates qualifiziert aktiv sind;
- Managed-Project-Migrationen wiederholbar und auditierbar sind.

## 24. Unveränderliche Leitregeln

> Springmaster vereinheitlicht Verträge, technische Grenzen, Qualitätsanforderungen und wiederverwendbare Patterns. Es vereinheitlicht nicht die Fachlogik der Anwendungen.

> Kein Sprint darf das Gesamtziel verkleinern, indem eine noch nicht implementierte Capability entfernt oder durch einen einfacheren Spezialfall ersetzt wird.

> Eine Capability darf später umgesetzt werden. Ihre Architekturgrenzen und ihre Kompatibilität mit den bekannten Anwendungen müssen jedoch bereits in den vorgelagerten Verträgen berücksichtigt sein.
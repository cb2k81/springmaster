# SPRINGMASTER-SPRINT-003

# Cross-App Backend Contract Foundation and GWC Readiness

**Dokumenttyp:** Sprintplan
**Status:** Proposed
**Übergeordnetes Zielbild:** `PROJECT_DOCS/CONCEPTS/CROSS_APP_BACKEND_GWC_TARGET_ARCHITECTURE_CONCEPT.md`
**Geplanter Ablagepfad:** `PROJECT_DOCS/OPERATIONAL/SPRINTS/SPRINGMASTER-SPRINT-003/SOLUTION_PLAN.md`
**Sprint Owner:** Springmaster Architecture
**Primäre Ziele:** `GOAL-001`, `GOAL-004`, `GOAL-005`
**Sekundäre Ziele:** `GOAL-002`, `GOAL-003`

---

## 1. Sprintauftrag

SPRINGMASTER-SPRINT-003 schafft das fachneutrale und maschinenlesbare Vertragsfundament für unterschiedliche Backendstrukturen und deren deterministische GWC-Anbindung.

Der Sprint muss insbesondere sicherstellen, dass folgende Anwendungsklassen ohne Änderung ihrer Fachlogik Springmaster-konform beschrieben werden können:

* IDM mit target-aware Security, Assignments, Candidates und Capabilities;
* Personnel mit komplexen Aggregate Graphs, Historien, Snapshots, append-only Strukturen, Ledger und Projections;
* Contacts mit eigenen Lifecycle-, Merge-, Lösch-, Restore- und Snapshot-Token-Verträgen;
* einfache CRUD- und Relation-Anwendungen;
* zukünftige GWC Standard Pages;
* zukünftige GWC Workspaces;
* synchrone und asynchrone Backend-Bulk-Operationen.

Der Sprint implementiert nur diejenigen Laufzeitanteile, deren allgemeine Semantik bereits ausreichend abgesichert ist.

Komplexe Aggregate-, Concurrency- und Workspace-Runtimes werden vertraglich vorbereitet, aber erst in einem Folgesprint referenzimplementiert.

---

# 2. Verbindliche Sprintprinzipien

## 2.1 Zielbild vor Sprintscope

Das übergeordnete Zielbild ist normativ.

Der Sprint darf:

* Teilmengen umsetzen;
* Fähigkeiten auf einen höheren Reifegrad heben;
* Implementierungen bewusst deferieren.

Der Sprint darf nicht:

* Zielkapazitäten entfernen;
* Begriffe neu definieren;
* noch nicht implementierte Fähigkeiten durch einfachere Spezialfälle ersetzen;
* lokale Sprintentscheidungen als konkurrierendes Zielbild etablieren.

## 2.2 Bestehende ausreichende Strukturen bleiben erhalten

Bereits ausreichende Springmaster-Verträge werden nicht neu entworfen.

Dies gilt insbesondere für:

* DTO- und API-Boundaries;
* Paging;
* Sortier-Allowlist;
* stabile sekundäre Sortierung;
* Filtergrundlagen;
* `/all`- und `/count`-Semantik;
* Detailresolver;
* Commands;
* Relationships;
* Command Prechecks;
* Fehlervertrag;
* opaque IDs;
* Service- und Transaktionsgrenzen;
* Permission- und Capability-Abgrenzung;
* bestehende Generated-Slice-V1-Verträge.

An diesen Strukturen sind nur zulässig:

* semantische Präzisierungen;
* Querverweise;
* additive Metadaten;
* dokumentierte Konsistenzkorrekturen.

## 2.3 Fachmodelle bleiben Anwendungseigentum

Der Sprint führt keine allgemeinen fachlichen Basisklassen ein für:

* Stellenpläne;
* Personen;
* Positionen;
* Kontakte;
* Adressen;
* Rollen;
* Scopes;
* Historien;
* Snapshots;
* Ledger;
* Lifecycle-Zustände.

## 2.4 Contract before Runtime

Die Reihenfolge ist verbindlich:

```text
Zielbild
-> ADR
-> Standard
-> maschinenlesbares Schema
-> positive und negative Fixtures
-> Validator
-> minimale Runtime
-> Referenzslice
-> Cross-App-Qualification
-> mögliche Canonicalization
```

Keine Runtimeklasse wird eingeführt, bevor die relevante Semantik normativ und durch negative Fixtures abgesichert ist.

---

# 3. Sprintziel

Nach Abschluss des Sprints verfügt Springmaster über:

1. einen aktiven, dauerhaften Cross-App-Zielbildvertrag;
2. einen maschinenlesbaren Capability Catalog;
3. stabile allgemeine Begriffe für Backend-Operationen;
4. versionierte Verträge für:

    * Operationsidentität;
    * Security und Capabilities;
    * Relations und Candidates;
    * History und Temporal Context;
    * Read Models und Projections;
    * Mutation Preconditions;
    * Transaktions- und Konsistenzklassifikation;
    * synchrone und asynchrone Bulk-Operationen;
    * Backend Effects;
5. einen deterministischen Operation Catalog;
6. ein reproduzierbares Contract-Handoff;
7. eine minimale allgemeine OpenAPI-Runtime;
8. einen einfachen Relation- und Candidate-Referenzslice;
9. Cross-App-Fixtures für IDM, Personnel, Contacts, Bulk und GWC;
10. einen automatisierten Non-Contradiction- und Anti-Drift-Nachweis;
11. einen qualifizierten Handoff an den Folgesprint für komplexe Aggregate und Workspaces.

---

# 4. Capability-Scope und Reifegradsprünge

Die endgültigen Ist-Reifegrade werden in Phase 0 gegen die Live-Baseline verifiziert.

Der Sprint darf die nachfolgend geplanten Zielreifegrade nicht unterschreiten.

| Capability-ID  | Fähigkeit                                              | Sprintziel                                            |
| -------------- | ------------------------------------------------------ | ----------------------------------------------------- |
| `CAP-API-001`  | Stabile Operationsidentität                            | `REFERENCE_IMPLEMENTED`                               |
| `CAP-API-002`  | Query-, Paging-, Filter- und Sortierverträge           | bestehenden Reifegrad erhalten und regressionssichern |
| `CAP-API-003`  | Command-, Relation- und Candidate-Verträge             | `REFERENCE_IMPLEMENTED`                               |
| `CAP-API-004`  | Security- und Capability-Verträge                      | `REFERENCE_IMPLEMENTED`                               |
| `CAP-CONC-001` | Mutation Preconditions                                 | `CONTRACTED`                                          |
| `CAP-CONC-002` | Optimistische, pessimistische und gemischte Konsistenz | `CONTRACTED`                                          |
| `CAP-CONC-003` | Aggregate-Graph- und Multi-Aggregate-Transaktionen     | `CONTRACTED`                                          |
| `CAP-HIST-001` | Root-Version- und Snapshot-Modelle                     | `CONTRACTED`                                          |
| `CAP-HIST-002` | Append-only-, Ledger- und Temporal-Modelle             | `CONTRACTED`                                          |
| `CAP-PROJ-001` | Read Models und Projections                            | `CONTRACTED`                                          |
| `CAP-BULK-001` | Synchroner Bulk Command                                | `CONTRACTED`                                          |
| `CAP-BULK-002` | Asynchroner Bulk Command                               | `CONTRACTED`                                          |
| `CAP-BULK-003` | Bulk Precheck, Capability und Target Selection         | `CONTRACTED`                                          |
| `CAP-GWC-001`  | Application UI Spec Backend Binding                    | `CONTRACTED`                                          |
| `CAP-GWC-002`  | Standard Page Patterns                                 | bestehenden Reifegrad erhalten                        |
| `CAP-GWC-003`  | Bulk Actions                                           | `CONTRACTED`                                          |
| `CAP-WS-001`   | Workspace Contract und Canonical IR                    | `DEFINED`, Kompatibilität nachgewiesen                |
| `CAP-WS-002`   | Resource Store und Reload Graph                        | `DEFINED`, Schnittstellen vorbereitet                 |
| `CAP-WS-003`   | Mutation Coordinator und Dirty State                   | `DEFINED`, Schnittstellen vorbereitet                 |
| `CAP-TOOL-001` | Operation Catalog und Contract Manifest                | `REFERENCE_IMPLEMENTED`                               |
| `CAP-TOOL-002` | Deterministischer Contract-Handoff                     | `REFERENCE_IMPLEMENTED`                               |
| `CAP-QUAL-001` | Cross-App-Qualification                                | `REFERENCE_IMPLEMENTED`                               |
| `CAP-MIG-001`  | Managed-Project-Migration                              | `DEFINED`, nicht umgesetzt                            |

## 4.1 Reifegradbegrenzung

Im Sprint dürfen nur folgende Fähigkeiten `REFERENCE_IMPLEMENTED` erreichen:

* Operationsidentität;
* Relation und Candidate;
* Security und Capability;
* Operation Catalog;
* Contract-Handoff;
* Cross-App-Qualification.

Folgende Fähigkeiten bleiben bewusst auf `CONTRACTED`:

* komplexe Concurrency;
* Aggregate-Graph-Transaktionen;
* History;
* Projections;
* Bulk Runtime.

Folgende Fähigkeiten bleiben bewusst auf `DEFINED`:

* produktive Workspace Runtime;
* Managed-Project-Migration.

---

# 5. Sprintanforderungen

| Requirement-ID | Anforderung                                                                                                            | Capability-IDs                                         |
| -------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `S003-REQ-001` | Das dauerhafte Zielbild wird als aktive normative Konzeptquelle persistiert.                                           | alle                                                   |
| `S003-REQ-002` | Ein maschinenlesbarer Capability Catalog bildet Ziel- und Ist-Reifegrade ab.                                           | alle                                                   |
| `S003-REQ-003` | `operationKey` ist die einzige stabile fachliche Operationsidentität.                                                  | `CAP-API-001`                                          |
| `S003-REQ-004` | `operationId` bleibt technische OpenAPI-Identität.                                                                     | `CAP-API-001`                                          |
| `S003-REQ-005` | `operationKind` und `operationRoles[]` werden getrennt modelliert.                                                     | `CAP-API-001`, `CAP-GWC-001`                           |
| `S003-REQ-006` | Bestehende Paging-, Filter- und Sortierverträge bleiben unverändert kompatibel.                                        | `CAP-API-002`                                          |
| `S003-REQ-007` | Relation-, Candidate- und Capability-Semantik wird fachneutral und maschinenlesbar.                                    | `CAP-API-003`, `CAP-API-004`                           |
| `S003-REQ-008` | Resource Roles und History Models können komplexe App-Strukturen darstellen.                                           | `CAP-HIST-001`, `CAP-HIST-002`, `CAP-PROJ-001`         |
| `S003-REQ-009` | Temporal Context kann Stichtage, Plan- und Variantenkontexte ausdrücken.                                               | `CAP-HIST-002`, `CAP-PROJ-001`                         |
| `S003-REQ-010` | Preconditions unterstützen mindestens `NONE`, `EXPECTED_VERSION`, `EXPECTED_VERSION_SET`, `SNAPSHOT_TOKEN` und `ETAG`. | `CAP-CONC-001`                                         |
| `S003-REQ-011` | Öffentliche Preconditions und interne Locking-Strategien bleiben getrennt.                                             | `CAP-CONC-001`, `CAP-CONC-002`                         |
| `S003-REQ-012` | Transaktionsumfänge unterstützen Single Aggregate, Aggregate Graph und Multi Aggregate.                                | `CAP-CONC-003`                                         |
| `S003-REQ-013` | Konsistenzstrategien unterstützen optimistische, pessimistische und gemischte Verfahren.                               | `CAP-CONC-002`                                         |
| `S003-REQ-014` | Synchroner und asynchroner Bulk Command werden vollständig normativ beschrieben.                                       | `CAP-BULK-001`, `CAP-BULK-002`                         |
| `S003-REQ-015` | Bulk Selection, Atomicity, Autorisierung, Preconditions, Idempotenz, Limits und Outcomes sind maschinenlesbar.         | `CAP-BULK-003`                                         |
| `S003-REQ-016` | Backend Effects und GWC Refresh-/Reload-Verantwortung werden getrennt.                                                 | `CAP-GWC-001`, `CAP-WS-002`                            |
| `S003-REQ-017` | Workspace bleibt eine eigene GWC-Patternfamilie.                                                                       | `CAP-WS-001` bis `CAP-WS-003`                          |
| `S003-REQ-018` | Ein allgemeiner Operation Catalog wird deterministisch erzeugt und validiert.                                          | `CAP-TOOL-001`                                         |
| `S003-REQ-019` | Ein reproduzierbares, hashgesichertes Contract-Bundle wird erzeugt.                                                    | `CAP-TOOL-002`                                         |
| `S003-REQ-020` | Ein einfacher Relation- und Candidate-Slice demonstriert die stabilen Runtime-Patterns.                                | `CAP-API-001`, `CAP-API-003`, `CAP-API-004`            |
| `S003-REQ-021` | IDM, Personnel und Contacts werden durch read-only Cross-App-Fixtures repräsentiert.                                   | `CAP-QUAL-001`                                         |
| `S003-REQ-022` | Keine allgemeine Regel erzwingt eine Änderung der Fachmodelle der Apps.                                                | alle                                                   |
| `S003-REQ-023` | Jede normative Regel besitzt positive und negative automatisierte Nachweise.                                           | alle                                                   |
| `S003-REQ-024` | Der Sprint erzeugt einen qualifizierten, driftfreien Handoff an Sprint 004.                                            | `CAP-WS-*`, `CAP-CONC-*`, `CAP-HIST-*`, `CAP-PROJ-001` |

---

# 6. Phasen

## Phase 0 – Sprintinitialisierung, Baseline und Anti-Drift-Fundament

### Ziel

Der aktuelle Zustand wird eingefroren und alle weiteren Arbeiten werden an das dauerhafte Zielbild gebunden.

### Arbeitspakete

1. Sprintverzeichnis und Harness anlegen.
2. Folgende Dokumente initialisieren:

    * `SPRINT_BRIEF.md`;
    * `SOLUTION_PLAN.md`;
    * `STATUS.md`;
    * vorbereiteter `COMPLETION_REPORT.md`.
3. Git-, Export-, Versions- und Gate-Baseline erfassen.
4. Zielbildkonzept unter dem kanonischen Pfad persistieren.
5. Capability Catalog V1 erstellen.
6. Requirements-to-Capability-Matrix erzeugen.
7. Requirements-to-Test-Matrix vorbereiten.
8. bestehende Standards klassifizieren:

```text
KEEP
CLARIFY
GENERALIZE
EXTEND
DEFER
```

9. Cross-App Pattern Compatibility Matrix erstellen.
10. Naming Decision Matrix erstellen.
11. Abhängigkeiten und Schreibkonflikte zu anderen aktiven Sprints klären.
12. Dateiscopes für alle folgenden Änderungsschnitte festlegen.

### Pflichtartefakte

```text
PROJECT_DOCS/CONCEPTS/CROSS_APP_BACKEND_GWC_TARGET_ARCHITECTURE_CONCEPT.md
contracts/architecture/cross-app-backend-gwc-target-capabilities.v1.yaml
PROJECT_DOCS/OPERATIONAL/SPRINTS/SPRINGMASTER-SPRINT-003/SPRINT_BRIEF.md
PROJECT_DOCS/OPERATIONAL/SPRINTS/SPRINGMASTER-SPRINT-003/SOLUTION_PLAN.md
PROJECT_DOCS/OPERATIONAL/SPRINTS/SPRINGMASTER-SPRINT-003/CROSS_APP_PATTERN_COMPATIBILITY_MATRIX.md
PROJECT_DOCS/OPERATIONAL/SPRINTS/SPRINGMASTER-SPRINT-003/NAMING_DECISION_MATRIX.md
```

### Tests und Gates

* Dokumentations-Gate;
* eindeutige Capability-IDs;
* alle Sprintanforderungen referenzieren bekannte Capability-IDs;
* keine Capability des Zielbilds fehlt im Catalog;
* kein unbekannter Primärbegriff;
* keine Dateiscope-Überlappung mit parallelem Sprint;
* `git diff --check`.

### Exit-Kriterium

Phase 1 beginnt erst, wenn:

* das Zielbild aktiv ist;
* der Capability Catalog validiert;
* die Cross-App-Matrix vollständig;
* die Terminologie akzeptiert;
* der Sprintscope konfliktfrei ist.

---

## Phase 1 – ADRs und normative Standards

### Ziel

Alle neuen Semantiken werden entschieden, bevor Schemas und Runtime entstehen.

### ADR-Themen

Die konkrete Anzahl der ADRs ist in Phase 0 zu minimieren. Inhaltlich müssen entschieden werden:

1. Operationsidentität und Operation Roles;
2. Cross-App Resource Semantics;
3. Mutation Preconditions und Concurrency Classification;
4. Bulk Operation Contract;
5. Backend Effects und GWC Reload Ownership;
6. Contract Source, Catalog und Handoff.

### Neue oder ergänzte Standards

Voraussichtlich:

```text
PROJECT_DOCS/STANDARDS/API/GWC_BACKEND_API_PROFILE_STANDARD.md
PROJECT_DOCS/STANDARDS/API/BULK_OPERATION_CONTRACT_STANDARD.md
PROJECT_DOCS/STANDARDS/API/MUTATION_PRECONDITION_STANDARD.md
PROJECT_DOCS/STANDARDS/ARCHITECTURE/RESOURCE_HISTORY_AND_PROJECTION_STANDARD.md
PROJECT_DOCS/STANDARDS/PERSISTENCE/TRANSACTION_AND_CONSISTENCY_CLASSIFICATION_STANDARD.md
```

Bestehende Standards werden nur additiv referenziert oder präzisiert.

### Normative Pflichtentscheidungen

#### Operationsidentität

```text
operationKey
operationId
operationKind
operationRoles[]
```

#### Resource Roles

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

#### History Models

```text
NONE
ROOT_VERSION
PLAN_SNAPSHOT
APPEND_ONLY
TEMPORAL_RELATION
```

#### Preconditions

```text
NONE
EXPECTED_VERSION
EXPECTED_VERSION_SET
SNAPSHOT_TOKEN
ETAG
```

#### Transaction Scope

```text
SINGLE_AGGREGATE
AGGREGATE_GRAPH
MULTI_AGGREGATE
```

#### Consistency Strategy

```text
OPTIMISTIC
PESSIMISTIC
MIXED
```

#### Bulk

```text
selectionMode:
  EXPLICIT_TARGETS
  QUERY_SNAPSHOT
  SELECTION_TOKEN

atomicity:
  ALL_OR_NOTHING
  PER_TARGET
  PER_CHUNK

executionMode:
  SYNCHRONOUS
  ASYNCHRONOUS
```

### Tests und Gates

* ADR-Governance;
* Dokumentverlinkung;
* Terminologieprüfung;
* keine doppelte Definition bestehender API-Semantik;
* kein IDM-, Personnel- oder Contacts-spezifischer Begriff in allgemeinen Regeln;
* negative Dokumentfixtures für widersprüchliche Beispiele.

### Exit-Kriterium

Alle für Schema und Runtime relevanten Begriffe besitzen genau eine normative Definition.

---

## Phase 2 – Maschinenlesbare Schemas und Fixtures

### Ziel

Die Standards werden als versionierte, strikt validierbare Verträge materialisiert.

### Vorgesehene Schemas

```text
contracts/api/schemas/backend-operation-profile.schema.v1.json
contracts/api/schemas/backend-resource-semantics.schema.v1.json
contracts/api/schemas/backend-precondition-profile.schema.v1.json
contracts/api/schemas/backend-bulk-operation-profile.schema.v1.json
contracts/api/schemas/backend-implementation-evidence.schema.v1.json
contracts/api/schemas/operation-catalog.schema.v1.json
contracts/api/schemas/contract-manifest.schema.v1.json
```

Die Dateiaufteilung darf reduziert werden, wenn Verantwortungsgrenzen erhalten bleiben.

### Positive Fixtures

#### Einfache Ressourcen

* Entity List;
* Entity Detail;
* Command;
* Relation List;
* Candidate List;
* Capability Evaluation.

#### History und Projection

* Root Version;
* Plan Snapshot;
* Append-only Record;
* Ledger Entry;
* Temporal Read;
* Projection Read.

#### Preconditions

* Expected Version;
* Expected Version Set;
* Snapshot Token;
* ETag.

#### Bulk

* synchron, explizite Ziele, `ALL_OR_NOTHING`;
* synchron, explizite Ziele, `PER_TARGET`;
* synchron, `PER_CHUNK`;
* asynchron mit Statusoperation;
* Selection Token;
* Query Snapshot;
* Bulk Precheck;
* Bulk Capability;
* Idempotency Key;
* per-target Expected Version.

### Negative Fixtures

Mindestens:

1. doppelter `operationKey`;
2. doppelter `operationId`;
3. unbekannter `operationKind`;
4. unbekannte `operationRole`;
5. `WORKSPACE` als Backendoperation;
6. Candidate ohne Target Context;
7. Temporal Read ohne Temporal Context;
8. Projection ohne Response Schema;
9. Ledger Entry als normale Update-Ressource;
10. Append-only-Ressource mit Delete-Operation;
11. Snapshot Token ohne Producer-Operation;
12. Expected Version Set ohne vollständige Bindings;
13. pessimistische JPA-Details im öffentlichen Profil;
14. UI-Reload-Graph im Backendprofil;
15. Bulk ohne Atomicity;
16. asynchrones Bulk ohne Statusoperation;
17. Selection Token ohne Actor- oder Kontextbindung;
18. irreversible Query-Auswahl ohne Snapshot-Semantik;
19. `ALL_OR_NOTHING` mit deklarierter Partial-Success-Semantik;
20. `PER_TARGET` ohne Einzeloutcomes;
21. Bulk ohne Maximalgrenze;
22. idempotenzpflichtige Operation ohne Idempotency-Key-Vertrag;
23. unklare Duplikatbehandlung;
24. Bulk-Capability als Ersatz für Zielautorisierung;
25. unbekannter `affectedResourceKey`.

### Tests und Gates

* vollständige JSON-Schema-Validierung;
* positive Fixtures bestehen;
* negative Fixtures scheitern mit stabilem Diagnosecode;
* Schemafelder sind versioniert;
* unbekannte Felder werden nach Profilregel behandelt;
* Arrays mit semantischer Mengenbedeutung werden kanonisch sortiert.

### Exit-Kriterium

Kein Validator- oder Runtimecode beginnt, bevor alle Pflicht-Negativfälle vorhanden sind.

---

## Phase 3 – Validator, Operation Catalog und Contract-Handoff

### Ziel

Die neuen Verträge werden deterministisch verarbeitet, geprüft und exportiert.

### Tooling

Vorgesehen ist ein klar abgegrenztes Tool mit Subcommands, beispielsweise:

```text
bin/backend-contract.py validate
bin/backend-contract.py catalog
bin/backend-contract.py verify
bin/backend-contract.py export
```

Ein Shell-Wrapper ist zulässig.

Mehrere fast identische Einzeltools sind zu vermeiden.

### Pflichtfunktionen

* Schemas validieren;
* OpenAPI und Profilquellen einlesen;
* `operationKey` und `operationId` prüfen;
* Method-/Pfad-Binding prüfen;
* Operation Roles validieren;
* Security-Metadaten prüfen;
* Precondition-Bindings prüfen;
* Bulk-Verträge prüfen;
* Operation Catalog erzeugen;
* Capability-Bezüge prüfen;
* Manifest mit Provenance und Hashes erzeugen;
* kanonisches JSON schreiben;
* reproduzierbares ZIP erzeugen;
* Drift erkennen;
* unbekannte oder widersprüchliche Verträge fail-closed ablehnen.

### Contract-Paket

```text
openapi.json
operation-catalog.json
resource-semantics.json
contract-manifest.json
SHA256SUMS
```

Optional:

```text
bulk-operation-catalog.json
capability-catalog.json
implementation-evidence.json
```

### Determinismustests

Bei identischem Input byteidentisch:

* Catalog;
* Manifest;
* Hashdatei;
* ZIP;
* ZIP-Sidecar;
* Compatibility Reports.

Testvarianten:

* unterschiedliche Locale;
* unterschiedliche Zeitzone;
* unterschiedliche Dateisystemreihenfolge;
* unterschiedliche Arbeitsverzeichnisse;
* wiederholte Ausführung;
* normalisierbare Zeilenenden;
* konstante ZIP-Zeitstempel.

### Negative Toolingtests

* fehlende Datei;
* ungültiges Schema;
* Hashabweichung;
* Catalog-/OpenAPI-Drift;
* unbekannte Operation;
* doppelte Operationsidentität;
* ungültige Bulk-Statusreferenz;
* unbekannte Capability-ID;
* Manifest enthält unerwartete Datei;
* nichtdeterministische Reihenfolge.

### Exit-Kriterium

Das Tooling arbeitet read-only gegenüber Quellprojekten und liefert reproduzierbare Ergebnisse.

---

## Phase 4 – Allgemeine OpenAPI-Runtime

### Ziel

Nur die stabilen, appübergreifend verstandenen Profilteile werden in Springmaster Runtime-Unterstützung umgesetzt.

### Vorgesehene fachneutrale Bausteine

Beispielsweise:

```text
ApiOperationContract
ApiOperationContractRegistry
ApiOperationKind
ApiOperationRole
ApiSecurityContract
ApiPreconditionContract
ApiResourceSemantics
ApiOperationEffects
ApiOperationContractCustomizer
```

Die tatsächliche Typzahl ist zu minimieren.

### Runtime-Grenzen

Die Runtime darf:

* Operationsmetadaten registrieren;
* Eindeutigkeit prüfen;
* OpenAPI Extensions materialisieren;
* profilierte Operationen fail-closed validieren;
* stabile Reihenfolge erzeugen.

Die Runtime darf nicht:

* pessimistische Sperren ausführen;
* Aggregate Graphs verwalten;
* History automatisch persistieren;
* Bulk-Operationen orchestrieren;
* Workspace Reload Graphs bestimmen;
* app-spezifische Operationstabellen enthalten.

### OpenAPI Extensions

Mindestens:

```text
x-cocondo-operation-key
x-cocondo-operation-kind
x-cocondo-operation-roles
x-cocondo-success-status
x-cocondo-idempotency
x-cocondo-security-classification
x-cocondo-required-permission
x-cocondo-target-type
x-cocondo-target-source
x-cocondo-read-visibility
x-cocondo-authorization-enforcement
```

Falls anwendbar:

```text
x-cocondo-precondition-type
x-cocondo-resource-roles
x-cocondo-history-model
x-cocondo-temporal-context
x-cocondo-affected-resource-keys
x-cocondo-bulk-contract
```

### Tests

#### Unit

* Schlüsselgrammatik;
* Enum-Validierung;
* unveränderliche Collections;
* Reihenfolge;
* Null- und Whitespace-Behandlung;
* Locale-Unabhängigkeit.

#### Spring Context

* vollständige Registry startet;
* doppelter Key verhindert Start;
* profilierte Operation ohne Contract verhindert Start;
* Contract ohne zugehörige Operation wird gemäß Pflichtstatus abgelehnt;
* unprofilierte vorhandene Endpunkte bleiben unverändert.

#### OpenAPI

* alle Extensions korrekt;
* keine Java-Klassennamen;
* keine App-spezifischen Kernbegriffe;
* Success Status vorhanden;
* Error Contract vorhanden;
* Arrays deterministisch;
* bestehende OpenAPI-Goldens bleiben kompatibel.

### Exit-Kriterium

Die neue Runtime ist opt-in und verändert keine vorhandene unprofilierte API.

---

## Phase 5 – Einfacher Relation- und Candidate-Referenzslice

### Ziel

Die bereits stabilen Patterns werden ausführbar demonstriert.

### Referenzdomäne

```text
Team Membership
```

Der Begriff `Workspace` wird nicht für diese einfache Fachressource verwendet.

### Vorgesehene Operationen

```text
GET    /api/demo/teams
GET    /api/demo/teams/{teamId}
GET    /api/demo/teams/{teamId}/members
GET    /api/demo/teams/{teamId}/member-candidates
GET    /api/demo/team-memberships
POST   /api/demo/teams/{teamId}/members
DELETE /api/demo/teams/{teamId}/members/{memberId}
GET    /api/demo/team-membership-capabilities
```

Die Pfade werden vor Implementierung gegen den bestehenden Relationship-Standard geprüft.

### Zu demonstrierende Fähigkeiten

* `operationKey`;
* `operationKind`;
* mehrere `operationRoles`;
* paginierte Liste;
* exakter Detailresolver;
* Relation List;
* Candidate List;
* Overview List;
* getrennte Read-, Assign- und Unassign-Capabilities;
* target-aware Security;
* serverseitige Visibility;
* erneute Mutation Authorization;
* stabile Row Identity;
* Sortier-Allowlist;
* stabiler Tie-Breaker;
* Command Effects;
* Fehlervertrag.

### Nicht zu demonstrieren

* Workspace Runtime;
* komplexe Historisierung;
* Multi-Aggregate-Transaktionen;
* pessimistische Sperren;
* Bulk Runtime;
* Personnel- oder Contacts-Fachlogik.

### Testumfang

#### Paging und Query

* leere Seite;
* erste, mittlere und letzte Seite;
* maximale Seitengröße;
* ungültige Seitengröße;
* erlaubte Sortierung;
* abgelehnte Sortierung;
* gleiche Primärsortierwerte;
* stabiler Tie-Breaker;
* List und Count mit identischem Visibility-Prädikat.

#### Detail

* sichtbar;
* unbekannt;
* nicht sichtbar;
* Direktaufruf;
* Deep Link;
* vollständige Displaydaten.

#### Candidate

* sichtbar, aber nicht auswählbar;
* auswählbar;
* bereits zugeordnet;
* Target fehlt;
* Target unsichtbar;
* Candidate außerhalb des Actor Scope;
* Status ändert sich zwischen Read und Mutation;
* Mutation prüft erneut.

#### Commands

* Assign erfolgreich;
* Duplicate Assign;
* Unassign erfolgreich;
* unbekannte Relation;
* nicht entziehbare Relation;
* fehlende Permission;
* Target-Scope-Verletzung;
* Zustandskonflikt;
* korrekte Effects.

#### Capabilities

* Read-only;
* Assign-only;
* Unassign-only;
* vollständig berechtigt;
* unberechtigt;
* mehrere Targets;
* Capability ersetzt keine Autorisierung.

#### Security

```text
401 unauthenticated
403 unauthorized
404 unknown or deliberately undisclosed
409 conflict
503 policy evaluation unavailable
```

`503` wird nur verwendet, wenn ein realer Ausfallpfad modelliert ist.

### Exit-Kriterium

Der Slice belegt ausschließlich die stabilen Runtimeverträge und wird als `candidate-reference-slice` klassifiziert.

---

## Phase 6 – Cross-App-Fixtures und Non-Contradiction-Qualification

### Ziel

Das Profil wird gegen die strukturell unterschiedlichen Anwendungen geprüft, ohne diese zu verändern.

### Fixture A – IDM Scoped Relation

Muss darstellbar sein:

* serverseitig gefilterte Liste;
* Target Scope;
* Candidate List;
* Assign und Unassign;
* getrennte Capabilities;
* target-aware Security;
* Operation Catalog;
* Contract-Handoff.

### Fixture B – Personnel Temporal Aggregate Graph

Muss darstellbar sein:

* Aggregate Root;
* Aggregate Member;
* Root Version;
* Plan Snapshot;
* append-only Relation;
* Ledger Entry;
* Projection Read;
* Temporal Read;
* Expected Version Set;
* gemischte Konsistenz;
* Aggregate-Graph-Transaktion;
* atomare Fachänderung plus Ledger.

### Fixture C – Contacts Lifecycle and Snapshot Token

Muss darstellbar sein:

* Root plus Version;
* Soft Delete;
* Restore;
* Hard Delete;
* Preview;
* Snapshot Token;
* erneute serverseitige Prüfung;
* pessimistische Konsistenz;
* Multi-Resource-Abhängigkeit;
* atomare Mutation.

### Fixture D – Generic Bulk Command

Muss darstellbar sein:

* alle Auswahlmodi;
* alle Atomicity-Modi;
* synchron und asynchron;
* Bulk Precheck;
* Bulk Capability;
* per-target Preconditions;
* Idempotency;
* Limits;
* Partial Outcomes;
* Effects.

### Fixture E – GWC Standard Page Binding

Muss darstellbar sein:

* Operation Keys;
* Entity List;
* Relation Grid;
* Candidate Assignment;
* Projection Read;
* History Presentation;
* Bulk Action;
* `refreshAfterSuccess`.

### Fixture F – GWC Workspace Binding

Muss darstellbar sein:

* Root Context;
* Area Resource Bindings;
* Temporal Context;
* Resource Keys;
* Backend Effects;
* spätere Reload-Graph-Zuordnung;
* Bulk-Operation innerhalb einer Area.

Die Fixture darf keine Workspace Runtime oder Canonical IR vortäuschen.

### Qualification-Statuswerte

```text
SUPPORTED
SUPPORTED_WITH_MAPPING
DEFERRED_TO_NEXT_SPRINT
BLOCKED
CONTRADICTORY
```

### Exit-Kriterium

Kein Finding besitzt `CONTRADICTORY`.

`BLOCKED` ist nur zulässig, wenn:

* die Blockade nicht durch einen Sprint-003-Vertrag verursacht wurde;
* ein expliziter Handoff an Sprint 004 vorliegt;
* das Zielbild die Fähigkeit weiterhin enthält.

---

## Phase 7 – GWC-Vertragsbindung und Generator-Kompatibilität

### Ziel

Die Backendverträge werden an bestehende GWC-Begriffe gebunden, ohne Standard Page und Workspace zu vermischen.

### Arbeitspakete

1. `operationKey`-Binding zur Application UI Spec präzisieren.
2. Backend `affectedResourceKeys` von UI-`refreshAfterSuccess` abgrenzen.
3. Bulk Actions als UI-fähige Vertragsfamilie beschreiben.
4. History- und Projection-Reads für Standard Pages beschreibbar machen.
5. Workspace-relevante Context- und Resource-Bindings vorbereiten.
6. bestehende Application-UI-Spec-Version nur additiv erweitern oder eine neue Version vorbereiten.
7. Generated Slice V1 unverändert lassen.
8. Erweiterung nur als neue Version oder Extension Family planen.

### Verbotene Änderungen

* Workspace durch Standard Page materialisieren;
* Backendprofil als UI Spec verwenden;
* Reload Graph im Backendvertrag speichern;
* vorhandene GWC-Begriffe umbenennen;
* bestehende Generated-Slice-V1-Fixtures brechen.

### Tests

* GWC-Namenskonsistenz;
* Application-UI-Spec-Schema;
* Operation-Key-Referenzen;
* unbekannte Operation Keys;
* unbekannte Resource Keys;
* Bulk Action ohne Bulk Contract;
* Workspace Binding ohne Context;
* Standard Page mit Workspace-only Semantik;
* deterministische Projektion.

### Exit-Kriterium

Der Folgesprint kann eine Workspace Canonical IR einführen, ohne Backend- oder Operationsbegriffe erneut ändern zu müssen.

---

## Phase 8 – Qualification, Evidence und Closure

### Ziel

Vollständige Regression, Driftprüfung und Übergabe an Sprint 004.

### Pflichtberichte

```text
IDM_COMPATIBILITY_REPORT.md
PERSONNEL_COMPATIBILITY_REPORT.md
CONTACTS_COMPATIBILITY_REPORT.md
GWC_CONTRACT_ALIGNMENT_REPORT.md
BULK_CONTRACT_QUALIFICATION_REPORT.md
CROSS_APP_NON_CONTRADICTION_REPORT.md
ANTI_DRIFT_REPORT.md
FOLLOW_UP_SPRINT_READINESS_REPORT.md
```

### Pflichtprüfungen

* alle Requirements bewertet;
* alle Capability-Reifegrade aktualisiert;
* alle Deferrals dokumentiert;
* alle neuen Regeln besitzen Tests;
* keine vorhandene ausreichende Struktur unnötig verändert;
* keine App-Fachlogik in Core;
* kein Workspace-/Standard-Page-Konflikt;
* keine Bulk-/Batch-Verwechslung;
* Contract-Bundle reproduzierbar;
* vollständige Maven- und Gate-Regression;
* Dokumentations- und Indexprüfung;
* Versionsauswirkungen entschieden.

### Exit-Kriterium

Sprintabschluss ist nur zulässig, wenn:

```text
CONTRADICTORY_FINDINGS=0
UNKNOWN_REQUIREMENTS=0
UNMAPPED_CAPABILITIES=0
UNTESTED_NORMATIVE_RULES=0
NONDETERMINISTIC_ARTIFACTS=0
```

---

# 7. Übergreifende Teststrategie

## 7.1 Mindestnachweis je Regel

Jede normative Regel benötigt:

```text
1 positiver Test
1 negativer Test
1 Contract- oder Schematest
1 Capability-Zuordnung
1 Evidence-Artefakt
```

Zusätzlich:

* Security-Regel: mindestens ein Boundary-Test;
* Concurrency-Regel: mindestens ein Konflikttest;
* Bulk-Regel: mindestens ein Partial- oder Rollback-Testfixture;
* Determinismusregel: mindestens zwei identische Wiederholungsläufe;
* Cross-App-Regel: mindestens zwei strukturell unterschiedliche Fixtures.

## 7.2 Testebenen

| Ebene            | Zweck                                        |
| ---------------- | -------------------------------------------- |
| Unit             | Value Objects, Enums, Grammatik, Invarianten |
| Schema           | Maschinenlesbare Vertragsstruktur            |
| Negative Fixture | Fail-closed-Verhalten                        |
| Tooling          | Validator, Catalog und Export                |
| Spring Context   | Registry- und Startup-Invarianten            |
| OpenAPI          | Extensions, Statuscodes, Bindings            |
| Controller       | HTTP-Vertrag                                 |
| Service          | Security, Capability und Mutation            |
| Repository       | Paging, Sortierung und Visibility            |
| Golden           | Catalogs, Manifest, Reports und IR           |
| Cross-App        | IDM, Personnel und Contacts                  |
| Regression       | Schutz bestehender Springmaster-Verträge     |

## 7.3 Bulk-Testmatrix

Die Vertragsfixtures müssen mindestens kombinieren:

| Dimension     | Werte                                      |
| ------------- | ------------------------------------------ |
| Selection     | explicit, query snapshot, token            |
| Atomicity     | all-or-nothing, per-target, per-chunk      |
| Execution     | sync, async                                |
| Authorization | all allowed, mixed, none                   |
| Preconditions | none, version, version set, snapshot, ETag |
| Outcomes      | success, partial, total conflict           |
| Idempotency   | new, repeated, payload mismatch            |
| Limits        | empty, one, max, exceeded                  |
| Duplicates    | reject, deduplicate                        |
| Order         | request order, canonical order             |

Nicht jede Kombination benötigt eine eigene Integrationstestklasse. Alle normativ unterschiedlichen Ergebnisse müssen jedoch mindestens durch Fixtures abgedeckt sein.

## 7.4 Concurrency-Vorbereitung

Sprint 003 testet:

* Vertrag und Bindung;
* Diagnose bei ungültiger Precondition;
* Conflict-Mapping;
* Cross-App-Repräsentierbarkeit;
* Locking-Details bleiben intern.

Sprint 004 testet später zusätzlich:

* echte Parallelität;
* MariaDB-Sperren;
* deterministische Lock Order;
* Timeout;
* Deadlock;
* Retry;
* vollständigen Rollback;
* Root-Version-Fortschreibung;
* atomare Fachänderung plus Ledger.

## 7.5 Regression

Mindestens:

```bash
mvn -q -Dtest=<gezielte neue Tests> test
mvn -q test
mvn -q -Pspringmaster-gates-report test
./bin/springmaster-gates.sh report --clean
./bin/springmaster-gates-selfcheck.sh
./bin/springmaster-gates-regression.sh
./bin/tooling-selfcheck.sh --no-export
git diff --check
```

Für Python und Shell:

```bash
python3 -m py_compile <tool.py>
bash -n <tool.sh>
```

Ein Full-Export erfolgt erst am qualifizierten Abschluss beziehungsweise Audit-Handoff.

---

# 8. Anti-Drift-Verfahren im Sprint

## 8.1 Eine Zielbildquelle

Das Architekturkonzept ist die einzige vollständige Zielbildquelle.

Der Sprintplan darf es nicht in gekürzter Form neu definieren.

## 8.2 Ein Reifegradregister

Der aktuelle Capability-Reifegrad wird ausschließlich im maschinenlesbaren Capability Catalog gepflegt.

Andere Dokumente referenzieren diesen Stand.

## 8.3 Verbindliche Patch-Metadaten

Jeder Änderungsschnitt nennt:

```text
requirementIds
capabilityIds
ruleIds
changedContractVersion
testPaths
evidencePaths
explicitDeferrals
```

## 8.4 Keine verdeckte Zielbildänderung

Folgende Änderungen benötigen Stop und ADR:

* neuer Primärbegriff;
* neue Capability;
* Entfernung einer Capability;
* Änderung der Verantwortungsgrenze;
* Änderung eines öffentlichen Contract-Feldes;
* Änderung eines Reifegradkriteriums;
* Zusammenlegung von Standard Page und Workspace;
* Änderung der Bulk-Atomicity-Semantik;
* neue globale Locking-Regel.

## 8.5 Anti-Drift-Gate

Das Gate prüft:

* alle Capability-IDs vorhanden;
* keine Capability ohne Zielreifegrad;
* alle Sprintanforderungen zugeordnet;
* alle normativen Regeln getestet;
* keine unbekannten Begriffe;
* keine Shadow Contracts;
* keine verschwundenen Deferrals;
* keine widersprüchlichen Current-State-Angaben;
* keine nicht versionierte Schemaänderung;
* keine `CANONICAL`-Promotion ohne Cross-App-Evidence.

## 8.6 Deferral-Schutz

Eine deferierte Fähigkeit bleibt im Catalog mit:

```text
currentMaturity
targetMaturity
blockingReason
plannedSprint
requiredEvidence
```

Ein Deferral darf nicht durch Löschen der Anforderung „gelöst“ werden.

---

# 9. Änderungsschnitte

Die tatsächlichen Patchnummern werden gegen die Live-Baseline vergeben.

| Schnitt   | Inhalt                                               |
| --------- | ---------------------------------------------------- |
| `S003-01` | Sprint-Harness, Baseline und Scopes                  |
| `S003-02` | Zielbildkonzept und Capability Catalog               |
| `S003-03` | Cross-App- und Naming-Matrix                         |
| `S003-04` | Operations- und Resource-Semantik-ADR                |
| `S003-05` | Preconditions-, Concurrency- und Bulk-ADR            |
| `S003-06` | normative Standards                                  |
| `S003-07` | Operations- und Resource-Schemas                     |
| `S003-08` | Precondition- und Bulk-Schemas                       |
| `S003-09` | positive und negative Fixture-Familien               |
| `S003-10` | Validator und Diagnosecodes                          |
| `S003-11` | Operation Catalog und Manifest                       |
| `S003-12` | deterministischer Export und Bundle                  |
| `S003-13` | OpenAPI-Runtime-Typen                                |
| `S003-14` | OpenAPI-Customizer und Startup-Gates                 |
| `S003-15` | Team-Membership-Read- und Relation-Slice             |
| `S003-16` | Candidate-, Command- und Capability-Slice            |
| `S003-17` | Cross-App-Fixtures IDM und Personnel                 |
| `S003-18` | Cross-App-Fixtures Contacts und Bulk                 |
| `S003-19` | GWC-Standard-Page- und Workspace-Bindings            |
| `S003-20` | Cross-App-Qualification und Non-Contradiction Report |
| `S003-21` | Full Regression, Versionierung und Closure           |

Ein Schnitt soll nicht gleichzeitig:

* Normen entscheiden;
* Schemas ändern;
* Runtime implementieren;
* Referenzslice erweitern;
* Cross-App-Promotion durchführen.

---

# 10. Definition of Ready

Der Sprint ist umsetzungsbereit, wenn:

* [ ] der aktuelle Springmaster-Export verifiziert ist;
* [ ] Zielbildkonzept und Capability-IDs akzeptiert sind;
* [ ] die Abgrenzung zu parallelen Sprints geklärt ist;
* [ ] alle bestehenden relevanten Standards inventarisiert sind;
* [ ] Cross-App Pattern Matrix vollständig ist;
* [ ] Naming Matrix vollständig ist;
* [ ] die Requirements-to-Capability-Matrix vorliegt;
* [ ] die Teststrategie für alle neuen Contract-Familien feststeht;
* [ ] kein Managed Project im Sprint mutiert werden muss;
* [ ] alle geplanten Schemafamilien einen Owner besitzen;
* [ ] die Bulk-Abgrenzung zu Composite Commands und Batch Jobs akzeptiert ist.

---

# 11. Definition of Done

Der Sprint ist abgeschlossen, wenn:

* [ ] das Zielbildkonzept aktiv und indexiert ist;
* [ ] der Capability Catalog schema-validiert ist;
* [ ] keine Capability des Gesamtziels fehlt;
* [ ] `operationKey` die einzige stabile fachliche Operationsidentität ist;
* [ ] `operationKind` und `operationRoles[]` getrennt sind;
* [ ] Resource Roles, History Models und Temporal Context definiert sind;
* [ ] Preconditions vollständig definiert sind;
* [ ] öffentliche Preconditions und interne Locking-Strategien getrennt sind;
* [ ] Transaction Scope und Consistency Strategy definiert sind;
* [ ] synchrone und asynchrone Bulk-Verträge vollständig sind;
* [ ] Bulk Selection, Atomicity, Idempotency, Limits und Outcomes vollständig sind;
* [ ] Bulk Capability die Zielautorisierung nicht ersetzt;
* [ ] Backend Effects von GWC Refresh und Workspace Reload Graph getrennt sind;
* [ ] alle Schemas positive und negative Fixtures besitzen;
* [ ] Validator und Diagnosecodes stabil sind;
* [ ] Operation Catalog und Manifest deterministisch erzeugt werden;
* [ ] das Contract-ZIP reproduzierbar ist;
* [ ] die OpenAPI-Runtime opt-in und fachneutral ist;
* [ ] vorhandene unprofilierte APIs unverändert bleiben;
* [ ] der Team-Membership-Referenzslice qualifiziert ist;
* [ ] IDM-Fixture validiert;
* [ ] Personnel-Fixture validiert;
* [ ] Contacts-Fixture validiert;
* [ ] Bulk-Fixture validiert;
* [ ] GWC Standard Page Binding validiert;
* [ ] GWC Workspace Binding ohne Runtime-Vortäuschung validiert;
* [ ] der Cross-App Non-Contradiction Report keinen Widerspruch enthält;
* [ ] alle neuen Gates korrekt `report-only` klassifiziert sind;
* [ ] bestehende Springmaster-Regressionen grün sind;
* [ ] keine App-Fachlogik in den Core übernommen wurde;
* [ ] keine unbelegte Canonicalization erfolgt;
* [ ] die Capability-Reifegrade aktualisiert sind;
* [ ] alle Deferrals einen Owner, geplanten Sprint und Evidence-Bedarf besitzen;
* [ ] Sprint 004 mit klaren Eingangsverträgen geplant werden kann.

---

# 12. Risiken und Gegenmaßnahmen

| Risiko                                      | Gegenmaßnahme                                               |
| ------------------------------------------- | ----------------------------------------------------------- |
| Zielbild wird durch Sprintscope verkleinert | Capability Catalog und Deferral-Schutz                      |
| zweiter konkurrierender API-Standard        | additive Profile, Querverweise auf bestehende Standards     |
| Bulk wird mit Batch Job vermischt           | normative Abgrenzung und negative Fixtures                  |
| Bulk-Partial-Success bleibt unklar          | explizite Atomicity und Outcome-Verträge                    |
| Concurrency wird global vereinheitlicht     | Use-Case-bezogene Klassifikation                            |
| Personnel-Modell passt nicht                | eigenes Temporal-Aggregate-Graph-Fixture                    |
| Contacts-Snapshot-Vertrag passt nicht       | eigenes Snapshot-Token-Fixture                              |
| IDM-Security wird verallgemeinert           | fachneutrale Metadaten und IDM-Mapping                      |
| Workspace wird als Detailseite behandelt    | eigene Capability- und Patternfamilie                       |
| Reload-Wahrheit wird dupliziert             | Backend Effects, GWC Refresh und Workspace Reload getrennt  |
| Schemas werden zu komplex                   | kleine versionierte Profile und klare Verantwortungsgrenzen |
| zu frühe Canonicalization                   | Reifegradmodell und Cross-App-Evidence                      |
| unkontrollierte Änderungen an Altverträgen  | Regression und KEEP-Klassifikation                          |
| Drift zwischen OpenAPI und Catalog          | automatisches Konsistenzgate                                |
| Drift zwischen Dokumenten                   | eine Zielbildquelle und ein Capability Catalog              |

---

# 13. Stopkriterien

Der aktuelle Schnitt beziehungsweise Sprint stoppt, wenn:

* eine bestehende akzeptierte ADR stillschweigend überschrieben werden müsste;
* ein neuer Primärbegriff ohne Zielbildänderung erforderlich wäre;
* eine App nur durch Änderung ihrer Fachlogik repräsentierbar wäre;
* ein globales Locking-Verfahren erzwungen werden müsste;
* Workspace und Standard Page nicht sauber getrennt werden können;
* Bulk-Atomicity nicht eindeutig beschreibbar ist;
* ein asynchroner Bulk Command keinen stabilen Statusvertrag besitzt;
* Capability-Projektion serverseitige Autorisierung ersetzen würde;
* bestehende Generated-Slice-V1-Verträge brechen;
* das Contract-Handoff nicht deterministisch erzeugt werden kann;
* der Cross-App-Report ein Finding `CONTRADICTORY` enthält;
* ein neues Gate im selben Schnitt unbegründet `strict` werden müsste;
* ein Managed Project zur Qualification mutiert werden müsste.

---

# 14. Versionswirkung

Voraussichtliche Auswirkungen:

* `PLATFORM_CORE_VERSION`: `minor`, falls allgemeine Runtime-Typen aufgenommen werden;
* `PLATFORM_TOOLING_VERSION`: `minor` für Validator, Catalog und Export;
* `PLATFORM_DEMO_VERSION`: `minor` für den Referenzslice;
* `PLATFORM_TEMPLATE_VERSION`: nur bei tatsächlicher versionierter Contract-Erweiterung;
* Foundation-Version erst bei qualifizierter gemeinsamer Promotion.

Die konkreten Versionswerte werden erst nach Abschluss der jeweiligen Änderungsschnitte entschieden.

---

# 15. Handoff an SPRINGMASTER-SPRINT-004

Vorgesehener Folgesprint:

```text
SPRINGMASTER-SPRINT-004
Complex Aggregate, Temporal History and Workspace Foundation
```

Sprint 004 erhält mindestens:

* akzeptierte Precondition-Verträge;
* Transaction-Scope- und Consistency-Klassifikation;
* Personnel-Aggregate-Graph-Fixture;
* Contacts-Snapshot-Token-Fixture;
* History- und Projection-Verträge;
* Workspace Context- und Resource-Bindings;
* Backend Effects;
* GWC-Verantwortungsgrenzen;
* vollständige negative Fixtures;
* Cross-App Non-Contradiction Report.

Sprint 004 soll darauf aufbauend referenzimplementieren:

1. komplexen Aggregate Graph;
2. gemischtes Expected-Version-/Pessimistic-Locking;
3. deterministische Lock Order;
4. Root Version und Snapshot;
5. append-only Relation und Ledger;
6. Projection und Temporal Read;
7. Snapshot-Token-Command;
8. Workspace Canonical IR;
9. Resource Store;
10. Reload Graph;
11. Mutation Coordinator;
12. Dirty-State-Registry;
13. echte Concurrency- und Failure-Mode-Tests.

---

# 16. Sprintabschlussstatus

Bei erfolgreichem Abschluss gilt:

```text
TARGET_ARCHITECTURE=PERSISTED
CAPABILITY_CATALOG=ACTIVE
ANTI_DRIFT_FOUNDATION=ACTIVE

OPERATION_IDENTITY=REFERENCE_IMPLEMENTED
RELATION_CANDIDATE_CAPABILITY=REFERENCE_IMPLEMENTED
OPERATION_CATALOG=REFERENCE_IMPLEMENTED
CONTRACT_HANDOFF=REFERENCE_IMPLEMENTED

PRECONDITIONS=CONTRACTED
CONCURRENCY_CLASSIFICATION=CONTRACTED
COMPLEX_TRANSACTIONS=CONTRACTED
HISTORY_AND_PROJECTIONS=CONTRACTED
SYNCHRONOUS_BULK=CONTRACTED
ASYNCHRONOUS_BULK=CONTRACTED
GWC_BULK_BINDING=CONTRACTED

WORKSPACE_RUNTIME=DEFINED_NOT_IMPLEMENTED
MANAGED_PROJECT_MIGRATION=DEFINED_NOT_IMPLEMENTED

CROSS_APP_CONTRADICTIONS=0
UNTRACKED_TARGET_CAPABILITIES=0
```

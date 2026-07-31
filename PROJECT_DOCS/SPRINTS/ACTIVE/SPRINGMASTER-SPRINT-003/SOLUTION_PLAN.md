---
documentId: SPRINGMASTER-SPRINT-003-PLAN
title: Cross-App Backend Contract Foundation and GWC Readiness – Solution Plan
documentType: plan
status: review
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
temporary: true
sprintId: SPRINGMASTER-SPRINT-003
---

# Cross-App Backend Contract Foundation and GWC Readiness – Solution Plan

## Lösungsoptionen und Auswahl

### Gewählte Lösung

SPRINGMASTER-SPRINT-003 realisiert eine contract-first Cross-App-Grundlage. Der Sprint hebt nur ausreichend verstandene Fähigkeiten bis zur Referenzimplementierung an und hält komplexe Runtime-Fähigkeiten bewusst auf `CONTRACTED` oder `DEFINED`.

Die gewählte Lösung besteht aus:

1. dauerhafter Zielbild- und Capability-Bindung;
2. ADRs und additiven Standards;
3. versionierten maschinenlesbaren Profilen;
4. positiven und negativen Cross-App-Fixtures;
5. Validator, Operation Catalog und reproduzierbarem Contract-Handoff;
6. minimaler opt-in OpenAPI-Runtime;
7. einfachem Relation-/Candidate-Referenzslice;
8. read-only Qualification gegen IDM, Personnel, Contacts und GWC;
9. qualifiziertem Handoff an Folgesprints.

### Verworfene Optionen

#### Vollständige Runtime in einem Sprint

Verworfen, weil komplexe Aggregate Graphs, gemischte Concurrency, Bulk-Orchestrierung und Workspace Runtime unterschiedliche Oracles und Failure Modes besitzen. Eine gemeinsame Umsetzung würde Reviewbarkeit, Cross-App-Evidence und deterministische Qualification schwächen.

#### Neuer paralleler API-Standard

Verworfen, weil Springmaster bereits ausreichende CRUD-, Query-, Command-, Relationship-, Precheck-, Error- und Security-Verträge besitzt. Das neue Profil ergänzt nur fehlende maschinenlesbare Semantik.

#### App-spezifische Übernahme aus IDM, Personnel oder Contacts

Verworfen. Bewährte Patterns werden fachneutral abstrahiert; Fachlogik, Entity-Namen, Tabellenmodelle und Sperrreihenfolgen bleiben Anwendungseigentum.

#### Automatischer Managed-Project-Umbau

Verworfen. Sprint 003 arbeitet gegenüber IDM, Personnel, Contacts und GWC ausschließlich read-only. Adoption und Migration erfolgen später kontrolliert und sliceweise.

### Aktivierungsvoraussetzung

Sprint 003 darf erst `active` werden, wenn genau eine der folgenden Bedingungen erfüllt ist:

- SPRINGMASTER-SPRINT-002 ist qualifiziert abgeschlossen und archiviert; oder
- ein akzeptiertes Sprint-002-Amendment definiert disjunkte Dateiscopes, Contract-Ownership und Evidence.

Bis dahin bleibt dieses Dokument `status: review`.

## Architektur- und Contract-Auswirkungen

### Zielbildbindung

Kanonisches Zielbild:

```text
PROJECT_DOCS/CONCEPT/CROSS_APP_BACKEND_GWC_TARGET_ARCHITECTURE_CONCEPT.md
```

Kanonische übergeordnete Zielquelle:

```text
PROJECT_DOCS/GOVERNANCE/SPRINGMASTER_PROJECT_GOALS.md
```

Der Sprint darf keine Capability entfernen, umbenennen oder durch einen einfacheren Spezialfall ersetzen.

### Geplante Capability-Reifegrade

Die Ist-Reifegrade werden zu Sprintbeginn gegen die Live-Baseline verifiziert.

| Capability-ID | Ziel nach Sprint 003 |
|---|---|
| `CAP-API-001` | `REFERENCE_IMPLEMENTED` |
| `CAP-API-002` | bestehende Reife erhalten und regressionssichern |
| `CAP-API-003` | `REFERENCE_IMPLEMENTED` |
| `CAP-API-004` | `REFERENCE_IMPLEMENTED` |
| `CAP-CONC-001` | `CONTRACTED` |
| `CAP-CONC-002` | `CONTRACTED` |
| `CAP-CONC-003` | `CONTRACTED` |
| `CAP-HIST-001` | `CONTRACTED` |
| `CAP-HIST-002` | `CONTRACTED` |
| `CAP-PROJ-001` | `CONTRACTED` |
| `CAP-BULK-001` | `CONTRACTED` |
| `CAP-BULK-002` | `CONTRACTED` |
| `CAP-BULK-003` | `CONTRACTED` |
| `CAP-JOB-001` | `DEFINED` |
| `CAP-EXPORT-001` | `DEFINED` |
| `CAP-QUERY-003` | `DEFINED` |
| `CAP-AGG-001` | `DEFINED` |
| `CAP-GWC-001` | `CONTRACTED` |
| `CAP-GWC-002` | bestehende Reife erhalten |
| `CAP-GWC-003` | `CONTRACTED` |
| `CAP-WS-001` | `DEFINED`, Kompatibilität nachgewiesen |
| `CAP-WS-002` | `DEFINED`, Schnittstellen vorbereitet |
| `CAP-WS-003` | `DEFINED`, Schnittstellen vorbereitet |
| `CAP-TOOL-001` | `REFERENCE_IMPLEMENTED` |
| `CAP-TOOL-002` | `REFERENCE_IMPLEMENTED` |
| `CAP-QUAL-001` | `REFERENCE_IMPLEMENTED` |
| `CAP-MIG-001` | `DEFINED`, nicht umgesetzt |

### Sprintanforderungen

| Requirement-ID | Anforderung |
|---|---|
| `S003-REQ-001` | Zielbild und Sprintscope sind kanonisch, indexiert und über Capability-IDs verbunden. |
| `S003-REQ-002` | Ein JSON-basierter Cross-App Backend and GWC Capability Catalog bildet Ziel-, Ist- und geplante Reifegrade ab. |
| `S003-REQ-003` | `operationKey` ist die einzige stabile fachliche Operationsidentität; `operationId` bleibt technisch. |
| `S003-REQ-004` | `operationKind` und `operationRoles[]` sind getrennt und mehrfach kombinierbar. |
| `S003-REQ-005` | Bestehende Paging-, Filter-, Sortier-, Command-, Relationship- und Error-Verträge bleiben kompatibel. |
| `S003-REQ-006` | Relation-, Candidate-, Security- und Capability-Semantik ist fachneutral und maschinenlesbar. |
| `S003-REQ-007` | Resource Roles, History Models, Temporal Context und Projections können Personnel- und Contacts-Strukturen darstellen. |
| `S003-REQ-008` | Preconditions unterstützen `NONE`, `EXPECTED_VERSION`, `EXPECTED_VERSION_SET`, `SNAPSHOT_TOKEN` und `ETAG`. |
| `S003-REQ-009` | Die bestehende Optimistic-Locking-Baseline bleibt erhalten; pessimistische und gemischte Verfahren sind additive Use-Case-Strategien. |
| `S003-REQ-010` | Transaction Scope unterstützt Single Aggregate, Aggregate Graph und Multi Aggregate. |
| `S003-REQ-011` | Synchroner und asynchroner Backend Bulk Command sind vollständig normativ beschrieben. |
| `S003-REQ-012` | Bulk Selection, Atomicity, Autorisierung, Non-Disclosure, Preconditions, Idempotenz, Limits, Outcomes und Result Delivery sind maschinenlesbar. |
| `S003-REQ-013` | Backend Bulk Command, GWC Batch Runtime, Composite Command und Background Job sind eindeutig getrennt und gemappt. |
| `S003-REQ-014` | Export, Aggregation, Cursor/Delta und Background Jobs bleiben als definierte Zielkapazitäten sichtbar. |
| `S003-REQ-015` | Backend Effects und GWC Refresh-/Workspace-Reload-Verantwortung bleiben getrennt. |
| `S003-REQ-016` | Workspace bleibt eigene GWC-Patternfamilie und wird nicht als Standard Page materialisiert. |
| `S003-REQ-017` | Application UI Spec v1.1 bleibt kompatibel; `operationKey` wird versioniert in vNext eingeführt. |
| `S003-REQ-018` | OpenAPI, Operation Catalog, Resource Semantics, UI Spec und Canonical IR besitzen eine eindeutige Authority Matrix. |
| `S003-REQ-019` | Ein deterministischer Operation Catalog und ein reproduzierbares Contract-Bundle werden erzeugt. |
| `S003-REQ-020` | Eine minimale allgemeine OpenAPI-Runtime bleibt opt-in und verändert keine unprofilierte API. |
| `S003-REQ-021` | Ein Team-Membership-Referenzslice demonstriert die stabilen Relation-, Candidate- und Capability-Patterns. |
| `S003-REQ-022` | IDM, Personnel, Contacts, Generic Bulk, GWC Standard Page und GWC Workspace werden read-only durch Fixtures qualifiziert. |
| `S003-REQ-023` | Keine allgemeine Regel erzwingt Änderungen an Fachlogik, Entity-Struktur, Tabellenmodell oder fachlicher Sperrreihenfolge. |
| `S003-REQ-024` | Jede normative Regel besitzt positive und negative automatisierte Evidence. |
| `S003-REQ-025` | Dokument-, Contract- und Sprintpfade entsprechen der bestehenden Springmaster-Governance. |
| `S003-REQ-026` | Ein Cross-App Non-Contradiction Report enthält keine Findings mit Status `CONTRADICTORY`. |
| `S003-REQ-027` | Der Capability Catalog schützt Deferrals gegen stilles Entfernen. |
| `S003-REQ-028` | Der Folgesprint erhält vollständige Eingangsverträge für komplexe Aggregate, Concurrency und Workspaces. |
| `S003-REQ-029` | Agentenbasierte Umsetzung erfolgt nur in kleinen, immutable, scopebegrenzten Tasks mit unabhängigen Oracles und menschlicher Integration. |
| `S003-REQ-030` | Normative Entscheidungen, Oracle-Freigabe, Gate-Promotion, Integration und Versionierungsentscheidung bleiben menschlich kontrolliert. |
| `S003-REQ-031` | Alle neuen Gates beginnen `report-only`; eine Strict-Promotion erfolgt separat. |
| `S003-REQ-032` | Generated Slice V1 und bestehende GWC-/OpenAPI-Verträge bleiben rückwärtskompatibel. |

### Geplante Contract-Familien

Vorgesehen sind versionierte JSON-Schemas und Catalogs, beispielsweise:

```text
contracts/architecture/cross-app-backend-gwc-target-capabilities.v1.json
contracts/api/schemas/backend-operation-profile.schema.v1.json
contracts/api/schemas/backend-resource-semantics.schema.v1.json
contracts/api/schemas/backend-precondition-profile.schema.v1.json
contracts/api/schemas/backend-bulk-operation-profile.schema.v1.json
contracts/api/schemas/backend-implementation-evidence.schema.v1.json
contracts/api/schemas/operation-catalog.schema.v1.json
contracts/api/schemas/contract-manifest.schema.v1.json
```

Die endgültige Aufteilung wird in der Contract-ADR entschieden. Neue technische Artefakte werden nicht unter `PROJECT_DOCS/**` abgelegt.

### Normative Dokumente

Voraussichtlich erforderlich:

```text
PROJECT_DOCS/ADR/ADR-0016-backend-operation-semantics-and-gwc-profile.md
PROJECT_DOCS/ADR/ADR-0017-mutation-precondition-concurrency-and-bulk-boundary.md
PROJECT_DOCS/STANDARDS/API/GWC_BACKEND_API_PROFILE_STANDARD.md
PROJECT_DOCS/STANDARDS/API/BULK_OPERATION_CONTRACT_STANDARD.md
PROJECT_DOCS/STANDARDS/API/MUTATION_PRECONDITION_STANDARD.md
PROJECT_DOCS/STANDARDS/ARCHITECTURE/RESOURCE_HISTORY_AND_PROJECTION_STANDARD.md
PROJECT_DOCS/STANDARDS/ARCHITECTURE/TRANSACTION_AND_CONSISTENCY_CLASSIFICATION_STANDARD.md
```

Die ADR-Nummern werden erst gegen die Live-Baseline vergeben.

## Slices und Reihenfolge

### Slice 0: Aktivierung, Baseline und Anti-Drift

- Sprint-2-Abschluss oder akzeptiertes Amendment verifizieren;
- Live-Commit, Versionen, Export und Gates erfassen;
- Zielbild, Sprint Brief, Solution Plan, Status und Completion Skeleton qualifizieren;
- Capability Catalog initialisieren;
- Cross-App Pattern Compatibility Matrix und Naming Matrix erstellen;
- Requirements-to-Capability- und Requirements-to-Test-Matrix anlegen;
- alle relevanten Bestandsverträge als `KEEP`, `CLARIFY`, `GENERALIZE`, `EXTEND` oder `DEFER` klassifizieren.

**Exit:** keine Code- oder Schemaänderung vor akzeptierter Baseline, Terminologie und Dateiscope-Abgrenzung.

### Slice 1: ADRs und Standards

- Operationsidentität, Operation Kind und Roles entscheiden;
- Contract-Source-Authority festlegen;
- Resource Roles, History, Temporal und Projection Semantik entscheiden;
- Precondition-, Transaction-Scope- und Consistency-Klassifikation entscheiden;
- Bulk-, Background-Job- und GWC-Batch-Abgrenzung entscheiden;
- Backend Effects gegen GWC Refresh und Workspace Reload abgrenzen;
- Application UI Spec v1.1 zu vNext migrierbar definieren.

**Exit:** jeder schema- oder runtimewirksame Begriff besitzt genau eine akzeptierte Definition.

### Slice 2: Maschinenlesbare Schemas und Oracles

- JSON-Schemas implementieren;
- Capability Catalog Contract implementieren;
- positive Fixtures für einfache API, History, Projection, Preconditions, Bulk und GWC-Bindings erstellen;
- negative Fixtures vor dem Validator implementieren;
- stabile Diagnosecodes definieren.

Pflicht-Negativfälle umfassen mindestens:

- doppelte Operationsidentitäten;
- unbekannte Kind-/Role-Werte;
- Candidate ohne Target Context;
- Temporal Read ohne Kontext;
- Projection ohne Response Schema;
- Ledger oder append-only Ressource mit unzulässiger Standardmutation;
- Snapshot Token ohne Producer;
- UI-Reload-Graph im Backendprofil;
- `WORKSPACE` als Backendoperation;
- Bulk ohne Atomicity, Limits oder Outcome-Semantik;
- asynchrones Bulk ohne Status-/Ergebnisvertrag;
- nicht eingefrorene irreversible Query-Auswahl;
- Non-Disclosure-Verstoß;
- v1.1-Spec wird brechend auf `operationKey` umgestellt;
- pessimistische Strategie entfernt den erforderlichen Versionstoken.

**Exit:** alle Pflicht-Negativfixtures liegen vor und scheitern deterministisch.

### Slice 3: Validator, Operation Catalog und Handoff

Ein fachneutraler CLI-Vertrag wird bevorzugt als ein Tool mit Subcommands umgesetzt:

```text
bin/backend-contract.py validate
bin/backend-contract.py catalog
bin/backend-contract.py verify
bin/backend-contract.py export
```

Pflichtfunktionen:

- Schema-, OpenAPI- und Profilvalidierung;
- Operations- und Capability-Eindeutigkeit;
- Method-/Path-/Operation-Bindung;
- Security-, Precondition- und Bulk-Prüfung;
- deterministischer Catalog;
- Manifest, Provenance und Hashes;
- reproduzierbares ZIP;
- Driftprüfung;
- fail-closed Diagnose.

**Exit:** identische Inputs erzeugen byteidentische Catalogs, Manifeste, Hashdateien und ZIPs.

### Slice 4: Minimale OpenAPI-Runtime

Fachneutrale Typen und Registry unterstützen ausschließlich stabile Profilsemantik:

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

Die Typzahl wird minimiert. Die Runtime darf keine Locking-Orchestrierung, History-Persistenz, Bulk-Ausführung oder Workspace-Steuerung implementieren.

**Exit:** vollständige Registry startet; unvollständige profilierte Operationen scheitern fail-closed; unprofilierte Bestandsendpunkte bleiben unverändert.

### Slice 5: Team-Membership-Referenzslice

Der einfache Referenzslice demonstriert:

- Listen-, Detail-, Relation-, Candidate- und Overview-Reads;
- getrennte Read-, Assign- und Unassign-Capabilities;
- target-aware Security und Visibility;
- erneute Mutation Authorization;
- stabile Row Identity und Sortierung;
- Operation Keys und Effects;
- bestehendes Fehler- und Command-Verhalten.

Er demonstriert ausdrücklich nicht Workspace Runtime, komplexe Historie, Multi-Aggregate-Locking oder Bulk Runtime.

**Exit:** der Slice ist als `candidate-reference-slice` qualifiziert und erzeugt keine unbelegte Canonicalization.

### Slice 6: Cross-App-Fixtures

- **IDM Scoped Relation:** servergefilterte Liste, Candidate, Assign/Unassign, target-aware Capabilities;
- **Personnel Temporal Aggregate Graph:** Root, Member, Root Version, Snapshot, append-only Relation, Ledger, Projection, Temporal Read, Expected Version Set, gemischte Konsistenz;
- **Contacts Lifecycle and Snapshot Token:** Soft Delete, Restore, Hard Delete, Preview, Snapshot Token, erneute Prüfung, atomare Mutation;
- **Generic Bulk Command:** alle Selection-, Atomicity- und Execution-Modi, Preconditions, Idempotenz, Non-Disclosure, Result Delivery;
- **GWC Standard Page Binding:** Operation Keys, Relation, History, Projection, Bulk Action und `refreshAfterSuccess`;
- **GWC Workspace Binding:** Root Context, Areas, Resource Keys, Temporal Context, Effects und spätere Reload-Graph-Zuordnung ohne Runtime-Vortäuschung.

Qualification-Statuswerte:

```text
SUPPORTED
SUPPORTED_WITH_MAPPING
DEFERRED_TO_NEXT_SPRINT
BLOCKED
CONTRADICTORY
```

**Exit:** kein Finding hat Status `CONTRADICTORY`.

### Slice 7: GWC- und Generator-Kompatibilität

- v1.1-Kompatibilitätsfixture;
- vNext-`operationKey`-Migration;
- Mappingtabellen zwischen Backend- und GWC-Semantik;
- GWC Batch Runtime zu Backend Bulk Mapping;
- Standard-Page- und Workspace-Abgrenzung;
- Generated Slice V1 Regression;
- neue Generatorfähigkeit nur als versionierte Extension oder Folgevertrag vorbereiten.

**Exit:** ein Folgesprint kann Workspace Canonical IR einführen, ohne Operations- oder Backendbegriffe erneut zu ändern.

### Slice 8: Qualification und Closure

- vollständige Regression;
- Cross-App Non-Contradiction Report;
- Anti-Drift Report;
- Compatibility Reports;
- Capability-Reifegrade aktualisieren;
- Deferrals mit Owner, geplantem Sprint und Evidence-Bedarf festhalten;
- Versionsauswirkungen bewerten;
- qualifizierten Handoff an Sprint 004 erstellen.

**Exit:** `CONTRADICTORY_FINDINGS=0`, `UNKNOWN_REQUIREMENTS=0`, `UNMAPPED_CAPABILITIES=0`, `UNTESTED_NORMATIVE_RULES=0`, `NONDETERMINISTIC_ARTIFACTS=0`.

## Teststrategie und Zwischenverifikationen

### Grundregel

Jede normative Regel benötigt mindestens:

```text
1 positiven Test
1 negativen Test
1 Schema- oder Contract-Test
1 Capability-Zuordnung
1 Evidence-Artefakt
```

Zusätzlich:

- Security-Regel: Boundary-Test;
- Concurrency-Regel: Konflikt- oder Repräsentierbarkeitstest;
- Bulk-Regel: Partial-, Rollback- oder Async-Lifecycle-Test;
- Determinismusregel: wiederholte byteidentische Läufe;
- Cross-App-Regel: mindestens zwei strukturell unterschiedliche Fixtures.

### Testebenen

| Ebene | Zweck |
|---|---|
| Unit | Value Objects, Enums, Grammatik, Invarianten |
| Schema | Maschinenlesbare Vertragsstruktur |
| Negative Fixture | Fail-closed-Verhalten |
| Tooling | Validator, Catalog und Export |
| Spring Context | Registry- und Startup-Invarianten |
| OpenAPI | Extensions, Statuscodes und Bindings |
| Controller | HTTP-Vertrag |
| Service | Security, Capability und Mutation |
| Repository | Paging, stabile Sortierung und Visibility |
| Golden | Catalogs, Manifest, Reports und IR |
| Cross-App | IDM, Personnel, Contacts und GWC |
| Regression | Schutz bestehender Springmaster-Verträge |

### Bulk-Testmatrix

Mindestens abzudecken:

| Dimension | Werte |
|---|---|
| Selection | explicit, query snapshot, selection token |
| Atomicity | all-or-nothing, per-target, per-chunk |
| Execution | synchronous, asynchronous |
| Authorization | all allowed, mixed, none |
| Preconditions | none, version, version set, snapshot, ETag |
| Outcomes | success, partial, total conflict, non-disclosed |
| Idempotency | new, repeated, payload mismatch |
| Limits | empty, one, max, exceeded |
| Result Delivery | inline, paged, artifact |
| Lifecycle | accepted, running, completed, failed, expired |

### Referenzslice-Tests

- leere, erste, mittlere und letzte Seite;
- maximale und ungültige Seitengröße;
- erlaubte und abgelehnte Sortierung;
- stabiler Tie-Breaker;
- identische List-/Count-Visibility;
- sichtbarer, unbekannter und nicht sichtbarer Detailresolver;
- Candidate sichtbar, auswählbar, bereits zugeordnet oder außerhalb des Scope;
- Statusänderung zwischen Candidate Read und Mutation;
- Assign, Duplicate Assign, Unassign, Konflikt und fehlende Permission;
- getrennte Capability-Personas;
- `401`, `403`, nicht offenbarendes `404`, `409` und nur bei realem Ausfall `503`.

### Determinismus

Bei identischem Input byteidentisch:

- Capability Catalog;
- Operation Catalog;
- Contract Manifest;
- Compatibility Reports;
- Qualification Reports;
- ZIP und SHA-256-Sidecars.

Variiert werden Locale, Zeitzone, Dateisystemreihenfolge, temporäres Arbeitsverzeichnis, wiederholte Ausführung und zulässige Zeilenendennormalisierung.

### Agentenbasierte Umsetzung

Codex-Aufgaben werden klein, immutable und baselinegebunden geschnitten. Ein Task darf nicht gleichzeitig normative Regel, Oracle, Runtime und Golden Output eigenständig verändern. Tests dürfen nur bei expliziter Capability geändert werden. Integration, ADR-Akzeptanz, Oracle-Freigabe und Gate-Promotion bleiben menschliche Entscheidungen.

## Messkriterien

Der Sprint ist messbar erfolgreich, wenn:

- alle 32 Anforderungen bewertet und traceable sind;
- alle Zielbild-Capabilities im Catalog erhalten bleiben;
- alle `CONTRACTED`-Fähigkeiten akzeptierte Standards und positive/negative Fixtures besitzen;
- alle `REFERENCE_IMPLEMENTED`-Fähigkeiten ausführbare Evidence besitzen;
- der Team-Membership-Slice seine Acceptance vollständig erfüllt;
- IDM-, Personnel-, Contacts-, Bulk- und GWC-Fixtures validieren;
- kein Cross-App-Finding `CONTRADICTORY` ist;
- alle Contract-Artefakte reproduzierbar sind;
- bestehende CRUD-, Query-, Error-, Command-, Relationship-, Generated-Slice-V1- und GWC-v1.1-Regressionen grün bleiben;
- keine app-spezifische Fachlogik im Core entsteht;
- alle neuen Gates `report-only` bleiben;
- jeder Deferral einen Owner, geplanten Sprint und Evidence-Bedarf besitzt.

Für agentenbasierte Tasks werden zusätzlich Zeit bis reviewfähigem Diff, First-Pass-Qualification, Reviewkorrekturen und manuelle Transfer-Schritte erfasst. Die Messung dient der Prozessverbesserung, nicht der automatischen Promotion.

## Migration und Rollback

### Repositoryänderungen

Jeder Änderungsschnitt ist baselinegebunden, klein und separat qualifizierbar. Fehlgeschlagene Dry-runs oder Agentläufe verändern Main nicht. Integration erfolgt nur nach Review und explizitem Accept.

### Contract-Versionierung

- bestehende V1-Verträge werden nicht stillschweigend erweitert;
- additive Erweiterungen erhalten eine versionierte Extension oder neue Contract-Version;
- Application UI Spec v1.1 bleibt lauffähig;
- `operationKey` wird versioniert in vNext eingeführt;
- eine Änderung öffentlicher Felder benötigt Migration oder Deprecation.

### Managed Projects

IDM, Personnel, Contacts und GWC werden nicht mutiert. Fixtures und Compatibility Reports sind read-only. Eine spätere Migration kann vollständig gestoppt werden, ohne die fachliche Baseline der Apps zu verändern.

### Rollback

- Contract- und Tooling-Slices werden separat zurücknehmbar gehalten;
- generierte Catalogs und Bundles sind aus unveränderten Inputs reproduzierbar;
- keine Datenmigration findet in diesem Sprint statt;
- keine Strict-Promotion ist Bestandteil desselben Implementierungsschnitts.

## Tool- und Gate-Einsatz

Mindestens:

```bash
python3 bin/documentation-gate.py --root . --check-all
python3 bin/sprint-gate.py --root . --mode all --check
./bin/project-directory-gate.sh --check
mvn -q -Dtest=<gezielte Tests> test
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

Für Contract-Handoff:

- Schema-Validation;
- OpenAPI-/Catalog-Konsistenz;
- SHA-256-Prüfung;
- reproduzierbares ZIP;
- unerwartete Datei blockiert;
- identischer Zweitlauf.

Neue Gates beginnen `report-only`. Strict-Promotion erfolgt nur in einem separaten, evidence-basierten Schnitt.

## Dokumentations- und Registerauswirkungen

### Dauerhafte Dokumentation

```text
PROJECT_DOCS/CONCEPT/CROSS_APP_BACKEND_GWC_TARGET_ARCHITECTURE_CONCEPT.md
PROJECT_DOCS/ADR/<vergebene ADRs>
PROJECT_DOCS/STANDARDS/API/GWC_BACKEND_API_PROFILE_STANDARD.md
PROJECT_DOCS/STANDARDS/API/BULK_OPERATION_CONTRACT_STANDARD.md
PROJECT_DOCS/STANDARDS/API/MUTATION_PRECONDITION_STANDARD.md
PROJECT_DOCS/STANDARDS/ARCHITECTURE/RESOURCE_HISTORY_AND_PROJECTION_STANDARD.md
PROJECT_DOCS/STANDARDS/ARCHITECTURE/TRANSACTION_AND_CONSISTENCY_CLASSIFICATION_STANDARD.md
```

### Sprintdokumente

```text
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-003/SPRINT_BRIEF.md
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-003/SOLUTION_PLAN.md
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-003/STATUS.md
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-003/COMPLETION_REPORT.md
```

### Maschinenlesbare Register und Contracts

```text
contracts/architecture/cross-app-backend-gwc-target-capabilities.v1.json
contracts/api/schemas/**
contracts/api/fixtures/**
```

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

Arbeitsberichte liegen während des Sprints unter dem zulässigen `WORK/`-Teilbaum und werden vor Closure promoviert, aggregiert oder verworfen. `PROJECT_DOCS/index.md` wird für alle dauerhaften oder aktiven Dokumente aktualisiert.

## Versionswirkung

Voraussichtliche Auswirkungen:

- `PLATFORM_CORE_VERSION`: `minor`, falls allgemeine Runtime-Typen aufgenommen werden;
- `PLATFORM_TOOLING_VERSION`: `minor` für Validator, Catalog und Export;
- `PLATFORM_DEMO_VERSION`: `minor` für den Referenzslice;
- `PLATFORM_TEMPLATE_VERSION`: nur bei tatsächlicher versionierter Generated-Slice- oder Application-UI-Spec-Erweiterung;
- Foundation-Version erst bei qualifizierter gemeinsamer Promotion.

Die konkreten Werte werden nach den jeweiligen qualifizierten Slices entschieden. Ein Schemaentwurf ohne aktivierte Runtimewirkung rechtfertigt nicht automatisch eine Plattformversionserhöhung.

## Patch- oder Commitsequenz

Die tatsächlichen Patchnummern werden gegen die Live-Baseline vergeben. Vorgesehene fachliche Schnitte:

| Schnitt | Inhalt |
|---|---|
| `S003-01` | Sprint-Harness, Baseline, Zielbild und Scopes |
| `S003-02` | Capability Catalog, Cross-App- und Naming-Matrix |
| `S003-03` | Operations-, Authority- und GWC-Binding-ADR |
| `S003-04` | Preconditions-, Concurrency-, Bulk- und Job-ADR |
| `S003-05` | normative Standards |
| `S003-06` | Operation- und Resource-Schemas |
| `S003-07` | Precondition-, Bulk- und Manifest-Schemas |
| `S003-08` | positive und negative Fixture-Familien |
| `S003-09` | Validator und Diagnosecodes |
| `S003-10` | Operation Catalog, Manifest und Export |
| `S003-11` | OpenAPI-Runtime-Typen und Registry |
| `S003-12` | OpenAPI-Customizer und Startup-Gates |
| `S003-13` | Team-Membership-Read- und Relation-Slice |
| `S003-14` | Candidate-, Command- und Capability-Slice |
| `S003-15` | IDM- und Personnel-Fixtures |
| `S003-16` | Contacts- und Bulk-Fixtures |
| `S003-17` | GWC v1.1/vNext-, Standard-Page- und Workspace-Bindings |
| `S003-18` | Cross-App-Qualification und Non-Contradiction Report |
| `S003-19` | Full Regression, Versionsbewertung und Closure |

Ein Schnitt soll nicht gleichzeitig Normen entscheiden, Schemas ändern, Runtime implementieren, Oracles verändern und Promotion durchführen.

## Unsicherheiten und Entscheidungszeitpunkte

### Vor Sprintaktivierung

- Status und Closure von Sprint 002;
- tatsächliche Live-Baseline und aktuelle Versionen;
- zulässige parallele Dateiscopes;
- Codex Write Readiness für Implementierungstasks.

### Vor Schemaimplementierung

- endgültige ADR-Aufteilung;
- ein gemeinsames Profil versus mehrere klar getrennte Schemas;
- genaue Ownership nicht in OpenAPI ausdrückbarer Resource Semantics;
- v1.1-zu-vNext-Migrationsform.

### Vor Runtimeimplementierung

- minimale Typzahl;
- Registry versus Annotation als Authoringmechanismus;
- Startup-Fail-closed-Grenze;
- Extension-Namen und OpenAPI-Darstellung.

### Vor Bulk- oder Job-Referenzruntime

Nicht Bestandteil dieses Sprints. Vor einem Folgesprint sind zu entscheiden:

- synchrone versus asynchrone Referenz;
- persistenter Execution Store;
- Result Retention;
- Cancellation;
- Retry- und Deadletter-Semantik;
- GWC Batch Runtime Integration.

### Vor Workspace-Runtime

Nicht Bestandteil dieses Sprints. Erforderlich sind Workspace Canonical IR, Resource Store, Reload Graph, Mutation Coordinator, Dirty State und mindestens ein zweiter echter Cross-App-Consumer.

### Stopkriterien

Der aktuelle Schnitt stoppt, wenn:

- eine akzeptierte ADR stillschweigend überschrieben werden müsste;
- ein neuer Primärbegriff ohne Zielbildänderung erforderlich wäre;
- eine App nur durch Änderung ihrer Fachlogik repräsentierbar wäre;
- die Optimistic-Locking-Baseline unbegründet aufgehoben würde;
- Workspace und Standard Page nicht sauber getrennt werden können;
- Bulk Atomicity, Autorisierung oder Non-Disclosure unklar bleibt;
- Application UI Spec v1.1 brechen würde;
- Generated Slice V1 brechen würde;
- Contract-Handoff nicht deterministisch ist;
- ein Cross-App-Finding `CONTRADICTORY` ist;
- ein Gate im selben Schnitt unbegründet `strict` werden müsste;
- ein Managed Project zur Qualification mutiert werden müsste.

## Lifecycle

1. `review`: Dieses Dokument ist inhaltlich vollständig, aber Sprint 003 noch nicht aktiviert.
2. `active`: erst nach erfüllter Aktivierungsvoraussetzung, vollständigem Sprint-Harness und bestandenen Documentation-/Sprint-Gates.
3. `completed`: nach vollständiger Qualification und akzeptiertem Completion Report.
4. Vor Archivierung wird der Solution Plan gemäß Sprint Governance aggregiert, promoviert, begründet archiviert oder verworfen; er ist standardmäßig kein Archivartefakt.

Geplanter Folgesprint:

```text
SPRINGMASTER-SPRINT-004
Complex Aggregate, Temporal History and Workspace Foundation
```

Der Handoff umfasst akzeptierte Precondition-, Concurrency-, History-, Projection- und Workspace-Bindings sowie Personnel-, Contacts- und GWC-Fixtures. Sprint 004 soll daraus komplexe Aggregate Graphs, gemischte Concurrency, deterministische Lock Order, Snapshot-Token-Commands und Workspace Foundation referenzimplementieren.
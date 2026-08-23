---
documentId: SPRINGMASTER-SPRINT-004-PLAN
title: Field-Proven Backend Contracts and Runtime Primitives - Solution Plan
documentType: plan
status: active
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-22
validFrom: 2026-08-22
lastReviewedAt: 2026-08-22
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-004
---

# Field-Proven Backend Contracts and Runtime Primitives - Solution Plan

## Lösungsoptionen und Auswahl

### Option A - Springmaster-Demo weiter ausbauen

Verworfen. CatalogItem oder Team Membership müssten künstlich um Persistenz-, Multi-Root-, Security- und Concurrency-Komplexität erweitert werden, obwohl belastbare reale Muster bereits in Personnel vorliegen. Das erhöht Demo- und Wartungsumfang ohne zusätzlichen Architekturwert.

### Option B - Personnel-Code upstream kopieren

Verworfen. Personnel enthält fachliche Aggregate, konkrete Lockphasen, Spring-/JPA-Bindungen und projektspezifische Security. Copy/Paste würde den Springmaster-Core fachlich verunreinigen und die bestehende Authority-Grenze verletzen.

### Option C - Read-only Field Evidence plus kleinste fachfreie Runtime-Primitives

Ausgewählt.

Springmaster qualifiziert die vorhandenen Contracts gegen Personnel 000248, übernimmt nur die nachweislich fachfreien Runtime-Primitives neu implementiert in `de.cocondo.system`, und präzisiert den generischen Concurrency-Vertrag. Personnel bleibt unverändert.

## Architektur- und Contract-Auswirkungen

### 1. Keine neue ADR erwartet

ADR-0017 und ADR-0018 decken Operation Profiles, Preconditions, Consistency und die Abgrenzung application-specific lock ordering bereits ab. Sprint 004 konkretisiert innerhalb dieser Entscheidungen.

Wenn die Umsetzung eine Änderung dieser Entscheidungen verlangt, wird nicht im Task improvisiert: `stop-and-replan`.

### 2. Business-Date-Core

Ziel-API:

```text
de.cocondo.system.time.BusinessDateProvider
  LocalDate currentDate()

de.cocondo.system.time.ClockBusinessDateProvider
  ClockBusinessDateProvider(Clock clock)
  LocalDate currentDate()
```

Leitplanken:

- reine `java.time`-Abhängigkeit;
- keine Spring-Annotation erforderlich;
- kein JPA;
- kein fachlicher Kalender, Holiday- oder Timezone-Framework;
- `Clock` ist explizite technische Zeitquelle;
- Business Date bleibt semantisch von Audit Timestamp/Instant getrennt.

### 3. Expected-Version-Core

Ziel-API:

```text
de.cocondo.system.concurrency.ExpectedVersionGuard
  void requireMatch(String resourceType, String resourceId, Long actualVersion, Long expectedVersion)

de.cocondo.system.exception.ExpectedVersionConflictException
```

Semantik:

- blank `resourceType`/`resourceId`, fehlender expected token oder negativer expected token -> `IllegalArgumentException` / Invalid Request;
- `actualVersion == null` oder mismatch -> `ExpectedVersionConflictException`;
- matching token -> no-op;
- kein Repository-/EntityManager-Zugriff;
- keine Spring-DAO-Exception in der Vergleichslogik;
- mehrere Einzelprüfungen sind die Primitive für ein application-owned `EXPECTED_VERSION_SET`.

Der globale HTTP-Adapter erhält eine explizite Abbildung `ExpectedVersionConflictException -> 409 / ApiErrorType.CONFLICT`. `If-Match`-Semantik 412/428 bleibt davon getrennt.

### 4. Transaction-/Concurrency-Standard

Der bestehende Wertebereich bleibt unverändert:

```text
transactionScope = SINGLE_AGGREGATE | AGGREGATE_GRAPH | MULTI_AGGREGATE
consistency = OPTIMISTIC | PESSIMISTIC | MIXED
```

Normative Ergänzung für komplexe Mutationen:

```text
preflight
-> graph discovery
-> complete lock-set derivation
-> application-owned deterministic lock order
-> acquire locks
-> revalidate graph + ownership + target/data scope + security
-> validate expected version(s)
-> revalidate business policies
-> mutate in one write transaction
-> flush / prove resulting versions where required
-> persist atomic evidence/events when contractually part of the same transaction
```

Nicht normiert werden konkrete Personnel-Phasen, Aggregate-Reihenfolgen, Repository-Methoden oder DB-Lockmodi.

### 5. Field-Qualification-Evidence

Neue Sprint-004-Evidence wird getrennt von Sprint-003-Historie geführt:

```text
contracts/api/fixtures/sprint-004/
contracts/api/evidence/sprint-004/
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-004/WORK/ANALYSES/
```

Keine Sprint-003-Fixture wird still überschrieben.

Die Field-Evidence bindet mindestens:

```text
sourceProject=Personnel
sourceExportSha256=541b6f97d22ca6aeb532f6d3f25f6f09fc16591ef7161791b5160a98f6cffb61
acceptedSourceCommit=1094199a84aeb809865d2992ef2aab65d8488226
acceptedPatch=000248_personnel_workspace_post_wsf2_contract_guardrails
excludedCandidatePatch=000249_personnel_workforce_discovery_contract_freeze
```

Für jede Real-World-Klasse stehen konkrete Source-Referenzen und das Springmaster-Mapping in der JSON-Evidence.

## Verbindlicher Personnel-Evidence-Satz

Als akzeptierte Referenz dürfen ausschließlich Aussagen aus 000248 bzw. aus Dateien verwendet werden, die der 000249-Dry-run nicht verändert.

Primäre Referenzen:

```text
PROJECT_DOCS/STANDARDS/PERSONNEL_TRANSACTION_LOCK_AND_CONCURRENCY_STANDARD.md
src/main/java/de/cocondo/app/domain/personnel/application/concurrency/ExpectedVersionGuard.java
src/main/java/de/cocondo/app/domain/personnel/classification/careergroup/CareerGroupCommandService.java
src/main/java/de/cocondo/app/domain/personnel/staffing/application/v3/V3StaffingPlanFoundationCommandService.java
src/main/java/de/cocondo/app/domain/personnel/staffing/application/v3/V3PlannedWorkforceCommandService.java
src/main/java/de/cocondo/app/domain/personnel/staffing/application/v3/V3PlannedWorkforceAccessPolicy.java
src/main/java/de/cocondo/app/domain/personnel/staffing/application/v3/V3PlannedWorkforceQueryService.java
src/main/java/de/cocondo/app/domain/personnel/staffing/application/v3/V3StaffingPlanWorkspaceQueryService.java
src/main/java/de/cocondo/app/domain/personnel/staffing/api/v3/V3PlannedWorkforceController.java
src/main/java/de/cocondo/app/domain/personnel/staffing/api/v3/V3StaffingPlanWorkspaceController.java
src/main/java/de/cocondo/app/domain/personnel/temporal/BusinessDateProvider.java
src/main/java/de/cocondo/app/domain/personnel/temporal/SystemBusinessDateProvider.java
```

Der 000249-Dry-run verändert 17 Pfade, insbesondere `PERS_ADR_0045_WORKSPACE_API_CONTRACT.md`, `PERS_ADR_0046_PLANNED_WORKFORCE_P1A.md`, mehrere Registers/Requirements und `PROJECT_DOCS/index.md`. Diese exportierten Candidate-Versionen sind keine positive Evidence.

## Real-World Qualification Cases

| ID | Personnel-Muster | Springmaster-Mapping | Erwartung |
|---|---|---|---|
| `RW-01` | CareerGroup-Revision mit `ExpectedVersionGuard` | `EXPECTED_VERSION`, `SINGLE_AGGREGATE`, `OPTIMISTIC` | PASS |
| `RW-02` | V3 Planned Workforce Allocation/Carry-forward mit mehreren Root-/Relation-Versionen | `EXPECTED_VERSION_SET`, `AGGREGATE_GRAPH` oder `MULTI_AGGREGATE` | PASS |
| `RW-03` | kanonische Lock-Ermittlung + Post-Lock-Revalidation in V3/Personnel-Concurrency | `PESSIMISTIC`/`MIXED`, application-specific order | PASS |
| `RW-04` | Business Date + effective-dated Workforce/Workspace Reads | `TEMPORAL_READ` / `TEMPORAL_RELATION` | PASS |
| `RW-05` | V3 Workspace Capacity / strukturelle Read Models | `PROJECTION_READ` | PASS |
| `RW-06` | V3 Planned Workforce Access Policy + Plan-Scope + Person Visibility | operation security + target/data scope | PASS |
| `RW-07` | V3 Workspace als Consumer mehrerer Backend-Ressourcen | `WORKSPACE` nicht Backend kind/role; UI reload/dirty state nicht Backend effect | PASS negative-boundary |

Ein einzelnes Fixture darf mehrere RW-Cases belegen, solange die maschinenlesbare Field-Evidence die Zuordnung eindeutig macht.

## Slices und Reihenfolge

### Slice 0 - Hostseitige Sprint-Aktivierung vor Codex

Vor jeder Codex-Execution ist die Sprint-Governance hostseitig erfüllt:

- Sprint 003 bleibt fachlich geschlossen und wird nicht reinvoked; sein stale Active-/Closure-Zustand wird, soweit im Live-Checkout noch vorhanden, deterministisch gegen die bereits akzeptierte Post-Sprint-003-Evidence reconciled und archiviert.
- `SPRINT_BRIEF.md` und `SOLUTION_PLAN.md` für Sprint 004 sind **vor Execution** `active`.
- `STATUS.md` existiert als einzige aktuelle Sprint-004-Statusquelle mit `sprintPhase: execution`.
- `COMPLETION_REPORT.md` existiert als `draft`, `qualificationStatus: pending`, `closureStatus: open`.
- `PROJECT_DOCS/index.md` referenziert die vier aktiven Sprint-004-Pflichtdokumente.

Diese Aktivierung ist Trusted-Host-/Operator-Arbeit und **kein Codex-Agent-Task**. Der daraus resultierende Main-HEAD wird zum `baseCommit` von `S004-A001`.

### Slice 1 - Task-interne Baseline und Authority

Read-only prüfen:

- `AGENTS.md`;
- aktiven Sprint-004-Brief und Solution Plan;
- ADR-0017/0018;
- Mutation Precondition Standard;
- Transaction and Consistency Classification Standard;
- Sprint-003 fixture index und Personnel fixture;
- Core- und Version Policy.

Keine Produktänderung, wenn der Worktree nicht exakt dem Task Contract/Base-Commit entspricht. Sprint Brief und Solution Plan sind immutable Task-Input und werden von Codex nicht abgeschwächt oder umgeschrieben.

### Slice 2 - Field-Proven Contract Fixtures und Work-Evidence

Im Task-Worktree neu anlegen bzw. gezielt aktualisieren:

```text
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-004/STATUS.md
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-004/COMPLETION_REPORT.md
PROJECT_DOCS/SPRINTS/ACTIVE/SPRINGMASTER-SPRINT-004/WORK/ANALYSES/FIELD_QUALIFICATION_REPORT.md
contracts/api/fixtures/sprint-004/**
contracts/api/evidence/sprint-004/**
```

`COMPLETION_REPORT.md` bleibt bis Host-Qualification ausdrücklich `qualificationStatus: pending`, `closureStatus: open`.

### Slice 3 - Business-Date-Core

Neue positive Sprint-004-Fixtures auf Basis des immutable Evidence-Blocks erstellen. Bestehende negative Sprint-003-Fixtures für Workspace/UI-Reload- und Version-Token-Grenzen dürfen über den Sprint-004-Index referenziert, aber nicht dupliziert oder umgedeutet werden.

Pflicht:

- 7/7 RW-Cases abgedeckt;
- keine neue operation kind/role;
- source-bound Field-Evidence JSON;
- kein unqualifizierter 000249-Source-Pfad als positive Evidence;
- bestehendes `bin/backend-contract.py validate` validiert den Sprint-004-Fixture-Index ohne Tooländerung.

### Slice 3 - Business-Date-Core

Implementieren:

```text
src/main/java/de/cocondo/system/time/BusinessDateProvider.java
src/main/java/de/cocondo/system/time/ClockBusinessDateProvider.java
src/test/java/de/cocondo/system/time/ClockBusinessDateProviderTest.java
PROJECT_DOCS/CORE/CORE_BUSINESS_DATE_BOUNDARY.md
```

Tests mindestens:

- fixed Clock liefert exakt erwartetes Datum;
- unterschiedliche Clock-Zonen werden ausschließlich über den injizierten Clock bestimmt;
- null Clock wird abgewiesen;
- kein Test ruft unkontrolliert `LocalDate.now()` auf.

### Slice 4 - Expected-Version-Core und HTTP-Adapter

Implementieren:

```text
src/main/java/de/cocondo/system/concurrency/ExpectedVersionGuard.java
src/main/java/de/cocondo/system/exception/ExpectedVersionConflictException.java
src/test/java/de/cocondo/system/concurrency/ExpectedVersionGuardTest.java
PROJECT_DOCS/CORE/CORE_EXPECTED_VERSION_GUARD.md
```

Gezielt erweitern:

```text
src/main/java/de/cocondo/system/http/GlobalApiExceptionHandler.java
src/test/java/de/cocondo/system/http/GlobalApiExceptionHandlerTest.java
```

Tests mindestens:

- match -> PASS;
- stale -> `ExpectedVersionConflictException`;
- actual null -> conflict;
- expected null -> invalid request primitive;
- expected < 0 -> invalid request primitive;
- blank resource identity -> invalid request primitive;
- global handler maps stale conflict deterministisch auf HTTP 409 + `ApiErrorType.CONFLICT`.

### Slice 5 - Standards

Gezielt präzisieren:

```text
PROJECT_DOCS/STANDARDS/API/MUTATION_PRECONDITION_STANDARD.md
PROJECT_DOCS/STANDARDS/ARCHITECTURE/TRANSACTION_AND_CONSISTENCY_CLASSIFICATION_STANDARD.md
```

Keine neue ADR, keine neuen Enumwerte.

Für neue normative Regeln positive/negative Evidence im Sprint-004-Test-/Fixture-Satz ergänzen.

### Slice 6 - Implementation Completion

Codex führt die im Task Contract vorgegebenen Qualification Commands so weit wie möglich im Worktree aus und repariert normale Implementierungsfehler innerhalb desselben Tasks.

Vor Handoff muss der Repository-Inhalt sagen:

```text
implementationStatus=COMPLETE
qualificationStatus=PENDING_TRUSTED_HOST
closureStatus=OPEN
SPRINT004_RESULT=NOT_YET_QUALIFIED
```

Codex setzt niemals `DOD_QUALIFIED`.

## Teststrategie und Zwischenverifikationen

Pflichtreihenfolge:

1. Core-targeted Tests;
2. Sprint-004 Field-Evidence/Fixture Validation;
3. Global API error mapping test;
4. `git diff --check`;
5. vollständige Maven Tests;
6. report-only gate profile;
7. `springmaster-gates report --clean`;
8. `mvn clean verify`.

Bestehende Sprint-003-Fixtures bleiben Regression Input.

## Messkriterien

```text
RW_CASES_PASS=7
RW_CASES_FAIL=0
UNRESOLVED_CONTRACT_GAPS=0
NEW_OPERATION_KINDS=0
NEW_OPERATION_ROLES=0
PERSONNEL_DEPENDENCIES_IN_CORE=0
NEW_RUNTIME_DEPENDENCIES=0
CORE_TARGETED_TEST_FAILURES=0
FULL_TEST_FAILURES=0
EXTERNAL_PROJECT_WRITES=0
HARNESS_CHANGES=0
```

## Migration und Rollback

Keine Datenmigration und keine Zielprojektmigration.

Die Änderungen sind additive Springmaster-Core-/Contract-Erweiterungen. Vor Human Accept bleibt der Candidate vollständig verwerfbar. Ein Rollback nach Acceptance ist ein normaler cpatch/Git-Folgechange, nicht Bestandteil des Codex-Tasks.

## Tool- und Gate-Einsatz

Codex nutzt ausschließlich Repository-Produktwerkzeuge und Maven innerhalb des vorbereiteten Worktrees.

Nicht Teil des Agent-Scope:

```text
agent-task lifecycle
codex-host-sandbox
process-ops
cpatch
patch dry-run
human accept
patch accept
```

Diese laufen auf dem Trusted Host.

## Dokumentations- und Registerauswirkungen

Dauerhaft:

- Core-Dokumentation für Business Date und Expected Version;
- zwei präzisierte Standards;
- Sprint-004 Brief und Completion Report;
- Field-Qualification-Evidence.

Temporär:

- `SOLUTION_PLAN.md`;
- `STATUS.md`;
- `WORK/**`-Analysen, soweit sie keinen eigenständigen historischen Evidenzwert besitzen.

Die finale Operator-Closure behandelt diese gemäß Sprint Governance und archiviert nur die dauerhaften Sprintartefakte.

## Versionswirkung

Erwartete SemVer-Wirkung:

```text
CORE: minor (neue öffentliche fachfreie Runtime-Primitives)
FOUNDATION: minor (neue qualifizierte Foundation-Fähigkeit)
TOOLING: none
DEMO: none
TEMPLATE: none
UPDATE: none
```

Codex dokumentiert den Impact, ändert aber nicht `platform/versions/platform.env`, `pom.xml` oder `PLATFORM_STATE_PATCH`. Die konkreten finalen Werte werden nach erfolgreicher Trusted-Host-Qualification und mit Kenntnis der finalen Patch-Provenienz deterministisch geschlossen. Dafür wird kein Agent-Task erzeugt.

## Patch- oder Commitsequenz

Bevorzugter Gesamtpfad:

```text
1. hostseitige Sprint-003-Closure-Reconciliation (nur falls noch stale)
2. Sprint-004-Pflichtdokumente aktivieren und indexieren
3. neuen sauberen Main-HEAD als S004-A001.baseCommit binden
4. S004-A001 Task Contract validieren und vorbereiten
5. Codex S004-A001 im detached Worktree
6. postcheck
7. Trusted-Host agent-task qualification
8. immutable handoff
9. separater Candidate aus dem Handoff
10. deterministische Host-Closure:
    - Qualification Evidence binden
    - STATUS/COMPLETION korrekt schließen
    - Sprint-Dokumente nach Governance finalisieren/archivieren
    - Version Truth + Maven-Version + finalen State Patch setzen
11. finalen Candidate vollständig prüfen
12. cpatch V5 create/plan
13. process-ops patch-dry-run
14. separater Human Accept
15. process-ops patch-accept
16. read-only Post-Accept-Verifikation
17. finaler Export/Handoff
```

Schritte 1-3 und 10 sind keine Agent-Arbeit und keine neue Harness-Entwicklung. Sie stellen nur die bereits entschiedene Sprint-/Version-Wahrheit her bzw. schließen sie nach realer Qualification.

## Unsicherheiten und Entscheidungszeitpunkte

### U-001 - echter Contract Gap

Wenn RW-01..RW-07 mit bestehenden Sprint-003-Begriffen nicht korrekt modellierbar sind: Stop-and-Replan. Kein neuer Enumwert durch Codex.

### U-002 - Historical Sprint-003 Lifecycle Drift

Die bekannte historische Sprint-003-Selbstauskunft ist nicht S004-Agent-Scope. Falls ein bestehender Directory-/Documentation-Gate dadurch Sprint 004 technisch blockiert, ist dies ein externer Host-Closure-Blocker und darf nicht durch Produktcode oder Harnessänderungen umgangen werden.

### U-003 - Version Closure

Die finalen Versionswerte werden erst nach realer Qualification bestätigt. Erwartet sind Core/Fundation minor, aber der Task erfindet weder Patch-ID noch State-Patch-Provenienz.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-22 | - | draft | Solution Plan aus bestätigter Sprint-004-DoD und Personnel-000248-Vergleich erstellt. |
| 2026-08-22 | draft | active | Lösungszuschnitt und Ausführungsgrenzen vor Execution bestätigt. |

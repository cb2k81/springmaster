---
documentId: SPRINGMASTER-SPRINT-004-BRIEF
title: Field-Proven Backend Contracts and Runtime Primitives - Sprint Brief
documentType: sprint-brief
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
temporary: false
sprintId: SPRINGMASTER-SPRINT-004
sprintStart: 2026-08-22
targetCompletion: 2026-08-31
---

# Field-Proven Backend Contracts and Runtime Primitives - Sprint Brief

## Sprintziel

Sprint 004 macht ausgewählte, in Sprint 003 definierte Backend-Verträge an realen komplexen Backend-Strukturen belastbar und überführt zwei nachweislich fachfreie Runtime-Primitives in den Springmaster-Core.

Der Sprint liefert drei zusammenhängende Ergebnisse:

1. Die Sprint-003-Semantik für Operations, Preconditions, Transaction Scope, Consistency, Security, Temporal/Projection und Backend Effects wird gegen den nachweislich qualifizierten Personnel-Stand `000248` read-only qualifiziert.
2. Springmaster erhält eine fachfreie Business-Date-Boundary und eine fachfreie Expected-Version-Validation-Boundary mit deterministischen Tests und standardkonformer Fehlerabbildung.
3. Der Transaction-/Concurrency-Standard wird um die generischen, feldbewährten Invarianten für `AGGREGATE_GRAPH` und `MULTI_AGGREGATE` ergänzt, ohne Personnel-spezifische Lockgraphen oder einen generischen Coordinator zu übernehmen.

Sprint 004 optimiert damit das Springmaster-Produkt und seine wiederverwendbare Backend-Basis. Host-Harness, `process-ops`, cpatch und Codex-Lifecycle sind Ausführungsgrenzen und ausdrücklich kein Sprintinhalt.

## Strategischer Bezug

- Springmaster bleibt kanonische Quelle für fachfreie Java-Backend-Grundlagen, Verträge und Standards.
- Reale Fachprojekte dienen als Belastungsprobe; ihre Fachlogik wird nicht in den Core kopiert.
- Feldbewährte Mechanismen werden nur übernommen, wenn ihre fachfreie Semantik unabhängig vom Quellprojekt nachweisbar ist.
- Agentenbasierte Umsetzung bleibt auf einen immutable, scopebegrenzten Springmaster-Task beschränkt; externe Projekte bleiben read-only.

## Ausgangslage und Baseline

Kanonische Springmaster-Ausgangsbaseline:

```text
BRANCH=main
HEAD=de7d31744a25036b3e4f544c048f0a53afc2cd34
SPRINT003_COMPLETE=true
PATCH_000242=ACCEPTED_AND_VERIFIED
A006_STATUS=HANDED_OFF
```

Sprint 003 gilt als geschlossen und wird durch Sprint 004 nicht erneut qualifiziert oder reinvoked.

Read-only Personnel-Referenz:

```text
EXPORT=personnel_export_full_2026-08-22_15-55-17-917Z.zip
EXPORT_SHA256=541b6f97d22ca6aeb532f6d3f25f6f09fc16591ef7161791b5160a98f6cffb61
LAST_FULLY_QUALIFIED_PATCH=000248_personnel_workspace_post_wsf2_contract_guardrails
LAST_FULLY_QUALIFIED_COMMIT=1094199a84aeb809865d2992ef2aab65d8488226
FULL_REGRESSION_STATUS=PASS
FULL_TESTS=1018
FULL_FAILURES=0
FULL_ERRORS=0
LIQUIBASE_VERSION=020
```

Der Export enthält bereits einen vorbereiteten, aber nicht qualifizierten `000249`-Contract-Freeze. Dessen neue oder geänderte Dateien sind keine Acceptance Evidence für Sprint 004. Sie dürfen höchstens als nichtnormativer Hinweis betrachtet werden.

## Problemstellung und Stakeholder

Sprint 003 hat eine belastbare Contract-Sprache geschaffen, aber mehrere komplexe Semantikklassen sind bislang überwiegend synthetisch oder über ältere externe Evidence belegt. Parallel hat Personnel reale Runtime-Muster für Expected Versions, Multi-Root-Concurrency, Business Date, target-aware Security und V3-Workspace-Reads umgesetzt.

Ohne kontrollierte Rückkopplung drohen zwei Fehlerbilder:

- Springmaster entwickelt künstliche Demo-Komplexität, obwohl belastbare Feld-Evidence bereits existiert;
- wiederverwendbare Mechanismen verbleiben projektspezifisch, obwohl ihre fachfreie Semantik inzwischen nachweisbar ist.

Stakeholder sind Springmaster-Maintainer, Entwickler gemanagter Backend-Projekte, Architektur-/Security-Reviewer und Betreiber des kontrollierten Codex-Prozesses.

## Anforderungen

| ID | Verbindliche Anforderung |
|---|---|
| `S004-REQ-001` | Sprint 004 bindet ausschließlich an die akzeptierte Springmaster-Post-Sprint-003-Baseline; Sprint 003 wird nicht wieder geöffnet. |
| `S004-REQ-002` | Personnel wird ausschließlich read-only verwendet; der qualifizierte Referenzanker ist Commit `1094199a84aeb809865d2992ef2aab65d8488226`. |
| `S004-REQ-003` | Dateien, die durch den unqualifizierten Personnel-Patch 000249 neu angelegt oder verändert wurden, dürfen keine positive Acceptance Evidence bilden. |
| `S004-REQ-004` | Mindestens sechs reale Semantikklassen werden source-bound gegen Springmaster-Verträge qualifiziert: single expected version, expected version set/multi-root, pessimistic-or-mixed revalidation, temporal relation/business date, projection read und operation security plus target/data scope. |
| `S004-REQ-005` | Die Real-World-Zuordnung ist maschinenlesbar und enthält Export-/Commit-Identität, konkrete Source-Referenzen, Springmaster-Contract-Mapping und Qualification Result. |
| `S004-REQ-006` | Kein Contract Gap wird durch Personnel-spezifische Enumwerte, Rollen, Aggregate, Permissions oder Lockphasen geschlossen. |
| `S004-REQ-007` | `WORKSPACE` bleibt kein Backend-`operationKind` oder `operationRole`; UI reload graph und dirty state bleiben außerhalb von Backend Effects. |
| `S004-REQ-008` | Springmaster erhält `de.cocondo.system.time.BusinessDateProvider` als fachfreie, injizierbare Business-Date-Boundary. |
| `S004-REQ-009` | Springmaster erhält einen Clock-basierten, frameworkfreien Adapter für die Business-Date-Boundary; deterministische Tests verwenden einen kontrollierten `Clock`. |
| `S004-REQ-010` | Springmaster erhält eine fachfreie Expected-Version-Validation-Boundary ohne Repository-, EntityManager-, HTTP- oder Personnel-Abhängigkeit. |
| `S004-REQ-011` | Ein gelieferter stale/mismatching body expected-version token führt über den Springmaster-Fehlervertrag zu `409 Conflict`; fehlende/ungültige Body-Tokens bleiben Invalid-Request/Validation-Fälle und werden nicht in `428` umgedeutet. |
| `S004-REQ-012` | `EXPECTED_VERSION_SET` bleibt eine Application-Orchestration aus mehreren fachfreien Einzelprüfungen; es entsteht kein generischer Multi-Aggregate-Coordinator. |
| `S004-REQ-013` | Der Transaction-/Concurrency-Standard normiert graph discovery, vollständige Lock-Set-Ermittlung, application-owned deterministische Lockordnung, Post-Lock-Revalidation, Expected-Version-Prüfung, Policy-Revalidation, atomare Mutation sowie Flush/Version-Proof, soweit erforderlich. |
| `S004-REQ-014` | Optimistic locking bleibt Default. `PESSIMISTIC` und `MIXED` bleiben explizite use-case-spezifische Ergänzungen. |
| `S004-REQ-015` | Die konkrete Lock-Reihenfolge, Lock-Phasennummern, Aggregate-Reihenfolgen und Datenbank-Lockmodi bleiben application-specific. |
| `S004-REQ-016` | Ein nach Revalidation veränderter notwendiger Lockgraph wird nicht opportunistisch in abweichender Reihenfolge nachgesperrt; die Anwendung benötigt fail-closed- oder explizite Retry-Semantik. |
| `S004-REQ-017` | Bestehende Sprint-003-Operation-/Precondition-/GWC-Verträge bleiben rückwärtskompatibel; keine neuen `operationKind`-/`operationRole`-Werte ohne nachgewiesenen allgemeinen Contract Gap. |
| `S004-REQ-018` | Keine neue Runtime-Dependency wird eingeführt. |
| `S004-REQ-019` | Neue oder geänderte normative Regeln besitzen positive und negative automatisierte Evidence. |
| `S004-REQ-020` | Code, Tests, Standards, Fixtures, Sprint-Evidence und Abschlussdokumentation treffen am Ende dieselbe Aussage. |
| `S004-REQ-021` | Personnel, GWC und andere Managed Targets werden durch Sprint 004 nicht mutiert. |
| `S004-REQ-022` | Codex verändert keinen Host-Harness, keine Agent-Lifecycle-Semantik, kein `process-ops`, kein cpatch und keine Toolkit-Runtime. |
| `S004-REQ-023` | Codex darf den Sprint nicht selbst als `DOD_QUALIFIED` oder `completed` schließen; die kanonische Closure folgt erst nach Trusted-Host-Qualification. |
| `S004-REQ-024` | Öffentliche Core-Erweiterungen erhalten eine explizite SemVer-Bewertung; Version Truth und finaler State Patch werden erst in der Trusted-Host-Closure auf den tatsächlich akzeptierten Patch gebunden. |

## Qualitätsanforderungen

- Keine fachprojektspezifische Semantik im Core.
- Keine neue generische Runtime nur deshalb, weil ein Contract-Wert existiert.
- Keine neue Library oder Framework-Abhängigkeit.
- Öffentliche Core-Typen besitzen knappe Javadoc und deterministische Unit Tests.
- Neue Evidence ist source-bound und unterscheidet akzeptierte Referenz von unqualifiziertem Candidate-Inhalt.
- Keine Reife-Promotion allein aufgrund externer Personnel-Implementierung; Springmaster-`REFERENCE_IMPLEMENTED` bleibt eine Aussage über Springmaster-eigene Referenzimplementierung.
- Keine stillen Breaking Changes an Sprint-003-Schemas oder Runtime Contracts.

## In Scope

- read-only Field Qualification gegen Personnel 000248;
- Sprint-004-Fixtures und maschinenlesbare Field-Qualification-Evidence;
- Business-Date-Core-Boundary und Clock-Adapter;
- Expected-Version-Guard plus fachfreie Conflict-Exception;
- standardkonforme `409`-Abbildung im globalen API-Fehleradapter;
- Präzisierung von Mutation-Precondition- und Transaction/Consistency-Standard;
- gezielte Core-/Contract-/Evidence-Tests;
- Sprint-004-Dokumente und Abschluss-Evidence;
- SemVer-Bewertung für Core und Foundation.

## Out of Scope

- jede Änderung an Personnel, GWC oder anderen Managed Targets;
- Personnel-`operationKey`-Adoption;
- Personnel-Core-Migration auf `de.cocondo.system`;
- CatalogItem-Canonicalization oder Ausbau zum komplexen Concurrency-Demo;
- Ausbau Team Membership zur Produktionsruntime;
- Effective-Dating-Framework, Calendar Engine oder Temporal-DB-Framework;
- generischer Lock Manager oder Multi-Aggregate-Transaction-Coordinator;
- generische Bulk-, Job-, History-, Projection-, Workspace- oder Reload-Runtime;
- neue Dependency;
- automatische Strict-Gate-Promotion;
- Harness-, cpatch-, `process-ops`- oder Agent-Governance-Änderung;
- A004/A005/A006-Reinvocation oder A007 zur Sprint-003-Closure;
- Cleanup historischer Worktrees/Evidence;
- Korrektur der bekannten historischen Sprint-003-Lifecycle-Dokumentdrift als Codex-Aufgabe.

## Constraints und Abhängigkeiten

- Codex arbeitet ausschließlich im autorisierten Springmaster-Task-Worktree.
- Der Personnel-Checkout ist für Codex kein Arbeitsbereich und darf nicht gesucht oder beschrieben werden.
- Die für Personnel erforderlichen Fakten werden als immutable, hashgebundener Prompt-Input bereitgestellt.
- Akzeptierte ADR-0017 und ADR-0018 bleiben Authority. Ein erforderlicher ADR-Change ist ein Stop-and-Replan-Ereignis.
- Bestehende `operationKind`-/`operationRole`-Enums bleiben unverändert, sofern kein allgemeiner Contract Gap nachgewiesen wird.
- Die Trusted-Host-Qualification bleibt vollständiger Qualification Owner.

## Risiken

- Personnel-spezifische Lock- und Aggregate-Strukturen könnten zu früh als allgemein interpretiert werden.
- Eine zu breite Core-Migration könnte Copy-and-diverge durch Big-Bang-Konvergenz ersetzen.
- Ein fehlender Unterschied zwischen Body Expected Version und HTTP `If-Match` könnte 409/412/428-Semantik verwischen.
- Die unqualifizierten Personnel-000249-Dokumente könnten versehentlich als akzeptierte Quelle verwendet werden.
- Codex könnte einen grünen lokalen Teststand fälschlich als Sprint-Closure interpretieren.

## Definition of Ready

- [x] Sprint-003-Baseline und Handoff sind forensisch gebunden.
- [x] Personnel-Export SHA256 ist verifiziert.
- [x] Der letzte vollständig qualifizierte Personnel-Stand 000248 ist identifiziert.
- [x] Die durch Personnel 000249 veränderte Pfadmenge ist bekannt und als Acceptance Evidence ausgeschlossen.
- [x] Sprintziel, DoD, Nichtziele und Architekturleitplanken sind bestätigt.
- [x] Kein Personnel-Write ist für Sprint 004 erforderlich.
- [x] Die Umsetzung kann als ein kohärenter Springmaster-Agent-Task geschnitten werden.

## Definition of Done

- [ ] Alle `S004-REQ-001` bis `S004-REQ-024` sind mit auflösbarer Evidence bewertet und erfüllt.
- [ ] Die sieben verbindlichen Real-World-Cases `RW-01` bis `RW-07` sind `PASS` und erzeugen keinen offenen allgemeinen Contract Gap.
- [ ] Business-Date- und Expected-Version-Primitives sind fachfrei implementiert, getestet und dokumentiert.
- [ ] Die neuen Transaction-/Concurrency-Invarianten sind normativ präzisiert und durch positive/negative Evidence abgesichert.
- [ ] Personnel, GWC, andere Managed Targets und Host-Harness bleiben unverändert.
- [ ] Trusted-Host-Qualification, Version Truth, Completion Report und Archivierungszustand sind konsistent geschlossen.

Sprint 004 ist nur qualifiziert, wenn alle folgenden Aussagen nach Trusted-Host-Qualification und finaler Closure wahr sind:

```text
SPRINT004_BASELINE_BOUND=true
PERSONNEL_REFERENCE_COMMIT=1094199a84aeb809865d2992ef2aab65d8488226
PERSONNEL_REFERENCE_MUTATED=false
REAL_WORLD_CASES=PASS_7_OF_7
UNRESOLVED_REAL_WORLD_CONTRACT_GAPS=0
PERSONNEL_SPECIFIC_CONTRACT_VALUES=0
BUSINESS_DATE_CORE_PRIMITIVE=true
EXPECTED_VERSION_CORE_PRIMITIVE=true
EXPECTED_VERSION_CONFLICT_HTTP_409=true
OPTIMISTIC_DEFAULT_PRESERVED=true
GENERIC_LOCK_ORDER_DEFINED=false
GENERIC_MULTI_AGGREGATE_COORDINATOR=false
NEW_RUNTIME_DEPENDENCIES=0
UNTESTED_NEW_NORMATIVE_RULES=0
UNINTENDED_PUBLIC_API_BREAKS=0
EXTERNAL_PROJECT_MUTATIONS=0
HARNESS_SCOPE_CHANGES=0
SPRINT004_RESULT=DOD_QUALIFIED
```

Zusätzlich:

- alle Sprint-004-Requirements sind auf Evidence gemappt;
- Sprint-004-Field-Evidence ist maschinenlesbar, deterministisch und source-bound;
- neue positive Fixtures validieren; negative Boundary-Fixtures scheitern mit den erwarteten stabilen Diagnosen;
- `git diff --check`, gezielte Tests, Full Tests, Report Gates und `mvn clean verify` sind grün;
- Core-, Contract- und Dokumentationsgrenzen sind eingehalten;
- finaler Completion Report wird erst aus realer Qualification Evidence geschlossen;
- der abgeschlossene Sprint wird gemäß Sprint Governance archivierungsfähig gemacht.

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Personnel-000248 Field Qualification | REQ-002..007 | 7/7 Real-World-Cases; 0 Contract Gaps | Sprint-004 Field Evidence + Fixtures | Springmaster | planned |
| M-002 | Business-Date-Core | REQ-008..009 | frameworkfrei, Clock-kontrolliert, Tests grün | Core Code + Unit Tests | Springmaster | planned |
| M-003 | Expected-Version-Core | REQ-010..012 | Match/Invalid/Stale deterministisch; stale -> 409 Adapter | Core Code + HTTP Test | Springmaster | planned |
| M-004 | Concurrency-Contract-Härtung | REQ-013..017 | generische Invarianten normiert; keine app-spezifische Lockordnung | Standards + positive/negative Evidence | Springmaster | planned |
| M-005 | Qualification und Closure | REQ-018..024 | vollständige Regression; externe Mutation 0; Closure aus Host-Evidence | Qualification + Completion Report | Trusted Host | planned |

## SemVer-Auswirkung

Erwarteter Impact:

```text
PLATFORM_CORE_VERSION=minor
PLATFORM_TOOLING_VERSION=none
PLATFORM_TEMPLATE_VERSION=none
PLATFORM_DEMO_VERSION=none
PLATFORM_UPDATE_VERSION=none
PLATFORM_VERSION=minor
```

Die konkreten Versionswerte und `PLATFORM_STATE_PATCH` werden erst in der finalen Trusted-Host-Closure gegen den tatsächlich akzeptierten Patch gesetzt. Codex erfindet keine Patch-ID.

## Stop- und Abbruchkriterien

`stop-and-replan`, wenn mindestens eines eintritt:

1. ein wichtiges reales Personnel-Muster ist mit bestehenden Springmaster-Concepts nicht semantisch korrekt ausdrückbar;
2. ein neuer `operationKind`/`operationRole` wäre nötig, ohne dass die Allgemeingültigkeit nachgewiesen ist;
3. Core-Code benötigt Personnel-spezifische Typen oder Semantik;
4. die Lösung benötigt einen generischen Multi-Aggregate-/Lock-Coordinator;
5. eine neue Runtime-Dependency wird nötig;
6. ein bestehender öffentlicher Springmaster-Vertrag müsste breaking geändert werden;
7. die erforderliche Personnel-Evidence ist durch 000249 verunreinigt oder nicht auf 000248 zurückführbar;
8. Personnel, GWC oder ein anderes Zielprojekt müsste mutiert werden;
9. ein ADR müsste materiell geändert werden;
10. der Task müsste den autorisierten Springmaster-Produkt-Scope verlassen.

Normale fehlgeschlagene Implementierungstests sind kein Stop-Kriterium, sondern Repair-Signal innerhalb desselben Tasks.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-22 | - | planned | Sprint-004-Vertrag aus Post-Sprint-003- und Personnel-000248-Vergleich abgeleitet. |
| 2026-08-22 | planned | active | Auftrag, Scope, DoR, DoD, Nichtziele und Stop-Kriterien vor Execution bestätigt. |

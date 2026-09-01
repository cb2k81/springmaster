---
documentId: SPRINGMASTER-SPRINT-006-BRIEF
title: Governance & Tooling Simplification / Managed Project Recovery - Sprint Brief
documentType: sprint-brief
status: active
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-09-01
validFrom: 2026-09-01
lastReviewedAt: 2026-09-01
reviewBy: 2026-09-30
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-006
sprintStart: 2026-09-01
targetCompletion: 2026-09-30
---

# Governance & Tooling Simplification / Managed Project Recovery - Sprint Brief

## Sprintziel

Sprint 006 stellt die praktische Nutzbarkeit von Springmaster-Governance und -Tooling wieder in den Vordergrund. Der Sprint setzt ADR-0020 und `GOAL-008` um und nutzt die in Sprint 005 qualifizierte autonome Foundation, ohne deren Sicherheits-, Scope- und Human-Accept-Grenzen abzuschwächen.

Leitprinzip:

> **Standardisieren, unterstützen, nicht blockieren.**

Der Sprint ist erfolgreich, wenn sichere Standardfälle einfacher herstellbar sind als lokale Sonderwege, defektes Tooling einen offiziellen Recovery-Pfad besitzt und reale Fachprojekte nach Übernahme eines versionierten Springmaster-Toolingstands autonom arbeitsfähig bleiben.

## Strategischer Bezug

- Springmaster bleibt Wissenssammler, Qualitätsintegrator, Producer und Releasequelle für fachfreie Backend-Grundlagen, gemeinsame Contracts und Tooling.
- Zielprojekte erhalten versionierte, projekt-eigene Tooling-Komponenten; ein Springmaster-Nachbarcheckout ist keine normale Laufzeit- oder Entwicklungsabhängigkeit.
- Governance kontrolliert reale Risiken, soll aber keine zusätzliche Protokollkenntnis oder Self-Lock erzeugen.
- Das Patchsystem bleibt an Delivery-/Acceptance-/Target-Grenzen stark; Exploration und normale Engineering-Arbeit werden davon getrennt.
- Portabilität und GWC-Konformität werden erst auf die vereinfachte, reparierbare Toolchain aufgebaut.

## Ausgangslage und Baseline

Kanonische Aktivierungsbaseline:

```text
BRANCH=main
HEAD=1a7af80ec573a0b4ef885d1d6e5d14e88bdb5021
PLATFORM_STATE_PATCH=000262_s005-trusted-closure
SPRINT005_ARCHIVED=true
SPRINT005_QUALIFICATION=qualified
SPRINT005_CLOSURE=completed
```

Der Aktivierungspatch selbst verändert keine ausführbare Tooling-Runtime, keine Plattformversion, kein Maven-/Java-Produkt und kein Zielprojekt. Er etabliert die normative Enabling-Governance-Foundation und den ausführbaren Sprint-006-Auftragsraum.

Feldinputs:

- **Personnel:** Der P3-Lauf zu `000273` fand reale Produktfehler, erforderte dafür aber einen großen Shadow-/Evidence-Bestand und zahlreiche isolierte Wiederholungen. Das ist Evidence für Tooling-/Qualification-Reibung, nicht für eine Umklassifizierung des Produktfehlers.
- **ZBM:** Der aktuelle Handoff zeigt wiederholte Patch-Producer-/Validator-Probleme, konkurrierende Patch-State-Wahrheiten, fehlende gemeinsame Runner-Semantik, Source-Diff-/Environment-/DBTool-/Fresh-Checkout-Lücken und die Notwendigkeit projekt-eigener autonomer Toolingstände. Die konkrete jeweilige Live-Ursache wird im Zielprojekt weiter forensisch belegt; der Handoff wird als Design-/Field-Evidence verwendet.

## Problemstellung und Stakeholder

Die Sprints 001 bis 005 haben starke Sicherheits-, Qualification-, Evidence- und autonome Repair-Mechanismen aufgebaut. Reale Nutzung in Personnel und ZBM zeigt jedoch, dass ein Teil dieser Mechanismen inzwischen mehr nicht-fachliche Arbeit erzeugt als die eigentliche Änderung. Besonders problematisch sind Situationen, in denen ein Validator einen komplexen Vertrag erzwingt, aber kein kanonischer Producer existiert, oder ein Tool nur durch den von ihm selbst blockierten Pfad repariert werden dürfte.

Stakeholder sind Springmaster-Maintainer, Entwickler gemanagter Backend-Projekte, KI-Agenten/Operatoren, Architektur-/Security-Reviewer und Betreiber lokaler DEV-/Build-Umgebungen.

## Anforderungen

| ID | Verbindliche Anforderung |
|---|---|
| `S006-REQ-001` | ADR-0020 und GOAL-008 werden als dauerhafte Enabling-Governance-Foundation genutzt; Safety Invariants und Human-Accept-Grenzen werden nicht abgeschwächt. |
| `S006-REQ-002` | Verbindliche Safety Invariants, akzeptierte Produkt-/Architekturverträge, Standard-Prozesspfade und Guidance/Automation werden explizit getrennt; ein Tool darf keine strengere Norm erfinden als seine Authority. |
| `S006-REQ-003` | Ein offizieller Maintenance-/Recovery-Pfad verhindert Governance-Self-Lock und erlaubt die kontrollierte Reparatur eines defekten Standardtools ohne dieses Tool als einzige Reparaturvoraussetzung. |
| `S006-REQ-004` | Maintenance-/Recovery besitzt positive und negative Fixtures für erlaubte Toolreparatur, verbotene Scope-/Permission-Ausweitung, Main-/Push-Schutz und falsche Qualification-Behauptungen. |
| `S006-REQ-005` | Mindestens ein absichtlich defekter Springmaster-Toolpfad wird über den Recovery-Pfad repariert und anschließend vollständig qualifiziert, ohne Safety Invariants zu umgehen. |
| `S006-REQ-006` | Normale lokale Engineering-Arbeit kann Branch/Worktree -> Change -> gezielte Verifikation -> risikogerechte Qualification -> Commit durchlaufen, ohne vorher ein Patchartefakt erzeugen zu müssen. |
| `S006-REQ-007` | cpatch bleibt der qualifizierte Delivery-/Acceptance-/Cross-Repository-Mechanismus; seine Sicherheitsgrenzen werden nicht als allgemeiner Development Hot Path missverstanden. |
| `S006-REQ-008` | Springmaster stellt einen kanonischen Patch-Artifact-Producer bereit, der Candidate-Diff, Scope, new/modified/deleted, Before-Hashes, Artifact-ID, Manifest und ZIP-Layout selbst deterministisch erzeugt und danach den eigenen Preflight aufruft. |
| `S006-REQ-009` | Patch-Artifact-Producer und Validator/Preflight verwenden dasselbe interne Patch Artifact Model oder eine nachweislich gemeinsame Vertragsquelle; Produzenten müssen das Format nicht aus Validatorfehlern rückwärts ableiten. |
| `S006-REQ-010` | Git HEAD, Foundation-/Tooling-Version, PLATFORM_STATE_PATCH und ausgelieferter Patch-/Toolingstand sind aus versionierten Quellen eindeutig rekonstruierbar; konkurrierende Latest-Wahrheiten werden beseitigt. |
| `S006-REQ-011` | Qualification ist progressiv und risikobasiert: Syntax/Static -> betroffene Tests -> Slice -> Contract/Integration -> Full Qualification an definierter Integrations-/Release-Grenze. |
| `S006-REQ-012` | Change-/Risikoklasse und konkrete Authority bestimmen die erforderliche Qualification-Breite; historische Tooling-Kopplung allein rechtfertigt keine unnötig breite frühe Prüfung. |
| `S006-REQ-013` | Success-Evidence bleibt kompakt; Fehlerdiagnostik enthält nur relevante Zustände und referenziert unveränderliche historische Evidence statt Repository-, Export-, Patcharchiv- oder Buildbestände pauschal zu kopieren. |
| `S006-REQ-014` | patches/work enthält nur den aktuellen Arbeits-/Diagnoselauf; dauerhafte Lauf-Evidence liegt unter patches/logs; Diagnose-ZIPs nehmen keine früheren Diagnose-ZIPs rekursiv auf. |
| `S006-REQ-015` | Erwartbare Blocker liefern mindestens reasonCode, Kategorie PRODUCT|TOOLING|ENVIRONMENT|GOVERNANCE, Recoverability, safeNextAction und Maintenance-Eignung; unbekannte unsichere Zustände dürfen weiter fail-closed bleiben. |
| `S006-REQ-016` | Gemeinsame Runner-Semantik modelliert required success, expected failure, Capture, Phase, Diagnose und Rollback-Evidence; erwartete Negativtests dürfen nicht durch globale ERR-Traps als Fehler klassifiziert werden. |
| `S006-REQ-017` | FAILED_STAGE beziehungsweise Phase wird unmittelbar vor der tatsächlich risikobehafteten Operation gesetzt; Follow/Watch-Fehler dürfen die autoritative Result-/Diagnostic-Phase nicht überspringen oder maskieren. |
| `S006-REQ-018` | Git-/Scope-Gates vergleichen semantische Source-Diff-Mengen statt positionsabhängiger sortierter Arrays und unterscheiden Source-Änderungen von definierten Laufartefakten; die Prüfung ist Locale-unabhängig. |
| `S006-REQ-019` | Normale Delivery-/Qualification-Abläufe bleiben terminalschonend und mit einer einzigen gestarteten Benutzerinteraktion ausführbar; notwendige Human-Trust-Entscheidungen dürfen innerhalb dieses laufenden Ablaufs explizit bleiben. |
| `S006-REQ-020` | Ein gemanagtes Projekt ist nach normalem Git-Checkout mit den im Projekt versionierten Tooling-Komponenten selbstständig arbeitsfähig; Springmaster-, Personnel- oder andere Nachbarcheckouts sind keine Runtime-/Engineering-Voraussetzung. |
| `S006-REQ-021` | .env.example bleibt getrackte secret-freie Defaultvorlage; .env bleibt lokaler Override. Ein Sync ergänzt/aktualisiert nur definierte Keys, erhält lokale/unknown Keys und Secrets und trackt .env niemals automatisch. |
| `S006-REQ-022` | DBTool besitzt explizite, validierte lokale Adminmodi wie sudo, socket und password sowie einen generischen DEV-Bootstrap für DB/User/Grant/Schema; destruktive Aktionen bleiben separat autorisiert. |
| `S006-REQ-023` | Der generische DB-Qualifikationspfad bleibt Fresh Schema -> Liquibase apply -> Hibernate validate -> Persistence/Integration Tests; Hibernate update ist keine stillschweigende Schema-Reparatur. |
| `S006-REQ-024` | Build, Packaging und Remote Deployment besitzen getrennte Side-Effect-Grenzen; ein Qualification-Build kann Deployment explizit deaktivieren, ohne lokale Secrets oder persistente Projektkonfiguration zu überschreiben. |
| `S006-REQ-025` | Tooling-/Managed-Project-Releasequalification enthält Fresh-Checkout-Fälle ohne .env sowie mit lokalem .env-Bootstrap; lokale Secrets bleiben erhalten und der Checkout benötigt keinen Springmaster-Nachbarcheckout. |
| `S006-REQ-026` | Personnel dient als Real-World-Canary: Ein realer Produktfehler/Change wird weiterhin korrekt gefunden, aber nicht-fachliche Interaktionen, wiederholte Teststarts, Shadow-/Evidence-Größe und Recovery-Schritte werden gegenüber dem aktuellen P3-Muster messbar reduziert. |
| `S006-REQ-027` | Der aktuelle ZBM-Blocker wird zuerst forensisch als PRODUCT, TOOLING, ENVIRONMENT oder GOVERNANCE klassifiziert, dann über Normal- oder Recovery-Pfad geschlossen und durch mindestens einen anschließenden realen Entwicklungschange validiert. |
| `S006-REQ-028` | Portable Managed Development umfasst Project Adapter sowie install/update/repair/rollback des projekt-eigenen Toolingstands; projektbezogene Runs, Worktrees und Artefakte bleiben getrennt. |
| `S006-REQ-029` | Cross-Project-Mutationen, automatische Pushes, direkte Agent-Mutation der Integrationsbranch und falsche PASS-/Qualification-Aussagen bleiben verboten; Vergleichsprojekte sind Evidence-Quelle, keine Runtime-Abhängigkeit. |
| `S006-REQ-030` | SPRINGMASTER_CONFORMANT und GWC_CONFORMANT bleiben getrennte Aussagen; ein Managed Project kann die für seinen GWC-Usecase benötigte Capability-Menge explizit deklarieren und qualifizieren. |
| `S006-REQ-031` | Der GWC-Conformance-Nachweis startet report-only mit positiver/negativer Evidence und darf erst nach bestehender Gate-Promotion-Governance strict werden; P0/P1 darf dadurch nicht blockiert werden. |
| `S006-REQ-032` | Code, Tooling, Contracts, ADRs/Governance, Roadmap, Sprintstatus, Completion Evidence und finale Version Truth treffen bei Sprint-Closure dieselbe Aussage; temporäre Dokumente und Deferrals sind explizit disponiert. |

## Qualitätsanforderungen

- Keine Abschwächung von Safety Invariants, Human-Accept, Baseline-/Scope-Schutz, Secret-Schutz oder Cross-Project-Mutationsgrenzen.
- Keine neue zweite Control Plane nur zur Umgehung der bestehenden Control Plane.
- Neue Producer, Scaffolds und Runner müssen deterministisch, lokal und mit möglichst wenigen externen Abhängigkeiten funktionieren.
- Jede neue harte Gate-Regel benennt Authority, reales Risiko, erforderliche Phase und Recovery-/Remediation-Pfad.
- Metriken dienen der Developer-Experience-Verbesserung und dürfen nicht selbst zu neuer Bürokratie werden.
- Reale Canaries unterscheiden Produktfehler, Toolingfehler, Environmentfehler und Governancefehler.

## In Scope

- Enabling-Governance- und Recovery-Contracts;
- kanonischer Patch Artifact Producer und gemeinsame Patch-Model-Quelle;
- vereinheitlichte Patch-/Tooling-State-Wahrheit;
- Engineering-/Candidate- versus Delivery-/Acceptance-Workflow;
- gemeinsame Runner-/Expected-Failure-/Phase-/Diagnose-Semantik;
- semantische Source-Diff-Gates;
- progressive Qualification und proportionale Evidence;
- `patches/work`-/`patches/logs`-Lifecycle;
- projekt-eigene Tooling-Distribution und Fresh-Checkout-Qualification;
- `.env.example`/`.env`-Sync, DBTool-Adminmodi, DEV-Bootstrap und Build-/Deploy-Side-Effects, soweit generisch;
- Personnel- und ZBM-Feldcanaries;
- Portable Managed Development Foundation;
- report-only GWC-Conformance-Profil, sofern P0/P1 nicht verzögert werden.

## Out of Scope

- Abschaffung des Patchsystems oder der Human-Accept-Grenze;
- automatische Pushes oder unkontrollierte Main-/Target-Mutation;
- projektspezifische Personnel- oder ZBM-Fachlogik in Springmaster;
- Pflicht zu Springmaster-, Personnel- oder ZBM-Nachbarcheckouts in Managed Projects;
- Big-Bang-Migration aller historischen Patcharchive oder alten Projekttoolings;
- neue generische Fachframeworks für Temporalität, History, Workspace oder GWC-Runtime;
- automatische Strict-Promotion neuer Gates;
- GWC-Conformance als P0-Blocker;
- ungeprüfte Übernahme lokaler Secrets oder Hostkonfiguration in Templates/Projekte.

## Constraints und Abhängigkeiten

- ADR-0020 ist Authority für Enabling Governance und Recovery; bestehende akzeptierte Safety-/Architecture-ADRs bleiben wirksam.
- Änderungen an Tooling und Governance werden zuerst in Springmaster qualifiziert und erst danach kontrolliert als versionierter Stand an Projekte verteilt.
- Reale Personnel-/ZBM-Checkouts dienen als Field Evidence und Canary-Ziele; sie sind keine generische Runtime-Abhängigkeit von Springmaster.
- Destruktive DB-Aktionen, Target Apply, Accept und Push bleiben separat autorisierte Grenzen.
- Ein nachgewiesener Konflikt mit einer akzeptierten ADR ist `stop-and-replan`, nicht Anlass für stillen Bypass.

## Risiken

- Vereinfachung kann versehentlich Safety Invariants abschwächen.
- Ein Maintenance-Modus kann selbst zu einer zu komplexen zweiten Control Plane werden.
- Ein Artifact Builder kann bei getrenntem Datenmodell erneut vom Validator driften.
- Fresh-Checkout- und Environment-Sync können lokale Secrets gefährden, wenn die Ownership falsch modelliert wird.
- Umfangreiche Cross-Project-Qualification kann erneut zu operativer Kopplung führen.
- GWC-Conformance kann zu früh als weiteres Pflichtgate verstanden werden.

## Definition of Ready

- [x] Post-S005-Baseline ist sauber, qualifiziert und archiviert.
- [x] Reibungsproblem und Leitprinzip sind bestätigt.
- [x] Personnel-P3-Evidence liegt als Feldinput vor und wird nicht mit Toolingfehlern vermischt.
- [x] ZBM-Handoff liefert konkrete generische Tooling-/Portabilitätsanforderungen.
- [x] Safety Invariants und Nichtziele sind benannt.
- [x] P0/P1/P2-Priorität ist bestimmt.
- [x] Real-World-Canaries für Personnel und ZBM sind formulierbar.
- [x] Erwartete Tooling-/Update-/Foundation-Versionwirkung ist grundsätzlich bestimmbar.

## Definition of Done

- [ ] Alle `S006-REQ-001` bis `S006-REQ-032` sind auf akzeptierte Evidence gemappt und bewertet.
- [ ] Ein kanonischer Patch Artifact Producer erzeugt ohne manuelle Manifest-/ZIP-Rekonstruktion ein vom eigenen Preflight akzeptiertes Artefakt.
- [ ] Patch-/Tooling-State ist in einem Fresh Checkout eindeutig aus versionierten Quellen rekonstruierbar.
- [ ] Ein absichtlich defektes Springmaster-Tool kann über den Maintenance-/Recovery-Pfad repariert und vollständig qualifiziert werden, ohne sich selbst als einzige Reparaturvoraussetzung zu benötigen.
- [ ] Ein normaler lokaler Engineering-Change benötigt vor der Delivery-Grenze kein Patchartefakt.
- [ ] Progressive Qualification und proportionale Evidence besitzen positive, negative und Tool-Error-/Recovery-Fixtures.
- [ ] `patches/work` enthält nur aktuellen Laufzustand; dauerhafte Evidence liegt unter `patches/logs`.
- [ ] Runner behandeln expected failure korrekt und melden die tatsächlich fehlgeschlagene Phase.
- [ ] Source-Diff-Gates sind semantisch, artefaktbewusst und Locale-unabhängig.
- [ ] Fresh Checkout ohne `.env` und mit lokalem `.env`-Bootstrap ist qualifiziert, ohne Secrets zu löschen oder einen Springmaster-Nachbarcheckout zu benötigen.
- [ ] DBTool-Adminmodus, Fresh-Schema-Liquibase-Hibernate-Validate und Build-/Deploy-Side-Effects sind generisch qualifiziert.
- [ ] Personnel-Canary findet weiterhin reale Produktfehler und reduziert nicht-fachliche Reibung messbar.
- [ ] ZBM-Blocker ist klassifiziert/geschlossen und ein anschließender realer Change läuft über den neuen Happy Path.
- [ ] Managed-Project-Portability basiert auf projekt-eigenem versioniertem Tooling mit install/update/repair/rollback.
- [ ] GWC-Conformance ist mindestens report-only qualifiziert oder kontrolliert deferriert, ohne falsche Reifeaussage.
- [ ] Keine unautorisierte Target-Mutation, kein Push, keine falsche PASS-/Qualification-Aussage und keine abgeschwächte Safety Invariant.
- [ ] Trusted-Host-Qualification, Version Truth, Completion Report, Index und Archivzustand sind konsistent geschlossen.

Sprint 006 ist nur qualifiziert, wenn mindestens folgende Aussagen durch reale Evidence belegt sind:

```text
STANDARD_PATH_SIMPLER_THAN_LOCAL_WORKAROUND=true
NORMAL_DEVELOPMENT_PATCH_HOT_PATH_REQUIRED=false
TOOL_SELF_REPAIR_WITHOUT_SELF_DEPENDENCY=true
MAINTENANCE_RECOVERY_PATH_QUALIFIED=true
CANONICAL_PATCH_ARTIFACT_PRODUCER=PASS
PATCH_ARTIFACT_MODEL_SHARED=PASS
PATCH_STATE_TRUTH=UNIFIED
RUNNER_EXPECTED_FAILURE_SEMANTICS=PASS
SOURCE_DIFF_GATE=PASS_LOCALE_INDEPENDENT
PROGRESSIVE_QUALIFICATION=true
EVIDENCE_IS_PROPORTIONAL=true
PATCHES_WORK_CURRENT_RUN_ONLY=true
BLOCKING_STATE_HAS_RECOVERY_PATH=true
FRESH_CHECKOUT_NO_ENV=PASS
FRESH_CHECKOUT_WITH_ENV=PASS
PROJECT_OWNED_TOOLING_AUTONOMY=PASS
FRESH_SCHEMA_LIQUIBASE_HIBERNATE_VALIDATE=PASS
BUILD_DEPLOY_SIDE_EFFECT_BOUNDARY=PASS
PERSONNEL_RECOVERY_CANARY=PASS
ZBM_RECOVERY_CANARY=PASS
MANAGED_PROJECT_PORTABILITY_FOUNDATION=PASS
SECURITY_INVARIANTS_WEAKENED=0
UNAUTHORIZED_TARGET_MUTATIONS=0
UNINTENDED_PUSHES=0
FALSE_QUALIFICATION_CLAIMS=0
SPRINT006_RESULT=DOD_QUALIFIED
```

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Governance-/Tooling-Reibungsinventur und Recovery Contract | REQ-001..005 | Regelklassen, Feldbaseline, Recovery Contract und Self-Repair-Canary definiert | Governance/Contracts + Baseline Report | Springmaster | in-progress |
| M-002 | Kanonischer Producer, State Truth, Runner und Source-Diff | REQ-008..010, REQ-014..018 | Producer->Preflight PASS; State eindeutig; Runner/Scope-Fixtures PASS | Tooling Code + IT/Evidence | Springmaster | planned |
| M-003 | Engineering-/Delivery-Trennung und Progressive Qualification | REQ-006..007, REQ-011..013, REQ-019 | normaler Change ohne Vorab-cpatch; Delivery weiter fail-closed | Tooling/Governance + Regression | Springmaster | planned |
| M-004 | DEV-/Build-Portabilität und projekt-eigenes Tooling | REQ-020..025, REQ-028..029 | Fresh Checkout, Env/DB/Build und project-owned tooling qualifiziert | Managed-Project Fixtures + Host Tests | Springmaster | planned |
| M-005 | Personnel- und ZBM-Feldqualification | REQ-026..027 | zwei reale Canaries; Produktfehler weiter sichtbar; Reibung reduziert | Field Qualification Evidence | Trusted Host | planned |
| M-006 | Portable Managed Development Foundation | REQ-028..029, REQ-032 | Project Adapter + install/update/repair/rollback und isolierte Runs | Managed-Project Qualification | Springmaster | planned |
| M-007 | GWC Conformance Profile | REQ-030..031 | report-only `GWC_CONFORMANT`-Nachweis oder dokumentierte P2-Deferral | Contract/Gate Fixtures | Springmaster | planned |

## SemVer-Auswirkung

Erwarteter Sprint-Impact:

```text
PLATFORM_CORE_VERSION=none
PLATFORM_TOOLING_VERSION=minor
PLATFORM_TEMPLATE_VERSION=none
PLATFORM_DEMO_VERSION=none
PLATFORM_UPDATE_VERSION=minor
PLATFORM_VERSION=minor
```

Die konkreten Werte und `PLATFORM_STATE_PATCH` werden erst aus den tatsächlich akzeptierten S006-Schnitten gemäß Version Policy geschlossen. Die reine Sprintaktivierung verursacht keinen pauschalen Komponenten-Bump.

## Stop- und Abbruchkriterien

`stop-and-replan`, wenn mindestens eines eintritt:

1. eine notwendige Vereinfachung würde eine akzeptierte Safety-/Architecture-ADR materiell brechen;
2. ein Recovery-Pfad erfordert unkontrollierte Main-, Target- oder Push-Mutation;
3. der Artifact Producer kann nicht dasselbe Vertragsmodell wie der Validator nutzen und würde eine zweite Formatwahrheit erzeugen;
4. projekt-autonomes Tooling wäre nur mit einer permanenten externen Springmaster-Abhängigkeit möglich;
5. Environment-/Bootstrap-Automation könnte lokale Secrets nicht zuverlässig erhalten;
6. eine Cross-Project-Canary müsste ein nicht autorisiertes Ziel mutieren;
7. P2-GWC-Arbeit blockiert P0/P1;
8. die Developer-Experience-Metriken zeigen keine Vereinfachung trotz zusätzlicher Mechanismen.

Normale Produkt-, Tooling- oder Fixture-Fehler innerhalb eines autorisierten Slices sind Repair-Signale und kein automatischer Sprintabbruch.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-09-01 | - | planned | Post-S005-Problemraum aus Personnel-/ZBM-Feldfeedback und Enabling-Governance-Ziel abgeleitet. |
| 2026-09-01 | planned | active | Auftrag, Prioritäten, DoR/DoD, Nichtziele und Stop-Kriterien für die Recovery-/Simplification-Stufe bestätigt. |

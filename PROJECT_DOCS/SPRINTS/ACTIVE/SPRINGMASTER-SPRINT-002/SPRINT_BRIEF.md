---
documentId: SPRINGMASTER-SPRINT-002-BRIEF
title: Codex Calibration and Business Partner End-to-End Pilot – Sprint Brief
documentType: sprint-brief
status: active
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-28
validFrom: 2026-07-28
lastReviewedAt: 2026-07-28
reviewBy: 2026-08-21
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-002
sprintStart: 2026-07-28
targetCompletion: 2026-08-21
---

# Codex Calibration and Business Partner End-to-End Pilot – Sprint Brief

## Sprintziel

Springmaster soll den akzeptierten Zustand `PROJECT_READY` kontrolliert in reale Codex-Kalibrierung überführen und anschließend die Business-Partner-Dummy-Anwendung als nachvollziehbaren End-to-End-Pilot qualifizieren. Der Sprint prüft zuerst die Sicherheits-, Scope-, Evidence- und Ergebnisqualität des Agenten. Eine schreibende Pilotfreigabe oder End-to-End-Ausführung erfolgt erst nach den jeweils ausdrücklich definierten Promotionskriterien.

Der Sprint ist erfolgreich, wenn Springmaster belastbar entscheiden kann, ob Codex für begrenzte lokale Springmaster-Aufgaben sicher und effizient eingesetzt werden darf und ob die Kette vom Fachkonzept bis zu einer disponiblen GWC-Anwendung deterministisch, traceable und wiederholbar funktioniert.

## Strategischer Bezug

- `GOAL-001`: Kalibrierung und Pilot qualifizieren das zentrale Tooling und den Systemkern-Entwicklungsprozess.
- `GOAL-003`: Die generierte Anwendung belegt einen reproduzierbaren, extern materialisierten Projektstart mit definierten Extension Points.
- `GOAL-004`: Fachkonzept, Intent, Generated-Slice-Spec, IR, UI-Spec und GWC-Manifest bilden eine explizite Contract-Kette.
- `GOAL-005`: Sicherheitsgrenzen, Tests, Evidence, Repeatability und kontrollierte Promotion werden als verbindliche Qualitätskriterien geprüft.
- `GOAL-002`: Auswirkungen auf gemanagte Projekte werden bewertet; reale Zielprojektmutation bleibt außerhalb dieses Sprints.

Kanonische Zielquelle ist `PROJECT_DOCS/GOVERNANCE/SPRINGMASTER_PROJECT_GOALS.md`.

## Ausgangslage und Baseline

Kanonische Baseline beim Sprintstart:

- Git-HEAD des geprüften Full-Exports: `ac090009742845b466f306cd240f0c61c6d935a6`;
- Branch: `main`, Exportstatus: sauber;
- Export-SHA-256: `869db646bac5d59960cafdafdc07ce9471848f64b81181fe38f805f8f9149885`;
- File-Manifest-SHA-256: `b85a72c49c2e2ce62ad0230c5590830e769579746a0f085a9e9e995367da6a53`;
- Plattformversion: `0.21.1-foundation`;
- Toolingversion: `0.11.1`;
- State Patch: `000187_springmaster_operator_log_history_compatibility`;
- akzeptierte Pilotentscheidung: ADR-0015;
- Readiness: `PROJECT_READY`;
- nächster erlaubter Zustand: `CODEX_CALIBRATION`;
- schreibender Codex-Einsatz: nicht autorisiert;
- Business-Partner-Fachkonzept und Acceptance Contract: vorhanden und eingefroren;
- Patch- und Prozessausführung: Cocondo Patch Toolkit 1.1.2 mit getrenntem Dry-run und Accept sowie activation-contract-basierter Version Closure.

Der frühere D3-Kalibrierungskandidat ist nicht Teil der Repositoryhistorie und muss gegen diese Baseline neu erzeugt werden.

## Problemstellung und Stakeholder

Governance, Harness und Referenzinput sind vorhanden, aber der reale Nachweis fehlt, dass Codex die geschlossenen Aufgaben-, Scope-, Host- und Evidence-Grenzen tatsächlich einhält und fachlich brauchbare Ergebnisse liefert. Ohne kontrollierte Kalibrierung wäre jede schreibende Nutzung eine unbelegte Promotion. Ohne End-to-End-Pilot bliebe zudem offen, ob die vorhandenen Verträge vom Fachkonzept bis zur GWC-Anwendung konsistent zusammenspielen.

Stakeholder sind Springmaster-Maintainer, Betreiber der lokalen Entwicklungsumgebung, Reviewer von Architektur und Sicherheit sowie spätere Nutzer von Project-New, GWC-Erzeugung und gemanagten Projekten.

## Anforderungen

| ID | Anforderung |
|---|---|
| `CAP-REQ-001` | Die allgemeinen Springmaster-Ziele und der aktive Sprintvertrag MÜSSEN als kanonische, indexierte Dokumente vorliegen. |
| `CAP-REQ-002` | Ein immutable Kalibrierungs-Task-Pack MUSS einen read-only Grenztest, einen negativen Boundary-Probe und zwei kleine implementierende Kalibrierungsaufgaben mit unabhängigen Oracles enthalten. |
| `CAP-REQ-003` | Jede Kalibrierung MUSS gegen einen exakten Commit, eine geschlossene Pfadmenge, definierte Capabilities, Größenlimits, Qualifikationskommandos und unveränderliche Evidence gebunden sein. |
| `CAP-REQ-004` | `PILOT_WRITE_READY` DARF nur durch eine separate, evidence-basierte Entscheidung nach zwei akzeptierten Kalibrierungsaufgaben und bestandenen Runtime-Grenzproben erreicht werden. |
| `CAP-REQ-005` | Der Business-Partner-Pilot MUSS die Kette Fachkonzept, canonical intent, Generated-Slice-Spec, IR, Application UI Spec, GWC Implementation Manifest und generierte Anwendung nachvollziehbar abbilden. |
| `CAP-REQ-006` | Die generierte Anwendung MUSS außerhalb des Springmaster-Checkouts in einem disponiblen Zielverzeichnis entstehen; GWC-Quellen und gemanagte Projekte bleiben read-only. |
| `CAP-REQ-007` | Build, Runtime, API, Validierung, Fehlervertrag, Persistenzentscheidung, Security-Klassifikation, UI-Verhalten und Extension Points MÜSSEN durch angemessene Acceptance-Evidence bewertet werden. |
| `CAP-REQ-008` | Drei saubere deterministische Wiederholungen und eine kontrollierte Fachkonzeptänderung V1.1 MÜSSEN Ergebnisstabilität, Traceability und den Erhalt manueller Extension Points belegen. |
| `CAP-REQ-009` | Der Sprint MUSS Safety, Qualität, Effizienz, technische Schulden und eine begründete Rollout- oder Stop-Entscheidung im Completion Report ausweisen. |

## Qualitätsanforderungen

- Kein Codex-Lauf darf Main, andere Repositories, Downloads, Operator-Home, Run-/Artifact-Roots, Git-Metadaten oder gemanagte Projekte außerhalb des Taskvertrags verändern.
- Task, Invocation, Worktree, Commit, Modell, Sandbox, Exitstatus, Diff, Qualifikation und Evidence müssen eindeutig korrelierbar sein.
- Oracles werden vor dem Lauf festgelegt und nicht aus dem Agentenergebnis abgeleitet.
- Tool Errors, Contract Findings, fachliche Abweichungen und bewusste Deferrals werden getrennt berichtet.
- Dry-run, Review und Accept bleiben getrennte Operatorentscheidungen; Push ist nicht Bestandteil dieses Sprints.
- Jede erzeugte Spezifikation besitzt stabile IDs und Rückverweise bis zum Fachkonzept.
- Wiederholungen verwenden identische Eingaben und qualifizierte Umgebungsparameter; nichtdeterministische Unterschiede werden erklärt oder blockieren den Abschluss.
- Neue dauerhafte Regeln werden in ADRs, Governance, Standards oder Contracts promoviert und nicht nur im Sprintstatus festgehalten.

## In Scope

- dauerhafte Persistenz der allgemeinen Projektziele und des aktiven Sprintvertrags;
- Rekonstruktion des D3-Kalibrierungs-Task-Packs gegen die aktuelle Baseline;
- read-only und negative Runtime-Boundary-Probes;
- zwei kleine, begrenzte Codex-Kalibrierungsaufgaben im Springmaster-Repository;
- separate Bewertung der Promotion zu `PILOT_WRITE_READY`;
- End-to-End-Transformation des eingefrorenen Business-Partner-Fachkonzepts;
- Erzeugung und Qualifikation einer disponiblen Anwendung außerhalb des Springmaster-Checkouts;
- drei deterministische Wiederholungen und eine kontrollierte V1.1-Fachkonzeptänderung;
- Abschlussbewertung, technische Schulden, SemVer- und Rolloutempfehlung.

## Out of Scope

- automatische oder unbegrenzte Codex-Schreibfreigabe;
- Push, automatische Integration in Main oder unbeaufsichtigte Hintergrundentwicklung;
- Mutation der GWC-Quellen, des ZBM-Projekts oder anderer gemanagter Projekte;
- allgemeine Agentenfreigabe für Project-New oder Zielprojekte;
- Canonicalization des Catalog-demo-Slices;
- neue produktive Fachlogik im Springmaster-Core;
- Einführung neuer Generator-Frameworks oder externer Abhängigkeiten ohne eigene Entscheidung;
- Release oder Distribution einer erzeugten Business-Partner-Anwendung als Produkt.

## Constraints und Abhängigkeiten

- ADR-0015 und AI Agent Development Governance bleiben bindend.
- `PROJECT_READY` erlaubt Kalibrierung, aber keine schreibende Pilotaufgabe ohne explizite Task- und Promotionsevidence.
- Das Cocondo Patch Toolkit bleibt die kanonische Integrations- und Commitgrenze.
- Externe Worktree-, Run- und Artifact-Roots müssen vorprovisioniert, getrennt, schreibbar und nicht symlinkbasiert sein.
- Das Business-Partner-Fachkonzept bleibt für die Baseline-Läufe unverändert; V1.1 wird als separate kontrollierte Eingabe geführt.
- GWC-Export und vorhandene IDM-/Personnel-Beispiele sind read-only Referenzen.
- Ein fehlender realer Codex- oder Runtime-Nachweis darf nicht durch statische Fixture-Ergebnisse ersetzt werden.

## Risiken

| Risiko | Wirkung | Behandlung |
|---|---|---|
| Boundary wird nur statisch, nicht real geprüft | falsche Sicherheitsfreigabe | verpflichtende Runtime-Denial-Probes vor `PILOT_WRITE_READY` |
| Task oder Oracle ist nachträglich angepasst | selbstbestätigende Evidence | immutable Hashbindung und unabhängige Vorab-Review |
| End-to-End-Scope wird zu groß | unklare Fehlerursache | staged Contracts und qualifizierte Zwischenprodukte |
| Generator überschreibt Extension Points | Verlust manueller Arbeit | Besitzklassen, Re-Generation-Test und V1.1-Evolution |
| Ergebnisse sind nicht deterministisch | nicht reproduzierbare Lieferung | drei Clean-Runs mit Hash- und Differenzanalyse |
| Pilot mutiert Referenz- oder Zielprojekte | Scope- und Governance-Verstoß | externe disposable Roots und read-only Guards |
| gute Demo wird als allgemeine Reife fehlinterpretiert | verfrühter Rollout | gesonderte Abschluss- und Generalisierungsentscheidung |

## Definition of Ready

- [x] ADR-0015 ist akzeptiert und der Zustand `PROJECT_READY` ist belegt.
- [x] Agent Task Contract V2, Harness, Process Operations und Operator Command Effect Contract sind vorhanden.
- [x] Das Business-Partner-Fachkonzept und sein Acceptance Contract sind eingefroren.
- [x] Die aktuelle Git-, Export-, Versions- und Toolingbaseline ist dokumentiert.
- [x] Allgemeine Projektziele und Sprintscope sind als kanonische Quellen definiert.
- [x] Mutationsverbote, externe Roots, Promotionen und Stopbedingungen sind benannt.
- [ ] Das gegen die aktuelle Baseline neu erzeugte Kalibrierungs-Task-Pack und seine Oracles sind unabhängig reviewed.
- [ ] Die konkrete lokale Codex-Umgebung und alle Runtime-Denial-Probes sind preflight-ready.

## Definition of Done

- [ ] `CAP-REQ-001` bis `CAP-REQ-009` sind jeweils erfüllt, bewusst deferiert oder mit Blocker bewertet.
- [ ] Die fünf allgemeinen Projektziele sind als aktive kanonische Zielquelle indexiert und werden vom Sprint referenziert.
- [ ] Der aktive Sprint besitzt Brief, Solution Plan, genau eine Statusquelle und einen vorbereiteten Completion Report mit konsistenter Milestone-Abdeckung.
- [ ] Das immutable Kalibrierungs-Task-Pack enthält read-only Analyse, negativen Boundary-Probe und zwei kleine implementierende Aufgaben mit vorab festgelegten Oracles.
- [ ] Alle Host-, Pfad-, Scope-, Git-, Sandbox-, Größen-, Capability- und Evidence-Grenzen wurden real geprüft; unerlaubte Mutation wurde verhindert und nachgewiesen.
- [ ] Zwei implementierende Kalibrierungsaufgaben wurden fachlich und technisch unabhängig akzeptiert oder `PILOT_WRITE_READY` wurde ausdrücklich blockiert.
- [ ] Eine separate Entscheidung hat `PILOT_WRITE_READY` evidenzbasiert promoviert oder den Abbruch vor schreibender Pilotnutzung dokumentiert.
- [ ] Die Business-Partner-Kette vom Fachkonzept bis zur disponiblen GWC-Anwendung ist vollständig traceable und ohne Mutation von GWC oder gemanagten Projekten erzeugt.
- [ ] Die generierte Anwendung besteht die definierten Build-, Runtime-, API-, Validierungs-, Fehler-, Persistenz-, Security- und UI-Acceptance-Kriterien oder weist begründete Deferrals aus.
- [ ] Drei Clean-Runs sind deterministisch vergleichbar; Abweichungen sind erklärt und akzeptiert oder blockieren die Qualification.
- [ ] Die V1.1-Fachkonzeptänderung wurde kontrolliert verarbeitet, ohne geschützte manuelle Extension Points zu überschreiben.
- [ ] Alle Patches und Commits wurden über den kanonischen Dry-run-/Review-/Accept-Flow qualifiziert; es erfolgten kein automatischer Accept, kein Push und keine unerlaubte Zielmutation.
- [ ] Completion Report, technische Schulden, temporäre Dokumentdisposition, SemVer-Auswirkung und Rollout-, Generalisierungs- oder Stopentscheidung sind vollständig.

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Projektziele und aktiver Sprintvertrag sind kanonisch persistiert. | CAP-REQ-001 | Documentation Gate und Sprint Gate ohne neue Findings; alle sechs Dokumente indexiert. | Gate-Reports und Repository-Diff | springmaster-maintainers | completed |
| M-002 | Kalibrierungs-Task-Pack und unabhängige Oracles sind gegen die aktuelle Baseline eingefroren. | CAP-REQ-002, CAP-REQ-003 | Schema, Hashbindung, Scope, Limits und positive/negative Oracles reviewed. | Task-, Oracle- und Preflight-Evidence | springmaster-maintainers | planned |
| M-003 | Reale Kalibrierung und Write-Readiness-Entscheidung sind abgeschlossen. | CAP-REQ-003, CAP-REQ-004 | Boundary-Probes und zwei Aufgaben qualifiziert; separate Promotion oder Blockerentscheidung. | Invocation-, Run-, Diff-, Qualification- und Promotion-Evidence | springmaster-maintainers | planned |
| M-004 | Business-Partner-End-to-End-Pilot ist traceable und disponibel erzeugt. | CAP-REQ-005, CAP-REQ-006, CAP-REQ-007 | Staged Contracts und generierte Anwendung bestehen definierte Acceptance-Kriterien. | Contract-Kette, Build-, Runtime-, API- und UI-Evidence | springmaster-maintainers | planned |
| M-005 | Repeatability, V1.1-Evolution und Sprintabschluss sind qualifiziert. | CAP-REQ-008, CAP-REQ-009 | Drei Clean-Runs, Evolutionstest, Debt-/Effizienzbewertung und Abschlussentscheidung liegen vor. | Vergleichsreports und finaler Completion Report | springmaster-maintainers | planned |

## SemVer-Auswirkung

Erwartete Auswirkung: `minor`, falls der Sprint neue freigegebene Tooling-, Generator- oder Pilotfähigkeiten aktiviert. Dieser Initialisierungspatch erhöht keine Version vorweg. Die tatsächliche Komponenten- und Foundation-Version wird erst bei qualifizierter Release Closure anhand der akzeptierten Ergebnisse entschieden.

## Stop- und Abbruchkriterien

Der Sprint stoppt und wird neu geplant oder abgebrochen, wenn:

- Codex außerhalb des erlaubten Worktrees oder Taskscopes schreibt;
- eine Host-, Git-, Sandbox- oder Evidence-Grenze nicht fail-closed wirkt;
- Task, Oracle oder Baseline nach Start nicht mehr unverändert nachweisbar sind;
- der Patch-/Commitpfad umgangen oder ein automatischer Accept/Push ausgelöst wird;
- GWC, ZBM oder ein anderes gemanagtes Projekt mutiert wird;
- zwei Kalibrierungsaufgaben nicht unabhängig qualifiziert werden können;
- die End-to-End-Kette keine eindeutige Traceability oder sichere Extension-Point-Semantik erreicht;
- wesentliche Nichtdeterministik nach drei Clean-Runs ungeklärt bleibt.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | active | Aktiver Sprint für reale Codex-Kalibrierung und den Business-Partner-End-to-End-Pilot angelegt. |

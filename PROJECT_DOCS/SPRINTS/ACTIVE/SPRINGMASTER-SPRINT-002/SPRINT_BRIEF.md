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
lastReviewedAt: 2026-08-14
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

Der Codex-Cutover-Anteil von Sprint 002 ist abgeschlossen: Springmaster ist nach realer Host-Qualification, A003-Kalibrierung, zwei unabhängig akzeptierten Implementierungsaufgaben, live verifizierter Confinement-Evidence und separater Promotion im Zustand `PILOT_WRITE_READY`/`PROMOTED`. Kontrollierte schreibende Codex-Pilot-Tasks sind damit gemäß Task Contract und Harness autorisiert; direkte Integration, automatischer Accept, Push oder Zielprojektmutation bleiben verboten.

Der verbleibende Sprintfokus ist M-004/M-005: die Business-Partner-Dummy-Anwendung als nachvollziehbaren End-to-End-Pilot qualifizieren, anschließend Repeatability und V1.1-Evolution belegen und den Sprint evidence-basiert schließen.

Der Sprint ist erfolgreich, wenn Springmaster belastbar zeigt, dass die Kette vom Fachkonzept bis zu einer disponiblen GWC-Anwendung deterministisch, traceable und wiederholbar funktioniert und daraus eine begründete Rollout-, Generalisierungs- oder Stopentscheidung ableitet.

## Strategischer Bezug

- `GOAL-001`: Kalibrierung und Pilot qualifizieren das zentrale Tooling und den Systemkern-Entwicklungsprozess.
- `GOAL-003`: Die generierte Anwendung belegt einen reproduzierbaren, extern materialisierten Projektstart mit definierten Extension Points.
- `GOAL-004`: Fachkonzept, Intent, Generated-Slice-Spec, IR, UI-Spec und GWC-Manifest bilden eine explizite Contract-Kette.
- `GOAL-005`: Sicherheitsgrenzen, Tests, Evidence, Repeatability und kontrollierte Promotion werden als verbindliche Qualitätskriterien geprüft.
- `GOAL-002`: Auswirkungen auf gemanagte Projekte werden bewertet; reale Zielprojektmutation bleibt außerhalb dieses Sprints.

Kanonische Zielquelle ist `PROJECT_DOCS/GOVERNANCE/SPRINGMASTER_PROJECT_GOALS.md`.

## Ausgangslage und Baseline

### Sprintinitialisierungs-Baseline (historisch)

Der Sprint wurde auf dem Full-Export-HEAD `c5c5846176d92c34b19b7a7827d7264c1923805f` mit Platform `0.21.1-foundation`, Tooling `0.11.3`, State Patch `000196_springmaster_directory_governance_runtime_audit_closure`, Patch Toolkit `1.1.2` und formalem Lifecycle `PROJECT_READY` gestartet. Die Versuche `000197` bis `000200` wurden ausschließlich als Incident-Evidence behandelt und nie Teil der akzeptierten Source-Baseline.

### Aktuelle Post-Cutover-Baseline – 2026-08-14

- Git-HEAD des abschließend geprüften Full-Exports: `60c99cf05330806d2cf14efd50d70fa7f98adf74`;
- Branch: `main`, Exportstatus: sauber;
- Export-SHA-256: `a0aff1666b83fda555122aa0c16f8c71224e1d8237ada226090094bce30ba290`;
- File-Manifest-SHA-256: `6a00907b6ba689bed65fa0b70de0416748a65d595c3d45304909e555248a7097`;
- Platform: `0.24.0-foundation`;
- Tooling: `0.14.1`;
- Patch Toolkit: `1.1.4`;
- Maven: `0.24.0-foundation-SNAPSHOT`;
- State Patch: `000219_patch-toolkit-python310-portability`;
- Codex Pilot Contract: `1.7.0`;
- Lifecycle: `PILOT_WRITE_READY` / `PROMOTED`;
- Write-Promotion: `000218_codex-cutover-write-promotion`, final `CODEX_CUTOVER_ACCEPTED`;
- M-002 und M-003: abgeschlossen;
- M-004: nächster fachlicher Slice;
- M-005: danach geplant;
- Sprint 003: weiterhin gesperrt, bis Sprint 002 geschlossen oder explizit disjunkt amended ist.

A001 und A002 bleiben unveränderliche fehlgeschlagene Calibration-/Incident-Evidence; A003 ist der erfolgreiche, vollständig qualifizierte Calibration-Attempt. Kein fehlgeschlagener Task wird erneut invoked oder als erfolgreiche Baseline umgedeutet.

## Problemstellung und Stakeholder

Die technische Frage, ob Codex die geschlossenen Aufgaben-, Scope-, Host- und Evidence-Grenzen real einhalten kann, ist durch den Cutover beantwortet. Offen ist nun die fachliche und methodische Frage, ob die vorhandenen Verträge vom Business-Partner-Fachkonzept bis zur GWC-Anwendung in kleinen kontrollierten Codex-Tasks konsistent zusammenspielen und ob die Ergebnisse deterministisch wiederholbar und evolvierbar sind.

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
| `CAP-REQ-010` | Vor jeder schreibenden Tooling-Operation MUSS ein zentraler Workspace-Lifecycle mit vollständigem, fail-closed Reset, aktiver-Run-Sperre und deterministischer Cleanup-Evidence verwendet werden. |
| `CAP-REQ-011` | Ein Artefakt-Root MUSS bereits existieren, kanonisch aufgelöst und durch einen exakten maschinenlesbaren Authorization Record freigegeben sein; Repository, Home, Downloads und temporäre Systempfade sind als Schreibziele verboten. |
| `CAP-REQ-012` | Delivery- und Patch-ID-Inventar MÜSSEN echte Delivery-Verzeichnisse, bekannte Metadateien, generische und patchbezogene Run Records sowie unbekannte, verlinkte, spezielle oder inkonsistente Einträge typisiert und fail-closed unterscheiden. |
| `CAP-REQ-013` | Tooling-Selfchecks MÜSSEN dauerhafte Start-/Result-Marker, getrennte Substep-Logs, Exitcodes und eindeutige Fehlerklassifikation liefern. |
| `CAP-REQ-014` | Schreibende Operatorabläufe MÜSSEN aus versioniertem Harness entstehen; freie Chat-Orchestrierung darf keine Mutations- oder Autorisierungsgrenze ersetzen. |

## Qualitätsanforderungen

- Kein Codex-Lauf darf Main, andere Repositories, Downloads, Operator-Home, Run-/Artifact-Roots, Git-Metadaten oder gemanagte Projekte außerhalb des Taskvertrags verändern.
- Task, Invocation, Worktree, Commit, Modell, Sandbox, Exitstatus, Diff, Qualifikation und Evidence müssen eindeutig korrelierbar sein.
- Oracles werden vor dem Lauf festgelegt und nicht aus dem Agentenergebnis abgeleitet.
- Tool Errors, Contract Findings, fachliche Abweichungen und bewusste Deferrals werden getrennt berichtet.
- Dry-run, Review und Accept bleiben getrennte Operatorentscheidungen; Push ist nicht Bestandteil dieses Sprints.
- Jede erzeugte Spezifikation besitzt stabile IDs und Rückverweise bis zum Fachkonzept.
- Wiederholungen verwenden identische Eingaben und qualifizierte Umgebungsparameter; nichtdeterministische Unterschiede werden erklärt oder blockieren den Abschluss.
- Neue dauerhafte Regeln werden in ADRs, Governance, Standards oder Contracts promoviert und nicht nur im Sprintstatus festgehalten.
- `PILOT_WRITE_READY` autorisiert die Vorbereitung und Ausführung ausdrücklich beauftragter Pilot-Tasks gemäß Task Contract und Harness; Handoff, Candidate-Integration, Dry-run, Accept, Push und Zielprojektmutation bleiben davon getrennte Grenzen.

## In Scope

- dauerhafte Persistenz der allgemeinen Projektziele und des aktiven Sprintvertrags;
- ein einziger vollständiger Tooling-Härtungsschnitt für Workspace-Lifecycle, Artefakt-Root-Autorisierung, typisiertes Delivery-Inventory, Selfcheck-Observability und harnessgebundene Operatorausführung;
- Rekonstruktion des D3-Kalibrierungs-Task-Packs erst nach Annahme dieses Härtungsschnitts gegen den dann tatsächlichen Live-Commit;
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
- `PILOT_WRITE_READY`/`PROMOTED` ist der aktuelle Repository- und Cutover-Lifecycle; schreibende Codex-Pilotarbeit bleibt strikt auf task-contract- und harnessgebundene Worktrees begrenzt.
- `CODEX_CALIBRATION` ist ein historischer Übergangszustand des Cutovers. Eine neue Kalibrierung oder Requalification wird nur bei konkret invalidierter Evidence beziehungsweise einer dafür vorgesehenen neuen Baseline erforderlich und ist keine generelle Vorbedingung für M-004.
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
| Legacy-Artefaktroot wird aus Konfiguration als Autorisierung missverstanden | Schreiben nach Home oder Downloads | exakter Authorization Record, Canonical-Path-Abgleich und Blockade vor Workerstart |
| historische Metadatei wird als Delivery klassifiziert | falsche Patch-ID oder fail-closed Abbruch an falscher Stelle | typisiertes Entry-Inventory ohne reine Namensheuristik |
| Workspace wird nur für einzelne Writer bereinigt | Cross-Run-Kontamination und unklare Evidence | ein zentraler Lifecycle für Patch, Dry-run, Accept, Diagnose, Collector und Handoff |
| Selfcheck verdeckt den fehlerhaften Substep | unnötige Wiederholung und schwache Forensik | dauerhafte Substep-Marker, Logs und Exitcodes |
| manuell erzeugtes Operator-Kommando weicht von Governance ab | unbeabsichtigte Hostwirkung | ausschließlich versionierter Harness für schreibende Abläufe |

## Definition of Ready

- [x] ADR-0015 ist akzeptiert und der Übergang von `PROJECT_READY` zu `PILOT_WRITE_READY` ist evidence-basiert abgeschlossen.
- [x] Agent Task Contract V2, Harness, Process Operations und Operator Command Effect Contract sind vorhanden.
- [x] Das Business-Partner-Fachkonzept und sein Acceptance Contract sind eingefroren.
- [x] Die aktuelle Git-, Export-, Versions- und Toolingbaseline ist dokumentiert.
- [x] Allgemeine Projektziele und Sprintscope sind als kanonische Quellen definiert.
- [x] Mutationsverbote, externe Roots, Promotionen und Stopbedingungen sind benannt.
- [x] `CAP-REQ-010` bis `CAP-REQ-014` sind über akzeptierte Tooling-/Cutover-Schnitte qualifiziert.
- [ ] Die Project Directory Governance ist entweder vollständig aktiviert oder bleibt für M-004 ausdrücklich mit begrenzter Geltung `draft`.
- [x] Das A003-Kalibrierungs-Task-Pack und seine Oracles wurden gegen die korrigierte Live-Baseline neu erzeugt und unabhängig qualifiziert.
- [x] Die konkrete lokale Codex-Umgebung, Host-Qualification und Runtime-Denial-Probes sind live belegt.
- [ ] Der erste M-004-Task Contract inklusive Scope, Oracle, Qualification und Evidence ist vor Invocation vollständig eingefroren.

## Definition of Done

- [ ] `CAP-REQ-001` bis `CAP-REQ-014` sind jeweils erfüllt, bewusst deferiert oder mit Blocker bewertet.
- [x] Workspace-Lifecycle, Artefakt-Root-Autorisierung, typisiertes Delivery-/Patch-ID-Inventory, Selfcheck-Observability und harnessgebundene Operatorausführung sind über akzeptierte Tooling-Schnitte geschlossen.
- [x] Die Incidents `000197`, `000198`, `000199` und `000200` sind als nicht akzeptierte Evidence dokumentiert; keine ihrer Payloads wurde in die Source-Baseline übernommen.
- [x] Die Readiness-Evidence dokumentiert den kontrollierten Übergang `PROJECT_READY -> CODEX_CALIBRATION -> PILOT_WRITE_READY` und die separate Promotion ohne automatische Schreibfreigabe aus einem Einzelrun.
- [ ] Die Project Directory Governance ist entweder nach vollständiger Closure evidenzbasiert aktiviert oder bleibt ausdrücklich `draft` mit eindeutig begrenzter Geltung.
- [x] Die Kalibrierung wurde erst nach akzeptiertem Härtungsschnitt gegen die jeweils aktuelle Live-Baseline neu vorbereitet.
- [x] Die fünf allgemeinen Projektziele sind als aktive kanonische Zielquelle indexiert und werden vom Sprint referenziert.
- [x] Der aktive Sprint besitzt Brief, Solution Plan, genau eine Statusquelle und einen vorbereiteten Completion Report mit konsistenter Milestone-Abdeckung.
- [x] Das immutable A003-Kalibrierungs-Task-Pack enthält read-only Analysis und zwei kleine implementierende Aufgaben mit vorab festgelegten Oracles; die mechanischen Negativproben sind durch die Host-/Confinement-Evidence gebunden.
- [x] Alle Cutover-relevanten Host-, Pfad-, Scope-, Git-, Sandbox-, Größen-, Capability- und Evidence-Grenzen wurden real geprüft; unerlaubte Mutation wurde verhindert und nachgewiesen.
- [x] Zwei implementierende Kalibrierungsaufgaben wurden fachlich und technisch unabhängig akzeptiert.
- [x] Eine separate akzeptierte Entscheidung hat `PILOT_WRITE_READY` evidenzbasiert promoviert (`000218_codex-cutover-write-promotion`).
- [ ] Die Business-Partner-Kette vom Fachkonzept bis zur disponiblen GWC-Anwendung ist vollständig traceable und ohne Mutation von GWC oder gemanagten Projekten erzeugt.
- [ ] Die generierte Anwendung besteht die definierten Build-, Runtime-, API-, Validierungs-, Fehler-, Persistenz-, Security- und UI-Acceptance-Kriterien oder weist begründete Deferrals aus.
- [ ] Drei Clean-Runs sind deterministisch vergleichbar; Abweichungen sind erklärt und akzeptiert oder blockieren die Qualification.
- [ ] Die V1.1-Fachkonzeptänderung wurde kontrolliert verarbeitet, ohne geschützte manuelle Extension Points zu überschreiben.
- [x] Alle bisher akzeptierten Cutover-Patches und Commits wurden über den kanonischen Dry-run-/Review-/Accept-Flow qualifiziert; es erfolgten kein automatischer Accept, kein Push und keine unerlaubte Zielmutation.
- [ ] Completion Report, technische Schulden, temporäre Dokumentdisposition, SemVer-Auswirkung und Rollout-, Generalisierungs- oder Stopentscheidung sind vollständig.

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Projektziele und aktiver Sprintvertrag sind kanonisch persistiert. | CAP-REQ-001 | Documentation Gate und Sprint Gate ohne neue Findings; alle sechs Dokumente indexiert. | Gate-Reports und Repository-Diff | springmaster-maintainers | completed |
| M-002 | Kalibrierungs-Task-Pack und unabhängige Oracles sind gegen die aktuelle Baseline eingefroren. | CAP-REQ-002, CAP-REQ-003 | Schema, Hashbindung, Scope, Limits und positive/negative Oracles reviewed. | A003 Task-, Oracle-, Host- und Preflight-Evidence | springmaster-maintainers | completed |
| M-003 | Reale Kalibrierung und Write-Readiness-Entscheidung sind abgeschlossen. | CAP-REQ-003, CAP-REQ-004 | Boundary-Probes und zwei Aufgaben qualifiziert; separate Promotion oder Blockerentscheidung. | A003 Invocation-, Handoff-, `000215`/`000216`, Confinement- und `000218`-Promotion-Evidence | springmaster-maintainers | completed |
| M-004 | Business-Partner-End-to-End-Pilot ist traceable und disponibel erzeugt. | CAP-REQ-005, CAP-REQ-006, CAP-REQ-007 | Staged Contracts und generierte Anwendung bestehen definierte Acceptance-Kriterien. | Contract-Kette, Build-, Runtime-, API- und UI-Evidence | springmaster-maintainers | planned |
| M-005 | Repeatability, V1.1-Evolution und Sprintabschluss sind qualifiziert. | CAP-REQ-008, CAP-REQ-009 | Drei Clean-Runs, Evolutionstest, Debt-/Effizienzbewertung und Abschlussentscheidung liegen vor. | Vergleichsreports und finaler Completion Report | springmaster-maintainers | planned |

## SemVer-Auswirkung

Erwartete Sprintauswirkung bleibt `minor`, sofern M-004/M-005 weitere freigegebene Generator-, Contract- oder Pilotfähigkeiten etablieren. Der Cutover-Anteil und der anschließende kompatible Portabilitätsfix `000219_patch-toolkit-python310-portability` haben die aktuelle Versionswahrheit auf Platform `0.24.0-foundation`, Tooling `0.14.1`, Toolkit `1.1.4` und Maven `0.24.0-foundation-SNAPSHOT` geführt. Die nachgelagerte Post-Cutover-Dokumentationssynchronisierung erhöht keine weitere Version; spätere M-004/M-005-Schnitte werden jeweils nach `SPRINGMASTER_VERSION_POLICY.md` klassifiziert.

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

### AMEND-001

- Datum: 2026-08-13
- Anlass: after-accepted-change; Codex Cutover wurde nach A003-Kalibrierung und separater Promotion final als `CODEX_CUTOVER_ACCEPTED` qualifiziert.
- Alte Aussage: Sprint 002 befand sich vor realer Codex-Kalibrierung; `PROJECT_READY` war der aktuelle Lifecycle, M-002/M-003 waren offen und schreibende Pilot-Tasks nicht autorisiert.
- Neue Aussage: M-002 und M-003 sind abgeschlossen; der Lifecycle ist `PILOT_WRITE_READY`/`PROMOTED`; M-004 ist der nächste fachliche Slice und M-005 folgt danach.
- Auswirkungen: Cutover-bezogene DoR-/DoD- und Milestone-Punkte werden auf erfüllt gesetzt; Sprint 002 bleibt aktiv, Sprint 003 bleibt gesperrt; M-004/M-005-Scope bleibt unverändert.
- Entscheidung: accepted; der Sprint wird ohne neue Cutover-Schleife mit dem Business-Partner-End-to-End-Pilot fortgesetzt.
- Freigaben: kanonische Acceptances `000215`, `000216`, `000218`, finale Live-Qualification `CODEX_CUTOVER_ACCEPTED` und Full-Export-HEAD `60c99cf05330806d2cf14efd50d70fa7f98adf74`.

### Amendment 2026-07-31 – akzeptierte Tooling-Härtung und Cutover-Foundation

- `000201_springmaster_tooling_hardening_cut` ist akzeptiert; frühere Aussagen `NOT_ACCEPTED` oder `NEXT_ACTION_BLOCKER=TOOLING_HARDENING` sind für den aktuellen Zustand superseded.
- Die repository-seitige Foundation `000203_springmaster_codex_cutover_foundation` ist ein qualifizierter, noch nicht akzeptierter Candidate.
- Vor realer Codex-Kalibrierung sind kanonische Acceptance von `000203`, Post-Accept-Live-Readiness und reale Host-Qualification verpflichtend.
- Vor `PILOT_WRITE_READY` sind zwei akzeptierte Implementierungskalibrierungen und eine separate Promotion erforderlich.
- Die Incident-Versuche `000197` bis `000200` bleiben historische Evidence und werden nicht als Baseline oder Payload wiederverwendet.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | active | Aktiver Sprint für reale Codex-Kalibrierung und den Business-Partner-End-to-End-Pilot angelegt. |
| 2026-07-30 | active | active | Tooling-Härtung als zwingende P0-Voraussetzung vor operativer Codex-Kalibrierung in Anforderungen, Risiken, DoR und DoD aufgenommen. |
| 2026-07-31 | active | active | Tooling-Härtung `000201` als akzeptiert und `000203` als qualifizierter, noch nicht akzeptierter Cutover-Foundation-Candidate fortgeschrieben. |
| 2026-08-13 | active | active | AMEND-001 akzeptiert: M-002/M-003 und Codex-Cutover abgeschlossen; Fokus auf M-004 Business-Partner-End-to-End-Pilot und anschließend M-005. |
| 2026-08-14 | active | active | Post-Cutover-Tooling-Portabilität `000219` in die aktuelle Baseline übernommen; keine Scope-Änderung an M-004/M-005 und kein Start von Sprint 003. |

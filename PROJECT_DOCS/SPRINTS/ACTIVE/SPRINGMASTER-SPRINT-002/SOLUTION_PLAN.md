---
documentId: SPRINGMASTER-SPRINT-002-PLAN
title: Codex Calibration and Business Partner End-to-End Pilot – Solution Plan
documentType: plan
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
temporary: true
sprintId: SPRINGMASTER-SPRINT-002
---

# Codex Calibration and Business Partner End-to-End Pilot – Solution Plan

## Lösungsoptionen und Auswahl

Bewertet wurden drei Optionen:

1. sofortige schreibende Agentennutzung;
2. reine statische Harness-Qualifikation ohne realen Agentenlauf;
3. staged Kalibrierung mit unabhängigen Oracles, separater Write-Promotion und anschließendem End-to-End-Pilot.

Gewählt wird Option 3. Sie entspricht ADR-0015, erhält den Patch- und Git-Transaktionspfad und trennt Sicherheitsnachweis, fachliche Ergebnisqualität und Generator-Pilot voneinander.

## Architektur- und Contract-Auswirkungen

Der Sprint verändert zunächst keine Produktarchitektur. Er verwendet und qualifiziert bestehende Contracts:

- Agent Task Contract V2 und External Root Contract;
- Codex Pilot Readiness und Business Partner Acceptance Contract;
- Operator Command Effect und Process Operations Contract;
- Generated-Slice-Spec, IR und Patch-Blueprint-Verträge;
- API-, Persistenz-, Security-, Validation-, Error- und UI-Schema-Regeln.

Neue dauerhafte Semantik wird nur über einen eigenen ADR-, Governance-, Standard- oder Contract-Schnitt eingeführt. Sprintdokumente bleiben Steuerungs- und Evidence-Quellen, nicht Ersatz für Produktverträge.

Der Cutover-Pfad ist abgeschlossen. Der aktuelle Lifecycle ist `PILOT_WRITE_READY`/`PROMOTED`; `WRITABLE_CODEX_AUTHORIZED=true` gilt ausschließlich innerhalb der unverändert strikten Task-, Worktree-, Qualification-, Handoff- und Operatorgrenzen. Slices 1 bis 3 sind abgeschlossen. Der aktive Ausführungsschwerpunkt beginnt mit Slice 4. Die Post-Cutover-Tooling-Portabilität ist mit `000219_patch-toolkit-python310-portability` auf Toolkit `1.1.4` / Tooling `0.14.1` geschlossen; daraus entsteht keine Änderung der M-004/M-005-Scope- oder Sprint-3-Grenzen.

## Slices und Reihenfolge

### Slice 1: Ziel- und Sprintwahrheit

Status: `completed`.

- kanonische Projektziele anlegen;
- vollständigen aktiven Sprint-002-Harness anlegen;
- Index, Gate-Evidence und Baselinebindung qualifizieren.

### Slice 1A: Tooling-Härtung vor Kalibrierung

Status: `completed`.

- genau einen vollständigen Candidate aus der akzeptierten Baseline `c5c5846176d92c34b19b7a7827d7264c1923805f` erzeugen;
- zentralen Workspace-Lifecycle für alle Writer schließen;
- explizite Artefakt-Root-Autorisierung ohne Root-Erzeugung schließen;
- Delivery- und Patch-ID-Inventar typisieren;
- dauerhafte Selfcheck-Substep-Evidence einführen;
- schreibende Operatorabläufe an versionierten Harness binden;
- gezielte und breite Qualification, kanonischen Dry-run, separaten Review und Accept ausführen;
- `000197` bis `000200` ausschließlich als Incident-Evidence behandeln.

Kein D3 Task Pack, keine Task-Vorbereitung und kein Codex-Aufruf sind vor Annahme dieses Slices zulässig.

### Slice 2: D3 Task Pack und Oracle

Status: `completed` durch den erfolgreichen A003-Neuaufbau; aufgegebene frühere Attempts bleiben historische Evidence.

- aufgegebenen Vor-000186-Kandidaten und die Payloads `000197` bis `000200` nicht wiederverwenden;
- Tasks gegen den aktuellen Commit neu erzeugen;
- read-only Aufgabe, negativer Boundary-Probe und zwei kleine Implementierungsaufgaben definieren;
- Oracles, Größenlimits, erlaubte Pfade, Qualifikationskommandos und Evidence vorab einfrieren.

### Slice 3: Runtime-Boundaries und Kalibrierung

Status: `completed`; A003, `000215`, `000216`, live Confinement und Promotion `000218` sind qualifiziert.

- externe Roots und isolierten Worktree preflighten;
- reale Denial-Probes ausführen;
- Kalibrierungsaufgaben einzeln starten, beobachten und qualifizieren;
- Ergebnisse unabhängig reviewen;
- separate Promotion zu `PILOT_WRITE_READY` oder Blockerentscheidung erstellen.

### Slice 4: Business-Partner-Contract-Kette

Status: `next`.

- Fachkonzept in canonical intent überführen;
- Generated-Slice-Spec und IR erzeugen;
- Application UI Spec aus Fach- und API-Verträgen ableiten;
- GWC Implementation Manifest gegen read-only GWC-/IDM-/Personnel-Referenzen erzeugen;
- jede Stufe schema-, hash- und anforderungsgebunden qualifizieren.

### Slice 5: Disposable Application

Status: `planned` nach qualifizierter Contract-Kette.

- Anwendung ausschließlich in einem externen disponiblen Zielroot materialisieren;
- Build, Runtime, API, Validierung, Fehler, Persistenz, Security-Klassifikation und UI prüfen;
- Re-Generation und geschützte Extension Points verifizieren.

### Slice 6: Repeatability und Evolution

Status: `planned` nach M-004.

- drei Clean-Runs mit identischen Baseline-Eingaben durchführen;
- Outputs, Hashes, semantische Unterschiede und Laufzeiten vergleichen;
- Fachkonzept V1.1 als kontrollierten Änderungsfall anwenden;
- Abschluss-, Debt-, Effizienz-, SemVer- und Rolloutentscheidung erstellen.

## Teststrategie und Zwischenverifikationen

Jeder Slice beginnt mit statischer Schema-, Hash-, Scope- und Baselineprüfung. Mutierende Schritte verwenden isolierte Worktrees oder disposable Roots und enden mit gezielter Verifikation vor breiter Qualification.

Mindestprüfungen:

- Documentation Gate und Sprint Gate für Slice 1;
- Workspace-, Artefakt-Autorisierungs-, Delivery-Inventory-, Selfcheck- und Harness-Fixtures für Slice 1A;
- Agent-Task-, Readiness-, Process- und Boundary-Fixtures für Slice 2 und 3;
- reale Denial-Probes und unveränderliche Invocation-/Run-Evidence für Slice 3;
- Schema-, Traceability- und Contract-Gates für Slice 4;
- Maven, Runtime-, API- und UI-Acceptance für Slice 5;
- Hash-/Semantikvergleich, Extension-Point- und Evolutionstest für Slice 6;
- vollständiger Tooling-Selfcheck und risikogerechter Patch-Validator vor Accept.

## Messkriterien

- Tooling-Härtung vor Kalibrierung vollständig akzeptiert;
- null unerlaubte Host-, Repository-, Git- oder Scope-Mutationen;
- zwei von zwei implementierenden Kalibrierungsaufgaben erfüllen ihre vorab festgelegten Oracles;
- hundert Prozent der pilotrelevanten Fachanforderungen besitzen stabile Traceability-Referenzen;
- drei Clean-Runs sind byteidentisch, wo Determinismus verlangt ist, oder semantisch identisch mit erklärten zulässigen Abweichungen;
- V1.1 ändert nur aus den Fachanforderungen abgeleitete Artefakte und erhält geschützte Extension Points;
- jeder Tool Error und jedes Finding besitzt Code, Stage, Log- oder Evidence-Pfad und Entscheidung;
- Effizienzvergleich enthält mindestens Laufzeit, manuelle Eingriffe, Rework und Reviewaufwand.

## Migration und Rollback

Es gibt keine Daten- oder Zielprojektmigration. Jeder Repositoryschnitt wird als eigener baselinegebundener Patch geliefert. Fehlgeschlagene Dry-runs oder Acceptance ändern Main nicht. Disposable Applications können vollständig gelöscht und aus unveränderten Inputs neu erzeugt werden.

Eine Write-Promotion ist eine separate, reversible Governanceentscheidung; sie wird nicht aus einem Taskstatus oder einem erfolgreichen Einzelrun abgeleitet.

## Tool- und Gate-Einsatz

- `bin/cpatch` und `bin/process-ops.sh` für Patchplan, Dry-run, Beobachtung und Accept;
- Documentation Gate und Sprint Gate für Dokumentwahrheit;
- Codex Pilot Readiness, Agent Task Harness und Process Operations für Kalibrierung;
- vorhandene Contract-, Test- und Quality-Registry-Gates für generierte Spezifikationen;
- Maven und applikationsspezifische Acceptance-Kommandos im disposable Zielroot;
- `bin/export.sh full --zip` nur für expliziten Handoff oder Audit.

Kein Outer-Orchestrator startet Dry-run und Accept automatisch nacheinander.

## Dokumentations- und Registerauswirkungen

Dauerhaft:

- `SPRINGMASTER_PROJECT_GOALS.md`;
- Sprint Brief und später finaler Completion Report;
- ggf. neue oder angepasste ADRs, Governance, Standards, Contracts und Tooling-Guides aus akzeptierten Erkenntnissen.

Temporär bis Closure:

- Solution Plan;
- Status;
- optionale Analysen, Checklisten und Solution Notes unter dem registrierten Sprint-WORK-Pfad.

Der Documentation Index wird bei jedem neuen dauerhaften oder aktiven Sprintdokument aktualisiert.

## Versionswirkung

Slice 1 ist eine Governance- und Planungsinitialisierung ohne unmittelbaren Komponenten-Bump. Spätere Tooling-, Contract-, Generator- oder Templateänderungen werden pro Schnitt klassifiziert. Die erwartete Sprintwirkung ist `minor`; die tatsächliche Version wird erst bei Release Closure gesetzt.

## Patch- oder Commitsequenz

Abgeschlossene Cutover-Sequenz:

1. `[completed]` Projektziele und Sprint-002-Harness;
2. `[completed]` Tooling-Härtung;
3. `[completed]` Annahme der Härtung und erneute Live-Baseline;
4. `[completed]` Calibration Task Pack und Oracle in A003;
5. `[completed]` Runtime-Boundary-Evidence;
6. `[completed]` Kalibrierungsaufgabe A / `000215`;
7. `[completed]` Kalibrierungsaufgabe B / `000216`;
8. `[completed]` Write-Readiness-Entscheidung / `000218`.

Verbleibende Sprintsequenz:

9. Business-Partner-Contract-Kette in kleinen taskvertraglich begrenzten Codex-Pilot-Schnitten;
10. Disposable Application;
11. Repeatability und V1.1-Evolution;
12. Sprint-Closure und Rollout-/Generalisierungsentscheidung.

Jeder mutierende Repositoryschnitt besitzt weiterhin eigene Baseline-Hashes, Scope, Changelog, Dry-run und expliziten Accept. Ein Codex-Handoff ist kein kanonischer Patch und keine Integrationsautorität.

## Unsicherheiten und Entscheidungszeitpunkte

- Form der Application UI Spec: Entscheidung vor beziehungsweise innerhalb von Slice 4, gestützt auf vorhandene GWC-/IDM-/Personnel-Referenzen und den eingefrorenen Business-Partner-Acceptance-Contract;
- Zerlegung von M-004: vor jeder realen Invocation werden Task Contract, Scope, Oracle, Qualification und Evidence eingefroren;
- Generator-/Rendererbedarf: Entscheidung erst nach qualifizierter Contract-Kette; keine vorschnelle Frameworkwahl;
- Persistenz-, Security- und UI-Deferrals: müssen aus den bestehenden Standards und dem Pilot-Acceptance-Contract abgeleitet und explizit qualifiziert werden;
- Generalisierung auf Project-New oder Managed Projects: nur nach Sprint Closure.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | active | Staged Lösungs- und Ausführungsplan für Sprint 002 angelegt. |
| 2026-07-30 | active | active | Vollständigen Tooling-Härtungsschnitt als Slice 1A und zwingende Annahmegrenze vor D3 und Codex-Kalibrierung eingefügt. |
| 2026-08-13 | active | active | Slices 1 bis 3 einschließlich A003-Kalibrierung und Write-Promotion abgeschlossen; aktiver Ausführungsschwerpunkt auf Slice 4/M-004 fortgeschrieben. |
| 2026-08-14 | active | active | Post-Cutover-Tooling-Portabilität `000219` geschlossen; Slice 4/M-004 bleibt unverändert der nächste Ausführungsschwerpunkt. |

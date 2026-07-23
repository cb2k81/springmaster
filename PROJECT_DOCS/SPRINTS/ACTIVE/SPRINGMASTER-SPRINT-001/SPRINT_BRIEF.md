---
documentId: SPRINGMASTER-SPRINT-001-BRIEF
title: Engineering Qualification Pilot – Sprint Brief
documentType: sprint-brief
status: active
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-23
validFrom: 2026-07-23
lastReviewedAt: 2026-07-23
reviewBy: 2026-08-07
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-001
sprintStart: 2026-07-23
targetCompletion: 2026-08-07
---

# Engineering Qualification Pilot – Sprint Brief

## Sprintziel

Springmaster soll den nächsten Governance-Reifegrad als real ausgeführter Pilotsprint erreichen: Änderungen werden vor ihrer Umsetzung durch maschinenlesbare Engineering-Profile, reproduzierbare Evidence- und Completion-Verträge, einen zentralen Quality-Rule-/Gate-Katalog und einen profilierten Test-Suite-Vertrag klassifiziert und report-only qualifiziert.

Der Sprint härtet ausschließlich die für einen belastbaren Pilotbetrieb notwendigen Steuerungs- und Nachweisfähigkeiten. Er führt keine Fachfeatures ein und aktiviert keine bislang report-only geführte Regel still als Strict Gate.

## Strategischer Bezug

Der Sprint unterstützt die übergeordneten Springmaster-Ziele wie folgt:

1. **Zentrale Tool- und Systemkern-Entwicklung:** ein einheitlicher Engineering- und Qualification-Vertrag für Änderungen am Masterprojekt.
2. **Steuerung gemanagter Projekte:** maschinenlesbare Profile und Evidence werden so geschnitten, dass spätere read-only Zielprojektprüfungen dieselben Begriffe verwenden können.
3. **Templating für neue Projekte:** Project-New-Auswirkungen werden für alle neuen Contracts und Gates geprüft; eine Materialisierung erfolgt nur, wenn sie für den lokalen Harness notwendig ist.
4. **Pattern und Verträge:** Engineering-, Evidence-, Quality-Rule-, Gate- und Test-Suite-Verträge werden als kanonische technische Quellen etabliert.
5. **Qualitätsanforderungen und Standards:** bestehende Governance und 399 Standard-Rule-IDs erhalten eine ausführbare, nachvollziehbare Zuordnung zu report-only Prüfung, manueller Review oder bewusster Nicht-Automatisierung.

## Ausgangslage und Baseline

Kanonische technische Baseline beim Sprintstart:

- Git-HEAD: `5d5bb86cdca11253d45f0950d8df59b0bffb92df`
- Branch: `main`
- Working Tree beim Export: sauber
- Full Export: `springmaster_export_full_2026-07-23T09-40-33-989283Z.zip`
- Export-SHA-256: `425f761aeb3cdb0e9927db60f0a6a643ebc3127311637eac258771176374979b`
- File-Manifest-SHA-256: `7c70caf078295a96eb997201098a67fd21855fce8b5b7c5f9d6d7e34267e8bf4`
- rekonstruierte Dateien: `661/661`
- Plattformversion: `0.17.0-foundation`
- Toolingversion: `0.7.0`
- Templateversion: `0.3.1`

Vorhanden und qualifiziert sind:

- Documentation Contract und Documentation Gate V2,
- Project Directory Contract und report-only Directory Gate,
- Sprint Contract, Drift Contract und report-only Sprint Gate,
- vollständige positive und negative Fixtures dieser drei Gatebereiche,
- Project-New-Materialisierung eines minimalen lokalen Governance-Harness,
- Fresh-Project-Acceptance mit eigenständiger Git-Baseline,
- neun Governance-Volltexte und vier Kernstandards im Draftstatus.

Noch fehlt die ausführbare technische Brücke zwischen Änderungsklassifikation, Qualitätsregeln, Testprofilen und qualifizierter Completion. Die bestehenden Governance-Texte beschreiben diesen Zielzustand, aber Engineering-Profile, Evidence-Schema, Gate Registry und Test-Suite-Vertrag sind noch nicht kanonisch materialisiert.

## Problemstellung und Stakeholder

Ohne gemeinsame Engineering- und Qualification-Verträge werden Prüfprofile weiterhin implizit aus Patchtyp, Toolwissen und Bestandskonventionen abgeleitet. Dadurch bleiben folgende Risiken bestehen:

- unterschiedliche Auslegung der für einen Änderungsschnitt erforderlichen Prüfungen,
- fehlende maschinenlesbare Verbindung zwischen Rule-ID, Gate, Severity, Enforcement und Evidence,
- unvollständige oder uneinheitliche Completion-Nachweise,
- unklare Trennung von Unit-, Integration-, Acceptance- und Tooling-Fixtures,
- erschwerte Propagation auf Project-New und gemanagte Projekte,
- verfrühte Strict- oder Reifegradbehauptungen.

Stakeholder sind Springmaster-Maintainer, Entwicklerinnen und Entwickler, Project-New-Nutzer, Eigentümer gemanagter Projekte sowie Reviewer von Architektur, Qualität, Tests und Releases.

## Anforderungen

| ID | Anforderung |
|---|---|
| `EQP-REQ-001` | Ein versionierter Engineering-Profile-Contract MUSS Änderungsklassen, betroffene Domänen, Mindestprüfungen, Readiness und zulässige Completion-Zustände maschinenlesbar beschreiben. |
| `EQP-REQ-002` | Ein Evidence- und Completion-Contract MUSS erforderliche Nachweise, Tool Errors, Findings, Deferrals, Hash-/Commitbezug und Abschlussurteil eindeutig modellieren. |
| `EQP-REQ-003` | Ein Quality Rule Catalog und eine Gate Registry MÜSSEN stabile Rule-IDs, Quellen, Prüfbarkeit, Severity, Enforcement, Gate-Zuordnung und Evidence-Typen abbilden. |
| `EQP-REQ-004` | Ein Test-Suite- und Fixture-Contract MUSS den aktuellen Maven-/Surefire-, Java-Test- und Tooling-Fixture-Bestand profilieren, ohne noch offene Coverage-Schwellen vorwegzunehmen. |
| `EQP-REQ-005` | Ein read-only, report-only Engineering-Qualification-Gate MUSS positive, negative und Tool-Error-Szenarien deterministisch auswerten und begrenzte JSON-Evidence erzeugen. |
| `EQP-REQ-006` | Tooling-Selfcheck, Patchprofile und Dokumentation MÜSSEN die neuen Verträge konsistent referenzieren; vorhandene Gates und Fresh-Project-Acceptance DÜRFEN nicht regressieren. |
| `EQP-REQ-007` | Auswirkungen auf Project-New und Managed Projects MÜSSEN bewertet werden; dieser Sprint DARF kein reales Zielprojekt mutieren. |
| `EQP-REQ-008` | Der Sprint MUSS mit einem Qualification- und Closure-Nachweis enden, der Aktivierungsreife, Deferrals, technische Schulden und SemVer-Empfehlung transparent ausweist. |

## Qualitätsanforderungen

- Alle neuen Verträge sind versioniert, schemaidentifiziert und fail-closed lesbar.
- Gates sind read-only, idempotent, deterministisch und standardmäßig report-only.
- Findings, Warnungen und Tool Errors werden getrennt gezählt und mit stabilen Codes ausgegeben.
- Jede automatisierte Regel besitzt mindestens ein positives und ein negatives Fixture; Toolfehlerpfade besitzen eigene Fixtures.
- Terminalausgaben bleiben kompakt; vollständige Evidence liegt in JSON- oder klar strukturierten Reportdateien.
- Bestehende Documentation-, Directory- und Sprint-Gates bleiben vollständig grün.
- Der vollständige Tooling-Selfcheck und die Fresh-Project-Acceptance bleiben grün.
- Neue externe Build- oder Analyseabhängigkeiten werden nur nach expliziter Dependency-Entscheidung eingeführt.
- Ungeklärte Schwellenwerte oder Toolentscheidungen werden nicht durch scheinpräzise Defaults ersetzt.

## In Scope

- Engineering-Profile-Contract für Springmaster-Änderungsschnitte.
- Evidence- und Completion-Schema für qualifizierte Änderungen.
- Quality Rule Catalog und Gate Registry als zentrale technische Zuordnung.
- Test-Suite- und Fixture-Contract auf Basis des vorhandenen Bestands.
- report-only Engineering-Qualification-Gate mit Fixtures.
- Integration in Tooling-Selfcheck, Exportprofile, Scope Registry und relevante Guides.
- Bestandsaufnahme und Mapping der bereits implementierten Documentation-, Directory- und Sprint-Gates.
- Bewertung der Project-New- und Managed-Project-Auswirkungen.
- Sprint-Qualification, Promotion dauerhafter Ergebnisse und Closure.

## Out of Scope

- neue Fach- oder Demo-Features,
- Änderungen am Platform Core,
- Strict-Promotion bestehender oder neuer Gates,
- Festlegung von Coverage-Schwellen,
- Festlegung konkreter Java-Komplexitäts- oder Größenwerte,
- Einführung von ArchUnit, Checkstyle, PMD, SpotBugs, JaCoCo oder Security-Scannern ohne eigene Entscheidung,
- Lizenz- und Vulnerability-Policy,
- Release Qualification V2,
- Migration von `docs/` oder historischen Transition-Pfaden,
- automatische Target-Registry-Aufnahme,
- Mutation realer gemanagter Projekte,
- Versionserhöhung vor der Release Closure.

## Constraints und Abhängigkeiten

- Die Governance-Dokumente und Standards bleiben bis zu einer eigenen Aktivierungsentscheidung im Draftstatus.
- Bestehende Rule-IDs und Gatecodes dürfen nicht still umgedeutet oder wiederverwendet werden.
- Contract-, Gate- und Evidence-Semantik muss mit Engineering-, Quality-Gate-, Test-, Dependency-, Managed-Project- und Release-Governance vereinbar sein.
- Der aktuelle Maven-Bestand verwendet Surefire; Failsafe- oder Tag-basierte Trennung ist eine offene Entscheidung.
- Coverage-Schwellen, Static-Analysis-Stack und Security-Tools sind offene Entscheidungen und blockieren nicht den report-only Contract-Schnitt.
- Jede Patchannahme benötigt Live-Baseline, Dry-run, Artifact Preflight und das passende Validierungsprofil.
- Project-New darf weiterhin nur den minimal erforderlichen lokalen Harness materialisieren.

## Risiken

| Risiko | Wirkung | Behandlung |
|---|---|---|
| Contract-Scope wird zu groß | Sprint verliert Pilotcharakter | pro Slice nur einen geschlossenen Vertrag oder Gatebaustein liefern |
| Rule Catalog dupliziert Standards | konkurrierende normative Wahrheit | nur IDs, Quellen, Prüfbarkeit und Enforcement referenzieren; Regeltext bleibt in der Quelle |
| implizite Toolentscheidung | unerwünschte Dependencies und Wartungslast | Toolauswahl aus dem Sprint ausschließen oder per separater Entscheidung behandeln |
| zu frühe Strict-Promotion | Bestandsbruch und falsche Reifeaussage | alle neuen Gates report-only; Promotion erst nach Closure-Empfehlung |
| Project-New-Überladung | erzeugte Projekte erhalten unnötige Masterkomplexität | nur lokal notwendige Verträge und ausführbare Checks materialisieren |
| Completion-Evidence wird selbstreferenziell | Gate bestätigt nur sein eigenes Format | unabhängige positive, negative und Tool-Error-Fixtures sowie Patch-/Git-Nachweise verlangen |
| Sprintumfang überschreitet Zielabschluss | stille Drift | verpflichtende Driftprüfung vor jedem neuen Slice und bei Terminüberschreitung |

## Definition of Ready

- [x] Sprintziel, Scope und Nicht-Ziele sind bestätigt.
- [x] Git-, Export- und Versionsbaseline sind dokumentiert und reproduzierbar.
- [x] Relevante Governance-Dokumente, Standards und bestehende Gates sind vorhanden.
- [x] Offene Entscheidungen zu Schwellenwerten und Tools sind benannt und vom Pilotumfang getrennt.
- [x] Der Contract-first- und report-only-Ansatz ist als sichere Ausführungsstrategie festgelegt.
- [x] Project-New- und Managed-Project-Auswirkungen sind als eigener Prüfschritt eingeplant.
- [x] Rollback erfolgt patchweise über den bestehenden transaktionalen Patchmechanismus.
- [x] Für jedes Teilziel bestehen messbare Acceptance- und Evidence-Erwartungen.

## Definition of Done

- [ ] `EQP-REQ-001` bis `EQP-REQ-008` sind jeweils erfüllt, deferiert oder mit Blocker bewertet.
- [ ] Engineering-Profile-, Evidence-/Completion-, Quality-Rule-/Gate- und Test-Suite-/Fixture-Contracts sind versioniert und dokumentiert.
- [ ] Das Engineering-Qualification-Gate ist read-only, report-only und mit positiven, negativen sowie Tool-Error-Fixtures qualifiziert.
- [ ] Bestehende Documentation-, Directory- und Sprint-Gates sowie deren Fixtures bestehen unverändert.
- [ ] Der vollständige Tooling-Selfcheck besteht ohne neue unbaselinierte Findings.
- [ ] Die Fresh-Project-Acceptance besteht oder eine begründete Project-New-Deferierung ist dokumentiert.
- [ ] Project-New- und Managed-Project-Auswirkungen sind explizit entschieden; kein reales Zielprojekt wurde mutiert.
- [ ] Alle akzeptierten Patches sind auf Sprint-ID und Teilziel referenzierbar.
- [ ] Dauerhafte Dokumentations-, Contract- und Registeränderungen sind in kanonische Quellen promoviert.
- [ ] Offene Findings, technische Schulden, Deferrals und Tool Errors sind im Completion Report erfasst.
- [ ] SemVer-Auswirkung und Releaseempfehlung sind begründet.
- [ ] Der Sprint ist qualifiziert abgeschlossen oder kontrolliert abgebrochen und archivierungsbereit.

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Engineering-Profile sowie Evidence-/Completion-Verträge sind kanonisch materialisiert. | `EQP-REQ-001`, `EQP-REQ-002` | Schema- und Negativtests bestehen; Beispieländerungen werden eindeutig profiliert. | Contracts, Fixture-Reports, Patch-Changelog | springmaster-maintainers | planned |
| M-002 | Quality Rule Catalog und Gate Registry bilden vorhandene und neue Prüfregeln ohne Regeltextduplikation ab. | `EQP-REQ-003` | Rule-IDs, Quellen, Severity, Enforcement und Gatebezug sind eindeutig; Duplikatprüfung besteht. | Katalog, Registry, statischer Auditreport | springmaster-maintainers | planned |
| M-003 | Test-Suite- und Fixture-Contract bilden den aktuellen Bestand reproduzierbar ab. | `EQP-REQ-004` | Surefire-, Java-Test- und Tooling-Fixture-Klassen sind profiliert; offene Schwellen bleiben explizit offen. | Contracts, Bestandsreport, Fixtures | springmaster-maintainers | planned |
| M-004 | Report-only Engineering-Qualification-Gate ist integriert und regressionsfrei. | `EQP-REQ-005`, `EQP-REQ-006` | Gate-, Tool-Error- und Integrationsfixtures bestehen; Selfcheck und bestehende Gates bleiben grün. | Gate-Reports, Selfcheck, Fresh-Project-Acceptance | springmaster-maintainers | planned |
| M-005 | Auswirkungen, Aktivierungsreife und Closure sind nachvollziehbar entschieden. | `EQP-REQ-007`, `EQP-REQ-008` | Project-New-/Managed-Project-Bewertung, Deferrals, SemVer- und Aktivierungsempfehlung liegen vor. | Completion Report, Register-/Dokumentpromotionen | springmaster-maintainers | planned |

## SemVer-Auswirkung

Erwartete Wirkung zum Sprintstart:

- Platform Core: `none`
- Demo: `none`
- Tooling: voraussichtlich `minor`, sofern neue additive Contract- und Gatefähigkeiten geliefert werden
- Template: `none` oder `patch`; nur bei notwendiger lokaler Harness-Erweiterung
- Platform Update: `none`
- Gesamtplattform: Entscheidung erst in der Version Closure

Die tatsächliche Version wird in diesem Sprint nicht vorab erhöht.

## Stop- und Abbruchkriterien

Der Sprint wird gestoppt und neu geplant, wenn mindestens eines gilt:

- eine notwendige Contract-Semantik widerspricht einer kanonischen Governance-Quelle,
- der Pilot erfordert eine nicht entschiedene externe Tool- oder Dependency-Einführung,
- bestehende Gate- oder Fresh-Project-Acceptance kann nicht ohne unzulässige Baseline-Ausweitung grün gehalten werden,
- eine Änderung würde reale gemanagte Projekte ohne eigenen autorisierten Lifecycle mutieren,
- Rule-IDs oder Evidence lassen sich nicht stabil und deterministisch modellieren,
- der Zielabschluss wird überschritten und die verpflichtende Driftprüfung ergibt `stop-and-replan`,
- der Umfang wächst über die fünf Teilziele hinaus, ohne akzeptiertes Amendment.

Ein kontrollierter Abbruch benötigt Completion Report, Ursachenbefund, Disposition temporärer Dokumente und Folgebedarf.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | – | planned | Sprintauftrag und Baseline formuliert. |
| 2026-07-23 | planned | active | Problemraum, DoR, Teilziele und Solution Plan für den Pilot bestätigt. |

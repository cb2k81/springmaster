---
documentId: RPT-ENG-QUAL-0001
title: Engineering Qualification Pilot – Activation and Impact Recommendation
documentType: report
status: final
authority: evidence
scope: repository
scopeLevel: project
scopePaths:
  - springmaster/engineering
  - springmaster/quality-gates
  - springmaster/testing
  - springmaster/managed-projects
  - springmaster/release-versioning
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-23
validFrom: 2026-07-23
lastReviewedAt: 2026-07-23
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-001
---

# Engineering Qualification Pilot – Activation and Impact Recommendation

## Zweck und Entscheidungsstatus

Dieser Report ist der dauerhafte Impact- und Aktivierungsnachweis aus `SPRINGMASTER-SPRINT-001`. Er bewertet die in den Slices S-01 bis S-04 materialisierte Engineering-Qualification-Kette und trennt vier Entscheidungen:

1. Nutzung innerhalb von Springmaster,
2. Strict-Promotion,
3. Materialisierung durch Project-New,
4. Propagation in gemanagte Projekte.

Gesamturteil: **report-only betriebsreif in Springmaster, nicht strict-ready und nicht automatisch propagationsreif**.

## Materialisierter Stand

Der Pilot hat folgende kanonische technische Quellen geschaffen:

- Change-Classification-, Engineering-Profile-, Evidence- und Completion-Contracts,
- Quality Rule Catalog und Gate Registry,
- Test-Suite-, Fixture- und versiegelten Test-Inventory-Contract,
- report-only Engineering-Qualification-Gate,
- Validatoren und positive, negative sowie Tool-Error-Fixtures,
- Integration in Scope Registry, Exportprofil und Tooling-Selfcheck.

Zum Abschluss sind 72 Quality Rules und sechs Gate-Deskriptoren eindeutig registriert. Die Engineering-Qualification-Kette führt registrierte Gates nicht selbst aus, mutiert keine Quelle und erteilt keine Sprint- oder Releasefreigabe. Das Sprint Gate behandelt physisch verbleibende, aber inhaltlich leere Active-Verzeichnisse nicht als Sprint; dadurch ist eine transaktionale Datei-Löschung vor dem Git-Commit closure-kompatibel.

## Springmaster-Aktivierung

Für Springmaster wird folgende Nutzung empfohlen:

| Dimension | Entscheidung | Begründung |
|---|---|---|
| Contract- und Registry-Validierung | freigegeben, report-only | Schemata, Referenzen und Fixtures sind reproduzierbar qualifiziert. |
| Engineering-Qualification-Evidence | freigegeben, report-only | Profilwahl, Record-Identität, Checkabdeckung und Completion sind deterministisch auswertbar. |
| Tooling-Selfcheck-Integration | freigegeben | Die realen Patchannahmen 000176 bis 000179 wurden mit Profil `tooling` erfolgreich abgeschlossen. |
| Strict-Enforcement | nicht freigegeben | Promotion benötigt eigene Rule-by-Rule-Entscheidung, Bestandsbaseline und nachgewiesene Zielprojektverträglichkeit. |
| Release Qualification | nicht freigegeben | Release Qualification V2, vollständiges `mvn clean verify`, SBOM- und Release-Evidence-Retention bleiben offen. |

Die Governance-Dokumente und Standards verbleiben im Status `draft`. Die technische report-only Nutzung ist keine normative Aktivierung der gesamten Governance.

## Project-New-Auswirkung

Ergebnis: **keine zusätzliche Materialisierung im Rahmen dieses Piloten**.

Begründung:

- Der seit Patch `000174` erzeugte Minimal-Harness deckt Dokumentation, Verzeichnisstruktur und Sprintsteuerung ab.
- Die zehn Project-New-relevanten Lieferdateien aus Patch `000174` sind bis zur Abschlussbaseline bytegenau unverändert.
- Ein frisch erzeugtes Projekt bestand in der Impactprüfung Documentation-, Directory- und Sprint-Gate ohne neue Findings.
- Engineering-Profile, Rule Catalog, Test Inventory und Qualification-Evidence sind derzeit Springmaster-spezifisch und würden ohne projektlokalen Adoption- und Profilvertrag eine zweite Wahrheit erzeugen.
- Die Project-New-Foundation soll fachfrei und minimal bleiben.

Eine spätere Materialisierung benötigt einen eigenen Project-New-Scope, ein projektlokales Engineering-Profil, reduzierte Rule-/Gate-Selektion, Fresh-Project-Acceptance und eine explizite Template-Versionentscheidung.

## Managed-Project-Auswirkung

Ergebnis: **read-only bewertbar, automatische Propagation und Target Apply für den neuen Engineering-Harness deferiert**.

Feststellungen:

- Die bestehenden Platform-Update-Profile liefern die neuen Engineering-, Quality- und Testing-Contracts sowie deren Gates nicht aus. Dadurch findet keine stille Propagation statt.
- Ein disposable Managed-Project-Pilot bestand Compatibility Check, Patchgenerierung und Target-Preflight für `tooling-cutover`; diese Schritte veränderten das Zielprojekt nicht.
- Reale Zielprojekte wurden nicht mutiert.
- Ein vollständiger Managed-Project-Adoption-/Deviation-Contract, ein read-only Managed-Project-Gate und profilbezogene Propagationsregeln fehlen weiterhin.

Vor einer Propagation sind mindestens erforderlich:

1. versionierter Adoption- und Deviation-Contract,
2. profilbezogene Auswahl von Contracts, Rules und Gates,
3. read-only Target-Comparison-Evidence,
4. Compatibility Decision für den Governance-Harness,
5. disposable Target-Acceptance einschließlich Ziel-Selfcheck,
6. separate Autorisierung jedes realen Target Apply.

## Deferrals und technische Schulden

| Thema | Disposition |
|---|---|
| Coverage-Schwellen und Coverage-Tool | deferiert; eigene Test-/Toolentscheidung erforderlich |
| Java-Komplexitäts- und Größenwerte | deferiert; keine scheinpräzisen Defaults |
| ArchUnit-/Static-Analysis-Stack | deferiert; Dependency- und Buildentscheidung erforderlich |
| Lizenz- und Vulnerability-Policy | deferiert; Dependency-Governance-Umsetzung erforderlich |
| Release Qualification V2 und Evidence-Retention | deferiert; eigener Release-Sprint erforderlich |
| Project-New Engineering-Harness | deferiert; derzeit kein lokaler Minimalbedarf nachgewiesen |
| Managed-Project-Propagation | deferiert; Adoption-, Deviation- und Target-Gate fehlen |
| Strict-Promotion | deferiert; nur regelweise und mit eigener Evidence zulässig |

Die 149 Legacy-Dokumentationsfindings und 61 versiegelten Directory-Transition-Findings bleiben unverändert; der Pilot erweitert keine Bestandsbaseline.

## SemVer- und Releaseempfehlung

| Komponente | Empfehlung |
|---|---|
| Platform Core | `none` |
| Demo | `none` |
| Tooling | `minor` bei nächster qualifizierter Release Closure |
| Project-New Template | `none` |
| Platform Update | `none` |
| Gesamtplattform | `minor`, sofern die Tooling-Fähigkeiten gemeinsam veröffentlicht werden |

Dieser Report erhöht keine Version und erteilt keine Releasefreigabe. Die tatsächliche Version Closure bleibt Aufgabe der Release and Version Governance.

## Aktivierungsbedingungen für Folgeschritte

Eine spätere Strict-, Project-New- oder Managed-Project-Aktivierung erfordert jeweils einen eigenen kontrollierten Änderungsschnitt. Gemeinsame Mindestbedingungen sind:

- eindeutige Owner und Rule-/Gate-Versionen,
- keine unbaselinierte Bestandsverschlechterung,
- positive, negative und Tool-Error-Fixtures,
- realer Selfcheck im betroffenen Profil,
- Fresh- oder Target-Acceptance entsprechend dem Geltungsbereich,
- dokumentierte Rollback- und SemVer-Wirkung,
- keine stillschweigende Mutation oder Propagation.

## Referenzen

- `PROJECT_DOCS/GOVERNANCE/ENGINEERING_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/QUALITY_GATE_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/TEST_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/MANAGED_PROJECT_GOVERNANCE.md`
- `PROJECT_DOCS/TOOLING/PROJECT_NEW.md`
- `PROJECT_DOCS/SPRINTS/ARCHIVE/2026/SPRINGMASTER-SPRINT-001/COMPLETION_REPORT.md`

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | – | final | Impact-, Aktivierungs-, Deferral- und SemVer-Entscheidung aus dem Engineering Qualification Pilot konsolidiert. |

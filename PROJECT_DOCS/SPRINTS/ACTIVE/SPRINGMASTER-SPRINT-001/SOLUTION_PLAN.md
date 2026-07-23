---
documentId: SPRINGMASTER-SPRINT-001-PLAN
title: Engineering Qualification Pilot – Solution Plan
documentType: plan
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
temporary: true
sprintId: SPRINGMASTER-SPRINT-001
---

# Engineering Qualification Pilot – Solution Plan

## Lösungsoptionen und Auswahl

### Option A – Big-Bang-Qualitätsplattform

Engineering-, Quality-, Test-, Dependency- und Release-Harness würden gemeinsam einschließlich externer Analysewerkzeuge und Strict Gates umgesetzt.

**Verworfen**, weil offene Schwellen- und Toolentscheidungen bestehen, der Änderungsschnitt nicht mehr pilotierbar wäre und Bestandsregressionen schwer lokalisierbar würden.

### Option B – Nur Dokumentation und manuelle Checklisten

Die Governance würde ausschließlich durch weitere Guides ergänzt.

**Verworfen**, weil die zentrale Lücke gerade in maschinenlesbaren Profilen, reproduzierbarer Evidence und deterministischer report-only Prüfung liegt.

### Option C – Contract-first Engineering Qualification Pilot

Engineering-, Evidence-, Quality-Rule-, Gate- und Test-Suite-Verträge werden in kleinen Slices materialisiert. Ein dependency-armes Python-/Bash-Gate prüft zunächst ausschließlich report-only. Bestehende Gates und Patchtransaktionen dienen als Referenzmuster.

**Ausgewählt**, weil diese Option die notwendige technische Brücke liefert, offene Toolentscheidungen nicht vorwegnimmt, kleine qualifizierbare Patches ermöglicht und den neuen Sprint-Harness real erprobt.

## Architektur- und Contract-Auswirkungen

Geplante neue technische Quellen:

```text
contracts/governance/engineering/
├── engineering-profile-contract.json
├── change-evidence-contract.json
└── completion-contract.json

contracts/governance/quality/
├── quality-rule-catalog.json
└── gate-registry.json

contracts/governance/testing/
├── test-suite-contract.json
└── fixture-contract.json
```

Geplante Tooling-Grenze:

```text
bin/engineering-qualification-gate.py
bin/engineering-qualification-gate.sh
bin/engineering-qualification-gate-it.sh
src/test/resources/tooling/engineering-qualification-gate-v1/
```

Die Contracts enthalten Referenzen auf Governance, Standards und bestehende Rule-IDs, aber keine duplizierten normativen Regeltexte. Das Gate mutiert weder Repository noch Zielprojekte und führt keine Releasefreigabe durch.

## Slices und Reihenfolge

| Slice | Primäres Teilziel | Inhalt | Eintritt | Abschluss |
|---|---|---|---|---|
| S-01 | M-001 | Engineering-Profile-, Evidence- und Completion-Contracts mit Schema-/Negativfixtures | Sprintdokumentation akzeptiert | Verträge validiert, Beispielprofile eindeutig |
| S-02 | M-002 | Quality Rule Catalog und Gate Registry; Mapping vorhandener Documentation-, Directory- und Sprint-Gates | S-01-Vertragsbegriffe stabil | Rule-ID- und Registry-Audit grün |
| S-03 | M-003 | Test-Suite- und Fixture-Contracts sowie Bestandsinventar | S-01 Evidence-Typen stabil | aktueller Java-/Tooling-Testbestand reproduzierbar klassifiziert |
| S-04 | M-004 | report-only Engineering-Qualification-Gate, CLI, Reports, Fixtures und Selfcheck-Integration | S-01 bis S-03 grün | positive, negative, Tool-Error- und Regressionsprüfungen grün |
| S-05 | M-005 | Project-New-/Managed-Project-Bewertung, Aktivierungsempfehlung, Promotionen und Closure | alle Implementierungsslices bewertet | Completion Report qualifiziert oder Deferrals explizit |

Jeder Slice wird als eigener begrenzter Patch oder als begründete kleine Patchgruppe geliefert. Die konkrete Patch-ID wird erst gegen die jeweils aktuelle Baseline vergeben.

## Teststrategie und Zwischenverifikationen

Für jeden Slice gelten mindestens:

1. JSON-/Schema- und Syntaxprüfung der betroffenen Artefakte.
2. positive Fixtures für gültige Profile, Evidence und Registry-Beziehungen.
3. negative Fixtures für fehlende Pflichtfelder, unbekannte IDs, Duplikate, ungültige Zustände und inkonsistente Relationen.
4. Tool-Error-Fixtures für fehlende, beschädigte oder inkompatible Contracts.
5. `git diff --check` und Payload-Parität.
6. Documentation Gate und zugehörige 10 Fixtures.
7. Project Directory Gate und zugehörige 17 Fixtures.
8. Sprint Gate und zugehörige 21 Fixtures.
9. vollständiger Tooling-Selfcheck für Tooling-Patches.
10. Fresh-Project-Acceptance, sobald Project-New-relevante Dateien betroffen sind.
11. `mvn test`, sobald Java-Test-, Build- oder Maven-Konfiguration betroffen ist.

Zwischen Slices wird eine Driftprüfung dokumentiert. Ein Folge-Slice beginnt nur, wenn der vorherige Slice eine saubere Git- und Exportbaseline erzeugt hat.

## Messkriterien

| Kriterium | Zielwert |
|---|---|
| Contract-Schemas | alle lesbar, versioniert und mit stabiler Schema-ID |
| Rule-ID-Eindeutigkeit | 0 Duplikate in Katalog und referenzierten Standardregeln |
| Gate-Registry-Referenzen | 0 unbekannte Rule-, Gate-, Evidence- oder Profil-IDs |
| positive Fixtures | 100 % bestanden |
| negative Fixtures | 100 % erwartungsgemäß erkannt |
| Tool-Error-Fixtures | 100 % mit Exit-Code `2` und strukturiertem Tool Error |
| bestehende Gate-Fixtures | Documentation `10/10`, Directory `17/17`, Sprint `21/21` |
| neue Directory-Findings | 0 |
| unbaselinierte neue Findings | 0 |
| Tooling-Selfcheck | `PASS` |
| Fresh-Project-Acceptance bei Auswirkung | `PASS` oder qualifizierte Deferierung |
| Zielprojektmutationen | 0 |

## Migration und Rollback

- Alle neuen Contracts und Gates starten additiv und report-only.
- Bestehende Patchprofile und Gates bleiben bis zu einer eigenen Promotion unverändert verbindlich.
- Jeder Slice besitzt vollständige Vorzustands-Hashes und wird über `patch.sh` transaktional angenommen.
- Rollback erfolgt pro akzeptiertem Patch; keine Datenmigration und keine Zielprojektmutation ist vorgesehen.
- Eine Findings-Baseline wird nur verwendet, wenn ein reproduzierbarer Bestandsbefund vorliegt und neue Findings nicht verdeckt werden.
- Contract-Versionen werden nicht nachträglich umgedeutet; inkompatible Änderungen benötigen eine neue Contract-Version.

## Tool- und Gate-Einsatz

Bevorzugt werden vorhandene Bordmittel:

- Python Standard Library für JSON, CLI und deterministische Relationstests,
- Bash Strict Mode für Wrapper und Integrationstests,
- vorhandenes Patch-, Export- und Artifact-Preflight-Tooling,
- Documentation-, Directory- und Sprint-Gates,
- Maven/Surefire nur für bestehende Java-Tests und betroffene Buildänderungen.

Nicht ohne eigene Entscheidung eingeführt werden ArchUnit, Checkstyle, PMD, SpotBugs, JaCoCo, Failsafe, Container- oder Security-Scanner.

## Dokumentations- und Registerauswirkungen

Voraussichtlich betroffen:

- Engineering Governance,
- Quality Gate Governance,
- Test Governance,
- Build and Tooling Standard,
- Documentation Scope Registry und Index,
- Tooling-Guides,
- Open-Decision-, Technical-Debt- und gegebenenfalls Risk-Register,
- Project-New-Dokumentation bei tatsächlicher Harness-Auswirkung.

Dauerhafte Erkenntnisse werden nicht im Sprintordner belassen. Contractentscheidungen werden in den kanonischen Governance-Dokumenten oder ADRs verankert; offene Punkte werden in Register promoviert.

## Versionswirkung

Der Lösungsschnitt ist additiv und voraussichtlich kompatibel:

- Tooling: erwarteter `minor`-Impact,
- Template: `none` oder `patch`, abhängig von notwendiger lokaler Materialisierung,
- Platform Core und Demo: `none`,
- Platform Update: `none`.

Die tatsächliche Versionsänderung wird erst nach qualifizierter Completion empfohlen und durch Release and Version Governance entschieden.

## Patch- oder Commitsequenz

1. Sprintinitiierung als Documentation Patch.
2. S-01 Contract Seed.
3. S-02 Quality Rule/Gate Registry.
4. S-03 Test Suite/Fixture Baseline.
5. S-04 Engineering Qualification Gate und Selfcheck-Integration.
6. optionaler Project-New-Harness-Patch nur bei nachgewiesenem lokalen Bedarf.
7. S-05 Reconciliation-, Qualification- und Closure-Patch.

Jeder akzeptierte Patch referenziert `SPRINGMASTER-SPRINT-001` und mindestens ein Teilziel im Changelog.

## Unsicherheiten und Entscheidungszeitpunkte

| Unsicherheit | Entscheidungspunkt | Behandlung bis dahin |
|---|---|---|
| minimale Profilanzahl | nach S-01-Fixture-Prototyp | nur aus vorhandenen Patch-/Engineering-Klassen ableiten |
| automatisierbarer Anteil der 399 Standardregeln | nach S-02-Mapping | `manual-review` oder `not-automatable` explizit zulassen |
| technische Suite-Trennung | nach S-03-Bestandsinventar | vorhandene Surefire-Baseline registrieren |
| Project-New-Materialisierung | nach S-04 Fresh-Project-Impactprüfung | keine vorsorgliche Kopie |
| Strict-Promotion | ausschließlich in S-05/folgendem Sprint | alle Gates report-only |
| externer Analyse- oder Coverage-Stack | außerhalb dieses Sprints | keine Dependency einführen |

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | – | draft | Lösungsoptionen und Contract-first-Slices formuliert. |
| 2026-07-23 | draft | active | Lösungsschnitt, Tests, Rollback und Teilzielzuordnung bestätigt. |

---
documentId: DOC-GOV-0001
title: Documentation Governance
documentType: governance
status: active
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/documentation
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-20
validFrom: 2026-07-22
lastReviewedAt: 2026-07-23
reviewBy: 2027-01-23
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Documentation Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie Springmaster menschlich lesbare Dokumentation klassifiziert, freigibt, prüft, ablöst, archiviert und auffindbar hält.

Sie gilt für dauerhafte und kontrolliert temporäre Markdown-Dokumente in:

- Springmaster,
- Project-New und erzeugten Projekten,
- gemanagten Projekten entsprechend ihrer Adoption.

Sie stellt sicher, dass:

- Git die dauerhafte Historie bleibt,
- jeder Inhalt genau eine kanonische Quelle besitzt,
- Dokumentart, Autorität, Scope und Lifecycle eindeutig sind,
- temporäre Arbeitsstände nicht unkontrolliert dauerhaft werden,
- technische Contract Sources nicht als zweite Dokumentwahrheit gepflegt werden,
- Documentation Gate V2 die formalen Regeln deterministisch prüfen kann.

Bei Aktivierung ersetzt dieser Text die bisherige Bootstrap-Regelung am selben Pfad. Die vorhandene inkrementelle Transition bleibt bestehen, bis Bestand und Gate V2 qualifiziert sind.

## 2. Nicht Gegenstand

Nicht hier geregelt werden:

- Root-Allowlist und allgemeine Dateiplatzierung: Project Directory Governance,
- Sprintphasen, Drift und Sprintabschluss: Sprint Governance,
- allgemeine Gate-, Finding- und Promotion-Semantik: Quality Gate Governance,
- fachliche Detailregeln von Standards und ADRs,
- Managed-Project-Adoption und Deviations im Detail.

Diese Governance referenziert solche Regeln, dupliziert sie aber nicht.

## 3. Kanonische Wahrheit und Artefaktgrenzen

### 3.1 Git und Statuswirkung

Git ist die verbindliche Historie für Dokumentinhalte, Statuswechsel, Korrekturen und Ablösungen. Exporte, Logs, Chatverläufe, Runtime-Zustände und nicht akzeptierte Arbeitsstände ersetzen keine Git-Historie.

Eine dauerhafte Änderung wird erst durch den vorgesehenen Git- oder Patchprozess zur Projektwahrheit.

### 3.2 Eine Quelle pro Inhalt

Jede normative Aussage, Entscheidung, Anforderung, Planung oder dauerhafte Evidenz besitzt genau eine kanonische Dokumentquelle.

Andere Dokumente dürfen Kontext geben und referenzieren. Vollständige manuell gepflegte Kopien sind nicht zulässig. Technisch erzeugte Ableitungen müssen ihre Quelle nennen und als abgeleitet erkennbar sein.

Bei Widersprüchen zwischen Dokumenten, Contracts, Code, Tests oder Evidence wird nicht still priorisiert. Der Konflikt wird anhand von Autorität, Status, Scope und Gültigkeit eingegrenzt und in den kanonischen Quellen gelöst.

### 3.3 Dokumentation und Contract Sources

Dokumentation beschreibt Ziele, Anforderungen, Entscheidungen, Konzepte, Standards, Verfahren, Pläne, Status und Ergebnisse.

Als Code oder Contract Source gelten insbesondere:

- XML, YAML, JSON und ENV-Definitionen,
- OpenAPI, Schemas und Liquibase-Dateien,
- maschinenlesbare Verträge und Registries,
- Golden Fixtures,
- Projekt- und Code-Templates,
- ausführbare Gate-Regeln,
- generierte Evidence sowie Build- und Runtime-Konfiguration.

Ihre Pfade bestimmt der Project Directory Contract. Markdown darf sie erklären und referenzieren, aber nicht als manuell gepflegte zweite Wahrheit duplizieren.

Eine normative Quelle KANN konkrete maschinenlesbare Parameter ausdrücklich an einen benannten Contract delegieren. Der Contract ist dann kanonisch für diese Werte, darf aber weder Geltungsbereich, Begründung noch Regelwirkung eigenständig erweitern.

Bereits vorhandene technische Dateien unter `PROJECT_DOCS/` sind nur als expliziter Übergangsbestand zulässig. Neue Fehlplatzierungen sind verboten; die Documentation Transition Baseline darf nicht erweitert werden.

## 4. Dokumenttypen

Jedes dauerhafte Markdown-Dokument besitzt genau einen `documentType`.

| `documentType` | Kanonischer Zweck | Typische Autorität |
|---|---|---|
| `governance` | Verbindliche Prozess- und Zusammenarbeitsregeln | `normative` |
| `goal` | Messbarer Zielzustand und Nicht-Ziele | `directive` |
| `strategy` | Langfristiger Lösungs- und Entwicklungsweg | `directive` |
| `requirements` | Funktionale oder qualitative Anforderungen | `normative` |
| `architecture-concept` | Zusammenhängendes Architektur- oder Lösungsmodell | `directive` oder `normative` |
| `adr` | Einzelne dauerhafte Architekturentscheidung | `normative` |
| `standard` | Wiederverwendbare, prüfbare Detailregeln | `normative` |
| `guide` | Erklärende Vorgehensweise oder Bedienanleitung | `informative` |
| `plan` | Zeitliche oder sachliche Umsetzungsplanung | `directive` |
| `checklist` | Kontrollierte manuelle Prüfschritte | `directive` oder `informative` |
| `report` | Datierter Status-, Audit-, Review- oder Readiness-Befund | `evidence` |
| `technical-debt` | Abgrenzung, Risiko und Behandlungsplan einer Schuld | `evidence` |
| `register` | Fortlaufende kontrollierte Liste | `evidence` |
| `sprint-brief` | Verbindlicher Sprintauftrag und Problemraum | `directive` |
| `sprint-status` | Temporärer aktueller Sprintzustand | `evidence` |
| `sprint-completion-report` | Dauerhafter Sprintabschluss | `evidence` |
| `documentation-index` | Aus Metadaten abgeleiteter Katalog | `informative` |

README-Dateien sind abhängig von ihrer Funktion `guide` oder `documentation-index`.

Enthält eine Datei mehrere unabhängig freigebbare, ablösbare oder archivierbare Dokumentarten, muss sie aufgeteilt werden.

## 5. Metadatenmodell

### 5.1 Gemeinsames Front Matter

Jedes dauerhafte Markdown-Dokument benötigt mindestens:

```yaml
---
documentId: DOC-...
title: Eindeutiger Titel
documentType: governance
status: draft
authority: normative
scopeLevel: project
scopePaths:
  - springmaster/documentation
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: YYYY-MM-DD
validFrom: null
lastReviewedAt: null
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
```

Während der Gate-Transition darf zusätzlich das bisherige Feld `scope` geführt werden. Es ist nur ein Kompatibilitätsfeld und entfällt mit vollständiger V2-Unterstützung.

### 5.2 Feldregeln

| Feld | Regel |
|---|---|
| `documentId` | Eindeutig und nach Vergabe unveränderlich |
| `title` | Menschlich lesbarer eindeutiger Titel |
| `documentType` | Genau ein aktiver Dokumenttyp |
| `status` | Für Typ und Lifecycle zulässiger Wert |
| `authority` | `normative`, `directive`, `informative` oder `evidence` |
| `scopeLevel` | Kleinste Ebene, die den Inhalt vollständig abdeckt |
| `scopePaths` | Nicht leere Liste registrierter Scope-Bezeichner |
| `appliesTo` | Projekte oder Projektklassen, für die das Dokument gilt |
| `owner` | Stabiler Verantwortungsbezeichner |
| `createdAt` | Unveränderliches Erstellungsdatum |
| `validFrom` | Gültigkeitsbeginn; vor Freigabe `null` |
| `lastReviewedAt` | Letzte inhaltliche Prüfung oder `null` |
| `reviewBy` | Spätestes Reviewdatum, soweit erforderlich |
| `supersedes` | Abgelöste Dokument-IDs |
| `supersededBy` | Ablösende Dokument-ID oder `null` |
| `temporary` | `true` nur für kontrolliert temporäre Dokumente |
| `sprintId` | Separate Sprint-ID; Pflicht für Sprint- und temporäre Sprintdokumente |

Manuelle Versionsnamen wie `final-v3`, `new`, `copy` oder `rev7` sind nicht zulässig.

### 5.3 Scope-Level

Zulässige Scope-Level sind mindestens:

- `ecosystem`, `platform`, `project`, `subsystem`, `component`,
- `layer`, `capability`, `interface`, `data`, `operation`.

Scope-Pfade und ihre Hierarchie werden maschinenlesbar registriert. Ein Scope-Pfad ist ein hierarchischer Bezeichner und kann einem physischen Repository-Pfad entsprechen, muss es aber nicht. Die Registry kennzeichnet seine Semantik; freie, nicht registrierte Scope-Bezeichnungen sind nach der Transition nicht zulässig.

### 5.4 Reviewpflicht

Aktive Governance-, Strategy-, Requirements-, Architecture-Concept-, Standard-, Guide-, Plan- und Registerdokumente benötigen `reviewBy`.

Akzeptierte ADRs dürfen event-driven ohne `reviewBy` geführt werden. Deferred ADRs benötigen ein Reviewdatum. Finale Reports und archivierte Dokumente benötigen kein periodisches Review, aber eine eindeutige Baseline oder Beobachtungsreferenz.

### 5.5 Typspezifische Ergänzungen

Der Documentation Contract definiert zusätzliche Pflichtfelder. Mindestens gilt:

- Reports und Completion Reports benötigen Baseline-Referenzen.
- Sprintdokumente benötigen `sprintId`.
- Temporäre Dokumente benötigen `temporary: true`, `sprintId` und `reviewBy`.
- Abgeleitete Indizes müssen Generator oder Quellmetadaten identifizierbar machen.

## 6. Statusmodelle

### 6.1 Normative und leitende Dokumente

Für Governance, Goals, Strategy, Requirements, Architecture Concepts, Standards, Guides, Plans und Checklists gilt grundsätzlich:

```text
draft -> review -> active -> deprecated | superseded | retired
```

`draft` oder `review` kann zu `withdrawn` werden. Pläne können zusätzlich `completed` oder `cancelled` werden.

### 6.2 ADRs

```text
proposed -> accepted | rejected | deferred
accepted -> superseded | deprecated
```

Ein akzeptiertes ADR wird nicht wieder `proposed`. Eine neue Entscheidung benötigt ein neues ADR.

### 6.3 Reports

```text
draft -> final -> corrected | historical
```

Finale Reports dürfen nicht still überschrieben werden. Korrekturen müssen Grund und betroffene Aussage sichtbar machen. Eine wesentlich neue Bewertung benötigt einen neuen Report mit Supersession-Beziehung.

### 6.4 Technical Debt und Register

```text
technical-debt: draft -> review -> active -> resolved | superseded | retired
register:       draft -> review -> active -> retired
```

Der Status einzelner Registereinträge ist vom Dokumentstatus getrennt.

### 6.5 Sprintdokumente

```text
planned -> active -> blocked | completed | cancelled -> archived
```

Die Documentation Governance besitzt die Dokumentstatus; die Sprint Governance besitzt Prozessbedeutung und Abschlussbedingungen.

## 7. Statuswechsel, Supersession und Archivierung

### 7.1 Atomarer Statuswechsel

Ein Statuswechsel umfasst als geschlossenen Änderungsschnitt:

1. Front Matter,
2. Lifecycle-Eintrag,
3. Review- und Gültigkeitsdaten,
4. beidseitige Supersession-Beziehungen,
5. Index,
6. betroffene Referenzen,
7. erforderliche Gates,
8. Übernahme durch Git oder akzeptierten Patch.

Jedes dauerhafte Dokument besitzt einen Abschnitt `## Lifecycle`:

```markdown
| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | - | draft | Dokument angelegt |
```

Front Matter und Lifecycle müssen konsistent sein.

### 7.2 Supersession

Ein Dokument ist `superseded`, wenn ein anderes Dokument seine kanonische Aussage ersetzt.

Erforderlich sind:

- beidseitige Referenzen über Dokument-IDs,
- Aktualisierung eingehender Verweise,
- Indexaktualisierung,
- Beseitigung widersprüchlicher aktiver Aussagen.

Das alte Dokument bleibt historisch erhalten, ist aber keine aktive Regelquelle.

### 7.3 Deprecation

Ein deprecated Dokument nennt:

- Grund,
- Alternative für neue Arbeit,
- Ablöse- oder Retirement-Bedingung.

### 7.4 Archivierung

Aktive, historische, superseded und temporäre Dokumente müssen logisch getrennt sein. Die physische Archivstruktur bestimmt die Project Directory Governance.

Ein Dokument darf nicht gleichzeitig in aktiver und archivierter Form manuell gepflegt werden.

## 8. Temporäre Dokumente

Temporäre Repository-Dokumente sind nur in einem registrierten aktiven Sprintbereich zulässig.

Allgemeine Arbeitsdokumente liegen unter:

```text
PROJECT_DOCS/SPRINTS/ACTIVE/<sprint-id>/WORK/
```

Die Sprint Governance kann klar benannte verpflichtende Steuerungsdokumente am Root des aktiven Sprintordners zulassen. Derzeit gilt diese Ausnahme ausschließlich für `SOLUTION_PLAN.md` und `STATUS.md`; sie dürfen keine allgemeinen Arbeitsnotizen aufnehmen.

Temporäre Dokumente benötigen:

```yaml
temporary: true
sprintId: SPRINT-...
reviewBy: YYYY-MM-DD
```

Am Sprintende wird genau eine Behandlung dokumentiert:

- `promote`,
- `aggregate`,
- `archive`,
- `discard`.

Ein Sprint darf mit unbehandelten temporären Dokumenten nicht archiviert werden.

Workspace-Entwürfe außerhalb des Repositorys sind keine Projektwahrheit. Bei Übernahme müssen sie den normalen Dokument-Lifecycle beginnen.

## 9. Architekturkonzepte und ADRs

### 9.1 Architekturkonzept

Ein Architekturkonzept ist ein Living Document für einen zusammenhängenden Lösungsraum. Es kann Kontext, Komponenten, Verantwortlichkeiten, Datenflüsse, Laufzeit, Persistenz, Security, Deployment, Betrieb, Migration und Qualitätsattribute beschreiben.

Es darf mehrere ADRs referenzieren, aber keine einzelne dauerhafte Entscheidung anstelle eines ADRs verstecken.

### 9.2 ADR

Ein ADR dokumentiert genau eine konkrete dauerhafte Architekturentscheidung im kleinsten vollständigen Scope.

Pflichtinhalte sind:

- Entscheidungsfrage, Kontext und Baseline,
- In Scope und Out of Scope,
- Treiber und Constraints,
- Alternativen,
- Entscheidung und Begründung,
- positive und negative Konsequenzen,
- Auswirkungen,
- betroffene Standards und Konzepte,
- Verifikation und Gate-Wirkung,
- Ausnahmen, Deferrals und Supersession.

Unabhängig entscheidbare Fragen werden getrennt. Der Zielumfang liegt ungefähr zwischen 800 und 2.500 Wörtern; ab etwa 3.500 Wörtern ist eine Begründung erforderlich. Die Größenprüfung ist zunächst eine Warnung.

Bestehende ADR-Governance und ADR-Templates dürfen Nummerierung und Detailstruktur konkretisieren, aber gemeinsame Metadaten und Status nicht neu definieren.

## 10. Templates und neue Dokumenttypen

### 10.1 Templates

Für jeden aktiven Dokumenttyp muss ein verbindliches Template bestehen. Mindestens erforderlich sind:

- allgemeines Dokument,
- Goal, Strategy und Requirements,
- Architecture Concept und ADR,
- Standard und Guide,
- Plan und Checklist,
- Report,
- Sprint Brief, Solution Plan, Sprint Status und Sprint Completion Report,
- Technical Debt,
- Register.

Der Zielpfad für Dokumentationstemplates ist `PROJECT_DOCS/_TEMPLATES/`. Er ist von technischen Projekt- und Code-Templates getrennt.

Templates enthalten vollständiges Front Matter, Pflichtabschnitte und Lifecycle. Beispielinhalte dürfen nicht wie normative Projektaussagen wirken.

### 10.2 Neuer Dokumenttyp

Ein neuer Typ benötigt vor Verwendung:

1. Zweck und Abgrenzung,
2. Autorität und Statusmodell,
3. Pflichtmetadaten,
4. Template,
5. Index- und Gate-Unterstützung,
6. Bewertung von Verzeichnis-, Project-New- und Managed-Project-Auswirkungen,
7. akzeptierte Änderung dieser Governance und des Documentation Contract.

Ein neuer Typ entsteht nicht allein durch einen neuen Ordner oder Dateinamen.

## 11. Dokumentationsindex

`PROJECT_DOCS/index.md` ist die primäre Auffindbarkeitssicht.

Der Index:

- wird aus Front Matter erzeugt oder vollständig dagegen geprüft,
- ist keine zweite normative Quelle,
- enthält alle nicht archivierten dauerhaften Dokumente,
- zeigt mindestens Typ, Status, Titel und Scope,
- trennt aktive von historischen und archivierten Dokumenten,
- nimmt temporäre Arbeitsdokumente nicht in die primäre aktive Sicht auf,
- enthält keine manuell gepflegten Statusaussagen, die Metadaten widersprechen können.

Lokale README-Dateien können Teilindizes sein, müssen aber aus demselben Metadatenbestand ableitbar oder gegen ihn prüfbar sein. Während der Documentation Transition dürfen explizit baselinete Bestandsdokumente weiterhin als pfadbasierte Einträge geführt werden; neue oder migrierte Dokumente werden aus ihrem V2-Front-Matter validiert.

## 12. Documentation Gate V2

### 12.1 Prüfumfang

Documentation Gate V2 prüft mindestens:

- Dokumenttypen und Pflichtmetadaten,
- eindeutige Dokument-IDs,
- typabhängige Statuswerte und Übergänge,
- Authority-, Scope- und Applies-To-Werte,
- Reviewfristen,
- Front-Matter-/Lifecycle-Konsistenz,
- beidseitige Supersession,
- vollständigen und aktuellen Index,
- interne Links,
- ADR-Nummern, Scope und Größenwarnung,
- Baselines finaler Reports,
- temporäre Dokumente und Sprintabschlussbedingungen,
- neue Contract Sources unter `PROJECT_DOCS/`,
- Adoption- und Deviation-Referenzen,
- unzulässige manuelle Dateiversionen.

Die allgemeine Gate- und Strict-Semantik wird nicht hier, sondern in der Quality Gate Governance geregelt.

### 12.2 Ausführung

Das Gate muss:

- geänderte Dokumente und den Gesamtbestand prüfen können,
- Quelldateien unverändert lassen,
- Findings und Tool Errors trennen,
- deterministische maschinenlesbare Reports erzeugen,
- kompakte Diagnosen liefern,
- positive, negative und Transition-Fixtures besitzen.

### 12.3 Transition

Patch `000168_springmaster_documentation_governance_bootstrap_v2` friert die V2-Transition einmalig gegen Git-HEAD `6f72a152892331c79ac483961dd64aa6f362b8e4` ein. Damit werden alle vor diesem Cutover vorhandenen, noch nicht auf V2-Metadaten migrierten Markdown-Dokumente und technischen Übergangsartefakte vollständig erfasst.

- Neue dauerhafte Dokumente erfüllen die aktive Metadatenregel vollständig.
- Explizit baselinete Bestandslücken bleiben report-only.
- Nach diesem Cutover darf die Baseline nur reduziert, nicht um neue Verstöße erweitert werden.
- Gate V2 wird erst über die Bootstrap-Prüfungen hinaus strict erweitert, wenn Contract, Implementierung, Fixtures, Bestandsbaseline und Project-New-Auswirkung der jeweiligen Regel qualifiziert sind.

## 13. Bestandsmigration

### 13.1 Migrationsentscheidungen

Jedes Bestandsdokument erhält genau eine Behandlung:

- `retain`, `reclassify`, `move`, `split`, `aggregate`,
- `archive`, `replace` oder `discard`.

Die Migration erfolgt in sachlich begrenzten Änderungen ohne fachfremde Massenbereinigung.

### 13.2 Bestehende Bereiche

Die vorhandenen Bereiche `ADR`, `CONCEPT`, `CORE`, `DEMO`, `GOVERNANCE`, `OPERATIONAL`, `PLANNING`, `STANDARDS`, `TARGET_UPDATES` und `TOOLING` bleiben während der Migration `legacy-accepted`.

Ihre Existenz ist keine dauerhafte Freigabe als Zielstruktur. Dokumente werden zuerst klassifiziert, bevor Pfade geändert werden.

`PROJECT_DOCS/CONFIG`, `PROJECT_DOCS/TEMPLATES/project-skeleton`, technische JSON-Dateien unter `PROJECT_DOCS/` und vergleichbare Contract Sources sind Migrationskandidaten. Sie werden nur gemeinsam mit abhängigen Generatoren, Tests, Exportprofilen und Patch-Scopes verschoben.

Der Root-Bereich `docs/` wird separat klassifiziert und bis dahin nicht als parallele aktive Dokumentationsstruktur erweitert.

### 13.3 Migrationskontrolle

Jeder Migrationsschritt muss:

- Index und Referenzen aktualisieren,
- relevante Gates ausführen,
- fachliche Semantik unverändert lassen oder ausdrücklich ändern,
- Project-New- und Managed-Project-Auswirkungen bewerten,
- die Documentation Transition Baseline reduzieren oder begründet unverändert lassen.

## 14. Project-New und gemanagte Projekte

Project-New muss eine minimale gültige Dokumentationsbasis mit Index, Governance-Adoption, erforderlichen Templates, vorgesehenen Sprint-/Registerstrukturen und ausführbarem Documentation Gate erzeugen.

Gemanagte Projekte dokumentieren den adoptierten Governance-Stand sowie lokale Ergänzungen, Deviations und Reviewfristen.

Die konkrete Kopier-, Referenz- und Update-Strategie gehört zur Managed Project Governance.

## 15. Verantwortlichkeiten

| Verantwortung | Aufgaben |
|---|---|
| Document Owner | Inhalt, Metadaten, Reviews, Status und Supersession |
| Documentation Governance Owner | Typen, Metadaten, Lifecycle, Templates und Migration |
| Gate Owner | Deterministische technische Umsetzung ohne neue Normerfindung |
| Maintainer | Freigabe neuer Typen, Governance-Änderungen und Strict-Promotion |

## 16. Abnahmekriterien

Diese Governance ist vollständig umgesetzt, wenn:

1. alle aktiven Dokumenttypen im Contract registriert sind,
2. jedes aktive dauerhafte Dokument eine eindeutige ID und gültige Metadaten besitzt,
3. Status, Reviews und Supersession typabhängig geprüft werden,
4. aktive, temporäre, superseded und historische Dokumente unterscheidbar sind,
5. der Index deterministisch erzeugt oder vollständig validiert wird,
6. neue technische Contract Sources unter `PROJECT_DOCS/` verhindert werden,
7. der Bestand vollständig klassifiziert ist,
8. die Documentation Transition Baseline nur kontrollierte Restfälle enthält,
9. Templates für alle aktiven Dokumenttypen existieren,
10. Documentation Gate V2 seine positiven, negativen und Transition-Fixtures besteht,
11. Project-New eine gültige Dokumentationsbasis erzeugt,
12. gemanagte Projekte read-only gegen ihre Adoption geprüft werden können,
13. keine konkurrierende Dokumentationsstruktur oder zweite manuelle Wahrheit besteht.

## 17. Technische Ableitungen

Mindestens abzuleiten sind:

- Documentation Contract,
- Dokumenttypen- und Statuskatalog,
- Scope- und Applies-To-Katalog,
- Front-Matter-Schema,
- Template-Katalog,
- Index-Generator oder -Validator,
- Documentation Gate V2,
- Documentation Transition Baseline und Migrationsreport.

Bestehende Contract-Pfade unter `contracts/governance/` sind zu bevorzugen, solange kein eigenständiger Lifecycle eine neue Contract-Familie erfordert.

## 18. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-20 | - | active | Bootstrap-Governance für neue Dokumente und Documentation Transition Baseline eingeführt |
| 2026-07-22 | active | active | Konsolidiertes Metadaten-, Lifecycle-, Index- und Gate-V2-Modell aktiviert |
| 2026-07-23 | active | active | Temporäre Sprint-Steuerungsdokumente und Solution Plan kontrolliert integriert |

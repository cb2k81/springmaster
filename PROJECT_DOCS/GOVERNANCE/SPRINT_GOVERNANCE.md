---
documentId: DOC-GOV-0007
title: Sprint Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-23
validFrom: null
lastReviewedAt: null
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Sprint Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie ein begrenzter Entwicklungsauftrag vom bestätigten Problemraum bis zur qualifizierten Schließung, Promotion dauerhafter Projektwahrheiten und Archivierung als Sprint geführt wird.

Sie bestimmt:

- Sprintidentität und Sprintscope,
- Trennung von Problem- und Lösungsraum,
- verbindliche Sprintdokumente,
- Phasen und messbare Teilziele,
- Definition of Ready und Definition of Done,
- Status, Drift und Amendments,
- Qualification, Abschluss, Abbruch und Archivierung,
- Behandlung temporärer Arbeitsdokumente.

Sie gilt für Springmaster, Project-New und profilgerecht für erzeugte und gemanagte Projekte. Ein Sprint kann Code, Tooling, Contracts, Governance, Standards, Templates oder Migrationen umfassen.

Ein Sprint ist eine ergebnisorientierte, begrenzte Steuerungseinheit. Ein Zielzeitraum unterstützt die Steuerung, ist aber weder Sprintidentität noch Ersatz für Abschlusskriterien.

## 2. Abgrenzung und kanonische Verantwortung

Diese Governance ist die kanonische Quelle für Sprintscope, Sprintdokumente, Phasen, Teilziele, Drift, Amendments, Qualification, Closure und Archivierung.

| Nicht hier geregelt | Kanonische Quelle |
|---|---|
| Dokumenttypen, Metadaten und allgemeiner Dokument-Lifecycle | Documentation Governance |
| physische Pfade, Extension Points und Strukturmigration | Project Directory Governance |
| technischer Lifecycle eines Änderungsschnitts | Engineering Governance |
| Teststufen und Test Completion | Test Governance |
| Gate-, Rule-, Waiver- und Baseline-Semantik | Quality Gate Governance |
| externe Abhängigkeiten | Dependency Governance |
| konkrete technische Regeln | Standards und ADRs |
| Releasefreigabe und tatsächliche Version | Release and Version Governance |
| Adoption und Mutation gemanagter Projekte | Managed Project Governance |
| Kommandos und Bedienabläufe | Development Guide und Tooling |

Diese Governance referenziert Ergebnisse dieser Quellen, wiederholt ihre Detailregeln aber nicht.

## 3. Grundsätze und Begriffe

| Begriff | Bedeutung |
|---|---|
| Sprint | begrenzter, ergebnisorientierter Entwicklungsauftrag |
| Sprint Brief | verbindlicher Problem- und Auftragsraum |
| Solution Plan | kontrollierter Lösungs- und Ausführungsraum |
| Teilziel | messbares Ergebnis innerhalb des Sprints |
| Sprint Status | genau eine aktuelle temporäre Steuerungsquelle |
| Drift | materielle Abweichung vom bestätigten Sprintvertrag |
| Amendment | akzeptierte Änderung des Sprintvertrags |
| Qualification | zusammengeführter Nachweis der Definition of Done |
| Promotion | Überführung dauerhafter Erkenntnisse in kanonische Quellen |
| Closure | kontrollierter Abschluss oder Abbruch |

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

### 3.1 Problemraum vor Lösungsraum

Der Sprint Brief beschreibt Ziel, Ausgangslage, Anforderungen, Constraints und Abschlussbedingungen. Der Solution Plan beschreibt Optionen, Slices, Tests, Tooling und Ausführung. Eine Lösung darf den Problemraum nicht still verändern.

### 3.2 Ergebnis vor Aktivität

Ziele werden als nachweisbare Ergebnisse formuliert. „Analysieren“, „implementieren“ oder „testen“ genügen allein nicht als Ziel.

### 3.3 Keine zweite dauerhafte Wahrheit

Der Sprintordner darf keine dauerhafte Anforderungs-, Architektur- oder Standardwahrheit exklusiv besitzen. Dauerhafte Ergebnisse werden spätestens bei Closure promoviert.

### 3.4 Kleine qualifizierbare Slices

Ein Sprint kann mehrere Änderungsschnitte und Patches enthalten. Jeder Schnitt durchläuft die Engineering Governance und ist mindestens einem Teilziel zugeordnet.

### 3.5 Keine stille Drift

Materielle Änderungen an Ziel, Scope, Anforderungen, DoD oder Constraints werden vor Fortsetzung als Drift bewertet und gegebenenfalls per Amendment übernommen.

### 3.6 Verbindliche Closure

Jeder Sprint wird abgeschlossen oder kontrolliert abgebrochen. Ein aktiver Sprintordner darf kein dauerhafter Sammelplatz offener Arbeit werden.

## 4. Identitäten, Scope und Zeitraum

### 4.1 Unabhängige Identitäten

Sprint-ID, Requirement-ID, Document-ID, ADR-ID, Teilziel-ID, Change-ID, Patch-ID, Artifact-ID, Git-Commit, Version und Release-ID bleiben unabhängig. Eine Sprintnummer ist weder Patchnummer noch Softwareversion.

### 4.2 Sprint-ID

Neue Sprints verwenden eine projektweit eindeutige, stabile ID. Empfohlenes Muster:

```text
<PROJECT>-SPRINT-<NNN>
```

Beispiele: `CBIX-SPRINT-001`, `SPRINGMASTER-SPRINT-001`. Das konkrete Muster wird im Sprint Contract profiliert.

### 4.3 Sprintscope

Der Scope enthält mindestens:

- gewünschtes Ergebnis,
- betroffene Anforderungen und Qualitätsziele,
- betroffene Komponenten oder Fähigkeiten,
- In Scope und Out of Scope,
- Constraints und Abhängigkeiten,
- erwartete Architektur-, Test-, Dependency-, Dokumentations-, Versions- und Projektwirkungen.

Eine Dateiliste oder Patchliste allein ist kein Sprintscope.

### 4.4 Zeitraum

Der Sprint Brief nennt geplanten Beginn, Zielabschluss und Reviewpunkte. Eine Überschreitung des Zielabschlusses löst eine Drift-Prüfung aus; sie verlängert den Sprint nicht still.

### 4.5 Zuordnung von Änderungen

Jeder akzeptierte Änderungsschnitt ist auf Sprint-ID und Teilziel referenzierbar. Ein Schnitt soll genau einem primären Sprint zugeordnet sein. Sprintübergreifende Änderungen benötigen eine Begründung und eindeutige Evidence-Zuordnung.

## 5. Verbindliche Sprintstruktur

### 5.1 Zielstruktur

```text
PROJECT_DOCS/SPRINTS/ACTIVE/<sprint-id>/
├── SPRINT_BRIEF.md
├── SOLUTION_PLAN.md
├── STATUS.md
├── COMPLETION_REPORT.md
└── WORK/
    ├── ANALYSES/
    ├── CHECKLISTS/
    └── SOLUTION_NOTES/
```

Nach Closure:

```text
PROJECT_DOCS/SPRINTS/ARCHIVE/<year>/<sprint-id>/
├── SPRINT_BRIEF.md
├── COMPLETION_REPORT.md
└── optional EVIDENCE_INDEX.md
```

Die Project Directory Governance registriert die Pfade. Diese Governance bestimmt Rolle, Pflicht und Abschlussbehandlung.

### 5.2 Pflichtdateien

| Datei | Dokumenttyp | `temporary` | Rolle |
|---|---|---:|---|
| `SPRINT_BRIEF.md` | `sprint-brief` | `false` | verbindlicher Problem- und Auftragsraum |
| `SOLUTION_PLAN.md` | `plan` | `true` | kontrollierter Lösungs- und Ausführungsplan |
| `STATUS.md` | `sprint-status` | `true` | einzige aktuelle Sprintstatusquelle |
| `COMPLETION_REPORT.md` | `sprint-completion-report` | `false` | dauerhafter Abschlussnachweis |

`SOLUTION_PLAN.md` und `STATUS.md` benötigen zusätzlich `sprintId` und `reviewBy`. Sie sind kontrollierte temporäre Sprintsteuerungsdokumente am Root des aktiven Sprintordners und bilden die ausdrückliche Ausnahme von der allgemeinen `WORK/`-Ablageregel.

Projektpräfix, Sprintnummer und Dokumentidentität stehen in Metadaten. Pflichtdateien werden nicht durch laufende Dateinummern identifiziert.

### 5.3 Arbeitsdokumente

Zusätzliche Dokumente liegen ausschließlich unter `WORK/`, tragen `temporary: true`, `sprintId` und `reviewBy`. Sie ersetzen keine Pflichtdatei. Beschreibende Dateinamen sind vorzuziehen; eine Ordnungsnummer ist keine Identität.

## 6. Sprint Brief: Problem- und Auftragsraum

Der Sprint Brief ist vor Execution aktiv und enthält mindestens:

1. Sprint-ID und Zeitraum,
2. Sprintziel und Bezug zu übergeordneten Zielen,
3. Ausgangslage und Baseline,
4. Problemstellung und Stakeholder,
5. funktionale und qualitative Anforderungen,
6. Constraints und Abhängigkeiten,
7. In Scope und Out of Scope,
8. Risiken,
9. Definition of Ready,
10. Definition of Done,
11. messbare Teilziele,
12. erwarteten SemVer-Impact je Komponente,
13. Stop- und Abbruchkriterien,
14. Amendments.

### 6.1 MVP-, Pilot- und Readiness-Ziele

Ein Reifegradziel MUSS operationalisiert werden. Der Brief benennt:

- zu härtende Fähigkeiten oder Komponenten,
- messbare Mindestmerkmale des Zielreifegrads,
- ausdrücklich ausgeschlossene Features,
- mit dem Reifegrad vereinbare und unvereinbare Deferrals.

„MVP-Reife herstellen“ allein ist kein prüfbares Ziel.

### 6.2 Ausgangslage

Die Ausgangslage referenziert Git- oder Exportbaseline, aktuelle Versionen, Reife-Evidence, bekannte Deferrals, Risiken, Schulden und relevante Regelquellen. Umfangreiche Analysen werden referenziert, nicht in den Brief kopiert.

### 6.3 Anforderungen und Nicht-Ziele

Sprintanforderungen referenzieren dauerhafte Requirement-IDs oder erhalten im Brief eindeutige IDs. Neu erkannte dauerhafte Anforderungen werden spätestens bei Closure promoviert.

Nicht-Ziele verhindern insbesondere Featureausweitung, fachfremde Refactorings, unautorisierte Zielprojektmutation, unnötige Strukturmigration und vorzeitige Reife- oder Releasebehauptungen.

### 6.4 Definition of Ready

Vor Solution Framing und Execution müssen mindestens gelten:

- Auftrag, Ziel, Scope und Nicht-Ziele sind bestätigt,
- Baseline und relevante Quellen sind bekannt,
- Anforderungen und Qualitätsziele sind ausreichend bestimmt,
- wesentliche Constraints, Abhängigkeiten und Blocker sind benannt,
- notwendige Architektur- oder Dependency-Entscheidungen liegen vor oder sind als Teilziel eingeplant,
- erforderliche Engineering-, Test- und Gate-Profile sind grundsätzlich bestimmbar,
- Teilziele und Acceptance Evidence sind formulierbar,
- Stop-Kriterien sind bei hohem oder kritischem Risiko definiert.

Engineering Readiness einzelner Changes ist Teil der Sprint-DoR, ersetzt sie aber nicht.

### 6.5 Definition of Done

Die DoD umfasst mindestens:

- Bewertung aller Sprintanforderungen und Teilziele,
- Engineering Completion übernommener Änderungen,
- erforderliche Test Completion und Qualification,
- Behandlung von Findings, Risiken, Schulden und Deferrals,
- Aktualisierung dauerhafter ADRs, Konzepte, Standards, Requirements und Register,
- Bewertung von Version und Releasewirkung,
- Entscheidung über alle temporären Dokumente,
- finalen Completion Report,
- konsistenten Index und archivierungsfähigen Sprintstand.

Ein grüner Einzeltest oder ein akzeptierter Patch erfüllt die Sprint-DoD nicht automatisch.

### 6.6 Stop- und Abbruchkriterien

Stop-Kriterien umfassen mindestens unzuverlässige Baseline, fehlende zentrale Entscheidung, unkontrollierbares Sicherheits- oder Datenrisiko, nicht qualifizierbaren Zielscope, nicht genehmigte Abhängigkeit oder wesentliche Scopeüberschreitung.

## 7. Solution Plan: Lösungs- und Ausführungsraum

Der Solution Plan übersetzt den bestätigten Problemraum in ein ausführbares Vorgehen. Er enthält mindestens:

1. Lösungsoptionen und Auswahl,
2. Architektur- und Contract-Auswirkungen,
3. ADR- und Standardbedarf,
4. geplante Slices oder Änderungsschnitte,
5. Reihenfolge und Abhängigkeiten,
6. Teststrategie und Zwischenverifikationen,
7. Messkriterien,
8. Migrations- und Rückrollstrategie,
9. Tool- und Gate-Einsatz,
10. Dokumentations- und Registerauswirkungen,
11. Versionswirkung,
12. Patch- oder Commitsequenz,
13. Unsicherheiten und Entscheidungszeitpunkte.

Materielle Architektur-, Dependency-, Security-, Persistenz- oder Toolentscheidungen nennen die ernsthaft betrachteten Optionen. Die dauerhafte Entscheidung gehört bei entsprechender Tragweite in eine ADR oder andere kanonische Quelle.

Slices erreichen ein messbares Teilziel, besitzen einen geschlossenen Change Scope und können kontrolliert qualifiziert, übernommen oder verworfen werden. Eine technische Aktivität ohne Ergebnis ist kein ausreichender Slice.

Der Plan bestimmt Zwischenverifikationen so, dass Drift und übergroße Endqualifikation vermieden werden. Toolwahl darf keine neue verbindliche Regel etablieren.

## 8. Sprintphasen

| Phase | Zweck | Verbindlicher Ausgang |
|---|---|---|
| 0. Intake und Alignment | Auftrag und Zielbezug klären | bestätigter Sprintauftrag |
| 1. Problem Framing | Anforderungen, Constraints und Nicht-Ziele bestimmen | aktiver Sprint Brief; DoR erfüllt |
| 2. Solution Framing | Optionen, Architektur-, ADR-, Test- und Migrationsbedarf bestimmen | reviewter Solution Plan |
| 3. Slice Planning | Teilziele, Reihenfolge und Evidence festlegen | ausführbarer Slice-Plan |
| 4. Execution | qualifizierbare Änderungsschnitte umsetzen | akzeptierte Slices und aktuelle Evidence |
| 5. Qualification | DoD, Tests, Dokumentation, Debt und Versionen bewerten | qualifizierter oder blockierter Stand |
| 6. Closure und Promotion | Wahrheiten aktualisieren und Arbeitsreste behandeln | finaler Report und archivierter oder abgebrochener Sprint |

Phasen sind Prozesszustände, keine Dokumentstatus. Die aktuelle Phase steht ausschließlich in `STATUS.md`.

Ein kontrollierter Rücksprung ist zulässig, wenn eine Drift-Prüfung ihn begründet. Das Phasenmodell verbietet keine iterative Umsetzung; es verlangt aber klare Klärungs- und Abschlusszustände.

## 9. Messbare Teilziele

Jedes Teilziel besitzt:

- Teilziel-ID,
- gewünschtes Ergebnis,
- betroffene Anforderungen,
- Acceptance-Kriterien,
- erforderliche Evidence,
- Abhängigkeiten,
- Owner,
- Status.

Statuswerte:

```text
planned | in-progress | blocked | completed | deferred | cancelled
```

Ein Teilziel ist nur abgeschlossen, wenn Ergebnis und Acceptance-Kriterien nachgewiesen sind.

Ein Deferral ist nur zulässig, wenn das Sprintziel konsistent erreichbar bleibt, keine falsche Reifebehauptung entsteht und Risiko, Owner und Folgeplanung dokumentiert sind. Ist das Teilziel DoD-relevant, führt Deferral zu `blocked`, Amendment oder Abbruch.

## 10. Sprint Status

`STATUS.md` ist die einzige aktuelle Statusquelle und enthält mindestens:

- Sprint-ID, aktuelle Phase und Gesamtstatus,
- abgeschlossene, aktive und blockierte Teilziele,
- Blocker und neue Erkenntnisse,
- letzte Drift-Bewertung,
- aktuelle Risiken und technische Schulden,
- erwartete Versionswirkung,
- nächsten kontrollierten Schritt,
- letzte Aktualisierung.

Der Status wird mindestens aktualisiert nach Phasenwechsel, akzeptiertem Patch, Teilzieländerung, Blockade, materieller Scope-, Risiko-, Architektur-, Dependency- oder Versionsänderung, Drift-Entscheidung und Closure.

Gesamtstatus:

```text
planned | active | blocked | completed | cancelled
```

Fortlaufende Statuskopien oder datierte Parallelstände sind nicht zulässig. Ausführliche Analysen und Reports werden referenziert.

## 11. Drift und Amendments

### 11.1 Prüfereignisse

Eine Drift-Prüfung erfolgt mindestens:

- vor einem neuen Slice,
- nach einem akzeptierten Patch oder materiellen Change,
- bei neuen Anforderungen,
- bei Architektur-, Dependency-, Security- oder Datenänderungen,
- bei Blockaden oder Stop-Kriterien,
- bei Überschreitung des Zielzeitraums,
- vor Qualification und Closure.

### 11.2 Kategorien

Zu bewerten sind mindestens Ziel-, Scope-, Anforderungs-, Architektur-, Lösungs-, Qualitäts-, Test-, Versions-, Abhängigkeits-, Dokumentations-, Struktur- und Projektprofil-Drift.

### 11.3 Ergebnisse

| Ergebnis | Bedeutung |
|---|---|
| `none` | keine materielle Abweichung |
| `accepted` | Änderung wird per Amendment übernommen |
| `deferred` | Gegenstand wird außerhalb des Sprints nachverfolgt |
| `split` | Gegenstand wird in einen separaten Sprint oder Change überführt |
| `stop-and-replan` | Execution pausiert; Vertrag oder Plan wird neu bestätigt |

Die aktuelle Bewertung steht kompakt in `STATUS.md`. Akzeptierte Änderungen stehen dauerhaft im Amendment-Abschnitt des Sprint Briefs.

### 11.4 Amendment-Pflicht

Ein Amendment ist erforderlich bei materiellen Änderungen an Ziel, Scope, Anforderungen, Qualitätszielen, DoR, DoD, Constraints, Stop-Kriterien, verpflichtenden Teilzielen, materieller Versionswirkung oder autorisierter Zielprojektwirkung.

Routineänderungen an Reihenfolge oder technischen Details im Solution Plan benötigen kein Amendment, solange der Sprintvertrag unverändert bleibt.

Jedes Amendment enthält ID, Datum, Anlass, alte und neue Aussage, Auswirkungen sowie Entscheidung. Es benötigt mindestens Freigabe durch Sprint Owner und einen für den betroffenen Scope verantwortlichen Reviewer. Zusätzliche ADR-, Dependency-, Governance- oder Releaseprozesse bleiben verpflichtend.

Ein Amendment darf unautorisierte Scope-Erweiterung nicht rückwirkend legitimieren.

## 12. Qualification

Qualification bewertet mindestens:

- Ergebnis je Anforderung und Teilziel,
- Engineering Completion der übernommenen Changes,
- erforderliche Test Completion,
- Gate- und Reviewresultate,
- Architektur-, Dependency-, Security- und Datenwirkung,
- Dokumentations- und Directory-Konsistenz,
- offene Findings, Risiken, Schulden, Waiver und Deferrals,
- Project-New- und Managed-Project-Auswirkungen,
- SemVer- und Releasewirkung,
- vollständige Promotion dauerhafter Ergebnisse.

Ergebniswerte:

```text
qualified | qualified-with-deferrals | blocked | cancelled
```

`qualified-with-deferrals` ist nur zulässig, wenn die DoD es erlaubt und keine falsche MVP-, Pilot-, Security-, Persistence-, Canonicalization- oder Releasebehauptung entsteht.

Qualification aggregiert vorhandene Evidence. Technische Reports werden referenziert, nicht kopiert.

## 13. Closure, Promotion und Archivierung

### 13.1 Closure-Schritte

Ein Sprintabschluss umfasst mindestens:

1. DoD und Anforderungen bewerten,
2. Teilziele abschließen oder kontrolliert überführen,
3. ADRs, Konzepte, Standards und Requirements aktualisieren,
4. Debt, Risiken und Deviations in Register überführen,
5. SemVer-Impact und Releaseempfehlung dokumentieren,
6. temporäre Dokumente behandeln,
7. Completion Report finalisieren,
8. Statusdatei entfernen,
9. Sprint archivieren,
10. Index, Referenzen und Verzeichnisstand bereinigen.

### 13.2 Promotion

| Dauerhaftes Ergebnis | Kanonisches Ziel |
|---|---|
| Architekturentscheidung | ADR |
| zusammenhängendes Lösungsmodell | Architecture Concept |
| wiederverwendbare Detailregel | Standard |
| dauerhafte Anforderung | Requirements |
| Vorgehenswissen | Guide |
| technische Schuld | Debt Register |
| Risiko | Risk Register |
| lokale Abweichung | Deviation Register |
| datierter Befund | Report |

Promotion aktualisiert Referenzen und Index. Das Sprintartefakt darf danach nicht als konkurrierende aktive Quelle fortbestehen.

### 13.3 Temporäre Dokumente

Jedes temporäre Dokument erhält genau eine Entscheidung:

- `promote`,
- `aggregate`,
- `archive`,
- `discard`.

`archive` ist nur bei eigenständigem historischem Nachweiswert zulässig. `discard` entfernt das Dokument; Git bewahrt die Historie.

Der Solution Plan ist standardmäßig kein Archivartefakt. Er wird aggregiert, promoviert, begründet archiviert oder verworfen. `STATUS.md` wird nicht archiviert; sein Endstand steht im Completion Report.

### 13.4 Archivierungsbedingungen

Archivierung ist erst zulässig, wenn:

- Completion Report final ist,
- Sprint Brief den Abschluss- oder Abbruchstatus trägt,
- keine unbehandelten temporären Dokumente bestehen,
- Promotionen und Deferrals referenziert sind,
- Index und Pfade konsistent sind,
- erforderliche Sprint-Gates bestanden oder Blocker als Abbruch dokumentiert sind.

## 14. Completion Report

Der Completion Report enthält mindestens:

- Sprint-ID, Ziel und Baseline,
- Abschlussstatus,
- Ergebnis je Anforderung und Teilziel,
- DoD- und Qualification-Bewertung,
- akzeptierte Patches und relevante Commits,
- betroffene Komponenten,
- aktualisierte ADRs, Konzepte, Standards und Contracts,
- offene Findings, Risiken, Schulden und Deferrals,
- Behandlung temporärer Dokumente,
- SemVer-Empfehlung,
- Releaseentscheidung oder Verweis auf deren Ausstand,
- nicht erreichte Ziele und Folgebedarf.

Er ist ein kompakter Ergebnisnachweis, keine Sprintchronik. Rohlogs und generierte Reports werden referenziert. Ein finaler Report wird nicht still überschrieben; Korrekturen folgen der Documentation Governance.

## 15. Blockade, Abbruch und Cancellation

Ein blockierter Sprint nennt in `STATUS.md` Blocker, Auswirkung, Owner, erforderliche Entscheidung und nächstes Reviewdatum.

Bei `stop-and-replan` pausiert Execution. Eine Fortsetzung benötigt ein akzeptiertes Amendment oder einen neuen Sprint.

Cancellation benötigt einen finalen Completion Report mit Grund, erreichtem Stand, übernommenen und verworfenen Änderungen, verbleibenden Risiken und Schulden sowie Auswirkungen auf Requirements, Roadmap und Release. Ein abgebrochener Sprint darf keine Reife- oder Completionbehauptung erzeugen.

## 16. Version, Project-New und Managed Projects

Während des Sprints wird je betroffener Komponente der erwartete Impact geführt:

```text
none | patch | minor | major
```

Der Sprintabschluss empfiehlt den Impact. Die tatsächliche Version und Releasefreigabe bestimmt die Release and Version Governance.

Ein Sprint mit Managed-Project-Bezug unterscheidet read-only Analyse, planbare Delivery, autorisierten Apply und lokale Deviation. Ein Sprintplan autorisiert keine Zielprojektmutation.

Bei Project-New-Änderungen gehören Fresh-Project-Acceptance und Auswirkungen auf erzeugte Governance-, Test- und Verzeichnisstrukturen in DoD und Qualification.

## 17. Sprint Gate und Contracts

Mindestens erforderlich sind:

```text
contracts/governance/sprint/sprint-contract.json
contracts/governance/sprint/sprint-drift-contract.json
```

Der Sprint Contract konkretisiert ID-Muster, Pflichtdateien, Phasen, Teilziele, Pflichtfelder und Closure. Der Drift Contract konkretisiert Ereignisse, Kategorien, Ergebnisse und Amendments.

Das Sprint Gate prüft mindestens:

- vollständige Pflichtdateien und gültige Sprint-ID,
- genau eine Statusdatei,
- getrennten Problem- und Lösungsraum,
- vollständige DoR-, DoD- und Teilzielangaben,
- gültige Phasen- und Statuswerte,
- aktuelle Drift-Bewertung und gültige Amendments,
- Completion Report vor Archivierung,
- Behandlung temporärer Dokumente,
- Index- und Archivkonsistenz.

Das Gate folgt der Quality Gate Governance, beginnt report-only und benötigt positive, negative und Tool-Error-Fixtures. Contract und Gate dürfen keine neue Prozessregel einführen.

## 18. Project-New, Managed Projects und Transition

Project-New stellt profilgerecht registrierte Sprintpfade, Templates für die vier Pflichtdateien, Sprint Contracts, Sprint Gate und einen gültigen Index bereit. Gemeinsame Prinzipien erfordern keine identische Springmaster-Struktur in jedem Projekt.

Gemanagte Projekte dokumentieren den adoptierten Governance-Stand. Lokale Abweichungen benötigen eine Managed-Project-Deviation und dürfen Problem-/Lösungsraum, Status oder Closure nicht still aufheben.

Der aktuelle Springmaster-Bestand enthält unter anderem:

- `PROJECT_DOCS/GOVERNANCE/SPRINT_RELEASE_GOVERNANCE.md`,
- `SPRINT_P1_RUNTIME_CONTRACT_FOUNDATION.md`,
- `SPRINT_P2_MANAGED_TARGET_LIFECYCLE.md`,
- operative Pläne unter `PROJECT_DOCS/OPERATIONAL/`.

Vor Aktivierung wird deren Verantwortung aufgeteilt:

- Sprintidentität und Closure in diese Governance,
- Releasequalification in Release and Version Governance,
- Target Lifecycle in Managed Project Governance,
- historische Sprintsummaries in historische Completion Reports oder Reports,
- operative Legacy-Pläne in Archiv, Migration oder Retirement.

Die Migration erfolgt in begrenzten Patches. Neue Sprints verwenden nach Aktivierung das Zielmodell; Legacy-Pfade werden nicht für neue Sprintwahrheiten erweitert.

## 19. Kanonische Ausgaben und Abnahmekriterien

Diese Governance kontrolliert ausschließlich Sprintidentität, Sprintdokumente, Problem-/Lösungsraum, Phasen, Teilziele, Status, Drift, Amendments, Qualification, Closure und Archivierung.

Sie ist vollständig, wenn:

1. Sprint- und andere Identitäten getrennt sind,
2. Problem- und Lösungsraum getrennt geführt werden,
3. jede Phase einen Ausgang besitzt,
4. Teilziele messbar und evidence-basiert sind,
5. genau eine Statusquelle existiert,
6. Drift und Scopeänderungen kontrolliert sind,
7. DoR und DoD Fachabschlüsse korrekt referenzieren,
8. temporäre Inhalte vollständig behandelt werden,
9. dauerhafte Wahrheiten promoviert werden,
10. Completion und Cancellation unterscheidbar sind,
11. SemVer-Empfehlung und Releaseentscheidung getrennt bleiben,
12. Project-New und Managed Projects profiliert berücksichtigt sind,
13. Bestandsdokumente migrationsfähig bleiben,
14. Contract und Gate eindeutig ableitbar sind,
15. menschliche und automatisierte Ausführung dieselbe Bedeutung ableiten.

### 19.1 Technischer Umsetzungsstand

Die report-only Erstimplementierung umfasst:

- `contracts/governance/sprint/sprint-contract.json`,
- `contracts/governance/sprint/sprint-drift-contract.json`,
- vier spezialisierte Templates für Sprint Brief, Solution Plan, Status und Completion Report,
- `bin/sprint-gate.py` und den Shell-Einstieg,
- positive, negative und Tool-Error-Fixtures,
- vollständige Prüfung aktiver und archivierter Sprints sowie Changed-to-All-Erweiterung bei Contractänderungen.

Der aktuelle Springmaster-Bestand enthält noch keinen Sprint unter `PROJECT_DOCS/SPRINTS/`; der Baseline-Scan ist daher ohne Transition-Ausnahme grün. Neue Sprintinstanzen müssen den Contract sofort vollständig erfüllen.

Vor einer Aktivierung oder Strict-Promotion bleiben offen:

- kontrollierte Materialisierung in Project-New,
- ein erster realer Springmaster-Pilotsprint im Zielpfad,
- Abgleich mit Managed-Project-Adoption und Release Closure,
- Promotionentscheidung nach Quality Gate Governance.

## 20. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | – | draft | Konsolidierter Volltextentwurf mit getrenntem Problem- und Lösungsraum |
| 2026-07-23 | draft | draft | Report-only Sprint und Drift Contracts, Templates, Gate und Fixtures technisch abgeleitet; Aktivierung bleibt offen |

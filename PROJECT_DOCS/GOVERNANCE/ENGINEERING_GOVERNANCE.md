---
documentId: DOC-GOV-0003
title: Engineering Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/engineering
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-22
validFrom: null
lastReviewedAt: null
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Engineering Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie ein technischer Änderungsschnitt von der Aufnahme bis zum qualifizierten Abschluss geführt wird.

Sie bestimmt:

- Change Scope, Baseline und Nicht-Ziele,
- Änderungsklassen und technische Risikostufen,
- Ermittlung relevanter Regelquellen,
- Bildung des kleinsten vollständigen Änderungsschnitts,
- Auswahl der Engineering-Profile,
- Engineering Readiness und Engineering Completion,
- Verantwortlichkeiten und minimale Abschluss-Evidence.

Sie gilt für Änderungen an Code, Contracts, Tests, Tooling, Templates, Build, Dokumentation, Governance, Platform Update und Lieferartefakten.

Für menschliche, automatisierte und KI-gestützte Entwicklung gelten dieselben Quellen, Scopes, Prüfungen und Abschlusskriterien. Diese Governance formuliert keine Sonderregeln für eine bestimmte ausführende Instanz.

## 2. Abgrenzung und kanonische Verantwortung

Diese Governance ist die kanonische Quelle für:

- Engineering-Lifecycle eines Änderungsschnitts,
- Change Scope und Baseline-Ermittlung,
- Engineering-Änderungs- und Risikoklassen,
- Auswahl und Zweck der Engineering-Profile,
- Engineering Readiness und Completion,
- technischen Abschlussstatus,
- minimale prozessbezogene Engineering-Evidence.

Nicht hier geregelt werden:

| Gegenstand | Kanonische Quelle |
|---|---|
| konkrete Coding-, Architektur-, API-, Persistenz- oder Security-Regeln | ADRs und technische Standards |
| Testportfolio, Testszenarien, Coverage und Testabschluss | Test Governance und Testing Standard |
| Gate-Ergebnisse, Rule Lifecycle, report-only, strict, Baselines, Waiver und Suppressions | Quality Gate Governance |
| Aufnahme externer Abhängigkeiten | Dependency Governance |
| Dokumenttypen und Dokumentstatus | Documentation Governance |
| physische Ablage und Strukturmigration | Project Directory Governance |
| Sprintauftrag, Drift und Sprintabschluss | Sprint Governance |
| Releaseentscheidung und Versionierung | Release and Version Governance |
| konkrete Kommandos und Beispiele | Development Guide und ausführbares Tooling |

Diese Governance referenziert Ergebnisse dieser Quellen, wiederholt ihre Detailregeln aber nicht.

## 3. Begriffe und Grundsätze

### 3.1 Begriffe

| Begriff | Bedeutung |
|---|---|
| Änderungsschnitt | kleinste fachlich oder technisch geschlossene Menge zusammengehöriger Änderungen |
| Change Scope | beabsichtigtes Ergebnis, betroffene Bereiche und ausdrückliche Nicht-Ziele |
| Baseline | eindeutig identifizierter Ausgangszustand der Änderung |
| Engineering-Profil | benannte, reproduzierbare Auswahl erforderlicher Prüfklassen |
| Engineering Readiness | technischer Zustand, in dem die Änderung kontrolliert begonnen werden kann |
| Engineering Completion | technischer Zustand, in dem die Änderung vollständig umgesetzt und qualifiziert ist |
| Fremdänderung | vorhandene Änderung außerhalb des autorisierten Change Scopes |
| Deferral | explizit verschobener und nachverfolgter Restgegenstand |

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

### 3.2 Kleinster vollständiger Schnitt

Ein Änderungsschnitt MUSS klein genug sein, um vollständig verstanden, geprüft und zurückgeführt werden zu können. Er MUSS zugleich alle Teile enthalten, die für eine konsistente Änderung des betroffenen Vertrags erforderlich sind.

Insbesondere dürfen nicht ohne begründeten Übergang getrennt bleiben:

- Implementierung und erforderliche Tests,
- Contract und Contract-Verifikation,
- Regeländerung und zugehörige Fixtures,
- Template-Änderung und Template-Acceptance,
- neue Dependency und ihre Genehmigung,
- Architekturänderung und erforderliche Entscheidungs- oder Standardänderung.

### 3.3 Keine fachfremden Nebenänderungen

Ein Änderungsschnitt DARF keine unverbundenen Refactorings, Formatierungswellen, Dateiverschiebungen oder Nachbarbereinigungen enthalten.

Eine erkannte Verbesserung außerhalb des Scopes wird separat geplant, als technische Schuld registriert oder ausdrücklich verworfen.

### 3.4 Keine stillen Vertragsänderungen

Ein geltender Vertrag DARF nicht ausschließlich durch neues Implementierungsverhalten verändert werden.

Betroffene normative Quellen, Contracts, Tests, Fixtures und aktuelle Evidence müssen nach Abschluss dieselbe Aussage treffen.

### 3.5 Bestehendes Verhalten nicht vermuten

Öffentliche, persistente, sicherheitsrelevante oder wiederverwendbare Verträge DÜRFEN nicht aus Vermutung abgeleitet werden. Vor einer Verhaltensänderung MUSS das Ist-Verhalten anhand geeigneter Quellen oder Charakterisierungstests bestimmt werden.

### 3.6 Risikobasierte und gestufte Verifikation

Die Prüftiefe richtet sich nach Änderungsklasse, Vertragswirkung, Kritikalität, Reversibilität und Auswirkung auf Project-New oder gemanagte Projekte.

Nach der Umsetzung wird zuerst die engste aussagekräftige Prüfung ausgeführt. Danach folgen die erforderlichen breiteren Profile. Eine gezielte Prüfung ersetzt Qualification nicht.

### 3.7 Keine implizite Korrektur

Prüf- und Qualifikationsläufe DÜRFEN versionierte Quellen nicht still verändern. Automatische Korrekturen sind nur als eigener Arbeitsschritt zulässig und durchlaufen anschließend denselben Engineering-Prozess.

## 4. Quellen und Konflikte

Abhängig vom Scope werden mindestens geprüft:

1. akzeptierte ADRs,
2. aktive Governance-Dokumente und Standards,
3. zugehörige maschinenlesbare Contracts,
4. Code, Tests und Fixtures als Ist-Baseline,
5. aktuelle Evidence- und Reifeaussagen,
6. aktuelle Komponenten- und Plattformversionen,
7. Planungs- und Sprintdokumente als Arbeitskontext.

Diese Liste ist keine pauschale Vorrangfolge: normative Quellen definieren das Soll, Code und Tests belegen die Implementierung, Evidence belegt einen konkreten Prüfstand.

Bei Widersprüchen DARF nicht geraten oder eine Quelle still ausgewählt werden. Der Konflikt MUSS auf Scope und Aussage eingegrenzt, anhand von Autorität, Status und Gültigkeit bewertet und in den kanonischen Quellen aufgelöst werden.

Ein grüner Test hebt keine normative Regel auf. Eine normative Regel allein beweist nicht ihre korrekte Implementierung.

## 5. Verantwortlichkeiten

### 5.1 Change Owner

Der Change Owner verantwortet:

- eindeutiges Ergebnis, Scope und Nicht-Ziele,
- Klassifikation und Risikostufe,
- Ermittlung relevanter Regelquellen,
- Vollständigkeit des Änderungsschnitts,
- Auswahl und Ausführung erforderlicher Profile,
- Behandlung offener Punkte,
- vollständige Abschluss-Evidence.

### 5.2 Reviewer

Der Reviewer bewertet:

- Geschlossenheit und Angemessenheit des Scopes,
- Einhaltung relevanter Quellen,
- Risiko und Prüftiefe,
- nicht automatisierbare semantische Aspekte,
- Plausibilität der Abschlussbewertung.

Automatisierte Prüfungen ersetzen kein Review, wenn eine Regel ausdrücklich manuelle oder architektonische Bewertung benötigt.

### 5.3 Maintainer

Die Maintainer verantworten:

- Freigabe normativer Änderungen,
- Auflösung konkurrierender Regelquellen,
- neue Änderungsklassen oder Engineering-Profile,
- Akzeptanz wesentlicher High- oder Critical-Risiken,
- Governance-übergreifende Konsistenz.

High- und Critical-Änderungen SOLLEN durch eine zweite verantwortliche Instanz geprüft werden. Ist dies nicht möglich, müssen fehlende Trennung, Risiko und kompensierende Prüfung in der Evidence dokumentiert werden.

## 6. Change Scope und Baseline

### 6.1 Change Scope

Vor Umsetzung MUSS der Scope mindestens enthalten:

- gewünschtes Ergebnis,
- betroffene Anforderung oder technischen Anlass,
- betroffene Komponenten, Verträge oder Pfade,
- ausdrückliche Nicht-Ziele,
- erwartete Test-, Dokumentations-, Dependency- und Versionswirkung,
- bekannte Risiken und Abhängigkeiten.

Eine materielle Scope-Erweiterung benötigt eine erneute Bewertung von Klassen, Risiko und Profilen.

### 6.2 Baseline

Vor einer Änderung MUSS die tatsächliche Baseline ermittelt werden. Dazu gehören, soweit anwendbar:

- aktueller Git-Stand und Working Tree,
- vorhandene Änderungen,
- relevante Komponenten- und Contract-Versionen,
- bestehendes Verhalten,
- Tests und Fixtures,
- aktuelle Findings, Waiver, Deviations und Deferrals.

### 6.3 Fremdänderungen

Fremdänderungen DÜRFEN nicht still übernommen, zurückgesetzt, überschrieben oder im selben Abschluss qualifiziert werden.

Der Änderungsschnitt MUSS so begrenzt oder isoliert werden, dass Wirkung und Evidence unterscheidbar bleiben.

Eine Dirty Baseline kann für Analyse oder begrenzte Entwicklung verwendet werden, wenn ihre Abweichungen vollständig bekannt sind. Für Handoff, Release oder qualifizierte Patch-Annahme gelten die strengeren Regeln der zuständigen Quellen.

## 7. Änderungsklassifikation

Ein Änderungsschnitt KANN mehrere Klassen besitzen. Dann gelten die Anforderungen aller betroffenen Klassen.

| Klasse | Typische Änderung |
|---|---|
| `documentation` | erläuternde Dokumentation ohne normative oder technische Wirkung |
| `governance` | Governance, Statusmodell oder Prozessregel |
| `standard` | normative technische Detailregel |
| `adr` | dauerhafte Architekturentscheidung |
| `contract` | maschinenlesbarer Vertrag, Schema, OpenAPI oder Registry |
| `fixture` | Golden Fixture, Referenzreport oder Testfixture |
| `java-core` | wiederverwendbarer fachfreier Core |
| `java-application` | ausführbare Springmaster-Anwendung |
| `java-demo` | Demo- oder Referenzslice |
| `api` | öffentliche oder interne Schnittstelle |
| `persistence` | Persistenz, Liquibase oder DBTool-Vertrag |
| `security` | Authentisierung, Autorisierung oder Permission-Vertrag |
| `test` | Test-Harness, Testcode, Testdaten oder Coverage-Konfiguration |
| `tooling` | Bash-, Python- oder Java-Tooling |
| `template` | Projekt-, Code- oder Konfigurationstemplate |
| `dependency` | Dependency, Plugin, Framework, Codegenerator oder externe CLI |
| `build` | Maven-Struktur, Profile, Packaging oder Buildumgebung |
| `quality-rule` | technisch prüfbare Qualitäts- oder Architekturregel |
| `platform-update` | Planung, Generierung, Kompatibilität oder Mutation von Zielprojekten |
| `managed-project-delivery` | qualifizierte Lieferung an ein gemanagtes Projekt |
| `release` | Release Build, Version oder Distribution |

Eine Markdown-Änderung ist nur dann ausschließlich `documentation`, wenn sie keine normative Regel, Architekturentscheidung, Reifeaussage, Statuswirkung, Versionierungsentscheidung oder technische Semantik verändert.

Die Klassifikation MUSS in der Engineering-Evidence ausgewiesen werden. Eine relevante Klasse darf nicht ausgelassen werden, um ein weniger umfangreiches Profil zu erhalten.

## 8. Technische Risikoklassifikation

| Stufe | Typische Merkmale |
|---|---|
| `low` | lokal, leicht reversibel, keine Vertrags-, Runtime-, Daten- oder Sicherheitswirkung |
| `medium` | internes Verhalten oder mehrere Klassen eines begrenzten Moduls; zusätzliche Tests erforderlich |
| `high` | öffentlicher oder wiederverwendbarer Vertrag, Persistenz, Security, neue Dependency, Project-New, Platform Update oder strict-relevante Regel |
| `critical` | irreversible Datenwirkung, zentrale Sicherheits- oder Integritätsgrenze, breite automatische Migration oder begrenzte Rückrollmöglichkeit |

Bei mehreren Auswirkungen gilt die höchste zutreffende Stufe. Eine niedrigere Einstufung benötigt eine dokumentierte Begründung.

Mit steigender Risikostufe steigen Auswirkungsanalyse, Prüftiefe, Reviewtiefe, Rückrollbetrachtung und Evidence-Umfang. Konkrete Teststufen und Gate-Inhalte bestimmen die zuständigen Governance-Dokumente und Contracts.

## 9. Engineering-Lifecycle

### 9.1 Intake und Readiness

Vor Beginn werden Ergebnis, Scope, Nicht-Ziele, Klassen, vorläufiges Risiko, relevante Quellen, Profile, Blocker und Abhängigkeiten bestimmt.

Ein Änderungsschnitt ist engineering-ready, wenn:

1. Ergebnis, Scope und Nicht-Ziele eindeutig sind,
2. Baseline und Fremdänderungen bekannt sind,
3. relevante Regelquellen identifiziert sind,
4. Klassen und vorläufiges Risiko bestimmt sind,
5. erforderliche Profile absehbar sind,
6. notwendige Entscheidungen vorliegen oder Teil des Scopes sind,
7. Blocker benannt sind,
8. der Schnitt ohne unkontrollierte Fremdänderungen bearbeitet werden kann.

Engineering Readiness ist technischer Bestandteil der Sprint Definition of Ready, aber nicht mit ihr identisch.

### 9.2 Ist-Verhalten und Auswirkungen

Vor einer Verhaltensänderung werden geeignete Nachweise für das Ist-Verhalten bestimmt, etwa Tests, Fixtures, Spezifikationen, Reports oder Charakterisierungstests.

Soweit anwendbar werden Architektur-, Vertrags-, Test-, Dependency-, Build-, Security-, Daten-, Migrations-, Dokumentations-, Versions-, Project-New- und Managed-Project-Wirkung bewertet.

### 9.3 Planung und Umsetzung

Der geplante Schnitt MUSS ein geschlossenes Ergebnis, Akzeptanzkriterien, erforderliche Evidence und Profile besitzen. High- und Critical-Änderungen benötigen Stop- und Abbruchkriterien.

Während der Umsetzung gilt:

- nur der autorisierte Scope wird geändert,
- Vertragsänderungen werden in ihren kanonischen Quellen geführt,
- neue Strukturen und Dependencies folgen ihrem Prozess,
- Fixtures werden nur bei beabsichtigter Vertragsänderung aktualisiert,
- Prüfungen werden nicht still deaktiviert,
- Findings werden nicht ohne zulässige Grundlage unterdrückt.

### 9.4 Verifikation und Qualification

Zuerst wird die engste aussagekräftige Prüfung ausgeführt. Fehlschläge werden ursächlich analysiert.

Vor Abschluss MUSS das aus Klassen und Risiko abgeleitete Qualification-Profil ausgeführt werden. Es umfasst die durch Test Governance, Quality Gate Governance, Dependency Governance und Standards geforderten Prüfungen.

Prüfresultate MÜSSEN inhaltlich ausgewertet werden. Zu unterscheiden sind mindestens erfolgreiche Nachweise, blockierende Ergebnisse, nicht blockierende Findings, nicht ausgeführte Prüfungen, Tool Error und bekannte Bestandsabweichungen.

### 9.5 Abschluss

Vor Abschluss werden:

- geplanter und tatsächlicher Scope abgeglichen,
- Findings behandelt oder nachverfolgt,
- Schulden, Risiken und Deferrals registriert,
- normative Quellen und Contracts konsolidiert,
- Versions- und Propagationswirkungen bewertet,
- Engineering-Evidence finalisiert.

## 10. Engineering-Profile

Jedes Profil MUSS einen eindeutigen Zweck besitzen, aus Klassen und Risiko deterministisch auswählbar sein, seine Prüfklassen sichtbar machen und reproduzierbare Evidence erzeugen.

| Profil | Zweck |
|---|---|
| `fast` | kurze lokale, bevorzugt changed-scope-begrenzte Rückkopplung während der Umsetzung |
| `qualification` | vollständiger technischer Nachweis für den Änderungsschnitt |
| `audit` | vollständige Bestandsprüfung unabhängig vom einzelnen Change Scope |
| `release` | Qualification und erforderliches Audit um Veröffentlichungs- und Distributionsnachweise erweitern |

Das Fast Profile ersetzt Qualification nicht. Ein Änderungsschnitt darf ohne erfolgreich abgeschlossenes Qualification Profile nicht engineering-complete sein.

Audit ist insbesondere für Governance- und Strukturmigrationen, Regelpromotions, periodische Qualitätsprüfungen und Release-Vorbereitung vorgesehen.

Ein höheres Profil ersetzt ein niedrigeres nur, wenn sein Contract alle für den Scope erforderlichen Prüfklassen enthält. Ein verpflichtendes Profil ist nur dann nicht anwendbar, wenn dies aus Scope und Contract eindeutig folgt.

## 11. Engineering Completion und Abschlussstatus

Ein Änderungsschnitt ist engineering-complete, wenn:

1. tatsächlicher und akzeptierter Scope übereinstimmen,
2. keine unverbundenen Nebenänderungen enthalten sind,
3. relevante ADRs, Governance-Dokumente und Standards eingehalten oder sichtbar aktualisiert sind,
4. Code, Contracts, Tests, Fixtures, Evidence und Dokumentation dieselbe Aussage treffen,
5. erforderliche Profile ausgeführt und bewertet wurden,
6. keine offenen Tool- oder Ausführungsfehler bestehen,
7. alle blockierenden Ergebnisse aufgelöst sind,
8. nicht blockierende Findings bewertet und nachverfolgt sind,
9. Dependencies und Strukturänderungen nach ihrem Prozess behandelt sind,
10. Versions-, Project-New- und Managed-Project-Auswirkungen bewertet sind,
11. Schulden, Risiken und Deferrals registriert sind,
12. keine Secrets, unzulässigen Runtime-Artefakte oder Fremdänderungen enthalten sind,
13. keine unbelegte Reife-, Security-, Persistenz-, Strict-Gate- oder Lieferbehauptung besteht,
14. die Engineering-Evidence vollständig ist.

Engineering Completion ist technischer Bestandteil der Sprint Definition of Done. Sie ersetzt weder Sprintabschluss noch Releaseentscheidung.

| Status | Bedeutung |
|---|---|
| `qualified` | alle Completion-Kriterien erfüllt |
| `qualified-with-findings` | Completion erfüllt; nur akzeptierte nicht blockierende Findings offen |
| `blocked` | mindestens eine verbindliche Abschlussanforderung nicht erfüllt |
| `incomplete` | Umsetzung, Prüfung oder Evidence noch nicht vollständig |
| `cancelled` | Änderungsschnitt beendet und nicht übernommen |

`qualified-with-findings` ist nur zulässig, wenn keine falsche Reife-, Sicherheits- oder Vollständigkeitsbehauptung entsteht. `incomplete` darf nicht als abgeschlossen kommuniziert werden.

## 12. Engineering-Evidence

Für einen qualifizierten Änderungsschnitt MUSS die Evidence mindestens enthalten:

- Change- oder Slice-Referenz,
- Baseline und Change Scope,
- Änderungsklassen und Risikostufe,
- betroffene Anforderungen und Regelquellen,
- ausgeführte Profile und Prüfungen,
- Ergebnisse und nicht ausgeführte Prüfungen mit Begründung,
- offene Findings, Deferrals und technische Schulden,
- Versions-, Project-New- und Managed-Project-Auswirkung,
- geänderte Artefaktfamilien,
- technischen Abschlussstatus.

Maschinenlesbare Reports und ein kompakter menschenlesbarer Abschluss ergänzen einander. Die Feldstruktur wird im Engineering-Evidence-Contract festgelegt.

Generierte Evidence ist ein technisches Artefakt und wird in einem registrierten Pfad erzeugt. Sie darf nicht als manuell gepflegte zweite Wahrheit in die Dokumentation kopiert werden.

## 13. Beziehung zu Sprint, Patch, Release und Projektprofilen

Ein Sprint kann mehrere Änderungsschnitte enthalten. Jeder Schnitt durchläuft diesen Engineering-Lifecycle; Sprintziel, Drift und Sprintabschluss bleiben Eigentum der Sprint Governance.

Änderungsschnitt, Sprint-ID, Patch-ID, Artifact-ID und Git-Commit sind unabhängige Identitäten. Die konkrete Patch- und Git-Transaktion bestimmen die zuständigen Tooling- und Patchregeln.

Engineering Completion beweist technische Qualifikation, erteilt aber keine Releasefreigabe und legt keine Version fest.

Project-New MUSS einen nutzbaren Engineering-Harness mit anwendbaren Klassen, Profilen, Contracts, Test- und Gate-Einstiegen sowie Evidence-Ausgabe bereitstellen. Ein frisch erzeugtes Projekt muss seine Qualification ohne manuelle Strukturreparatur ausführen können.

Gemanagte Projekte adoptieren Regeln anhand eines identifizierbaren Springmaster-Stands. Lokale Ergänzungen und Deviations regelt die Managed Project Governance. Eine read-only Prüfung autorisiert keine Mutation.

Gemeinsame Engineering-Prinzipien verlangen keine identischen Repositorystrukturen oder alle Springmaster-spezifischen Profile in Fachprojekten.

## 14. Maschinenlesbare Ableitungen und Transition

Mindestens erforderlich sind:

```text
contracts/governance/engineering/change-classification-contract.json
contracts/governance/engineering/engineering-profile-contract.json
contracts/governance/engineering/engineering-evidence-contract.json
contracts/governance/engineering/engineering-completion-contract.json
```

Der Project Directory Contract bestimmt die endgültigen Pfade. Die Contracts konkretisieren Klassen, Risikokriterien, deterministische Profilzuordnung, Evidence-Felder und die vierzehn Completion-Kriterien, dürfen aber keine neue normative Prozessregel einführen.

Die Contract-Familie ist seit `SPRINGMASTER-SPRINT-001`, Slice S-01, als report-only Foundation materialisiert. `bin/engineering-contracts.py` validiert die Verträge sowie Classification-, Evidence- und Completion-Records. Der Validator ist noch kein Engineering-Qualification-Gate und erteilt weder Strict-Promotion noch Releasefreigabe. Seine positiven, negativen und Tool-Error-Szenarien liegen unter `src/test/resources/tooling/engineering-contracts-v1/`.

Die aktuelle `AGENTS.md` enthält bereits belastbare Regeln zu Baseline, Klassifikation, kleinstem vollständigen Schnitt, risikobasierter Verifikation und Definition of Done. Diese Governance konsolidiert sie kanonisch; die `AGENTS.md` bleibt anschließend ein kompakter Einstieg.

Bestehende Prüfkommandos bleiben bis zur Einführung der Profile gültige Bestandsanweisungen. Ihre spätere Zuordnung erfolgt in Contracts und Development Guide. Diese Governance verlangt keine sofortige Umbenennung oder neue Orchestrierung.

Die Aktivierung dieser Governance promotet keine bestehende Regel und kein Gate automatisch zu strict.

## 15. Kanonische Ausgaben und Abnahmekriterien

Diese Governance kontrolliert ausschließlich:

- Engineering-Änderungs- und Risikoklassen,
- Engineering-Lifecycle,
- Auswahl und Zweck der Engineering-Profile,
- Engineering Readiness und Completion,
- technischen Abschlussstatus,
- minimale Engineering-Evidence.

Sie ist inhaltlich vollständig, wenn:

1. jeder technische Änderungsschnitt klassifizierbar ist,
2. Risiko und erforderliche Profile nachvollziehbar bestimmbar sind,
3. Baseline und Fremdänderungen zwingend berücksichtigt werden,
4. der Lifecycle vom Intake bis zum Abschluss geschlossen ist,
5. Readiness und Completion eindeutig definiert sind,
6. Completion von Sprintabschluss und Releaseentscheidung getrennt ist,
7. minimale Evidence vollständig bestimmt ist,
8. keine Gate-, Test-, Dependency- oder Coding-Detailregel dupliziert wird,
9. Project-New und Managed Projects profilgerecht berücksichtigt sind,
10. die Regeln in maschinenlesbare Contracts überführbar sind,
11. der Ablauf für menschliche und automatisierte Ausführung gleich interpretierbar ist.

## 16. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Konsolidierter Volltextentwurf auf Basis des verifizierten Springmaster-Bestands |
| 2026-07-23 | draft | draft | S-01 materialisiert Classification-, Profile-, Evidence- und Completion-Contracts als report-only Foundation. |

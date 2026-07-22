---
documentId: DOC-GOV-0006
title: Dependency Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/dependencies
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

# Dependency Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie externe Softwareabhängigkeiten begründet, bewertet, genehmigt, eingeführt, versioniert, überprüft, aktualisiert und entfernt werden.

Sie gilt für:

- Maven-Dependencies und Maven-Plugins,
- Frameworks und Codegeneratoren,
- externe CLI- und Analysewerkzeuge,
- Runtime-, Compile-, Provided- und Testabhängigkeiten,
- direkte und transitive Abhängigkeiten,
- vendorte oder eingebettete Fremdkomponenten,
- Springmaster, Project-New sowie adoptierte Regeln in erzeugten und gemanagten Projekten.

Ziel ist ein kleiner, nachvollziehbarer, sicher aktualisierbarer und entfernbarer Abhängigkeitsbestand. Eine neue Dependency darf nicht allein aus Bequemlichkeit oder kurzfristiger Implementierungsgeschwindigkeit eingeführt werden.

## 2. Kanonische Verantwortung und Abgrenzung

Diese Governance ist die kanonische Quelle für:

- Dependency-Klassen und Entscheidungstiefe,
- Notwendigkeits- und Alternativenprüfung,
- Dependency Request und Genehmigung,
- Approved-, Conditional-, Experimental- und Banned-Modell,
- Versionsquellen und BOM-Grundsätze,
- transitive, Lizenz- und Security-Bewertung,
- Review, Upgrade, Entfernung und Exit Strategy,
- Anforderungen an Dependency-Evidence und Dependency Gate.

| Nicht hier geregelt | Kanonische Quelle |
|---|---|
| Architekturentscheidung für Framework oder Codegenerator | zuständige ADR |
| Engineering-Lifecycle und Risikoklassifikation | Engineering Governance |
| Gate-Ergebnis, Promotion, Waiver und Suppression | Quality Gate Governance |
| Maven-Struktur, Plugin-Konfiguration und Exit-Codes | Build and Tooling Standard |
| konkrete erlaubte und verbotene Artifacts | maschinenlesbarer Dependency Contract |
| konkrete Produkt- und Komponentenversionen | `pom.xml`, Version Contracts und Release and Version Governance |
| projektlokale Abweichung eines gemanagten Projekts | Managed Project Governance |

Die Governance besitzt Prozess und Lifecycle. Artifact-Listen und technische Parameter werden in Contracts geführt.

## 3. Bestehende Baseline und Transition

### 3.1 Springmaster

Die aktuelle Baseline verwendet Java 21, Maven, Spring-Boot-Dependency-Management, Spring Boot Starter, Springdoc, Liquibase, MariaDB, H2 für Tests, Spring Boot Test und versionierte Build-Plugins einschließlich CycloneDX.

Diese Beschreibung ist keine zweite Registry. Die aktuelle technische Wahrheit verbleibt in `pom.xml`, dem effektiven Dependency Graph und daraus erzeugter SBOM.

### 3.2 Project-New

Die Project-New-Template-Quelle besitzt eine eigene kleinere Maven-Baseline. Sie darf nicht automatisch alle Springmaster-Dependencies übernehmen.

### 3.3 Übergangsstatus

Vorhandene direkte Dependencies und Plugins gelten während der Migration als `legacy-approved`. Vor einer Strict-Aktivierung des Dependency Gates müssen sie:

1. inventarisiert,
2. klassifiziert,
3. Zweck, Owner und Versionsquelle zugeordnet,
4. in die Approved Registry übernommen

werden.

Neue Dependencies dürfen nicht nachträglich als `legacy-approved` deklariert werden.

## 4. Begriffe und Dependency-Klassen

### 4.1 Begriffe

| Begriff | Bedeutung |
|---|---|
| direkte Dependency | ausdrücklich im Build- oder Toolvertrag deklarierte Abhängigkeit |
| transitive Dependency | durch eine direkte Dependency eingebrachte Abhängigkeit |
| Dependency Request | dokumentierter Antrag zur Einführung oder wesentlichen Änderung |
| Approved Registry | maschinenlesbare Liste genehmigter direkter Dependencies und Plugins |
| Banned Registry | maschinenlesbare Verbotsliste |
| Versionsquelle | BOM, Parent, zentrale Property oder genehmigter Pin |
| Exit Strategy | Vorgehen für Update, Ersatz oder Entfernung |
| Framework | Dependency mit breiter struktureller oder Laufzeitwirkung |
| Codegenerator | Tool, das versionierte Quellen, Contracts oder Artefakte erzeugt |
| vendorte Komponente | Fremdinhalt, der in Repository oder Distribution kopiert wird |

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

### 4.2 Klassen und Mindestverfahren

| Klasse | Mindestverfahren |
|---|---|
| bestehende genehmigte Dependency im erlaubten Scope | normaler Engineering-Change |
| neue Test-Dependency ohne Runtime-Wirkung | vereinfachtes Dependency Review |
| neue Runtime-Dependency | vollständiges Dependency Review |
| Build Plugin oder externe CLI | vollständiges Review und Tooling-Auswirkung |
| Framework oder Codegenerator | vollständiges Review und ADR |
| vendorte Komponente | vollständiges Review, Lizenz- und Updatekonzept, regelmäßig ADR |
| transitive Dependency | Graph-, Lizenz- und Security-Prüfung |

Bei Mehrfachklassifikation gilt das strengste Verfahren.

## 5. Grundsätze

### 5.1 Bedarf vor Einführung

Eine neue Dependency MUSS eine konkret benannte Fähigkeitslücke schließen. Der Request beschreibt Anforderungsbezug, Scope, Nutzen und geprüfte Alternativen.

### 5.2 Plattformmittel zuerst

Vor einer neuen Dependency werden geprüft:

1. JDK und Standardbibliothek,
2. Spring Boot und vorhandene Starter,
3. bestehende genehmigte Dependencies,
4. eine kleine lokal beherrschbare Implementierung,
5. neue externe Dependency.

Eine lokale Implementierung ist nicht automatisch besser; Wartung, Sicherheit, Komplexität und Testbarkeit sind mitzubewerten.

### 5.3 Kleinste hinreichende Lösung

Es SOLL die kleinste Dependency gewählt werden, die den erforderlichen Vertrag zuverlässig erfüllt. Große Starter oder Frameworks benötigen eine Begründung, wenn nur ein kleiner Teil ihrer Funktion genutzt wird.

### 5.4 Transitive Gesamtwirkung

Bewertet wird der relevante transitive Graph, nicht nur das direkte Artifact. Größere Runtime-, Lizenz- oder Sicherheitsflächen benötigen eine begründete Entscheidung.

### 5.5 Zentrale Versionen

Versionen MÜSSEN über eine definierte Quelle geführt werden. Verboten sind:

- dynamische Versionsbereiche,
- `LATEST` oder `RELEASE`,
- unkontrollierte externe Snapshots,
- dieselbe Version an mehreren manuell gepflegten Stellen,
- Einzelversionen entgegen einer geltenden BOM ohne Begründung.

### 5.6 Keine stille Build-Erweiterung

Eine Dependency, ein Plugin oder ein externes Tool DARF nicht ausschließlich durch Änderung von `pom.xml`, Skript oder CI-Konfiguration eingeführt werden. Genehmigung, Registry, Implementierung, Tests und Evidence bilden einen Änderungsschnitt.

### 5.7 Reproduzierbarkeit und Exit-Fähigkeit

Externe Werkzeuge und Libraries müssen eindeutig versionierbar und in lokaler sowie CI-Qualifikation reproduzierbar sein.

Wesentliche Dependencies MÜSSEN aktualisierbar, ersetzbar oder entfernbar bleiben. Fremdtypen SOLLEN nicht ohne Not in öffentliche Springmaster-Verträge gelangen.

### 5.8 Keine versteckte Architekturentscheidung

Eine Dependency darf keine neue Architektur, Runtime-Plattform, Persistenz-, Security- oder Codegenerierungsstrategie stillschweigend etablieren. Solche Wirkungen benötigen die zuständige ADR oder Standardänderung.

## 6. Entscheidungstiefe und Genehmigung

### 6.1 Normale Nutzung

Ein normaler Engineering-Change genügt, wenn Artifact, Scope, Modul und Projektprofil bereits genehmigt sind und keine neue öffentliche oder architektonische Wirkung entsteht.

### 6.2 Vereinfachtes Review

Ein vereinfachtes Review ist für eine neue Test-Dependency zulässig, wenn:

- ausschließlich Test-Scope gilt,
- keine Runtime-, Distribution- oder Infrastrukturwirkung entsteht,
- Lizenz und Security nach aktiver Policy zulässig sind,
- der transitive Graph begrenzt ist,
- die Dependency ohne Produktmigration entfernbar bleibt.

Request, Registry-Eintrag, Tests und technische Prüfung bleiben erforderlich.

### 6.3 Vollständiges Review

Ein vollständiges Review ist mindestens erforderlich bei:

- Runtime-Dependency,
- Build Plugin oder externer CLI,
- explizitem Pin außerhalb einer BOM,
- wesentlicher transitiver Erweiterung,
- neuer Lizenz- oder Sicherheitsklasse,
- Wirkung auf Project-New oder gemanagte Projekte,
- Major Upgrade oder vendorter Komponente.

### 6.4 ADR-Pflicht

Eine akzeptierte ADR ist zusätzlich erforderlich bei:

- Framework oder Codegenerator,
- prägender öffentlicher API-Wirkung,
- neuem Runtime-Container oder grundlegender Infrastrukturabhängigkeit,
- vendorter Kernkomponente,
- grundlegender Änderung der Dependency- oder Distributionsstrategie.

### 6.5 Genehmigungsverantwortung

| Entscheidung | Genehmigung |
|---|---|
| neue Test-Dependency im vereinfachten Review | Change Review und Springmaster Maintainer |
| Runtime-Dependency oder Build Plugin | vollständiges Review und Springmaster Maintainer |
| Framework, Codegenerator oder öffentliche API-Wirkung | akzeptierte ADR und Springmaster Maintainer |
| lizenz- oder sicherheitsbezogene Ausnahme | zuständige Policy-Entscheidung; technischer Waiver allein genügt nicht |
| lokale Abweichung eines gemanagten Projekts | Managed-Project-Deviation |

## 7. Dependency Request und Bewertung

### 7.1 Pflichtinhalt

Ein Request enthält mindestens:

- Request-ID und Owner,
- Dependency oder Toolfamilie,
- Klasse, Scope, Module und Projektprofile,
- Fähigkeitslücke und Anforderungsbezug,
- geprüfte Alternativen,
- erwarteten Nutzen,
- Architektur-, transitive, Lizenz- und Security-Wirkung,
- Test- und Qualifikationsplan,
- Versionsquelle,
- Project-New- und Managed-Project-Auswirkung,
- Exit Strategy,
- Entscheidung und Referenz.

### 7.2 Alternativenprüfung

Zu prüfen sind, soweit fachlich realistisch:

- keine Änderung,
- JDK- oder Spring-Boot-Mittel,
- bestehende genehmigte Dependency,
- lokale Implementierung,
- geeignete externe Kandidaten.

Existiert keine realistische Alternative, wird dies begründet; ein Scheinvergleich ist nicht erforderlich.

### 7.3 Bewertungsdimensionen

| Dimension | Mindestinhalt |
|---|---|
| Funktionspassung | Anforderung, API, Konfiguration und Einschränkungen |
| Architektur | Layer, öffentliche Verträge, Persistenz, Security und Betrieb |
| Wartung | Releases, Kompatibilität, Security-Reaktion und Upgradepfad |
| Technik | transitive Fläche, Ressourcenwirkung, Determinismus und Testbarkeit |
| Distribution | Lizenz, Notice, SBOM und Lieferartefakte |
| Propagation | Project-New, Zielprojekte, Migration und Rückführung |

Popularität allein ist kein Genehmigungskriterium.

### 7.4 Entscheidungsstatus

| Status | Bedeutung |
|---|---|
| `proposed` | Bewertung offen |
| `approved` | Einführung im genehmigten Scope zulässig |
| `approved-with-conditions` | nur unter dokumentierten Bedingungen zulässig |
| `experimental` | befristete Erprobung ohne automatische Dauerfreigabe |
| `deferred` | Entscheidung verschoben |
| `rejected` | Einführung unzulässig |
| `retired` | aus dem genehmigten Bestand entfernt |

`experimental` benötigt Owner, Erfolgskriterien sowie Ablauf- oder Reviewdatum.

## 8. Approved-, Conditional- und Banned-Modell

### 8.1 Approved Registry

Jede genehmigte direkte Dependency und jedes Plugin MUSS maschinenlesbar registriert werden. Der Eintrag enthält mindestens:

- stabile Dependency-ID und Coordinates,
- Klasse, erlaubte Scopes, Profile und Module,
- Versionsquelle,
- genehmigten Zweck,
- Owner und Approval-Referenz,
- Lizenzklassifikation,
- Status und gegebenenfalls Reviewdatum,
- Exit Strategy.

### 8.2 Keine pauschale Gruppenfreigabe

Eine gesamte Group-ID SOLL nicht pauschal genehmigt werden. Ausnahmen sind kontrollierte Plattformfamilien mit gemeinsamer Versionierung und klarer Scope-Grenze.

### 8.3 Bedingte Freigabe

Bedingungen können insbesondere sein:

- nur Test-Scope oder bestimmtes Modul,
- keine öffentliche API-Exposition,
- verpflichtende Exclusions oder zusätzliche Tests,
- befristete Nutzung,
- keine Project-New- oder Managed-Project-Propagation.

Bedingungen müssen technisch prüfbar oder ausdrücklich manuell reviewbar sein.

### 8.4 Banned Registry

Verbote können Artifact, Gruppe, Version, Scope, Projektprofil, transitive Herkunft, Lizenzklasse, Sicherheitsrisiko oder konkurrierende Funktion betreffen.

Jeder Banned-Eintrag benötigt Grund, Scope und Entscheidungsreferenz.

## 9. Einführung als geschlossener Änderungsschnitt

Die Einführung umfasst gemeinsam:

1. genehmigten Dependency Request,
2. Registry-Eintrag,
3. Änderung von Build, Template oder Toolkonfiguration,
4. erforderliche Implementierung,
5. positive und negative Tests,
6. Dependency- und Buildprüfung,
7. Lizenz- und Security-Evidence nach aktiver Policy,
8. gegebenenfalls ADR oder Standardänderung,
9. Versions- und Propagationsbewertung,
10. aktualisierte SBOM oder vergleichbares Inventar, sofern im Profil vorgesehen.

Eine POM-Änderung ohne Registry- und Evidence-Änderung ist unvollständig.

## 10. Versions- und BOM-Governance

### 10.1 Präferenz der Versionsquellen

1. akzeptierter Parent oder Plattform-BOM,
2. importierte Spring-Boot-BOM,
3. zentrale projektweite Property,
4. genehmigter lokaler Pin.

Für durch Spring Boot verwaltete Dependencies SOLL keine zusätzliche Einzelversion deklariert werden.

### 10.2 Abweichung von der BOM

Eine Überschreibung ist nur zulässig, wenn:

- eine konkrete Kompatibilitäts- oder Sicherheitsanforderung besteht,
- der betroffene Graph geprüft wurde,
- die Abweichung in Registry und Evidence sichtbar ist,
- Rückkehr zur BOM oder eine Zielversion geplant ist.

### 10.3 Plugins und Konvergenz

Build-Plugins MÜSSEN reproduzierbar versioniert werden. Versionen SOLLEN zentral geführt werden.

Unaufgelöste konkurrierende Artifact-Versionen sind nicht zulässig. Konfliktlösungen benötigen Ursache, Zielversion und Kompatibilitätstest.

### 10.4 Major Upgrade und End-of-Life

Ein Major Upgrade benötigt ein vollständiges Review einschließlich Migration, Rückrollfähigkeit und Propagation.

Nicht mehr gepflegte oder inkompatible Dependencies werden als Risiko registriert und mit Upgrade-, Ersatz- oder Entfernungsplan versehen.

## 11. Transitive Dependencies und Exclusions

### 11.1 Transitive Inventarisierung

Transitive Dependencies benötigen nicht zwingend einzelne Approved-Einträge. Sie MÜSSEN jedoch:

- über ihren direkten Ursprung nachvollziehbar,
- in Dependency Tree oder SBOM sichtbar,
- gegen Banned-, Lizenz- und Security-Regeln prüfbar

sein.

### 11.2 Undeclared und unused

Verwendete, aber nicht deklarierte direkte Dependencies SOLLEN erkannt werden. Nachweislich ungenutzte direkte Dependencies SOLLEN entfernt werden.

Prüfwerkzeuge müssen Grenzen durch Reflection, Service Loader, Annotation Processing und Build Plugins berücksichtigen und vor Strict-Promotion qualifiziert werden.

### 11.3 Exclusions

Eine Exclusion benötigt Ursache, betroffene Dependency, erwartete Wirkung und Regressionstest. Pauschale oder unkommentierte Exclusion-Sammlungen sind nicht zulässig.

### 11.4 Doppelte Funktionalität

Mehrere Libraries mit im Wesentlichen gleicher Funktion SOLLEN vermieden werden. Eine zweite Lösung benötigt eine klare Abgrenzung oder einen befristeten Migrationszweck.

## 12. Lizenz- und Security-Governance

### 12.1 License Policy

Konkrete erlaubte, reviewpflichtige und verbotene Lizenzklassen werden maschinenlesbar geführt.

Bis diese Policy akzeptiert ist, darf kein Gate rechtliche Zulässigkeit behaupten.

Vor Freigabe einer neuen direkten oder vendorten Komponente sind Lizenz, transitive oder gebündelte Lizenzen, Notice-Pflichten und Distributionswirkung zu prüfen.

Unklare oder mehrdeutige Lizenzierung benötigt eine ausdrückliche Entscheidung. Eine nicht freigegebene Lizenzklasse kann nicht durch einen normalen Engineering-Waiver legitimiert werden.

### 12.2 Zwei Security-Prüfarten

| Prüfung | Zweck |
|---|---|
| deterministische Strukturprüfung | registrierte Artifacts, Versionen, Scopes und lokale Bans |
| datenabhängiger Vulnerability Scan | Abgleich gegen eine aktualisierte externe Datenbasis |

Ein Vulnerability Report weist Tool, Toolversion, Datenstand, Scanzeitpunkt, Baseline, Artifact, Finding, Kritikalität, Bewertung und Status aus.

Ein nicht ausführbarer Scan ist ein Tool Error. Eine veraltete Datenbasis darf nicht als aktueller vollständiger Nachweis dargestellt werden.

### 12.3 Bewertung und Fristen

Ein Finding darf nur mit konkreter Versions-, Nutzungs-, Erreichbarkeits- oder Herstellerbegründung als nicht relevant bewertet werden.

Kritikalitätsabhängige Fristen werden im Dependency- oder Security-Contract festgelegt. Bis dahin gilt:

- jedes Security-Finding wird vor Abschluss bewertet,
- bekannte ausnutzbare oder unvertretbare Risiken blockieren,
- Verschiebungen benötigen Owner, Risiko, Kompensation und Termin,
- abgelaufene Ausnahmen blockieren nach Quality Gate Governance.

## 13. Review, Upgrade und Entfernung

### 13.1 Review-Anlässe

Eine Dependency wird mindestens überprüft bei:

- Einführung oder Major Upgrade,
- Wechsel von Java- oder Spring-Boot-Baseline,
- relevantem Security- oder Lizenzfinding,
- End-of-Life,
- geänderter Project-New- oder Managed-Project-Wirkung,
- festgestellter doppelter oder entfallener Nutzung.

Reviewfähige Einträge besitzen Owner und bei Bedarf `reviewBy`.

### 13.2 Updateprinzip

Ein Update wird nicht allein wegen einer neueren Version durchgeführt. Zu bewerten sind Nutzen, Dringlichkeit, Kompatibilität, transitive Änderungen, Security, Lizenz, Tests, Propagation und Releasewirkung.

### 13.3 Entfernungsanlässe

Eine Dependency SOLL entfernt werden, wenn Zweck oder Nutzung entfallen, Plattformmittel sie ersetzen, Wartung oder Sicherheit unvertretbar werden oder die transitive Last den Nutzen nicht mehr rechtfertigt.

### 13.4 Vollständiger Entfernungsnachweis

Die Entfernung umfasst:

1. direkte Deklaration,
2. Code-, Test- und Toolnutzung,
3. Konfiguration und Ressourcen,
4. Registry-Status `retired`,
5. transitive Restnutzung,
6. Template- und Managed-Project-Auswirkung,
7. Dependency Tree, SBOM, Tests und Gates.

## 14. Ausnahmen und Abweichungen

### 14.1 Springmaster-Waiver

Eine vorübergehende technische Abweichung verwendet den Waiver-Prozess der Quality Gate Governance und nennt zusätzlich Dependency, Version, Scope, Risiko und Rückführungsplan.

Ein Waiver ersetzt weder Dependency-Genehmigung noch ADR oder Lizenzentscheidung.

### 14.2 Experimentelle Nutzung

Eine experimentelle Dependency benötigt Zweck, Hypothese, Owner, Ablaufdatum, Erfolgskriterien und Entfernungsplan. Sie darf nicht still in Produktiv-, Template- oder Managed-Project-Baselines übergehen.

### 14.3 Managed-Project-Deviation

Projektlokale Abweichungen werden nach Managed Project Governance behandelt und referenzieren verletzten Springmaster-Vertrag, lokale Version, Risiko, Reviewdatum und Rückführungsplan.

## 15. Dependency Gate und Evidence

### 15.1 Mindestprüfungen

Das Gate SOLL mindestens erkennen:

- nicht registrierte direkte Dependencies, Plugins und externe Tools,
- verbotene Artifacts, Versionen oder Scopes,
- unzulässige Profile oder Module,
- Versionen entgegen der vorgeschriebenen Quelle,
- fehlende Approval-Referenzen,
- Konvergenzprobleme und unbegründete Exclusions,
- abgelaufene Conditional-, Experimental-, Waiver- oder Deviation-Einträge,
- undeclared oder nachweislich unused Dependencies,
- unerwartete transitive Banned-, License- oder Security-Findings,
- Drift zwischen Springmaster- und Project-New-Baseline.

Es unterstützt `changed`, `affected`, `all` und `report`. Ergebnis- und Promotion-Semantik richtet sich nach Quality Gate Governance.

### 15.2 Leichtgewichtige Einführung

Die technische Einführung erfolgt über:

1. Bestandsinventar und Registry,
2. positive und negative Fixtures,
3. report-only Vergleich,
4. Fehlalarm- und Toolgrenzenanalyse,
5. kontrollierte Bereinigung,
6. gezielte Strict Promotion.

### 15.3 Dependency Evidence

Ein qualifizierter Dependency-Change enthält mindestens:

- Request und Entscheidung,
- Registry- und Buildänderung,
- Dependency Tree oder Graphnachweis,
- Lizenz- und Security-Bewertung nach aktivem Profil,
- Tests und Gate-Ergebnisse,
- Versionsquelle,
- Project-New- und Managed-Project-Bewertung,
- Exit Strategy sowie offene Bedingungen und Reviewtermine.

Release- und Auditprofile ergänzen SBOM und aktuelle datenabhängige Security-Evidence.

## 16. Project-New und gemanagte Projekte

### 16.1 Project-New

Project-New besitzt eine eigene minimale Dependency-Baseline für `generated-project`.

Eine Änderung betrifft gemeinsam:

- Template-Source,
- Approved Registry,
- Template-Version,
- Project-New-Acceptance,
- Fresh-Project-Dependency- oder SBOM-Report,
- gegebenenfalls Managed-Project-Updateplanung.

Springmaster-interne Tooling- oder Demo-Dependencies dürfen nicht automatisch kopiert werden.

### 16.2 Gemanagte Projekte

Ein gemanagtes Projekt dokumentiert adoptierte Policy, lokale Baseline, Ergänzungen und Deviations.

Springmaster muss Zielbestände read-only auf unbekannte Dependencies, nicht unterstützte Versionen, Bans, Lizenz- und Security-Risiken sowie abgelaufene Deviations prüfen können.

Ein Update behandelt POM, Contract und installed state gemeinsam und muss Quellversion, Zielversion, Kompatibilität und Migration kennen.

## 17. Maschinenlesbare Ableitungen

Mindestens erforderlich sind:

```text
contracts/governance/dependency-policy.json
contracts/governance/approved-dependencies.json
contracts/governance/banned-dependencies.json
contracts/governance/dependency-deviations.json
contracts/governance/license-policy.json
```

Dateien dürfen zusammengeführt werden, wenn Teilbereiche eindeutig adressierbar bleiben und kein konkurrierender Lifecycle entsteht.

Die Contracts enthalten Parameter und Artifact-Listen. Diese Governance bleibt die normative Quelle für Prozess und Lifecycle.

## 18. Einführung und Migration

Die Einführung erfolgt in begrenzten Schritten:

1. Springmaster- und Project-New-Baseline inventarisieren,
2. direkte Dependencies und Plugins klassifizieren,
3. Approved-, Banned- und License-Contracts erstellen,
4. Versionsquellen und bestehende Abweichungen abbilden,
5. Dependency Gate mit Fixtures report-only einführen,
6. Project-New-Baseline abgleichen,
7. Managed-Project-Pilot read-only prüfen,
8. Bestandsabweichungen behandeln,
9. einzelne stabile Regeln strict promoten.

Während der Transition gilt:

- keine neue Dependency ohne Request,
- keine Erweiterung der Legacy-Baseline durch bloße Aufnahme,
- keine pauschale Strict-Schaltung,
- keine erzwungene POM-Neustrukturierung ohne eigenen Engineering-Change.

## 19. Kanonische Ausgaben und Abnahmekriterien

### 19.1 Kanonische Ausgaben

Diese Governance erzeugt oder kontrolliert:

- Dependency-Entscheidungsklassen,
- Request und Genehmigung,
- Approved-, Conditional-, Experimental- und Banned-Modell,
- Versionsquellen- und BOM-Grundsätze,
- transitive, Lizenz- und Security-Bewertung,
- Review-, Upgrade- und Entfernungsprozess,
- Dependency-Evidence und Anforderungen an das Dependency Gate.

Nicht dazu gehören konkrete Artifact-Listen, Toolkonfigurationen, Exit-Codes, Releaseversionen oder Java-Nutzungsregeln einer Library.

### 19.2 Abnahmekriterien

Die Governance ist vollständig, wenn:

1. jede neue direkte Dependency Bedarf und Entscheidung benötigt,
2. Entscheidungstiefe für Test, Runtime, Plugin, Framework und Codegenerator eindeutig ist,
3. POM und Registry technisch vergleichbar sind,
4. Conditional-, Experimental- und Banned-Fälle modelliert sind,
5. BOM, Pins, Transitives und Exclusions geregelt sind,
6. Lizenz- und Vulnerability-Prozess definiert sind, ohne ungeklärte Policywerte zu erfinden,
7. Review, Upgrade und Entfernung vollständig geregelt sind,
8. Project-New und gemanagte Projekte eigene Profile besitzen,
9. das Dependency Gate deterministisch ableitbar ist,
10. keine Gate-, Architektur-, Build- oder Release-Verantwortung dupliziert wird,
11. der Bestand ohne Big-Bang-Migration überführt werden kann.

## 20. Offene Entscheidungen

Vor technischer Aktivierung sind noch zu entscheiden:

- erlaubte, reviewpflichtige und verbotene Lizenzklassen,
- Vulnerability-Fristen je Kritikalität,
- konkrete Dependency-, License- und Vulnerability-Tools,
- mögliche Einführung von ArchUnit oder Testcontainers,
- technische Aufteilung der Registries für Springmaster, Templates und gemanagte Projekte.

Diese Punkte blockieren nicht den Governance-Volltext, sondern die betreffenden Contracts, Tools oder Strict-Promotions.

## 21. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Volltextentwurf aus Governance-Anforderungen und Springmaster-Baseline |

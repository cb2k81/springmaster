---
documentId: DOC-GOV-0005
title: Test Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/testing
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

# Test Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie Testbedarf aus Anforderungen, Verträgen, Risiken und Änderungen abgeleitet, umgesetzt, ausgeführt, ausgewertet und nachgewiesen wird.

Sie bestimmt insbesondere:

- Teststrategie und Testumfang eines Änderungsschnitts,
- Teststufen und ihre jeweilige Aussage,
- verpflichtend zu bewertende Szenarioklassen,
- Testdaten, Fixtures und Golden Fixtures,
- Testumgebungen, Isolation und Determinismus,
- Coverage-Governance,
- Behandlung instabiler Tests,
- testseitige Evidence und Abschlusskriterien,
- Mindestanforderungen an Project-New und gemanagte Projekte.

Sie gilt für Java-Code, APIs, Persistenz, Security, Contracts, Tooling, Templates, Project-New, Platform Update und qualifizierte Lieferungen an gemanagte Projekte.

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

## 2. Kanonische Verantwortung und Abgrenzung

Diese Governance ist die kanonische Quelle für Teststrategie, Teststufen, Szenarioabdeckung, Testumgebungen, Coverage-Verfahren, Flakiness und Test Completion.

| Nicht hier geregelt | Kanonische Quelle |
|---|---|
| Change Scope, Risikostufe und Engineering-Profil | Engineering Governance |
| Gate-Ergebnisse, Rule Lifecycle, Baselines und Waiver | Quality Gate Governance |
| JUnit-, Assertion-, Mocking- und Testcode-Konventionen | Testing Standard |
| konkrete API-, Persistenz- oder Security-Verträge | zuständiger Standard oder ADR |
| konkrete Coverage-Schwellen | Coverage Policy Contract |
| Auswahl und Konfiguration von Testwerkzeugen | Build and Tooling Standard und Dependency Governance |
| Sprintziele, Definition of Done und Sprintabschluss | Sprint Governance |
| Project-New-Adoption und lokale Project-Deviations | Managed Project Governance |
| konkrete Ausführungskommandos | Development Guide und Tooling |

Testresultate sind Evidence für einen Vertrag. Sie definieren den Vertrag nicht selbst.

Eine hohe Coverage, eine große Testanzahl oder ein grüner Gesamtbuild ersetzen keine nachvollziehbare Szenario- und Vertragsabdeckung.

## 3. Bestehende Testbaseline

Springmaster besitzt bereits eine belastbare, aber noch nicht vollständig klassifizierte Testbaseline:

- JUnit 5, AssertJ und Spring Boot Test über `spring-boot-starter-test`,
- Maven Surefire als bestehender Java-Testläufer,
- H2 für isolierte Datenbanktests,
- MockMvc-Tests für HTTP-Verhalten,
- OpenAPI- und Report-Contract-Tests,
- Core-, Mapper-, Service-, Persistenz- und Spring-Context-Tests,
- Tooling-Integrationstests als Bash-Skripte,
- Golden Fixtures unter `src/test/resources/tooling/`,
- Project-New-Instantiation-Acceptance einschließlich optionalem Maven-Test des erzeugten Projekts.

Diese Governance klassifiziert und erweitert diese Baseline. Sie entscheidet noch nicht:

- über konkrete Coverage-Schwellen,
- über die Einführung von JaCoCo, ArchUnit oder Testcontainers,
- über eine technische Trennung von Surefire und Failsafe,
- über neue externe Test-Libraries.

Solche Entscheidungen folgen den zuständigen Standards, Contracts und der Dependency Governance.

## 4. Testgrundsätze

### 4.1 Anforderungen und Risiken bestimmen den Testbedarf

Der Testbedarf MUSS aus den betroffenen Anforderungen, Verträgen, Risiken und Fehlerfolgen abgeleitet werden.

Tests DÜRFEN nicht ausschließlich aus der vorhandenen Implementierung oder aus dem Wunsch nach einer bestimmten Coverage-Zahl abgeleitet werden.

### 4.2 Kleinste aussagekräftige Teststufe

Für jede Aussage SOLL die kleinste Teststufe gewählt werden, die den Vertrag verlässlich nachweist.

Eine niedrigere Teststufe darf verwendet werden, wenn sie dieselbe relevante Aussage stabiler, schneller und eindeutiger liefert. Eine höhere Teststufe darf eine fehlende gezielte Prüfung nicht automatisch ersetzen.

### 4.3 Positive und negative Evidence

Jeder neue oder geänderte Vertrag MUSS mindestens einen erfolgreichen und einen relevanten negativen Nachweis besitzen, sofern ein negativer Fall fachlich oder technisch möglich ist.

Nur Happy-Path-Tests sind für validierte Eingaben, Fehlerverträge, Security, Persistenz, Tooling und Migrationen nicht ausreichend.

### 4.4 Determinismus und Reproduzierbarkeit

Tests MÜSSEN bei gleicher Baseline und kontrollierter Umgebung reproduzierbare Ergebnisse liefern.

Unkontrollierte Abhängigkeiten von Netzwerk, realer Uhr, Testreihenfolge, Zufall, lokaler Benutzerkonfiguration oder verbleibendem Testzustand sind nicht zulässig.

### 4.5 Isolation und Rückstandsfreiheit

Ein Test MUSS seinen Zustand kontrollieren und DARF nach erfolgreicher oder fehlgeschlagener Ausführung keine unregistrierten Änderungen an Repository, Zielprojekt, Datenbank oder Benutzerumgebung hinterlassen.

Mutierende Acceptance- und Tooling-Tests MÜSSEN in einer isolierten Arbeitskopie oder einem ausdrücklich dafür vorgesehenen temporären Bereich laufen.

### 4.6 Testqualität vor Testmenge

Tests MÜSSEN eine erkennbare Vertrags- oder Risikoevidenz liefern.

Redundante Tests ohne zusätzliche Aussage, fragile Implementierungsdetailtests und pauschale Snapshot-Aktualisierungen SOLLEN vermieden werden.

### 4.7 Keine stillen Auslassungen

Erforderliche Tests DÜRFEN nicht still übersprungen, auskommentiert, deaktiviert oder aus einer Suite entfernt werden.

Nicht ausgeführte oder nicht anwendbare Tests MÜSSEN in der Engineering-Evidence sichtbar und begründet sein.

## 5. Teststrategie eines Änderungsschnitts

Vor oder während der Planung eines Änderungsschnitts MUSS eine risikogerechte Teststrategie bestimmt werden.

Sie enthält mindestens:

| Bestandteil | Inhalt |
|---|---|
| betroffene Anforderungen | funktionale, qualitative und technische Verträge |
| Risiken | relevante Fehlermöglichkeiten und Auswirkungen |
| Teststufen | erforderliche Aussageebenen |
| Szenarien | positive, negative und nicht anwendbare Klassen |
| Testdaten | notwendige Zustände, Grenzen und Fixtures |
| Umgebungen | benötigte Laufzeit-, Datenbank- und Toolbedingungen |
| Regression | bestehende Tests, die den geänderten Vertrag sichern |
| Evidence | erwartete Reports und Acceptance-Nachweise |

Die Teststrategie KANN als Abschnitt eines Sprint Briefs, einer Change-Evidence oder eines technischen Plans geführt werden. Für kleine Änderungen genügt eine kompakte Zuordnung in der Engineering-Evidence.

Eine Änderung mit hohem oder kritischem Risiko MUSS die Teststrategie vor der Umsetzung sichtbar festlegen.

## 6. Teststufen

Teststufen beschreiben die nachzuweisende Aussage, nicht zwingend einen bestimmten Testläufer oder Dateinamen.

### 6.1 Unit Test

Unit Tests prüfen isolierte Logik, Wertebereiche, Transformationen und Fehlerpfade mit kontrollierten Abhängigkeiten.

Sie SOLLEN schnell, lokal und ohne vollständigen Spring Context ausführbar sein.

### 6.2 Component Test

Component Tests prüfen das Zusammenspiel einer begrenzten Gruppe von Klassen oder Komponenten.

Sie sind geeignet, wenn reine Unit Tests den relevanten Vertrag nicht vollständig abbilden, ein vollständiger Anwendungskontext aber nicht erforderlich ist.

### 6.3 Application- und Context-Test

Application- und Context-Tests prüfen insbesondere:

- Spring-Konfiguration und Bean-Wiring,
- Component Scan und Profile,
- Konfigurationsbindung,
- notwendige technische Infrastruktur im Anwendungskontext.

Ein bloß startender Context ist kein ausreichender Nachweis für Fach- oder API-Verhalten.

### 6.4 Architecture Test

Architecture Tests prüfen mechanisch beschreibbare Strukturverträge, insbesondere:

- Package- und Layer-Abhängigkeiten,
- verbotene Zugriffe,
- öffentliche und interne Typgrenzen,
- Controller-, Repository- und Transaktionsgrenzen,
- Zyklusfreiheit definierter Bereiche.

Die Architekturregeln selbst gehören in den Java Architecture Standard. Das Prüfwerkzeug wird nicht durch diese Governance vorgegeben.

### 6.5 Contract Test

Contract Tests prüfen stabile fachliche oder technische Schnittstellen unabhängig von internen Implementierungsdetails.

Dazu gehören insbesondere:

- HTTP- und OpenAPI-Verträge,
- Fehler- und Validierungsformate,
- maschinenlesbare Governance- und Tooling-Contracts,
- Report-Schemas und Exit-Semantik,
- Persistenz- und Migrationsverträge,
- Template- und Generierungsverträge.

### 6.6 Integration Test

Integration Tests prüfen das Zusammenspiel mit realitätsnaher technischer Infrastruktur, etwa Persistenz, Liquibase, Serialisierung, Security-Konfiguration oder technische Adapter.

Der Einsatz externer Container oder Dienste benötigt eine explizite, reproduzierbare Testumgebung und gegebenenfalls eine Dependency-Entscheidung.

### 6.7 Tooling Integration Test

Tooling Integration Tests prüfen ausführbare Werkzeuge über ihre öffentlichen Ein- und Ausgänge.

Sie MÜSSEN je nach Werkzeug mindestens relevante Klassen aus folgenden Bereichen abdecken:

- erfolgreicher Lauf,
- ungültige Eingabe,
- fehlende Datei oder Voraussetzung,
- Pfad- und Scope-Verletzung,
- Berechtigungs- oder Hashfehler,
- Tool-Ausführungsfehler,
- Rollback oder Rückstandsfreiheit bei Mutation.

### 6.8 Template Acceptance Test

Template Acceptance Tests erzeugen ein neues Projekt oder Artefakt aus der tatsächlichen Template-Quelle und prüfen das erzeugte Ergebnis.

Sie müssen mehr als die Anwesenheit einzelner Dateien nachweisen. Je nach freigegebenem Profil gehören dazu:

- gültige Projektstruktur,
- aufgelöste Platzhalter,
- kompilierbarer oder ausführbarer Build,
- initiale Tests,
- anwendbare Contracts und Gates,
- Projektidentität und lokale Konfiguration,
- keine manuelle Reparatur vor der ersten regulären Entwicklung.

### 6.9 End-to-End- und Release-Acceptance

End-to-End- oder Release-Acceptance prüft ausgewählte vollständige Flüsse über mehrere Systemgrenzen.

Sie wird nur eingesetzt, wenn die höhere Aussage den zusätzlichen Aufwand rechtfertigt, insbesondere für:

- plattformkritische Referenzflüsse,
- transaktionale Patch- oder Updateabläufe,
- Project-New-Qualifikation,
- Release- und Distributionsartefakte,
- autorisierte Managed-Project-Lieferungen.

Sie ersetzt keine gezielten niedrigeren Tests für Fehlerursachen und Vertragsdetails.

## 7. Szenariomodell

Für jede betroffene Anforderung oder jeden geänderten Vertrag MÜSSEN die folgenden Szenarioklassen auf Anwendbarkeit geprüft werden:

| Szenarioklasse | Typische Aussage |
|---|---|
| Normalfall | erwartetes gültiges Ergebnis |
| Grenzwert | Mindest-, Höchst-, Leer- oder Übergangswerte |
| ungültige Eingabe | Validierung und Fehlervertrag |
| fehlende Ressource | Not Found oder fehlende Voraussetzung |
| Konflikt | Duplikat, Version, Zustand oder konkurrierende Änderung |
| Authentisierung und Berechtigung | `401`, `403`, Permission und Scope |
| Persistenz und Transaktion | Mapping, Constraints, Rollback und Konsistenz |
| technischer Ausfall | I/O-, Tool-, Adapter- oder Infrastrukturfehler |
| Wiederholung | Idempotenz, Retry oder Mehrfachausführung |
| Migration und Kompatibilität | alte Baseline, Upgrade und Versionsgrenze |
| Cleanup und Rückstand | keine unerlaubten Restartefakte oder Zustände |

Nicht jede Szenarioklasse ist für jeden Vertrag anwendbar. Nichtanwendbarkeit MUSS bei hohem oder kritischem Risiko sowie bei öffentlichen, persistenz-, security- oder tooling-relevanten Verträgen begründet werden.

Ein Testname allein ist kein Szenarionachweis. Die Verbindung zwischen Anforderung, Szenario und Evidence MUSS aus Test, Contract oder Abschlussbericht nachvollziehbar sein.

## 8. Mindesttestbedarf nach Änderungsklasse

Die Engineering Governance bestimmt Änderungsklasse, Risiko und Profil. Diese Governance bestimmt den daraus folgenden Mindesttestbedarf.

| Änderungsklasse | Mindestanforderung |
|---|---|
| reine Dokumentation ohne Vertragswirkung | Link-, Format- oder Dokumentationsprüfung; keine Java-Suite erforderlich |
| Governance, Standard oder Contract | Schema-/Regelprüfung sowie positive und negative Fixture, sobald technische Durchsetzung entsteht |
| Java-Logik oder Core | gezielter Unit-/Component-Nachweis plus betroffene Regression |
| Spring-Konfiguration | Context- oder Konfigurationsbinding-Nachweis plus negativer Fehlkonfigurationsfall, sofern relevant |
| API oder Fehlervertrag | MockMvc- oder gleichwertiger Behavior-Test, OpenAPI-/Contract-Test sowie positive und negative Fälle |
| Persistenz oder Liquibase | Mapping-/Repository-Test, Integrations- oder Migrationsevidence und relevanter Fehler-/Rollbackfall |
| Security | positive und negative Authentisierungs-, Permission- und Scope-Fälle |
| Tooling | positiver, negativer und Tool-Error-Fall; bei Mutation zusätzlich Rollback oder Rückstandsfreiheit |
| Template oder Project-New | echte Instanziierung, Strukturprüfung und freigegebene Build-/Test-/Gate-Acceptance |
| Dependency oder Build | reproduzierbarer Build, betroffene Regression und gegebenenfalls Runtime-/Packaging-Nachweis |
| Platform Update oder Managed Delivery | read-only Plan-/Kompatibilitätstest; Mutation nur in isolierter autorisierter Acceptance |
| Release | freigegebene Qualification-, Audit- und Artefakt-Acceptance |

Die Tabelle definiert Mindestklassen. Zusätzliche Tests folgen aus Risiko, Vertrag und Fehlerfolge.

Ein vorhandener breiter Testlauf darf einen fehlenden gezielten Nachweis nicht verdecken.

## 9. Testdaten und Fixtures

### 9.1 Testdaten

Testdaten MÜSSEN:

- den beabsichtigten Zustand eindeutig erzeugen,
- minimale, verständliche Werte verwenden,
- Grenz- und Fehlerfälle sichtbar machen,
- unabhängig von produktiven oder personenbezogenen Daten sein,
- nach Ausführung kontrolliert bereinigt oder verworfen werden.

Produktionsdaten DÜRFEN nicht ungeprüft als Testdaten übernommen werden.

### 9.2 Fixtures

Fixtures besitzen einen definierten Owner und einen kanonischen Pfad.

Sie DÜRFEN nicht an mehreren Stellen manuell parallel gepflegt werden. Generierte Ableitungen müssen als solche gekennzeichnet und reproduzierbar sein.

### 9.3 Golden Fixtures

Eine Golden Fixture ist Vertrags-Evidence, kein bequemes Snapshot-Update.

Sie darf nur geändert werden, wenn:

1. die Vertragsänderung beabsichtigt ist,
2. die neue Ausgabe fachlich geprüft wurde,
3. der zugehörige Regressionstest die Änderung absichert,
4. unerwartete Nebendifferenzen ausgeschlossen sind.

Ein Test darf eine Golden Fixture nicht im normalen Prüflauf automatisch überschreiben.

### 9.4 Fixture-Lebenszyklus

Veraltete oder nicht mehr referenzierte Fixtures MÜSSEN entfernt, archiviert oder als historische Evidence klassifiziert werden.

Fixture-Duplikate und konkurrierende Autorität werden durch Directory- und Quality-Gate-Regeln kontrolliert.

## 10. Testumgebungen, Isolation und Determinismus

### 10.1 Netzwerk und externe Dienste

Unit-, Component- und normale Contract-Tests DÜRFEN nicht unkontrolliert auf externe Netzwerke oder produktive Dienste zugreifen.

Ein notwendiger externer Testdienst MUSS:

- ausdrücklich zur Teststufe gehören,
- reproduzierbar provisioniert werden,
- zeitlich begrenzt und isoliert sein,
- klaren Fehlerstatus bei Nichtverfügbarkeit liefern.

### 10.2 Zeit und Zufall

Reale Zeit und Zufall MÜSSEN über kontrollierbare Abstraktionen, feste Seeds oder eindeutig tolerierte Bereiche beherrscht werden.

Tests DÜRFEN nicht allein aufgrund von Zeitzone, Tageswechsel, Ausführungsreihenfolge oder zufälliger Daten instabil sein.

### 10.3 Datenbanken

Datenbanktests MÜSSEN ein klar bestimmtes Schema und eine isolierte Datenbasis verwenden.

H2 darf nur Verträge belegen, die durch H2 realistisch abgebildet werden. Datenbankspezifische MariaDB-, SQL- oder Liquibase-Eigenschaften benötigen eine dafür geeignete Integrationsevidence.

Destruktive DBTool-Befehle gehören nicht in normale Tests und benötigen die dafür vorgesehenen Sicherheitsfreigaben.

### 10.4 Dateisystem und Arbeitskopien

Tests, die Dateien erzeugen oder verändern, MÜSSEN registrierte temporäre Pfade oder isolierte Arbeitskopien verwenden.

Sie DÜRFEN nicht:

- fremde Änderungen zurücksetzen,
- lokale Secrets lesen oder schreiben,
- unkontrolliert in `src/`, `PROJECT_DOCS/` oder andere versionierte Quellen schreiben,
- vom zufällig neuesten Runtime-Artefakt abhängen.

### 10.5 Umgebungsvariablen und Secrets

Tests MÜSSEN notwendige Umgebungsvariablen explizit setzen oder sichere Testdefaults verwenden.

Reale Secrets DÜRFEN nicht erforderlich, protokolliert oder in Fixtures übernommen werden.

### 10.6 Reihenfolge und Parallelität

Tests MÜSSEN unabhängig von der Reihenfolge ausführbar sein.

Parallelisierung darf nur aktiviert werden, wenn geteilte Zustände, Ports, Datenbanken und Dateipfade entsprechend isoliert sind.

### 10.7 Cleanup

Cleanup MUSS auch nach fehlgeschlagenen Tests soweit technisch möglich erfolgen.

Nicht entfernbare Reste oder bewusst erhaltene Diagnoseartefakte MÜSSEN in einem registrierten Runtime- oder Reportpfad liegen und im Testresultat erkennbar sein.

## 11. Coverage-Governance

### 11.1 Zweck und Grenzen

Coverage misst ausgeführten Code, nicht die Richtigkeit der Szenarien.

Sie dient dazu:

- ungetestete relevante Bereiche sichtbar zu machen,
- Regressionen in der Testtiefe zu erkennen,
- besonders kritische Logik gezielt abzusichern,
- neue oder geänderte Codepfade zu bewerten.

Coverage DARF nicht als alleinige Definition von Testqualität oder Releasefähigkeit verwendet werden.

### 11.2 Differenzierte Policy

Coverage-Schwellen MÜSSEN nach Codeklasse und Risiko differenziert werden. Eine globale Einzelzahl für das gesamte Repository ist nicht ausreichend.

Mindestens unterscheidbar sind:

- wiederverwendbare Core- und Vertragslogik,
- Application- und Orchestrierungslogik,
- Tooling,
- Konfiguration und reine Datenstrukturen,
- generierter oder bewusst ausgeschlossener Code.

Konkrete Schwellen werden im Coverage Policy Contract festgelegt und vor Strict-Aktivierung anhand der Bestandsbaseline qualifiziert.

### 11.3 Messgrößen

Line Coverage KANN als Basismetrik verwendet werden. Für Verzweigungen und Fehlerlogik MUSS zusätzlich Branch- oder eine gleichwertige Pfadmetrik berücksichtigt werden, sobald das verwendete Tool dies zuverlässig unterstützt.

Changed-Code-Coverage SOLL eingesetzt werden, um neue ungetestete Pfade von historischem Bestand zu unterscheiden.

### 11.4 Ausschlüsse

Coverage-Ausschlüsse sind nur zulässig, wenn sie:

- auf eine definierte Codeklasse oder einen engen Scope begrenzt sind,
- begründet und maschinenlesbar registriert sind,
- keine relevante Logik verdecken,
- regelmäßig überprüft werden.

Pauschale Package- oder Modul-Ausschlüsse ohne Begründung sind nicht zulässig.

### 11.5 Einführung

Coverage wird nach Quality Gate Governance schrittweise eingeführt:

1. Messbarkeit und Reportstabilität,
2. Bestandsanalyse,
3. differenzierte Schwellenentscheidung,
4. report-only,
5. Behandlung oder Baseline bestehender Lücken,
6. gezielte Strict Promotion.

Die offene Entscheidung über konkrete Schwellen blockiert nicht die übrige Test Governance.

## 12. Flaky Tests und Quarantäne

### 12.1 Flaky Test

Ein Test gilt als flaky, wenn er bei gleicher relevanter Baseline ohne beabsichtigte Änderung wiederholt unterschiedliche Ergebnisse liefert.

Ein einzelner erneuter grüner Lauf beweist nicht, dass ein vorheriger Fehler irrelevant war.

### 12.2 Klassifikation

Ein instabiles Ergebnis MUSS mindestens einer Kategorie zugeordnet werden:

- bestätigte Testinstabilität,
- umgebungsabhängiger Test,
- nicht reproduzierter Fehler,
- echter Produkt- oder Vertragsfehler,
- Tool- oder Infrastrukturfehler.

### 12.3 Behandlung

Flaky Tests MÜSSEN priorisiert stabilisiert oder entfernt und durch einen verlässlichen Nachweis ersetzt werden.

Automatische Wiederholung DARF Diagnose unterstützen, aber einen instabilen ersten Lauf nicht still als Erfolg umdeuten.

### 12.4 Quarantäne

Quarantäne ist nur zulässig, wenn sie mindestens enthält:

- Test- oder Suite-ID,
- betroffenen Vertrag,
- Ursache oder aktuellen Erkenntnisstand,
- Risiko,
- Owner,
- Ablauf- oder Reviewdatum,
- Reparatur- oder Ersatzplan.

Ein quarantänisierter Test gilt nicht als bestandener Nachweis. Fehlt dadurch eine verbindliche Testaussage, bleibt der Änderungsschnitt blockiert oder benötigt eine nach Quality Gate Governance zulässige Behandlung.

Abgelaufene Quarantänen MÜSSEN als Blocker erscheinen.

## 13. Testausführung und Ergebnisbewertung

### 13.1 Gezielte und breite Ausführung

Die Testausführung erfolgt gestuft:

1. gezielter Test für die geänderte Aussage,
2. betroffene Suite oder Modulregression,
3. durch Engineering-Profil und Risiko erforderliche breitere Qualification,
4. Audit- oder Release-Suite nur bei entsprechendem Anlass.

Ein Full-Repository-Test ist nicht bei jeder kleinen Änderung erforderlich. Eine changed-scope-Ausführung darf jedoch keine relevanten betroffenen Verträge auslassen.

### 13.2 Ergebnisstatus

Tests und Suites MÜSSEN mindestens zwischen folgenden Zuständen unterscheiden:

- bestanden,
- fehlgeschlagen,
- übersprungen oder deaktiviert,
- abgebrochen,
- nicht ausgeführt,
- Ausführungs- oder Infrastrukturfehler.

Die Aggregation in Quality-Gate-Ergebnisse erfolgt nach Quality Gate Governance.

### 13.3 Fehlerauswertung

Fehlgeschlagene Tests MÜSSEN inhaltlich ausgewertet werden. Ein Failure darf nicht ohne Ursachenanalyse durch Fixture-Update, Testdeaktivierung, zusätzliche Toleranz oder pauschale Wiederholung beseitigt werden.

### 13.4 Nicht ausgeführte Tests

Ein erforderlicher, aber nicht ausgeführter Test ist kein Erfolg.

Nichtausführung MUSS mit Grund, Auswirkung und geplanter Behandlung in der Evidence erscheinen.

## 14. Test Evidence und Test Completion

### 14.1 Test Evidence

Die testseitige Evidence eines qualifizierten Änderungsschnitts enthält mindestens:

- betroffene Anforderungen oder Verträge,
- angewendete Teststrategie,
- ausgeführte Teststufen und Suites,
- relevante Szenarioklassen,
- Ergebnisse einschließlich Skip-, Abort- und Tool-Error-Zuständen,
- verwendete Testumgebung und wesentliche Testdaten,
- Coverage-Ergebnis, sofern anwendbar,
- geänderte Fixtures und ihre Begründung,
- bekannte Lücken, Flakiness und Quarantänen,
- nicht ausgeführte Prüfungen mit Begründung.

Maschinenlesbare Testreports und der kompakte Engineering-Abschluss ergänzen einander.

### 14.2 Test Completion

Ein Änderungsschnitt ist testseitig abgeschlossen, wenn:

1. Testbedarf aus Anforderungen und Risiken abgeleitet wurde,
2. erforderliche Teststufen ausgeführt wurden,
3. positive und relevante negative Szenarien nachgewiesen sind,
4. erforderliche Grenz-, Fehler-, Security-, Persistenz- oder Toolingfälle bewertet sind,
5. Tests reproduzierbar und isoliert sind,
6. Fixtures nur aufgrund beabsichtigter Vertragsänderungen geändert wurden,
7. Coverage nach geltender Policy bewertet wurde,
8. keine unbehandelte Flakiness oder abgelaufene Quarantäne besteht,
9. keine erforderliche Testsuite still fehlt,
10. Testlücken als Blocker, Debt oder zulässiges Deferral sichtbar sind,
11. Test Evidence vollständig ist.

Test Completion ist Bestandteil der Engineering Completion. Sie ersetzt weder die fachliche Abnahme noch Sprint- oder Releaseabschluss.

## 15. Project-New und gemanagte Projekte

### 15.1 Project-New-Mindestharness

Ein erzeugtes Projekt MUSS mindestens besitzen:

- einen ausführbaren initialen Test,
- eine definierte Testkonfiguration,
- sichere Testdefaults ohne reale Secrets,
- die adoptierten Test- und Coverage-Verträge,
- einen kanonischen Testeinstieg für Qualification,
- die für das Projektprofil anwendbaren Testfixtures und Gates.

### 15.2 Fresh-Project-Acceptance

Project-New-Acceptance MUSS das tatsächlich erzeugte Projekt prüfen.

Vor einer Strict-Promotion des Project-New-Testvertrags muss die Acceptance mindestens nachweisen:

- vollständige Instanziierung ohne verbleibende Platzhalter,
- gültige Struktur und Konfiguration,
- erfolgreicher vorgesehener Maven-Test oder gleichwertiger Buildnachweis,
- erfolgreiche anwendbare Contract- und Governance-Prüfungen,
- keine manuelle Reparatur für den ersten regulären Testlauf.

Die bestehende optionale Maven-Ausführung ist Übergangsbestand und darf erst nach belastbarer Laufzeit- und Umgebungsqualifikation verpflichtend werden.

### 15.3 Gemanagte Projekte

Gemanagte Projekte adoptieren Test Governance und Testverträge anhand eines identifizierbaren Springmaster-Stands.

Lokale Ergänzungen müssen ihren Scope und Owner benennen. Abweichungen von adoptierten Testanforderungen werden durch Managed Project Governance geregelt.

Read-only-Vergleiche dürfen Tests und Konfigurationen analysieren, aber keine Zielprojekte verändern.

## 16. Technische Ableitungen und Transition

### 16.1 Maschinenlesbare Contracts

Der report-only Umsetzungsstand verwendet folgende kanonische Contract-Familie:

```text
contracts/governance/testing/test-suite-contract.json
contracts/governance/testing/test-fixture-contract.json
contracts/governance/testing/test-inventory-baseline.json
```

Der Suite Contract registriert Runner, logische Suites, Profile, Ergebniszustände und die unveränderte Surefire-Baseline. Der Fixture Contract besitzt Source-Fixtures, Consumer und Mutationsregeln. Die versiegelte Inventory Baseline klassifiziert den aktuellen Java-, Tooling- und Fixture-Bestand; neue oder fehlende Artefakte erscheinen report-only als Findings.

Coverage Policy und Test Quarantine Contract bleiben eigenständige spätere Ableitungen. Der aktuelle Contract enthält deshalb weder ein Coverage-Tool noch Schwellen und behauptet keine Failsafe- oder Tag-basierte Suite-Trennung.

### 16.2 Testkatalog

Der Test-Suite-Contract SOLL mindestens abbilden:

- Suite-ID,
- Teststufe,
- verantworteten Scope,
- zugeordnete Änderungsklassen und Engineering-Profile,
- Testläufer oder Einstiegspunkt,
- Umgebungsvoraussetzungen,
- erzeugte Reports,
- erwartete Laufzeitklasse,
- Parallelisierbarkeit,
- Enforcement-Status.

### 16.3 Migrationsarme Einführung

Die Umsetzung erfolgt schrittweise:

1. vorhandene Java- und Tooling-Tests inventarisieren,
2. bestehende Tests Teststufen und Verträgen zuordnen,
3. fehlende Szenarien und Umgebungsabhängigkeiten berichten,
4. Test- und Coverage-Contracts einführen,
5. Testausführung zunächst ohne erzwungene Surefire-/Failsafe-Neustrukturierung registrieren,
6. Coverage und zusätzliche Werkzeuge report-only qualifizieren,
7. Project-New-Acceptance erweitern,
8. Regeln nur einzeln nach Quality Gate Governance strict schalten.

Bestehende Testnamen oder Pfade werden nicht allein zur Erfüllung eines idealisierten Stufenmodells massenhaft geändert.

### 16.4 Bestandslücken

Folgende Lücken bleiben bis zur technischen Umsetzung sichtbar:

- keine akzeptierte differenzierte Coverage-Policy,
- keine implementierte Coverage-Messung,
- keine explizite Architecture-Test-Suite,
- keine technische Trennung von Unit- und Integrationstests,
- keine registrierte Quarantäne- und Flakiness-Prüfung,
- Maven-Test in Project-New-Acceptance noch optional.

Diese Lücken sind keine Begründung, vorhandene belastbare Tests abzuwerten oder eine Big-Bang-Umstellung zu verlangen.

### 16.5 Pilotabschluss und Test-Deferrals

Der Engineering Qualification Pilot materialisiert Suite-, Fixture- und versiegelten Inventory-Contract sowie deren report-only Validator. Die aktuelle Surefire-basierte Ausführung bleibt Bestandswahrheit. Es werden weder Failsafe-/Tag-Segmentierung noch Coverage-, Komplexitäts- oder Static-Analysis-Schwellen implizit eingeführt.

Project-New übernimmt diese Springmaster-spezifische Testinventarisierung nicht ohne eigenen lokalen Profilvertrag. Managed Projects benötigen vor einer Übernahme profilbezogene Test- und Fixture-Selektion. Die Closure-Entscheidung ist im Aktivierungsreport dokumentiert.

## 17. Abnahmekriterien

Diese Governance ist inhaltlich vollständig, wenn:

1. Teststrategie aus Anforderungen und Risiken ableitbar ist,
2. alle erforderlichen Teststufen eindeutig beschrieben sind,
3. Änderungsklassen auf Mindesttestbedarf abgebildet werden können,
4. positive, negative und nicht anwendbare Szenarien kontrolliert behandelt werden,
5. Testdaten und Golden Fixtures einen eindeutigen Lifecycle besitzen,
6. Netzwerk, Zeit, Zufall, Datenbank, Dateisystem und Secrets kontrolliert sind,
7. Coverage differenziert und nicht als alleinige Qualitätsaussage geregelt ist,
8. Flaky Tests und Quarantänen nicht still ignoriert werden können,
9. Test Evidence und Test Completion eindeutig sind,
10. Project-New und gemanagte Projekte propagierbare Mindestanforderungen besitzen,
11. technische Contracts ohne widersprüchliche Zweitregel ableitbar sind,
12. keine konkrete Tool- oder Schwellenentscheidung ohne zuständigen Prozess vorweggenommen wurde.

## 18. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Volltextentwurf auf Basis der bestehenden Springmaster-Testbaseline und des Governance-Gerüsts |
| 2026-07-23 | draft | draft | Suite-, Fixture- und Inventory-Contracts sowie report-only Validator und 18 Fixtures materialisiert; Coverage, Failsafe und Quarantäne bleiben offen |
| 2026-07-23 | draft | draft | Test-Contracts und Inventory qualifiziert; Tool- und Schwellenentscheidungen bleiben deferiert. |

---
documentId: DOC-STD-0003
title: Testing Standard
documentType: standard
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/standards/testing
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

# Testing Standard

## 1. Zweck und Geltungsbereich

Dieser Standard definiert die konkreten Gestaltungs- und Implementierungsregeln für automatisierten Testcode in Springmaster, Project-New und Projekten, die den Springmaster-Teststandard übernehmen.

Er regelt insbesondere:

- Ablage, Benennung und Aufbau von Testcode,
- Formulierung einzelner Testfälle,
- Assertions und Fehlerprüfungen,
- parametrisierte und dynamische Tests,
- Mocks, Stubs, Fakes und andere Test Doubles,
- Kontrolle von Zeit, Zufall, Reihenfolge, Netzwerk und Dateisystem,
- Testdaten, Fixtures und Golden Fixtures,
- Spring-, HTTP-, OpenAPI-, Persistenz- und Migrationstests,
- Tooling-Integrationstests,
- verbotene oder begründungspflichtige Testmuster.

Der Standard konkretisiert die Test Governance. Die Test Governance bestimmt, welche Teststufen und Szenarien für einen Änderungsschnitt erforderlich sind. Dieser Standard bestimmt, wie der zugehörige Testcode gestaltet werden MUSS.

Für menschliche, automatisierte und KI-gestützte Entwicklung gelten dieselben Regeln.

## 2. Abgrenzung und kanonische Verantwortung

Dieser Standard ist die kanonische Quelle für die technische Gestaltung von Testcode und Test-Fixtures.

| Nicht hier geregelt | Kanonische Quelle |
|---|---|
| Auswahl der Teststufen und Szenarioklassen | Test Governance |
| Coverage-Verfahren, Schwellen und Flaky-Test-Quarantäne | Test Governance und Coverage Contract |
| Gate-Ergebnisse, report-only, strict, Baselines und Waiver | Quality Gate Governance |
| Produktive Java-Codegestaltung | Java Coding Standard |
| Package-, Layer- und Modulgrenzen | Java Architecture Standard |
| konkrete HTTP-, Persistence-, Security- und Tooling-Verträge | zuständiger Fachstandard oder ADR |
| Auswahl, Versionierung und Maven-Integration von Testwerkzeugen | Dependency Governance und Build and Tooling Standard |
| Ausführungskommandos und Entwicklerablauf | Development Guide und Tooling |

Testcode DARF keine neue Produktsemantik definieren, die nicht aus einer Anforderung, ADR, einem Standard, Contract oder einer ausdrücklich dokumentierten Charakterisierung des Bestands ableitbar ist.

## 3. Normative Begriffe und Regelmodell

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

Jede technisch relevante Regel besitzt eine stabile Rule ID mit dem Präfix `TST`.

| Prüfbarkeitsklasse | Bedeutung |
|---|---|
| `automated` | deterministisch aus Source, Bytecode, Testreport oder Fixture prüfbar |
| `partially-automated` | Werkzeug erkennt Indikatoren; die semantische Bewertung bleibt erforderlich |
| `manual-review` | Aussagekraft, Angemessenheit oder Lesbarkeit müssen geprüft werden |
| `architectural-review` | Testdesign berührt eine dauerhafte Architektur- oder Infrastrukturentscheidung |

Der Quality Rule Catalog ordnet Rule IDs, Gates, Enforcement und technische Umsetzung zu. Toolkonfigurationen und Testläufer sind keine zweite normative Quelle.

## 4. Testorganisation und Ablage

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-ORG-001` | Java-Testcode MUSS unter `src/test/java/**` liegen und grundsätzlich die Package-Struktur des geprüften Codes spiegeln. Tooling- und repositoryweite Contract-Tests dürfen in einem klar benannten Tooling-Package liegen. | `automated` |
| `TST-ORG-002` | Testressourcen MÜSSEN unter `src/test/resources/**` oder einem durch den Directory Contract registrierten Fixture-Pfad liegen. Produktive Ressourcen dürfen nicht als versteckte Testablage verwendet werden. | `automated` |
| `TST-ORG-003` | Shell- und Python-Integrationstests MÜSSEN in einem registrierten Tooling-Pfad liegen und durch Name oder Manifest eindeutig als Test, Integrationstest, Acceptance, Regression oder Selfcheck erkennbar sein. | `automated` |
| `TST-ORG-004` | Eine Testklasse SOLL genau einen klar benennbaren Subject- oder Contract-Bereich prüfen. Unabhängig änderbare Verträge gehören in getrennte Testklassen. | `manual-review` |
| `TST-ORG-005` | Testklassen und Testmethoden SOLLEN package-private sein, sofern Framework oder Wiederverwendung keine größere Sichtbarkeit verlangen. | `automated` |
| `TST-ORG-006` | Gemeinsame Testhilfen DÜRFEN nur in einen wiederverwendbaren Test-Support-Bereich verschoben werden, wenn sie eine stabile, mehrfach genutzte Testsemantik besitzen. Allgemeine `TestUtils`-Sammlungen sind nicht zulässig. | `partially-automated` |
| `TST-ORG-007` | Die technische Zuordnung zu Unit-, Integration- und Acceptance-Suites MUSS aus einer repositoryweiten Konfiguration ableitbar sein. Konkurrierende lokale Namens- oder Tag-Schemata sind nicht zulässig. | `automated` |

Die aktuelle Springmaster-Baseline verwendet Maven Surefire und überwiegend `*Test`-Klassen. Dieser Standard verlangt keine sofortige Umbenennung oder Failsafe-Einführung. Die spätere Suite-Trennung wird im Test Suite Contract und Build and Tooling Standard festgelegt.

## 5. Benennung

### 5.1 Testklassen

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-NAM-001` | Eine Testklasse MUSS das geprüfte Subject oder den geprüften Contract im Namen erkennen lassen. | `partially-automated` |
| `TST-NAM-002` | Schnelle Java-Tests verwenden grundsätzlich das Suffix `Test`. Spezialisierte Rollen dürfen durch eindeutige Suffixe wie `ContractTest`, `SpringContextTest`, `AcceptanceTest` oder `ArchitectureTest` sichtbar gemacht werden. | `automated` |
| `TST-NAM-003` | Das Suffix `IT` oder `IntegrationTest` darf erst verbindlich einem eigenen Testläufer zugeordnet werden, wenn der Test Suite Contract diese Zuordnung festlegt. | `automated` |
| `TST-NAM-004` | Namen wie `CommonTest`, `MiscTest`, `AllTests`, `TemporaryTest` oder rein numerische Varianten sind nicht zulässig. | `automated` |

### 5.2 Testmethoden

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-NAM-005` | Testmethoden verwenden `lowerCamelCase` und beschreiben beobachtbares Verhalten oder einen Vertrag. | `automated` |
| `TST-NAM-006` | Testmethodennamen SOLLEN mit einem Verb beginnen und Ergebnis, Bedingung oder Fehlerfall erkennen lassen, zum Beispiel `rejectsDuplicateSkuCaseInsensitively`. | `partially-automated` |
| `TST-NAM-007` | Das Präfix `test` ist nicht zulässig, wenn der verbleibende Name keine zusätzliche Verhaltensaussage enthält. Bestehende Einzelfälle werden nicht durch eine reine Umbenennungswelle migriert. | `automated` |
| `TST-NAM-008` | Kryptische Abkürzungen, Ticketnummern oder Implementierungsdetails sind kein Ersatz für eine Verhaltensbeschreibung. | `manual-review` |
| `TST-NAM-009` | `@DisplayName` KANN verwendet werden, wenn es die fachliche Aussage verbessert. Es darf einen unklaren Methodennamen nicht kompensieren. | `manual-review` |

## 6. Aufbau eines Testfalls

### TST-STR-001 – Ein primärer Verhaltensgegenstand

Ein Testfall MUSS einen primären Vertrag oder ein zusammenhängendes Verhalten prüfen. Mehrere Assertions sind zulässig, wenn sie gemeinsam denselben beobachtbaren Zustand oder dieselbe Antwort beschreiben.

Unabhängige Fehlerursachen, Varianten oder Lifecycle-Schritte gehören in getrennte Tests oder einen parametrisierten Test.

**Prüfbarkeit:** `manual-review`

### TST-STR-002 – Lesbarer Arrange-Act-Assert-Aufbau

Ein Testfall MUSS Setup, Ausführung und Verifikation klar erkennen lassen. Dies kann durch:

- getrennte Absätze,
- sprechende lokale Variablen,
- kleine Fixture- oder Assertion-Hilfen,
- bei komplexen Flüssen durch `given`, `when`, `then`-Kommentare

erfolgen.

Kommentare sind nicht erforderlich, wenn die Struktur ohne sie eindeutig ist.

**Prüfbarkeit:** `partially-automated`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-STR-003` | Die eigentliche Aktion SOLL pro Testfall klar identifizierbar und grundsätzlich einmal ausgeführt werden. Mehrstufige Workflows sind nur zulässig, wenn gerade der Workflow den Vertrag bildet. | `manual-review` |
| `TST-STR-004` | Testsetup MUSS minimal sein. Nicht für den geprüften Vertrag benötigte Daten, Beans oder Konfigurationen sollen nicht erzeugt werden. | `manual-review` |
| `TST-STR-005` | Hilfsmethoden MÜSSEN die fachliche Aussage verbessern und dürfen relevante Vorbedingungen oder Assertions nicht verstecken. | `manual-review` |
| `TST-STR-006` | Ein Test DARF keinen erfolgreichen Abschluss allein durch das Ausbleiben einer Exception behaupten, wenn ein beobachtbares Ergebnis geprüft werden kann. | `partially-automated` |
| `TST-STR-007` | `try`/`catch` im Testkörper SOLL nicht zur Prüfung erwarteter Exceptions verwendet werden. Dafür sind die Assertion-Mechanismen des Testframeworks zu verwenden. | `automated` |
| `TST-STR-008` | Testcode SOLL keine produktive Implementierung nachbauen. Erwartungswerte werden aus dem Vertrag oder aus kleinen, unabhängigen Berechnungen abgeleitet. | `manual-review` |

## 7. Assertions

### 7.1 Grundsätze

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-AST-001` | Jede Testmethode MUSS mindestens eine wirksame Assertion, eine erwartete Exception oder einen anderweitig eindeutig ausgewerteten Contract-Check besitzen. | `automated` |
| `TST-AST-002` | Assertions MÜSSEN den relevanten Vertrag präzise prüfen. Allgemeine Wahrheitsprüfungen oder reine `notNull`-Assertions sind nicht ausreichend, wenn konkrete Werte, Struktur oder Seiteneffekte bestimmbar sind. | `partially-automated` |
| `TST-AST-003` | Collection-Assertions SOLLEN Inhalt, Reihenfolge und Größe entsprechend dem Vertrag direkt ausdrücken, statt Elemente einzeln über Indizes zu prüfen. | `partially-automated` |
| `TST-AST-004` | Exception-Assertions MÜSSEN mindestens den spezifischen Exception-Typ prüfen und SOLLEN relevante Fehlermeldung, Fehlercode oder Contract-Felder verifizieren. | `partially-automated` |
| `TST-AST-005` | Testcode DARF keine Exception pauschal schlucken oder nur protokollieren. | `automated` |
| `TST-AST-006` | Mehrere Assertions zu einem Objekt oder Response-Vertrag SOLLEN so strukturiert sein, dass ein Fehler die verletzte Vertragsstelle eindeutig erkennen lässt. | `manual-review` |
| `TST-AST-007` | Assertions auf private Methoden, interne Aufrufreihenfolgen oder andere nicht vertragliche Implementierungsdetails sind nicht zulässig. | `manual-review` |

### 7.2 Assertion-Bibliotheken

AssertJ ist die bevorzugte allgemeine Assertion-DSL der aktuellen Springmaster-Baseline. JUnit-Assertions und Hamcrest-/MockMvc-Matcher bleiben zulässig, wenn sie den jeweiligen Vertrag klarer ausdrücken.

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-AST-008` | Innerhalb eines einzelnen Assertion-Blocks SOLL eine konsistente DSL verwendet werden. Ein unnötiger Wechsel zwischen JUnit, AssertJ und Hamcrest ist zu vermeiden. | `partially-automated` |
| `TST-AST-009` | Statische Imports sind im Testcode für Assertions, MockMvc-Builder und andere klar erkennbare Test-DSLs zulässig. Wildcard-Imports bleiben verboten. | `automated` |
| `TST-AST-010` | Eigene Assertion-Hilfen müssen einen wiederkehrenden fachlichen oder technischen Contract kapseln. Sie dürfen keine weicheren Prüfungen als die direkte Assertion einführen. | `manual-review` |

## 8. Parametrisierte und dynamische Tests

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-PAR-001` | Ein parametrisierter Test SOLL verwendet werden, wenn derselbe Vertrag für mehrere Eingaben, Grenzwerte oder Äquivalenzklassen geprüft wird. | `manual-review` |
| `TST-PAR-002` | Parameterquellen MÜSSEN klein, nachvollziehbar und mit sprechenden Argumentnamen oder Display Names versehen sein. | `partially-automated` |
| `TST-PAR-003` | Unterschiedliche erwartete Fehlerursachen oder unterschiedliche Vertragsaussagen DÜRFEN nicht allein zur Reduktion der Testanzahl in eine Parameterliste gepresst werden. | `manual-review` |
| `TST-PAR-004` | Dynamic Tests sind nur zulässig, wenn die Testfälle tatsächlich datengetrieben erzeugt werden und statische oder parametrisierte Tests weniger verständlich wären. | `manual-review` |
| `TST-PAR-005` | Generierte Testfälle MÜSSEN deterministische, eindeutige Namen und reproduzierbare Eingaben besitzen. | `automated` |

## 9. Test Doubles

### 9.1 Auswahl

Test Doubles werden nach ihrer Aussage gewählt:

- **Stub:** liefert kontrollierte Antworten,
- **Fake:** implementiert einen vereinfachten, aber funktionalen Vertrag,
- **Mock:** prüft relevante Interaktionen an einer Boundary,
- **Spy:** beobachtet einen realen oder teilrealen Mitarbeiter.

### TST-DBL-001 – Mocks nur an echten Boundaries

Mocks SOLLEN nur für technische oder fachliche Boundaries verwendet werden, deren reale Ausführung den Test unnötig breit, langsam oder nicht deterministisch machen würde.

Eigene Value Objects, DTOs, Mapper oder einfache Domänenlogik SOLLEN nicht gemockt werden.

**Prüfbarkeit:** `manual-review`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-DBL-002` | Ein Fake MUSS den für den Test relevanten Vertrag korrekt und deterministisch implementieren. Ein Fake darf keine alternative Produktsemantik einführen. | `manual-review` |
| `TST-DBL-003` | Deep Stubs, globale Mocks und versteckte statische Mocking-Infrastruktur sind grundsätzlich nicht zulässig. Eine Ausnahme benötigt eine explizite technische Begründung. | `partially-automated` |
| `TST-DBL-004` | Lenient Stubbing oder pauschale Unused-Stubbing-Unterdrückung ist nicht zulässig. | `automated` |
| `TST-DBL-005` | Interaktionsprüfungen dürfen nur verwendet werden, wenn Aufruf, Reihenfolge oder Nicht-Aufruf Teil des Vertrags ist. `verifyNoMoreInteractions` ist kein allgemeines Qualitätsmerkmal. | `manual-review` |
| `TST-DBL-006` | Ein Test DARF keine vollständig gemockte interne Implementierungskette als Ersatz für Component- oder Integrationsevidence verwenden. | `manual-review` |
| `TST-DBL-007` | Test Doubles MÜSSEN pro Test zurückgesetzt oder neu erzeugt werden. Zustandsübernahme zwischen Tests ist nicht zulässig. | `automated` |

Eine neue Mocking- oder Test-Double-Library benötigt den Prozess der Dependency Governance.

## 10. Determinismus und Isolation

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-DET-001` | Tests DÜRFEN nicht von der Ausführungsreihenfolge anderer Tests abhängen. `@TestMethodOrder` und `@Order` sind nur zulässig, wenn ein expliziter Workflow-Contract geprüft wird und Isolation auf einer niedrigeren Ebene nicht sinnvoll ist. | `automated` |
| `TST-DET-002` | `Thread.sleep` und aktive Wartezeiten sind in regulären Tests nicht zulässig. Asynchrones Verhalten MUSS über kontrollierte Signale, Polling mit Timeout oder eine geeignete Testabstraktion geprüft werden. | `automated` |
| `TST-DET-003` | Produktive Uhrzeit darf im Test nicht unkontrolliert über `now()` bezogen werden, wenn sie das Ergebnis beeinflusst. Clock oder Eingabezeitpunkt MÜSSEN kontrolliert werden. | `partially-automated` |
| `TST-DET-004` | Zufall, UUIDs oder generierte Daten MÜSSEN kontrollierbar, reproduzierbar oder für die Assertion bedeutungslos sein. Seeds sind sichtbar festzulegen, wenn Reproduktion erforderlich ist. | `partially-automated` |
| `TST-DET-005` | Tests MÜSSEN Locale, Zeitzone und Zeichensatz explizit kontrollieren, wenn diese das Ergebnis beeinflussen. | `partially-automated` |
| `TST-DET-006` | Tests DÜRFEN kein reales externes Netzwerk verwenden. Lokale Testserver oder ausdrücklich kontrollierte Integrationstestumgebungen sind zulässig. | `automated` |
| `TST-DET-007` | Tests DÜRFEN nicht von Benutzer-Home, globalen Systemdateien, lokalen IDE-Einstellungen oder nicht registrierten Umgebungsvariablen abhängen. | `partially-automated` |
| `TST-DET-008` | Temporäre Dateien und Verzeichnisse MÜSSEN in registrierten Test- oder Buildpfaden erzeugt und nach dem Lauf entfernt oder bewusst als Evidence erhalten werden. | `partially-automated` |
| `TST-DET-009` | Ein Test darf weder den echten Repository-Working-Tree noch ein reales gemanagtes Projekt mutieren. Mutierende Tests arbeiten in einer isolierten Kopie oder Fixture. | `partially-automated` |
| `TST-DET-010` | Tests MÜSSEN parallelisierbar sein oder ihre notwendige Exklusivität ausdrücklich deklarieren. Globale mutable Zustände sind zu vermeiden. | `partially-automated` |

## 11. Testdaten und Fixtures

### TST-DAT-001 – Minimale aussagekräftige Testdaten

Testdaten MÜSSEN nur die Werte enthalten, die für den geprüften Vertrag relevant sind. Unbeteiligte Felder erhalten neutrale, nachvollziehbare Werte.

Realistisch wirkende, aber semantisch unnötige Datenmengen sind zu vermeiden.

**Prüfbarkeit:** `manual-review`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-DAT-002` | Testdaten dürfen keine realen personenbezogenen Daten, Zugangsdaten oder produktiven Secrets enthalten. | `automated` |
| `TST-DAT-003` | Builder und Factorys SOLLEN sinnvolle Defaults besitzen und für den Test relevante Abweichungen am Aufruf sichtbar machen. | `manual-review` |
| `TST-DAT-004` | Ein gemeinsames Fixture darf Tests nicht durch versteckte globale Zustandsänderungen koppeln. Mutable Fixture-Objekte werden pro Test neu erzeugt oder defensiv kopiert. | `partially-automated` |
| `TST-DAT-005` | SQL-, JSON-, YAML-, XML- oder andere Testressourcen MÜSSEN einem konkreten Test oder einer Contract-Familie eindeutig zuordenbar sein. | `automated` |
| `TST-DAT-006` | Umfangreiche Testdatenmengen benötigen eine deklarierte Herkunft, Generierungsregel oder fachliche Begründung. | `manual-review` |
| `TST-DAT-007` | Testdaten für Boundary Values MÜSSEN den Grenzfall im Testnamen, Parametername oder Fixture-Namen erkennen lassen. | `partially-automated` |

## 12. Golden Fixtures und Snapshots

### TST-GOL-001 – Golden Fixture als Contract Evidence

Eine Golden Fixture ist nur zulässig, wenn sie einen stabilen, maschinenlesbaren Vertrag repräsentiert, dessen vollständige Struktur relevant ist.

Golden Fixtures sind keine bequeme Alternative zu gezielten Assertions für beliebige Objektzustände.

**Prüfbarkeit:** `manual-review`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-GOL-002` | Golden Fixtures MÜSSEN in einem registrierten Fixture-Pfad liegen und einem erzeugenden Regressionstest eindeutig zugeordnet sein. | `automated` |
| `TST-GOL-003` | Der erzeugte Output MUSS byte-deterministisch sein oder volatile Felder müssen vor dem Vergleich kontrolliert normalisiert werden. | `automated` |
| `TST-GOL-004` | Eine Golden Fixture DARF nur geändert werden, wenn die zugehörige Vertragsänderung beabsichtigt und im Änderungsschnitt sichtbar ist. | `manual-review` |
| `TST-GOL-005` | Ein Update-Modus darf Golden Fixtures nicht pauschal oder ohne sichtbaren Diff überschreiben. Qualification- und Gate-Läufe verändern keine Golden Fixtures. | `automated` |
| `TST-GOL-006` | Der Regressionstest MUSS sowohl Übereinstimmung mit dem Golden als auch relevante Fail-Closed- oder Negativfälle prüfen. | `partially-automated` |
| `TST-GOL-007` | Raw-Byte-, JSON-, YAML- oder XML-Vergleiche müssen das kanonische Format verwenden. Eine gerenderte Textdarstellung ist kein Ersatz für den Contract Source. | `automated` |
| `TST-GOL-008` | Snapshot-Tests mit sehr breitem, nicht erklärtem Inhalt sind nicht zulässig. Der Snapshot-Scope MUSS benannt und reviewbar sein. | `manual-review` |

## 13. Spring Context und Test-Slices

### TST-SPR-001 – Kleinster geeigneter Spring Context

Ein Spring-Test SOLL den kleinsten Anwendungskontext laden, der den relevanten Vertrag nachweist.

Ein vollständiges `@SpringBootTest` ist zulässig für:

- tatsächliches Bean-Wiring und Component Scan,
- übergreifende Konfigurations- oder Transaktionsverträge,
- HTTP- oder Persistence-Integration, wenn ein engerer Slice die Aussage nicht zuverlässig liefert.

Es darf nicht allein aus Bequemlichkeit für isolierbare Logik verwendet werden.

**Prüfbarkeit:** `partially-automated`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-SPR-002` | Spring-Tests MÜSSEN ein kontrolliertes Testprofil verwenden, wenn produktive Konfiguration, Datenbank oder externe Adapter sonst aktiv würden. | `automated` |
| `TST-SPR-003` | `@MockBean`, `@SpyBean` oder gleichwertige Context-Ersetzungen dürfen nur an einer klaren Boundary eingesetzt werden und nicht den größten Teil des zu prüfenden Slices ersetzen. | `partially-automated` |
| `TST-SPR-004` | Ein reiner Context-Load-Test weist nur Start- und Wiringfähigkeit nach. Er darf nicht als Evidence für fachliches Verhalten verwendet werden. | `manual-review` |
| `TST-SPR-005` | `@DirtiesContext` SOLL vermieden werden. Seine Verwendung benötigt eine benannte globale Zustandsänderung, die nicht mit kleinerem Context oder kontrolliertem Cleanup isolierbar ist. | `automated` |
| `TST-SPR-006` | Testkonfigurationen und Test-Beans DÜRFEN nicht versehentlich in produktive Scans oder Artefakte gelangen. | `automated` |

Die aktuelle Springmaster-Baseline verwendet mehrere vollständige `@SpringBootTest`-Klassen. Diese werden zunächst als qualifizierter Bestand behandelt und nicht pauschal auf Test-Slices umgebaut.

## 14. HTTP- und MockMvc-Tests

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-HTTP-001` | HTTP-Tests MÜSSEN mindestens Status und den für den Vertrag relevanten Response-Inhalt prüfen. | `partially-automated` |
| `TST-HTTP-002` | Content Type, Header wie `Location` oder Correlation ID und Bodylosigkeit sind zu prüfen, wenn sie Teil des Endpoint-Vertrags sind. | `partially-automated` |
| `TST-HTTP-003` | Validierungs-, Not-Found-, Conflict-, Authentisierungs- und Autorisierungsfälle MÜSSEN entsprechend dem betroffenen Vertrag negativ geprüft werden. | `manual-review` |
| `TST-HTTP-004` | MockMvc-Tests SOLLEN den Controller über seine HTTP-Boundary aufrufen und nicht Controller-Methoden direkt ausführen. | `automated` |
| `TST-HTTP-005` | Tests DÜRFEN keine Repository- oder Entity-Details als öffentliche API-Annahme festschreiben. | `manual-review` |
| `TST-HTTP-006` | JSON-Assertions SOLLEN stabile Pfade und Werte prüfen. Vollständige Stringvergleiche sind nur für bewusst kanonische Contract-Ausgaben zulässig. | `partially-automated` |
| `TST-HTTP-007` | Listen-, `/all`- und `/count`-Verträge MÜSSEN gemeinsame Filter-, Sortier-, Security- und Data-Scope-Semantik durch passende Paritätstests absichern. | `manual-review` |
| `TST-HTTP-008` | Schreibtests MÜSSEN relevante Seiteneffekte und Fehlerfälle prüfen, nicht nur den HTTP-Status. | `manual-review` |

## 15. OpenAPI- und Schema-Tests

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-OAS-001` | OpenAPI-Tests MÜSSEN die erzeugte Spezifikation oder den tatsächlich veröffentlichten Contract prüfen, nicht nur Annotationen im Source. | `automated` |
| `TST-OAS-002` | Für geänderte Endpoints sind Pfad, HTTP-Methode, Operation ID, Parameter, Request Body, Responses und relevante Schemas zu prüfen. | `partially-automated` |
| `TST-OAS-003` | Verbotene Repository-, Entity- oder Frameworktypen im öffentlichen Contract MÜSSEN negativ geprüft werden, wenn die Änderung diese Boundary berührt. | `partially-automated` |
| `TST-OAS-004` | Hilfsassertions für OpenAPI müssen fehlende Knoten fail-closed behandeln. Optionalität darf nicht still angenommen werden. | `manual-review` |
| `TST-OAS-005` | OpenAPI-Golden- oder Report-Fixtures folgen zusätzlich den Golden-Fixture-Regeln dieses Standards. | `automated` |

## 16. Persistenz-, Transaktions- und Migrationstests

### TST-PER-001 – Datenbankaussage explizit bestimmen

Ein Persistenztest MUSS klar erkennen lassen, ob er:

- JPA-Mapping,
- Repository-Verhalten,
- Transaktionsgrenzen,
- Optimistic Locking,
- Liquibase-Migration,
- oder datenbankspezifische SQL-Semantik

prüft.

Die Testumgebung MUSS für diese Aussage geeignet sein.

**Prüfbarkeit:** `manual-review`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-PER-002` | Persistenztests MÜSSEN ihren Datenzustand kontrolliert aufbauen und bereinigen. Reihenfolge- oder Restdatenabhängigkeit ist nicht zulässig. | `partially-automated` |
| `TST-PER-003` | Wenn Persistenz-Reload oder Flush-Semantik Teil des Vertrags ist, MUSS der Test den Persistence Context ausdrücklich flushen und bei Bedarf leeren. | `manual-review` |
| `TST-PER-004` | H2-Evidence darf nicht als Nachweis für MariaDB-spezifisches SQL-, Locking-, Constraint- oder Migrationsverhalten dargestellt werden. | `manual-review` |
| `TST-PER-005` | Datenbankspezifische Verträge benötigen eine reproduzierbare, realitätsnahe Datenbankevidence. Die konkrete Container- oder CI-Strategie wird separat entschieden. | `architectural-review` |
| `TST-PER-006` | Liquibase-Tests MÜSSEN mindestens Syntax, Reihenfolge und Anwendbarkeit der relevanten Changelogs prüfen. Für kritische Migrationen sind Bestands- und Upgradepfade zu testen. | `manual-review` |
| `TST-PER-007` | Rollback-Tests dürfen nur behauptet werden, wenn ein fachlich und technisch unterstützter Rollback-Vertrag existiert. Vorwärtsgerichtete Migrationen werden nicht durch künstliche Down-Skripte simuliert. | `manual-review` |
| `TST-PER-008` | Transaktionstests MÜSSEN den beobachtbaren Commit-, Rollback- oder Isolationseffekt prüfen und dürfen nicht nur das Vorhandensein einer Annotation behaupten. | `manual-review` |

## 17. Tooling-, Shell- und Python-Integrationstests

### TST-TOL-001 – Öffentliche Tooloberfläche prüfen

Ein Tooling-Integrationstest MUSS das Werkzeug über seinen öffentlichen CLI-, Datei- oder Reportvertrag aufrufen. Direkter Zugriff auf interne Hilfsfunktionen ersetzt keine Integrationsevidence.

**Prüfbarkeit:** `manual-review`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-TOL-002` | Mutierende Tooling-Tests MÜSSEN in einer isolierten Fixture oder Arbeitskopie laufen. | `automated` |
| `TST-TOL-003` | Exit-Code, relevante Konsolenausgabe und maschinenlesbarer Report MÜSSEN entsprechend dem Toolvertrag geprüft werden. | `partially-automated` |
| `TST-TOL-004` | Tool-Ausführungsfehler und fachliche Findings MÜSSEN in positiven und negativen Fixtures getrennt geprüft werden. | `manual-review` |
| `TST-TOL-005` | Fail-Closed-Verhalten MUSS für ungültige Eingaben, fehlende Voraussetzungen, Pfad-/Scope-Verstöße und beschädigte Contracts geprüft werden, soweit diese Fehlerklassen anwendbar sind. | `manual-review` |
| `TST-TOL-006` | Mutierende Werkzeuge benötigen Tests für Rückstandsfreiheit, Rollback oder eindeutig dokumentierten Recovery-Zustand. | `manual-review` |
| `TST-TOL-007` | Shell-Tests beginnen mit `#!/usr/bin/env bash` und `set -euo pipefail`. Fehlgeschlagene Erwartungen MÜSSEN den Test mit einem eindeutigen Fehler beenden. | `automated` |
| `TST-TOL-008` | Tooling-Tests DÜRFEN nicht durch Auswahl der „neuesten“ Datei über unsichere Verzeichnissortierung von fremden Läufen abhängen. Lauf- und Artefaktidentitäten müssen explizit sein. | `partially-automated` |
| `TST-TOL-009` | Erforderliche externe Kommandos MÜSSEN vor dem Test geprüft werden. Ein Skip ist nur zulässig, wenn das Profil ihn erlaubt und der ausgelassene Nachweis sichtbar bleibt. | `partially-automated` |
| `TST-TOL-010` | Testlogs SOLLEN kompakte Statuszeilen ausgeben und ausführliche Diagnose in einem deterministischen Build-/Testpfad ablegen. | `partially-automated` |

## 18. Deaktivierte, instabile und bedingte Tests

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `TST-STA-001` | `@Disabled`, auskommentierte Tests oder pauschale Suite-Ausschlüsse sind ohne registrierten Grund, Owner und Reviewdatum nicht zulässig. | `automated` |
| `TST-STA-002` | Ein instabiler Test darf nicht durch Wiederholungsloops, größere Timeouts oder pauschale Retry-Plugins verborgen werden. | `partially-automated` |
| `TST-STA-003` | Bedingte Tests MÜSSEN die Bedingung sichtbar benennen. Das Qualification-Ergebnis muss unterscheiden, ob der Test bestanden, nicht anwendbar oder nicht ausgeführt wurde. | `partially-automated` |
| `TST-STA-004` | Quarantäne und Flaky-Test-Lifecycle werden ausschließlich nach Test Governance geführt. Der Testcode MUSS auf den gültigen Eintrag verweisen. | `automated` |

## 19. Verbotene Testmuster

| Rule ID | Verbotenes Muster | Prüfbarkeit |
|---|---|---|
| `TST-ANT-001` | Abhängigkeit von realem externem Netzwerk, realer Benutzerumgebung oder unkontrollierter Systemzeit | `automated` |
| `TST-ANT-002` | `Thread.sleep`, Polling ohne Timeout oder unbeschränkte Warteoperation | `automated` |
| `TST-ANT-003` | Testreihenfolge als versteckte Vorbedingung | `partially-automated` |
| `TST-ANT-004` | pauschales Catch-and-Ignore, nur geloggte Fehler oder leere Catch-Blöcke | `automated` |
| `TST-ANT-005` | Assertions nur auf `notNull`, `true` oder Exit-Code 0, obwohl ein genauerer Vertrag vorliegt | `partially-automated` |
| `TST-ANT-006` | Übermockung eigener Schichten oder Prüfung privater Implementierungsdetails | `manual-review` |
| `TST-ANT-007` | Produktionsergebnis und Erwartungswert werden durch dieselbe produktive Funktion erzeugt | `partially-automated` |
| `TST-ANT-008` | pauschales Golden-/Snapshot-Update ohne beabsichtigte Vertragsänderung | `automated` |
| `TST-ANT-009` | Tests schreiben in produktive Source-, Contract- oder Dokumentationspfade | `automated` |
| `TST-ANT-010` | Test-only-Schalter oder öffentliche Produktions-APIs allein zur Umgehung testbarer Boundaries | `manual-review` |
| `TST-ANT-011` | ein vollständiger Spring Context ersetzt ohne Begründung isolierbare Unit- oder Component-Tests | `partially-automated` |
| `TST-ANT-012` | Erfolg wird nur durch Testanzahl oder Coverage statt durch Vertrags- und Szenarioevidence behauptet | `manual-review` |

## 20. Technische Prüfung und Rule Mapping

### 20.1 Prüfbereiche

Aus diesem Standard sind mindestens folgende Prüfbereiche ableitbar:

| Prüfbereich | Beispiele |
|---|---|
| Source und Naming | Ablage, Suffixe, package-private, verbotene Namen |
| Determinismus | Sleep, Testreihenfolge, Netzwerk, Uhr, Zufall |
| Assertions | fehlende Assertions, leere Catch-Blöcke, Exception-Prüfung |
| Spring Tests | Full-Context-Nutzung, Testprofil, `@DirtiesContext` |
| Test Doubles | Deep Stubs, lenient Stubbing, globale Mocks |
| Golden Fixtures | Pfad, deterministischer Vergleich, Update-Sicherheit |
| Tooling Tests | Isolation, Exit-Code, Fail-Closed, Rollback |
| Status | Disabled, Quarantäne, bedingte Ausführung |

Die konkrete Toolkombination wird erst nach Build and Tooling Standard und Dependency Governance festgelegt. JUnit, Maven Surefire, statische Analyse, eigene Contract-Checks oder SonarQube können einzelne Regeln implementieren, sind aber nicht selbst die Regelquelle.

### 20.2 Prüfmodi

Der Test-Harness MUSS mindestens unterstützen:

- `changed`: geänderte Tests, Fixtures und unmittelbar betroffene Testregeln,
- `affected`: vollständige betroffene Test- und Contract-Familien,
- `all`: repositoryweiter Teststandard-Audit,
- `report`: maschinenlesbare Bestands- und Migrationsauswertung.

Die Zuordnung zu Fast-, Qualification-, Audit- und Release-Profilen erfolgt durch Engineering- und Quality-Gate-Contracts.

### 20.3 Fixtures für den Testing Standard

Für automatisierte Regeln MÜSSEN positive und negative Teststandard-Fixtures vorgesehen werden, insbesondere für:

- gültige und ungültige Testnamen,
- Sleep und Reihenfolgeabhängigkeit,
- fehlende oder wirkungslose Assertions,
- Golden-Update-Sicherheit,
- deaktivierte Tests,
- isolierte und nicht isolierte Tooling-Tests,
- Spring-Context-Überbreite,
- Tool Error und fachliches Finding.

## 21. Bestand und Einführung

### 21.1 Verifizierte Springmaster-Baseline

Der aktuelle Bestand umfasst:

- 49 Java-Testdateien,
- 156 erkannte JUnit-Testmethoden,
- 7 Golden Fixtures unter `src/test/resources/tooling/`,
- zahlreiche Shell-Integration-, Acceptance-, Regression- und Selfcheck-Tests,
- JUnit 5, AssertJ, MockMvc und H2,
- 10 Klassen mit `@SpringBootTest`,
- keine `@Disabled`-, Testreihenfolge-, `Thread.sleep`- oder reale-Zeit-Aufrufe im Java-Testbestand,
- keine Mockito-Nutzung im aktuellen Java-Testbestand,
- überwiegend verhaltensbeschreibende `lowerCamelCase`-Testnamen.

Diese Baseline ist eine gute Grundlage. Sie ist jedoch noch nicht vollständig in Unit-, Integration- und Acceptance-Suites klassifiziert und besitzt noch keine technische Coverage-Policy.

### 21.2 Übergang

Dieser Standard verlangt keine pauschale Testumbenennung oder sofortige Neuorganisation bestehender Tests.

Bei neuen und wesentlich geänderten Tests gelten die Regeln vollständig. Bestehende Abweichungen werden:

1. report-only ermittelt,
2. nach Relevanz und Änderungsnähe bewertet,
3. in begrenzten Änderungen bereinigt oder qualifiziert baselined,
4. erst nach stabiler Tool- und Fixture-Evidence strict geschaltet.

Reine Formatierungs-, Rename- oder Test-Slice-Massenänderungen sind nicht Teil der Governance-Einführung.

## 22. Project-New und gemanagte Projekte

### 22.1 Project-New

Ein neu erzeugtes Projekt MUSS mindestens besitzen:

- einen startfähigen Context- oder Application-Smoke-Test,
- eine deterministische Testkonfiguration,
- einen registrierten Testressourcenpfad,
- die anwendbaren Teststandard-Regeln und Gate-Einstiegspunkte,
- keine deaktivierten oder nur lokal ausführbaren Pflichtests,
- eine Fresh-Project-Acceptance, die Testausführung und Ergebnis nachweist.

Project-New muss nicht alle Springmaster-spezifischen Tooling-Tests übernehmen.

### 22.2 Gemanagte Projekte

Gemanagte Projekte übernehmen den Testing Standard über ihr Governance-Adoptionsprofil. Lokale Testframeworks oder zusätzliche Testarten sind zulässig, wenn:

- der lokale Zweck dokumentiert ist,
- die Springmaster-Mindestregeln nicht still aufgehoben werden,
- Tool- und Dependency-Entscheidungen registriert sind,
- lokale Abweichungen über die Managed Project Governance geführt werden.

Read-only-Prüfungen sollen mindestens Teststruktur, deaktivierte Tests, Fixture-Drift, nicht kontrollierte externe Abhängigkeiten und veraltete Teststandard-Adoption erkennen.

## 23. Abnahmekriterien

Der Testing Standard ist inhaltlich vollständig, wenn:

1. Testablage und Benennung eindeutig geregelt sind,
2. Testfallstruktur und Assertions konkrete Regeln besitzen,
3. Parametrisierung und Test Doubles kontrolliert sind,
4. Zeit, Zufall, Netzwerk, Reihenfolge und Dateisystem deterministisch geregelt sind,
5. Testdaten und Golden Fixtures einen eindeutigen Lifecycle besitzen,
6. Spring-, HTTP-, OpenAPI-, Persistenz- und Tooling-Tests konkretisiert sind,
7. deaktivierte und instabile Tests nicht still verborgen werden können,
8. verbotene Testmuster technisch oder durch Review prüfbar sind,
9. jede technisch relevante Regel eine stabile Rule ID besitzt,
10. Project-New und gemanagte Projekte ein klares Mindestprofil erhalten,
11. keine Coverage-Schwelle oder Toolauswahl ohne zuständige Entscheidung vorweggenommen wird,
12. der Bestand ohne Big-Bang-Migration schrittweise qualifiziert werden kann.

## 24. Kanonische Ausgaben

Dieser Standard erzeugt oder kontrolliert ausschließlich:

- Regeln für Testcode und Testklassen,
- Benennungs- und Strukturregeln,
- Assertion- und Test-Double-Regeln,
- Determinismus- und Isolationregeln,
- Fixture- und Golden-Fixture-Regeln,
- konkrete Spring-, HTTP-, OpenAPI-, Persistenz- und Tooling-Testkonventionen,
- verbotene Testmuster,
- `TST`-Rule-IDs für die technische Ableitung.

Nicht zu seinen kanonischen Ausgaben gehören Teststufenauswahl, Coverage-Schwellen, Flaky-Test-Governance, Gate-Enforcement, konkrete Toolprodukte oder Maven-Profile.

## 25. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Erstentwurf aus Test Governance, AGENTS.md, ADR-0006 und verifiziertem Springmaster-Testbestand |

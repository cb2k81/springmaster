---
documentId: DOC-STD-0002
title: Java Coding Standard
documentType: standard
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/standards/java-coding
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

# Java Coding Standard

## 1. Zweck und Geltungsbereich

Dieser Standard definiert die lokalen Gestaltungs- und Qualitätsregeln für produktiven Java-Code in Springmaster, Project-New und Projekten, die Springmaster-Coding-Regeln übernehmen.

Er regelt:

- Source-Format, Imports und Benennung,
- Sichtbarkeit, Klassenaufbau und Konstruktion,
- Immutability, Collections und Nullbehandlung,
- Methoden, Kontrollfluss und lokale Komplexität,
- Exceptions, Logging, Kommentare und Javadoc,
- allgemeine Spring- und Generator-Konventionen,
- technisch prüfbare Clean-Code-Regeln.

Der Standard gilt primär für `src/main/java/**`. Testcode folgt zusätzlich dem Testing Standard. Für menschliche, automatisierte und KI-gestützte Entwicklung gelten dieselben Regeln.

## 2. Abgrenzung und kanonische Verantwortung

Dieser Standard ist die kanonische Quelle für lokale Java-Codegestaltung. Andere Inhalte verbleiben bei ihren Eigentümern:

| Gegenstand | Kanonische Quelle |
|---|---|
| Namespace-, Package-, Layer- und Modulabhängigkeiten | Java Architecture Standard |
| HTTP-, DTO- und OpenAPI-Verträge | ADR-0002 und API-Standards |
| Application-, Service-, Use-Case- und Transaktionssemantik | ADR-0003 und Controller/Service/UseCase Standard |
| Entity-, Identity-, Auditing- und Persistenzsemantik | ADR-0004 und Domain Entity/Persistence Standard |
| Permission- und Security-Semantik | ADR-0005 und Security Standard |
| Mapping-Verantwortung | Mapping Standard |
| Testaufbau, Assertions und Mocking | Testing Standard |
| Toolauswahl und Maven-Integration | Build and Tooling Standard |
| Enforcement, Baselines, Waiver und Suppression-Lifecycle | Quality Gate Governance |
| Libraries und Annotation Processor | Dependency Governance |
| Java-API-Kompatibilität und SemVer | Release and Version Governance |

Der fachlich spezifischere aktive Standard bestimmt die Fachsemantik; dieser Standard bestimmt die lokale Codequalität.

## 3. Normative Begriffe und Regelmodell

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

Jede technisch relevante Regel besitzt eine stabile Rule ID mit dem Präfix `JCODE`.

| Prüfbarkeitsklasse | Bedeutung |
|---|---|
| `automated` | deterministisch aus Source, Bytecode oder Compilerinformationen prüfbar |
| `partially-automated` | Werkzeug erkennt Indikatoren; semantische Bewertung bleibt erforderlich |
| `manual-review` | Lesbarkeit, Verantwortung oder fachliche Angemessenheit müssen bewertet werden |
| `architectural-review` | Änderung berührt eine dauerhafte technische Grundentscheidung |

Der Quality Rule Catalog ordnet Rule ID, Gate, Enforcement und technische Implementierung zu. Toolkonfigurationen sind keine zweite Regelquelle.

## 4. Source-Format und Imports

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-SRC-001` | Java-Quelldateien MÜSSEN UTF-8 ohne BOM und LF-Zeilenenden verwenden. | `automated` |
| `JCODE-SRC-002` | Einrückung erfolgt mit vier Leerzeichen. Tabs sind nicht zulässig. | `automated` |
| `JCODE-SRC-003` | Eine Datei enthält grundsätzlich genau einen fachlich relevanten Top-Level-Typ; Dateiname und Typname stimmen überein. `package-info.java` und `module-info.java` sind ausgenommen. | `automated` |
| `JCODE-SRC-004` | Imports MÜSSEN explizit sein. Wildcard-, doppelte und unbenutzte Imports sind nicht zulässig. | `automated` |
| `JCODE-SRC-005` | Produktiver Code SOLL keine statischen Imports verwenden. Test-DSLs werden im Testing Standard geregelt. | `automated` |
| `JCODE-SRC-006` | Imports werden nach einer einzigen repositoryweiten Konfiguration gruppiert und deterministisch sortiert. Konkurrierende IDE-Profile sind nicht zulässig. | `automated` |
| `JCODE-SRC-007` | Kontrollstrukturen verwenden immer geschweifte Klammern. Öffnende Klammern stehen auf derselben Zeile wie Deklaration oder Kontrollausdruck. | `automated` |
| `JCODE-SRC-008` | Produktive Java-Zeilen SOLLEN höchstens 120 Zeichen lang sein. Begründete, nicht sinnvoll teilbare Ausnahmen bleiben report-only sichtbar. | `automated` |
| `JCODE-SRC-009` | Trailing Whitespace, unnötige Leerzeilen und fehlender finaler Zeilenumbruch sind nicht zulässig. Qualification- und Audit-Gates verändern keine Sources. | `automated` |

## 5. Benennung

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-NAM-001` | Packages werden vollständig kleingeschrieben und folgen den Verantwortungsgrenzen des Java Architecture Standard. | `automated` |
| `JCODE-NAM-002` | Klassen, Interfaces, Records und Enums verwenden `UpperCamelCase`; Methoden, Parameter und Felder `lowerCamelCase`. | `automated` |
| `JCODE-NAM-003` | Konstanten verwenden `UPPER_SNAKE_CASE`. Unveränderliche Instanzfelder sind keine Konstanten. | `automated` |
| `JCODE-NAM-004` | Namen MÜSSEN Rolle oder Fachbedeutung ausdrücken. Unspezifische Namen wie `Helper`, `Manager`, `Util`, `Common`, `Data`, `Object` oder `Impl` benötigen einen konkretisierenden Kontext. | `partially-automated` |
| `JCODE-NAM-005` | Rollenbegriffe wie `Controller`, `Service`, `Repository`, `Mapper`, `DTO`, `Command`, `Query`, `Result`, `Properties` und `Contributor` werden konsistent mit den Fachstandards verwendet. | `partially-automated` |
| `JCODE-NAM-006` | Etablierte Akronyme wie `DTO`, `API`, `ID`, `URI` und `URL` dürfen erhalten bleiben. Neue uneinheitliche Kurzformen sind nicht zulässig. | `partially-automated` |
| `JCODE-NAM-007` | Einbuchstabige oder stark verkürzte Namen sind nur in sehr kleinen lokalen Scopes mit unmittelbar sichtbarer Bedeutung zulässig. | `partially-automated` |
| `JCODE-NAM-008` | Java-Identifier, technische Kommentare und Javadoc SOLLEN Englisch verwenden. Fachbegriffe folgen der verbindlichen Ubiquitous Language. | `manual-review` |

## 6. Sichtbarkeit und API-Fläche

### JCODE-VIS-001 – Kleinste erforderliche Sichtbarkeit

Typen, Konstruktoren, Methoden und Felder MÜSSEN die kleinste Sichtbarkeit besitzen, die ihr Vertrag benötigt. `public` ist keine Standardwahl; package-private ist für package-internen Code zu bevorzugen.

**Prüfbarkeit:** `partially-automated`

### JCODE-VIS-002 – Public benötigt einen Grund

Ein produktiver Typ oder Member darf nur `public` sein, wenn mindestens einer der folgenden Gründe gilt:

- veröffentlichte oder projektinterne API,
- zulässige Nutzung aus einem anderen Package,
- Framework-, Serialization- oder Persistence-Vertrag,
- expliziter Extension Point.

`public`, `project-api` und `published-api` werden nach dem Java Architecture Standard unterschieden.

**Prüfbarkeit:** `partially-automated`

### JCODE-VIS-003 – Protected ist ein Extension Contract

`protected` DARF nur verwendet werden, wenn Vererbung ausdrücklich Teil des Designs ist. Protected mutable fields sind nicht zulässig; Erweiterungspunkte werden bevorzugt über Methoden oder Komposition definiert.

**Prüfbarkeit:** `partially-automated`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-VIS-004` | Produktive Instanzfelder MÜSSEN grundsätzlich `private` sein. Frameworkausnahmen benötigen eine begründete Regelquelle. | `automated` |
| `JCODE-VIS-005` | Konstruktoren sind nur so sichtbar wie die vorgesehene Erzeugungsstrategie. Public No-Args-Konstruktoren dürfen nicht allein aus Bequemlichkeit entstehen. | `partially-automated` |
| `JCODE-VIS-006` | Mutable public, protected oder package-private Fields sind nicht zulässig. | `automated` |

## 7. Klassenaufbau und Verantwortung

### 7.1 Member-Reihenfolge

Neue und wesentlich überarbeitete Typen SOLLEN ihre Member in folgender Reihenfolge anordnen:

1. Konstanten und statische Felder,
2. Instanzfelder,
3. Konstruktoren und Factorys,
4. öffentliche Methoden,
5. protected und package-private Methoden,
6. private Hilfsmethoden,
7. Nested Types.

Annotations, Javadoc und Kommentare bleiben unmittelbar an der Deklaration. Überschriebene Methoden dürfen zusammen mit der zugehörigen Vertragssicht stehen.

### JCODE-CLS-001 – Klare Verantwortung

Ein Typ MUSS eine klar benennbare Verantwortung besitzen. Er SOLL aufgeteilt werden, wenn er mehrere unabhängig änderbare Rollen, technische Layer oder nicht zusammengehörige Seiteneffekte vereint.

Metriken dürfen einen Review auslösen, entscheiden aber nicht allein über die Aufteilung.

**Prüfbarkeit:** `partially-automated`

### JCODE-CLS-002 – Kohäsion vor Generalisierung

Code DARF nicht allein wegen ähnlicher Aufrufstellen in eine allgemeine Basis-, Helper- oder Utility-Klasse verschoben werden. Eine Extraktion benötigt gemeinsame stabile Semantik und einen benennbaren Vertrag.

**Prüfbarkeit:** `manual-review`

### JCODE-CLS-003 – Vererbung ist begründet

Komposition ist gegenüber Implementierungsvererbung zu bevorzugen. Eine Basisklasse benötigt gemeinsame Invarianten oder Lifecycle-Semantik; Vererbung allein zur Wiederverwendung einzelner Methoden oder Felder ist nicht zulässig.

Frameworkbedingte Vererbung bleibt zulässig.

**Prüfbarkeit:** `manual-review`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-CLS-004` | Unveränderliche Felder MÜSSEN `final` sein, soweit Framework oder Lifecycle dies nicht verhindern. | `partially-automated` |
| `JCODE-CLS-005` | Reine, nicht erweiterbare Hilfs- und Value-Typen SOLLEN `final` oder Records sein. Spring-Proxies, JPA-Entities und Extension Points dürfen nicht pauschal finalisiert werden. | `partially-automated` |
| `JCODE-CLS-006` | Ein reguläres Objekt MUSS nach erfolgreichem Konstruktor- oder Factory-Aufruf seine grundlegenden Invarianten erfüllen. Versteckte Setter-Reihenfolgen sind nicht zulässig. | `manual-review` |
| `JCODE-CLS-007` | Nested Types sind nur zulässig, wenn sie ausschließlich dem umgebenden Typ dienen. Unabhängig genutzte oder versionierte Typen werden Top-Level-Typen. | `manual-review` |
| `JCODE-CLS-008` | Utility-Klassen sind eng begrenzte Ausnahmen. Sie MÜSSEN `final` sein, einen privaten Konstruktor besitzen und dürfen keinen veränderlichen globalen Zustand halten. Allgemeine `Utils`-Sammlungen sind nicht zulässig. | `automated` |
| `JCODE-CLS-009` | Member-Reihenfolge MUSS der repositoryweiten Formatkonfiguration entsprechen. | `automated` |

## 8. Konstruktion und Dependency Injection

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-DI-001` | Produktive Spring-Komponenten MÜSSEN erforderliche externe Collaborators über den Konstruktor erhalten. Field Injection ist nicht zulässig. | `automated` |
| `JCODE-DI-002` | Produktiver Code DARF Beans nicht über globalen Application Context, statische Holder oder Service Locator suchen. | `automated` |
| `JCODE-DI-003` | Extern konfigurierte, substituierbare oder lifecycle-relevante Collaborators MÜSSEN injiziert werden. | `manual-review` |
| `JCODE-DI-004` | Kleine zustandslose Mapper, Validatoren oder Query-Helfer KÖNNEN lokal konstruiert werden, wenn sie keine externe Abhängigkeit, Konfiguration oder versteckte Lifecycle-Semantik besitzen. | `manual-review` |
| `JCODE-DI-005` | Konstruktoren und statische Initializer DÜRFEN keine Datenbank-, Netzwerk-, Dateisystem- oder andere externe I/O ausführen. | `partially-automated` |
| `JCODE-DI-006` | Erforderliche Konstruktorparameter DÜRFEN nicht still `null` akzeptieren. Wo der Frameworkvertrag keine Garantie liefert, wird die Invariante explizit geprüft. | `partially-automated` |
| `JCODE-DI-007` | Lombok oder vergleichbare Source-Transformation DARF nicht ohne Dependency Review, Nutzenbegründung und IDE-/Build-Qualifikation eingeführt werden. | `automated` |

Lokale Konstruktion darf keine Architektur-, Proxy- oder Testgrenze umgehen.

## 9. Immutability, Collections und Null

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-DAT-001` | Value Objects, Query-Kriterien, Konfigurationswerte und Ergebnisdaten SOLLEN unveränderlich modelliert werden, sofern Framework- oder Persistenzanforderungen nicht entgegenstehen. | `partially-automated` |
| `JCODE-DAT-002` | Records sind zulässig, wenn öffentliche Semantik, Validation und Serialisierung zum Vertrag passen. | `manual-review` |
| `JCODE-DAT-003` | Mutable Collections, Maps, Arrays und vergleichbare Container MÜSSEN an Objekt- und API-Grenzen defensiv kopiert werden, wenn externe Änderung internen Zustand beeinflussen könnte. | `partially-automated` |
| `JCODE-DAT-004` | Getter und Rückgaben DÜRFEN keine intern veränderliche Collection oder internes Array direkt exponieren. | `partially-automated` |
| `JCODE-DAT-005` | Collection-, Map-, Stream- und Array-Ergebnisse DÜRFEN nicht `null` sein; leere Ergebnisse werden leer und möglichst unveränderlich zurückgegeben. | `partially-automated` |
| `JCODE-DAT-006` | `Optional` KANN für einzelne regulär abwesende Lookup- oder Berechnungsergebnisse verwendet werden. Es SOLL NICHT als Feld, Parameter, Collection-Element oder Wrapper um Collections dienen. | `partially-automated` |
| `JCODE-DAT-007` | Öffentliche und projektinterne Methoden MÜSSEN erkennen lassen, ob `null` zulässig ist. Verdeckte Null-Sonderfälle sind nicht zulässig. | `manual-review` |
| `JCODE-DAT-008` | Technische Case-Normalisierung MUSS `Locale.ROOT` oder eine fachlich festgelegte Locale verwenden. Normalisierung darf nicht uneinheitlich über Layer verteilt werden. | `partially-automated` |
| `JCODE-DAT-009` | Fachlich relevante Uhrzeit und Zufall MÜSSEN über kontrollierbare Abstraktionen wie `Clock` oder Generatoren zugänglich sein. | `partially-automated` |
| `JCODE-DAT-010` | Mutable statische Felder, globale fachliche Caches ohne Lifecycle-Vertrag und prozessweite fachliche Singleton-Zustände sind nicht zulässig. | `automated` |

## 10. Methoden und Kontrollfluss

### JCODE-MET-001 – Eine erkennbare Aufgabe

Eine Methode MUSS eine klar erkennbare Aufgabe auf einer konsistenten Abstraktionsebene ausführen. Unabhängig änderbare Validierung, I/O, Mapping, Autorisierung und Persistenz dürfen nicht allein aus Bequemlichkeit in einer langen Methode vermischt werden.

**Prüfbarkeit:** `partially-automated`

### JCODE-MET-002 – Guard Clauses und klare Bedingungen

Fehler- und Sonderfälle SOLLEN früh behandelt werden, wenn dies den Hauptpfad klärt. Tiefe Verschachtelung, mehrfach negierte Bedingungen und verschachtelte Ternaries SOLLEN durch Guard Clauses, benannte Prädikate oder kleinere Methoden reduziert werden.

**Prüfbarkeit:** `partially-automated`

### JCODE-MET-003 – Zusammenhängende Parameter

Methodenparameter MÜSSEN einen verständlichen Vertrag bilden. Gemeinsam variierende oder wiederholt weitergereichte Parameter SOLLEN in Command-, Query-, Criteria- oder Value-Typen gebündelt werden. Ein Parameterobjekt darf nicht allein zur Umgehung einer Metrik entstehen.

**Prüfbarkeit:** `partially-automated`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-MET-004` | Öffentliche und projektinterne Methoden SOLLEN keine unklaren booleschen Steuerparameter verwenden. Benannte Varianten, Enums oder Criteria-Typen sind vorzuziehen. | `partially-automated` |
| `JCODE-MET-005` | Methodenname und Platzierung MÜSSEN Seiteneffekte erkennen lassen. Query-Methoden SOLLEN keine fachlichen Schreibseiteneffekte besitzen; Getter dürfen keine I/O verstecken. | `manual-review` |
| `JCODE-MET-006` | Stream-Pipelines SOLLEN Transformation, Filterung oder Aggregation dienen. Versteckte Seiteneffekte in `map`, `filter` oder `peek` sind nicht zulässig. Eine klarere Schleife ist vorzuziehen. | `partially-automated` |
| `JCODE-MET-007` | Code SOLL die einfachste verständliche Form verwenden. Reflektive Umgehungen, unnötig generische Abstraktionen und trickreiche Mehrfachausdrücke sind zu vermeiden. | `manual-review` |
| `JCODE-MET-008` | Wiederverwendete oder fachlich bedeutende Magic Values MÜSSEN einen benannten Eigentümer besitzen. Offensichtliche lokale Werte benötigen nicht automatisch Konstanten. | `partially-automated` |
| `JCODE-MET-009` | `var` KANN lokal verwendet werden, wenn Typ und Bedeutung aus der Initialisierung unmittelbar ersichtlich sind. Bei abstrakten Factory-Ergebnissen, relevanten generischen Typen oder typabhängigem Verständnis SOLL der Typ explizit bleiben. | `partially-automated` |
| `JCODE-MET-010` | Methodenlänge, Klassenlänge, Parameteranzahl, Verschachtelung sowie zyklomatische und kognitive Komplexität MÜSSEN messbar sein. Findings lösen zunächst Review aus; konkrete Grenzwerte werden nach Bestandsmessung festgelegt. | `automated` |

## 11. Exceptions und Fehlerbehandlung

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-ERR-001` | Erwartbare Validation-, Not-Found-, Conflict- und andere Vertragsfehler MÜSSEN spezifische Exception-Typen oder einen gleichwertigen expliziten Fehlervertrag verwenden. | `partially-automated` |
| `JCODE-ERR-002` | Leere Catch-Blöcke und still ignorierte relevante Exceptions sind nicht zulässig. | `automated` |
| `JCODE-ERR-003` | Beim Übersetzen technischer Exceptions MUSS die ursprüngliche Cause erhalten bleiben, sofern sie nicht sicherheitsbedingt bewusst entfernt wird. | `partially-automated` |
| `JCODE-ERR-004` | `Throwable` und `Error` DÜRFEN in regulärem Anwendungscode nicht gefangen werden. `Exception` ist nur an klaren technischen Boundaries zulässig. | `automated` |
| `JCODE-ERR-005` | Eine Exception SOLL nicht auf mehreren Layern vollständig geloggt und unverändert weitergeworfen werden. Logging erfolgt an der Boundary mit ausreichendem Kontext. | `partially-automated` |
| `JCODE-ERR-006` | Produktiver Code DARF nicht über `System.out`, `System.err` oder `printStackTrace` diagnostizieren. | `automated` |
| `JCODE-ERR-007` | Fehlermeldungen SOLLEN Diagnosekontext liefern, dürfen aber keine Secrets oder unnötigen personenbezogenen Daten enthalten. | `manual-review` |

Die HTTP-Zuordnung und externe Fehlerform gehören in die API- und Error-Standards.

## 12. Logging und sensible Daten

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-LOG-001` | Produktiver Java-Code MUSS das freigegebene Logging-API verwenden. Direkte Implementierungsabhängigkeiten benötigen einen Dependency-Vertrag. | `automated` |
| `JCODE-LOG-002` | Logmeldungen SOLLEN parameterisiert erzeugt werden; deaktivierte Log-Level dürfen keine unnötig teuren Meldungswerte berechnen. | `partially-automated` |
| `JCODE-LOG-003` | `ERROR` bezeichnet unerwartete Fehler mit Betriebswirkung, `WARN` kontrollierte Auffälligkeiten, `INFO` begrenzte Lifecycle-Information, `DEBUG` Diagnose und `TRACE` Detaildiagnose. Erwartbare 4xx-Fälle werden nicht pauschal als Serverfehler geloggt. | `manual-review` |
| `JCODE-LOG-004` | Logs DÜRFEN keine Passwörter, Tokens, API-Keys, vollständigen Credentials, unkontrollierte Bodies, Binärinhalte oder fachlich sensible Daten ohne dokumentierten Betriebsbedarf enthalten. | `partially-automated` |
| `JCODE-LOG-005` | Correlation- und Trace-Informationen MÜSSEN den zentralen Observability-Vertrag verwenden. Layer dürfen keine konkurrierenden IDs erzeugen. | `partially-automated` |

## 13. Kommentare, Javadoc und Suppressions

### JCODE-DOC-001 – Kommentare erklären Grund oder Grenze

Kommentare SOLLEN erklären, warum eine nicht offensichtliche Entscheidung, Invariante, externe Einschränkung oder Übergangslösung besteht. Sie DÜRFEN nicht Identifier oder offensichtlichen Kontrollfluss in Prosa wiederholen.

**Prüfbarkeit:** `manual-review`

### JCODE-DOC-002 – Kommentare bleiben aktuell

Kommentare MÜSSEN mit dem beschriebenen Code geändert oder entfernt werden. Auskommentierter Code und Änderungsprotokolle in Quelldateien sind nicht zulässig; Git besitzt die Historie.

**Prüfbarkeit:** `partially-automated`

### JCODE-DOC-003 – Öffentliche Core-Typen besitzen Javadoc

Öffentliche Typen unter `de.cocondo.system` MÜSSEN knappe Javadoc besitzen, die Zweck, wesentliche Semantik und relevante Grenzen erklärt. Javadoc darf nicht nur den Typnamen wiederholen.

Fehlende Javadoc im aktuellen Core wird als Transition-Bestand inventarisiert und in geänderten Bereichen schrittweise geschlossen.

**Prüfbarkeit:** `partially-automated`

### JCODE-DOC-004 – Javadoc außerhalb des Core ist vertragsbezogen

Öffentliche Application- oder Demo-Typen benötigen Javadoc, wenn sie einen Extension Point, eine Configuration-/Integrationsoberfläche, eine nicht offensichtliche Lifecycle-Semantik oder ein bewusst zu übernehmendes Referenzmuster bilden.

Controller, DTOs, Entities und interne Spring-Komponenten benötigen nicht allein wegen `public` pauschale Javadoc, wenn ihr Vertrag anderweitig eindeutig ist.

**Prüfbarkeit:** `partially-automated`

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-DOC-005` | Öffentliche Methoden benötigen Javadoc, wenn Parameter, Rückgabe, Seiteneffekt, Fehlermodell oder Lifecycle aus Typen und Namen nicht eindeutig hervorgehen. Triviale oder vollständig geerbte Verträge werden nicht redundant dokumentiert. | `manual-review` |
| `JCODE-DOC-006` | `TODO`, `FIXME`, `XXX` oder vergleichbare Marker benötigen eine Debt-, Requirement-, Issue- oder Waiver-Referenz und eine konkrete Restbeschreibung. | `automated` |
| `JCODE-DOC-007` | `@SuppressWarnings`, Tool-Suppressions und `NOSONAR`-ähnliche Marker DÜRFEN nur den kleinsten Scope betreffen und benötigen Regelbezug sowie technische Begründung; Governance-relevante Suppressions zusätzlich Waiver oder Baseline. | `automated` |
| `JCODE-DOC-008` | `@Deprecated` benötigt Javadoc mit Ablösegrund, Alternative und gegebenenfalls Entfernungshorizont. | `automated` |

## 14. Spring- und Generator-Konventionen

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-SPR-001` | Spring-Stereotype MÜSSEN zur tatsächlichen Rolle passen. `@Component` darf keine unklare Verantwortung verdecken. | `partially-automated` |
| `JCODE-SPR-002` | Zusammengehörige Konfiguration SOLL typisiert und validiert gebunden werden. Verstreute `@Value`-Ausdrücke SOLLEN nicht der primäre Konfigurationsmechanismus sein. | `partially-automated` |
| `JCODE-SPR-003` | Framework-Komponenten DÜRFEN nicht mit `new` erzeugt werden, wenn dadurch Proxy-, Scope-, Configuration- oder Lifecycle-Semantik umgangen wird. | `partially-automated` |
| `JCODE-SPR-004` | Code DARF nicht voraussetzen, dass private Methoden oder Self-Invocation Spring-Proxy-Semantik wie Transaction, Security, Async oder Cache aktivieren. | `automated` |
| `JCODE-SPR-005` | Configuration- und Bean-Factory-Code DARF keine Fachlogik, Datenmigration oder versteckte Runtime-Entscheidung enthalten. | `manual-review` |
| `JCODE-SPR-006` | Neue Component-, Entity- oder Repository-Scans benötigen Prüfung gegen Java Architecture Standard und Project-New. | `automated` |
| `JCODE-GEN-001` | Generierte Java-Sources MÜSSEN in registrierten Generated-Source-Pfaden liegen und auf Generator, Eingabe und Version zurückführbar sein. | `automated` |
| `JCODE-GEN-002` | Neue Annotation Processor, Codegeneratoren oder Source-Transformationen benötigen Dependency Review und bei grundlegender Entwicklungswirkung eine ADR. | `architectural-review` |
| `JCODE-GEN-003` | Generierter Code wird bewusst geprüft oder in einem registrierten Generated-Code-Scope getrennt ausgewertet. Pauschale Ausschlüsse ohne Herkunftsnachweis sind nicht zulässig. | `automated` |

## 15. Verbotene Muster und technische Prüfung

### 15.1 Algorithmisch zu verhindernde Muster

Der Java Quality Harness MUSS mindestens folgende Muster erkennen:

- Field Injection,
- Wildcard-Imports,
- `System.out`, `System.err` und `printStackTrace`,
- leere Catch-Blöcke und Catch von `Throwable`,
- mutable nicht private Fields und mutable globale statische Zustände,
- Service-Locator- und unkontrollierte Application-Context-Zugriffe,
- auskommentierten Code,
- ungetrackte TODO-/FIXME-Marker,
- pauschale Suppressions ohne Regelbezug,
- finalizer-basierten Cleanup und `System.gc()` als Steuerung,
- Thread-Erzeugung außerhalb freigegebener Executor-/Runtime-Verträge,
- unregistrierte Generated-Source-Pfade.

Semantische Regeln zu Verantwortung, Abstraktion, Lesbarkeit und fachlicher Angemessenheit bleiben Review-Aufgabe. Automatisierte Metriken liefern dazu Evidence.

### 15.2 Toolneutraler Prüfbereich

| Regelklasse | Mindestprüfung |
|---|---|
| Source Hygiene | Encoding, Tabs, Zeilenenden, Whitespace, Dateiname, Imports |
| Naming und Visibility | Typ-, Member- und Konstantennamen, unnötige öffentliche Fläche, mutable Fields |
| Injection und Spring | Field Injection, Service Locator, private Proxy-Annahmen, lokale Scan-Erweiterungen |
| Error Handling | leere Catches, Catch von `Throwable`, verlorene Causes, Konsolenausgabe |
| Immutability | mutable statische Zustände und erkennbare Collection-Leaks |
| Complexity | Methoden-/Klassenlänge, Parameter, Nesting, zyklomatische und kognitive Komplexität |
| Duplication | duplizierte nicht generierte Codeblöcke |
| Documentation | öffentliche Core-Typen, Deprecation, TODO und Suppressions |
| Generated Code | Herkunft, Scope und getrennte Auswertung |

Checkstyle, PMD, SpotBugs, ArchUnit oder SonarQube sind mögliche Implementierungen, aber keine normative Quelle. Die kleinste geeignete Toolkombination wird nach Dependency Governance und Build and Tooling Standard festgelegt.

### 15.3 Ausführungsmodi und Fixtures

Der Harness MUSS unterstützen:

- `changed`: geänderte Java-Sources und unmittelbar betroffene Regeln,
- `all`: vollständiger Projektbestand,
- `report`: deterministischer menschen- und maschinenlesbarer Befund.

Für strict-fähige Regeln sind positive, negative und relevante Tool-Error-Fixtures erforderlich. Die Prüfungen dürfen Sources nicht verändern und müssen stabile Rule IDs, Finding-Positionen sowie Baseline-/Waiver-Behandlung nachweisen.

## 16. Bestandsbaseline und Einführung

Der verifizierte Springmaster-Bestand umfasst 62 produktive Java-Dateien.

| Merkmal | Bestand |
|---|---:|
| Tabs / CRLF / Wildcard-Imports | 0 / 0 / 0 |
| statische Imports / `var` im Produktcode | 0 / 0 |
| Field Injection | 0 |
| `System.out`/`System.err`/`printStackTrace` | 0 |
| ungetrackte TODO-/FIXME- und Suppression-Marker | 0 |
| Zeilen über 120 Zeichen | 6, maximal 126 |
| Klassen über 150 / 200 Zeilen | 2 / 1 |
| öffentliche Top-Level-Typen mit Javadoc | 11 von 61 |

Bestehende Stärken werden als Baseline gesichert, aber nicht ohne Rule Fixtures sofort strict geschaltet. Folgende Punkte sind Übergangsbestand:

- fehlende Javadoc bei bestehenden öffentlichen Core-Typen,
- einzelne lange Zeilen und Klassen,
- noch nicht festgelegte Komplexitäts- und Größenwerte,
- fehlender dedizierter Java-Quality-Toolstack.

Bestehende Findings werden nach Quality Gate Governance inventarisiert. Neue Verstöße dürfen nicht pauschal in die Transition-Baseline aufgenommen werden.

Wird ein bestehender Typ wesentlich geändert, SOLLEN lokale, risikoarme Verstöße im direkt betroffenen Bereich behoben werden. Dies rechtfertigt keine unverbundene Formatierungs-, Javadoc- oder Refactoring-Welle.

## 17. Project-New und gemanagte Projekte

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `JCODE-PROJ-001` | Ein frisch erzeugtes Projekt MUSS die für sein Profil anwendbaren Coding-Regeln ohne Springmaster-Legacy-Baseline erfüllen. | `automated` |
| `JCODE-PROJ-002` | Generatoren und Templates MÜSSEN Source Hygiene, Imports, Constructor Injection, verbotene Muster und registrierte Javadoc-Verträge korrekt erzeugen. | `automated` |
| `JCODE-PROJ-003` | Projekte MÜSSEN die angewendete Standard-, Rule-Catalog- und Toolkonfigurationsversion identifizierbar machen. | `automated` |
| `JCODE-PROJ-004` | Lokale Abweichungen gemanagter Projekte benötigen eine Deviation. Projektweite Suppressions oder reduzierte Toolprofile ohne Deviation sind nicht zulässig. | `partially-automated` |
| `JCODE-PROJ-005` | Springmaster SOLL gemanagte Projekte read-only auf verbotene Patterns, neue Suppressions, Rule-/Tooldrift, neue Findings und abgelaufene Deviations prüfen können. | `automated` |

Eine Drift-Prüfung autorisiert keine Zielmutation.

## 18. Technische Ableitungen

Aus diesem Standard werden mindestens abgeleitet:

- Java Coding Rule Catalog Entries,
- Java Source and Style Contract,
- Visibility and Javadoc Contract,
- Complexity and Size Policy,
- tool-spezifische Java-Quality-Konfiguration,
- positive und negative Fixtures,
- Java Quality Gate Report,
- Fresh-Project-Coding-Acceptance,
- Managed-Project-Coding-Drift-Report.

Vorgesehene Contract-Familie:

```text
contracts/governance/java-coding-contract.json
contracts/governance/java-quality-policy.json
```

Die endgültige Aufteilung richtet sich nach unabhängigem Lifecycle und Project Directory Governance.

## 19. Offene Entscheidungen

| Decision ID | Entscheidung | Blockiert |
|---|---|---|
| `GOV-DEC-005` | konkrete Warn- und Blockierschwellen für Methodenlänge, Klassenlänge, Parameter, Nesting und Komplexität | Quality Rule Contract und Strict Promotion |
| `GOV-DEC-007` | kleinste geeignete Kombination aus Checkstyle, PMD, SpotBugs und weiteren Prüfmitteln | Toolintegration und Maven-Profile |

Die Grundregeln zu `var`, statischen Imports, Utility-Klassen und Javadoc sind mit diesem Standard entschieden.

## 20. Abnahmekriterien

Dieser Standard ist inhaltlich vollständig, wenn:

1. Source-Format, Imports, Naming und Sichtbarkeit technisch ableitbar sind,
2. Klassenaufbau, Verantwortung und Konstruktion eindeutig sind,
3. Immutability, Collections, Optional und Nullverträge geregelt sind,
4. Methodenmetriken und semantisches Review getrennt sind,
5. Error Handling und Logging keine Fachstandards duplizieren,
6. Kommentar-, Javadoc-, Deprecation- und Suppression-Regeln eindeutig sind,
7. Spring- und Generatorregeln mit Architecture und Dependency Governance übereinstimmen,
8. algorithmische Regeln und manuelle Reviews klar getrennt sind,
9. Übergangsbestand nicht als Zielmuster gilt,
10. Project-New ohne Legacy-Ausnahme qualifiziert werden kann,
11. konkrete Tools aus den Regeln ableitbar sind, ohne selbst Normquelle zu werden.

## 21. Kanonische Ausgaben

Dieser Standard erzeugt oder kontrolliert ausschließlich:

- lokale Java-Source-, Format-, Naming- und Sichtbarkeitsregeln,
- Klassenaufbau, Konstruktion und Dependency Injection,
- Immutability-, Null-, Collection- und Methodenregeln,
- allgemeines Error Handling und Logging,
- Kommentare, Javadoc, Deprecation und Suppressions,
- allgemeine Spring- und Generator-Coding-Regeln,
- Java-Quality-Regelklassen und technische Prüfbarkeit.

Nicht zu seinen kanonischen Ausgaben gehören Package-Architektur, HTTP-Verträge, Persistence-Mapping, Permission-Semantik, Testcode-Regeln, konkrete Toolprodukte, Dependency-Listen oder Releaseversionen.

## 22. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Erstentwurf aus AGENTS.md, bestehenden Fachstandards und verifiziertem Java-Codebestand |

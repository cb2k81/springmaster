---
documentId: DOC-STD-0001
title: Java Architecture Standard
documentType: standard
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/standards/java-architecture
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

# Java Architecture Standard

## 1. Zweck und Geltungsbereich

Dieser Standard definiert die strukturellen Grenzen für Java-Code in Springmaster, in Project-New und in Projekten, die den Springmaster-Core oder Springmaster-Architekturregeln übernehmen.

Er regelt:

- Java-Namespaces und Package-Verantwortungen,
- zulässige Abhängigkeitsrichtungen,
- die Grenze zwischen wiederverwendbarem Core, Springmaster-Anwendung und Demo,
- Controller-, Application-, Domain-, Mapping-, Persistence- und Infrastrukturgrenzen,
- öffentliche, projektinterne und interne Java-API-Flächen,
- Spring-Component-Scan-, Bean- und Proxy-Grenzen,
- Transaktions- und Repository-Zugriffsgrenzen auf Architekturebene,
- Package-Zyklen und verbotene Kopplungen,
- Anforderungen an algorithmische Architekturprüfungen.

Der Standard gilt für produktiven Java-Code und für Architekturtests. Testcode darf Produktcode zur Verifikation verwenden, darf aber keine alternative Produktarchitektur etablieren.

Für menschliche, automatisierte und KI-gestützte Entwicklung gelten dieselben Architekturgrenzen.

## 2. Abgrenzung und kanonische Verantwortung

Dieser Standard ist die kanonische Quelle für:

- Namespace- und Package-Modell,
- logische Architekturflächen und ihre Abhängigkeitsrichtung,
- Core-, Application- und Demo-Grenzen,
- strukturelle Layer- und Adaptergrenzen,
- Klassifikation veröffentlichter und interner Java-Flächen,
- strukturelle Spring-, Transaktions- und Repository-Regeln,
- Architekturtest-Anforderungen.

Nicht hier geregelt werden:

| Gegenstand | Kanonische Quelle |
|---|---|
| konkrete HTTP-Pfade, DTO-Formen und Statuscodes | ADR-0002 und API-Standards |
| konkrete Service- und Transaktionssemantik | ADR-0003 und Controller/Service/UseCase Standard |
| Identity, Entity-Mapping, Auditing und Delete-Semantik | ADR-0004 und Domain Entity/Persistence Standard |
| Permission-Namen und Security-Semantik | ADR-0005 und Security Standard |
| lokale Sichtbarkeit, Klassenaufbau, Kommentare und Clean-Code-Regeln | Java Coding Standard |
| Teststufen und Testabschluss | Test Governance und Testing Standard |
| Gate-Ergebnisse, Rule Promotion und Waiver | Quality Gate Governance |
| physische Repository-Verzeichnisse | Project Directory Governance |
| Java-API-Kompatibilitätsbewertung und SemVer | Release and Version Governance |
| konkrete Architekturprüfwerkzeuge | Dependency Governance und Build and Tooling Standard |

Dieser Standard konsolidiert strukturelle Aussagen der genannten ADRs und Standards. Er ändert deren fachliche Semantik nicht.

## 3. Normative Begriffe und Regelmodell

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

Jede technisch relevante Regel besitzt eine stabile Rule ID mit dem Präfix `JARCH`.

| Prüfbarkeitsklasse | Bedeutung |
|---|---|
| `automated` | durch Source-, Bytecode- oder Dependency-Analyse deterministisch prüfbar |
| `partially-automated` | Tool erkennt Strukturindikatoren; fachliche Bewertung bleibt erforderlich |
| `manual-review` | semantische Architekturprüfung erforderlich |
| `architectural-review` | Entscheidung oder Änderung einer dauerhaften Architekturgrenze erforderlich |

Die Zuordnung von Rule ID, Prüfbarkeitsklasse, Gate, Enforcement und Tool erfolgt im Quality Rule Catalog. Dieser Standard besitzt den normativen Regeltext.

## 4. Architekturmodell

### 4.1 Logische Architekturflächen

Springmaster besitzt vier voneinander getrennte Java-Flächen:

| Fläche | Aktueller Namespace | Verantwortung |
|---|---|---|
| wiederverwendbarer Core | `de.cocondo.system` | fachfreie, in Zielprojekte übertragbare Bausteine und Verträge |
| Springmaster-Anwendung | `de.cocondo.platform.app` | ausführbare Master-Anwendung, Assembly und Springmaster-spezifische technische Endpunkte |
| Demo und Referenz | `de.cocondo.platform.demo` | ausführbare fachliche Beispiel- und Referenz-Slices |
| Test- und Tooling-Verifikation | überwiegend `de.cocondo.platform.tooling` unter `src/test` | Tests von Generatoren, Gates, Patch- und Tooling-Verträgen |

Ein erzeugtes Fachprojekt besitzt zusätzlich einen projektspezifischen Basisnamespace. Der übertragene Core bleibt unter `de.cocondo.system`.

### JARCH-MOD-001 – Logische Grenzen gelten auch im Single-Module-Build

Springmaster ist derzeit ein Maven-Modul. Package- und Architekturgrenzen gelten unabhängig davon, ob sie durch Maven-Module physisch getrennt sind.

Ein Wechsel zu mehreren Maven-Modulen oder zu einer separat publizierten Core-Distribution benötigt eine akzeptierte Architekturentscheidung und einen Migrationsplan.

**Prüfbarkeit:** `architectural-review`

### JARCH-MOD-002 – Capability Ownership vor globalen Layer-Sammlungen

Fachlicher Application- und Demo-Code SOLL nach Capability oder fachlichem Kontext gruppiert werden. Innerhalb einer nicht trivialen Capability KÖNNEN Unterpackages wie `api`, `application`, `domain`, `persistence`, `mapping` und `infrastructure` verwendet werden.

Neue globale Package-Sammlungen wie `controller`, `service`, `repository` oder `entity`, die unabhängige fachliche Capabilities vermischen, SOLLEN NICHT angelegt werden.

Technische, fachfreie Core-Packages und kleine Springmaster-Assembly-Packages sind davon ausgenommen.

**Prüfbarkeit:** `partially-automated`

### JARCH-MOD-003 – Ein Package besitzt eine eindeutige Verantwortung

Ein Package MUSS eine erkennbare fachliche oder technische Verantwortung besitzen. Es DARF nicht gleichzeitig als API-, Persistenz-, Tooling- und allgemeine Ablagefläche dienen.

Ein neues Package benötigt keinen eigenen ADR, wenn es innerhalb eines registrierten Namespace-Extension-Points liegt und die Abhängigkeitsregeln dieses Standards erfüllt.

**Prüfbarkeit:** `partially-automated`

## 5. Namespace-Standard

### JARCH-NS-001 – Kanonischer Core-Namespace

Wiederverwendbarer Springmaster-Core MUSS unter folgendem Root liegen:

```text
de.cocondo.system
```

Core-Code DARF NICHT unter `de.cocondo.platform.core`, einem Demo-Namespace oder einem projektspezifischen Fachnamespace angelegt werden.

Der gleiche Core-Namespace gilt in Springmaster und in Zielprojekten. Package-Rewrites sind kein regulärer Update-Mechanismus.

**Prüfbarkeit:** `automated`

### JARCH-NS-002 – Springmaster-Anwendungsnamespace

Springmaster-spezifische Runtime-Assembly, Master-Konfiguration und technische Master-Endpunkte liegen unter:

```text
de.cocondo.platform.app
```

Dieser Namespace DARF keinen wiederverwendbaren Core vortäuschen und SOLL keine Demo-Fachlogik aufnehmen.

**Prüfbarkeit:** `automated`

### JARCH-NS-003 – Demo- und Referenznamespace

Fachliche Demo- und Referenz-Slices liegen unter:

```text
de.cocondo.platform.demo
```

Demo-Code darf Core-Verträge verwenden. Core-Code DARF NICHT von Demo-Code abhängen.

Ein Demo-Slice wird nicht allein durch seine Package-Lage zu einem kanonischen Template oder einer veröffentlichten Referenz.

**Prüfbarkeit:** `automated`

### JARCH-NS-004 – Project-New-Namespace

Ein erzeugtes Projekt besitzt einen eigenen, bei der Erzeugung festgelegten Basisnamespace. Projektfachlichkeit und Projekt-Assembly liegen unter diesem Namespace; übertragener Springmaster-Core bleibt unter `de.cocondo.system`.

Ein Projekt DARF `de.cocondo.platform.app` oder `de.cocondo.platform.demo` nicht als eigenen Fachnamespace übernehmen, sofern kein ausdrücklich registriertes Springmaster-Referenzprofil erzeugt wird.

**Prüfbarkeit:** `automated`

### JARCH-NS-005 – Test-Namespaces spiegeln die geprüfte Verantwortung

Tests SOLLEN unter einem zum geprüften Produktpackage passenden Namespace liegen. Tooling-Vertragstests dürfen unter einem getrennten Testnamespace wie `de.cocondo.platform.tooling` liegen, wenn dieser keine produktive Runtime-Fläche darstellt.

Produktionscode DARF nicht von Klassen unter `src/test` oder test-only Namespaces abhängen.

**Prüfbarkeit:** `automated`

### JARCH-NS-006 – Neue Root-Namespaces sind Architekturänderungen

Ein neuer Root unter `de.cocondo` außerhalb der registrierten Springmaster- oder Projektprofile benötigt:

- eine dokumentierte Verantwortung,
- eine Abhängigkeitsbewertung,
- Anpassung des Architecture Contract,
- Prüfung von Component Scan, Templates und Managed-Project-Auswirkung,
- bei dauerhafter Plattformwirkung eine ADR.

**Prüfbarkeit:** `architectural-review`

## 6. Abhängigkeitsrichtungen zwischen Architekturflächen

### 6.1 Grundmatrix

`erlaubt` bedeutet, dass die Abhängigkeit bei fachlich passender Verantwortung zulässig ist. Sie ist keine pauschale Freigabe für jeden Typ.

| Von | Darf abhängig sein von | Darf nicht abhängig sein von |
|---|---|---|
| `de.cocondo.system` | JDK, freigegebene Jakarta-/Spring-Verträge, andere passende Core-Packages | `de.cocondo.platform.*`, Projektfachlichkeit, Zielprojektspezifika |
| `de.cocondo.platform.app` | Core, app-eigene Verträge und technische Infrastruktur | Demo-Implementierungsdetails, Zielprojektcode |
| `de.cocondo.platform.demo` | Core, demo-eigene Capability-Typen und freigegebene technische Libraries | `de.cocondo.platform.app`-Implementierungsdetails, andere Zielprojekte |
| projektspezifischer Code | eigener Projektcode, adoptierter Core | Springmaster-App- oder Demo-Implementierung, fremde Projektfachlichkeit |
| Test-/Tooling-Code | geprüfter Produktcode und Testwerkzeuge | produktiver Import von Testcode |

### JARCH-DEP-001 – Keine Rückabhängigkeit in den Core

Kein Typ unter `de.cocondo.system` DARF einen Typ unter `de.cocondo.platform`, einem projektspezifischen Basispackage oder einem Zielprojekt importieren oder reflektiv als feste Implementierungsabhängigkeit voraussetzen.

Konfigurierbare SPI-Nutzung ist nur zulässig, wenn das SPI im Core definiert und die Implementierung außerhalb des Core bereitgestellt wird.

**Prüfbarkeit:** `automated`

### JARCH-DEP-002 – Demo bleibt von der Master-App entkoppelt

Demo-Code DARF keine Implementierungsabhängigkeit zu `de.cocondo.platform.app` besitzen.

Die Master-App KANN Demo-Komponenten durch Scan- oder Assembly-Konfiguration einbinden. Diese Assembly-Beziehung darf nicht zu direkten fachlichen Imports aus der App in Demo-Implementierungen führen.

**Prüfbarkeit:** `automated`

### JARCH-DEP-003 – App-Assembly ist kein fachlicher Shared Layer

Gemeinsam benötigte fachfreie Verträge DÜRFEN nicht allein zur Wiederverwendung in `de.cocondo.platform.app` abgelegt werden. Sie gehören nach nachgewiesener Fachfreiheit in den Core oder verbleiben im jeweiligen Capability-Scope.

**Prüfbarkeit:** `manual-review`

### JARCH-DEP-004 – Capability-übergreifende Kopplung ist explizit

Eine Capability DARF nicht direkt auf Repository-Implementierungen oder Entities einer anderen Capability zugreifen.

Capability-übergreifende Zusammenarbeit erfolgt über:

- einen expliziten Application- oder Domain-Vertrag,
- einen Use Case,
- ein Ereignis oder einen anderen akzeptierten Integrationsvertrag.

Eine dauerhafte bidirektionale Capability-Abhängigkeit ist nicht zulässig.

**Prüfbarkeit:** `partially-automated`

## 7. Core-Grenze

### JARCH-CORE-001 – Fachfreiheit

Core-Typen MÜSSEN ohne Kenntnis einer konkreten Fachdomäne, eines Zielprojekts oder eines Demo-Slices verständlich und nutzbar sein.

Core-Typen DÜRFEN insbesondere keine fachlichen Ressourcen-, Permission-, Controller-Pfad-, Tabellen- oder Projektbezeichnungen fest einbauen.

**Prüfbarkeit:** `partially-automated`

### JARCH-CORE-002 – Wiederverwendbarer Vertrag

Ein Typ SOLL nur in den Core aufgenommen werden, wenn:

- seine Semantik fachfrei ist,
- mindestens ein belastbarer Wiederverwendungsfall besteht,
- sein Vertrag stabil genug für mehrere Projekte ist,
- Tests die Grenzen und Fehlerfälle belegen,
- Dependency- und Versionsauswirkung bewertet sind.

Mehrfache Nutzung allein rechtfertigt keine Core-Aufnahme.

**Prüfbarkeit:** `architectural-review`

### JARCH-CORE-003 – Framework-Abhängigkeiten sind begrenzt

Core-Code KANN Spring-, Jakarta- oder Persistenzverträge verwenden, wenn sie zum ausdrücklich definierten Core-Vertrag gehören. Eine Framework-Abhängigkeit DARF nicht nur aus Bequemlichkeit oder wegen einer Demo-Implementierung in den Core gezogen werden.

Core-Typen SOLLEN keine Spring-MVC-, Servlet- oder Springmaster-App-Typen verwenden, sofern sie nicht ausdrücklich einen wiederverwendbaren HTTP-Infrastrukturvertrag bilden.

**Prüfbarkeit:** `partially-automated`

### JARCH-CORE-004 – Core-Spring-Komponenten

Ein Spring-Bean im Core MUSS:

- fachfrei sein,
- in allen vorgesehenen Projektprofilen sinnvoll registrierbar sein,
- keine Demo- oder projektspezifische Konfiguration voraussetzen,
- durch Component-Scan- oder explizite Konfigurations-Evidence abgesichert sein.

Ein Core-Bean DARF nicht still von einer Springmaster-only Bean abhängen.

**Prüfbarkeit:** `partially-automated`

### JARCH-CORE-005 – Core-Promotion ist sichtbar

Die Überführung eines Typs aus Demo- oder Projektcode in den Core ist eine eigene Architekturänderung. Sie MUSS Semantik, Package, Abhängigkeiten, Tests, Versionswirkung und Managed-Project-Auswirkung gemeinsam bewerten.

Eine reine Dateiverschiebung ist kein ausreichender Promotion-Nachweis.

**Prüfbarkeit:** `architectural-review`

## 8. Springmaster-App- und Demo-Grenze

### JARCH-APP-001 – Verantwortung der Master-App

`de.cocondo.platform.app` besitzt:

- den Spring-Boot-Einstiegspunkt,
- Master-spezifische Assembly und Konfiguration,
- technische Master-Endpunkte wie Plattforminformationen,
- die kontrollierte Einbindung von Core und Demo.

Die Master-App SOLL keine Demo-Domänenlogik oder wiederverwendbare Core-Implementierung besitzen.

**Prüfbarkeit:** `partially-automated`

### JARCH-DEMO-001 – Demo ist fachlicher Beweisraum

`de.cocondo.platform.demo` dient zur ausführbaren Verifikation von Standards und Patterns. Demo-Code MUSS seinen Reife- und Referenzstatus korrekt ausweisen.

Candidate-Code DARF nicht automatisch in Project-New oder Managed Projects übernommen werden.

**Prüfbarkeit:** `manual-review`

### JARCH-DEMO-002 – Demo darf den Core verwenden, nicht umdefinieren

Demo-Code darf Core-Schnittstellen implementieren oder Core-Bausteine verwenden. Er DARF keine parallelen, konkurrierenden Core-Verträge unter dem Demo-Namespace etablieren.

Ein demospezifischer Adapter bleibt im Demo-Scope, bis eine Core-Promotion ausdrücklich akzeptiert wurde.

**Prüfbarkeit:** `partially-automated`

## 9. Layer- und Adaptergrenzen

Die folgenden Grenzen gelten unabhängig davon, ob sie bereits in getrennten Unterpackages sichtbar sind. Bei nicht trivialen Capabilities SOLL die Package-Struktur die Rollen erkennbar machen.

### JARCH-LAY-001 – Controller sind HTTP-Adapter

Controller dürfen:

- HTTP-Eingaben binden und Boundary Validation aktivieren,
- an eine Application-, Query-, Command- oder Use-Case-Grenze delegieren,
- HTTP-Status, Header und API-DTOs gemäß API-Vertrag zurückgeben.

Controller DÜRFEN NICHT:

- Repositories oder `EntityManager` injizieren oder aufrufen,
- Transaktionen besitzen,
- Persistenzabfragen konstruieren,
- Entities oder Spring-Data-Pagingtypen als öffentlichen Vertrag exponieren,
- wiederverwendbare Business- oder Autorisierungslogik besitzen.

**Prüfbarkeit:** `automated`

### JARCH-LAY-002 – Application Boundary orchestriert Use Cases

Application Services, Query Services, Command Services oder Use-Case-Handler besitzen die Anwendungsorchestrierung.

Sie dürfen:

- Repositories und technische Ports koordinieren,
- Transaktionen besitzen,
- Autorisierung an der wiederverwendbaren Operationsgrenze durchsetzen,
- Domain-Verhalten und Mapper verwenden,
- Application-Ergebnisse und DTOs erzeugen.

Sie SOLLEN keine HTTP-Servlet-Typen, `ResponseEntity` oder Controller-Annotationen verwenden.

**Prüfbarkeit:** `partially-automated`

### JARCH-LAY-003 – Domain-Verhalten ist HTTP-unabhängig

Domain-Modelle und Domain Services DÜRFEN nicht von Spring MVC, Servlet API, HTTP-DTOs, `ResponseEntity`, Controllern oder globalen Exception Handlern abhängen.

Eine Domain Entity KANN gemäß ADR-0004 JPA-Annotationen besitzen. Persistenzbewusstsein hebt die HTTP- und Application-Unabhängigkeit nicht auf.

Domain Services SOLLEN keine Repositories koordinieren, wenn diese Orchestrierung zu einem Application Use Case gehört.

**Prüfbarkeit:** `partially-automated`

### JARCH-LAY-004 – Repositories sind Persistence Adapter

Repositories dürfen Entities, Projections und persistence-orientierte Typen verwenden. Sie DÜRFEN NICHT:

- von Controllern aufgerufen werden,
- API-Response-Envelopes erzeugen,
- HTTP- oder Security-Entscheidungen treffen,
- fachliche Use-Case-Orchestrierung besitzen.

Nicht triviale neue Capabilities SOLLEN Repositories in einem erkennbaren Persistence-Scope ablegen.

**Prüfbarkeit:** `automated`

### JARCH-LAY-005 – Mapper konvertieren Schichten

Mapper dürfen Quell- und Zieltypen konvertieren und technisch notwendige Normalisierung durchführen.

Mapper DÜRFEN NICHT:

- Repositories, `EntityManager` oder externe Clients verwenden,
- Transaktionen oder Autorisierung besitzen,
- Lifecycle-Entscheidungen oder Business-Invarianten treffen,
- versteckte Datenbankabfragen auslösen.

Komplexe Read-Model-Orchestrierung gehört in die Query- oder Application-Schicht.

**Prüfbarkeit:** `automated`

### JARCH-LAY-006 – Infrastruktur implementiert technische Ports

Externe Clients, Messaging-, Dateisystem-, Clock-, Security- oder andere technische Adapter SOLLEN hinter expliziten Application- oder Core-Verträgen liegen, wenn Austauschbarkeit, Testbarkeit oder Projektpropagation dies erfordert.

Infrastrukturcode DARF nicht als allgemeine Abkürzung für fachliche Orchestrierung verwendet werden.

**Prüfbarkeit:** `partially-automated`

### JARCH-LAY-007 – Globaler Error Adapter bleibt an der Boundary

Ein globaler HTTP-Exception-Handler darf Application- und Domain-Fehler auf den API-Fehlervertrag abbilden.

Domain-, Repository- und Mapper-Code DARF nicht vom globalen Handler oder von HTTP-Fehlerantworten abhängen.

**Prüfbarkeit:** `automated`

## 10. Öffentliche und interne Java-APIs

### 10.1 API-Klassen

Java-Sichtbarkeit und Plattform-Kompatibilitätsgarantie sind getrennte Konzepte.

| API-Klasse | Bedeutung |
|---|---|
| `published-api` | ausdrücklich registrierter, projektübergreifend unterstützter Core-Vertrag |
| `project-api` | innerhalb eines Projekts oder einer Capability bewusst verwendbarer Vertrag ohne automatische Plattformgarantie |
| `internal` | Implementierungsdetail; keine Nutzung außerhalb des erlaubten Scopes |

### JARCH-API-001 – `public` bedeutet nicht automatisch veröffentlicht

Ein `public` Core-Typ gilt nur dann als `published-api`, wenn er im Java API Surface Contract registriert ist und Release-/Kompatibilitätsregeln auf ihn angewendet werden.

Frameworkbedingte öffentliche Sichtbarkeit, Bean-Registrierung, JPA-Konstruktoren oder Serialisierbarkeit erzeugen keine automatische Kompatibilitätsgarantie.

**Prüfbarkeit:** `automated` gegen Registry, sonst `manual-review`

### JARCH-API-002 – Minimale exportierte Fläche

Neue Typen und Member SOLLEN die kleinste für ihren Vertrag erforderliche Sichtbarkeit besitzen. Implementierungen, Adapter und Hilfstypen sollen package-private oder innerhalb eines klaren internen Scopes liegen, soweit Framework und Vertrag dies erlauben.

Konkrete Java-Sichtbarkeitsregeln gehören in den Java Coding Standard.

**Prüfbarkeit:** `partially-automated`

### JARCH-API-003 – Interne Typen werden nicht querschnittlich verwendet

Ein als intern klassifizierter Typ DARF nicht aus fremden Capabilities, Zielprojekten oder veröffentlichten APIs referenziert werden.

Ein Package-Name wie `internal` ist ein unterstützendes Signal, ersetzt aber nicht den Architecture Contract.

**Prüfbarkeit:** `automated`

### JARCH-API-004 – Öffentliche Core-Fläche ist explizit

Welche Core-Packages oder Typen eine Kompatibilitätsgarantie erhalten, MUSS vor der ersten Strict-Kompatibilitätsprüfung im Java API Surface Contract entschieden werden.

Bis dahin dürfen bestehende öffentliche Core-Typen nicht pauschal als dauerhaft veröffentlichte API behauptet werden.

**Prüfbarkeit:** `architectural-review`

## 11. Spring- und Runtime-Grenzen

### JARCH-SPR-001 – Component Scan ist explizit und getestet

Springmaster scannt die registrierten Master- und Core-Namespaces explizit. Erzeugte Projekte scannen ihren Projektbasisnamespace und `de.cocondo.system`.

Neue Spring-Komponenten MÜSSEN innerhalb eines registrierten Scan-Scope liegen oder durch eine explizite Konfiguration eingebunden werden.

Eine Änderung der Scan-Roots benötigt Spring-Context-Tests und, wenn Project-New betroffen ist, Fresh-Project-Acceptance.

**Prüfbarkeit:** `automated`

### JARCH-SPR-002 – Entity- und Repository-Scan besitzen begrenzten Scope

Entity- und Repository-Scans SOLLEN auf die tatsächlich benötigten Namespaces begrenzt bleiben. Eine Erweiterung darf keine unbeabsichtigten Entities oder Repositories registrieren.

Änderungen an Entity- oder Repository-Scan MÜSSEN durch Context- und Persistence-Evidence abgesichert sein.

**Prüfbarkeit:** `partially-automated`

### JARCH-SPR-003 – Konfiguration besitzt einen Owner

Spring-Konfigurationen, Bean-Factories und Runtime-Properties MÜSSEN einer klaren Architekturfläche gehören.

- wiederverwendbare fachfreie Konfiguration kann im Core liegen,
- Springmaster-only Assembly liegt in der App,
- demo-spezifische Beans bleiben im Demo-Scope,
- projektspezifische Konfiguration bleibt im Projektbasisnamespace.

**Prüfbarkeit:** `partially-automated`

### JARCH-SPR-004 – Keine Container-Abhängigkeit im Domain-Modell

Entities und fachliche Value Objects DÜRFEN keine Beans aus dem Spring Context beziehen, keine statischen Application-Context-Zugriffe verwenden und keine Services lokalisieren.

JPA-Listener dürfen nur eng begrenzte technische Lifecycle-Aufgaben besitzen und keine Use Cases ausführen.

**Prüfbarkeit:** `automated`

### JARCH-SPR-005 – Proxy-Semantik ist an sichtbaren Boundaries verankert

Transaktions-, Security- oder andere Proxy-basierte Semantik DARF nicht von privater Self-Invocation oder nicht-proxyfähigen Aufrufspfaden abhängen.

Proxy-relevante Annotationen gehören auf eine von außen aufgerufene Application- oder Use-Case-Grenze oder auf eine ausdrücklich akzeptierte Konfiguration.

**Prüfbarkeit:** `partially-automated`

## 12. Transaktions- und Persistenzgrenzen

### JARCH-TX-001 – Transaktionen gehören an die Application Boundary

Controller, Mapper, DTOs und Entities DÜRFEN keine Transaktionsgrenze besitzen.

Write-Transaktionen gehören an Command Service, Application Service oder Use-Case-Handler. Read-Transaktionen können an Query Service oder Application Service liegen, wenn Persistenzkonsistenz dies erfordert.

Die konkrete Semantik richtet sich nach ADR-0003 und dem Controller/Service/UseCase Standard.

**Prüfbarkeit:** `automated`

### JARCH-TX-002 – Repository-Zugriff ist durch die Application Boundary geschützt

Produktiver Repository- oder `EntityManager`-Zugriff MUSS hinter einer Application-, Query-, Command- oder Use-Case-Grenze erfolgen.

Domain Services dürfen Repositories nur verwenden, wenn sie ausdrücklich die Application-Einstiegsgrenze des Use Cases bilden. Ein interner Domain Helper soll keine Persistenzorchestrierung übernehmen.

**Prüfbarkeit:** `partially-automated`

### JARCH-TX-003 – Ein Command besitzt eine erkennbare Transaktionsverantwortung

Eine state-changing Operation MUSS einen eindeutigen Transaktionsowner besitzen. Mehrere konkurrierende oder implizit verschachtelte Owner sind zu vermeiden.

Langlaufende externe I/O darf nicht ohne spezifische Integrationsentscheidung in einer Datenbanktransaktion ausgeführt werden.

**Prüfbarkeit:** `manual-review`

### JARCH-TX-004 – Persistenztypen verlassen die Persistence Boundary kontrolliert

Entities, JPA-Proxies, `EntityManager`, Spring-Data-`Page`, `Pageable` oder `Slice` DÜRFEN nicht Bestandteil eines öffentlichen HTTP-Vertrags sein.

Application-interne Verwendung bleibt zulässig; die API-Grenze verwendet DTOs und definierte Envelopes.

**Prüfbarkeit:** `automated`

## 13. Security- und Datenzugriffsgrenzen

### JARCH-SEC-001 – Wiederverwendbare Autorisierung liegt an der Operationsgrenze

Controller-Security kann ein grobes HTTP-Gate bilden. Die wiederverwendbare Autorisierungsentscheidung für Management-Operationen MUSS an Query Service, Command Service, Application Service, Use-Case-Handler oder einem ausdrücklich akzeptierten Policy Adapter liegen.

Repositories, Entities und Mapper DÜRFEN keine Autorisierungsentscheidung treffen.

**Prüfbarkeit:** `partially-automated`

### JARCH-SEC-002 – Daten-Scope ist kein Controller-Filter

Tenant-, Organisations- oder andere Data-Scope-Prädikate gehören in Query-/Command-Grenzen oder dedizierte Policies. Sie DÜRFEN nicht allein als ad-hoc Controller-Filter implementiert werden.

**Prüfbarkeit:** `manual-review`

### JARCH-SEC-003 – Security-Framework-Typen bleiben an technischen Boundaries

Domain-Entities und fachfreie Core-Verträge SOLLEN nicht von Security-Context-, Token- oder HTTP-Authentisierungstypen abhängen.

Komplexe Security-Prüfungen gehören in einen Authorization Collaborator oder Policy Service, nicht in lange, schwer testbare Annotation-Ausdrücke.

**Prüfbarkeit:** `partially-automated`

## 14. Zyklen und verbotene Kopplungen

### JARCH-CYC-001 – Keine Package-Zyklen zwischen Architekturflächen

Zwischen Core, App, Demo, Projektfachlichkeit und Tooling DÜRFEN keine zyklischen Abhängigkeiten bestehen.

**Prüfbarkeit:** `automated`

### JARCH-CYC-002 – Keine Capability-Zyklen

Zwei fachliche Capabilities DÜRFEN nicht dauerhaft bidirektional voneinander abhängen.

Ein erkannter Zyklus MUSS durch einen expliziten Vertrag, eine Verantwortungsverschiebung oder eine akzeptierte Integrationsentscheidung aufgelöst werden.

**Prüfbarkeit:** `automated` für Imports; `manual-review` für semantische Zyklen

### JARCH-CYC-003 – Verbotene Rückkopplungen

Folgende Kopplungen sind für neuen Code verboten:

- Core zu App, Demo oder Zielprojekt,
- Demo zu Master-App-Implementierung,
- Controller zu Repository oder `EntityManager`,
- Mapper zu Repository, Transaktion oder Autorisierung,
- Entity zu Controller, Application Service oder Security Context,
- Repository zu HTTP-Response-Typen,
- Produktionscode zu Testcode,
- Project-New-Produktcode zu Springmaster-Demo-Implementierungen.

**Prüfbarkeit:** `automated`

### JARCH-CYC-004 – Keine parallelen Architekturverträge

Eine Capability DARF keine lokalen Paralleltypen einführen, die einen aktiven Core- oder Plattformvertrag mit gleicher Verantwortung imitieren, ohne eine bewusste Abweichung oder Ablösung zu dokumentieren.

**Prüfbarkeit:** `partially-automated`

## 15. Architekturverifikation

### 15.1 Toolneutrale Anforderung

Architekturgrenzen MÜSSEN soweit algorithmisch möglich durch Source-, Bytecode- oder Dependency-Analyse geprüft werden. Die Wahl eines konkreten Tools ist nicht Teil dieses Standards.

ArchUnit ist ein möglicher Kandidat, aber erst nach Dependency Review, Fixture-Prototyp und Quality-Rule-Qualifikation verbindlich.

### JARCH-VER-001 – Mindestumfang der automatisierten Architekturprüfung

Der Architecture Gate MUSS mindestens prüfbar machen:

- `de.cocondo.system` importiert kein `de.cocondo.platform.*`,
- Demo importiert keine App-Implementierung,
- Produktionscode importiert keinen Testcode,
- Controller greifen nicht auf Repository oder `EntityManager` zu,
- Controller tragen keine Transaktionsgrenze,
- Mapper verwenden keine Repository-, Transaktions- oder Security-Grenzen,
- Entities hängen nicht von Controller- oder Application-Service-Typen ab,
- registrierte interne Typen werden nicht außerhalb ihres Scopes genutzt,
- Package- oder Capability-Zyklen werden erkannt,
- Scan- und Namespace-Verträge bleiben konsistent.

**Prüfbarkeit:** `automated`

### JARCH-VER-002 – Architekturregeln besitzen Rule IDs und Fixtures

Jede automatisierte Architekturregel MUSS:

- eine Rule ID dieses Standards referenzieren,
- mindestens eine positive und eine negative Fixture besitzen,
- Findings und Tool Errors trennen,
- deterministische, kompakte Reports erzeugen,
- den geprüften Scope ausweisen.

**Prüfbarkeit:** `automated`

### JARCH-VER-003 – Keine sofortige Strict-Einführung

Neue Architekturprüfungen werden entsprechend der Quality Gate Governance zunächst qualifiziert und report-only ausgeführt. Eine Strict-Promotion erfolgt erst nach Bestandsanalyse, stabilen Fixtures und geklärten Übergangsabweichungen.

**Prüfbarkeit:** `automated` gegen Rule Catalog

### JARCH-VER-004 – Changed- und Full-Audit-Modus

Der Architecture Gate SOLL einen schnellen Changed-/Affected-Modus und einen vollständigen Auditmodus besitzen.

Changed-Scope-Prüfung darf keine für den geänderten Vertrag erforderliche transitive Abhängigkeitsprüfung auslassen. Full Audit bleibt für Promotion, Release und periodische Bestandsprüfung erforderlich.

**Prüfbarkeit:** `automated`

### JARCH-VER-005 – Semantische Architekturprüfung bleibt sichtbar

Tooling kann Import-, Annotation-, Sichtbarkeits- und Zyklusregeln prüfen. Fachfreiheit, angemessene Verantwortungsgrenzen, Core-Promotion und Capability-Schnitt bleiben ergänzende Architekturreview-Aufgaben.

Eine automatisierte Teilprüfung DARF nicht als vollständiger semantischer Architekturnachweis dargestellt werden.

**Prüfbarkeit:** `manual-review`

## 16. Übergangsbaseline des aktuellen Springmaster-Stands

### 16.1 Aktuell bestätigte Struktur

Der aktuelle Bestand bestätigt:

- Core unter `de.cocondo.system`,
- Master-App unter `de.cocondo.platform.app`,
- Demo unter `de.cocondo.platform.demo`,
- expliziten Component Scan für Plattform und Core,
- Entity Scan für Demo und Core,
- Repository Scan für Demo,
- keine Importabhängigkeit vom Core zur Plattform,
- keine Importabhängigkeit der Demo zur Master-App.

### 16.2 Zulässige Übergangsformen

Folgende Bestandsformen werden nicht allein durch Aktivierung dieses Standards zu blockierenden Verstößen:

- die aktuell flache Package-Struktur des Catalog-Demo-Slices,
- der kombinierte `CatalogItemService` mit Query- und Command-Verantwortung im Candidate-Slice,
- aktuelle öffentliche Core-Typen ohne bereits finalisierte Published-API-Registry,
- vorhandene manuelle Mapper und manuell erzeugte Validatoren,
- das Fehlen eines dedizierten Architecture-Gate-Werkzeugs.

Diese Formen sind keine automatische Empfehlung für neuen, nicht trivialen Code. Neue Verstöße dürfen nicht über eine Transition-Baseline legitimiert werden.

### 16.3 Migration statt Big Bang

Bestehende Abweichungen werden:

1. inventarisiert,
2. einer Rule ID zugeordnet,
3. als akzeptierter Bestand, Debt oder Migrationskandidat klassifiziert,
4. in begrenzten Änderungsschnitten behoben,
5. erst danach für die betreffende Regel strict blockierend.

Der Standard verlangt keine pauschale Package-Umsortierung des bestehenden Codes.

## 17. Project-New und gemanagte Projekte

### JARCH-PROJ-001 – Project-New erzeugt getrennte Namespace-Flächen

Project-New MUSS:

- den Projektbasisnamespace und `de.cocondo.system` getrennt behandeln,
- beide erforderlichen Scan-Scope korrekt konfigurieren,
- keine Springmaster-Demo-Implementierungen als Projektfachlichkeit kopieren,
- Architecture Contracts und anwendbare Tests bereitstellen,
- mit einem frischen Projekt nachweisen, dass Core und Projektcode gemeinsam starten.

**Prüfbarkeit:** `automated`

### JARCH-PROJ-002 – Managed Projects adoptieren statt umdeuten

Ein gemanagtes Projekt dokumentiert den adoptierten Architekturstandard und lokale Abweichungen. Legacy-Namespaces oder andere Layerstrukturen werden über Migrations- oder Deviation-Regeln behandelt und nicht still als kanonischer Springmaster-Standard umgedeutet.

**Prüfbarkeit:** `partially-automated`

### JARCH-PROJ-003 – Read-only Architecture Drift

Springmaster SOLL gemanagte Projekte read-only auf folgende Punkte prüfen können:

- Core-Namespace und unerlaubte Rückabhängigkeiten,
- Package- und Capability-Zyklen,
- Controller-/Repository- und Transaktionsgrenzen,
- Abweichungen der Public API Surface,
- abgelaufene Architecture Deviations.

Eine Drift-Prüfung autorisiert keine Zielmutation.

**Prüfbarkeit:** `automated`

## 18. Technische Ableitungen

Aus diesem Standard werden mindestens abgeleitet:

- Java Architecture Contract,
- Namespace- und Package-Profile,
- Abhängigkeitsmatrix,
- Java API Surface Contract,
- Architecture Rule Catalog Entries,
- positive und negative Architecture Fixtures,
- Architecture Gate Report,
- Fresh-Project-Architecture-Acceptance,
- Managed-Project-Architecture-Drift-Report.

Vorgesehene Contract-Familie:

```text
contracts/governance/java-architecture-contract.json
contracts/governance/java-api-surface-contract.json
```

Die endgültige Dateiaufteilung richtet sich nach unabhängigem Lifecycle und Project Directory Governance.

## 19. Offene Entscheidungen

Folgende Entscheidungen sind für die spätere technische Umsetzung noch offen:

| Decision ID | Entscheidung | Blockiert |
|---|---|---|
| `GOV-DEC-006` | ArchUnit oder gleichwertiges Architecture-Gate-Werkzeug | Toolintegration und Architecture Gate |
| `GOV-DEC-012` | konkrete Core-Packages oder Typen mit Published-API-Garantie | Java API Surface Contract und Kompatibilitätsgate |

Diese Entscheidungen blockieren den normativen Standard nicht. Bis zu ihrer Klärung dürfen jedoch weder ein konkretes Architekturtool noch eine pauschale Core-Kompatibilitätsgarantie als verbindlich behauptet werden.

## 20. Abnahmekriterien

Dieser Standard ist inhaltlich vollständig, wenn:

1. alle bestehenden Root-Namespaces korrekt abgebildet sind,
2. Core, App, Demo, Projektcode und Testtooling klar getrennt sind,
3. zulässige und verbotene Abhängigkeitsrichtungen eindeutig sind,
4. Controller-, Application-, Domain-, Repository- und Mapper-Grenzen technisch ableitbar sind,
5. Spring-Scan- und Proxy-Grenzen beschrieben sind,
6. Transaktions- und Security-Platzierung strukturell eindeutig sind,
7. `public` und `published-api` unterschieden sind,
8. Package- und Capability-Zyklen verboten und prüfbar sind,
9. Project-New und Managed Projects profilbezogen berücksichtigt sind,
10. bestehende Candidate- und Legacy-Strukturen nicht als neues Zielmuster missverstanden werden,
11. konkrete Architecture Rules mit IDs, Fixtures und Reports ableitbar sind,
12. keine Detailregel der referenzierten ADRs oder Standards konkurrierend neu definiert wird.

## 21. Kanonische Ausgaben

Dieser Standard erzeugt oder kontrolliert ausschließlich:

- Java-Namespace- und Package-Modell,
- logische Architekturflächen,
- Java-Abhängigkeitsrichtungen,
- Core-, App-, Demo- und Projektgrenzen,
- Public-/Internal-API-Klassifikation,
- strukturelle Layer-, Spring-, Transaktions- und Security-Grenzen,
- Architekturtest-Anforderungen.

Nicht zu seinen kanonischen Ausgaben gehören konkrete HTTP-Verträge, Persistence-Mappings, Permission-Namen, Coding-Grenzwerte, Teststufen, Toolprodukte oder Releaseversionen.

## 22. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Erstentwurf aus ADR-0002 bis ADR-0005, bestehenden Standards und aktuellem Springmaster-Codebestand |

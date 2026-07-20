# AGENTS.md

## Geltungsbereich

Diese Datei gilt für das gesamte Springmaster-Repository. Eine tiefer liegende `AGENTS.md` darf Regeln für ihren Teilbaum präzisieren, aber keine akzeptierte ADR oder verbindliche Sicherheitsregel stillschweigend aufheben.

Die Datei wurde aus dem vollständigen Springmaster-Export vom 17. Juli 2026 abgeleitet. Vor jeder Änderung sind der tatsächliche Working Tree, `platform/versions/platform.env`, `pom.xml` und die für den Auftrag relevanten aktuellen Dokumente erneut zu prüfen.

## Verbindliche lokale Ausführungspfade

Für vorbereitete und manuell ausgeführte Springmaster-Kommandos gelten diese Pfade:

```bash
cd /opt/cocondo/springmaster || exit 1
```

Patch-ZIPs und andere vom Benutzer heruntergeladene Übergabeartefakte werden ausschließlich unter folgendem Pfad erwartet:

```text
/home/cb/Downloads
```

Kein vorbereiteter mutierender Befehl darf sich auf das aktuelle Terminalverzeichnis verlassen. Jeder ausführbare Block setzt das Arbeitsverzeichnis explizit. Ein Bundle- oder Patch-Runner muss vor einer Mutation den sauberen Git-Status, den erwarteten Downloadpfad und die Patchdatei prüfen.

## Auftrag des Projekts

Springmaster ist die kanonische Entwicklungs- und Verteilungsbasis für Cocondo-Backend-Grundlagen. Das Repository hat vier zusammengehörige Rollen:

1. **Tooling Source** für Patch-, Export-, Build-, DBTool-, Project-New-, Gate- und Platform-Update-Werkzeuge.
2. **Platform Core** für fachfreie, wiederverwendbare Java-Bausteine unter `de.cocondo.system`.
3. **Demo- und Referenzanwendung** für ausführbare, testbare Backend-Muster unter `de.cocondo.platform.demo`.
4. **Standards- und Entscheidungsquelle** für APIs, Architektur, Persistenz, Sicherheit, Verifikation und spätere Zielprojekt-Updates.

Springmaster ist kein Sammelplatz für projektspezifische Fachlogik und kein automatischer Remediator für bestehende Zielprojekte.

## Quellen der Wahrheit

Nutze Quellen in dieser Reihenfolge und für ihren jeweiligen Zweck:

1. **Akzeptierte ADRs** unter `PROJECT_DOCS/ADR/` definieren dauerhafte Architekturentscheidungen. Neuere akzeptierte Ergänzungen oder explizite Ablösungen gehen älteren Aussagen vor.
2. **Akzeptierte Standards** unter `PROJECT_DOCS/STANDARDS/` definieren die detaillierten Verträge. Lies den aktuellen Status und spätere Ergänzungsabschnitte, nicht nur den ursprünglichen Dokumentanfang.
3. **Ausführbarer Code, Tests und Golden Fixtures** definieren, was die aktuelle Baseline tatsächlich implementiert und prüft.
4. **Maschinenlesbare Evidence-Dateien** definieren insbesondere deklarierte Reife- und Gate-Zustände. Prüfe ihre Detailaussagen gegen neuere Tests und Implementierungsnotizen.
5. **`platform/versions/platform.env`** ist die kanonische Quelle für aktuelle Plattform- und Komponentenstände.
6. **Planungs-, Readiness-, Review- und Changelog-Dokumente** liefern Kontext und Historie, sind aber nicht automatisch der aktuelle Sollvertrag.

Bei Widersprüchen nicht raten und nicht stillschweigend eine Seite auswählen. Ermittle die jüngste akzeptierte Entscheidung, vergleiche sie mit Code und Tests und behandle die Abweichung als explizit zu lösende Inkonsistenz.

Wichtige aktuelle Zustände:

- `CatalogItem` ist ein `candidate-reference-slice`, kein `canonical-reference-slice`.
- Catalog-demo ist `not-canonical` und verwendet derzeit `documented-deferred-security`.
- Die produktive CatalogItem-Demo arbeitet weiterhin in-memory. `CatalogItemJpaQueryReference` ist Referenzcode, kein registrierter Runtime-Bean und kein Nachweis einer vollständigen persistenten Anwendung.
- Zielprojektvergleich und Zielprojektauslieferung sind für eine automatische Catalog-demo-Übernahme nicht freigegeben.
- Gate-Ausführung ist grundsätzlich report-only, solange eine Regel nicht nach ADR-0006 ausdrücklich als strict-ready promoviert wurde.
- ADR-0008 bis ADR-0010 sind akzeptiert. Konfiguration, DB-Migration/DBTool und die lokale HTTP-Korrelationsbaseline sind durch maschinenlesbare Verträge und Tests abgesichert. Verteiltes Tracing, externe Metrik-/Log-Backends und Produktionsmigrationen bleiben ausdrücklich deferred.

## Repository-Orientierung

| Pfad | Verantwortung |
|---|---|
| `src/main/java/de/cocondo/system/**` | wiederverwendbarer, fachfreier Core |
| `src/test/java/de/cocondo/system/**` | Core-Vertragstests |
| `src/main/java/de/cocondo/platform/app/**` | ausführbare Springmaster-Anwendung |
| `src/main/java/de/cocondo/platform/demo/**` | Demo- und Referenz-Slices |
| `src/test/java/de/cocondo/platform/**` | App-, Demo-, OpenAPI- und Tooling-Vertragstests |
| `src/test/resources/tooling/**` | Golden Reports und maschinenlesbare Tooling-Evidence |
| `PROJECT_DOCS/ADR/**` | akzeptierte Architekturentscheidungen und ADR-Governance |
| `PROJECT_DOCS/STANDARDS/**` | normative technische Standards |
| `PROJECT_DOCS/CORE/**` | Core-Klassifikation, Migration und Implementierungsevidence |
| `PROJECT_DOCS/DEMO/**` | Demo-Reifegrad, Candidate-Evidence und Contract Reports |
| `PROJECT_DOCS/TOOLING/**` | Tool-Verträge, Sicherheits- und Verifikationsabläufe |
| `PROJECT_DOCS/TARGET_UPDATES/**` | Zielprojekt-Registry und Update-Evidence |
| `bin/**` | Bash-/Python-Tooling |
| `platform/versions/platform.env` | aktuelle Komponenten- und Foundation-Versionen |
| `platform/update/**` | Target-Deskriptoren, Regeln, Templates und Update-Tooling |
| `patches/logs/**/CHANGELOG-*.md` | Legacy-Provenienz der lokalen Patch-Engine, keine zweite Produktwahrheit |

## Technische Baseline

- Java 21.
- Maven-Projekt mit Spring Boot 3.3.x.
- Spring MVC, Bean Validation, Springdoc OpenAPI, Liquibase und MariaDB; H2 nur für Tests.
- JUnit 5, AssertJ und MockMvc für Java- und HTTP-Vertragstests.
- Bash- und Python-Tooling soll lokal, deterministisch und mit möglichst wenigen externen Abhängigkeiten funktionieren.
- Keine neue Bibliothek, kein Framework und kein Codegenerator ohne nachweisbaren Bedarf, passende Tests und erforderlichen Architektur-/Versionsentscheid.

## Arbeitsweise für Änderungen

1. **Änderungsbereich klassifizieren.** Core, Demo, API-Vertrag, Tooling, Template, Platform-Update, Dokumentation und Zielprojektarbeit haben unterschiedliche Regeln.
2. **Relevante Entscheidungen lesen.** Mindestens die betroffene ADR, den Detailstandard und die vorhandenen Tests/Golden Fixtures prüfen.
3. **Ist-Verhalten sichern.** Vor der Änderung gezielte Tests oder Report-Familien identifizieren; bestehende öffentliche Verträge nicht aus Vermutung ableiten.
4. **Kleinsten vollständigen Schnitt implementieren.** Keine fachfremden Refactorings, Formatierungswellen oder Nachbarbereinigungen in denselben Change aufnehmen.
5. **Vertrag und Evidence gemeinsam pflegen.** Code, Tests, OpenAPI-/Report-Goldens, aktuelle Dokumentation und Versionsstand müssen dieselbe Aussage treffen.
6. **Risikobasiert verifizieren.** Zuerst gezielt, danach die für den Change vorgeschriebene breitere Prüfung.
7. **Abschluss transparent berichten.** Geänderte Dateien, ausgeführte Prüfungen, verbleibende Deferrals und nicht ausgeführte Prüfungen nennen.

Eine explizite Aufgabe definiert den gewünschten Scope, hebt aber akzeptierte ADRs nicht automatisch auf. Verlangt die Aufgabe eine Architekturänderung, muss die Entscheidung sichtbar angepasst oder ergänzt werden; die Änderung darf nicht nur im Code versteckt werden.

## Paket- und Modulgrenzen

- Wiederverwendbarer Core liegt ausschließlich unter `de.cocondo.system`.
- `de.cocondo.platform.*` gehört zur ausführbaren Springmaster-App, Demo und projektlokalem Tooling-Testcode.
- `SpringmasterApplication` scannt bewusst `de.cocondo.platform` und `de.cocondo.system`. Neue Core-Spring-Komponenten oder Projekt-Templates dürfen diese Scan-Grenze nicht versehentlich verlieren.
- Lege keinen Core unter `de.cocondo.platform.core` an.
- Demo-Code darf Core verwenden, aber Core darf keine Demo-, Zielprojekt- oder Fachdomänenabhängigkeit erhalten.
- Core-Schnittstellen bleiben fachfrei. Fachliche Filter, Controller-Pfade, Permissions und Persistenzentscheidungen gehören in das konkrete Modul.
- Überführe Demo-Code nicht allein deshalb in den Core, weil er mehrfach verwendet werden könnte. Erst fachfreie Semantik, stabiler Vertrag und belastbare Tests rechtfertigen Core-Aufnahme.

## HTTP- und API-Verträge

Für neue oder geänderte Management-APIs gelten ADR-0002 und die Standards unter `PROJECT_DOCS/STANDARDS/API/`.

- Controller exponieren ausschließlich DTOs und definierte Response-Envelopes.
- Keine JPA-Entity, kein Repository, kein `EntityManager`, kein Spring-Data-`Pageable`, `Page` oder `Slice` im öffentlichen API-Vertrag.
- Request Bodies mit Constraints verwenden `@Valid @RequestBody` oder einen gleichwertigen validierten Boundary-Mechanismus.
- Öffentliche IDs sind opaque Strings. Business Keys wie `sku`, `code` oder `number` bleiben eigene Felder.
- Kanonische Ressourcenpfade:
  - paged: `GET /api/<domain>/<resources>`;
  - vollständig: `GET /api/<domain>/<resources>/all` nur als vollständiges, nicht still begrenztes Result Set;
  - count-only: `GET /api/<domain>/<resources>/count` nur bei echtem Consumer-Bedarf;
  - detail: `GET /api/<domain>/<resources>/{id}`;
  - alternate key: `GET /api/<domain>/<resources>/by-<key>/{value}`;
  - create: `POST /api/<domain>/<resources>`;
  - full update: `PUT /api/<domain>/<resources>/{id}`;
  - single delete: bodyless `DELETE /api/<domain>/<resources>/{id}`;
  - complex search: `POST /api/<domain>/<resources>/search`;
  - Commands und Beziehungen nach den spezialisierten Command-/Relationship-Standards.
- Paged Queries verwenden `page`, `size`, `sortBy`, `sortDir` und explizite fachliche Filter.
- `/all` verwendet dieselben Filter- und Sortiersemantiken, aber keine öffentlichen `page`-/`size`-Parameter und keine stille Kappung.
- `/count` verwendet dieselben Filter- sowie Security-/Data-Scope-Prädikate, aber keine Paging- oder Sortierparameter. Antwort: `CountResponseDTO` mit `totalElements`.
- Sortierfelder sind öffentliche API-Feldnamen und müssen über eine Allowlist aufgelöst werden. Nutze eine stabile Tie-Breaker-Sortierung.
- `/options` ist für kleine, begrenzte Selektor-Daten; `/reference-data` benötigt eine dokumentierte, ADR-gestützte Semantik.
- Keine neuen öffentlichen Pfade oder Operation IDs mit `findOne`, `findFirst`, `findLast`, `loadPage`, `/list` oder Repository-Vokabular.
- Create: `201 Created`, möglichst mit `Location` auf die opaque ID.
- Full Update: standardmäßig `200 OK` mit DTO.
- Erfolgreiches bodyless Delete: `204 No Content`; unbekannte Ressource: `404 Not Found`.
- Bulk Delete ist ein `POST .../commands/delete-multiple`, kein body-bearing `DELETE`.
- Fehler laufen über den Core-Fehlervertrag und den globalen Handler. Keine lokalen ad-hoc `Map<String,Object>`-Fehlerkörper und keine neuen Controller-`@ExceptionHandler`, wenn der globale Vertrag greift.

## Controller-, Service- und Transaktionsgrenzen

Nach ADR-0003:

- Controller sind dünne HTTP-Adapter: Binding, Boundary Validation, Delegation, HTTP-Status und Header.
- Controller greifen nie direkt auf Repository oder `EntityManager` zu und tragen kein `@Transactional`.
- Repositories liegen hinter `ResourceService`, `QueryService`, `CommandService` oder Use-Case-Handlern.
- Schreiboperationen besitzen eine explizite Write-Transaction an der Application Boundary.
- Read-Transactions dürfen `readOnly = true` verwenden, wenn JPA-Konsistenz oder Mapping dies verlangt.
- Ein HTTP-Command entspricht grundsätzlich einer Business-Transaktion. Langlaufende externe I/O gehört nicht ungeprüft in eine DB-Transaktion.
- Keine Abhängigkeit von privater Self-Invocation für Spring-Proxy-Transaktionssemantik.
- Bei nicht-trivialen Ressourcen Read- und Write-Verantwortung strukturell trennen. Das ist keine Pflicht zu einem CQRS-Framework.
- Domain Services enthalten wiederverwendbare Domänenregeln, nicht HTTP-Orchestrierung.

## Persistenz und Identität

Nach ADR-0004:

- Standard-Aggregate Roots können `DomainEntity` als `@MappedSuperclass`-Basis verwenden; konkrete Entities besitzen ihre eigene `@Entity`- und Tabellenabbildung.
- Persistenz-ID und öffentliche ID sind standardmäßig opaque Strings. Code darf daraus keine fachliche Bedeutung ableiten.
- IDs werden bevorzugt über `IdGeneratorService` oder eine gleichwertige explizite Boundary erzeugt.
- Create-APIs akzeptieren keine clientgewählten Ressourcen-IDs ohne expliziten Import-/Sync-Entscheid.
- Business Keys sind keine technischen `@Id`-Felder. Eindeutigkeit wird in Application Validation und Persistenz-Constraints abgesichert.
- `persistenceVersion` ist die aktuelle Optimistic-Locking-Basis. Konflikte dürfen nicht als generische `500` enden.
- Audit-Felder sind Infrastrukturwerte und kein Client-Input.
- Hard Delete, Soft Delete, Archive, Deactivate und Restore sind unterschiedliche Domänenentscheidungen; keine Semantik verstecken.
- Liquibase-Änderungen müssen deterministisch, vorwärtsgerichtet und mit DBTool-/Test-Evidence geliefert werden.

## Mapping, DTOs und Collections

- Mapper konvertieren Schichten und enthalten keine Repository-Zugriffe, Transaktionen, Autorisierung, externen Calls oder Lifecycle-Entscheidungen.
- Manuelle Mapper und MapStruct sind erlaubt; MapStruct ist keine Pflicht.
- DTO-Namen machen ihre Rolle sichtbar, zum Beispiel `CreateDTO`, `UpdateDTO`, `ListItemDTO`, `OptionDTO`, `CommandDTO`, `CommandResultDTO`.
- Inbound-DTOs dürfen keine Persistenztypen als bequeme Abkürzung exponieren.
- Mutable Collections defensiv kopieren und null-sicher normalisieren.
- Query-Kriterien können als immutable Records modelliert werden, wenn dies den fachlichen Vertrag klarer macht.
- Normalisierung von fachlichen Strings ist deterministisch; für technische Case-Normalisierung `Locale.ROOT` verwenden.

## Sicherheit und Permissions

Nach ADR-0005:

- Jeder Endpoint wird als `public`, `authenticated`, `management`, `technical` oder `system` klassifiziert. Fehlende Klassifikation bei Application Resources bedeutet `management`.
- Management-Operationen benötigen operation-level Permissions nach `<domain>:<resource>:<operation>`.
- Anwendungscode prüft Permissions, nicht Rollenamen.
- Controller-Security darf ein grobes HTTP-Gate sein; die wiederverwendbare Autorisierung sitzt an Service-/Use-Case-Boundaries.
- Repositories, Entities und Mapper treffen keine Autorisierungsentscheidung.
- `401` bedeutet fehlende/ungültige Authentisierung; `403` bedeutet authentisiert, aber nicht autorisiert.
- Capability- und Precheck-Antworten unterstützen UI-Zustände, ersetzen aber niemals die Prüfung bei der tatsächlichen Command-Ausführung.
- Behaupte keine implementierte Management-Security, solange nur `documented-deferred-security` vorliegt.

## Catalog-demo und Referenzstatus

- Kopiere Candidate-Code nicht automatisch als kanonisches Template.
- Ein Slice wird nur durch eine ausdrückliche, evidence-basierte Zustandsänderung `canonical-reference-slice`.
- Eine Canonicalization-Behauptung benötigt mindestens Endpoint-, DTO-, Validation-, Error-, Application-, Persistence-, Mapping-, Security-, OpenAPI-/Gate- und Deferral-Evidence.
- Neue Demo-Erweiterungen bleiben candidate-level, solange Durable Persistence, Liquibase, implementierte Management-Security, erforderliche OpenAPI-Evidence und Gate-Promotion nicht explizit geschlossen sind.
- Historische `legacy-demo-seed`-Texte nicht als aktuellen Zustand missverstehen; aktuelle maschinenlesbare Candidate-Evidence und neuere Implementierungsnotizen berücksichtigen.

## Java-Konventionen

- Bestehenden Stil fortführen: 4 Leerzeichen, explizite Imports, Constructor Injection, keine Field Injection.
- Keine Lombok-Einführung ohne eigene Entscheidung und Nutzenbegründung.
- Öffentliche Core-Typen mit knapper Javadoc zu Semantik und Grenzen dokumentieren; keine Javadoc, die nur den Typnamen wiederholt.
- Validierungs-, Not-Found- und Conflict-Fälle mit spezifischen Exceptions ausdrücken und global auf den API-Fehlervertrag mappen.
- Tests deterministisch halten: kein Netzwerk, keine reale Uhr ohne kontrollierte Abstraktion, keine Abhängigkeit von Testreihenfolge.
- Für API-Verträge MockMvc und OpenAPI-Snapshots/Assertions verwenden. Positive und negative Fälle testen.
- Golden Fixtures nur ändern, wenn die Vertragsänderung beabsichtigt ist; Änderung durch den zugehörigen Regressionstest absichern.

## Bash- und Python-Tooling

- Bash-Skripte beginnen mit `#!/usr/bin/env bash` und `set -euo pipefail`.
- Projektroot robust aus dem Skriptpfad ableiten und gemeinsame Umgebung über `bin/init.env.sh` beziehungsweise vorhandene Libs laden.
- Konsolenausgabe kompakt halten; detaillierte Diagnostik in deterministische Log-/Reportdateien schreiben.
- Mutierende Tools benötigen Fail-Closed-Preflights und dürfen keine stillen Fallbacks auf unsichere Defaults einführen.
- Python-Tools verwenden `argparse`, klare Exit-Codes, UTF-8, deterministische JSON-Ausgabe und soweit möglich nur die Standardbibliothek.
- Tool-Ausführungsfehler strikt von report-only Findings unterscheiden.
- Bei Änderungen an Patch-, Export- oder Platform-Update-Tooling positive und negative Integration Fixtures ergänzen. Rollback-, Hash-, Pfad- und Berechtigungsklassen nicht nur im Happy Path testen.

## Verifikation nach Änderungstyp

Führe mindestens die zur Änderung passende Prüfung aus. Starte gezielt und erweitere danach auf die geforderte Breite.

### Dokumentation ohne Vertrags- oder Statuswirkung

```bash
git diff --check
```

Kein Maven-Lauf ist standardmäßig nötig. Ändert die Dokumentation jedoch einen maschinenlesbaren Vertrag, einen Reifezustand, eine Golden Fixture oder Tooling-Semantik, gelten die Prüfungen des betroffenen Bereichs.

### Java-, Core- oder Demo-Code

```bash
mvn -q -Dtest=<RelevanterTest> test
mvn -q test
```

Bei API-, OpenAPI-, Error-, Query- oder Gate-Verträgen zusätzlich:

```bash
mvn -q -Pspringmaster-gates-report test
./bin/springmaster-gates.sh report --clean
```

Report-only Findings sind nicht automatisch Fehler. Tool-Ausführungsfehler sind Fehler.

### Tooling

Für geänderte Dateien mindestens:

```bash
bash -n <geändertes-script.sh>
python3 -m py_compile <geändertes-tool.py>
./bin/tooling-selfcheck.sh --no-export
```

Zusätzlich die fachlich passende Integration-/Regression-Suite ausführen, zum Beispiel `springmaster-gates-selfcheck.sh`, `springmaster-gates-regression.sh`, `patch-system-it.sh`, `patch-artifact-preflight-it.sh` oder einen zugehörigen Java-Tooling-Test.

### POM, Abhängigkeiten, Build oder Release-Artefakte

```bash
mvn clean verify
```

Für einen ausdrücklich verlangten Runtime-Build:

```bash
./bin/build.sh
```

### Datenbank und Liquibase

Nicht destruktiv beginnen:

```bash
./bin/dbtool.sh status
./bin/dbtool.sh changelogs
```

`rebuild-dev` und `rebuild-stage` sind destruktiv und nur bei ausdrücklicher Anforderung sowie `APP_DBTOOL_ALLOW_DESTRUCTIVE=true` zulässig.

### Handoff, Release oder Audit

Ein Full-Export ist kein Standardabschluss jeder Änderung. Nur bei ausdrücklichem Handoff-, Release- oder Audit-Bedarf:

```bash
./bin/export.sh full --zip
```

Für Tooling-Qualifikation mit bewusstem Export:

```bash
./bin/tooling-selfcheck.sh --export
```

Quellhashes stammen aus dem Raw-Byte-`fileManifest` der Metadatei, niemals aus der gerenderten Textdarstellung.

## Patch-, Git- und Export-Governance

Nach ADR-0012 ist das Patchsystem ein Transaktionsmechanismus; Git bleibt die dauerhafte Repositoryhistorie.

- Erzeuge nicht für jede normale lokale Änderung künstlich Patch-ZIPs, Patchnummern, Acceptance-Evidence oder Full-Exports.
- Wenn der Auftrag ausdrücklich ein lieferbares Patchartefakt verlangt, gelten Manifest-, Baseline-Hash-, Sandbox- und Artifact-Preflight-Regeln vollständig.
- Neue lieferbare Patchartefakte führen eine globale, sequenzunabhängige `artifactId`; die lokale `patchId` dient nur der Apply-Reihenfolge und Provenienz.
- Das Manifest ist die Transaktionswahrheit. Der aktuelle `CHANGELOG` ist eine Legacy-Pflicht der vorhandenen Engine, keine zweite dauerhafte Produktbeschreibung.
- Vor einem Patch-Apply vollständige Live-Baseline-Hashes prüfen; keine Hashes aus dem Textexport ableiten.
- Qualifizierte Patch-ZIPs gegen einen sauberen committed Baseline-Stand prüfen:

```bash
./bin/patch.sh live-baseline <patch.zip>
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh artifact-preflight <patch.zip> --no-export
```

- Für einen ausdrücklich verlangten lokalen Patchabschluss ohne Release-/Handoff-Export bevorzugt den validierten Flow verwenden:

```bash
./bin/patch.sh accept <patch.zip> --no-export --commit
```

- Niemals pauschal `git add .` verwenden. Keine fremden oder bereits vorgestagten Änderungen übernehmen.
- Kein Push ohne ausdrückliche Freigabe; `--push` ist immer separat und bewusst.
- Keine fremden Änderungen zurücksetzen, überschreiben oder in denselben Commit ziehen.
- Lokale Runtime-, Validation-, Accept-, Build-, Export- und Generated-Artefakte nicht committen.

Insbesondere nicht versionieren:

```text
.env
target/
build/
tmp/
exports/
patches/archives/
patches/runtime/
patches/logs/accept/
patches/logs/validation/
platform/update/generated/
platform/update/manifests/
```

## Versionierung und Dokumentationspflicht

- Prüfe bei jeder Änderung, ob eine Komponenten- oder Foundation-Version nach `SPRINGMASTER_VERSION_POLICY.md` erhöht werden muss.
- Core-Code/API betrifft typischerweise `PLATFORM_CORE_VERSION`; Tooling-Verträge `PLATFORM_TOOLING_VERSION`; Demo-Fähigkeiten `PLATFORM_DEMO_VERSION`; Templates `PLATFORM_TEMPLATE_VERSION`; Target-Update-Mechanik `PLATFORM_UPDATE_VERSION`.
- Nicht pauschal alle Versionen erhöhen. `PLATFORM_STATE_PATCH` nur gemäß aktueller Version Policy setzen.
- Architektur- oder Vertragsentscheidungen nicht nur in einem Changelog oder Implementierungsplan festhalten. Betroffene ADR/Standards und aktuelle Evidence müssen übereinstimmen.
- Historische Changelogs nicht als Living Documentation umschreiben, außer eine ausdrücklich beauftragte Provenienzkorrektur verlangt es.
- Neue dauerhafte Produktverträge und ADR-Entscheidungen nicht an lokale numerische Patch-IDs koppeln. Patch-IDs sind Provenienz, keine fachliche Versionsidentität.
- Eine report-only Regel nur nach den sechs Promotion-Kriterien aus ADR-0006 als strict markieren: akzeptierte Regelquelle, stabile getestete Implementierung, Referenzevidence, deterministische Kriterien, kompakte Reports und dokumentierte Promotion.

## Zielprojekte und Platform Update

- Bestehende Projekte sind standardmäßig read-only Vergleichs- oder Lieferziele. Keine direkte Änderung aus dem Springmaster-Checkout ohne ausdrücklich autorisierten Update-Flow.
- `plan`, `generate`, `preflight`, `compatibility-plan` und `apply-plan` dürfen Zielprojekte nicht mutieren.
- `target-apply` ist der einzige Platform-Update-Befehl, der ein Zielprojekt verändern darf, und benötigt eine ausdrückliche Aufgabe/Freigabe.
- Target-Deskriptor, erlaubtes Profil, erwartete Versionen, Baseline-Hashes, Kompatibilität und Ziel-Tests vor jeder Lieferung prüfen.
- Keine Springmaster-`.env`, lokalen Defaults oder projektspezifischen Pfade ungeprüft in ein Zielprojekt kopieren.
- Generated-Slice-Spec, IR und Patch-Blueprint sind Planungs-/Generierungsverträge. Sie autorisieren weder Source Rendering noch Target Mutation allein durch ihre Existenz.
- Jeder generierte Target-Patch führt Payload, betroffene Komponentenstände, `PLATFORM_STATE_PATCH`, Compatibility-Entscheidung und Managed-State-Provenienz atomar in derselben Transaktion.
- Profile, Payloadpfade, Scope und Validation Policy stammen aus `platform/update/rules/profiles.json`; neue Hardcodierungen im Shell-Dispatcher sind nicht zulässig.
- Vor Generate, Preflight und Apply muss die Compatibility Matrix den konkreten Source-to-Target-Übergang freigeben. Downgrades und ungeprüfte Major-Sprünge bleiben fail-closed.
- Ein isolierter Pilot unter `target/` oder einem temporären Pfad ist Evidence, aber keine Freigabe für ein reales Zielprojekt.

## Definition of Done

Eine Änderung ist erst abgeschlossen, wenn:

- der Scope klein und vollständig ist;
- relevante ADRs und Standards eingehalten oder sichtbar aktualisiert wurden;
- Code, Tests, OpenAPI/Reports, Golden Fixtures, Evidence und aktuelle Dokumentation dieselbe Aussage treffen;
- erforderliche Versionsänderungen erfolgt sind;
- gezielte und bereichsweite Prüfungen erfolgreich waren oder bewusst ausgelassene Prüfungen begründet genannt werden;
- keine Secrets, lokalen Artefakte oder fremden Änderungen enthalten sind;
- keine unbelegte Canonicalization-, Security-, Persistence-, Strict-Gate- oder Target-Delivery-Behauptung gemacht wird;
- der Abschlussbericht geänderte Dateien, ausgeführte Kommandos, Resultate und verbleibende Deferrals enthält.

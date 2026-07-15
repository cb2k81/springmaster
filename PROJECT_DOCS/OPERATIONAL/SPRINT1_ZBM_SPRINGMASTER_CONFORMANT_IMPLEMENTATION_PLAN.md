# Sprint 1: Springmaster-konforme Umsetzung von ZBM

## 1. Status und Verbindlichkeit

Dieses Dokument ist der operative Steuerungs- und Freigabeplan für Sprint 1 der Springmaster-konformen ZBM-Umsetzung.

Es persistiert den nach der forensischen Doppel-Baseline-Analyse festgelegten Arbeitsplan, damit Ziele, Reihenfolge, Qualitätsgates und Eigentumsgrenzen nicht durch den weiteren Chat- oder Patchverlauf driften.

Sprint 1 ist erst abgeschlossen, wenn die in Abschnitt 12 definierte Definition of Done nachweislich erfüllt ist. Ein dokumentierter Plan, eine statische Codeprüfung oder eine lokale Simulation allein reichen nicht als Freigabenachweis.

## 2. Sprintziel

ZBM wird zunächst sicher auf den aktuellen freigegebenen Stand der Springmaster-Tools und des Springmaster-System-Kernels gebracht. Darauf aufbauend werden die fachlichen Grundlagen des ZBM-Fachkonzepts so geschlossen, dass ein erster fachlicher Service-Slice nach den Springmaster-Patterns deterministisch erzeugt, in einer isolierten ZBM-Sandbox angewendet und vollständig geprüft werden kann.

Die verbindliche Zielkette lautet:

```text
saubere Springmaster-Baseline
        ↓
qualifizierte Springmaster-Delivery-Mechanik
        ↓
ZBM-Tooling-Cutover
        ↓
ZBM-System-Kernel-Cutover
        ↓
ZBM Pilot-Readiness
        ↓
Fachmodell und Invarianten
        ↓
Persistence und Validation
        ↓
Security und Permissions
        ↓
GeneratedServiceSlice-Spezifikation
        ↓
IR → Blueprint → Renderer → Patch
        ↓
ZBM-Sandbox-Pilot
        ↓
Live-Apply nach ausdrücklicher Freigabe
```

## 3. Eigentums- und Architekturgrenzen

| Bereich | Verbindlicher Eigentümer |
|---|---|
| Patch-, Export-, Update- und Generator-Tooling | Springmaster |
| Gemeinsamer technischer Kernel unter `de.cocondo.system` | Springmaster |
| Generische API-, Query-, Error-, Validation- und Delivery-Patterns | Springmaster |
| Fachlichkeit unter `de.cocondo.zbm` | ZBM |
| ZBM-Persistence und Liquibase-Migrationen | ZBM |
| ZBM-Rollen, Permissions und Security-Verträge | ZBM |
| Projektlokale Scopes, Zielpfade und `.env`-Erweiterungen | ZBM |
| Betriebliche ZBM-Konfiguration | ZBM |

Verbindliche Regeln:

1. Springmaster enthält keine ZBM-Fachlogik.
2. ZBM-spezifische Tabellen, Rollen, Pfade, Scopes und Sonderfälle werden nicht im zentralen Springmaster-Tooling hart kodiert.
3. ZBM-Fachcode wird nicht in Tooling- oder Kernel-Cutover-Patches vermischt.
4. Der System-Kernel enthält keine ZBM-Domainlogik.
5. `BusinessPartner` und `CatalogItem` bleiben Referenz- beziehungsweise Golden-Fixtures und werden nicht als ZBM-Domäne übernommen.
6. Bestehende ZBM-Entities werden nur nach einer expliziten Adoption-, Konflikt- und Migrationsentscheidung in einen generierten Slice eingebunden.

## 4. Bestätigte Ausgangslage

### 4.1 Springmaster

Die analysierte Baseline weist unter anderem folgende Versionen aus:

```text
PLATFORM_VERSION=0.13.65-foundation
PLATFORM_CORE_VERSION=0.3.6
PLATFORM_TOOLING_VERSION=0.3.25
PLATFORM_UPDATE_VERSION=0.8.4
```

Vorhanden sind:

- Exportformat v2;
- Raw-Byte-Manifest;
- Closure-Evidence;
- Patch Artifact Preflight;
- Generated-Slice Spec Contract und Golden Fixture;
- Spec-to-IR-Transformation;
- target-neutraler Patch-Blueprint;
- Query-, DTO-, Error-, Validation- und Security-Patterns;
- aktueller System-Kernel.

Noch nicht operativ geschlossen sind:

- dependency-vollständige Tooling-Delivery;
- vollständig patchvertragskonforme Manifestgenerierung durch `platform-update`;
- target-bound Renderer;
- Patch-Assembler;
- Existing-Domain-Adoption;
- vollständige Konflikt- und Migrationsklassifikation;
- konkrete ZBM-Persistence- und Security-Bindings;
- vollständiger ZBM-Sandbox-Pilot.

### 4.2 ZBM

Die analysierte Baseline weist unter anderem folgende Versionen aus:

```text
PLATFORM_VERSION=0.13.41-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.11
```

Vorhanden sind:

- ein früher Time-Recording-Domain-Seed;
- erste JPA-Annotationen;
- Liquibase-ChangeSets;
- erste Domain- und Mappingtests;
- ein älterer Patch- und Exporttooling-Stand.

Nicht geschlossen sind:

- Exportformat v2 und Raw-Byte-Evidence;
- aktueller Artifact Preflight;
- aktueller System-Kernel;
- reale JPA-/Repository-Runtime;
- aktives und getestetes Liquibase;
- realer Bean-Validation-Provider;
- fachliche Application Services;
- REST-API und DTO-Boundary;
- globaler API-Error-Contract;
- OpenAPI-Verträge;
- Security und Permissions;
- fachlich vollständige Invarianten.

## 5. Prioritäten

### P0: vor jedem fachlichen Pilot

1. Saubere und commit-paritätische Springmaster- und ZBM-Baselines bestätigen.
2. Springmaster Platform-Update-/Delivery-Vertrag schließen.
3. ZBM-Tooling auf den freigegebenen Springmaster-Stand bringen.
4. ZBM-Exportformat und Evidence auf v2 bringen.
5. ZBM-System-Kernel getrennt aktualisieren.
6. Bestehenden ZBM-Maven-Teststand herstellen.
7. Fachlich falsche Invarianten und Tests korrigieren.
8. Persistence-, Validation- und Security-Entscheidungen treffen und testen.

### P1: Pilotfähigkeit

1. Fachmodell und Status-Commands schließen.
2. JPA-, Repository- und Liquibase-Runtime aufbauen.
3. Permission Vocabulary und Security implementieren.
4. Pilotaggregat begründet auswählen.
5. Target Bindings und Kollisionsklassifikation erstellen.
6. Generator nur um konkret benötigte generische Funktionen erweitern.
7. Ersten standardisierten Service-Slice in einer isolierten ZBM-Sandbox erzeugen und prüfen.

### P2: nachgewiesene Erweiterungen nach Pilotreife

1. Weitere Aggregate und Relationship-Commands.
2. Export-/Abrechnungssicht und Historisierung.
3. weitergehende Generatorabdeckung.
4. betriebliche Performance-, Last- und Recovery-Tests.

P2-Themen werden in Sprint 1 nur bearbeitet, wenn sie sich als nachgewiesener Blocker der Sprint-1-Definition-of-Done erweisen.

## 6. Arbeitspakete und Freigabegates

### AP0: Host-Truth und Baseline-Freigabe

Vor jedem Patch sind für das betroffene Projekt zu bestätigen:

- leerer `git status --short`;
- vollständiger Git-HEAD und Branch;
- aktuelle Latest-Patch-ID;
- Plattformversionen;
- Java- und Maven-Version;
- relevante `.env`-Scopes und Zielpfade;
- geltende `AGENTS.md`, ADRs und Governance-Dokumente;
- keine laufende Patchoperation;
- ein zum HEAD passender Full-Export, wenn dieser als Baseline dient.

**Gate G0:** Beide Projekte besitzen eine saubere, eindeutig identifizierte und nicht veraltete Ausgangsbasis.

### AP1: Springmaster Delivery Closure

Der erste technische Sprintpatch liegt in Springmaster.

Ziel ist, dass `platform-update` ein Tooling-Patchartefakt erzeugt, das den aktuellen Springmaster-Patchvertrag vollständig erfüllt und gegen die konkrete Zielbaseline fail-closed qualifiziert werden kann.

Erforderlich sind mindestens:

1. dependency-vollständiges Tooling-Profil;
2. Übertragung aller vom Selfcheck und Artifact Preflight benötigten Dateien;
3. konsistente Manifestfelder `id`, `patchId`, `name` und `scope`;
4. vollständige `baseline.expectedBeforeSha256`-Abdeckung;
5. Hashableitung aus echten Zielrepository-Bytes oder einem autoritativen v2-Raw-Byte-Manifest;
6. korrekter Git-Mode-Vertrag;
7. Producer Artifact Preflight;
8. isolierter Ziel-Dry-run und Ziel-Apply;
9. Payload-Byte- und Changed-Path-Parität;
10. target-sichere Versions- und Konfigurationsbehandlung.

**Nicht-Ziele:** kein ZBM-Apply, kein Kernel-Update, kein Fachcode und keine ZBM-Sonderlogik.

**Gate G1:** Springmaster kann ein vom aktuellen Ziel-Patchsystem akzeptiertes, dependency-vollständiges und baseline-gebundenes Tooling-Artefakt erzeugen.

### AP2: ZBM Tooling Cutover

Der Tooling-Cutover erfolgt in getrennten Patches.

#### AP2.1 Atomarer Tooling-Bootstrap

Der erste ZBM-Patch verwendet das ausdrücklich freigegebene Profil
`tooling-cutover`. Er übernimmt gemeinsames Tooling, darunter insbesondere:

```text
bin/patch.py
bin/patch.sh
bin/export.sh
bin/init.env.sh
bin/tooling-selfcheck.sh
bin/patch-artifact-preflight.py
bin/patch-artifact-preflight-it.sh
bin/export-integrity-check.py
bin/export-integrity-it.sh
bin/lib/**
PROJECT_DOCS/TOOLING/**
```

Die Host-nahe Delivery-Analyse hat nachgewiesen, dass ein Legacy-Ziel nach einem
reinen Tooling-Apply noch keinen integren Closure-Export erzeugen kann, solange
seine Exportkonfiguration mutable Validation-Logs einschließt. Als eng begrenzte
Bootstrap-Ausnahme enthält derselbe Patch deshalb eine aus der ZBM-Konfiguration
synthetisierte `export.config.json`, die ausschließlich den verbindlichen
Ausschluss `patches/logs/validation/**` ergänzt und alle ZBM-Werte erhält.
Springmaster-Defaults werden nicht kopiert.

Das Ziel-Accept läuft mit `--profile tooling --full-test --no-export`. Danach
erzeugt `target-apply` genau einen Full-v2-Export mit Closure-Evidence und prüft
ihn gegen die echten ZBM-Bytes. Nicht enthalten sind ZBM-Fachcode, `pom.xml`,
Kernel, Datenbankmigrationen oder lokale Fachscopes.

#### AP2.2 ZBM-lokale Tooling- und Versionskonfiguration

Ein separater, reviewbarer ZBM-Patch ergänzt anschließend die übrigen
projektlokalen Verträge, insbesondere:

- `APP_EXPORT_PROJECT_KEY=zbm`;
- `APP_CORE_PACKAGE=de.cocondo.system`;
- projektlokale Patch-Scopes;
- ZBM-spezifische Exportprofile;
- versionsgenaue Tooling-Angaben in `platform.env`.

Springmaster-Defaults dürfen weiterhin nicht blind über ZBM-Konfigurationen
kopiert werden.

**Gate G2:** ZBM-Tooling-Selfcheck, Artifact-Preflight-Fixtures, Exportintegrität und Full Maven sind grün; genau ein integerer ZBM-Full-Export liegt vor.

### AP3: ZBM System-Kernel Cutover

Tooling und Kernel bleiben getrennt.

Vor dem Kernel-Patch werden geprüft:

- konkreter Deltaumfang unter `de.cocondo.system`;
- Import-, Konstruktor- und Methodensignaturen;
- bestehende ZBM-Nutzung geänderter Core-Typen;
- benötigte Maven-Abhängigkeiten;
- vorhandene Core- und Domain-Regressionstests.

Der Kernel-Patch darf nur Springmaster-eigene Kernelpfade und unmittelbar notwendige Versions-/Dependency-Dateien enthalten. Änderungen unter `de.cocondo.zbm` sind ausgeschlossen.

**Gate G3:** ZBM verwendet den freigegebenen Springmaster-Kernel; Core-targeted Tests, ZBM-Domain-Regression, Full Maven und Full-v2-Export sind grün.

### AP4: ZBM Pilot-Readiness

Ein ZBM-lokaler Evidence-Patch dokumentiert und entscheidet:

- bestätigte Tooling- und Kernelversion;
- Fachmodellbefund;
- Aggregate Boundary;
- Pilotaggregat;
- natürlicher Business Key oder bewusster Verzicht auf Alternate Lookup;
- Persistence-Entscheidung;
- Security-Entscheidung;
- API-Basispfad;
- Target Bindings;
- Konflikt- und Migrationsklassifikation;
- lokale Patch-Scope-Entscheidung;
- Stop-Bedingungen;
- Sandbox- und Live-DoD.

`Period` beziehungsweise der fachlich abgestimmte Tätigkeitszeitraum ist nur ein Kandidat. Die Auswahl wird erst nach der fachlichen und technischen Prüfung verbindlich.

**Gate G4:** Keine offene Architektur- oder Fachentscheidung verhindert die fachliche Runtime-Umsetzung.

### AP5: Fachliche Runtime-Korrektur

Noch ohne REST-Service-Slice werden mindestens geschlossen:

- `PeriodType.SINGLE` bildet genau einen Kalendertag ab;
- Zeitraumgrenzen sind valide;
- Tätigkeitsbeginn liegt vor Tätigkeitsende;
- Tätigkeitsnachweise liegen im zugehörigen Zeitraum;
- Tätigkeitsdauer ist positiv;
- Pause überschreitet die Gesamtdauer nicht;
- Pause und Dauer besitzen ein belastbares Modell;
- Reisestatus und typabhängige Pflichtfelder sind eindeutig;
- Statusübergänge, Delete- und Änderungsregeln sind fachlich modelliert;
- fachlich falsche Tests werden korrigiert;
- die Rolle von `GebExport` ist als View, Snapshot, Exportlauf oder historisiertes Objekt entschieden.

**Gate G5:** Fachliche Invarianten und Statusübergänge sind durch positive und negative Tests nachgewiesen.

### AP6: Persistence und Validation

Erforderlich sind:

- Spring Data JPA;
- realer Datenbanktreiber;
- aktives, profilabhängiges Liquibase;
- Repositories im ZBM-Fachpackage;
- Application Services als Transaktionsgrenzen;
- realer Bean-Validation-Provider;
- Constraint-Parität zwischen Liquibase und JPA;
- Datenbank-, Repository-, Rollback- und Optimistic-Lock-Tests.

Bereits angewendete Liquibase-ChangeSets werden nicht nachträglich verändert. Korrekturen erfolgen über neue ChangeSets.

**Gate G6:** Liquibase, JPA, Repositories, Transaktionen und Bean Validation sind in einer realen oder ausdrücklich qualifizierten Testdatenbank grün.

### AP7: Security und Permissions

Vor der Freigabe fachlicher Endpunkte werden entschieden und umgesetzt:

- Authentifizierungsgrenze;
- Principal-Modell;
- Permission Vocabulary;
- Rollen-zu-Permission-Zuordnung;
- eigene versus fremde Daten;
- Berechtigungen für Lesen, Anlegen, Ändern, Schließen, Wiederöffnen, Löschen und Relationships;
- `401`-/`403`-Vertrag;
- Testprincipals und negative Security-Tests.

Fachliche Zustandskonflikte werden nicht als `403`, sondern entsprechend dem API-Error-Contract als fachlicher Konflikt behandelt.

**Gate G7:** Authentifizierungs-, Autorisierungs- und fachliche Konfliktfälle sind eindeutig getrennt und getestet.

### AP8: Standardisierter erster Service-Slice

Erst nach G7 wird eine ZBM-Slice-Spezifikation erstellt.

Sie enthält mindestens:

- Slice-ID und Aggregate Root;
- Create-, Update-, Read- und ListItem-DTO-Verträge;
- Filter- und Sort-Allowlist;
- stabilen Sort-Tie-Breaker;
- paged List;
- `/all` mit denselben Filter- und Sortierregeln;
- `/count` über denselben gefilterten Datenraum;
- Detailzugriff;
- fachlich begründeten Alternate Lookup oder explizit keinen;
- Error-, Validation- und Permission-Verträge;
- Status- und Relationship-Commands;
- Persistence-Disposition;
- Existing-Domain-Adoption;
- Testselektoren.

Springmaster ergänzt nur die generischen Generatorfunktionen, die für den konkret qualifizierten Pilot benötigt werden:

- Existing-Domain-Adoption;
- target-bound Bindings;
- Renderer;
- Patch-Assembler;
- Konflikt- und Migrationsklassifikation;
- optionale Alternate Lookups;
- Persistence- und Security-Bindings.

Der Generator wird mindestens gegen die BusinessPartner-Golden-Fixture, eine zweite abweichende Struktur und die ZBM-Binding-Fixture geprüft.

**Gate G8:** Spec, IR, Blueprint, Renderer und Patch-Assembler sind deterministisch und domänenneutral qualifiziert.

### AP9: ZBM Sandbox-Pilot

Die Pilotkette lautet:

```text
Spec
→ Fixture Gate
→ IR
→ Blueprint
→ target-bound Renderer
→ Patch-ZIP
→ Producer Artifact Preflight
→ ZBM-Live-Dry-run
→ isolierter ZBM-Apply
→ targeted Tests
→ Full Maven
→ API-/OpenAPI-/DB-/Security-Gates
→ genau ein Full-v2-Export
```

Ein Live-Apply ist erst nach vollständiger Sandbox-Closure und ausdrücklicher Benutzerfreigabe zulässig.

**Gate G9:** Der generierte Pilotpatch ist vollständig sandboxqualifiziert.

**Gate G10:** Live-Apply, Commit und Push sind ausdrücklich freigegeben und erfolgreich abgeschlossen.

## 7. Verbindliche Springmaster-Patterns für ZBM

Für fachliche Service-Slices gelten mindestens:

1. Keine Entity als Request Body.
2. Separate Create-, Update-, Read- und ListItem-DTOs.
3. Application Service als Transaktionsgrenze.
4. Controller ohne Domainlogik.
5. Explizite und testbare Mapper.
6. Filter und Sortierung ausschließlich per Allowlist.
7. Stabile Sortierung mit Tie-Breaker.
8. `/all` ohne Pagination, aber mit denselben Filtern und derselben Sortierung wie die Liste.
9. `/count` zählt exakt denselben gefilterten Datenraum.
10. Globaler API-Error-Contract.
11. Definierte `400`-, `401`-, `403`-, `404`- und `409`-Familien.
12. Bean Validation mit realem Provider.
13. OpenAPI- und Request-Validation-Gates.
14. Security vor Freigabe fachlicher Endpunkte.
15. Delete, Statuswechsel und Relationships als Commands, wenn fachlich kein CRUD vorliegt.
16. Liquibase und JPA drücken dieselben Constraints aus.
17. Keine künstlichen Alternate Keys.
18. Keine Übernahme der BusinessPartner- oder CatalogItem-Domäne.
19. Generated Code wird gegen mindestens eine zweite abweichende Struktur neutralitätsgeprüft.
20. Controller, Mapper und Persistence enthalten keine versteckte Autorisierungslogik.

## 8. Patchprozess

### 8.1 Grundregeln

- Alle Änderungen erfolgen ausschließlich über das Patchsystem.
- Keine direkte Dateiänderung im Live-Projekt.
- Kein `sed`, `cat >`, Editor- oder Kopier-Workaround im Zielrepository.
- Kein Apply ohne vollständigen Producer Artifact Preflight.
- Kein Reapply nach einem späten Fehler.
- Jeder Patch verwendet den kleinstmöglichen korrekten Scope.
- `root` ist nur bei unvermeidbaren Querschnittsänderungen zulässig.
- Dokumentation, Tooling, Kernel und Fachcode werden nicht in einem Patch vermischt.

### 8.2 Patchartefakte

Pro Patch werden mindestens geliefert:

```text
<patch-id>.zip
run_<patch-id>.sh
```

Für beide Artefakte werden SHA-256-Werte angegeben.

Das ZIP enthält ausschließlich:

```text
manifest.json
files/**
delete/**
logs/CHANGELOG-*.md
```

`manifest.id`, `manifest.patchId`, Archivname und erwartete Patch-ID des Runners müssen exakt übereinstimmen.

### 8.3 Baseline-Vertrag

`manifest.baseline.expectedBeforeSha256` ist für jede Operation vollständig:

- existierende Datei: SHA-256 der echten Repositorybytes;
- neue Datei: `null`;
- gelöschte Datei: SHA-256 der echten Repositorybytes;
- keine Hash-Einträge ohne Operation.

Ein Full-Textexport ist keine Bytequelle. Autoritativ sind echte Live-Bytes oder `fileManifest` eines integren v2-Exports.

### 8.4 Producer Artifact Preflight

Vor Auslieferung muss mindestens grün sein:

```text
ZIP-Integrität
Manifest-Identität
Scope
vollständige Live-Baseline-Hashes
Payload-Hygiene
exakt eine finale LF-Zeile
kein Trailing Whitespace
Git-Mode-Vertrag
isolierter Dry-run
isolierter Apply
Payload-Byte-Parität
Changed-Path-Parität
git diff --check
targeted Gates
Full-Export-Integrität
```

Nur ein Bericht mit `ARTIFACT_PREFLIGHT=PASS` qualifiziert das Patchartefakt. Hosttests und echter Live-Apply bleiben zusätzliche Gates.

### 8.5 Runner-Vertrag

Der Runner verwendet intern:

```bash
set -euo pipefail
set +H
```

Er schreibt mindestens:

```text
patches/logs/validation/<patch-id>/STATUS.txt
patches/logs/validation/<patch-id>/SUMMARY.txt
patches/logs/validation/<patch-id>/EXIT_CODE.txt
patches/logs/validation/<patch-id>/FAILED_STAGE.txt
patches/logs/validation/<patch-id>/RUN_PID.txt
patches/logs/validation/<patch-id>/run.log
```

Der Runner:

- erzeugt kurze Konsolenausgaben;
- schreibt Detailausgaben in Logs;
- prüft Git, Patch-ID, Scope und SHA-256 vor Apply;
- nutzt `patch.sh accept` mit passendem Profil;
- erzeugt genau einen finalen Full-Export;
- prüft `show latest` gegen die erwartete Patch-ID;
- stoppt bei Fehlern vor Apply ohne Mutation;
- startet bei Fehlern nach Apply keine automatische Reapply-Schleife.

### 8.6 Testpflichten

#### Documentation-only

- kein Maven-Test;
- kein Build;
- Artifact Preflight;
- Scope- und Payloadprüfung;
- Dokumentationsvertrag;
- `git diff --check`;
- genau ein Full-Export;
- Exportintegrität.

#### Tooling, Kernel oder Fachcode

- direkte Tool-/Contract-Gates;
- targeted Tests;
- relevante Regressionstests;
- vollständiger Maven-Test für Tooling-, Kernel- und Fachcode-Patches;
- DB-, API-, OpenAPI- und Security-Gates nach Scope;
- `git diff --check`;
- genau ein Full-Export;
- Exportintegrität.

## 9. Terminalschonende Bedienung

Konkrete Lieferungen enthalten vollständig eingesetzte Dateinamen und Hashwerte. Es bleiben keine Platzhalter im Benutzerkommando.

Bevorzugtes Muster:

```text
kurzer Runner-Start
Statusdateien im Projekt
keine ungefilterten Maven-/Runner-Logs
kurzer Statusabruf
```

Lange inline Apply-/Verify-Blöcke sind nicht zulässig. Ein Runner darf über `nohup` gestartet werden, sofern er den Prozessstatus und alle Abschlussdateien zuverlässig schreibt.

## 10. Fehlerbehandlung

### Fehler vor Apply

- keine Mutation;
- kein Reapply;
- Ursache vollständig analysieren;
- alte Artefaktvariante sperren;
- korrigierte Variante mit neuer Artefaktidentität;
- vollständige Neuqualifizierung.

### Fehler nach Apply

- kein erneuter Apply;
- Working Tree, Latest Patch und Patchstatus erfassen;
- fehlgeschlagene Stufe analysieren;
- Resume oder Repair nur bei eindeutiger Ursache;
- kein Commit und kein Push vor grüner Closure.

Ein lokal simulierter Erfolg ersetzt keinen echten Hosttest. Hostunterschiede wie Git-Modi, `umask`, `.env`, Java-/Maven-Versionen, Dateisystemrechte, Symlinks und Exportprofile werden in der Vorprüfung berücksichtigt.

## 11. Commit- und Push-Freigabe

Commit und Push sind nur zulässig bei:

```text
STATUS=DONE
EXIT_CODE=0
PROCESS=FINISHED
FAILED_STAGE leer
Latest Patch korrekt
alle Pflichtgates grün
Full-Export vorhanden
Exportintegrität grün
Changed Paths exakt
```

Der Commit enthält ausschließlich die expliziten Patchpfade. `git add .`, `git add -A` und pauschale Commits sind unzulässig. Push erfolgt nur nach ausdrücklicher Freigabe oder über einen ausdrücklich beauftragten `--push`-Lauf.

## 12. Sprint-1-Definition-of-Done

Sprint 1 ist vollständig abgeschlossen, wenn alle folgenden Punkte nachgewiesen sind.

### DoD A: Plattformbasis

```text
Springmaster Delivery-Vertrag ist geschlossen.
ZBM Tooling entspricht dem freigegebenen Springmaster-Stand.
ZBM System-Kernel entspricht dem freigegebenen Springmaster-Stand.
Tooling- und Kernel-Selfchecks sind grün.
Full Maven ist grün.
Export v2, Raw-Byte-Manifest und Closure-Evidence sind integer.
```

### DoD B: Fachliche Readiness

```text
Pilotaggregat ist fachlich begründet.
Invarianten und Statusübergänge sind korrekt.
Persistence und Liquibase sind real lauffähig.
Bean Validation besitzt einen realen Provider.
Security und Permissions sind entschieden und getestet.
Target Bindings sind vollständig.
Kollisionen und Migrationen sind klassifiziert.
Es bestehen keine offenen P0-Blocker.
```

### DoD C: Sandbox-Pilot

```text
Spec → IR → Blueprint → Renderer → Patch ist deterministisch.
Producer Artifact Preflight ist grün.
ZBM-Live-Dry-run ist grün.
Isolierter Apply ist grün.
Targeted Tests sind grün.
Full Maven ist grün.
API-, OpenAPI-, Persistence-, Validation- und Security-Gates sind grün.
Ein integerer finaler ZBM-Full-v2-Export liegt vor.
```

### DoD D: Operative Pilotdelivery

```text
Der Benutzer hat den Live-Apply ausdrücklich freigegeben.
Live-Apply ist erfolgreich.
Der Working Tree enthält exakt den Patchumfang.
Commit und Push sind erfolgreich.
Latest Patch ist korrekt.
Der Abschlussbericht enthält keine spekulativen Folgepatches.
```

## 13. Sprint-Nicht-Ziele

Sprint 1 umfasst nicht automatisch:

- vollständige Umsetzung aller ZBM-Aggregate;
- produktive Abrechnung und externe Exporte;
- fachlich ungeklärte CRUD-Endpunkte;
- Einführung künstlicher Business Keys;
- ungeprüfte Übernahme aller Springmaster-Defaults;
- ZBM-Sonderlogik im Springmaster-Generator;
- Live-Apply eines generierten Fachpatches ohne Sandbox-Closure;
- zusätzliche Optimierungen nach Erreichen der Sprint-1-DoD.

## 14. Verbindliche nächste Aktion

Nach Persistierung dieses Plans beginnt die technische Umsetzung mit einem Springmaster-Patch zur Schließung des Platform-Update- und Tooling-Delivery-Vertrags.

Sein alleiniger Zweck ist:

> Springmaster muss ein dependency-vollständiges, baseline-gebundenes und vom aktuellen Artifact Preflight akzeptiertes Tooling-Patchartefakt für ZBM erzeugen können.

Ein ZBM-Tooling-Patch ist erst nach grüner Springmaster-Delivery-Closure zulässig.

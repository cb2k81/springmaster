# Springmaster – Umsetzungsplan

## 1. Zweck

Dieser Plan steuert die schrittweise Umsetzung des Masterkonzepts. Jeder Schritt muss ein prüfbares Ergebnis liefern und durch passende Kommandos validiert werden.

## 2. Aktueller Stand nach Bootstrap

Nach Patch `000001` ist vorhanden:

* minimales Maven-/Spring-Boot-Projekt
* Basis-Tooling für Patch, Export, Build und DBTool-Status
* initiale Projekt- und Dokumentationsstruktur
* leeres Liquibase-Master-Changelog
* erfolgreiche Basisprüfung per `mvn test`

Nach Patch `000002` ist zusätzlich vorhanden:

* deklarativer Templatebereich für künftige Projektanlage
* Ergänzung des Masterkonzepts zum Project Skeleton
* dieser Umsetzungsplan

Nach Patch `000003` ist zusätzlich vorhanden:

* generalisierte Tooling-Baseline aus dem IDM-Referenzstand
* erweiterte Exportprofile und Split-Exports
* erweitertes Patch-Scope-Modell für Template-, Planungs- und Plattform-Update-Patches
* modulares DBTool-Fundament
* Tooling-Selfcheck

Nach Patch `000004` ist zusätzlich vorhanden:

* bereinigte Export-/Git-Hygiene für Python-Cache- und lokale Tool-Cache-Artefakte
* dokumentierter Standardabschluss mit Full-ZIP- und Full-Parts-Baseline-Export

Nach Patch `000005` ist zusätzlich vorhanden:

* `bin/project-new.sh` als konservatives Projektanlage-Tool
* operationalisierter Project-Skeleton-Generator mit Dry-run
* Bootstrap-Nachweis im erzeugten Zielprojekt

Nach Patch `000006` ist zusätzlich vorhanden:

* IDM-System-Core-Dateien sind klassifiziert
* Core-Migrationsregeln sind dokumentiert
* noch kein Java-Core-Code ist migriert

Nach Patch `000007` ist zusätzlich vorhanden:

* Core-Namespace-Strategie ist verbindlich geklärt
* wiederverwendbarer Core verwendet künftig `de.cocondo.system`
* Springmaster-App und Demo bleiben unter `de.cocondo.platform.*`

Nach Patch `000008` ist zusätzlich vorhanden:

* Patch-Validierung ist nach Patch-Kategorie geregelt
* Documentation-only-Patches verzichten grundsätzlich auf Build und Maven-Test
* Code-, Test- und Build-Konfigurationspatches behalten verbindliche Testpflicht

Nach Patch `000009` ist zusätzlich vorhanden:

* technischer Patch-Scope `core` ist auf `de.cocondo.system` ausgerichtet
* Exportprofil `core` verwendet denselben kanonischen Core-Pfad
* der erste Core-Code-Slice kann ohne Package-Abweichung vorbereitet werden

Nach Patch `000010` ist zusätzlich vorhanden:

* erster fachfreier Core-Code-Slice unter `de.cocondo.system`
* DTO-/Entity-Marker, Validierungsbasis, Basisausnahme und ID-Generator-Contract
* Unit-Tests für die neuen Core-Basistypen

Nach Patch `000011` ist zusätzlich vorhanden:

* Springmaster scannt `de.cocondo.platform` und `de.cocondo.system`
* das Project Skeleton erzeugt neue Apps mit Scan-Ausrichtung auf App-Basispackage und `de.cocondo.system`
* spätere Spring-Komponenten im Core sind damit scanfähig

Nach Patch `000012` ist zusätzlich vorhanden:

* Jakarta-Persistence-API ist als minimale Compile-Dependency für persistenznahe Core-Typen vorbereitet
* der Core-Scope darf bei begründeten Core-Dependency-Änderungen `pom.xml` enthalten
* die nächste Persistenz-Code-Übernahme ist dependency-seitig entkoppelt vorbereitet

## 3. Leitregeln

* Ein Schritt entspricht idealerweise genau einem Patch.
* Jeder Patch enthält einen begrenzten Scope.
* Jeder Patch muss mit Dry-run angewendet werden können.
* Documentation-only-Patches führen grundsätzlich keinen Build und keinen Maven-Test aus.
* Java-Code-, Test- und Build-Konfigurationspatches benötigen verbindlich `mvn test`.
* Tooling-Änderungen benötigen Shell-/Python-Syntaxprüfung und Tooling-Selfcheck; `mvn test` nur bei Build-/Projektstrukturwirkung.
* DBTool-Änderungen benötigen mindestens `./bin/dbtool.sh env` und `./bin/dbtool.sh status`.
* Exportänderungen benötigen mindestens `./bin/export.sh full --zip`.
* Core-Änderungen benötigen konkrete Tests und mindestens eine Demo-Nutzung.
* Demo-Code wird nicht in Zielprojekte übertragen.

## 4. Phasenplan

### Phase 1 – Foundation und Template-Basis

Ziel: Projektfundament und kanonisches Project Skeleton herstellen.

| Patch | Scope | Ergebnis | Pflichtprüfung |
|---|---|---|---|
| 000001 | Bootstrap | Projekt ist lauffähig und patchfähig | `mvn test`, `./bin/export.sh full --zip`, `./bin/dbtool.sh status` |
| 000002 | Docs/Templates | Templatebereich und Umsetzungsplan sind angelegt | `./bin/patch.sh show latest`, `./bin/export.sh full --zip` |

Abschlusskriterium:

* Masterkonzept benennt das Project Skeleton.
* Templatebereich ist versioniert vorhanden.
* Folgeumsetzung ist geplant.

### Phase 2 – Tooling-Baseline aus IDM generalisieren

Ziel: Export-, Build-, Patch- und DBTool aus dem IDM-Referenzstand kontrolliert auf `springmaster` übertragen und generalisieren.

Umgesetzte Schritte:

1. Exporttool vollständig generalisiert.
2. Patchsystem-Scope-Modell für `springmaster` vervollständigt.
3. Buildtool lokal-first stabilisiert.
4. DBTool von Bootstrap-Status zu Liquibase-/MariaDB-Steuerung vorbereitet.
5. `.idea/**` aus Git/Export ausgeschlossen.

Zusätzlicher Hygiene-Schritt:

6. Python-Cache-Artefakte und lokale Tool-Caches aus Git/Export ausschließen.

Pflichtprüfungen:

```bash
bash -n ./bin/*.sh
python3 -m py_compile ./bin/patch.py
./bin/patch.sh list
./bin/export.sh full --zip
./bin/dbtool.sh env
./bin/dbtool.sh status
mvn test
```

### Phase 3 – Project-New-Tooling

Ziel: Neue Projekte deterministisch aus dem Project Skeleton erzeugen.

Umgesetzter Foundation-Schritt:

1. Tokenmodell operationalisiert.
2. `bin/project-new.sh` als trockenlauf- und validierungsfähiges Tool angelegt.
3. Template-Manifest auf Project-New-Foundation aktualisiert.
4. Bootstrap-Nachweis im erzeugten Zielprojekt definiert.

Noch nicht Bestandteil der Foundation:

* keine Zielprojekt-Registry-Aktualisierung
* keine automatische Platform-Update-Anbindung
* keine Core- oder Demo-Übertragung

Pflichtprüfungen:

```bash
./bin/project-new.sh --help
rm -rf /tmp/springmaster-sample
./bin/project-new.sh create --dry-run --name sample --path /tmp/springmaster-sample
./bin/project-new.sh create --name sample --path /tmp/springmaster-sample
(cd /tmp/springmaster-sample && ./bin/patch.sh list && ./bin/export.sh full --zip && ./bin/export.sh --full-parts baseline --zip && ./bin/dbtool.sh status && mvn test)
```

### Phase 4 – Platform Core Baseline

Ziel: Wiederverwendbare Java-Core-Bausteine aus dem IDM-Referenzstand fachfrei und paketkonform nach `de.cocondo.system` überführen.

Umgesetzter Vorbereitungsschritt:

1. IDM-System-Core-Dateien klassifiziert.
2. ursprüngliche Zielpfadregel aus `000006` erkannt und vor Code-Migration korrigiert.
3. Core-Namespace-Strategie `de.cocondo.app.system` -> `de.cocondo.system` verbindlich dokumentiert.
4. Dependency-Bänder für Basic Core, Persistence, Web, Event und Security abgegrenzt.
5. Migrationsregeln dokumentiert.
6. Patchsystem- und Export-Core-Scope auf `src/main/java/de/cocondo/system/**` und `src/test/java/de/cocondo/system/**` ausgerichtet.

Geplante nächste Schritte:

1. Persistenznahen Core-Slice mit JPA-API, aber ohne Repository-/Runtime-Aktivierung übernehmen.
2. Listener- und Basistyp-Verhalten mit direkten Unit-Tests prüfen.
3. Key-Value-Metadata, Repositories und Demo-Domäne weiterhin getrennt behandeln.
4. Erst bei echter Repository-Nutzung Spring Data JPA und DB-Validierung aktivieren.
5. Demo-Nutzung definieren oder vorbereiten.

Pflichtprüfungen:

```bash
mvn test
./bin/export.sh full --zip
```

Zusätzlich je Core-Baustein:

* Testklasse vorhanden
* keine Imports aus `de.cocondo.app.domain.idm`
* keine Core-Pakete unter `de.cocondo.platform.core`
* keine IDM-Ressourcenabhängigkeit

### Phase 5 – Demo Catalog Foundation

Ziel: `Catalog-demo` als prüfbare Referenzimplementierung auf Basis des Core und der Springmaster-Standards aufbauen.

Readiness-Regel seit `000056_springmaster_catalog_demo_readiness_plan`:

* Catalog-demo wird nicht durch Kompilierbarkeit kanonisch.
* Der erste `CatalogItem`-Slice muss die Standards für Endpoints, DTOs, Validation, Error Contract, Controller/Service/Transaction, Persistence, Security-Klassifikation, Mapping und Gates nachweisbar erfüllen oder explizit deferred markieren.
* Bestehende Zielprojekte bleiben bis zur Catalog-demo-Beweisführung Vergleichsinputs und werden nicht beliefert.

Geplante Schritte:

1. CatalogItem-Code-Slice anhand des Readiness-Plans konkret schneiden.
2. DTO-, Mapper-, Service- und Controller-Struktur gegen die Standards ausrichten.
3. Positive und negative MockMvc-Tests für create, detail, paged list, validation, not-found und conflict ergänzen.
4. Update und bodyless delete ergänzen, bevor der Slice kanonisch wird.
5. OpenAPI-Contract-Gate oder mindestens OpenAPI-Readiness-Nachweis vorbereiten.
6. Security-Klassifikation dokumentieren oder bewusst als `documented-deferred-security` markieren.
7. Persistenz und Liquibase erst in einem dedizierten Slice aktivieren, sofern die Persistence-Readiness erfüllt wird.

Pflichtprüfungen für Code-/Test-Patches:

```bash
mvn test
./bin/export.sh full --zip
./bin/export.sh full --zip
```

### Phase 6 – Target Update Foundation

Ziel: Zielprojekt-Registry und Update-Patch-Erzeugung schrittweise operationalisieren.

Geplante Schritte:

1. Registry-Dateien verifizieren.
2. Zielprojekt-Mapping-Regeln definieren.
3. Update-Patch-Manifest spezifizieren.
4. Tooling-Update für ein Zielprojekt im Dry-run erzeugen.
5. Konflikt- und Versionsprüfung einbauen.

Pflichtprüfungen:

```bash
./bin/platform-update.sh --help
./bin/platform-update.sh create --dry-run --target idm --scope tooling
```

## 5. Standard-Kommandos nach Patch-Typ

Die vollständige Regel ist in `PROJECT_DOCS/TOOLING/PATCH_VALIDATION_POLICY.md` dokumentiert.

### Documentation-only

```bash
cd /opt/cocondo/springmaster
./bin/patch.sh show latest
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
ls -1t exports/text/*.zip | head -n 2
```

Für Documentation-only-Patches werden `mvn test` und `./bin/build.sh` grundsätzlich nicht ausgeführt.

### Code-, Test- oder Build-Konfigurationspatches

```bash
cd /opt/cocondo/springmaster
./bin/patch.sh show latest
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
ls -1t exports/text/*.zip | head -n 2
```

### Tooling-Patches

```bash
cd /opt/cocondo/springmaster
./bin/patch.sh show latest
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
ls -1t exports/text/*.zip | head -n 2
```

Bei Tooling-Patches wird `mvn test` nur ergänzt, wenn der Patch Build-Konfiguration, Projektstruktur, Java-Code oder Template-Erzeugung mit Java-Projektwirkung betrifft.

## 6. Abbruchkriterien

Ein Schritt wird abgebrochen, wenn:

* eine erforderliche Baseline-Datei fehlt
* ein Patch-Scope nicht passt
* ein Dry-run fehlschlägt
* eine für die Patch-Kategorie verpflichtende Prüfung fehlschlägt
* `mvn test` bei Code-, Test- oder Build-Konfigurationspatches fehlschlägt
* ein Tooling-Test bei Tooling-Patches fehlschlägt
* eine Datei außerhalb des geplanten Scopes geändert werden müsste
* IDM-Fachcode unkontrolliert in Core oder Template übernommen würde

## 7. Aktueller Stand nach 000012

Nach Patch `000012_springmaster_core_persistence_dependency_preparation` ist folgender Foundation-Stand erreicht:

* Bootstrap, Patchsystem, Exporttool, DBTool-Basis und Buildtool sind vorhanden.
* Project-New erzeugt ein Maven-testbares Minimalprojekt aus dem Skeleton.
* Der Core-Namespace ist auf `de.cocondo.system` festgelegt und technisch im Patch-/Export-Scope verankert.
* Der erste fachfreie Core-Code-Slice ist umgesetzt und getestet.
* Springmaster und Project Skeleton scannen `de.cocondo.system`.
* Die minimale Jakarta-Persistence-API-Abhängigkeit ist vorbereitet.
* Die Validierungsregel unterscheidet Documentation-only-, Tooling-, Code-, Build- und DB-Patches.

Offen bleiben:

* Demo-Domäne mit realer Core-Nutzung
* operativer Target-Update-Generator
* reale DBTool-/Liquibase-Validierung gegen MariaDB
* OpenAPI-/SBOM-/Runtime-ZIP-Endvalidierung
* dedizierte Rollback-Archiv-Sicherung

## 8. Stand Review und Versionierung

Patch `000013_springmaster_project_state_review_and_version_policy` hält den erreichten Foundation-Stand fest.

Er ergänzt:

* `PROJECT_DOCS/PLANNING/PROJECT_STATE_REVIEW_000012.md`
* `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`
* `PROJECT_DOCS/CONCEPT/PATCH_ARCHIVE_AND_ROLLBACK_POLICY.md`
* aktualisierte Versionen in `platform/versions/platform.env`

Der Stand nach `000013` ist der erste versionierte Foundation-Milestone:

```text
PLATFORM_VERSION=0.2.0-foundation
PLATFORM_CORE_VERSION=0.1.0
PLATFORM_TOOLING_VERSION=0.2.0
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.0.0
PLATFORM_UPDATE_VERSION=0.0.0
```

## 9. Nächster geplanter Umsetzungsschritt

Nach `000013` wurde vor dem nächsten Core-Code-Slice eine Scope-Lücke festgestellt:

* Die Version Policy verlangt, dass Core-Code- und Core-API-Erweiterungen die Versionsdatei aktualisieren.
* Der bisherige Scope `core` erlaubte jedoch `platform/versions/platform.env` nicht.

Daher folgt zunächst ein Tooling-/Policy-Ausrichtungsschritt:

```text
000014_springmaster_core_version_scope_alignment.zip
```

Ziel von `000014`:

* Core-Scope um `platform/versions/platform.env` erweitern
* Version Policy und Patch-Dokumentation synchronisieren
* Tooling-Version auf `0.2.1` erhöhen
* keinen Java-Code ändern
* keinen Maven-Test ausführen

Danach folgt als nächster Code-Schritt:

```text
000015_springmaster_core_persistence_basic_types.zip
```

Ziel von `000015`:

* erster JPA-naher, aber fachfreier Core-Code-Slice
* atomare Core-Versionserhöhung im selben Patch
* keine Repository-Schicht
* keine DataSource-Konfiguration
* keine Liquibase-Änderung
* keine Spring-Data-JPA-Runtime-Aktivierung

Pflichtvalidierung für `000015`:

```bash
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
ls -1t exports/text/*.zip | head -n 2
```

## 10. Demo-Anschluss als Qualitätsgrenze

Weitere Core-Slices dürfen nicht dauerhaft ohne Demo-Nutzung wachsen.

Spätestens nach dem ersten persistenznahen Core-Code-Slice muss entweder:

1. eine minimale Demo-Domäne folgen, oder
2. ein konkreter Demo-Anschluss im nächsten Patch geplant und dokumentiert werden.

Der Core bleibt nur dann qualitativ tragfähig, wenn die Bausteine nicht ausschließlich abstrakt und isoliert getestet werden.

## 11. Stand nach 000015 und nächster Schritt

Patch `000015_springmaster_core_persistence_basic_types` wurde als Core-Code-Patch abgeschlossen. Der Stand ist:

```text
PLATFORM_VERSION=0.3.0-foundation
PLATFORM_CORE_VERSION=0.2.0
PLATFORM_STATE_PATCH=000015_springmaster_core_persistence_basic_types
```

Die Pflichtvalidierung für Code-Patches wurde erfüllt. Der nächste Qualitätsengpass ist nun nicht ein weiterer abstrakter Core-Slice, sondern der Demo-Anschluss.

Vor dem ersten Demo-Code-Patch wird ein Scope-/Policy-Schritt benötigt, damit Demo-Code und Demo-Versionserhöhung atomar geliefert werden können:

```text
000016_springmaster_demo_version_scope_alignment.zip
```

Ziel von `000016`:

* Demo-Scope um `platform/versions/platform.env` erweitern
* Version Policy und Patch-Dokumentation synchronisieren
* regulären Kommandoabschluss auf Full-ZIP-Export begrenzen
* Tooling-Version auf `0.2.2` erhöhen
* keinen Java-Code ändern
* keinen Maven-Test ausführen

Danach folgt als nächster Code-Schritt:

```text
000017_springmaster_demo_catalog_basic_domain.zip
```

Ziel von `000017`:

* erste minimale Demo-Domäne unter `de.cocondo.platform.demo.catalog`
* Nutzung vorhandener Core-Basistypen aus `de.cocondo.system`
* kein Spring-Data-JPA und keine reale Datenbankpflicht
* verifizierende Tests und `mvn test` als Pflichtprüfung


## Stand nach Patch 000022

Patch `000022_springmaster_patch_accept_verify_workflow` führt den standardisierten Patch-Abnahme-Workflow ein.

Vorherige lange Kommando-Stacks werden ersetzt durch:

```bash
./bin/patch.sh accept <patch.zip> --full-test --export
./bin/patch.sh verify latest --full-test --export
```

Damit ist das Patchsystem nicht nur für Apply/Rollback, sondern auch für die ausgabearme und nachvollziehbare Abnahme zuständig.

## Nächster geplanter Schritt

```text
000023_springmaster_patch_accept_workflow_hardening.zip
```

Ziel: Nach erster praktischer Nutzung von `accept`/`verify` werden Summary-Qualität, Logumfang und automatische Validierungsprofile weiter geschärft. Fachliche Demo- oder Core-Erweiterungen werden erst danach fortgesetzt, damit die tägliche Patch-Abnahme stabil bleibt.


## Stand nach Patch 000023

Patch `000023_springmaster_patch_accept_workflow_hardening` härtet die in `000022` eingeführte Abnahme ab.

Der neue Standard lautet:

```bash
./bin/patch.sh accept <patch.zip>
./bin/patch.sh verify latest
```

Das Patchsystem entscheidet im Profil `auto` anhand der Zielpfade, ob ein vollständiger Maven-Test erforderlich ist. Außerdem erzeugt der Tooling-Selfcheck nur noch einen Full-ZIP-Export, um unnötige Exportdaten zu vermeiden.

## Nächster geplanter Schritt nach 000023

```text
000025_springmaster_platform_update_foundation.zip
```

Ziel: Nach Stabilisierung des Abnahme-Workflows beginnt die Operationalisierung der Zielprojekt-Update-Mechanik. Dabei wird zunächst ein konservativer Dry-run-/Planungsmodus vorbereitet, bevor echte Updates auf Zielprojekte angewendet werden.

## Stand nach Patch 000024

Patch `000024_springmaster_patch_accept_export_hygiene` wird als kurzfristiger Tooling-Hygiene-Schritt vor die Platform-Update-Foundation gezogen.

Begründung:

* Die praktische Nutzung von `accept` zeigte, dass der Workflow durch `tooling-selfcheck.sh` und den abschließenden Export sonst unnötig mehrere Full-ZIP-Exporte erzeugen kann.
* Der Standardbefehl bleibt einzeilig.
* Die eigentliche Zielprojekt-Update-Mechanik folgt danach als nächster fachlicher Tooling-Schritt.

Nächster geplanter Schritt:

```text
000025_springmaster_platform_update_foundation.zip
```

## Stand nach Patch 000025

Patch `000025_springmaster_platform_update_foundation` führt die erste operative, aber nicht-invasive Platform-Update-Grundlage ein.

Erreicht:

* `bin/platform-update.sh` ist kein Placeholder mehr.
* Zielprojekt-Deskriptoren können gelistet, angezeigt und syntaktisch validiert werden.
* Für Zielprojekte können Planartefakte unter `platform/update/manifests/**` erzeugt werden.
* Zielprojekte werden dabei nicht verändert.
* Der `platform-update`-Scope ist für atomare Versionierungsänderungen vorbereitet.

Nächster geplanter Schritt:

```text
000026_springmaster_platform_update_patch_generation_plan.zip
```

Ziel: Auf Basis der Planungsgrundlage wird die Erzeugung von Zielprojekt-Patch-ZIPs vorbereitet. Auch dieser Schritt bleibt zunächst Dry-run-/Plan-orientiert und darf Zielprojekte nicht automatisch verändern.


## Stand nach Patch 000026

Patch `000026_springmaster_platform_update_patch_generation_plan` erweitert die Platform-Update-Mechanik um eine erste target-lokale Patch-ZIP-Erzeugung.

Erreicht:

* `platform-update generate` erzeugt Plan-Patch-ZIPs unter `platform/update/generated/**`.
* `--dry-run` zeigt die geplante ZIP- und Payload-Struktur ohne Dateiänderung.
* Das erzeugte ZIP nutzt das bestehende Patchformat (`manifest.json`, `files/**`, `logs/CHANGELOG-*.md`).
* Zielprojekte werden weiterhin nicht verändert.

Nächster geplanter Schritt:

```text
000027_springmaster_platform_update_core_payload_mapping.zip
```

Ziel: Für das Profil `core` wird die spätere Übertragung von `de.cocondo.system` vorbereitet. Auch dieser Schritt soll zunächst deterministisch planen und validieren, bevor Zielprojekte automatisch verändert werden.

## Stand nach 000029 – No-op-Guard nachgezogen

Patch `000029_springmaster_patch_accept_noop_guard_and_state_alignment` zieht den No-op-Schutz im Accept-Workflow nach und korrigiert die Zustandsdokumentation nach der tatsächlichen Anwendung des Platform-Update-Core-Payload-Mappings als `000028`.

Nächster geplanter Exkurs:

```text
000030_springmaster_patch_project_local_scope_env.zip
```

Ziel: projektspezifische zusätzliche Patch-Scopes und Pfade werden nicht zentral in Springmaster hart kodiert, sondern aus der `.env` des jeweiligen Projekts ergänzt.


## Stand nach Patch 000031

Patch `000031_springmaster_platform_update_target_patch_apply_plan` ergänzt die Platform-Update-Mechanik um einen nicht-invasiven Apply-Plan für generierte Zielpatches.

Erreicht:

* `platform-update apply-plan` erzeugt Markdown-Plan und Shell-Skript unter `platform/update/manifests/**`.
* Das Zielprojekt wird bei der Planerzeugung nicht verändert.
* Die Anwendung eines generierten Zielpatches bleibt ein bewusster manueller Schritt im Zielprojekt.
* Die Dokumentation zum Platform-Update-Workflow wurde um die Apply-Plan-Phase erweitert.

Nächster geplanter Schritt:

```text
000032_springmaster_platform_update_target_scope_preflight.zip
```

Ziel: Vor dem manuellen Anwenden eines generierten Zielpatches soll geprüft werden können, ob das Zielprojekt den benötigten Patch-Scope unterstützt oder ob zunächst ein Tooling-/Scope-Update erforderlich ist.


## Stand nach Patch 000033

Patch `000033_springmaster_platform_update_target_compatibility_plan` ergänzt die Platform-Update-Mechanik um einen Target-Compatibility-Plan.

Auslöser war der Preflight-Befund im Zielprojekt `idm`:

```text
Unbekannter Patch-Scope im manifest.json: core
```

Der neue Schritt erzeugt ein Kompatibilitäts-ZIP und ein reviewbares Skript, verändert das Zielprojekt aber nicht automatisch. Projektspezifische zusätzliche Scopes und Pfade bleiben in der jeweiligen Zielprojekt-`.env`.

Nächster geplanter Schritt:

```text
000034_springmaster_platform_update_target_compatibility_apply_review.zip
```


## Stand nach Patch 000057

Patch `000057_springmaster_standard_consistency_and_adr_gap_review` ergänzt eine forensische Konsistenzprüfung der Standards und eine ADR-Gap-Analyse vor dem ersten Gate-Tooling-Seed.

Erreicht:

* Die Standards aus `000044` bis `000056` wurden als zusammenhängender Regelbestand bewertet.
* Blockierende Inkonsistenzen vor Gate-Tooling wurden dokumentiert, insbesondere `sort` versus `sortBy` und `/all` versus `/options`/`/reference-data`.
* ADR-Lücken wurden in `PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md` erfasst.
* Interface- und Test-Utility-Kandidaten wurden als spätere Prüfbarkeitsbausteine dokumentiert.
* Catalog-demo bleibt Ziel der Referenzimplementierung, darf aber erst nach Gap-Schließung oder expliziter Ausnahme kanonisch werden.

Nächster geplanter Schritt:

```text
000058_springmaster_api_query_reference_data_consistency_standard.zip
```

Ziel: Harmonisierung der P0-API-Lücken, insbesondere `sortBy` als finaler Query-Parameter-Kandidat sowie die Abgrenzung von `/all`, `/options` und `/reference-data`, bevor Gate-Tooling implementiert wird.


## 000058 query/reference-data consistency

`000058_springmaster_api_query_reference_data_consistency_standard` resolves the first P0 gap from the 000057 review. The API contract gate tooling seed may now assume `sortBy`/`sortDir` as canonical, `/options` as selector vocabulary, `/reference-data` as ADR-backed bounded reference data and `/all` as non-canonical for new reference APIs.


## Gap work update since 000059

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` resolves the error identity and first-slice status-code gap identified by 000057.

The next gap work should continue with ADR governance/backlog alignment, OpenAPI naming/schema standardization and test/gate execution strategy before API contract gate tooling is implemented.


## Gap work update since 000060

Patch `000060_springmaster_adr_governance_and_backlog_alignment` aligns ADR governance and the ADR backlog before strict API contract gate tooling is implemented.

Erreicht:

* ADR status model, numbering rules, template requirements and standards-to-ADR mapping are documented.
* `ADR_GAP_BACKLOG.md` now distinguishes planning status, priority and tooling blocker class.
* ADR-0002, ADR-0006, ADR-0003, ADR-0004 and ADR-0007 are accepted through patches 000061 through 000065.
* Strict gate tooling must wait for accepted ADRs when the rule is architectural and ADR-required.
* Report-only gate tooling remains allowed when the output is non-binding and clearly labeled.

Nächste Gap-Arbeit:

```text
000061_springmaster_adr_0002_api_boundary_and_endpoint_contract
```

Ziel: API-Boundary, Endpoint-Kontrakte, DTO-/Validation-Boundary, Error Contract, Query-/Reference-Data-Entscheidungen und Statuscode-/Command-Result-Regeln als erste accepted ADR konsolidieren.



## Stand nach Patch 000061

Patch `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepts ADR-0002 as the first P0 architecture decision after the ADR governance alignment.

Erreicht:

* API boundary and endpoint contract decisions are now ADR-backed.
* Endpoint vocabulary, DTO/validation boundary, query/reference-data semantics, error contract, command semantics and first-slice status-code defaults are consolidated in one accepted ADR.
* Existing target projects remain comparison inputs only.
* Strict gate execution still waits for ADR-0006 and concrete gate implementation evidence.

Nächster geplanter Schritt:

`000062_springmaster_adr_0006_verification_and_gate_strategy` - accepted by patch 000062



## Stand nach Patch 000062

Patch `000062_springmaster_adr_0006_verification_and_gate_strategy` accepts ADR-0006.

Erreicht:

* Gate layers G0 through G6 are decision-backed.
* Report-only, strict and manual-review execution modes are defined.
* Finding severity vocabulary is defined.
* Future Maven profiles are named: `springmaster-gates-report`, `springmaster-gates-strict` and `springmaster-gates-target-compare`.
* Compact report structure under `target/springmaster-gates/<gate-run-id>/` is defined.
* First API contract gate tooling is allowed as report-only diagnostics.
* Strict gates require explicit strict-readiness and implementation evidence.
* Target-project comparison remains read-only and non-destructive.

Nächster geplanter Schritt:

`000063_springmaster_adr_0003_application_layer_transaction_boundary` - accepted by patch 000063

## Stand nach Patch 000063

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts ADR-0003.

Erreicht:

* Controller are fixed as thin HTTP boundary adapters.
* Repository and `EntityManager` access from controllers is rejected for new reference APIs.
* Transaction ownership belongs to service, query-service, command-service or use-case boundaries.
* Query service, command service, resource service and use-case handler selection is now an accepted architecture decision.
* Mapper-boundary and security-placement relationships are documented without replacing ADR-0004 or ADR-0005.
* Report-only Java boundary diagnostics may now use ADR-0003 as rule source.

Nächster geplanter Schritt:

`000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` - accepted by patch 000064




## Stand nach Patch 000064

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts ADR-0004.

Erreicht:

* Persistence identity and public API identity defaults are accepted.
* `DomainEntity` remains the mapped-superclass default for standard aggregate roots.
* Business keys are explicit domain fields, not implicit technical IDs.
* Internal surrogate IDs require explicit documented criteria and must not leak into normal public API contracts.
* `persistenceVersion`, audit fields and repository boundary are decision-backed.
* Report-only persistence identity diagnostics may now use ADR-0004 as rule source.

Nächster geplanter Schritt:

`000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` - accepted by patch 000065

## Stand nach Patch 000065

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts ADR-0007.

Erreicht:

* Catalog-demo canonicalization states are defined: `legacy-demo-seed`, `candidate-reference-slice`, `canonical-reference-slice` and `deprecated-seed-fragment`.
* The existing CatalogItem implementation remains `legacy-demo-seed`.
* A future CatalogItem implementation patch must explicitly state whether it creates a candidate slice or completes canonicalization.
* Canonical status requires evidence across endpoint, DTO, validation, error, application-layer, persistence, mapping, security-classification, gate-evidence and deferral topics.
* G5 report-only readiness diagnostics may use ADR-0007 as rule source.
* Target projects remain read-only comparison inputs and are not supplied by this ADR.

Nächster geplanter Schritt:

`000066_springmaster_adr_0005_security_and_permission_boundary` or a narrowly scoped report-only gate seed that avoids strict security enforcement.

## Stand nach Patch 000066

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts ADR-0005.

Erreicht:

* Endpoint security classification is now an accepted architecture decision.
* Permission naming uses `<domain>:<resource>:<operation>`.
* Catalog-demo first security vocabulary is defined for read, create, update, delete, delete-multiple, options and lifecycle transitions.
* Role-to-permission mapping and authorization placement are decision-backed.
* `documented-deferred-security` and `implemented-management-security` are accepted Catalog-demo security modes.
* Report-only G4 security diagnostics may reference ADR-0005 as rule source.

Nächster geplanter Schritt:

`000067_springmaster_report_only_gate_seed_plan` or `000067_springmaster_adr_0008_configuration_runtime_profile_strategy`, depending on whether the next step should start gate planning or close the next P1 ADR before implementation.

## Stand nach Patch 000067

Patch `000067_springmaster_report_only_gate_seed_plan` introduces the planning bridge from accepted ADRs to the first report-only gate implementation.

Erreicht:

* The first report-only seed identity is defined as `springmaster.report-only-gate-seed.v1`.
* Initial gate IDs are defined for G0, G1, G3, G4 and G5 diagnostics.
* Rule sources are mapped to accepted ADRs `ADR-0002` through `ADR-0007`.
* Report files are defined: `summary.txt`, `summary.json`, `findings.jsonl`, `rule-sources.json`, `input-manifest.json` and optional `evidence/`.
* Report-only exit behavior is clarified.
* Target-project scanning and modification are explicitly excluded.

Nächster geplanter Schritt:

`000068_springmaster_report_only_gate_tooling_seed` as a code/tooling patch with tests/build validation, or a smaller preparatory tooling patch if the existing build structure requires it.

## Stand nach Patch 000068

Patch `000068_springmaster_report_only_gate_tooling_seed` introduces the first executable report-only gate seed as a tooling/code patch.

Erreicht:

* `bin/springmaster-gates.py` implements the first source-based report-only diagnostics.
* `bin/springmaster-gates.sh` provides the wrapper command.
* `bin/springmaster-gates-selfcheck.sh` validates report generation and report structure.
* The report shape from patch 000067 is implemented with `summary.txt`, `summary.json`, `findings.jsonl`, `rule-sources.json` and `input-manifest.json`.
* The scope remains `springmaster-reference-only`.
* Target-project input is rejected and no target project is scanned or modified.
* Findings remain non-blocking in report-only mode.

Nächster geplanter Schritt:

`000069_springmaster_gate_maven_profile_report_mode` or a narrow hardening patch for JSON report schemas and OpenAPI input discovery, depending on the validation result of the first tooling seed.


## Stand nach Patch 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` hardens the report-only gate tooling introduced by 000068.

Erreicht:

* `bin/springmaster-gates-regression.sh` validates the gate report structure and safety behavior.
* `summary.json`, `rule-sources.json` and `input-manifest.json` include the schema marker `springmaster.report-only-report.v1`.
* JUnit coverage executes gate regression during `mvn test`.
* Maven profile `springmaster-gates-report` runs an additional report-only gate report with run id `maven-profile`.
* Findings remain non-blocking in report-only mode.
* Target-project input remains rejected.

Nächster geplanter Schritt:

`000070_springmaster_gate_report_schema_and_fixture_expansion` or a first narrow OpenAPI input discovery patch, depending on whether the next priority is report schema documentation or deeper G1 API diagnostics.

## Stand nach Patch 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` classifies the first report-only gate findings baseline.

Erreicht:

* The current report-only output with `12` findings is documented and interpreted.
* G0 rule-source findings are classified as positive evidence.
* G1 query/status/error findings are classified as expected Catalog-demo `legacy-demo-seed` gaps or candidate-slice work items.
* G4 security warning is kept as documented deferred-security evidence.
* G5 Catalog-demo readiness remains `MANUAL_REVIEW` because Catalog-demo is not candidate or canonical.
* No strict gate, target scan, Java change, Maven change or Catalog-demo implementation change is introduced.

Nächster geplanter Schritt:

`000071_springmaster_catalog_demo_candidate_slice_contract_plan` - implemented as the candidate-slice contract planning bridge.

## Stand nach Patch 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` creates the implementation bridge from report-only gate findings to Catalog-demo candidate work.

Erreicht:

* `PROJECT_DOCS/DEMO/CATALOG_DEMO_CANDIDATE_SLICE_CONTRACT_PLAN.md` defines the first CatalogItem candidate endpoint contract.
* The plan maps the `000070` G1, G4 and G5 findings to concrete candidate-slice work items.
* The next CatalogItem code patch must create a `candidate-reference-slice`, not a canonical slice.
* The candidate contract includes paged list, detail by opaque `id`, lookup by `sku`, create, full update and bodyless delete.
* `sortBy`, standard error body, explicit DTO roles, security classification evidence and candidate evidence are mandatory for the implementation patch.
* The plan remains documentation-only and does not modify Java code, Maven, gate tooling, target projects or Demo runtime behavior.

Nächster geplanter Schritt:

`000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation` as a code/demo patch with Maven tests, report-only gate validation and Full-ZIP export.

## Stand nach Patch 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` performs a documentation-only forensic review of the CatalogItem candidate foundation from `000072`.

Erreicht:

* Candidate endpoint contract is substantially implemented.
* Report-only findings decreased from `12` to `9`.
* The slice is accepted as `candidate-reference-slice foundation`.
* Catalog-demo is still not canonical.
* Target comparison and target delivery remain blocked.
* Remaining cleanup is documented: DTO boundary for availability/range, service update validation symmetry, legacy unpaged service helper and G5 evidence detection.

Nächster geplanter Schritt:

`000074_springmaster_catalog_demo_candidate_slice_alignment` as a small code/demo and gate-alignment patch with Maven tests, gate regression, gate smoke and Full-ZIP export.



## Stand nach Patch 000074

Patch `000074_springmaster_catalog_demo_candidate_slice_alignment` aligns the report-only gate with CatalogItem candidate evidence.

Erreicht:

* `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json` adds machine-readable candidate evidence.
* `input-manifest.json` now includes `catalogDemoEvidence`.
* G5 recognizes current `candidate-reference-slice` evidence before historical `legacy-demo-seed` text.
* Report-only findings decrease from `9` to `8`.
* G5 manual review is closed for the current candidate slice.
* G4 remains as expected `documented-deferred-security` warning.
* No strict gates, target scans or target updates are introduced.

Nächster geplanter Schritt:

`000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup` as a demo-code patch for DTO-boundary cleanup and service update validation symmetry.

## Stand nach Patch 000075

Patch `000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup` closes the DTO-boundary and validation cleanup for the CatalogItem candidate-reference-slice.

Erreicht:

* `CatalogItemAvailabilityDTO` separates public request DTOs from the persistence-oriented `Range` type.
* Create and Update validation are symmetric at the service boundary.
* The unpaged legacy helper `CatalogItemService.list()` is removed.
* Candidate evidence records DTO-boundary and service-validation state.
* Report-only gates remain stable with `8` findings and no `BLOCKER`/`ERROR`.

Nächster geplanter Schritt:

`000076_springmaster_project_new_instantiation_acceptance_review` as a tooling/acceptance patch to prove that Springmaster can instantiate a new technical Java backend baseline.

## Stand nach Patch 000076

Patch `000076_springmaster_project_new_instantiation_acceptance_review` validates the conservative service-instantiation path.

Erreicht:

* `bin/project-new-acceptance.sh` creates and validates a disposable `sample-backend` project.
* `ProjectNewInstantiationAcceptanceTest` includes the instantiation proof in Maven tests without nested generated-project Maven execution.
* `project-new.sh` renders copied DBTool defaults with sanitized DB identifiers.
* Generated projects can prove patch bootstrap, export and DBTool status immediately after creation.

Nächster geplanter Schritt:

`000077_springmaster_generated_service_slice_readiness_plan` defines the readiness bridge from a generated technical backend skeleton to a later generated fachlicher service slice.


## Stand nach Patch 000077

Patch `000077_springmaster_generated_service_slice_readiness_plan` documents the transition from technical skeleton instantiation to generated service-slice readiness.

Erreicht:

* Springmaster remains a validated technical Backend-Skeleton factory after `000076`.
* A generated service slice is explicitly defined as a second stage above Project-New.
* Core distribution is identified as the next architectural decision before generated fachlicher slices can rely on `de.cocondo.system` code in target projects.
* The CatalogItem candidate slice is classified as blueprint input, not as canonical copy source.
* Readiness criteria are documented for DTOs, validation, mapping, service boundary, error contract, evidence, tests, generated-project export and gate behavior.
* Target comparison and target delivery remain blocked.

Nächster Korrekturschritt:

`000078_springmaster_generated_service_slice_readiness_marker_alignment` aligns the readiness documentation with the existing validation marker `technical Backend-Skeleton`, without introducing code, target scans, generated slices or strict gates.


## Stand nach Patch 000078

Patch `000078_springmaster_generated_service_slice_readiness_marker_alignment` closes the documentation-marker gap found during the `000077` validation.

Erreicht:

* `PROJECT_DOCS/TOOLING/GENERATED_SERVICE_SLICE_READINESS_PLAN.md` explicitly contains the stable validation marker `technical Backend-Skeleton`.
* The marker is documented as a synonym for the German wording `technisches Java-Backend-Skeleton`.
* The planned generated-service-slice blueprint patch is renumbered to `000079` to avoid semantic collision with this corrective marker patch.
* No Java, Maven, Shell tooling, Core, Demo, Template, Platform-Update or target-project files are changed.

Nächster geplanter Schritt:

`000079_springmaster_generated_service_slice_blueprint_spec` was originally planned to specify the concrete file/package/token blueprint and acceptance scenario for a first generated aggregate slice. This slot is now intentionally used for the ZBM target-registry and lifecycle alignment before generation continues.

## Stand nach Patch 000079

Patch `000079_springmaster_zbm_target_registry_and_lifecycle_alignment` aligns Springmaster target configuration with the first planned delivered Java backend project `zbm`.

Erreicht:

* `zbm` is added as the first planned Springmaster-delivered target under `/opt/cocondo/zbm`.
* Existing/running projects `idm` and `personnel` are explicitly deferred as `DEFERRED_EXISTING_PROJECT_NO_DELIVERY`.
* `contacts` and `orders` remain non-delivery references until explicitly verified and reclassified.
* Target descriptors distinguish initialization from updates through lifecycle fields.
* `target-apply` is guarded by `TARGET_DELIVERY_ENABLED=true`, preventing accidental delivery into deferred projects.
* The Platform-Update profile list includes `defaults` for baseline configuration defaults.

Nächster geplanter Schritt:

`000080_springmaster_generated_service_slice_blueprint_spec` should specify the concrete file/package/token blueprint and acceptance scenario for a first generated aggregate slice for the new target direction, without delivery to IDM or Personnel.

## Stand nach Patch 000080

Patch `000080_springmaster_generated_service_slice_blueprint_spec` documents the generator blueprint and the first ZBM initialization concept test.

Erreicht:

* The service-slice generator is specified as a future patch-producing generator, not as a direct target mutator.
* `project-new` remains responsible for technical project initialization only.
* `platform-update` remains responsible for later controlled Core/Tooling/Defaults updates.
* The first practical target remains `zbm` under `/opt/cocondo/zbm` with base package `de.cocondo.zbm`.
* The initial test scope is limited to ZBM project initialization, local patch-system validation, `mvn test`, and target full export.
* IDM and Personnel remain explicitly deferred and are not part of this test.

Nächster geplanter Schritt:

Run the ZBM initialization concept test. After that, decide whether `000081` should implement Slice Generator Foundation or first implement a controlled Core source-copy update for `zbm`.


## Stand nach Patch 000081

Patch `000081_springmaster_zbm_core_source_copy_acceptance` prepares the first controlled Core source-copy update for the generated ZBM backend.

Erreicht:

* `platform-update generate --profile core` writes its generated review document to a Core-scope-compatible path under `PROJECT_DOCS/CORE/PLATFORM_UPDATES/**`.
* Core and Core-runtime generated patches synthesize a target-local `pom.xml` with the minimal Core dependencies instead of copying the Springmaster master `pom.xml`.
* The ZBM Core source-copy acceptance is documented as the required bridge between technical project initialization and fachlicher service-slice generation.
* The acceptance keeps `TARGET_DELIVERY_ENABLED=false`; the reviewed patch is applied through ZBM's local patch system.

Nächster geplanter Schritt:

Run the ZBM Core source-copy acceptance. After that, implement a first small generated fachlicher service slice for `zbm`.

## Stand nach Patch 000115

Patch `000115_springmaster_backend_api_pattern_operational_roadmap` persistiert die operative Priorisierung für die nächsten Backend-API-Pattern-Arbeiten.

Erreicht:

* Der Query-/List-/All-/Count-Strang ist nach `000114` als abgeschlossenes Candidate-Reference-Thema eingeordnet.
* Die nächsten operativen Pattern-Familien sind priorisiert: Global Error Contract, Detail/Lookup, Write API Contract, Request Validation/OpenAPI Gate und Generated Slice Adoption Plan.
* Nachgelagerte Themen wie Command-Bulk, Relationship Commands, Strict-Gate-Promotion, Cursor-/Keyset-Pagination, Async Export und Observability sind bewusst zurückgestellt.
* Die Abarbeitung ist mit Patch-Schnitt, Vorprüfung, Baseline-Regel und Abschlusskriterien operationalisiert.

Nächster geplanter Schritt:

`000116_springmaster_global_api_error_contract_core` als Core-/Demo-/Test-Patch.

Hinweis: Die Nummerierung verschiebt sich gegenüber der Analyseempfehlung, weil dieses operative Roadmap-Dokument als eigener Patch persistiert wird.

## Stand nach Patch 000118

Patch `000118_springmaster_detail_lookup_contract_report` ergänzt nach Query und globaler Fehlerbehandlung die report-only Absicherung für Detail-/Alternate-Key-Lookup-Endpunkte.

Erreicht:

* `bin/detail-lookup-contract-gate-report.py` und `.sh` erzeugen ein maschinenlesbares Detail/Lookup-Report-Artefakt.
* `DETAIL_LOOKUP_CONTRACT_REPORT.md` definiert Schema, Finding-Familien und Promotion-Regeln.
* CatalogItem ist Golden Reference für `GET /api/demo/catalog/items/{id}` und `GET /api/demo/catalog/items/by-sku/{sku}`.
* MockMvc- und OpenAPI-Evidence sichern positive Lookup-Fälle, `404 RESOURCE_NOT_FOUND`, path variables und create-`Location` Detail-Follow-up ab.
* Der Report bleibt bewusst report-only; Write API, Validation/OpenAPI und Generated-Slice-Adoption bleiben Folgearbeiten.

Nächster geplanter Schritt:

`000119_springmaster_write_api_contract_report` für Create/Update/Delete-Basismuster.

## Stand nach Patch 000119

Patch `000119_springmaster_write_api_contract_report` ergänzt nach Query, globaler Fehlerbehandlung und Detail/Lookup die report-only Absicherung für Create-/Update-/Delete-Endpunkte.

Erreicht:

* `bin/write-api-contract-gate-report.py` und `.sh` erzeugen ein maschinenlesbares Write-API-Report-Artefakt.
* `WRITE_API_CONTRACT_REPORT.md` definiert Schema, Finding-Familien und Promotion-Regeln.
* CatalogItem ist Golden Reference für `POST /api/demo/catalog/items`, `PUT /api/demo/catalog/items/{id}` und bodyless `DELETE /api/demo/catalog/items/{id}`.
* MockMvc- und OpenAPI-Evidence sichern CreateDTO/UpdateDTO Request Bodies, `201 Created` plus `Location`, `200 OK` Update, `204 No Content` Delete und globale Fehlerfälle für `400`, `404` und `409` ab.
* Der Report bleibt bewusst report-only; Request Validation/OpenAPI-required-Felder und Generated-Slice-Adoption bleiben Folgearbeiten.

Nächster geplanter Schritt:

`000120_springmaster_request_validation_openapi_gate` für Bean Validation, Boundary-DTOs und OpenAPI-required-Feld-Abgleich.

## Stand nach Patch 000120

Patch `000120_springmaster_request_validation_openapi_gate` ergänzt das report-only Gate für Request Validation, DTO-Boundary und OpenAPI-required-Feld-Abgleich.

Erreicht:

* `REQUEST_VALIDATION_OPENAPI_GATE.md` definiert Ziel, Report-Schema, Finding-Familien und Promotion-Regeln.
* CatalogItem ist Golden Reference für Bean Validation Required Fields in `CatalogItemCreateDTO` und `CatalogItemUpdateDTO`.
* Das neue Tooling `request-validation-openapi-gate-report` erzeugt eine stabile JSON-Fixture.
* Die OpenAPI-Evidenz prüft, dass Create `sku` und `name` sowie Update `name` als required dokumentiert.
* Die globale `VALIDATION_FAILED` Fehlerbehandlung bleibt Runtime-Referenz für ungültige Request Bodies.

Nächster geplanter Schritt:

`000121_springmaster_generated_slice_api_pattern_adoption_plan` zur Planung der Generator-/Template-Adoption für Query, Detail, Write, Error und Validation Patterns.

## Stand nach Patch 000121

Patch `000121_springmaster_generated_slice_api_pattern_adoption_plan` überführt die abgeschlossenen API-Basismuster in eine konkrete Generator-/Template-Adoptionsplanung.

Erreicht:

* `PROJECT_DOCS/TOOLING/GENERATED_SLICE_API_PATTERN_ADOPTION_PLAN.md` definiert das Zielbild eines generated service slice nach Query, Detail, Write, Error und Validation Patterns.
* Die ältere Blueprint-Spezifikation wird an den aktuellen API-Stand angepasst: `/all` und `/count` sind für managementfähige Generated Slices jetzt Bestandteil des Standard-Query-Surface.
* CatalogItem bleibt Candidate Reference, aber nicht Copy-and-Paste-Template.
* Die Akzeptanzkriterien für generated target patches, Evidence, report-only Gates, Zielprojekt-Maven-Test und Full-ZIP-Export sind dokumentiert.
* Zielprojekt-Delivery, Generator-Code, strict Gate Promotion, Bulk Commands, State Commands und Relationship Commands bleiben bewusst außerhalb dieses Patches.

Nächster geplanter Schritt:

`000122_springmaster_generated_slice_spec_contract` für den YAML-/JSON-Spec-Vertrag und eine Golden Spec eines neutralen Generated Slice.


## Stand nach Patch 000122

Patch `000122_springmaster_generated_slice_spec_contract` definiert den verbindlichen Dokumentationsvertrag für künftige Generated Service Slices.

Erreicht:

* `PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_CONTRACT.md` beschreibt den YAML-/JSON-fähigen `GeneratedServiceSlice` Contract.
* `PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml` liefert eine neutrale Golden Spec ohne Demo-Package-Reuse.
* Die Spec bündelt Query/List/All/Count, Detail/Lookup, Write, Request Validation/OpenAPI und global Error Contract in einem reviewbaren Modell.
* Zielprojekt-Delivery bleibt Patch-ZIP-basiert und wird weiterhin nicht direkt aus Springmaster angewendet.

Nächster geplanter Schritt:

`000123_springmaster_generated_slice_spec_fixture_gate` für ein maschinenlesbares Fixture-/Report-Gate des Slice-Spec-Vertrags.


## Stand nach Patch 000123

Patch `000123_springmaster_generated_slice_spec_fixture_gate` implements the first executable gate for the `GeneratedServiceSlice` contract.

Erreicht:

* dependency-free strict YAML parsing for contract version `1`;
* deterministic JSON report and committed BusinessPartner golden fixture;
* strict validation of all eleven top-level fields;
* full management API surface including alternate lookup;
* explicit CreateDTO/UpdateDTO and request validation boundary;
* global Core error response with machine-readable `400`, `404` and `409` families;
* all four required report families;
* patch-only delivery and Demo-package prohibition;
* negative fail-closed test cases for representative contract violations.

Nicht Bestandteil dieses Patches sind Intermediate Representation, renderer, patch-blueprint generation and ZBM target delivery.

Nächster P0-Schritt:

```text
000124_springmaster_patch_artifact_preflight_hardening
```

Nach dessen Abschluss folgt `000125_springmaster_generated_slice_intermediate_representation`.

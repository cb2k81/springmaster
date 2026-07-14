# Springmaster Version Policy

## Zweck

Diese Policy legt fest, wie der Stand von Springmaster, Core, Tooling, Templates, Demo und Platform-Update-Mechanik versioniert wird.

Die Versionierung ist eine Arbeits- und Update-Versionierung innerhalb des Masterprojekts. Sie ersetzt nicht zwingend spätere Maven-Artefakt-Versionierung, bereitet diese aber vor.

## Versionsdatei

Die kanonische Versionsdatei ist:

```text
platform/versions/platform.env
```

Sie ist bewusst als Shell-kompatible `.env`-Datei gehalten, damit Tooling sie später ohne Parser-Abhängigkeit lesen kann.

## Versionsdimensionen

| Variable | Bedeutung |
|---|---|
| `PLATFORM_VERSION` | Gesamtstand des Masterprojekts als Kombination aus Tooling, Core, Templates, Demo und Update-Fähigkeit |
| `PLATFORM_CORE_VERSION` | Stand des wiederverwendbaren Java-Core unter `de.cocondo.system` |
| `PLATFORM_TOOLING_VERSION` | Stand von Patch-, Export-, Build-, DBTool-, Project-New- und Update-Tooling |
| `PLATFORM_TEMPLATE_VERSION` | Stand des Project Skeletons und der Projektanlage-Vorlagen |
| `PLATFORM_DEMO_VERSION` | Stand der Demo-Domänen im Masterprojekt |
| `PLATFORM_UPDATE_VERSION` | Stand der Zielprojekt-Update-Mechanik |
| `PLATFORM_STATE_PATCH` | letzter Patch, mit dem der versionierte Stand fachlich festgestellt wurde |
| `PLATFORM_BASELINE_KIND` | bevorzugter Baseline-Artefakttyp für Übergabe und Review |

## Initiale Foundation-Versionen nach 000012

```text
PLATFORM_VERSION=0.2.0-foundation
PLATFORM_CORE_VERSION=0.1.0
PLATFORM_TOOLING_VERSION=0.2.0
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.0.0
PLATFORM_UPDATE_VERSION=0.0.0
```

Begründung:

* `PLATFORM_CORE_VERSION=0.1.0`: erster fachfreier Core-Code-Slice ist vorhanden und Persistence-Dependency ist vorbereitet.
* `PLATFORM_TOOLING_VERSION=0.2.0`: Patchsystem, Export, DBTool-Basis, Buildtool, Selfcheck und Project-New sind operationalisiert.
* `PLATFORM_TEMPLATE_VERSION=0.1.0`: Project Skeleton erzeugt ein testbares Minimalprojekt.
* `PLATFORM_DEMO_VERSION=0.0.0`: noch keine echte Demo-Domäne vorhanden.
* `PLATFORM_UPDATE_VERSION=0.0.0`: Zielprojekt-Update-Generator ist noch nicht operativ.
* `PLATFORM_VERSION=0.2.0-foundation`: der Gesamtstand ist mehr als Bootstrap, aber noch nicht Feature-complete.

## Erhöhungsregeln

### Patch-Version

Die Patch-Version wird erhöht bei:

* Dokumentationskorrekturen mit versionierter Relevanz
* kleinen Tooling-Fixes ohne neue Fähigkeit
* kleinen Core-Bugfixes ohne API-Erweiterung

### Minor-Version

Die Minor-Version wird erhöht bei:

* neuem Core-Slice
* neuer Tooling-Fähigkeit
* neuem Template-Generator-Verhalten
* erster Demo-Domäne
* erster operativer Target-Update-Erzeugung

### Major-Version

Die Major-Version wird erst verwendet, wenn:

* inkompatible Core-Änderungen eingeführt werden
* Zielprojekt-Update-Verträge brechen
* Patch-/Export-/Rollback-Formate inkompatibel geändert werden

## Versionierungspflicht

Ein Patch muss die Versionsdatei aktualisieren, wenn er mindestens eine der folgenden Eigenschaften hat:

* Core-Code oder Core-API wird erweitert oder inkompatibel geändert.
* Tooling-Fähigkeiten werden erweitert oder Vertragsverhalten ändert sich.
* Project Skeleton oder `project-new.sh` ändern das erzeugte Projektverhalten.
* Demo-Domänen werden eingeführt oder erweitert.
* Zielprojekt-Update-Mechanik wird eingeführt oder geändert.
* Ein Review-Patch stellt einen neuen Foundation-/Milestone-Stand fest.

Reine Dokumentationspatches ohne Status- oder Policy-Wirkung erhöhen keine Version.

## Beziehung zu Patches

Jede Versionserhöhung muss auf einen Patch verweisen. Der Patch wird in `PLATFORM_STATE_PATCH` festgehalten, wenn er den aktuellen versionierten Gesamtstand markiert.

## Beziehung zu Zielprojekten

Solange Core und Tooling noch nicht als eigene Artefakte veröffentlicht werden, ist die Version in `platform.env` die Referenz für Update-Patches in Zielprojekte.

Zielprojekt-Updates müssen später mindestens prüfen:

* Zielprojektname
* aktuell installierte Platform-/Core-/Tooling-Version
* erwartete Vorversion
* anzuwendende Zielversion
* Patch-Scope
* Rollback-Hinweis

## Verbotene Praxis

Nicht zulässig:

* Versionen stillschweigend ändern, ohne Changelog und Patch-Log.
* Core-, Tooling- und Template-Versionen pauschal gemeinsam erhöhen, obwohl nur ein Bereich betroffen ist.
* Zielprojekt-Updates ohne Versionsprüfung erzeugen.
* Versionsdatei als dekoratives Dokument führen, ohne sie in Tooling-Entscheidungen zu berücksichtigen.

## Patch-Scope-Unterstützung für Versionspflicht

Seit Patch `000014_springmaster_core_version_scope_alignment` darf der Patch-Scope `core` zusätzlich die Datei `platform/versions/platform.env` ändern.

Begründung:

* Core-Code- und Core-API-Erweiterungen müssen gemäß dieser Policy versioniert werden.
* Die Core-Änderung und die zugehörige Core-Versionserhöhung müssen atomar im selben Patch erfolgen können.
* Die Versionsdatei bleibt trotzdem kanonisch unter `platform/versions/platform.env`.

Zulässige Nutzung im Scope `core`:

* Erhöhung von `PLATFORM_CORE_VERSION` bei Core-Code- oder Core-API-Erweiterungen.
* Anpassung von `PLATFORM_VERSION`, wenn der Gesamtstand dadurch einen neuen Foundation-/Milestone-Stand erreicht.
* Aktualisierung von `PLATFORM_STATE_PATCH` auf den ausführenden Patch.

Nicht zulässig:

* pauschale Erhöhung nicht betroffener Teilversionen.
* Änderung der Target-Update-Version ohne Änderung an der Target-Update-Mechanik.
* Änderung der Template-Version ohne Änderung am Skeleton oder Project-New-Verhalten.

## Versionierter Stand nach 000015

Patch `000015_springmaster_core_persistence_basic_types` erhöht den Core-Stand auf:

```text
PLATFORM_VERSION=0.3.0-foundation
PLATFORM_CORE_VERSION=0.2.0
PLATFORM_STATE_PATCH=000015_springmaster_core_persistence_basic_types
```

Begründung:

* Der Core erhält einen neuen persistenznahen Code-Slice.
* Tooling-, Template-, Demo- und Platform-Update-Versionen bleiben unverändert.
* Der Gesamtstand steigt auf `0.3.0-foundation`, da der Master nach Bootstrap/Tooling/Basic-Core nun eine zweite Core-Fähigkeit enthält.

## Demo-Scope-Unterstützung für Versionspflicht

Seit Patch `000016_springmaster_demo_version_scope_alignment` darf der Patch-Scope `demo` zusätzlich die Datei `platform/versions/platform.env` und diese Version Policy ändern.

Begründung:

* Demo-Domänen sind ein eigener versionierter Bestandteil des Masterprojekts.
* Die erste Demo-Domäne und spätere Demo-Erweiterungen müssen `PLATFORM_DEMO_VERSION` atomar mit dem Demo-Code aktualisieren können.
* Demo-Code bleibt unter `de.cocondo.platform.demo` und wird nicht als distributable Core in Zielprojekte übertragen.

Zulässige Nutzung im Scope `demo`:

* Erhöhung von `PLATFORM_DEMO_VERSION` bei Einführung oder Erweiterung von Demo-Domänen.
* Anpassung von `PLATFORM_VERSION`, wenn der Gesamtstand dadurch einen neuen Foundation-/Milestone-Stand erreicht.
* Aktualisierung von `PLATFORM_STATE_PATCH` auf den ausführenden Patch.

Nicht zulässig:

* Änderung der Core-Version ohne Core-Code- oder Core-API-Änderung.
* Änderung der Tooling- oder Template-Version ohne Änderung an Tooling oder Templates.
* Übertragung von Demo-Code in den verteilbaren Core-Namespace `de.cocondo.system`.

## Versionierter Stand nach 000016

Patch `000016_springmaster_demo_version_scope_alignment` erhöht den Tooling-Stand auf:

```text
PLATFORM_VERSION=0.3.1-foundation
PLATFORM_TOOLING_VERSION=0.2.2
PLATFORM_STATE_PATCH=000016_springmaster_demo_version_scope_alignment
PLATFORM_BASELINE_KIND=full-zip
```

Begründung:

* Das Patchsystem unterstützt nun Demo-Code und Demo-Versionserhöhung atomar im Scope `demo`.
* Die Export- und Validierungsdokumentation wird auf den aktuell bevorzugten Full-ZIP-Abschluss ausgerichtet.
* Core-, Template-, Demo- und Platform-Update-Versionen bleiben unverändert.


## Versionierter Stand nach 000017

Patch `000017_springmaster_demo_catalog_basic_domain` erhöht den Demo-Stand auf:

```text
PLATFORM_VERSION=0.4.0-foundation
PLATFORM_DEMO_VERSION=0.1.0
PLATFORM_STATE_PATCH=000017_springmaster_demo_catalog_basic_domain
```

Begründung:

* Die erste echte Demo-Domäne wird unter `de.cocondo.platform.demo.catalog` eingeführt.
* Die Demo nutzt bestehende Core-Bausteine aus `de.cocondo.system`.
* Core-, Tooling-, Template- und Platform-Update-Versionen bleiben unverändert.
* Der Gesamtstand steigt auf `0.4.0-foundation`, weil der Master nun Core-Fähigkeiten nicht mehr nur isoliert testet, sondern durch eine Demo-Domäne verwendet.

## Versionierter Stand nach 000019

Patch `000019_springmaster_demo_catalog_validation_fix` erhöht den Demo-Stand auf:

```text
PLATFORM_VERSION=0.4.1-foundation
PLATFORM_DEMO_VERSION=0.1.1
PLATFORM_STATE_PATCH=000019_springmaster_demo_catalog_validation_fix
```

Begründung:

* Die erste Demo-Domäne aus `000017` war dateiseitig angewendet, aber die Maven-Pflichtvalidierung zeigte zwei Testprobleme.
* Patchnummer `000018` ist im lokalen Patch-Archiv bereits durch eine unveränderte Wiederanwendung des `000017`-Archivs belegt.
* Die Spring-Context-Testklasse lädt die Spring-Boot-Konfiguration nun explizit über `SpringmasterApplication`, weil Demo-Code unter `de.cocondo.platform.demo` nicht unterhalb des App-Pakets `de.cocondo.platform.app` liegt.
* Die Duplicate-SKU-Fehlermeldung ist an den erwarteten fachlichen Begriff `SKU` angepasst.
* Core-, Tooling-, Template- und Platform-Update-Versionen bleiben unverändert.

## Versionierter Stand nach 000020

Patch `000020_springmaster_demo_catalog_api_controller` erhöht den Demo-Stand auf:

```text
PLATFORM_VERSION=0.5.0-foundation
PLATFORM_DEMO_VERSION=0.2.0
PLATFORM_STATE_PATCH=000020_springmaster_demo_catalog_api_controller
```

Begründung:

* Die Demo-Domäne `catalog` erhält eine erste Spring-Web-API unter `/api/demo/catalog/items`.
* Die API verwendet den bestehenden Demo-Service und damit weiterhin Core-Bausteine aus `de.cocondo.system`.
* Die Fehlerabbildung für Validierungs- und Duplicate-SKU-Fälle wird über Controller-Tests abgesichert.
* Persistenz-Runtime, Repository-Schicht, DataSource-Konfiguration und Liquibase-Demo-Tabellen bleiben weiterhin bewusst ausgeklammert.
* Core-, Tooling-, Template- und Platform-Update-Versionen bleiben unverändert.

## Versionierter Stand nach 000021

Patch `000021_springmaster_demo_catalog_api_pathvariable_fix` erhöht den Demo-Stand auf:

```text
PLATFORM_VERSION=0.5.1-foundation
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_STATE_PATCH=000021_springmaster_demo_catalog_api_pathvariable_fix
```

Begründung:

* Patch `000020` wurde dateiseitig angewendet, die Maven-Pflichtvalidierung zeigte jedoch einen Controller-Testfehler bei Pfadvariablen.
* Der API-Controller bindet die SKU-Pfadvariable nun explizit mit `@PathVariable("sku")`.
* Dadurch bleibt die API unabhängig davon, ob der Java-Compiler Parameter-Namen per `-parameters` verfügbar macht.
* Core-, Tooling-, Template- und Platform-Update-Versionen bleiben unverändert.


## Tooling-Version 0.3.0

Patch `000022_springmaster_patch_accept_verify_workflow` erhöht die Tooling-Version auf `0.3.0`, weil das Patchsystem mit `accept` und `verify` eine neue operative Abnahmefähigkeit erhält.

Die Gesamtversion wird auf `0.6.0-foundation` erhöht. Der Stand ist weiterhin Foundation, aber die tägliche Patch-Integration ist ab diesem Punkt deutlich stärker operationalisiert.


## Tooling-Version 0.3.1

Patch `000023_springmaster_patch_accept_workflow_hardening` erhöht die Tooling-Version auf `0.3.1`.

Der Patch verschärft die Abnahmefähigkeit aus `000022`:

* `accept` und `verify` verwenden standardmäßig das Profil `auto`.
* Der Full-ZIP-Export ist standardmäßig aktiv.
* Vollständige Maven-Tests werden automatisch aktiviert, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind.
* Der Tooling-Selfcheck erzeugt im Standard keinen Full-Parts-Baseline-Export mehr.

Die Gesamtversion wird auf `0.6.1-foundation` erhöht. Core-, Demo-, Template- und Platform-Update-Versionen bleiben unverändert.

## Tooling-Version 0.3.2

Patch `000024_springmaster_patch_accept_export_hygiene` erhöht die Tooling-Version auf `0.3.2`.

Der Patch reduziert Export-Duplikate im neuen Patch-Abnahme-Workflow:

```text
PLATFORM_VERSION=0.6.2-foundation
PLATFORM_TOOLING_VERSION=0.3.2
PLATFORM_STATE_PATCH=000024_springmaster_patch_accept_export_hygiene
```

Begründung:

* `accept` und `verify` führen den Tooling-Selfcheck künftig mit `--no-export` aus.
* Der eigentliche Full-ZIP-Export bleibt weiterhin ein eigener, zentraler Abnahmeschritt des Patchworkflows.
* `tooling-selfcheck.sh` bleibt als Standalone-Kommando abwärtskompatibel und erzeugt im Standard weiterhin einen Full-ZIP-Export.
* Für ausgabearme Patch-Abnahmen wird dadurch nur noch der explizite Workflow-Export erzeugt.
* Core-, Demo-, Template- und Platform-Update-Versionen bleiben unverändert.

## Platform-Update-Version 0.1.0

Patch `000025_springmaster_platform_update_foundation` erhöht die Platform-Update-Version auf `0.1.0`.

```text
PLATFORM_VERSION=0.7.0-foundation
PLATFORM_TOOLING_VERSION=0.3.3
PLATFORM_UPDATE_VERSION=0.1.0
PLATFORM_STATE_PATCH=000025_springmaster_platform_update_foundation
```

Begründung:

* `bin/platform-update.sh` wird vom Placeholder zu einem konservativen Foundation-Tool ausgebaut.
* Zielprojekt-Deskriptoren können gelistet, angezeigt und validiert werden.
* Für ein Zielprojekt kann ein nicht-invasiver Update-Plan erzeugt werden.
* Der `platform-update`-Scope unterstützt künftig die zentrale Versionsdatei und die Version Policy, damit spätere Platform-Update-Patches ihre Versionsänderung atomar mitliefern können.
* Zielprojekt-Patch-ZIP-Erzeugung und automatische Anwendung bleiben bewusst Folgearbeiten.


## Platform-Update-Version 0.2.0

Patch `000026_springmaster_platform_update_patch_generation_plan` erhöht die Platform-Update-Version auf `0.2.0`.

```text
PLATFORM_VERSION=0.8.0-foundation
PLATFORM_UPDATE_VERSION=0.2.0
PLATFORM_STATE_PATCH=000026_springmaster_platform_update_patch_generation_plan
```

Begründung:

* `bin/platform-update.sh` kann erstmals target-lokale Plan-Patch-ZIPs erzeugen.
* Die Generierung bleibt nicht-invasiv und schreibt nicht in Zielprojektpfade.
* Das erzeugte ZIP folgt dem bestehenden Patchformat mit `manifest.json`, `files/**` und `logs/CHANGELOG-*.md`.
* Der Payload ist bewusst dokumentationsbasiert, damit das Format validiert werden kann, bevor echte Core- oder Tooling-Dateien übertragen werden.
* Core-, Demo-, Template- und allgemeine Patch-Abnahme-Versionen bleiben unverändert.


## Stand nach 000028

Patch `000028_springmaster_patch_accept_noop_guard` erhöht die Tooling-Version auf `0.3.4`.

```text
PLATFORM_VERSION=0.8.1-foundation
PLATFORM_TOOLING_VERSION=0.3.4
PLATFORM_STATE_PATCH=000028_springmaster_patch_accept_noop_guard
```

Die Erhöhung dokumentiert ausschließlich eine Tooling-Härtung: `patch.sh accept` verhindert künftig die versehentliche erneute Archivierung eines bereits angewendeten No-op-Patches.


## Platform-Update-Version 0.3.0

Patch `000029_springmaster_platform_update_core_payload_mapping` erhöht die Platform-Update-Version auf `0.3.0`.

```text
PLATFORM_VERSION=0.9.0-foundation
PLATFORM_UPDATE_VERSION=0.3.0
PLATFORM_STATE_PATCH=000029_springmaster_platform_update_core_payload_mapping
```

Begründung:

* `platform-update generate --profile core` erzeugt erstmals ein Zielprojekt-Patch-ZIP mit realem Core-Payload.
* Der Payload umfasst `src/main/java/de/cocondo/system/**`, `src/test/java/de/cocondo/system/**` und `PROJECT_DOCS/CORE/**`.
* Zielprojekte werden weiterhin nicht automatisch verändert.
* Die Anwendung des generierten ZIPs bleibt Aufgabe des Zielprojekt-Patchsystems.
* Core-, Demo-, Template- und allgemeine Patch-Abnahme-Versionen bleiben unverändert.

## Stand 000029 – Historien- und No-op-Korrektur

Der Patch `000029_springmaster_patch_accept_noop_guard_and_state_alignment` erhöht den Tooling-Stand auf `0.3.5` und den Gesamtstand auf `0.9.1-foundation`.

Hintergrund: Das Platform-Update-Core-Payload-Mapping wurde lokal als Patch `000028_springmaster_platform_update_core_payload_mapping` angewendet. Die ursprünglich geplante No-op-Guard-Härtung war dabei nicht lokal verfügbar. `000029` stellt diese Härtung her und setzt den State-Pointer wieder auf den tatsächlich letzten steuernden Patch.

## Stand 000030 – Projektlokale Scope-Konfiguration

Mit `000030_springmaster_patch_project_local_scope_env` steigt die Tooling-Version auf `0.3.6`. Die Änderung erweitert das Patchsystem um projektlokale Scope-/Pfaddefinitionen aus `.env` und verändert keine Core-, Demo- oder Platform-Update-Payloads.


## Platform-Update-Version 0.4.0

Patch `000031_springmaster_platform_update_target_patch_apply_plan` erhöht die Platform-Update-Version auf `0.4.0`.

```text
PLATFORM_VERSION=0.10.0-foundation
PLATFORM_UPDATE_VERSION=0.4.0
PLATFORM_STATE_PATCH=000031_springmaster_platform_update_target_patch_apply_plan
```

Begründung:

* `platform-update apply-plan` erzeugt für generierte Zielpatches einen prüfbaren Apply-Plan.
* Die tatsächliche Anwendung im Zielprojekt bleibt manuell und zielprojektlokal.
* Springmaster schreibt bei der Planerzeugung nicht nach `TARGET_PATH`.
* Core-, Demo-, Template- und allgemeine Patch-Abnahme-Versionen bleiben unverändert.

## Stand nach 000032

`000032_springmaster_platform_update_target_scope_preflight` erhöht den Platform-Update-Stand auf `PLATFORM_UPDATE_VERSION=0.5.0` und den Gesamtstand auf `PLATFORM_VERSION=0.11.0-foundation`. Der Patch ergänzt keinen Java-Code, sondern erweitert den nicht-invasiven Platform-Update-Workflow um eine Zielprojekt-Preflight-Prüfung.


## Version nach Target Compatibility Plan

Patch `000033_springmaster_platform_update_target_compatibility_plan` erhöht den Platform-Update-Stand, weil die Zielprojekt-Update-Mechanik um einen neuen nicht-invasiven Compatibility-Plan erweitert wird.

```text
PLATFORM_VERSION=0.12.0-foundation
PLATFORM_UPDATE_VERSION=0.6.0
PLATFORM_STATE_PATCH=000033_springmaster_platform_update_target_compatibility_plan
```

## Stand nach 000034

Patch `000034_springmaster_export_and_build_artifact_hygiene` erhöht den Tooling-Stand auf `PLATFORM_TOOLING_VERSION=0.3.7` und den Gesamtstand auf `PLATFORM_VERSION=0.12.1-foundation`.

```text
PLATFORM_VERSION=0.12.1-foundation
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_STATE_PATCH=000034_springmaster_export_and_build_artifact_hygiene
```

Begründung:

* Der reguläre Export wird wieder als saubere Projektbaseline geschärft.
* `.git/**`, generierte Platform-Update-Artefakte und Manifest-/Plan-Artefakte werden aus normalen Exports ausgeschlossen.
* Die globale `.env.example`-Ausnahme wird so begrenzt, dass sie `patches/archives/**` nicht mehr versehentlich wieder einschließt.
* Der geplante Build-/Transfer-Workspace unter `build/platform-update/**` wird als exportierter Nicht-Baseline-Bereich vorbereitet, aber noch nicht als primärer Schreibort eingeführt.
* Core-, Demo-, Template- und Platform-Update-Versionen bleiben unverändert.



## Platform-Update Build-Workspace seit 000035

`PLATFORM_UPDATE_VERSION=0.6.1` führt den dedizierten Workspace `build/platform-update/**` für generierte Zielpatches, Pläne und Logs ein. Dieser Bereich ist überschreibbar und nicht Teil regulärer Full-ZIP-Baselines.




## Platform-Update Review-Gate seit 000036

`000036_springmaster_platform_update_review_gate` erhöht den Platform-Update-Stand auf `PLATFORM_UPDATE_VERSION=0.7.0` und den Gesamtstand auf `PLATFORM_VERSION=0.12.3-foundation`.

Begründung:

* `apply-plan` ist jetzt ein verbindliches Review-Gate und erzeugt keine target-mutierenden Shell-Skripte mehr.
* Die reale Zielprojektänderung erfolgt ausschließlich über den expliziten Befehl `platform-update target-apply`.
* `target-apply` führt einen erneuten Preflight aus und schreibt vollständige Zielausgaben nach `build/platform-update/logs/**`.
* Terminalausgaben bleiben ausgabearm und enthalten nur Status, Logpfad und Exportpfad.



## Platform-Update Payload-Profile seit 000037

`000037_springmaster_platform_update_payload_profiles` erhöht den Platform-Update-Stand auf `PLATFORM_UPDATE_VERSION=0.8.0` und den Gesamtstand auf `PLATFORM_VERSION=0.12.4-foundation`.

Begründung:

* Der bisherige Core-Zielpayload war zu breit, weil Runtime, Tests und Springmaster-Masterdokumentation gemeinsam übertragen wurden.
* `core` steht künftig für Runtime + Tests.
* `core-docs` überträgt `PROJECT_DOCS/CORE/**` nur bei expliziter Auswahl.
* `platform-update-doc` erlaubt eine reine Zielprojekt-Update-Dokumentation.
* Zielprojektänderungen bleiben weiterhin an den Review-Gate und `target-apply` gebunden.

## Core Gap Inventory seit 000038

`000038_springmaster_core_idm_system_gap_inventory` erhöht den Gesamtstand auf `PLATFORM_VERSION=0.12.5-foundation`, lässt aber `PLATFORM_CORE_VERSION=0.2.0` unverändert.

Begründung:

* Der Patch verändert keinen Java-Code und keine Maven-Konfiguration.
* Er dokumentiert den verbindlichen Gap zwischen IDM-Alt-Core `de.cocondo.app.system` und Springmaster-Core `de.cocondo.system`.
* Die Entscheidung, den Springmaster-Core im IDM funktionsfähig zu machen und den Alt-Core später zu entfernen, wird in eine deterministische Migrationsreihenfolge übersetzt.
* Die Core-Implementierungsversion bleibt unverändert, weil noch kein zusätzlicher Core-Code übernommen wird.

```text
PLATFORM_VERSION=0.12.5-foundation
PLATFORM_CORE_VERSION=0.2.0
PLATFORM_STATE_PATCH=000038_springmaster_core_idm_system_gap_inventory
```

## Core DTO/List/Metadata Foundation seit 000039

`000039_springmaster_core_dto_list_metadata_foundation` erhöht den Gesamtstand auf `PLATFORM_VERSION=0.13.0-foundation` und den Core-Stand auf `PLATFORM_CORE_VERSION=0.3.0`.

Begründung:

* Der Patch erweitert den wiederverwendbaren Java-Core um DTO-, Paging- und Metadata-Vertragsbausteine.
* `spring-data-commons` wird bewusst als minimale Dependency für `Page`/`Sort` ergänzt, ohne JPA-Starter, Repository-Infrastruktur oder Liquibase einzuführen.
* Der Slice ist die erste Umsetzung aus der IDM-System-Core-Gap-Inventarisierung nach `000038`.
* IDM-Zielprojektänderungen bleiben weiterhin ausgesetzt und erfolgen später nur über Review-Gate und explizites `target-apply`.

```text
PLATFORM_VERSION=0.13.0-foundation
PLATFORM_CORE_VERSION=0.3.0
PLATFORM_STATE_PATCH=000039_springmaster_core_dto_list_metadata_foundation
```


## Core ID Generator Implementation seit 000040

`000040_springmaster_core_id_generator_implementation` erhöht den Gesamtstand auf `PLATFORM_VERSION=0.13.1-foundation` und den Core-Stand auf `PLATFORM_CORE_VERSION=0.3.1`.

Begründung:

* Der Patch ergänzt den bestehenden Core-Vertrag `IdGeneratorService` um die konkrete UUID-basierte Standardimplementierung `UuidIdGeneratorService`.
* Die Implementierung ist fachfrei, dependency-arm und als Spring `@Service` registrierbar.
* Der Slice schließt den risikoarmen Gap `core-id-implementation` aus der IDM-System-Core-Gap-Inventarisierung.
* IDM-Zielprojektänderungen, Importmigration und Löschung des alten IDM-Core bleiben weiterhin separaten, reviewpflichtigen Zielprojekt-Patches vorbehalten.

```text
PLATFORM_VERSION=0.13.1-foundation
PLATFORM_CORE_VERSION=0.3.1
PLATFORM_STATE_PATCH=000040_springmaster_core_id_generator_implementation
```

## Core Entity/Service/Sequence Inventory seit 000041

`000041_springmaster_core_entity_service_sequence_inventory` erhöht den Gesamtstand auf `PLATFORM_VERSION=0.13.2-foundation`, lässt aber `PLATFORM_CORE_VERSION=0.3.1` unverändert.

Begründung:

* Der Patch verändert keinen Java-Code und keine Maven-Konfiguration.
* Er klassifiziert den persistenznahen Slice `core-entity-service-and-sequence` aus der IDM-System-Core-Gap-Inventarisierung.
* Der Slice wird nicht als Ganzes übernommen, sondern in risikoarme Service-Unterstützung, Metadata-Persistenzmodell und NumberSequence-Foundation getrennt.
* Die Core-Implementierungsversion bleibt unverändert, weil keine zusätzlichen Core-Klassen eingeführt werden.

```text
PLATFORM_VERSION=0.13.2-foundation
PLATFORM_CORE_VERSION=0.3.1
PLATFORM_STATE_PATCH=000041_springmaster_core_entity_service_sequence_inventory
```

## Core Domain Entity Service Support seit 000042

`000042_springmaster_core_domain_entity_service_support` erhöht den Gesamtstand auf `PLATFORM_VERSION=0.13.3-foundation` und den Core-Stand auf `PLATFORM_CORE_VERSION=0.3.2`.

Begründung:

* Der Patch ergänzt den wiederverwendbaren Java-Core um `DomainEntityService` und `TagService` unter `de.cocondo.system.entity.service`.
* Die Umsetzung ist bewusst dependency-arm und verändert kein `DomainEntity`-Mapping.
* Persistenznahe Metadata-Entities, `KeyValueService`, NumberSequence, Repositories, Schema-/Liquibase-Themen und IDM-Zielprojektänderungen bleiben separaten Folgeschnitten vorbehalten.
* IDM-Importmigration und Löschung des alten IDM-Core erfolgen erst nach vollständiger Core-Abdeckung und Review-Gate.

```text
PLATFORM_VERSION=0.13.3-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_STATE_PATCH=000042_springmaster_core_domain_entity_service_support
```

## Reference Project and Standards Strategy since 000043

`000043_springmaster_reference_project_and_standards_strategy` increases the overall platform version to `PLATFORM_VERSION=0.13.4-foundation` and leaves `PLATFORM_CORE_VERSION=0.3.2` unchanged.

Reasoning:

* The patch changes documentation and strategy only.
* Existing projects such as IDM and Personnel are not supplied first by Springmaster.
* A new clean-room reference/demo application named Catalog-demo becomes the first integration proof.
* CatalogItem is the first pattern object for demonstrating entity, DTO, service, repository, controller, API and testing conventions.
* Springmaster is explicitly established as the owner of standards, conventions, ADRs, reference implementations and enforceable quality gates.
* The Core implementation version remains unchanged because no Java Core classes are introduced or changed.

```text
PLATFORM_VERSION=0.13.4-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_STATE_PATCH=000043_springmaster_reference_project_and_standards_strategy
```



## API Standards ADR Extraction since 000044

`000044_springmaster_api_standards_adr_extraction` increases the overall platform version to `PLATFORM_VERSION=0.13.5-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* Generic API standards are extracted from IDM API-readiness ADR themes into Springmaster-owned master-level standards.
* The patch defines standards for request validation, required OpenAPI fields, list/filter/query contracts, command HTTP semantics, external IDs and OpenAPI/YAML readiness.
* The standards are not target-project changes and do not supply IDM, Personnel or other existing projects.
* Catalog-demo remains the first intended demonstrator in later patches.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.5-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000044_springmaster_api_standards_adr_extraction
```

## API Endpoint Contract Definition Backlog since 000045

`000045_springmaster_api_endpoint_contract_definition_backlog` increases the overall platform version to `PLATFORM_VERSION=0.13.6-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It sharpens the API standardization workstream by documenting endpoint-contract decisions that must be made before Catalog-demo becomes the canonical reference implementation.
* It records the required definition backlog for list, bounded all-list, detail, lookup, first/latest/current retrieval, single delete, delete-multiple, state-transition commands, assignments, endpoint naming and OpenAPI gates.
* The patch uses IDM and Personnel as forensic comparison inputs only and does not change or supply existing target projects.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.6-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000045_springmaster_api_endpoint_contract_definition_backlog
```


## API Endpoint Contract Standard since 000046

`000046_springmaster_api_endpoint_contract_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.7-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It converts the endpoint-contract backlog from 000045 into canonical Springmaster API endpoint rules for new reference APIs.
* It defines the standard for paged list, bounded options/reference data, detail by id, alternate unique lookups, create, update, single delete, delete-multiple, state-transition commands and complex search.
* It explicitly separates public API vocabulary from Java repository/service vocabulary and prohibits public `findOne`, `findFirst` and `findLast` endpoint vocabulary for management APIs unless an ADR allows a special integration API.
* The patch defines future OpenAPI, MockMvc, reflection and ArchUnit gate targets but does not implement gates yet.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.7-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000046_springmaster_api_endpoint_contract_standard
```

## Real App Pattern Forensics since 000047

`000047_springmaster_real_app_pattern_forensics` increases the overall platform version to `PLATFORM_VERSION=0.13.8-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It analyzes current IDM and Personnel exports as comparison inputs for Springmaster standards, ADRs, Core contracts and future quality gates.
* It documents which real-app patterns Springmaster should adopt, which patterns should not become canonical and which topics require explicit standards or ADRs before Catalog-demo becomes the reference implementation.
* It derives a prioritized standards and gate backlog for API errors, DTO boundaries, validation, list/query contracts, commands, relationships, state transitions, security, persistence, mapping and architecture gates.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.8-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000047_springmaster_real_app_pattern_forensics
```

## API Error Contract Standard since 000048

`000048_springmaster_api_error_contract_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.9-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the canonical Springmaster API error response body, baseline error types, validation violation shape, status-code mapping, OpenAPI expectations and Catalog-demo readiness rule for error behavior.
* It converts a high-priority finding from `000047_springmaster_real_app_pattern_forensics` into a concrete standard before Catalog-demo becomes canonical.
* It does not introduce Java DTOs, ControllerAdvice, Maven checks, OpenAPI generators or test utilities yet; those belong to later Core/Gate patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.9-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000048_springmaster_api_error_contract_standard
```

## DTO Boundary and Validation Standard since 000049

`000049_springmaster_dto_boundary_and_validation_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.10-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the canonical Springmaster DTO boundary and validation standard before Catalog-demo becomes the reference implementation.
* It converts the high-priority DTO/validation finding from `000047_springmaster_real_app_pattern_forensics` into concrete rules for inbound DTOs, outbound DTOs, controller signatures, create/update/command/query roles, validation activation, OpenAPI visibility and future gates.
* It references and refines the existing request validation and required-field standards from 000044 without changing Java code.
* It does not introduce Java DTOs, reflection scans, OpenAPI tests, MockMvc helpers, ArchUnit rules or Maven-bound gates yet; those belong to later Core/Gate patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.10-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000049_springmaster_dto_boundary_and_validation_standard
```

## Controller Service UseCase Transaction Standard since 000050

`000050_springmaster_controller_service_usecase_transaction_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.11-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the canonical Springmaster controller, service, query service, command service, use-case handler and transaction-boundary standard before Catalog-demo becomes the reference implementation.
* It converts the high-priority controller/service/use-case finding from `000047_springmaster_real_app_pattern_forensics` into concrete rules for thin controllers, service-style selection, transaction ownership, repository boundaries, mapper boundaries, security-placement expectations and future architecture gates.
* It references the endpoint, error and DTO/validation standards from 000046 through 000049 without changing Java code.
* It does not introduce Java interfaces, service base classes, reflection scans, OpenAPI tests, MockMvc helpers, ArchUnit rules or Maven-bound gates yet; those belong to later Core/Gate patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.11-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000050_springmaster_controller_service_usecase_transaction_standard
```

## Domain Entity and Persistence Standard since 000051

`000051_springmaster_domain_entity_persistence_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.12-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the canonical Springmaster domain entity and persistence standard before Catalog-demo becomes the reference implementation.
* It converts the high-priority persistence finding from `000047_springmaster_real_app_pattern_forensics` into concrete rules for `DomainEntity`, opaque IDs, business-key separation, repository boundaries, audit fields, optimistic locking, delete/lifecycle implications, metadata deferral, tag usage and NumberSequence deferral.
* It references the controller/service/use-case/transaction standard from 000050 without changing Java code.
* It does not introduce Java entities, repositories, Spring Data dependencies, Liquibase changes, test utilities, reflection scans, ArchUnit rules or Maven-bound gates yet; those belong to later Core/Gate patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.12-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000051_springmaster_domain_entity_persistence_standard
```

## Security and Permission Boundary Standard since 000052

`000052_springmaster_security_permission_boundary_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.13-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the canonical Springmaster security and permission boundary standard before Catalog-demo becomes the reference implementation.
* It converts the high-priority security finding from `000047_springmaster_real_app_pattern_forensics` into concrete rules for endpoint classification, permission naming, role-to-permission mapping, authorization placement, `@PreAuthorize` usage, current-user/capability endpoints, audit-current-user interaction and future gates.
* It integrates with the API error standard from 000048, the controller/service/use-case/transaction standard from 000050 and the domain/persistence audit boundary from 000051 without changing Java code.
* It does not introduce Spring Security configuration, JWT mapping, Java permission catalogs, test fixtures, role persistence, migrations, reflection scans, ArchUnit rules or Maven-bound gates yet; those belong to later Core/Gate patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.13-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000052_springmaster_security_permission_boundary_standard
```



## Command and Relationship Endpoint Standard since 000053

`000053_springmaster_command_relationship_endpoint_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.14-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the canonical Springmaster command and relationship endpoint standard before Catalog-demo becomes the reference implementation.
* It specializes the endpoint and command HTTP standards for state transitions, resource commands, collection commands, relationship reads, assignment-style APIs, bulk relationship changes, nested aggregate commands, command DTOs, permission mapping, transaction/audit expectations and future gates.
* It integrates with the endpoint standard from 000046, the error standard from 000048, the DTO/validation standard from 000049, the controller/service/use-case/transaction standard from 000050, the domain/persistence standard from 000051 and the security/permission standard from 000052 without changing Java code.
* It does not introduce Java command DTOs, controllers, services, security configuration, OpenAPI tests, MockMvc helpers, reflection scans, ArchUnit rules or Maven-bound gates yet; those belong to later Core/Gate patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.14-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000053_springmaster_command_relationship_endpoint_standard
```


## Mapping Standard since 000054

`000054_springmaster_mapping_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.15-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the canonical Springmaster mapping standard before Catalog-demo becomes the reference implementation.
* It covers mapper responsibility, MapStruct versus manual mapping, mapper placement, naming conventions, DTO role mapping, entity mapping, relationship mapping, metadata/audit visibility, validation boundaries, transaction/security boundaries, Catalog-demo readiness and future mapping gates.
* It integrates with the DTO/validation standard from 000049, the controller/service/use-case/transaction standard from 000050, the domain/persistence standard from 000051, the security/permission standard from 000052 and the command/relationship endpoint standard from 000053 without changing Java code.
* It does not introduce Java mappers, MapStruct dependencies, Maven configuration, generated mapper interfaces, ArchUnit rules, OpenAPI tests, MockMvc helpers or target-project changes yet; those belong to later Core/Gate patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.15-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000054_springmaster_mapping_standard
```

## API Contract Gate Concept since 000055

`000055_springmaster_api_contract_gate_concept` increases the overall platform version to `PLATFORM_VERSION=0.13.16-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the first canonical Springmaster gate concept for making documented API standards mechanically verifiable before Catalog-demo becomes the reference implementation.
* It covers OpenAPI contract gates, MockMvc behavior gates, Java boundary scans, security gates, Catalog-demo reference proof, later target comparison and gate maturity levels.
* It integrates with the API, DTO, error, endpoint, command/relationship, controller/service/use-case/transaction, domain/persistence, security/permission and mapping standards from 000044 through 000054 without changing Java code.
* It does not introduce Java test utilities, OpenAPI parsers, Maven profiles, ArchUnit rules, Spring Boot tests, Catalog-demo implementation or target-project changes yet; those belong to later Core/Gate/Demo patches.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.16-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000055_springmaster_api_contract_gate_concept
```

## Catalog-demo Readiness Plan since 000056

`000056_springmaster_catalog_demo_readiness_plan` increases the overall platform version to `PLATFORM_VERSION=0.13.17-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines the readiness plan for making Catalog-demo a canonical Springmaster reference implementation.
* It connects the standards from 000044 through 000055 to concrete CatalogItem readiness criteria for endpoints, DTOs, validation, errors, controller/service/transaction boundaries, persistence, security classification, mapping and gates.
* It explicitly distinguishes mandatory first-slice behavior from deferred topics such as complex search, delete-multiple, state transitions, relationships, metadata persistence, NumberSequence, implemented security and target-project comparison.
* It does not introduce Java code, Catalog-demo implementation, OpenAPI helpers, MockMvc tests, Maven profiles, Tooling changes, Template changes, Core changes or target-project changes.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.17-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000056_springmaster_catalog_demo_readiness_plan
```


## Standard Consistency and ADR Gap Review since 000057

`000057_springmaster_standard_consistency_and_adr_gap_review` increases the overall platform version to `PLATFORM_VERSION=0.13.18-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It performs a forensic consistency review of the standards created from `000044` through `000056` before the first API contract gate tooling seed.
* It identifies blocking P0 gaps such as `sort` versus `sortBy`, `/all` versus `/options`/`/reference-data`, OpenAPI naming, error operational semantics, test strategy and ADR coverage.
* It creates an ADR backlog under `PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md` without accepting those ADRs yet.
* It documents interface and test-utility candidates but does not implement Java contracts, OpenAPI helpers, MockMvc utilities, reflection scans, ArchUnit rules, Maven profiles, Catalog-demo code or target-project changes.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.18-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000057_springmaster_standard_consistency_and_adr_gap_review
```



## API Query and Reference Data Consistency Standard since 000058

`000058_springmaster_api_query_reference_data_consistency_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.19-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It resolves the first P0 consistency gap from `000057_springmaster_standard_consistency_and_adr_gap_review`.
* It makes `sortBy` the canonical Springmaster sorting parameter for new reference APIs and treats `sort` as legacy/target-comparison vocabulary.
* It originally harmonizes `/all`, `/options` and `/reference-data` by treating ambiguous `/all` as non-canonical, `/options` as the bounded selector endpoint and `/reference-data` as ADR-backed semantics. This historical rule is amended by `000091_springmaster_list_query_export_all_contract`: `/all` is canonical when it is an explicit complete-result-set endpoint for frontend export, backend batch or integration consumers and uses the same documented filters, sorting, security and data-scope predicates as the paged list without public `page`/`size` truncation.
* It updates the API, Catalog-demo readiness, ADR-gap and consistency-review documentation so the first API contract gate tooling seed can rely on a stable query/reference-data vocabulary.
* It does not introduce Java code, OpenAPI helpers, MockMvc tests, Maven profiles, Tooling changes, Template changes, Core changes, Demo implementation or target-project changes.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.19-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000058_springmaster_api_query_reference_data_consistency_standard
```


## API Error Identity and Statuscode Consistency Standard since 000059

`000059_springmaster_api_error_identity_and_statuscode_consistency_standard` increases the overall platform version to `PLATFORM_VERSION=0.13.20-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It resolves the error identity and status-code narrowing gaps from `000057_springmaster_standard_consistency_and_adr_gap_review`.
* It defines the distinction between `errorId`, `correlationId`, `traceId`, `messageKey`, `message` and `localMessage`.
* It narrows first-slice status defaults for create, update, single delete, delete-multiple, state commands and asynchronous commands.
* It updates API, Catalog-demo readiness, ADR-gap and consistency-review documentation so the first API contract gate tooling seed can rely on stable error/status behavior.
* It does not introduce Java code, OpenAPI helpers, MockMvc tests, Maven profiles, Tooling changes, Template changes, Core changes, Demo implementation or target-project changes.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.20-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000059_springmaster_api_error_identity_and_statuscode_consistency_standard
```


## ADR Governance and Backlog Alignment since 000060

`000060_springmaster_adr_governance_and_backlog_alignment` increases the overall platform version to `PLATFORM_VERSION=0.13.21-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It defines ADR governance, ADR status semantics, ADR template requirements and standards-to-ADR mapping.
* It aligns the ADR backlog with priority, planning status and tooling blocker classes.
* It marks the first P0 ADRs as ready-to-draft before strict API contract gate tooling or Catalog-demo canonicalization.
* It does not introduce Java code, OpenAPI helpers, MockMvc tests, Maven profiles, shell tooling, templates, demo implementation or target-project changes.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.21-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000060_springmaster_adr_governance_and_backlog_alignment
```



## ADR-0002 API Boundary and Endpoint Contract since 000061

`000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` increases the overall platform version to `PLATFORM_VERSION=0.13.22-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It creates accepted `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md`.
* It consolidates API endpoint, DTO, validation, query/reference-data, error, command and first-slice status-code standards as an accepted architecture decision for new Springmaster reference APIs.
* It updates the ADR index, ADR gap backlog, ADR governance, standards index, consistency review and implementation plan.
* It does not introduce Java code, OpenAPI helpers, MockMvc tests, Maven profiles, shell tooling, templates, demo implementation or target-project changes.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.22-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000061_springmaster_adr_0002_api_boundary_and_endpoint_contract
```



## ADR-0006 Verification and Gate Strategy since 000062

`000062_springmaster_adr_0006_verification_and_gate_strategy` increases the overall platform version to `PLATFORM_VERSION=0.13.23-foundation` and leaves all implementation sub-versions unchanged.

Reasoning:

* The patch changes documentation and version metadata only.
* It creates accepted `PROJECT_DOCS/ADR/ADR-0006-verification-and-gate-strategy.md`.
* It defines gate layers, execution modes, severity vocabulary, report structure, future Maven profile names and target-comparison policy as an accepted architecture decision.
* It updates the ADR index, ADR gap backlog, ADR governance, gate concept, standards review and implementation plan.
* It does not introduce Java code, OpenAPI helpers, MockMvc tests, Maven profiles, shell tooling, templates, demo implementation or target-project changes.
* Existing IDM, Personnel, Contacts, Orders or other target projects are not changed or supplied by this patch.
* Core, Tooling, Template, Demo and Platform-Update implementation versions remain unchanged because no Java code, shell tooling, templates, demo code or update tooling are changed.

```text
PLATFORM_VERSION=0.13.23-foundation
PLATFORM_CORE_VERSION=0.3.2
PLATFORM_TOOLING_VERSION=0.3.7
PLATFORM_TEMPLATE_VERSION=0.1.0
PLATFORM_DEMO_VERSION=0.2.1
PLATFORM_UPDATE_VERSION=0.8.0
PLATFORM_STATE_PATCH=000062_springmaster_adr_0006_verification_and_gate_strategy
```

## Versionierter Stand nach 000063

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.24-foundation
PLATFORM_STATE_PATCH=000063_springmaster_adr_0003_application_layer_transaction_boundary
```

Begründung:

* ADR-0003 wird als Accepted ADR eingeführt.
* Controller-, Service-, UseCase-, Repository-, Mapper- und Transaction-Boundaries sind nun ADR-backed.
* Die Änderung ist documentation-only und verändert keine Core-, Tooling-, Template-, Demo- oder Update-Codeartefakte.
* Die Teilversionen für Core, Tooling, Template, Demo und Platform-Update bleiben unverändert.




## Versionierter Stand nach 000064

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.25-foundation
PLATFORM_STATE_PATCH=000064_springmaster_adr_0004_persistence_identity_domainentity_strategy
```

Begründung:

* ADR-0004 wird als Accepted ADR eingeführt.
* Persistence Identity, `DomainEntity`, Business Keys, `persistenceVersion`, technische Audit-Felder und Repository-Boundary sind nun ADR-backed.
* Die Änderung ist documentation-only und verändert keine Core-, Tooling-, Template-, Demo- oder Update-Codeartefakte.
* Die Teilversionen für Core, Tooling, Template, Demo und Platform-Update bleiben unverändert.

## Versionierter Stand nach 000065

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.26-foundation
PLATFORM_STATE_PATCH=000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy
```

Begründung:

* ADR-0007 wird als Accepted ADR eingeführt.
* Catalog-demo canonicalization states, evidence requirements, accepted deferrals and target-comparison boundary are now ADR-backed.
* Die Änderung ist documentation-only und verändert keine Core-, Tooling-, Template-, Demo- oder Update-Codeartefakte.
* Die Teilversionen für Core, Tooling, Template, Demo und Platform-Update bleiben unverändert.

## Versionierter Stand nach 000066

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.27-foundation
PLATFORM_STATE_PATCH=000066_springmaster_adr_0005_security_and_permission_boundary
```

Begründung:

* ADR-0005 wird als Accepted ADR eingeführt.
* Security Classification, Permission Naming, Role-to-Permission Mapping, Authorization Placement, Current-User-/Capability-Boundaries und Catalog-demo Security Evidence sind nun ADR-backed.
* Die Änderung ist documentation-only und verändert keine Core-, Tooling-, Template-, Demo- oder Update-Codeartefakte.
* Die Teilversionen für Core, Tooling, Template, Demo und Platform-Update bleiben unverändert.

## Versionierter Stand nach 000067

Patch `000067_springmaster_report_only_gate_seed_plan` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.28-foundation
PLATFORM_STATE_PATCH=000067_springmaster_report_only_gate_seed_plan
```

Begründung:

* Der erste report-only Gate Seed wird fachlich planbar und versioniert.
* Accepted ADRs werden in konkrete Gate IDs, Rule Sources, Report-Dateien, Finding Schema und Exit-Verhalten überführt.
* Die Änderung ist documentation-only und verändert keine Core-, Tooling-, Template-, Demo- oder Update-Codeartefakte.
* Die Teilversionen für Core, Tooling, Template, Demo und Platform-Update bleiben unverändert.

## Versionierter Stand nach 000068

Patch `000068_springmaster_report_only_gate_tooling_seed` erhöht den Foundation- und Tooling-Stand auf:

```text
PLATFORM_VERSION=0.13.29-foundation
PLATFORM_TOOLING_VERSION=0.3.8
PLATFORM_STATE_PATCH=000068_springmaster_report_only_gate_tooling_seed
```

Begründung:

* Der erste ausführbare report-only Gate Runner wird eingeführt.
* Das Tooling erhält neue Wrapper- und Selfcheck-Skripte unter `bin/**`.
* Der Runner erzeugt die ADR-gestützte Report-Struktur unter `target/springmaster-gates/<gate-run-id>/`.
* Die Änderung betrifft Tooling-Code und Tooling-Dokumentation, aber keinen Core-Code, keine Templates, keine Demo-Fachimplementierung, keine Platform-Update-Mechanik und keine Zielprojekte.
* Deshalb wird `PLATFORM_TOOLING_VERSION` erhöht; Core, Template, Demo und Platform-Update-Version bleiben unverändert.


## Versionierter Stand nach 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` erhöht den Foundation- und Tooling-Stand auf:

```text
PLATFORM_VERSION=0.13.30-foundation
PLATFORM_TOOLING_VERSION=0.3.9
PLATFORM_STATE_PATCH=000069_springmaster_report_only_gate_regression_and_maven_profile
```

Begründung:

* Der report-only Gate Runner erhält eine Regression-Suite.
* Die Reportstruktur erhält den stabilen Schema-Marker `springmaster.report-only-report.v1`.
* Maven-Profil `springmaster-gates-report` wird eingeführt.
* Die Änderung betrifft Tooling-Code, Tests und Tooling-Dokumentation, aber keinen Core-Code, keine Templates, keine Demo-Fachimplementierung, keine Platform-Update-Mechanik und keine Zielprojekte.
* Deshalb wird `PLATFORM_TOOLING_VERSION` erhöht; Core, Template, Demo und Platform-Update-Version bleiben unverändert.

## Versionierter Stand nach 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.31-foundation
PLATFORM_TOOLING_VERSION=0.3.9
PLATFORM_STATE_PATCH=000070_springmaster_report_only_gate_findings_baseline_review
```

Begründung:

* Der erste report-only Gate-Findings-Stand wird forensisch klassifiziert.
* Die Änderung ist documentation-only und verändert kein Gate-Tooling, keine Tests, kein Maven-Profil, keinen Core-Code, keine Templates, keine Demo-Fachimplementierung, keine Platform-Update-Mechanik und keine Zielprojekte.
* Deshalb bleibt `PLATFORM_TOOLING_VERSION` unverändert; nur `PLATFORM_VERSION` und `PLATFORM_STATE_PATCH` werden fortgeschrieben.

## Versionierter Stand nach 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.32-foundation
PLATFORM_TOOLING_VERSION=0.3.9
PLATFORM_STATE_PATCH=000071_springmaster_catalog_demo_candidate_slice_contract_plan
```

Begründung:

* Der Catalog-demo Candidate Slice Contract Plan wird dokumentiert.
* Die Änderung übersetzt die report-only Gate Findings aus 000070 in einen konkreten CatalogItem Candidate-Slice-Arbeitsplan.
* Die Änderung ist documentation-only und verändert kein Gate-Tooling, keine Tests, kein Maven-Profil, keinen Core-Code, keine Templates, keine Demo-Fachimplementierung, keine Platform-Update-Mechanik und keine Zielprojekte.
* Deshalb bleibt `PLATFORM_TOOLING_VERSION` unverändert; nur `PLATFORM_VERSION` und `PLATFORM_STATE_PATCH` werden fortgeschrieben.



## Versionierter Stand nach 000072

Patch `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation` erhöht den Foundation- und Demo-Stand auf:

```text
PLATFORM_VERSION=0.13.33-foundation
PLATFORM_DEMO_VERSION=0.2.2
PLATFORM_STATE_PATCH=000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation
```

Begründung:

* Der Patch verändert Demo Java/API-Verhalten, Demo-Tests und CatalogItem Candidate-Slice-Evidence.
* Der Patch verändert keinen Core-Code, kein Gate-Tooling, keine Templates, keine Platform-Update-Mechanik und keine Zielprojekte.
* Deshalb wird `PLATFORM_DEMO_VERSION` erhöht; Core, Tooling, Template und Platform-Update-Version bleiben unverändert.

## Versionierter Stand nach 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.34-foundation
PLATFORM_DEMO_VERSION=0.2.2
PLATFORM_TOOLING_VERSION=0.3.9
PLATFORM_STATE_PATCH=000073_springmaster_catalog_demo_candidate_slice_forensic_review
```

Begründung:

* Der Patch ist documentation-only und bewertet den Demo-Code-Slice aus `000072` forensisch gegen ADRs, Standards und report-only Gate Findings.
* Es werden keine Java-, Maven-, Tooling-, Template-, Platform-Update- oder Zielprojektdateien geändert.
* Deshalb bleiben `PLATFORM_DEMO_VERSION`, `PLATFORM_TOOLING_VERSION`, Core, Template und Platform-Update-Version unverändert; nur `PLATFORM_VERSION` und `PLATFORM_STATE_PATCH` werden fortgeschrieben.



## Versionierter Stand nach 000074

Patch `000074_springmaster_catalog_demo_candidate_slice_alignment` erhöht den Foundation- und Tooling-Stand auf:

```text
PLATFORM_VERSION=0.13.35-foundation
PLATFORM_TOOLING_VERSION=0.3.10
PLATFORM_DEMO_VERSION=0.2.2
PLATFORM_STATE_PATCH=000074_springmaster_catalog_demo_candidate_slice_alignment
```

Begründung:

* Der Patch verändert report-only Gate-Tooling, Gate-Regression, Gate-Selfcheck und Tooling-Dokumentation.
* Zusätzlich wird machine-readable CatalogItem Candidate Evidence unter `PROJECT_DOCS/DEMO` ergänzt.
* Die Demo-Java-Fachimplementierung bleibt unverändert; deshalb bleibt `PLATFORM_DEMO_VERSION=0.2.2`.
* Core, Template und Platform-Update-Version bleiben unverändert.

## Versionierter Stand nach 000075

Patch `000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup` advances Springmaster to `PLATFORM_VERSION=0.13.36-foundation` and Demo to `PLATFORM_DEMO_VERSION=0.2.3`.

The patch is a Demo-code cleanup for the CatalogItem candidate-reference-slice. Tooling remains `PLATFORM_TOOLING_VERSION=0.3.10`; Core remains `PLATFORM_CORE_VERSION=0.3.2`.

## Versionierter Stand nach 000076

Patch `000076_springmaster_project_new_instantiation_acceptance_review` erhöht den Foundation- und Tooling-Stand auf:

```text
PLATFORM_VERSION=0.13.37-foundation
PLATFORM_TOOLING_VERSION=0.3.11
PLATFORM_DEMO_VERSION=0.2.3
PLATFORM_STATE_PATCH=000076_springmaster_project_new_instantiation_acceptance_review
```

Begründung:

* Der Patch verändert `project-new.sh`, ergänzt `bin/project-new-acceptance.sh` und fügt eine JUnit-Acceptance für die Projektinstanziierung hinzu.
* Das Demo-Fachmodell bleibt unverändert; deshalb bleibt `PLATFORM_DEMO_VERSION=0.2.3`.
* Core, Template und Platform-Update-Version bleiben unverändert.
* Die Änderung ist ein Tooling-/Acceptance-Patch und erhöht deshalb `PLATFORM_TOOLING_VERSION`.


## Versionierter Stand nach 000077

Patch `000077_springmaster_generated_service_slice_readiness_plan` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.38-foundation
PLATFORM_TOOLING_VERSION=0.3.11
PLATFORM_DEMO_VERSION=0.2.3
PLATFORM_STATE_PATCH=000077_springmaster_generated_service_slice_readiness_plan
```

Begründung:

* Der Patch ist documentation-only und definiert die Readiness-Brücke von Project-New zu einem später generated fachlichen Service-Slice.
* Es werden keine Java-, Maven-, Shell-Tooling-, Template-, Demo-Code-, Core-, Platform-Update- oder Zielprojektdateien geändert.
* Deshalb bleiben `PLATFORM_TOOLING_VERSION`, `PLATFORM_DEMO_VERSION`, Core, Template und Platform-Update-Version unverändert; nur `PLATFORM_VERSION` und `PLATFORM_STATE_PATCH` werden fortgeschrieben.

## Versionierter Stand nach 000078

Patch `000078_springmaster_generated_service_slice_readiness_marker_alignment` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.39-foundation
PLATFORM_TOOLING_VERSION=0.3.11
PLATFORM_DEMO_VERSION=0.2.3
PLATFORM_STATE_PATCH=000078_springmaster_generated_service_slice_readiness_marker_alignment
```

Begründung:

* Der Patch ist documentation-only und korrigiert ausschließlich die Marker-Kompatibilität der `000077`-Readiness-Dokumentation.
* Der Kontrollbegriff `technical Backend-Skeleton` wird im Readiness-Plan explizit dokumentiert, damit Acceptance-/Verify-Skripte stabil gegen den fachlich bereits beschriebenen Zustand prüfen können.
* Der geplante Blueprint-Patch wird auf `000079` verschoben, weil `000078` als Korrekturpatch verwendet wird.
* Es werden keine Java-, Maven-, Shell-Tooling-, Template-, Demo-Code-, Core-, Platform-Update- oder Zielprojektdateien geändert.
* Deshalb bleiben `PLATFORM_TOOLING_VERSION`, `PLATFORM_DEMO_VERSION`, Core, Template und Platform-Update-Version unverändert; nur `PLATFORM_VERSION` und `PLATFORM_STATE_PATCH` werden fortgeschrieben.




## Versionierter Stand nach 000079

Patch `000079_springmaster_zbm_target_registry_and_lifecycle_alignment` erhöht den Foundation- und Platform-Update-Stand auf:

```text
PLATFORM_VERSION=0.13.40-foundation
PLATFORM_UPDATE_VERSION=0.8.1
PLATFORM_STATE_PATCH=000079_springmaster_zbm_target_registry_and_lifecycle_alignment
```

Begründung:

* Der Patch ändert die Target Registry und Platform-Update-Dokumentation auf den ersten geplanten Zielnamen `zbm`.
* Bestehende/running Projekte `idm` und `personnel` werden explizit als nicht belieferbar zurückgestellt.
* Target-Deskriptoren unterscheiden Initialisierung und Update; realer `target-apply` wird durch `TARGET_DELIVERY_ENABLED=true` abgesichert.
* Die Platform-Update-Mechanik erhält das Update-Profil `defaults` für Basis-Konfigurationsdefaults.
* Es werden keine Java-, Maven-, Core-, Demo- oder Template-Dateien verändert.
* Deshalb wird `PLATFORM_UPDATE_VERSION` erhöht; Core-, Demo-, Template- und Tooling-Versionen bleiben unverändert.

Der ursprünglich für `000079` geplante generated-service-slice Blueprint wird auf `000080_springmaster_generated_service_slice_blueprint_spec` verschoben, weil vor dem Generator-Schritt die Zielprojektstrategie (`zbm`, Initialisierung vs. Update, keine Lieferung an IDM/Personnel) festgeschrieben wird.

## Versionierter Stand nach 000080

Patch `000080_springmaster_generated_service_slice_blueprint_spec` erhöht den Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.41-foundation
PLATFORM_UPDATE_VERSION=0.8.1
PLATFORM_STATE_PATCH=000080_springmaster_generated_service_slice_blueprint_spec
```

Begründung:

* Der Patch ist documentation-only und spezifiziert den Generated-Service-Slice-Blueprint sowie den ZBM-Initialisierungskonzepttest.
* Es werden keine Java-, Maven-, Shell-Tooling-, Core-, Demo-, Template-, Platform-Update- oder Zielprojektdateien verändert.
* Deshalb bleiben `PLATFORM_UPDATE_VERSION`, `PLATFORM_TOOLING_VERSION`, `PLATFORM_DEMO_VERSION`, Core und Template unverändert; nur `PLATFORM_VERSION` und `PLATFORM_STATE_PATCH` werden fortgeschrieben.


## Versionierter Stand nach 000081

Patch `000081_springmaster_zbm_core_source_copy_acceptance` erhöht den Foundation- und Platform-Update-Stand auf:

```text
PLATFORM_VERSION=0.13.42-foundation
PLATFORM_UPDATE_VERSION=0.8.2
PLATFORM_STATE_PATCH=000081_springmaster_zbm_core_source_copy_acceptance
```

Begründung:

* Der Patch verändert `bin/platform-update.sh`, damit generierte Core-Patches scope-kompatible Review-Dokumente unter `PROJECT_DOCS/CORE/PLATFORM_UPDATES/**` erzeugen.
* Für `core` und `core-runtime` wird eine target-lokale `pom.xml` synthetisiert, die die minimal notwendigen Core-Compile-Abhängigkeiten ohne DataSource-Autokonfiguration ergänzt, ohne die Springmaster-Master-`pom.xml` zu kopieren.
* Zusätzlich wird die ZBM Core Source-Copy Acceptance dokumentiert.
* Es werden keine Springmaster-Java-, Demo-, Template- oder Core-Quellcodedateien geändert.
* Deshalb wird `PLATFORM_UPDATE_VERSION` erhöht; Core-, Demo-, Template- und Tooling-Versionen bleiben unverändert.



## Versionierter Stand nach 000082

Patch `000082_springmaster_patch_runtime_locking_background_git_rollback` erhöht die Tooling-Version auf `0.3.12` und die Plattform-Version auf `0.13.43-foundation`.

Grund ist die Härtung der portablen Patch-Runtime: projektweiter Write-Lock, `--background`/`--wait`, projektlokal konfigurierbare Test-/Exportkommandos, kompakte Summary-Dateien, patchbezogene Git-Commit-Skripte und ein Fixture-Test für Apply-/Rollback-/Lock-Szenarien.



## Versionierter Stand nach 000093

Patch `000093_springmaster_paged_query_support_sort_allowlist_tiebreaker` erhöht den Core- und Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.46-foundation
PLATFORM_CORE_VERSION=0.3.3
PLATFORM_STATE_PATCH=000093_springmaster_paged_query_support_sort_allowlist_tiebreaker
```

Begründung:

* Der Patch erweitert `PagedQuerySupport` als wiederverwendbaren Core-API-Baustein für Management-Listen.
* Die neue Core-Funktionalität validiert öffentliche Sort-Allowlists, löst Default-Sort-Felder auf und erzeugt stabile Sortierungen beziehungsweise Comparatoren mit explizitem Tie-Breaker.
* Der Core bleibt fachfrei: Sort-Felder, fachliche Comparatoren und Tie-Breaker werden von Fachmodulen oder generierten Service-Slices übergeben.
* Es werden keine Demo-, Tooling-, Template- oder Platform-Update-Versionen erhöht.


## `/all` Contract Documentation Consistency Sweep since 000097

`000097_springmaster_all_contract_documentation_consistency_sweep` is documentation-only and does not change platform version metadata.

Reasoning:

* It aligns historical readiness, ADR-gap, standards and gate-planning documents with the current `000091` decision that `/all` is canonical only as an explicit complete-result-set contract.
* It preserves the historical meaning of older findings: ambiguous, selector-like, undocumented or silently capped `/all` endpoints remain non-canonical.
* It clarifies that CatalogItem candidate evidence from `000092` and `000094` now includes `/all` as export/batch/integration result-set evidence while Catalog-demo itself remains `candidate-reference-slice`, not canonical.
* It changes documentation only; Core, Tooling, Template, Demo implementation and Platform-Update versions remain unchanged.




## Versionierter Stand nach 000099

Patch `000099_springmaster_count_response_dto_core_candidate` erhöht den Core- und Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.47-foundation
PLATFORM_CORE_VERSION=0.3.4
PLATFORM_STATE_PATCH=000099_springmaster_count_response_dto_core_candidate
```

Begründung:

* Der Patch führt `CountResponseDTO` als neuen fachfreien Core-API-DTO-Baustein ein.
* Der DTO setzt den in `000098_springmaster_count_response_contract_candidate` dokumentierten Count-only-Response-Shape `{ "totalElements": 0 }` im Core um.
* Negative Count-Werte werden auf DTO-Ebene verhindert; Filter-, Sortier-, Security-, Data-Scope- und Persistenzsemantik bleiben außerhalb des DTO.
* Demo-, Tooling-, Template- und Platform-Update-Versionen bleiben unverändert.


## Versionierter Stand nach 000100

Patch `000100_springmaster_catalogitem_count_reference_slice` erhöht den Demo- und Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.48-foundation
PLATFORM_DEMO_VERSION=0.2.4
PLATFORM_STATE_PATCH=000100_springmaster_catalogitem_count_reference_slice
```

Begründung:

* Der Patch ergänzt den CatalogItem-Candidate-Slice um `GET /api/demo/catalog/items/count`.
* Die Response nutzt den Core-DTO-Baustein `CountResponseDTO` aus `000099`.
* Der Count nutzt dieselben Filterprädikate wie paginierte Liste und `/all`, aber keine Sortier- oder Paging-Semantik.
* Core-, Tooling-, Template- und Platform-Update-Versionen bleiben unverändert.

## Patch 000101: Query Operations Interface Contract Core

Patch `000101_springmaster_query_operations_interface_contract_core` erhöht die Core-Version auf `0.3.5` und die Platform-Version auf `0.13.49-foundation`.

Grund der Erhöhung ist die Einführung einer fachfreien Java-Vertragsfläche für kanonische Query-Operationen unter `de.cocondo.system.query`:

```text
PagedResultSetQuery
CompleteResultSetQuery
CountResultSetQuery
ResultSetQueryOperations
```

Die Änderung betrifft ausschließlich Core-Contracts. Eine Demo-Adoption erfolgt separat, damit Core- und Demo-Scope weiterhin sauber getrennt bleiben.

```text
PLATFORM_VERSION=0.13.49-foundation
PLATFORM_CORE_VERSION=0.3.5
PLATFORM_STATE_PATCH=000101_springmaster_query_operations_interface_contract_core
```



## Versionierter Stand nach 000102

Patch `000102_springmaster_catalogitem_query_operations_interface_adoption` erhöht den Demo- und Foundation-Stand auf:

```text
PLATFORM_VERSION=0.13.50-foundation
PLATFORM_DEMO_VERSION=0.2.5
PLATFORM_STATE_PATCH=000102_springmaster_catalogitem_query_operations_interface_adoption
```

Begründung:

* Der Patch adaptiert die Core-Query-Operations-Interfaces aus `000101` im CatalogItem-Candidate-Slice.
* `CatalogItemService` implementiert `ResultSetQueryOperations<CatalogItemPagedQuery, CatalogItemAllQuery, CatalogItemCountQuery, CatalogItemListItemDTO>`.
* Die fachlichen Query-Records bleiben im Demo-Slice; der Core bleibt frei von CatalogItem-Fachlichkeit und Spring-MVC-Mapping.
* Der Controller bleibt expliziter HTTP-Adapter und delegiert in fachliche Query-Typen.
* Core-, Tooling-, Template- und Platform-Update-Versionen bleiben unverändert.




## Query Operations Contract Closure Review since 000103

`000103_springmaster_query_operations_contract_closure_review` is documentation-only and does not change platform version metadata.

Reasoning:

* It records the closure state after `000098` through `000102` for paged list, complete-result-set `/all`, count-only `/count`, Core query-operation interfaces and CatalogItem service adoption.
* It clarifies that Springmaster standardizes typed service/application query contracts, not generic Spring-MVC controller inheritance.
* It separates closed candidate-level Query Operations evidence from remaining canonical blockers such as durable persistence, Liquibase, implemented security, OpenAPI evidence, strict gates, async export and target-project comparison.
* No Core, Demo, Tooling, Template or Platform-Update runtime version is changed.



## JPA Count Query Efficiency Reference since 000105

`000105_springmaster_jpa_count_query_efficiency_reference` is documentation-only and does not change platform version metadata.

Reasoning:

* It documents how persistent JPA-backed query slices should compute `PagedResponseDTO.totalElements` and count-only endpoint values efficiently.
* It does not change Core Java code, Demo runtime behavior, Tooling, Template or Platform-Update artifacts.
* The CatalogItem candidate slice remains in-memory; durable persistence evidence is still a later milestone.


## Query Contract Gate Report since 000106

`000106_springmaster_query_contract_gate_report` is documentation-only and does not change platform version metadata.

Reasoning:

* It defines the report-only JSON artifact, rule IDs and finding schema for future query-contract diagnostics.
* It does not add executable gate tooling, Maven profiles, Core code, Demo runtime behavior, Templates, Platform-Update artifacts or target-project changes.
* Strict enforcement remains deferred until a later ADR-0006-aligned gate implementation patch.

## Query Contract Report Tooling MVP since 000107

Patch `000107_springmaster_query_contract_report_tooling_mvp` advances the executable Tooling and Foundation versions:

```text
PLATFORM_VERSION=0.13.51-foundation
PLATFORM_TOOLING_VERSION=0.3.17
PLATFORM_STATE_PATCH=000107_springmaster_query_contract_report_tooling_mvp
```

Reasoning:

* It turns the report-only query-contract concept from `000106` into an executable MVP.
* It adds a deterministic source-based report generator for the CatalogItem candidate reference slice.
* It produces a machine-readable JSON report with stable schema, resource summary and findings list.
* It keeps the report mode non-strict; findings remain review evidence and do not fail builds by themselves.
* It does not change Core runtime contracts, Demo runtime behavior, Templates, Platform-Update artifacts or target-project delivery.

## CatalogItem query report golden fixture since 000108

Patch `000108_springmaster_catalogitem_query_contract_report_fixture` advances the Tooling and Foundation versions:

```text
PLATFORM_VERSION=0.13.52-foundation
PLATFORM_TOOLING_VERSION=0.3.18
PLATFORM_STATE_PATCH=000108_springmaster_catalogitem_query_contract_report_fixture
```

Reasoning:

* It stabilizes the executable query-contract reporter from `000107` with a committed CatalogItem golden JSON fixture.
* It converts the query-contract report regression from substring smoke evidence into byte-for-byte expected-output evidence.
* It does not change Core runtime contracts, Demo runtime behavior, Templates, Platform-Update artifacts or target-project delivery.

## CatalogItem OpenAPI query-contract evidence since 000109

Patch `000109_springmaster_query_openapi_contract_evidence` advances the Foundation version:

```text
PLATFORM_VERSION=0.13.53-foundation
PLATFORM_STATE_PATCH=000109_springmaster_query_openapi_contract_evidence
```

Reasoning:

* It adds runtime-generated OpenAPI evidence for the CatalogItem query-contract reference slice.
* It verifies that `/api-docs` exposes the paged list, `/all` and `/count` query vocabulary consistently.
* It verifies that `/count` exposes the `CountResponseDTO.totalElements` schema contract.
* It does not change Core runtime contracts, Demo runtime behavior, Tooling command behavior, Templates, Platform-Update artifacts or target-project delivery.

## OpenAPI api-docs path alignment since 000109a

Patch `000110_springmaster_query_openapi_contract_evidence_api_docs_path_fix` advances the Foundation version:

```text
PLATFORM_VERSION=0.13.54-foundation
PLATFORM_STATE_PATCH=000110_springmaster_query_openapi_contract_evidence_api_docs_path_fix
```

Reasoning:

* It aligns the CatalogItem OpenAPI evidence test with the project-local Springdoc path configured in `src/main/resources/application.yml`.
* The canonical endpoint for this Springmaster project is `/api-docs`; `/v3/api-docs` is only the Springdoc default and is intentionally not exposed by the current configuration.
* It keeps the OpenAPI evidence goal from `000109` unchanged and only repairs the executable endpoint used by the test and documentation.
* It does not change Core runtime contracts, Demo runtime behavior, Tooling command behavior, Templates, Platform-Update artifacts or target-project delivery.



## CatalogItem OpenAPI repair chain since 000111 and 000112

Patches `000111_springmaster_catalogitem_openapi_json_media_type_fix` and `000112_springmaster_query_contract_report_mapping_attribute_fix` repaired the OpenAPI evidence chain introduced by `000109` and aligned the source-based query report parser with named Spring mapping attributes.

Reasoning:

* `000111` makes the CatalogItem query endpoints explicitly produce `application/json` so the OpenAPI contract exposes JSON response schemas deterministically.
* `000112` repairs the report parser so `@GetMapping(path = "...")` and `@GetMapping(value = "...")` are recognized like direct mapping literals.
* These patches are part of the OpenAPI evidence repair chain and do not promote CatalogItem to canonical status.

## CatalogItem persistent JPA count reference since 000113

Patch `000113_springmaster_persistent_jpa_count_reference_slice` advances the Demo and Foundation versions:

```text
PLATFORM_VERSION=0.13.55-foundation
PLATFORM_DEMO_VERSION=0.2.6
PLATFORM_STATE_PATCH=000113_springmaster_persistent_jpa_count_reference_slice
```

Reasoning:

* It adds a compile-time persistent JPA reference for CatalogItem query operations without replacing the in-memory demo runtime.
* It demonstrates a dedicated `CriteriaQuery<Long>` count implementation with shared predicates and without list materialization.
* It records tests that guard the JPA count reference against paging, sorting and DTO-mapping leakage into count semantics.
* It keeps the remaining security/data-scope parity work explicit and deferred to a later patch.


## CatalogItem security/data-scope query parity reference since 000114

Patch `000114_springmaster_query_security_scope_parity_reference` advances the Demo and Foundation versions:

```text
PLATFORM_VERSION=0.13.56-foundation
PLATFORM_DEMO_VERSION=0.2.7
PLATFORM_STATE_PATCH=000114_springmaster_query_security_scope_parity_reference
```

Reasoning:

* It adds a compact CatalogItem query-scope reference with `catalog:item:read` and `allowedSkus` data-scope evidence.
* It proves that paged list, `/all` and `/count` use the same permission/data-scope predicate family before operation-specific behavior.
* It completes the planned five-step Query/List/All/Count maturity track at candidate-reference level.
* It does not enable Spring Security runtime enforcement or promote CatalogItem to canonical status.

## Backend API pattern operational roadmap since 000115

Patch `000115_springmaster_backend_api_pattern_operational_roadmap` records a documentation-only planning state.

Reasoning:

* It persists the forensic prioritization of the remaining backend API pattern work after Query/List/All/Count reached candidate-reference maturity.
* It defines the operative sequence for Global Error Contract, Detail/Lookup, Write API Contract, Request Validation/OpenAPI Gate and Generated Slice Adoption Plan.
* It documents deferred topics so they are not accidentally started before the broader API foundations are closed.
* It does not change Core runtime contracts, Demo runtime behavior, Tooling command behavior, Templates, Platform-Update artifacts or target-project delivery.

## Global API error contract Core since 000116

Patch `000116_springmaster_global_api_error_contract_core` advances the Core and Foundation versions:

```text
PLATFORM_VERSION=0.13.57-foundation
PLATFORM_CORE_VERSION=0.3.6
PLATFORM_STATE_PATCH=000116_springmaster_global_api_error_contract_core
```

Reasoning:

* It establishes reusable System-Core DTOs and a global `@RestControllerAdvice` for the Springmaster API error envelope.
* It prepares the CatalogItem migration but leaves the Demo-scope migration to the next patch.
* It establishes the Core-owned implementation that the next Demo-scope migration must consume.
* It adds targeted Core error tests and keeps Detail/Lookup, Write, Validation/OpenAPI and Generated-Slice adoption as follow-up roadmap items.


## CatalogItem global API error handler migration since 000117

Patch `000117_springmaster_catalogitem_global_api_error_handler_migration` advances the Demo and Foundation versions:

```text
PLATFORM_VERSION=0.13.58-foundation
PLATFORM_DEMO_VERSION=0.2.8
PLATFORM_STATE_PATCH=000117_springmaster_catalogitem_global_api_error_handler_migration
```

Reasoning:

* It consumes the Core global API error contract introduced by `000116` in the CatalogItem Demo slice.
* It removes controller-local error DTOs and local `@ExceptionHandler` methods from CatalogItem.
* It maps CatalogItem not-found and duplicate-SKU failures to Core-owned error handling while preserving domain message keys.
* It keeps Detail/Lookup, Write, Validation/OpenAPI and Generated-Slice adoption as follow-up roadmap items.

## Detail/Lookup contract report since 000118

Patch `000118_springmaster_detail_lookup_contract_report` advances the Tooling and Foundation versions:

```text
PLATFORM_VERSION=0.13.59-foundation
PLATFORM_TOOLING_VERSION=0.3.19
PLATFORM_STATE_PATCH=000118_springmaster_detail_lookup_contract_report
```

Reasoning:

* It adds a report-only Detail/Lookup Contract Gate Report for single-object and alternate-key lookup endpoints.
* It records CatalogItem as the first golden evidence for `GET /api/demo/catalog/items/{id}` and `GET /api/demo/catalog/items/by-sku/{sku}`.
* It verifies detail/lookup route presence, path variables, global `RESOURCE_NOT_FOUND` error behavior and create-`Location` detail consistency through targeted tests.
* It keeps Write, Request Validation/OpenAPI and Generated-Slice adoption as follow-up roadmap items.

## Write API contract report since 000119

Patch `000119_springmaster_write_api_contract_report` advances the Tooling and Foundation versions:

```text
PLATFORM_VERSION=0.13.60-foundation
PLATFORM_TOOLING_VERSION=0.3.20
PLATFORM_STATE_PATCH=000119_springmaster_write_api_contract_report
```

Reasoning:

* It adds a report-only Write API Contract Gate Report for Create/Update/Delete management endpoints.
* It records CatalogItem as the first golden evidence for `POST /api/demo/catalog/items`, `PUT /api/demo/catalog/items/{id}` and bodyless `DELETE /api/demo/catalog/items/{id}`.
* It verifies CreateDTO/UpdateDTO request-body evidence, `201 Created` with `Location`, `200 OK` update responses, `204 No Content` deletes and global error behavior through targeted tests.
* It keeps Request Validation/OpenAPI required-field alignment, generated-slice adoption, bulk commands, state commands and relationship commands as follow-up roadmap items.

## Request Validation/OpenAPI gate since 000120

Patch `000120_springmaster_request_validation_openapi_gate` advances the Tooling and Foundation versions:

```text
PLATFORM_VERSION=0.13.61-foundation
PLATFORM_TOOLING_VERSION=0.3.21
PLATFORM_STATE_PATCH=000120_springmaster_request_validation_openapi_gate
```

Reasoning:

* It adds a report-only Request Validation/OpenAPI Gate Report for DTO-boundary and required-field alignment.
* It records CatalogItem as the first golden evidence for `CatalogItemCreateDTO` and `CatalogItemUpdateDTO` Bean Validation required fields.
* It verifies that OpenAPI required fields are aligned with `@NotBlank` constraints for create and update request bodies.
* It keeps Generated-Slice adoption, strict gate promotion, bulk commands, state commands and relationship commands as follow-up roadmap items.

## Generated Slice API Pattern adoption plan since 000121

Patch `000121_springmaster_generated_slice_api_pattern_adoption_plan` records a documentation-only Tooling/Planning state.

Reasoning:

* It consolidates the completed API pattern families Query, Detail/Lookup, Write, Request Validation/OpenAPI and global Error Contract into a generated-service-slice adoption target.
* It aligns the older generated-service-slice blueprint with the current API surface, including `/all` and `/count` for management-style generated slices.
* It defines the next generator implementation sequence: Slice-Spec Contract, Intermediate Model and Patch-Blueprint Dry-run before any target-project delivery.
* It does not change Core runtime contracts, Demo runtime behavior, Tooling command behavior, Templates, Platform-Update artifacts or target-project delivery.

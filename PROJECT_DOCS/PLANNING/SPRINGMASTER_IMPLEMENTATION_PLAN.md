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

## 3. Leitregeln

* Ein Schritt entspricht idealerweise genau einem Patch.
* Jeder Patch enthält einen begrenzten Scope.
* Jeder Patch muss mit Dry-run angewendet werden können.
* Jeder Patch muss mindestens `mvn test` bestehen, sofern Java-/Build-Dateien betroffen sind.
* Tooling-Änderungen benötigen zusätzlich Shell-/Python-Syntaxprüfung.
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
| 000002 | Docs/Templates | Templatebereich und Umsetzungsplan sind angelegt | `./bin/patch.sh show latest`, `./bin/export.sh full --zip`, `mvn test` |

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

Ziel: Wiederverwendbare Java-Core-Bausteine aus dem IDM-Referenzstand fachfrei und paketkonform nach `de.cocondo.platform.core` überführen.

Geplante Schritte:

1. IDM-System-Core-Dateien klassifizieren.
2. Core-Paketstruktur anlegen.
3. Fachfreie Basisklassen übernehmen.
4. Tests ergänzen.
5. Demo-Nutzung definieren oder vorbereiten.

Pflichtprüfungen:

```bash
mvn test
./bin/export.sh full --zip
```

Zusätzlich je Core-Baustein:

* Testklasse vorhanden
* keine Imports aus `de.cocondo.app.domain.idm`
* keine IDM-Ressourcenabhängigkeit

### Phase 5 – Demo Catalog Foundation

Ziel: Erste kleine Demo-Domäne auf Basis des Core anlegen.

Geplante Schritte:

1. Catalog-Modell definieren.
2. Liquibase-Changelog ergänzen.
3. Repository, Service, DTO, Controller umsetzen.
4. REST-/Service-Tests ergänzen.
5. OpenAPI-Erzeugung prüfen, sobald Tooling verfügbar ist.

Pflichtprüfungen:

```bash
mvn test
./bin/dbtool.sh validate-stage
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

## 5. Standard-Kommando nach jedem Patch

```bash
cd /opt/cocondo/springmaster
./bin/patch.sh show latest
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
ls -1t exports/text/*.zip | head -n 2
```

Bei Tooling-Änderungen zusätzlich vor dem Export:

```bash
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py
./bin/tooling-selfcheck.sh
```

## 6. Abbruchkriterien

Ein Schritt wird abgebrochen, wenn:

* eine erforderliche Baseline-Datei fehlt
* ein Patch-Scope nicht passt
* ein Dry-run fehlschlägt
* `mvn test` fehlschlägt
* ein Tooling-Test fehlschlägt
* eine Datei außerhalb des geplanten Scopes geändert werden müsste
* IDM-Fachcode unkontrolliert in Core oder Template übernommen würde

## 7. Nächster geplanter Schritt

Nach erfolgreichem Abschluss der Project-New-Foundation folgt die fachfreie Core-Baseline-Vorbereitung:

```text
000006_springmaster_core_baseline_preparation.zip
```

Dieser nächste Schritt darf noch keinen IDM-Fachcode übernehmen. Zuerst ist der wiederverwendbare System-Core aus dem IDM-Referenzexport zu klassifizieren und gegen das Zielpaket `de.cocondo.platform.core` abzugrenzen.



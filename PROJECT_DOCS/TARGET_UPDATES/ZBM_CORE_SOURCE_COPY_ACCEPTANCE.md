# ZBM Core Source-Copy Acceptance

Patch: `000081_springmaster_zbm_core_source_copy_acceptance`

> Historical evidence: This document records the Core source-copy acceptance state from patch `000081`. It does not prove the current ZBM HEAD, patch state, Persistence, Security or fachlicher service baseline. Those inputs must be supplied again under `ZBM_GENERATED_SLICE_PILOT_PLAN.md`.


## Zweck

Dieses Dokument definiert den ersten kontrollierten Core-Update-Test für das neu initialisierte Zielprojekt `zbm`.

Der Test ist bewusst kein fachlicher Service-Slice. Er stellt nur sicher, dass ein von Springmaster initialisiertes Java-Backend den wiederverwendbaren Core unter `de.cocondo.system` als target-lokalen Patch erhalten kann.

## Ausgangspunkt

Der ZBM-Initialisierungstest aus `000080` hat nachgewiesen:

```text
Target: /opt/cocondo/zbm
Base package: de.cocondo.zbm
Patch baseline: 000001_project_new_bootstrap
Maven test: successful
Target export: available under /opt/cocondo/zbm/exports/text
```

Die `ZbmApplication` scannt bereits:

```java
@SpringBootApplication(scanBasePackages = {
    "de.cocondo.zbm",
    "de.cocondo.system"
})
```

Vor `000081` existieren die Core-Klassen im Zielprojekt aber noch nicht.

## Zielbild

Springmaster erzeugt einen target-lokalen Core-Patch für `zbm`.

Der Patch enthält:

```text
pom.xml
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
PROJECT_DOCS/CORE/PLATFORM_UPDATES/<generated-update-id>.md
logs/CHANGELOG-<generated-update-id>.md
manifest.json
```

Der Patch enthält ausdrücklich nicht:

```text
src/main/java/de/cocondo/platform/**
src/test/java/de/cocondo/platform/**
PROJECT_DOCS/DEMO/**
PROJECT_DOCS/TOOLING/**
PROJECT_DOCS/PLATFORM_UPDATES/**
```

## Dependency-Regel

Die Core-Source-Copy darf nicht die Springmaster-Master-`pom.xml` in das Zielprojekt kopieren.

Stattdessen synthetisiert Springmaster für `core` und `core-runtime` eine target-lokale `pom.xml`, die die minimal notwendigen Core-Compile-Abhängigkeiten ohne DataSource-Autokonfiguration ergänzt:

```text
jakarta.persistence:jakarta.persistence-api
jakarta.validation:jakarta.validation-api
org.springframework.data:spring-data-commons
```

Vorhandene Zielprojekt-Abhängigkeiten bleiben erhalten.

## Anwendung

Die reale Anwendung erfolgt nicht per ungeschütztem Direktkopieren.

Ablauf:

```text
Springmaster platform-update generate zbm --profile core
Springmaster platform-update preflight zbm --zip <generated-core-patch.zip>
ZBM local patch.sh apply --dry-run <generated-core-patch.zip>
ZBM local patch.sh apply <generated-core-patch.zip>
ZBM mvn test
ZBM export.sh full --zip
```

`TARGET_DELIVERY_ENABLED=false` bleibt im Springmaster-Target-Descriptor bestehen. Für diesen Acceptance-Test wird das erzeugte ZIP nach Review durch das lokale Patchsystem von `zbm` angewendet; `target-apply` bleibt weiterhin ein späterer Delivery-Gate-Mechanismus.

## Akzeptanzkriterien

| Kriterium | Erwartung |
|---|---|
| Springmaster State | `000081_springmaster_zbm_core_source_copy_acceptance` |
| Target | `zbm` unter `/opt/cocondo/zbm` |
| Target Descriptor | `TARGET_LIFECYCLE=initialization`, `TARGET_DELIVERY_ENABLED=false` |
| Payload | Core Runtime + Core Tests |
| Scope | `core` |
| Review-Dokument | `PROJECT_DOCS/CORE/PLATFORM_UPDATES/**` |
| Plattform-Code | kein `de.cocondo.platform.*` im ZBM-Patch |
| Demo-Code | kein Demo-Payload |
| Dependency-Synthese | Zielprojekt-`pom.xml` enthält Core-Abhängigkeiten |
| Preflight | erfolgreich |
| Lokaler Apply | erfolgreich |
| Maven | `mvn test` in `/opt/cocondo/zbm` erfolgreich |
| Export | Full-ZIP-Export in `/opt/cocondo/zbm/exports/text` |

## Nächster Schritt

Nach erfolgreicher Core-Source-Copy-Acceptance kann der Service-Slice-Generator mit einem ersten fachlichen, kleinen ZBM-Aggregate-Slice getestet werden.

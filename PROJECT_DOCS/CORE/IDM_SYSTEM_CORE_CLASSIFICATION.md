# IDM System Core Classification

## 1. Zweck

Dieses Dokument klassifiziert den wiederverwendbaren technischen System-Core aus dem IDM-Referenzexport als Vorbereitung für eine spätere, fachfreie Migration nach `springmaster`.

Dieser Patch übernimmt **keinen Java-Code**. Er erzeugt nur die prüfbare Entscheidungsgrundlage für die folgenden Core-Patches.

## 2. Eingaben

| Quelle | Wert |
|---|---|
| IDM-Referenzexport | `idm_export_full_parts_baseline_2026-06-24_05-45-34-337Z.zip` |
| Springmaster-Baseline | `springmaster_export_full_parts_baseline_2026-06-24T08-55-49-108651Z.zip` |
| IDM-Quellwurzel | `src/main/java/de/cocondo/app/system` |
| Springmaster-Zielwurzel | `src/main/java/de/cocondo/system` |
| Springmaster-Zielpackage | `de.cocondo.system` |

## 3. Gesamtergebnis

| Kennzahl | Ergebnis |
|---|---:|
| Java-Dateien unter `de.cocondo.app.system` | 73 |
| direkte Imports aus `de.cocondo.app.domain.idm` | 0 |
| automatisch abgeleitete Zielpfade | 73 |

Der Befund `0` direkte IDM-Domain-Imports bedeutet nur, dass die technische System-Schicht nicht direkt auf `de.cocondo.app.domain.idm` importiert. Es bedeutet **nicht**, dass alle Dateien sofort migrierbar sind. Mehrere Dateien benötigen zusätzliche Dependency-Entscheidungen oder Infrastruktur-Slices.

## 4. Paketübersicht

| IDM-System-Paketgruppe | Dateien |
|---|---:|
| `config` | 3 |
| `core/http` | 7 |
| `core/id` | 2 |
| `core/locale` | 1 |
| `core/util` | 1 |
| `dto` | 8 |
| `entity` | 8 |
| `entity/metadata` | 6 |
| `entity/sequence` | 3 |
| `entity/validation` | 2 |
| `event` | 10 |
| `exception` | 1 |
| `info` | 5 |
| `list` | 2 |
| `mapper` | 1 |
| `security/authorization` | 3 |
| `security/config` | 5 |
| `security/http` | 2 |
| `security/jwt` | 2 |
| `swagger` | 1 |

## 5. Migrationsgruppen

| Gruppe | Dateien |
|---|---:|
| `basic-core-candidate` | 16 |
| `defer-persistence` | 18 |
| `defer-security` | 12 |
| `dependency-policy-required` | 8 |
| `event-foundation` | 4 |
| `web-infrastructure` | 15 |

### Bedeutung der Gruppen

| Gruppe | Bedeutung |
|---|---|
| `basic-core-candidate` | Kandidat für frühe Übernahme; keine JPA-/Security-/JWT-Abhängigkeit erkannt. Trotzdem ist pro Datei ein Build-Test erforderlich. |
| `dependency-policy-required` | Datei nutzt insbesondere Lombok. Vor Übernahme muss entschieden werden, ob Lombok in Springmaster erlaubt ist oder ob Code manuell ent-lombokisiert wird. |
| `web-infrastructure` | Web-/Spring-MVC-/Swagger-/Info-Bausteine. Übernahme erst nach Abgleich mit vorhandener Minimal-App und API-Kontrakt. |
| `event-foundation` | Domain-/Error-Event-Bausteine. Teilweise JPA- und Repository-Abhängigkeiten möglich; nur als eigener Slice übernehmen. |
| `defer-persistence` | Datei benötigt JPA/Spring Data/Transaktionen. Erst nach Dependency- und Liquibase-Baseline übernehmen. |
| `defer-security` | Datei gehört zur Security-/JWT-Schicht. Erst nach eigener Security-Architekturentscheidung übernehmen. |

## 6. Dependency-Befund gegen aktuellen Springmaster-Stand

Der aktuelle Springmaster-POM enthält bereits Web, Actuator, Validation, Springdoc, Liquibase, MariaDB, Test und H2. Im IDM-System-Core wurden zusätzlich relevante Abhängigkeiten gefunden, die im aktuellen Springmaster-POM noch nicht vollständig als Core-Entscheidung verankert sind:

* `spring-boot-starter-data-jpa` / Spring Data / Hibernate / JPA
* `spring-boot-starter-security`
* `jjwt-*`
* `lombok`

Daraus folgt: Eine vollständige 1:1-Core-Migration in einem Patch ist nicht zulässig. Die Migration muss in kleinen, testbaren Slices erfolgen.

## 7. Zielpfadregel

Jede übernommene Datei wird von:

```text
src/main/java/de/cocondo/app/system/<relativer-pfad>.java
```

nach:

```text
src/main/java/de/cocondo/system/<relativer-pfad>.java
```

überführt.

Dabei sind package- und import-Deklarationen entsprechend von `de.cocondo.app.system` nach `de.cocondo.system` anzupassen. Imports aus `de.cocondo.app.domain.idm` bleiben verboten.

## 8. Nächste zulässige Umsetzung

Der nächste Code-Patch darf nur einen kleinen Core-Slice übernehmen. Die Namespace-Korrektur aus Patch `000007` ist Voraussetzung. Empfohlener nächster Code-Patch:

```text
000008_springmaster_core_basic_types_foundation.zip
```

Ziel dieses Folgepatches:

* nur fachfreie Basistypen aus `dto`, `core/id`, `entity/validation` und `exception` prüfen
* Lombok-Verwendung explizit behandeln
* Tests ergänzen
* `mvn test` als Pflichtprüfung bestehen

Die vollständige Datei-Inventarisierung liegt maschinenlesbar in `PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_CLASSIFICATION.json`.

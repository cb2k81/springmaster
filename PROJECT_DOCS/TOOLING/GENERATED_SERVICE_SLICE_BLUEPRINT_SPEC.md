# Generated Service Slice Blueprint Spec

Patch: `000080_springmaster_generated_service_slice_blueprint_spec`

## Zweck

Dieses Dokument legt den Blueprint für die spätere Erzeugung fachlicher Java-Backend-Service-Slices aus Springmaster fest.

Der Patch ist bewusst eine Spezifikation und kein Generator-Code. Er bereitet den Test am ersten neuen Zielprojekt `zbm` vor und hält die Trennung zwischen technischer Projektinitialisierung, Plattform-Updates und fachlicher Slice-Erzeugung verbindlich fest.

## Leitentscheidung

Springmaster erzeugt neue Java-Backends in kontrollierten Stufen:

1. `project-new` erzeugt ein technisches Backend-Skeleton.
2. Core, Tools und Defaults werden als kontrollierte Plattformbestandteile eingebracht oder aktualisiert.
3. Ein Service-Slice-Generator erzeugt später fachliche Aggregate-Slices als Zielprojekt-Patches.
4. Ein Zielprojekt wird nur verändert, wenn der Lifecycle, der lokale Patchprozess und die Delivery-Freigabe explizit passen.

Für den ersten Praxistest gilt:

```text
Target:        zbm
Target path:   /opt/cocondo/zbm
Base package:  de.cocondo.zbm
Lifecycle:     initialization
Delivery:      disabled for platform target-apply until explicit acceptance
```

Bestehende laufende Projekte wie `idm` und `personnel` bleiben bewusst deferred und werden nicht beliefert.

## Generator-Ebenen

### 1. Project Generator

`bin/project-new.sh` bleibt der technische Projektgenerator.

Erzeugt werden insbesondere:

* Maven-Projektstruktur;
* Spring-Boot-Application;
* `/api/platform/info` Minimalendpoint;
* Patch-, Export-, Build- und DBTooling;
* `.env.example`, aber keine lokale `.env`;
* `export.config.json`;
* leeres Liquibase-Master-Changelog;
* Bootstrap-Patchnachweis;
* Versionsdatei im Zielprojekt.

`project-new` erzeugt keine fachliche Domäne und keinen fachlichen Aggregate-Code.

### 2. Platform Update Generator

`bin/platform-update.sh` erzeugt später reviewbare Update-Patches für Zielprojekte.

Relevante Profile:

| Profil | Zweck |
|---|---|
| `core` | wiederverwendbaren Core inklusive relevanter Dateien vorbereiten |
| `core-runtime` | Core-Runtime ohne Tests |
| `core-tests` | Core-Tests |
| `tooling` | Patch-, Export-, Build- und DBTooling |
| `defaults` | Basiskonfiguration wie `.env.example`, `export.config.json`, Env-Template |
| später `slice` | fachliche Slice-Artefakte |

Regel:

```text
generate != apply
```

Generation darf Artefakte und Review-Pläne erzeugen. Zielprojektmutation bleibt durch lokale Patch-Dry-runs, Scopeprüfung und `TARGET_DELIVERY_ENABLED=true` geschützt.

### 3. Service Slice Generator

Der spätere Service-Slice-Generator erzeugt fachlichen Code nicht direkt im Zielprojekt, sondern als Patch-ZIP für das lokale Patchsystem des Zielprojekts.

Ein generierter Slice besteht mindestens aus:

* REST Controller;
* Create-, Update-, Response- und ListItem-DTOs;
* Mapper;
* Validator;
* Application Service;
* Domain-/Persistence-Modell;
* Repository oder klar dokumentierter Candidate-Store;
* Liquibase-Changelog für durable Persistence oder explizit dokumentierte Candidate-Abweichung;
* Controller-, Service-, Mapper- und Validator-Tests;
* maschinenlesbarer Evidence-Datei;
* Patch-Manifest und Changelog.

## Eingabeformat

Der Slice-Generator soll eine explizite YAML- oder JSON-Spec verwenden. Eine typische Spec enthält:

```yaml
target: zbm
appName: zbm
basePackage: de.cocondo.zbm

slice:
  boundedContext: administration
  aggregate: BusinessPartner
  resourcePath: business-partners
  tableName: zbm_business_partner

api:
  collectionPath: /api/administration/business-partners
  operations:
    - list
    - detail
    - create
    - update
    - delete

fields:
  - name: id
    type: string
    generated: true
    exposed: true
  - name: name
    type: string
    required: true
    maxLength: 255
  - name: active
    type: boolean
    required: true
    default: true

security:
  mode: documented-deferred-security
  permissions:
    read: administration.business-partner.read
    write: administration.business-partner.write
    delete: administration.business-partner.delete

persistence:
  mode: liquibase-jpa
  database: mariadb

tests:
  controller: true
  service: true
  mapper: true
  validator: true
  repository: true
```

## Ausgabeformat

Für ein Aggregate `BusinessPartner` unter `de.cocondo.zbm.administration.businesspartner` ergibt sich folgende Zielstruktur:

```text
src/main/java/de/cocondo/zbm/administration/businesspartner/
  api/BusinessPartnerController.java
  application/BusinessPartnerService.java
  domain/BusinessPartner.java
  dto/BusinessPartnerCreateRequest.java
  dto/BusinessPartnerUpdateRequest.java
  dto/BusinessPartnerResponse.java
  dto/BusinessPartnerListItem.java
  mapper/BusinessPartnerMapper.java
  persistence/BusinessPartnerEntity.java
  persistence/BusinessPartnerRepository.java
  validation/BusinessPartnerValidator.java

src/test/java/de/cocondo/zbm/administration/businesspartner/
  api/BusinessPartnerControllerTest.java
  application/BusinessPartnerServiceTest.java
  mapper/BusinessPartnerMapperTest.java
  validation/BusinessPartnerValidatorTest.java
```

Persistence-Artefakte:

```text
src/main/resources/db/changelog/changes/<patch-id>-create-business-partner.xml
src/main/resources/db/changelog/db.changelog-master.xml
```

Patch-Artefakte:

```text
manifest.json
files/**
logs/CHANGELOG-<patch-id>.md
evidence/generated-slice-business-partner.json
```

## API-Standard

Der Generator muss die bestehenden Springmaster-API-Standards erzwingen.

Für ein Aggregate `BusinessPartner` sind die Standard-Endpunkte:

```text
GET    /api/administration/business-partners
GET    /api/administration/business-partners/{id}
POST   /api/administration/business-partners
PUT    /api/administration/business-partners/{id}
DELETE /api/administration/business-partners/{id}
```

Listenparameter:

```text
page
size
sortBy
sortDir
search
```

Nicht kanonisch als Standard:

```text
/all
/list
/findOne
/findFirst
/getById
```

Spezielle Lookups wie `by-number` sind nur zulässig, wenn der fachliche Schlüssel eindeutig und dokumentiert ist.

## DTO- und Boundary-Standard

Der Generator erzeugt getrennte DTOs:

| DTO | Zweck |
|---|---|
| `CreateRequest` | Eingabe bei `POST` |
| `UpdateRequest` | Eingabe bei `PUT` |
| `Response` | Detailantwort |
| `ListItem` | Listenantwort |
| optional `OptionItem` | selector-/options-Daten |

Regeln:

* keine Entities an der API-Grenze;
* keine Repository-Typen an der API-Grenze;
* keine Spring-Data-`Page` direkt als API-Response;
* öffentliche API nutzt Springmaster-konforme Paged-Response-Struktur.

## Validation-Standard

Der Generator muss zwei Validierungsebenen unterstützen:

1. Bean Validation am HTTP-Boundary, z. B. `@NotBlank`, `@Size`, `@Valid`;
2. Service-Boundary-Validation in einem expliziten Validator.

Der Validator prüft fachliche Regeln wie Pflichtfelder, Eindeutigkeit, Statuswechsel, Löschbarkeit und Referenzintegrität.

## Error-Standard

Generierte Slices verwenden den Springmaster-Fehlerkontrakt:

```json
{
  "errorId": "...",
  "status": 400,
  "errorType": "VALIDATION_ERROR",
  "message": "...",
  "path": "/api/...",
  "method": "POST",
  "violations": []
}
```

Status-Code-Mapping:

| Fall | Status |
|---|---:|
| Validation | 400 |
| Nicht gefunden | 404 |
| Konflikt / Duplicate | 409 |
| Nicht authentifiziert | 401 |
| Nicht berechtigt | 403 |
| Unerwarteter Fehler | 500 |

## Security-Standard

Für den ersten Generator-Reifegrad ist `documented-deferred-security` zulässig.

Der Generator muss dann trotzdem erzeugen oder dokumentieren:

* Security-Modus;
* Permission Vocabulary;
* Deferred-Marker;
* Evidence-Eintrag;
* Promotionsblocker für canonical/production.

`implemented-security` ist ein späteres Promotionsziel und erfordert echte Auth/AuthZ-Konfiguration sowie 401-/403-Tests.

## Core-Verteilung

Für die erste praktische Stufe wird `source-core-copy` als bevorzugter Kurzfristpfad festgelegt.

Regeln:

* übertragen wird nur wiederverwendbarer Core unter `de.cocondo.system`;
* `de.cocondo.platform.*` wird nicht in Zielprojekte übernommen;
* Demo-Code wird nicht übernommen;
* Core-Tests werden als eigene Update-Einheit behandelt;
* Core-Updates bleiben separat von fachlichen Slice-Updates;
* Zielprojekt-spezifische Scopes bleiben projektlokal.

Langfristig bleibt ein Maven-Artefakt möglich. Es ist aber nicht Voraussetzung für den ersten `zbm`-Initialisierungstest.

## ZBM-Konzepttest

Der erste Praxistest validiert noch keinen fachlichen Slice. Er validiert die Initialisierungsseite des Konzepts:

```text
Springmaster 000080+
  -> target descriptor zbm
  -> project-new initialization
  -> generated zbm backend skeleton
  -> local patch system
  -> dbtool status
  -> mvn test
  -> full export in /opt/cocondo/zbm
```

Acceptance-Kriterien:

| Kriterium | Erwartung |
|---|---|
| Target Descriptor | `zbm` ist `INITIALIZATION_CANDIDATE` |
| Zielpfad | `/opt/cocondo/zbm` fehlt, ist leer oder ist bereits ein gültiges ZBM-Skeleton |
| Project-New Dry-run | erfolgreich vor echter Anlage |
| Project-New Apply | erzeugt technisches ZBM-Skeleton |
| Patchsystem | im Zielprojekt vorhanden und listbar |
| DBTool | `dbtool.sh status` läuft ohne destruktive Operation |
| Maven | `mvn test` im Zielprojekt grün |
| Export | Zielprojekt erzeugt Full-ZIP-Export |
| Running Projects | IDM und Personnel werden nicht verändert |

## Nicht-Ziele von 000080

Patch `000080` implementiert noch nicht:

* produktiven Service-Slice-Generator;
* echten fachlichen ZBM-Slice;
* Zielprojekt-Delivery per `target-apply`;
* Updates in IDM, Personnel, Contacts oder Orders;
* implemented security;
* strict gates;
* Maven-Artefakt-Publishing für Core.

## Nachfolge

Nach erfolgreichem ZBM-Initialisierungstest sind zwei sinnvolle Folgepfade möglich:

1. `000081` implementiert die Generator-Foundation für Slice-Spec zu Patch-ZIP.
2. `000081` führt zuerst Core-Source-Copy für `zbm` als kontrollierten Update-Patch ein.

Die Entscheidung hängt davon ab, ob der erste fachliche Slice bereits Core-Typen zwingend voraussetzt.

## Entscheidung nach ZBM-Initialisierungstest 000080

Der ZBM-Initialisierungstest wurde erfolgreich abgeschlossen. Damit ist die technische Projektinitialisierung bewiesen, aber der generierte Zielcode enthält noch keine Core-Implementierung unter `de.cocondo.system`.

Für den nächsten Schritt wird daher der zweite Nachfolgepfad gewählt:

```text
000081_springmaster_zbm_core_source_copy_acceptance
```

Ziel ist kein fachlicher Slice, sondern die Core-Bereitstellung im Zielprojekt `zbm` als Voraussetzung für später generierte Service-Slices.

Akzeptanzregeln:

* Springmaster erzeugt einen target-lokalen Core-Patch für `zbm`.
* Das Patch-ZIP enthält `src/main/java/de/cocondo/system/**` und `src/test/java/de/cocondo/system/**`.
* Das Patch-ZIP enthält keine Dateien unter `de.cocondo.platform.*` und keinen Demo-Code.
* Für Core-Runtime-Profile wird die Zielprojekt-`pom.xml` dependency-seitig ergänzt, statt die Springmaster-Master-`pom.xml` zu kopieren.
* Der generierte Review-Plan liegt scope-kompatibel unter `PROJECT_DOCS/CORE/PLATFORM_UPDATES/**`.
* Die Anwendung erfolgt über das lokale Patchsystem des Zielprojekts und wird anschließend mit `mvn test` und Full-ZIP-Export validiert.

Erst nach erfolgreicher Core-Source-Copy-Acceptance ist die Grundlage für einen fachlichen Slice-Generator-Test vorhanden.

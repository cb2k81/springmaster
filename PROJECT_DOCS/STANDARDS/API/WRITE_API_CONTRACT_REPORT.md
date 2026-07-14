# Write API Contract Report

## Zweck

Der Write API Contract Report ist ein report-only Gate-Artefakt für einfache Create-/Update-/Delete-Endpunkte in Springmaster-Referenzslices.

Der Report ergänzt die bereits vorhandenen Query- und Detail-/Lookup-Reports. Er prüft nicht fachliche Persistenzdetails, sondern die öffentliche HTTP- und DTO-Grenze einer Management-Collection.

## Scope

Der initiale Scope ist bewusst eng:

```text
POST   /api/<domain>/<resources>
PUT    /api/<domain>/<resources>/{id}
DELETE /api/<domain>/<resources>/{id}
```

Für den ersten Golden-Reference-Slice gilt:

```text
POST   /api/demo/catalog/items
PUT    /api/demo/catalog/items/{id}
DELETE /api/demo/catalog/items/{id}
```

Nicht Bestandteil dieses Reports sind:

* Bulk Delete;
* State Commands;
* Relationship Commands;
* Command Precheck;
* Optimistic Locking;
* persistente Repository-Transaktionen.

Diese Themen bleiben Folgearbeiten nach dem stabilen Write-Basismuster.

## Report-Modus

Der Report bleibt zunächst report-only.

```json
{
  "schemaVersion": "springmaster.write-api-contract-gate-report.v1",
  "mode": "report-only"
}
```

Strict-Gate-Promotion ist erst zulässig, wenn Query, Detail/Lookup, Write und Request-Validation/OpenAPI-Reports stabil sind und Generated-Slice-Adoptionskriterien definiert wurden.

## Contract-Regeln

### Create

Create verwendet die Collection Root:

```text
POST /api/<domain>/<resources>
```

Erwartungen:

* separates CreateDTO als Request Body;
* Bean Validation am Request Body;
* kein Persistence Entity als public Request Body;
* `201 Created`;
* `Location` zeigt auf den opaque-id Detail-Endpunkt;
* Response Body ist das öffentliche Response DTO;
* Duplicate Business Key ergibt `409 CONFLICT` über den globalen Error Contract.

### Update

Update verwendet die opaque-id Detail-Route:

```text
PUT /api/<domain>/<resources>/{id}
```

Erwartungen:

* `id` ist Path Variable;
* separates UpdateDTO als Request Body;
* Bean Validation am Request Body;
* kein Persistence Entity als public Request Body;
* Erfolg ist `200 OK` mit Response DTO;
* unbekannte ID ergibt `404 RESOURCE_NOT_FOUND` über den globalen Error Contract.

### Delete

Single-resource Delete ist bodyless:

```text
DELETE /api/<domain>/<resources>/{id}
```

Erwartungen:

* `id` ist Path Variable;
* kein Request Body;
* Erfolg ist `204 No Content`;
* kein Response Body;
* unbekannte ID ergibt `404 RESOURCE_NOT_FOUND` über den globalen Error Contract.

## Finding-Familien

| ID | Bedeutung |
|---|---|
| `WRT-GATE-001` | Eingabedatei für den Report fehlt |
| `WRT-CREATE-001` | Create-Route ist nicht die Collection Root |
| `WRT-CREATE-002` | Create verwendet kein validiertes CreateDTO |
| `WRT-CREATE-003` | Create zeigt kein `201 Created`/`Location`/DTO-Evidence |
| `WRT-CREATE-004` | Create-`Location` zeigt nicht erkennbar auf die Detail-Route |
| `WRT-UPDATE-001` | Update ist nicht `PUT /{id}` mit Path Variable `id` |
| `WRT-UPDATE-002` | Update verwendet kein validiertes UpdateDTO |
| `WRT-UPDATE-003` | Update zeigt kein `200 OK`/DTO-Evidence |
| `WRT-DELETE-001` | Delete ist nicht `DELETE /{id}` mit Path Variable `id` |
| `WRT-DELETE-002` | Delete verwendet einen Request Body |
| `WRT-DELETE-003` | Delete zeigt kein `204 No Content` Evidence |
| `WRT-CONFLICT-001` | Duplicate Business Key nutzt nicht den globalen Conflict Contract |
| `WRT-NOTFOUND-001` | Update/Delete Not Found nutzt nicht den globalen Not-Found Contract |
| `WRT-TEST-001` | MockMvc-Evidence ist unvollständig |
| `WRT-OPENAPI-001` | OpenAPI-Evidence ist unvollständig |
| `WRT-DTO-001` | Public Write Boundary leakt Persistence Entity Vocabulary |

## CatalogItem Golden Reference

Der erste Golden-Reference-Report ist:

```text
src/test/resources/tooling/write-api-contract-report.catalogitem.golden.json
```

Der zugehörige Test ist:

```text
src/test/java/de/cocondo/platform/tooling/SpringmasterWriteApiContractReportTest.java
```

Das OpenAPI-Evidence-Testfile ist:

```text
src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemOpenApiWriteContractTest.java
```

## Operative Anwendung

Der Report kann manuell erzeugt werden:

```bash
./bin/write-api-contract-gate-report.sh
```

Für stabile Tests kann der Zeitstempel fixiert werden:

```bash
./bin/write-api-contract-gate-report.sh \
  --out target/write-api-contract-gate-report.json \
  --generated-at 2026-07-14T00:00:00Z
```

## Promotion-Regel

Der Report darf erst zum Strict Gate werden, wenn mindestens folgende Bedingungen erfüllt sind:

* Query Contract Report ist stabil;
* Detail/Lookup Contract Report ist stabil;
* Write API Contract Report hat Golden Fixtures;
* globaler API Error Contract ist operativ genutzt;
* Request-Validation/OpenAPI-required-Feld-Abgleich ist definiert;
* Generated-Slice-Adoption entscheidet, welche Regeln generierbar sind.

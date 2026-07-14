# Request Validation / OpenAPI Gate Report

**Patch:** `000120_springmaster_request_validation_openapi_gate`  
**Status:** report-only candidate reference  
**Scope:** Springmaster API boundary standards, CatalogItem golden reference

## 1. Ziel

Dieser Standard schließt die Lücke zwischen Java Bean Validation, DTO-Boundary und der veröffentlichten OpenAPI-Spezifikation.

Für generierte oder manuell gepflegte Management-APIs muss deterministisch nachweisbar sein:

* Create- und Update-Endpunkte verwenden explizite Boundary-DTOs als Request Body.
* Domain Entities werden nicht direkt als `@RequestBody` akzeptiert.
* `@Valid` ist am Request Body vorhanden.
* Bean-Validation-Pflichtfelder sind in OpenAPI als `required` sichtbar.
* Längen- und Validierungsgrenzen sind in OpenAPI nachvollziehbar, soweit der Generator sie abbildet.
* Validierungsfehler laufen über den globalen API Error Contract mit `VALIDATION_FAILED`.

Der erste Umsetzungsstand bleibt bewusst **report-only**. Ein Strict Gate erfolgt erst, wenn mehrere generierte Slices vergleichbar belegt sind.

## 2. Kanonische Prüfregeln

### 2.1 DTO Boundary

Create- und Update-Endpunkte dürfen keine Domain Entity als Request Body verwenden.

Zulässig:

```java
@PostMapping
public ResponseEntity<ResourceDTO> create(@Valid @RequestBody ResourceCreateDTO request)

@PutMapping("/{id}")
public ResourceDTO update(@PathVariable("id") String id, @Valid @RequestBody ResourceUpdateDTO request)
```

Nicht zulässig:

```java
public ResourceDTO create(@RequestBody ResourceEntity entity)
public ResourceDTO update(@RequestBody DomainEntity entity)
```

### 2.2 Required-Felder

Bean-Validation-Anmerkungen wie `@NotBlank`, `@NotNull` und `@NotEmpty` definieren Pflichtfelder für die API Boundary. Diese Pflichtfelder müssen in der OpenAPI-Komponente des jeweiligen Request DTO als `required` erscheinen.

CatalogItem-Referenz:

```text
CatalogItemCreateDTO.required = sku, name
CatalogItemUpdateDTO.required = name
```

### 2.3 Validierungsfehler

Ungültige Request Bodies müssen über den globalen API Error Contract beantwortet werden:

```json
{
  "status": 400,
  "errorType": "VALIDATION_FAILED",
  "messageKey": "springmaster.validation.failed",
  "violations": [
    {
      "field": "sku"
    }
  ]
}
```

### 2.4 OpenAPI Evidence

Die OpenAPI-Evidenz muss mindestens nachweisen:

* `POST /api/<domain>/<resources>` verwendet das CreateDTO.
* `PUT /api/<domain>/<resources>/{id}` verwendet das UpdateDTO.
* CreateDTO und UpdateDTO sind als Komponenten vorhanden.
* Die `required`-Listen der Komponenten enthalten die Bean-Validation-Pflichtfelder.
* Bekannte `@Size(max = ...)` Grenzen erscheinen als `maxLength`, soweit sie für String-Felder gelten.

## 3. Report Schema

Default-Ausgabe:

```text
reports/api/request-validation-openapi-gate-report.json
```

Schema-Version:

```text
springmaster.request-validation-openapi-gate-report.v1
```

Report-Eigenschaften:

| Feld | Bedeutung |
|---|---|
| `schemaVersion` | stabile Report-Version |
| `generatedAt` | Erstellzeitpunkt |
| `mode` | initial `report-only` |
| `project` | Projektname |
| `summary` | Ressourcen- und Findings-Zählung |
| `resources` | erkannte Ressourcen und Validation-/OpenAPI-Evidenz |
| `findings` | nicht-konforme Punkte |
| `standards` | referenzierte Standards und Belege |

## 4. Finding Families

| ID | Bedeutung |
|---|---|
| `VAL-GATE-001` | Required report input fehlt |
| `VAL-BOUNDARY-001` | Create verwendet kein validiertes CreateDTO |
| `VAL-BOUNDARY-002` | Update verwendet kein validiertes UpdateDTO |
| `VAL-BOUNDARY-003` | Request Body verwendet eine Domain Entity oder nicht erlaubtes DTO |
| `VAL-REQUIRED-001` | Bean-Validation-Pflichtfeld fehlt im Report/OpenAPI-Abgleich |
| `VAL-RUNTIME-001` | Runtime-Test für `VALIDATION_FAILED` fehlt |
| `VAL-OPENAPI-001` | OpenAPI-required-Feld-Evidenz fehlt |

## 5. Promotion Rules

Ein späterer Strict Gate darf erst aktiviert werden, wenn:

* mindestens CatalogItem und ein zweiter generierter Slice report-only grün sind;
* OpenAPI-Evidence stabil und nicht generator-/springdoc-versionsempfindlich ist;
* das Gate keine fachlichen Pflichtfelder aus Namenskonventionen errät, sondern aus Bean Validation oder expliziter Slice-Metadatenquelle ableitet;
* DTO-Boundary-Regeln mit Generator-Templates synchronisiert sind.

Bis dahin bleibt der Report ein deterministisches Artefakt für Review, CI-Evidence und Golden Fixtures.

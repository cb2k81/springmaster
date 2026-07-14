# CatalogItem Request Validation / OpenAPI Gate Evidence

**Patch:** `000120_springmaster_request_validation_openapi_gate`  
**Status:** CatalogItem candidate reference evidence

## 1. Ziel

CatalogItem belegt als Golden Reference, dass Bean Validation, DTO-Boundary und OpenAPI-required-Felder konsistent sind.

Der Patch ergänzt keine neue Fachlogik und ändert keine Runtime-Endpoints. Er fügt report-only Tooling, eine Golden Fixture und gezielte OpenAPI-/Tooling-Tests hinzu.

## 2. Request DTO Boundary

CatalogItem verwendet explizite Boundary-DTOs:

```text
POST /api/demo/catalog/items        -> CatalogItemCreateDTO
PUT  /api/demo/catalog/items/{id}   -> CatalogItemUpdateDTO
```

Die Controller-Signaturen bleiben:

```java
@Valid @RequestBody CatalogItemCreateDTO
@Valid @RequestBody CatalogItemUpdateDTO
```

Die Domain Entity `CatalogItem` wird nicht als `@RequestBody` verwendet.

## 3. Bean Validation Required Fields

Die aktuelle Bean-Validation-Quelle ist:

```text
CatalogItemCreateDTO.sku   -> @NotBlank, @Size(max = 128)
CatalogItemCreateDTO.name  -> @NotBlank, @Size(max = 255)
CatalogItemUpdateDTO.name  -> @NotBlank, @Size(max = 255)
```

Daraus folgt die OpenAPI-required-Erwartung:

```text
CatalogItemCreateDTO.required = sku, name
CatalogItemUpdateDTO.required = name
```

`description`, `tags` und `availability` bleiben optional.

## 4. Runtime Error Contract

Ungültige Create-/Update-Payloads werden über den globalen Error Contract beantwortet:

```text
400 VALIDATION_FAILED
messageKey = springmaster.validation.failed
violations[].field = sku | name | availability.chronological
```

Die bestehenden MockMvc-Tests bleiben die Runtime-Evidenz. Der neue Patch ergänzt die OpenAPI-/Report-Evidenz.

## 5. Neue Artefakte

```text
bin/request-validation-openapi-gate-report.py
bin/request-validation-openapi-gate-report.sh
src/test/resources/tooling/request-validation-openapi-gate.catalogitem.golden.json
src/test/java/de/cocondo/platform/tooling/SpringmasterRequestValidationOpenApiGateReportTest.java
src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemOpenApiRequestValidationContractTest.java
```

## 6. Nicht enthalten

Nicht Teil dieses Patches sind:

* Bulk-/Command-/Relationship-DTOs;
* Optimistic-Locking-/Version-Validation;
* Persistent-Transaction-Validation;
* Strict Gate Promotion;
* Generator-Template-Umbau.

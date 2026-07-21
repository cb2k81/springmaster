# Demo Domains

Dieser Bereich dokumentiert Demo-Domänen des Springmaster-Projekts.

Demo-Code liegt unter:

```text
src/main/java/de/cocondo/platform/demo/**
src/test/java/de/cocondo/platform/demo/**
```

Demo-Code dient dazu, Core- und Tooling-Fähigkeiten im Masterprojekt realistisch zu verwenden und zu testen. Er ist nicht Teil des verteilbaren Core-Namespace `de.cocondo.system`.

## Aktueller Stand

* `000017_springmaster_demo_catalog_basic_domain` führte die erste minimale Demo-Domäne `catalog` ein.
* Die Demo nutzt vorhandene Core-Bausteine wie `DomainEntity`, `Range`, `Validator`, `ValidationException`, `DTO` und `EntityAlreadyExistsException`.
* Seit `000163_springmaster_catalogitem_persistent_candidate_runtime` arbeitet der CatalogItem-Candidate über Spring Data JPA und Liquibase.
* Der Slice bleibt bis zur MariaDB-/Konfliktqualifikation, Management-Security und ausdrücklichen ADR-0007-Promotion ein `candidate-reference-slice`.

## Validierungsfix

* `000019_springmaster_demo_catalog_validation_fix` behebt die Testvalidierung der ersten Catalog-Demo.
* Patchnummer `000018` ist lokal bereits durch eine unveränderte Wiederanwendung des `000017`-Archivs belegt.
* Der Spring-Context-Test referenziert die App-Konfiguration explizit, da Demo-Tests nicht im Paketbaum unter `de.cocondo.platform.app` liegen.
* Die Duplicate-SKU-Fehlermeldung verwendet den fachlichen Begriff `SKU`.

## REST-API

* `000020_springmaster_demo_catalog_api_controller` ergänzt die erste REST-API für die Demo-Domäne.
* Die Endpunkte liegen unter `/api/demo/catalog/items`.
* Die API verwendet weiterhin den In-Memory-Service und aktiviert keine Datenbank- oder Repository-Schicht.
* Validierungsfehler werden auf `400`, Duplicate-SKU-Fehler auf `409` abgebildet.
## REST-API-Fix

* `000021_springmaster_demo_catalog_api_pathvariable_fix` korrigiert die Pfadvariablenbindung der Catalog-API.
* Die SKU-Pfadvariable wird explizit über `@PathVariable("sku")` gebunden, damit die Controller-Tests auch ohne Compiler-Parameter-Metadaten stabil laufen.

## Catalog-demo readiness plan since 000056

Patch `000056_springmaster_catalog_demo_readiness_plan` adds `CATALOG_DEMO_READINESS_PLAN.md`. The plan defines when Catalog-demo may become the canonical Springmaster reference implementation.

The existing CatalogItem code remains an implementation seed until it satisfies the documented readiness criteria. A canonical CatalogItem slice must demonstrate endpoint contracts, DTO/validation boundaries, standard error behavior, mapping boundaries, service/transaction separation, persistence rules, security classification and gate status.

A slice that only compiles is not canonical. It must have tests, OpenAPI or gate evidence, and an explicit list of deferred standards.

## ADR-0007 Catalog-demo canonicalization

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts the canonicalization strategy for Catalog-demo.

The current CatalogItem implementation remains `legacy-demo-seed`. Future implementation patches may create a `candidate-reference-slice`, but the slice is only canonical when a patch records ADR-0007 evidence and explicitly marks it as `canonical-reference-slice`.

This ADR keeps IDM, Personnel, Contacts, Orders and other existing projects outside the delivery scope. They may be compared read-only only after Catalog-demo has canonical evidence and a comparison scope exists.



## Catalog-demo candidate contract plan since 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` defines the first CatalogItem candidate-slice contract in `CATALOG_DEMO_CANDIDATE_SLICE_CONTRACT_PLAN.md`.

The plan does not change Demo code. It prepares the next code patch to create a `candidate-reference-slice` with canonical endpoints, DTO roles, standard error behavior, bodyless delete, security classification evidence and report-only gate evidence.

The current implementation remains `legacy-demo-seed` until that code patch is applied and validated.



## CatalogItem candidate-reference-slice foundation

Patch `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation` adds the first executable `CatalogItem` candidate foundation. Evidence is recorded in `CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md`.

The candidate foundation is standards-oriented but not canonical. Catalog-demo target comparison and target delivery remain blocked.

## CatalogItem forensic review after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` confirms the `CatalogItem` implementation as a `candidate-reference-slice foundation`.

The slice is not canonical. The review records remaining blockers and cleanup items in `CATALOG_DEMO_CANDIDATE_SLICE_FORENSIC_REVIEW.md`.

## 000075 DTO/validation cleanup

The Catalog-demo `CatalogItem` candidate-reference-slice now includes DTO-boundary cleanup and service validation symmetry. Public request DTOs use `CatalogItemAvailabilityDTO` instead of the persistence-facing `Range` embeddable. The slice remains candidate-level and not canonical.




## CatalogItem query-operations interface adoption

Patch `000102_springmaster_catalogitem_query_operations_interface_adoption` adapts the Core query-operations interfaces in the CatalogItem candidate slice. The service implements `ResultSetQueryOperations` with Demo-owned query records for paged list, complete result set and count-only operations. Controllers remain explicit Spring MVC adapters.




## Query Operations closure review

Patch `000103_springmaster_query_operations_contract_closure_review` records that the CatalogItem candidate slice now demonstrates the complete Query Operations pattern: paged list, complete result set `/all`, count-only `/count`, Core DTO/interface usage and Demo-owned query records.

The slice remains `candidate-reference-slice`, not canonical, until the remaining MariaDB/constraint, optimistic-locking, management-security, gate-promotion and target-comparison blockers are resolved.



## Persistent JPA query runtime since 000159

Patch `000113_springmaster_persistent_jpa_count_reference_slice` originally added a non-runtime JPA reference. Patch `000163_springmaster_catalogitem_persistent_candidate_runtime` replaces it with the registered `CatalogItemJpaQueryRepository` and makes the CatalogItem Candidate persist through Spring Data JPA and Liquibase.

The runtime demonstrates the durable query pattern required for generated or later persistent slices:

* paged list uses a data query plus a separate count query for `totalElements`;
* `/all` uses the same filter family and stable sorting without paging;
* `/count` uses a dedicated `CriteriaQuery<Long>` with `cb.count(root)`;
* count uses the same predicates as list and `/all`, but no sorting, paging, DTO mapping or entity-list materialization;
* invalid paging and sorting input is rejected before pageable or criteria-query construction.

The slice remains candidate-level until MariaDB/constraint and optimistic-lock qualification, implemented management security and explicit canonical-promotion evidence are added.

## CatalogItem security/data-scope query parity since 000114

Patch `000114_springmaster_query_security_scope_parity_reference` adds a compact query-scope reference for CatalogItem read operations.

The reference keeps the current CatalogItem runtime lightweight, but proves the rule that paged list, `/all` and `/count` must use the same resolved read permission and data-scope predicate family. `CatalogItemScopedQueryReference` applies `catalog:item:read`, `allowedSkus`, `sku` and `name` through one shared matcher before operation-specific paging, sorting, DTO mapping or count-only behavior.

This closes the security/data-scope parity gap for the Query/List/All/Count candidate reference track. CatalogItem remains candidate-level until a later canonical-promotion decision explicitly accepts it as canonical.


## CatalogItem global API error handler migration since 000117

Patch `000117_springmaster_catalogitem_global_api_error_handler_migration` migrates the CatalogItem candidate reference slice from controller-local error DTOs and `@ExceptionHandler` methods to the Core-owned `GlobalApiExceptionHandler`.

The Demo slice now proves that standard API failures can be represented by the shared Core error envelope without local controller error code:

* validation failures use `VALIDATION_FAILED`;
* invalid query/request failures use `INVALID_REQUEST`;
* missing resources use `RESOURCE_NOT_FOUND`;
* duplicate business keys use `CONFLICT`;
* CatalogItem-specific not-found and conflict cases retain catalog message keys;
* correlation IDs are propagated by the global handler.

The old CatalogItem-local error DTOs and local not-found exception are removed. Detail/Lookup and Write API contract reports remain follow-up roadmap items.

## CatalogItem Detail/Lookup contract report since 000118

Patch `000118_springmaster_detail_lookup_contract_report` adds report-only Detail/Lookup contract evidence for CatalogItem.

The reference now proves the canonical read-by-one family:

```text
GET /api/demo/catalog/items/{id}
GET /api/demo/catalog/items/by-sku/{sku}
```

The report and targeted tests cover opaque-id lookup, unique SKU lookup, global `RESOURCE_NOT_FOUND` error behavior, create `Location` follow-up and OpenAPI route/path-variable evidence. Write API and Request Validation/OpenAPI gates remain follow-up roadmap items.

## CatalogItem Write API contract report since 000119

Patch `000119_springmaster_write_api_contract_report` adds report-only Create/Update/Delete evidence for the CatalogItem candidate reference slice.

Erreicht:

* `bin/write-api-contract-gate-report.py` and `.sh` generate a machine-readable Write API report.
* `WRITE_API_CONTRACT_REPORT.md` defines report schema, finding families and promotion rules for simple write endpoints.
* CatalogItem is Golden Reference for `POST /api/demo/catalog/items`, `PUT /api/demo/catalog/items/{id}` and bodyless `DELETE /api/demo/catalog/items/{id}`.
* MockMvc and OpenAPI evidence cover CreateDTO/UpdateDTO boundaries, `201 Created` plus `Location`, `200 OK` update, `204 No Content` delete and global error behavior for validation, not-found and conflict cases.
* Bulk delete, state commands, relationship commands and optimistic locking remain deferred.

## CatalogItem Request Validation/OpenAPI gate since 000120

Patch `000120_springmaster_request_validation_openapi_gate` adds report-only Request Validation/OpenAPI evidence for the CatalogItem candidate reference slice.

Erreicht:

* `bin/request-validation-openapi-gate-report.py` and `.sh` generate a machine-readable validation/OpenAPI report.
* `REQUEST_VALIDATION_OPENAPI_GATE.md` defines report schema, finding families and promotion rules for DTO-boundary and required-field alignment.
* CatalogItem is Golden Reference for `CatalogItemCreateDTO` and `CatalogItemUpdateDTO`.
* OpenAPI evidence covers required fields derived from Bean Validation: Create requires `sku` and `name`; Update requires `name`.
* DTO-boundary evidence proves that the controller uses `@Valid @RequestBody` with CreateDTO/UpdateDTO and does not expose the Domain Entity as request body.
* Runtime validation remains backed by the existing global `VALIDATION_FAILED` MockMvc tests.

Generated-slice adoption planning remains the next roadmap item.

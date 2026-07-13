# Demo Domains

Dieser Bereich dokumentiert Demo-Domänen des Springmaster-Projekts.

Demo-Code liegt unter:

```text
src/main/java/de/cocondo/platform/demo/**
src/test/java/de/cocondo/platform/demo/**
```

Demo-Code dient dazu, Core- und Tooling-Fähigkeiten im Masterprojekt realistisch zu verwenden und zu testen. Er ist nicht Teil des verteilbaren Core-Namespace `de.cocondo.system`.

## Aktueller Stand

* `000017_springmaster_demo_catalog_basic_domain` führt die erste minimale Demo-Domäne `catalog` ein.
* Die Demo nutzt vorhandene Core-Bausteine wie `DomainEntity`, `Range`, `Validator`, `ValidationException`, `DTO` und `EntityAlreadyExistsException`.
* Es gibt noch keine Spring-Data-JPA-Repositories, keine reale Datenbankpflicht und keine Liquibase-Demo-Tabellen.

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

The slice remains `candidate-reference-slice`, not canonical, until persistence, security, OpenAPI, gate and target-comparison blockers are resolved.

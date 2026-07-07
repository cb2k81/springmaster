# Catalog-demo Readiness Plan

## Purpose

This plan defines when `Catalog-demo` is allowed to become the canonical Springmaster reference implementation.

The plan exists because Springmaster has already documented a broad set of API, application-layer, persistence, security, mapping and gate standards. A demo domain that merely compiles would now be insufficient. The first Catalog-demo implementation must demonstrate the standards deliberately and must mark every intentionally deferred rule.

This document is documentation-only. It does not create Java code, test utilities, Maven profiles, OpenAPI generators, Spring Security configuration, database changes, target-project updates or Catalog-demo implementation changes.

## Baseline position

As of `000056_springmaster_catalog_demo_readiness_plan`, Springmaster has the following pre-demo standard baseline:

| Area | Current reference |
|---|---|
| API request validation | `PROJECT_DOCS/STANDARDS/API/API_REQUEST_VALIDATION_STANDARD.md` |
| Required fields and OpenAPI required properties | `PROJECT_DOCS/STANDARDS/API/REQUIRED_FIELDS_OPENAPI_STANDARD.md` |
| List, filter, query and paging | `PROJECT_DOCS/STANDARDS/API/LIST_FILTER_QUERY_STANDARD.md` |
| Endpoint contracts | `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md` |
| Command and relationship endpoints | `PROJECT_DOCS/STANDARDS/API/COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md` |
| Command HTTP semantics | `PROJECT_DOCS/STANDARDS/API/COMMAND_HTTP_STANDARD.md` |
| External IDs and OpenAPI boundary | `PROJECT_DOCS/STANDARDS/API/EXTERNAL_ID_OPENAPI_BOUNDARY_STANDARD.md` |
| API error contract | `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md` |
| DTO boundary and validation | `PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md` |
| Controller/service/use-case/transaction boundary | `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md` |
| Domain entity and persistence foundation | `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md` |
| Security and permission boundary | `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md` |
| Mapping | `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md` |
| API contract gate concept | `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md` |
| Real-app pattern comparison | `PROJECT_DOCS/STANDARDS/REAL_APP_PATTERN_FORENSICS.md` |

Catalog-demo must be built against this baseline rather than inventing new implicit conventions.

## Readiness principle

Catalog-demo is not canonical when it compiles. Since accepted ADR-0007, it is canonical only when a patch explicitly transitions a slice from `candidate-reference-slice` to `canonical-reference-slice` and records evidence for the relevant Springmaster standards.

A Catalog-demo slice may have deferred concerns, but deferrals must be explicit. Silent omissions are not allowed.

The first reference slice must therefore provide three things:

1. a small functional domain implementation;
2. tests or gate placeholders that prove the public contract;
3. a readiness summary that lists satisfied, partially satisfied and deferred standards.

## First reference slice

The first canonical slice remains `CatalogItem` in the `Catalog-demo` domain.

The intended resource vocabulary is:

| Concern | Standardized vocabulary |
|---|---|
| Domain | `catalog` |
| Resource | `items` |
| Main resource name | `CatalogItem` |
| Collection endpoint | `GET /api/demo/catalog/items` |
| Detail endpoint | `GET /api/demo/catalog/items/{id}` |
| Create endpoint | `POST /api/demo/catalog/items` |
| Full update endpoint | `PUT /api/demo/catalog/items/{id}` |
| Single delete endpoint | `DELETE /api/demo/catalog/items/{id}` with no request body |
| Bounded selector endpoint | `GET /api/demo/catalog/items/options` if needed |
| Complex search endpoint | `POST /api/demo/catalog/items/search` only when simple list filters are insufficient |
| Collection command endpoint | `POST /api/demo/catalog/items/commands/<command>` only for non-CRUD commands |

The existing early demo API under `/api/demo/catalog/items` is classified as `legacy-demo-seed`. It remains useful as historical seed code, but it is not the final canonical reference until a later patch supplies ADR-0007 evidence and changes the slice state deliberately.

## Mandatory first-slice capabilities

The first canonical `CatalogItem` slice must demonstrate these capabilities before it can be treated as the reference pattern.

| Capability | Required first-slice behavior |
|---|---|
| Create | validates required fields and returns `201 Created` with response DTO and `Location` when practical |
| Detail | retrieves by opaque string ID, not by internal numeric persistence ID |
| Paged list | exposes explicit `page`, `size`, `sortBy`, `sortDir` and selected filters; no `sort` alias and no controller-level `Pageable` contract leakage |
| Full update | uses a dedicated update DTO, returns `200 OK` with updated response DTO and handles missing IDs through the standard error contract |
| Single delete | uses bodyless `DELETE`, returns `204 No Content` on success and `404` when already absent; structured delete input is not accepted as the single-delete contract |
| Error behavior | returns the 000048/000059 standard error body for validation, not-found and conflict cases, including required `errorId` |
| DTO boundary | exposes request/response DTOs only; no entity or Spring Data response body leaks |
| Mapping | maps entity/read model state through an explicit mapper or approved mapping method without repository or security logic |
| Service boundary | keeps controller logic thin and places business behavior in resource, query, command service or use-case boundary |
| Persistence boundary | uses the 000051 persistence rules when persistent storage is introduced |
| Security classification | explicitly marks each endpoint as public, authenticated, management, technical or system, even if the first security implementation is deferred |
| Gate summary | records which standard checks are implemented, manually reviewed or deferred |

## DTO readiness matrix

The first slice should use DTO roles deliberately.

| DTO role | First-slice expectation |
|---|---|
| `CatalogItemCreateDTO` | required create fields and Bean Validation annotations |
| `CatalogItemUpdateDTO` | full replacement fields and Bean Validation annotations |
| `CatalogItemPatchDTO` | deferred unless partial update is introduced deliberately |
| `CatalogItemDTO` | detail response shape |
| `CatalogItemListItemDTO` | list-row response shape when list and detail differ |
| `CatalogItemOptionDTO` | bounded selector response only if `/options` is introduced |
| `CatalogItemSearchDTO` | deferred until complex search is needed |
| `CatalogItem<Command>NameCommandDTO` | deferred until non-CRUD commands exist |
| `CatalogItem<Command>NameResultDTO` | deferred until a command returns structured result data |

DTO names may be simplified only when the standard documents an explicit reason. Simplification must not make role boundaries ambiguous.

## Endpoint readiness matrix

| Endpoint type | First-slice status |
|---|---|
| Paged collection | mandatory |
| Detail by ID | mandatory |
| Create | mandatory |
| Full update | mandatory before the slice is canonical; may be a second code patch after create/list/detail |
| Single delete | mandatory before the slice is canonical; may be a second code patch after create/list/detail |
| Bounded options | optional and only for UI selector semantics |
| Complex search | deferred |
| Delete multiple | deferred until a real bulk use case exists |
| State transition command | deferred until a real lifecycle exists |
| Relationship endpoint | deferred until a second related resource exists |
| Nested aggregate command | deferred until a real nested aggregate exists |

A deferred endpoint type must remain absent. It must not be represented by a placeholder endpoint that creates a false standard.

## Error readiness matrix

The first canonical slice must demonstrate at least these negative cases:

| Scenario | Expected standard behavior |
|---|---|
| Invalid create body | `400 BAD_REQUEST` with standard error body and `violations` |
| Invalid update body | `400 BAD_REQUEST` with standard error body and `violations` |
| Invalid list query | `400 BAD_REQUEST` with standard error body and query violation |
| Unknown ID | `404 NOT_FOUND` with standard error body |
| Duplicate business key | `409 CONFLICT` with standard error body |
| Missing authentication | `401 UNAUTHORIZED` once security is implemented |
| Missing permission | `403 FORBIDDEN` once security is implemented |

If security is deferred in the first slice, `401` and `403` behavior must be listed as deferred, not omitted.

## Persistence readiness

The first persistent Catalog-demo slice must satisfy the 000051 domain/persistence standard.

Minimum expectations:

* `CatalogItem` uses the Core `DomainEntity` foundation unless a later ADR changes the standard.
* The public `id` is an opaque string identifier.
* Business identifiers such as `sku` remain explicit business fields.
* `persistenceVersion` is available for optimistic locking when persistence is active.
* Repositories are not injected into controllers.
* EntityManager access is not exposed at API boundaries.
* Hard delete, archive and deactivate semantics are not mixed.

Deferred persistence topics:

* metadata persistence;
* tag/key-value persistence;
* NumberSequence/business-number generation;
* soft-delete framework;
* multi-tenancy/data-scope persistence;
* generic repository base interfaces.

## Security readiness

Catalog-demo must not accidentally normalize unprotected management endpoints.

The first slice may choose one of two explicit modes:

| Mode | Meaning |
|---|---|
| `documented-deferred-security` | endpoints are classified and planned, but enforcement is deliberately deferred |
| `implemented-management-security` | endpoints require authentication and operation permissions according to the security standard |

If `documented-deferred-security` is chosen, the readiness summary must list the intended permissions, for example:

| Operation | Candidate permission |
|---|---|
| list/detail | `catalog:item:read` |
| create | `catalog:item:create` |
| update | `catalog:item:update` |
| delete | `catalog:item:delete` |
| options | `catalog:item:read-options` when options need a distinct permission |

A slice with no security classification cannot be canonical.

## Gate readiness matrix

The first Catalog-demo slice should be evaluated with the 000055 maturity vocabulary.

| Gate layer | First-slice readiness target |
|---|---|
| G0 Documentation gate | mandatory |
| G1 OpenAPI contract gate | mandatory before canonical status, implementation may follow in a dedicated gate patch |
| G2 MockMvc behavior gate | mandatory for positive and negative API behavior |
| G3 Java boundary gate | mandatory as reflection/classpath scan or explicitly deferred to the first gate-tooling patch |
| G4 Security/permission gate | deferred or implemented, but never silent |
| G5 Catalog-demo reference gate | mandatory readiness summary before canonical status |
| G6 Target comparison gate | deferred until Catalog-demo proves the standards |

The first code patch for Catalog-demo may produce a `candidate` slice. The slice becomes `canonical` only after the required gates are implemented or explicitly deferred with owner and rationale.

## Suggested implementation sequence

Recommended sequence after this plan:

1. `000057_springmaster_catalog_demo_contract_slice_plan` or equivalent implementation plan for the first CatalogItem code slice.
2. Implement the minimum DTO, service, mapper, controller and test shape for create/detail/paged list as a candidate slice.
3. Add error handling and negative MockMvc tests.
4. Add update and bodyless delete.
5. Add the first OpenAPI contract assertion helper.
6. Add Java boundary scans for controller, DTO and mapper leakage.
7. Decide security mode and add security classification or enforcement.
8. Mark the slice as canonical only when the readiness summary is complete.

This sequence may be split differently, but no step may silently bypass the standards.

## Target-project boundary

This plan does not authorize target-project changes.

IDM, Personnel, Contacts, Orders and other existing applications remain comparison inputs only. Their code may inform future gates, but they must not be remediated or supplied by Springmaster until Catalog-demo has reached canonical readiness and a separate target-comparison strategy exists.

## Current status

As of `000056_springmaster_catalog_demo_readiness_plan`, Catalog-demo readiness is defined but not implemented.

The next implementation step should either define the concrete CatalogItem code-slice plan or create the first gate-tooling seed. If implementation starts next, the patch must be a code/test patch and must run the required Maven/test validation.


## Consistency review dependency since 000057

Patch `000057_springmaster_standard_consistency_and_adr_gap_review` reviews the readiness plan against the standards created up to 000056.

Catalog-demo remains the intended first reference project, but the existing CatalogItem seed must not become canonical until the P0 consistency gaps from the review are resolved or explicitly classified as accepted exceptions.

Blocking readiness implications:

- the canonical list query contract uses `sortBy` and `sortDir`;
- `/all` is non-canonical, `/options` is the bounded selector endpoint, and `/reference-data` requires a dedicated ADR before it appears in Catalog-demo;
- the first canonical CatalogItem slice must not inherit non-standard behavior from the legacy seed;
- deferred security must include minimum documented evidence;
- OpenAPI naming and schema conventions must be defined before strict OpenAPI gates.


## Query/reference-data consistency since 000058

The first CatalogItem slice must use `sortBy` and `sortDir` as the public sorting parameters. `sort` is not allowed as the canonical Catalog-demo parameter. Catalog-demo must not introduce `/all`. It may introduce `/options` only for a documented bounded selector use case, and it must not introduce `/reference-data` without a dedicated ADR.


## Error identity and status-code consistency since 000059

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` narrows the first CatalogItem canonical defaults.

Catalog-demo readiness now requires:

- create returns `201 Created` with response DTO and `Location` when practical;
- full update returns `200 OK` with updated response DTO;
- single bodyless delete returns `204 No Content` on success and `404` when already absent;
- delete-multiple remains deferred, but when introduced it must return `200 OK` with result DTO;
- every error response includes `errorId`;
- `messageKey`, `correlationId`, `traceId` and `localMessage` are either implemented or explicitly deferred in the readiness summary.

## ADR-0007 canonicalization update

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts the Catalog-demo canonicalization strategy.

Readiness status after 000065:

| Item | Status |
|---|---|
| Existing CatalogItem implementation | `legacy-demo-seed` |
| First standards-aligned implementation patch | must be labeled `candidate-reference-slice` unless all evidence is complete |
| Canonical CatalogItem slice | requires explicit `canonical-reference-slice` evidence patch |
| Target-project comparison | deferred until canonical Catalog-demo evidence exists |

A future patch that changes Catalog-demo code must state whether it creates a candidate slice or completes canonicalization. A future patch may not claim canonical status without endpoint, DTO, validation, error, application-layer, persistence, mapping, security-classification, gate-evidence and deferral evidence.

## ADR-0005 security update

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts the security and permission boundary ADR.

Catalog-demo readiness impact:

- every CatalogItem endpoint must have explicit security classification before a slice may become canonical;
- `documented-deferred-security` must include endpoint classification, intended permissions, planned role mapping, deferred security tests and rationale;
- `implemented-management-security` must include authentication behavior, permission checks, positive and negative tests and role mapping evidence;
- first-slice permission vocabulary should use `catalog:item:read`, `catalog:item:create`, `catalog:item:update`, `catalog:item:delete`, optional `catalog:item:delete-multiple`, optional `catalog:item:read-options` and future `catalog:item:<transition>`;
- a slice with unclassified or accidentally public management endpoints cannot be `canonical-reference-slice`.

## Report-only gate seed relationship since 000067

Patch `000067_springmaster_report_only_gate_seed_plan` defines how the first report-only gate seed may summarize Catalog-demo readiness evidence.

Catalog-demo impact:

- the first gate seed may report missing Catalog-demo evidence as `MANUAL_REVIEW` or `WARNING` findings;
- the seed must not declare Catalog-demo canonical;
- `legacy-demo-seed`, `candidate-reference-slice` and `canonical-reference-slice` remain documentation states governed by ADR-0007;
- security evidence may be checked only as report-only evidence based on ADR-0005;
- target-project comparison remains blocked until Catalog-demo evidence exists and a later decision authorizes comparison.



## Candidate slice contract plan since 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` adds `CATALOG_DEMO_CANDIDATE_SLICE_CONTRACT_PLAN.md` as the implementation bridge from findings baseline to Catalog-demo code work.

Readiness impact:

- the next CatalogItem implementation patch must be labeled `candidate-reference-slice`, not `canonical-reference-slice`;
- the candidate endpoint contract is create, paged list, detail by opaque `id`, lookup by `sku`, full update and bodyless delete;
- `/all`, public `findOne`/`findFirst`/`findLast`, body-bearing single `DELETE`, `/reference-data`, delete-multiple, complex search and relationship endpoints remain out of scope;
- the candidate slice must use `page`, `size`, `sortBy` and `sortDir` for list queries;
- errors must use the Springmaster standard error body with `errorId`;
- security may be `documented-deferred-security` only when endpoint classification and intended permissions are recorded;
- a candidate evidence document is required before the G5 readiness finding can move away from pure legacy-seed manual review.

The existing CatalogItem implementation remains `legacy-demo-seed` until a code patch implements the candidate contract and records evidence.



## Candidate slice foundation since 000072

Patch `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation` introduces the first executable `CatalogItem` `candidate-reference-slice` foundation.

The slice does not make Catalog-demo canonical. It records candidate evidence in:

```text
PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md
```

The candidate foundation demonstrates paged list, opaque-ID detail, business-key lookup by `sku`, create, full update, bodyless delete, DTO boundary, Bean Validation boundary, standard error-body evidence, application-layer delegation and documented-deferred-security evidence.

Remaining canonicalization blockers include durable persistence evidence, implemented management security, OpenAPI evidence, strict gate promotion and explicit canonical readiness review.

## Forensic review after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` reviews the `CatalogItem` candidate foundation introduced by `000072`.

The review confirms:

- the candidate endpoint contract from `000071` is implemented at HTTP level;
- report-only findings are reduced from `12` to `9`;
- CatalogItem is a valid `candidate-reference-slice foundation`;
- Catalog-demo remains non-canonical;
- target comparison and target delivery remain blocked.

The review also records cleanup required before canonical promotion:

- replace public request DTO exposure of the persistence-facing `Range` embeddable;
- add service-level update validation symmetry;
- remove or isolate the legacy unpaged service list helper;
- align G5 report-only readiness detection with the candidate evidence file;
- keep durable persistence, implemented management security and OpenAPI evidence as canonicalization blockers.

The next recommended patch is `000074_springmaster_catalog_demo_candidate_slice_alignment`.



## Candidate evidence alignment since 000074

Since `000074_springmaster_catalog_demo_candidate_slice_alignment`, current CatalogItem candidate state is also recorded in:

```text
PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json
```

This file is the machine-readable source for the report-only G5 heuristic. Historical `legacy-demo-seed` wording in this readiness plan remains useful as context, but it is no longer the current classification when the JSON evidence declares `sliceState=candidate-reference-slice` and `canonicalState=not-canonical`.

Catalog-demo remains not canonical. The next canonicalization blockers are unchanged: durable persistence, implemented management security, OpenAPI evidence, DTO-boundary cleanup, service validation symmetry and final readiness review.

## DTO/validation cleanup since 000075

The `CatalogItem` candidate-reference-slice now has a cleaner public request boundary:

- `CatalogItemCreateDTO` and `CatalogItemUpdateDTO` use public `CatalogItemAvailabilityDTO`;
- persistence-facing `Range` is no longer part of public request DTOs;
- update validation is symmetric with create validation at the service boundary;
- the unpaged service helper `CatalogItemService.list()` has been removed.

This improves candidate readiness but does not make Catalog-demo canonical.


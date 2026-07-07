# Catalog-demo Candidate Slice Contract Plan

## Purpose

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` defines the contract for the first standards-aligned Catalog-demo `CatalogItem` candidate slice.

The plan translates the report-only findings baseline from `000070` into a concrete implementation scope for a later code patch. It does not change Java code, Maven configuration, gate tooling, database migration files, templates, target-project configuration or generated target-project artifacts.

The next implementation patch may use this document as the acceptance baseline for a `candidate-reference-slice`. It must not claim `canonical-reference-slice` status unless all ADR-0007 canonical evidence is complete and explicitly recorded.

## Source baseline

The plan is based on the Springmaster state after:

```text
000070_springmaster_report_only_gate_findings_baseline_review
springmaster_export_full_2026-07-01T05-39-43-150103Z.zip
```

Relevant accepted rule sources:

| Rule source | Relevance for this plan |
|---|---|
| `ADR-0002` | API boundary, endpoint vocabulary, DTO boundary, status/error behavior |
| `ADR-0003` | controller/service/use-case and transaction boundary |
| `ADR-0004` | opaque public ID, `DomainEntity`, business-key separation |
| `ADR-0005` | endpoint classification, permission vocabulary, deferred security evidence |
| `ADR-0006` | report-only gate behavior and strict-promotion boundary |
| `ADR-0007` | Catalog-demo lifecycle states and evidence requirements |

## Current state before the candidate slice

The existing Catalog-demo `CatalogItem` implementation remains `legacy-demo-seed`.

Current useful seed behavior:

- resource path base exists under `/api/demo/catalog/items`;
- create returns `201 Created`;
- duplicate SKU produces conflict semantics;
- the domain object already extends `DomainEntity`;
- `sku` exists as explicit business key;
- mapper, service, validator and controller tests exist;
- report-only gate tooling can observe the current gaps.

Current known non-canonical behavior:

- list response is a plain `List<CatalogItemDTO>` rather than a paged response envelope;
- public detail lookup uses `/{sku}` rather than opaque `/{id}`;
- no explicit `by-sku` lookup endpoint exists;
- no full update endpoint exists;
- no bodyless single delete endpoint exists;
- canonical query parameters `page`, `size`, `sortBy`, `sortDir` are not public evidence yet;
- errors are controller-local ad-hoc `Map<String,Object>` bodies;
- validation is not yet Bean Validation at the public DTO boundary;
- security is not implemented and not yet represented with explicit endpoint evidence;
- Catalog-demo has no readiness evidence file that marks a candidate slice.

These gaps are accepted only because the code is not canonical yet.

## Candidate slice identity

The first implementation patch based on this plan should explicitly label the `CatalogItem` implementation state as:

```text
candidate-reference-slice
```

The candidate slice means:

- it is intended to be standards-aligned;
- it is eligible for report-only diagnostic improvement;
- it is not yet the final canonical reference;
- it may carry explicit deferrals;
- it must not enable target-project comparison or target-project delivery.

The implementation patch should add or update a small human-readable readiness/evidence artifact. Preferred location:

```text
PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md
```

That evidence file should record the slice state, implemented contracts, deferrals and report-only gate result.

## Required public endpoint contract

The candidate slice should expose the following public API shape.

| Operation | Method and path | Response | Candidate requirement |
|---|---|---|---|
| Paged list | `GET /api/demo/catalog/items?page=&size=&sortBy=&sortDir=` | `200 OK` with `PagedResponseDTO<CatalogItemListItemDTO>` or equivalent Springmaster envelope | mandatory |
| Detail by public ID | `GET /api/demo/catalog/items/{id}` | `200 OK` with `CatalogItemDTO`; `404` when absent | mandatory |
| Lookup by SKU | `GET /api/demo/catalog/items/by-sku/{sku}` | `200 OK` with `CatalogItemDTO`; `404` when absent | mandatory as business-key lookup evidence |
| Create | `POST /api/demo/catalog/items` | `201 Created` with `CatalogItemDTO`; `Location` points to `/{id}` | mandatory |
| Full update | `PUT /api/demo/catalog/items/{id}` | `200 OK` with updated `CatalogItemDTO`; `404` when absent | mandatory |
| Single delete | `DELETE /api/demo/catalog/items/{id}` | `204 No Content`; `404` when already absent | mandatory |

The following endpoint shapes are explicitly out of scope for the candidate slice:

- `/all`;
- `/list` as a new Springmaster endpoint;
- body-bearing single `DELETE`;
- public `findOne`, `findFirst` or `findLast` vocabulary;
- delete-multiple;
- complex search;
- relationship endpoints;
- lifecycle/state transition commands;
- `/reference-data`;
- `/options`, unless a real bounded selector use case is documented in a later patch.

## Query and sorting contract

The list endpoint must expose the canonical query vocabulary:

| Parameter | Candidate default | Rule |
|---|---|---|
| `page` | `0` | zero-based page index |
| `size` | implementation default, bounded | invalid or excessive values must not silently bypass validation |
| `sortBy` | `sku` or another documented allowed field | canonical public sort parameter |
| `sortDir` | `ASC` | allowed values should be documented and tested |

The candidate slice may implement a narrow allow-list of sort fields. Recommended first allow-list:

```text
sku, name
```

Unsupported sort fields should produce `400 Bad Request` with the standard error response body.

The candidate slice must not use `sort` as its canonical public parameter. If later backward compatibility is required, it must be documented as legacy compatibility and not as the Springmaster reference default.

## DTO matrix

The candidate slice should use explicit DTO roles.

| DTO | Purpose | Candidate requirement |
|---|---|---|
| `CatalogItemCreateDTO` | create request body | mandatory |
| `CatalogItemUpdateDTO` | full update request body | mandatory |
| `CatalogItemDTO` | detail/create/update response | mandatory |
| `CatalogItemListItemDTO` | paged list item response | mandatory |
| `CatalogItemOptionDTO` | bounded selector response | deferred |
| `CatalogItemSearchDTO` | complex search request | deferred |
| `CatalogItemDeleteMultipleCommandDTO` | bulk delete command | deferred |

DTOs should not expose JPA entities, repositories, Spring Data `Page`, framework request objects or internal storage structures.

## Identity and business-key contract

The candidate slice should demonstrate the ADR-0004 identity model:

| Concept | Candidate decision |
|---|---|
| Public resource identity | opaque string `id` |
| Business key | `sku` |
| Detail path | `/{id}` |
| Alternative lookup | `/by-sku/{sku}` |
| Create `Location` | points to `/{id}`, not `/{sku}` |
| SKU mutability | preferably immutable after create for the candidate slice; if mutable, conflict and lookup behavior must be tested |

The candidate implementation may remain in-memory. A real JPA repository, Liquibase table or DBTool migration is not required for the first candidate slice. If persistence remains in-memory, the evidence file must state that the candidate proves public identity and boundary semantics, not durable database persistence.

## Validation contract

The implementation patch should move public request validation to the DTO boundary.

Candidate expectations:

- request bodies use `@Valid @RequestBody` or an equivalent Bean Validation boundary;
- required fields such as `sku` and `name` are validated by DTO constraints;
- invalid create and invalid update requests return `400 Bad Request`;
- unsupported query parameters or invalid query values return `400 Bad Request`;
- duplicate `sku` returns `409 Conflict`;
- not-found `id` and not-found `sku` return `404 Not Found`;
- validation errors use the standard error body with `violations` when field-level errors exist.

Manual validators may remain internally when they express domain rules, but they must not be the only public boundary evidence for required request fields.

## Error and status-code contract

The candidate slice should demonstrate standard error bodies for at least:

| Scenario | Status | Error type expectation |
|---|---:|---|
| invalid request body | `400` | `VALIDATION_FAILED` |
| invalid list query | `400` | `VALIDATION_FAILED` or `INVALID_REQUEST` |
| unknown resource ID | `404` | `RESOURCE_NOT_FOUND` |
| unknown SKU lookup | `404` | `RESOURCE_NOT_FOUND` |
| duplicate SKU | `409` | `CONFLICT` or more specific conflict type aligned with the standard vocabulary |

Every error response must include at least the required error contract fields, especially `errorId`, `status`, `error`, `errorType`, `message`, `path` and `method`.

`messageKey`, `correlationId`, `traceId`, `localMessage` and rich `violations` may be implemented or explicitly deferred. When deferred, the evidence file must say so.

## Application-layer and mapping contract

The candidate code should make `ADR-0003` observable.

Required shape:

- controller remains thin HTTP adapter;
- controller delegates to a CatalogItem application service, query service and/or command service;
- controller does not own storage structures;
- controller has no repository or `EntityManager` dependency;
- controller has no transaction demarcation;
- mapper does not call repositories, services, authorization components or external clients;
- business-key normalization and conflict checks stay outside the controller;
- tests demonstrate public behavior through controller/API boundary and service-level behavior where useful.

The candidate slice may keep a simple in-memory store behind the service boundary. That store is not the public contract.

## Security classification contract

The first candidate slice may choose exactly one of these security modes.

| Mode | Meaning | Candidate acceptance |
|---|---|---|
| `documented-deferred-security` | endpoint classification and permissions are documented, but enforcement is intentionally deferred | acceptable for the first candidate slice |
| `implemented-management-security` | authentication and permission checks are implemented with positive/negative tests | acceptable but not required for the first candidate slice |

If the first code patch uses `documented-deferred-security`, it must record endpoint classification and intended permissions.

Recommended candidate permission vocabulary:

| Operation | Permission |
|---|---|
| list/detail/by-sku | `catalog:item:read` |
| create | `catalog:item:create` |
| update | `catalog:item:update` |
| delete | `catalog:item:delete` |

Unclassified management endpoints are not acceptable for a candidate evidence claim.

## Report-only finding target map

The implementation patch after this plan should treat the `000070` report-only findings as follows.

| Current finding area | Current state | Candidate target |
|---|---|---|
| G0 rule-source findings | positive ADR evidence | remain stable |
| G1 query parameters | missing canonical pageable query evidence | close or convert to positive evidence through `page`, `size`, `sortBy`, `sortDir` |
| G1 ad-hoc error body | current controller uses `Map<String,Object>` | close through standard error response DTO/handler |
| G1 create status evidence | `201 Created` already present | keep, but change `Location` to opaque `id` |
| G1 missing delete status evidence | delete absent | close through bodyless `DELETE /{id}` |
| G4 security classification | missing implemented security evidence | either keep as documented deferral with evidence or implement management security |
| G5 Catalog readiness | manual because legacy seed | change to candidate evidence, still not canonical |

No finding should be promoted to strict as part of the candidate implementation patch.

## Required test and validation evidence for the implementation patch

The next code patch should include tests or verifiable evidence for at least:

- create valid item returns `201` and `Location` with opaque `id`;
- duplicate `sku` returns `409` with standard error body;
- invalid create returns `400` with standard error body;
- paged list returns canonical envelope and honors `sortBy`/`sortDir`;
- invalid sort field returns `400`;
- detail by `id` returns `200` or `404`;
- lookup by `sku` returns `200` or `404`;
- full update returns `200` and does not bypass validation;
- delete by `id` returns `204` and subsequent detail returns `404`;
- unsupported/non-canonical endpoint shapes such as `/all` are not introduced;
- gate report still runs in report-only mode and target-project input remains rejected.

Because the next patch will be code/demo work, it must run Maven tests and the report-only gate validation.

## Explicit deferrals for the candidate slice

These deferrals are acceptable for the first candidate slice when recorded in evidence:

| Deferral | Reason |
|---|---|
| real database repository | candidate proves boundary contract first; persistence durability can follow later |
| Liquibase migration | no durable table is required for the first candidate contract slice |
| OpenAPI schema snapshot | source/gate and MockMvc evidence may precede strict OpenAPI tooling |
| implemented security | may remain `documented-deferred-security` with permissions and rationale |
| `/options` | no bounded selector use case exists yet |
| delete-multiple | no bulk use case exists yet |
| complex search | no search use case exists yet |
| relationships and nested aggregate commands | only one resource exists in the first slice |
| lifecycle state transitions | no lifecycle exists yet |

A deferral is invalid when it introduces a non-canonical replacement. For example, `/all` must not be used as a placeholder for paged list or `/options`.

## Acceptance criteria for the next implementation patch

The next implementation patch should be accepted only when all of the following are true:

1. The patch states that it creates a `candidate-reference-slice`, not a canonical slice.
2. No target project path is touched.
3. The public endpoint contract in this document is implemented or explicitly narrowed with rationale.
4. DTO roles are explicit.
5. Errors use the standard error contract.
6. Query parameters use `sortBy`, not canonical `sort`.
7. `/all` is absent.
8. Bodyless delete is present.
9. Security classification evidence exists.
10. Candidate evidence is recorded.
11. `mvn test` passes.
12. Report-only gate validation passes as tool execution, while findings remain non-blocking.
13. A Full-ZIP export is produced and its path is printed.

## Status after this plan

After `000071`, the Catalog-demo workstream is ready for a narrow code/demo patch.

The recommended next patch is:

```text
000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation
```

That patch should be treated as a code/demo patch, not documentation-only.



## Implementation status after 000072

Patch `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation` implements the first `CatalogItem` candidate foundation described by this plan.

Implemented candidate evidence includes:

- paged collection endpoint with `page`, `size`, `sortBy` and `sortDir`;
- detail endpoint by opaque `id`;
- business-key lookup endpoint `/by-sku/{sku}`;
- create endpoint with `201 Created` and `Location` based on opaque `id`;
- full update endpoint by `id`;
- bodyless single delete endpoint by `id`;
- explicit `CatalogItemUpdateDTO` and `CatalogItemListItemDTO`;
- demo-local standard error response body with `errorId`, `status`, `error`, `errorType`, `message`, `path`, `method` and field-level `violations`;
- `documented-deferred-security` evidence.

The slice remains `candidate-reference-slice`, not `canonical-reference-slice`.

## Forensic review outcome after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` confirms that `000072` implemented the planned `CatalogItem` candidate foundation substantially as specified.

The implementation is accepted as candidate baseline, not canonical baseline.

Remaining alignment work before canonical promotion:

- DTO boundary cleanup for the public availability/range value;
- direct service update validation symmetry;
- cleanup or isolation of the legacy unpaged service list helper;
- G5 report-only detection alignment so candidate evidence is no longer reported as pure legacy seed state.

These items are assigned to the recommended next patch `000074_springmaster_catalog_demo_candidate_slice_alignment`.

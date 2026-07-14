# API Standards

Springmaster API standards define generic conventions for future Fachprojekt backends and for the Catalog-demo reference implementation.

The initial standards were extracted from existing IDM API-readiness ADR themes. They are not copied as IDM-specific rules. Springmaster keeps only the reusable API contract and documents it as master-level convention.

## Extracted standards since 000044

| Standard | Document | Current enforcement state |
|---|---|---|
| API request validation | `API_REQUEST_VALIDATION_STANDARD.md` | documented; Catalog-demo and tests follow later |
| Required fields and OpenAPI required properties | `REQUIRED_FIELDS_OPENAPI_STANDARD.md` | documented; OpenAPI contract tests follow later |
| List, filter and query contracts | `LIST_FILTER_QUERY_STANDARD.md` | documented; Core paging support already exists, gates follow later |
| Command HTTP semantics | `COMMAND_HTTP_STANDARD.md` | documented; delete-body and command tests follow later |
| External IDs and OpenAPI boundary | `EXTERNAL_ID_OPENAPI_BOUNDARY_STANDARD.md` | documented; OpenAPI/YAML readiness gates follow later |
| Endpoint operation contract backlog | `API_ENDPOINT_CONTRACT_DEFINITION_BACKLOG.md` | backlog documented with 000045; core decisions converted into standard with 000046 |
| Endpoint contract standard | `API_ENDPOINT_CONTRACT_STANDARD.md` | canonical list/detail/create/update/delete/bulk/search endpoint contracts documented; gates follow later |
| API error contract standard | `API_ERROR_CONTRACT_STANDARD.md` | canonical error body, status mapping and future error gates documented with 000048 |
| DTO boundary and validation standard | `DTO_BOUNDARY_AND_VALIDATION_STANDARD.md` | canonical DTO roles, boundary validation, entity exposure prohibition and future DTO gates documented with 000049 |
| Command and relationship endpoint standard | `COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md` | canonical command, assignment, relationship, nested aggregate and bulk-operation endpoint rules documented with 000053 |
| API contract gate concept | `API_CONTRACT_GATE_CONCEPT.md` | layered OpenAPI, MockMvc, reflection, security and Catalog-demo gate model documented with 000055; implementation follows later |
| Query/reference-data consistency standard | `API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md` | `sortBy`, complete-result-set `/all`, `/options` and ADR-backed `/reference-data` resolved with 000058/000091 |
| Result-set export/all standard | `API_RESULT_SET_EXPORT_ALL_STANDARD.md` | frontend export, backend batch, complete result-set `/all`, count and empty/error behavior documented with 000091 |
| Count response contract candidate | `API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md` | optional `/count` and `/search/count` response shape with required `totalElements`; Core DTO and CatalogItem evidence now exist |
| Query operations closure review | `QUERY_OPERATIONS_CONTRACT_CLOSURE_REVIEW.md` | closure review for paged list, `/all`, `/count`, Core query-operation interfaces and CatalogItem service adoption after 000102 |
| Query contract gate report | `QUERY_CONTRACT_GATE_REPORT.md` | report-only gate artifact, rule IDs and finding schema for query-contract diagnostics since 000106 |
| Detail/Lookup contract report | `DETAIL_LOOKUP_CONTRACT_REPORT.md` | report-only gate artifact and CatalogItem golden evidence for `/{id}` and `/by-sku/{sku}` since 000118 |
| Write API contract report | `WRITE_API_CONTRACT_REPORT.md` | report-only gate artifact and CatalogItem golden evidence for `POST`, `PUT` and bodyless `DELETE` since 000119 |
| Error identity and status-code consistency standard | `API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md` | `errorId`/correlation/message-key semantics and first-slice status defaults resolved with 000059 |

## ADR-backed decision since 000061

Patch `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepts `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md`. The endpoint, DTO, validation, query/reference-data, error, command and first-slice status-code standards are now consolidated as an accepted architecture decision for new Springmaster reference APIs.

Strict gate execution still requires `ADR-0006 Verification and Gate Strategy`, and operationId/tag/schema naming remains a separate standard gap.


## Detail/Lookup report since 000118

Patch `000118_springmaster_detail_lookup_contract_report` adds report-only Detail/Lookup evidence for CatalogItem. The report covers the canonical opaque-id detail endpoint `GET /api/demo/catalog/items/{id}` and the unique alternate-key lookup endpoint `GET /api/demo/catalog/items/by-sku/{sku}`. It records path variables, DTO response evidence, global `RESOURCE_NOT_FOUND` behavior, MockMvc coverage, OpenAPI route evidence and create-`Location` detail follow-up consistency.

The report remains report-only. Strict-gate promotion is deferred until Write and Validation/OpenAPI report coverage exists and generated-slice adoption criteria are defined.

## Write API report since 000119

Patch `000119_springmaster_write_api_contract_report` adds report-only Write API evidence for CatalogItem. The report covers `POST /api/demo/catalog/items`, `PUT /api/demo/catalog/items/{id}` and bodyless `DELETE /api/demo/catalog/items/{id}`. It records CreateDTO/UpdateDTO request-body evidence, `201 Created` with `Location`, `200 OK` update responses, `204 No Content` deletes, global `VALIDATION_FAILED`, `RESOURCE_NOT_FOUND` and `CONFLICT` error behavior, MockMvc coverage and OpenAPI route/body evidence.

The report remains report-only. Bulk delete, state commands, relationship commands, command precheck, optimistic locking and persistent transaction templates remain deferred follow-up topics.

## Boundary to IDM

IDM ADR material is source material only. These standards do not instruct IDM, Personnel, Contacts or Orders to change immediately. Existing projects remain comparison candidates after Catalog-demo demonstrates the standards and the gate concept is available.

## Reference implementation expectation

Catalog-demo should implement the API standards through `CatalogItem` first.

The first CatalogItem API should demonstrate:

- paged list endpoint for UI tables,
- complete-result-set `/all` endpoint for export/batch use cases when the slice is promoted to export-ready canonical status,
- optional count-only endpoint using required `totalElements` when a badge/dashboard/preflight use case exists,
- optional `/options` endpoint only for bounded selector use cases,
- detail endpoint,
- create endpoint,
- update endpoint,
- bodyless delete endpoint,
- request DTO validation,
- OpenAPI required-field visibility,
- opaque string external IDs,
- standard response codes,
- tests for positive and negative contract cases,
- standard command and relationship endpoint behavior when Catalog-demo introduces relationships, assignments, bulk operations or state transitions,
- standard API error body for validation, not-found and conflict scenarios,
- dedicated create/update/command DTOs with Bean Validation,
- response DTOs, `PagedResponseDTO` and `CountResponseDTO` instead of entity, Spring Data or ad-hoc response leakage;
- typed query-operation interfaces at the service/application boundary, without generic Spring-MVC controller inheritance.

Since patch `000046_springmaster_api_endpoint_contract_standard`, Catalog-demo must follow the canonical endpoint standard when CatalogItem becomes the reference slice. The collection path is the canonical paged list endpoint, `/all` is the complete-result-set endpoint for frontend export and batch/integration consumers, `/options` is the bounded selector endpoint, public `findOne`/`findFirst`/`findLast` vocabulary is prohibited for management APIs, single deletes are bodyless, and delete-multiple is a collection command rather than a body-bearing `DELETE`.

## Expected gates

The API standards should become enforceable through:

- controller/integration tests for HTTP behavior,
- OpenAPI contract tests for generated schema and endpoint structure,
- reusable test helpers where possible,
- optional ArchUnit rules for controller boundary and dependency checks,
- Maven-bound quality gates once the checks are stable.

Until those gates exist, the standards are documentation-first and must be demonstrated by Catalog-demo before being applied to existing target projects.

Since `000103_springmaster_query_operations_contract_closure_review`, the paged-list, complete-result-set `/all`, count-only and Core query-operation interface pattern is considered reference-demonstrated at CatalogItem candidate level. Strict target-project enforcement remains deferred.

## Real-app comparison since 000047

Patch `000047_springmaster_real_app_pattern_forensics` compares IDM and Personnel against the current Springmaster API standards.

Relevant API conclusions:

- IDM contributes strong OpenAPI contract-test examples for required fields, list/filter parameters and bodyless assignment deletes.
- Personnel contributes richer aggregate commands, state transitions, metadata endpoints, current-user capabilities and reference-data patterns.
- Springmaster keeps the 000046 endpoint standard as the new-reference baseline and treats IDM `/list`, Personnel controller-level `Pageable` and public `Page<DTO>` responses as comparison inputs, not as new canonical defaults.
- Patch `000048_springmaster_api_error_contract_standard` resolves the first high-priority gap by defining the canonical error body, error types, status mapping and future error gates. Patch `000049_springmaster_dto_boundary_and_validation_standard` resolves the next high-priority gap by defining inbound and outbound DTO roles, controller boundary rules, validation activation, entity exposure prohibitions and DTO/OpenAPI gate targets. Springmaster still needs explicit standards for relationship commands, state transitions, security boundaries, metadata/reference-data, mapping and persistence foundations. The controller/service/use-case/transaction boundary is resolved as a documentation-level standard with 000050.

## Related application-layer standard since 000050

Patch `000050_springmaster_controller_service_usecase_transaction_standard` adds the non-API standard `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md`. It complements these API standards by defining where controller logic ends, where query/command/use-case services begin, where transactions live and which future architecture gates should protect the HTTP boundary.

## Security boundary since 000052

Patch `000052_springmaster_security_permission_boundary_standard` adds the cross-cutting security and permission standard under `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md`.

API standards continue to define endpoint shapes, DTOs and error responses. The security standard defines which endpoints are public, authenticated, management, technical or system endpoints; how permission names are formed; how role-to-permission mapping is tested; and how current-user/capability endpoints should be shaped.

For new reference APIs, missing authentication maps to `401 UNAUTHORIZED`, missing permission maps to `403 FORBIDDEN`, and management endpoints are protected by default unless explicitly documented otherwise.



## Command and relationship endpoint specialization since 000053

Patch `000053_springmaster_command_relationship_endpoint_standard` adds `COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md` as the specialization for operations that are not simple resource CRUD.

The endpoint standard from 000046 remains the baseline for list, detail, create, update and single delete. The 000053 specialization defines how Springmaster handles state-transition commands, collection commands, assignment and relationship endpoints, bulk relationship changes, nested aggregate commands, command DTOs, permission mapping, transaction/audit expectations and future OpenAPI/MockMvc/security gates.

For new reference APIs, body-bearing `DELETE` remains prohibited. Bulk delete, remove-multiple and assignment changes that need structured input use `POST` or idempotent `PUT` command endpoints with dedicated DTOs.

## Mapping boundary since 000054

Patch `000054_springmaster_mapping_standard` adds the cross-cutting mapping standard under `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md`.

API standards define public endpoint, DTO, validation and error contracts. The mapping standard defines how those public DTOs are created from command inputs, entities, read models, relationship summaries and option/reference-data structures without leaking persistence types or hiding business logic in mapper code.

For new reference APIs, mapped public response shapes must be verifiable through OpenAPI and tests. Mappers must not introduce repository access, transaction ownership, authorization decisions or ad-hoc error behavior.

## API contract gate concept since 000055

Patch `000055_springmaster_api_contract_gate_concept` adds `API_CONTRACT_GATE_CONCEPT.md` as the bridge from documentation-first standards to mechanically verifiable API quality gates.

The concept defines a layered gate model for OpenAPI contract checks, MockMvc behavior tests, Java boundary scans, security checks, Catalog-demo reference proof and later read-only target-project comparison. It does not implement those gates yet.

For new reference APIs, Catalog-demo must not be considered canonical by compilation alone. It needs demonstrable endpoint, DTO, validation, error, mapping and security-classification checks, with explicit markers for any deferred gates.


## API standard consistency review since 000057

Patch `000057_springmaster_standard_consistency_and_adr_gap_review` reviews the API standards before OpenAPI or MockMvc gate tooling is implemented.

API-specific findings:

- Patch `000058_springmaster_api_query_reference_data_consistency_standard` resolves the P0 query/reference-data vocabulary gap by making `sortBy` canonical, treating `sort` as legacy/target-comparison vocabulary, making `/options` the selector endpoint and requiring ADR-backed `/reference-data` for broader bounded read models. Patch `000091_springmaster_list_query_export_all_contract` amends this by making `/all` canonical for documented complete-result-set export/batch semantics and keeping ambiguous `/all` as non-canonical.
- OpenAPI operationId, tag, schema, error schema and security scheme naming require a dedicated standard before reusable OpenAPI assertions become strict.
- Error contract gates need an operational clarification for `errorId`, correlation ID, trace ID, message keys and localized messages.
- Bodyless single delete and the prohibition of public `findOne`/`findFirst`/`findLast` endpoint vocabulary are considered ready-for-tooling candidates.

Until these gaps are closed, API gate tooling must remain narrow and must not encode unsettled contract details.


## Query/reference-data consistency since 000058

Patch `000058_springmaster_api_query_reference_data_consistency_standard` resolves the first P0 consistency gap from the 000057 review. New Springmaster reference APIs use `sortBy` and `sortDir` for sorting, not `sort`. Selector data uses `/options`; broader bounded reference data may use `/reference-data` only with ADR-backed semantics. Since patch `000091_springmaster_list_query_export_all_contract`, `/all` is canonical for complete result-set retrieval when it shares the paged query's filters, sorting, security and data-scope semantics and does not silently truncate. Legacy `/all` endpoints that do not satisfy this contract remain comparison findings.


## Result-set export/all consistency since 000091

Patch `000091_springmaster_list_query_export_all_contract` adds `API_RESULT_SET_EXPORT_ALL_STANDARD.md` and updates the query/list standards so frontend exports and backend batch/integration consumers can request the complete matching result set. The canonical simple shape is `GET /api/<domain>/<resources>/all`; complex search DTOs use `POST /api/<domain>/<resources>/search/all` unless an ADR-backed job/export resource is required.

The `/all` endpoint is paired with the paged list, reuses the same documented filters, `sortBy` and `sortDir`, applies the same security/data-scope predicates and returns a complete JSON array of public list/export DTOs. It is not an `/options` replacement and must not silently cap results at the public page-size limit.


## Error identity and status-code consistency since 000059

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` resolves the API error identity and status-code narrowing gap from the consistency review.

For new reference APIs:

- `errorId` is required and identifies one concrete error occurrence;
- `correlationId`, `traceId`, `messageKey` and `localMessage` are optional public fields unless a later standard makes them mandatory;
- create defaults to `201 Created`;
- full update defaults to `200 OK` with response body;
- single bodyless delete defaults to `204 No Content` and repeated strict delete returns `404`;
- delete-multiple defaults to `200 OK` with result DTO;
- `202 Accepted` requires a deterministic status, job or operation resource.




## Command Precheck Endpoint Standard since 000082

Patch `000082_springmaster_command_precheck_capability_standard` adds `COMMAND_PRECHECK_ENDPOINT_STANDARD.md` and accepts `ADR-0011-command-precheck-and-capability-boundary.md`.

The standard defines optional side-effect-free command precheck endpoints such as:

```text
GET /api/<domain>/<resources>/{id}/commands/<command>/precheck
```

Prechecks provide UI-consumable command capability information for a concrete actor, target and command. They do not replace command execution validation. The executing command and its precheck must share the same backend policy or guard.

List and bulk UIs are not required to call per-item prechecks. Bulk command execution continues to follow the command and relationship endpoint standard, including the existing atomic/partial-success rules.


## Count query efficiency

- `JPA_COUNT_QUERY_EFFICIENCY_REFERENCE.md`

## JPA count query efficiency since 000105

Persistent implementations must use repository/query-level count queries for `totalElements` and count-only endpoints. The standard reference is `PROJECT_DOCS/STANDARDS/API/JPA_COUNT_QUERY_EFFICIENCY_REFERENCE.md`.


## Query contract gate report since 000106

`QUERY_CONTRACT_GATE_REPORT.md` defines the report-only target for checking paged list, `/all`, optional `/count`, filter parity, sort allowlists, typed query-operation adoption and JPA count-efficiency indicators. The first executable implementation remains follow-up work; strict Maven failure is deferred until ADR-0006 promotion.

## Query contract report tooling since 000107

`QUERY_CONTRACT_GATE_REPORT.md` is now backed by an executable report-only MVP:

```bash
./bin/query-contract-gate-report.sh
```

The command writes a JSON report to `reports/api/query-contract-gate-report.json` by default. The initial implementation validates the Springmaster CatalogItem candidate reference slice and is intentionally not a strict build gate.

## CatalogItem query report golden fixture since 000108

Patch `000108_springmaster_catalogitem_query_contract_report_fixture` commits the first golden JSON fixture for the dedicated query-contract report command:

```text
src/test/resources/tooling/query-contract-gate-report.catalogitem.golden.json
```

`SpringmasterQueryContractReportTest` now compares the generated CatalogItem report with this fixture. This keeps the report schema, summary, resource evidence and finding baseline stable while the command remains report-only.

## OpenAPI query-contract evidence since 000109

Patch `000109_springmaster_query_openapi_contract_evidence` adds `OPENAPI_QUERY_CONTRACT_EVIDENCE.md` and the runtime-generated CatalogItem OpenAPI proof.

The dedicated test `CatalogItemOpenApiQueryContractTest` loads `/api-docs` and verifies that the public OpenAPI contract exposes the same query vocabulary already proven by source/report evidence:

- paged list: `page`, `size`, `sortBy`, `sortDir`, `sku`, `name`;
- `/all`: `sortBy`, `sortDir`, `sku`, `name`, without paging parameters;
- `/count`: `sku`, `name`, without paging or sorting parameters;
- `/count` response schema: `CountResponseDTO.totalElements`.

This evidence remains reference-project verification. It does not yet promote generated target-project OpenAPI scans or strict gate failure semantics.

## Backend API Pattern operational roadmap since 000115

Patch `000115_springmaster_backend_api_pattern_operational_roadmap` adds the operational roadmap `PROJECT_DOCS/PLANNING/BACKEND_API_PATTERN_OPERATIONAL_ROADMAP.md`.

The roadmap freezes the current Query/List/All/Count maturity as complete at candidate-reference level and prioritizes the next API pattern families:

1. global API error contract in System-Core;
2. detail and alternate-key lookup contracts;
3. create, update and delete write API contracts;
4. request-validation and OpenAPI required-field gates;
5. generated service-slice API pattern adoption planning.

Further Query work, strict gate promotion, cursor/keyset pagination and async export are intentionally deferred until these broader API foundations are closed.

## Request Validation / OpenAPI gate since 000120

Patch `000120_springmaster_request_validation_openapi_gate` adds `REQUEST_VALIDATION_OPENAPI_GATE.md` and a report-only executable MVP:

```bash
./bin/request-validation-openapi-gate-report.sh
```

The command writes a JSON report to `reports/api/request-validation-openapi-gate-report.json` by default. The initial implementation validates the Springmaster CatalogItem candidate reference slice and proves alignment between `@Valid @RequestBody` DTO boundaries, Bean Validation required fields, OpenAPI `required` lists and the global `VALIDATION_FAILED` error contract.

The report remains reference-project evidence and does not yet promote generated target-project scans or strict gate failure semantics.

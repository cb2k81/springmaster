# API Contract Gate Concept

## Purpose

This concept defines how the documented Springmaster API standards should become mechanically verifiable before `Catalog-demo` becomes the canonical reference implementation and before existing applications such as IDM, Personnel, Contacts or Orders are supplied by Springmaster.

The concept is documentation-only. It does not add Java test utilities, Maven profiles, ArchUnit rules, OpenAPI parsers, generated reports, Spring Boot test classes, target-project updates or Catalog-demo implementation changes.

## Scope

The concept covers API-facing and API-adjacent gates derived from the Springmaster standards created in patches `000044` through `000054`.

It covers gates for:

* endpoint vocabulary and HTTP method contracts;
* request validation and OpenAPI required fields;
* DTO boundary and public schema shape;
* list, filter, query, paging and bounded selector contracts;
* command, delete, delete-multiple and relationship endpoints;
* error response shape and status-code mapping;
* opaque external IDs and OpenAPI boundary behavior;
* security and permission classification at the API boundary;
* controller/service/use-case/transaction boundary indicators that are visible from API code;
* mapping and persistence leakage prevention where it affects public contracts.

The concept does not define a production-ready implementation yet. Implementation follows in later Core, Tooling or Demo patches.

## Gate principle

A Springmaster API standard is only mature when it has at least one verification path.

Springmaster uses a layered gate model instead of one monolithic checker:

| Gate layer | Primary mechanism | Purpose |
|---|---|---|
| G0 Documentation gate | standard documents and patch review | ensure a rule exists before Catalog-demo demonstrates it |
| G1 OpenAPI contract gate | generated OpenAPI JSON/YAML assertions | verify public endpoint and schema contracts |
| G2 MVC behavior gate | MockMvc or Spring MVC integration tests | verify runtime HTTP behavior, validation and errors |
| G3 Java boundary gate | reflection, classpath scan or ArchUnit | verify code boundary rules that OpenAPI cannot see |
| G4 Security gate | security integration tests and permission catalog checks | verify authentication, authorization and capability contracts |
| G5 Reference implementation gate | Catalog-demo contract suite | prove that Springmaster standards work together in a realistic demo |
| G6 Target comparison gate | read-only comparison against IDM/Personnel/others | compare existing applications after Catalog-demo is stable |

The first implementable gate generation should focus on G1 and G2 because they directly protect API contracts and are less invasive than architecture-wide rule engines.

## Maturity levels

Each standard requirement should be classified by verification maturity.

| Level | Meaning | Example |
|---|---|---|
| `documented` | rule exists, not mechanically checked | standard says `DELETE` must not have a body |
| `reference-demonstrated` | Catalog-demo demonstrates the rule | CatalogItem delete uses bodyless `DELETE` |
| `test-checked` | local test verifies the rule in a project | MockMvc validates `400` on invalid create DTO |
| `contract-checked` | OpenAPI test verifies the public contract | OpenAPI schema marks create fields as required |
| `architecture-checked` | reflection or ArchUnit prevents code boundary violations | controller must not inject repository |
| `maven-gated` | check is part of a stable Maven/build quality command | `mvn test` or profile fails on contract violation |
| `target-ready` | rule is stable enough for existing-project comparison and later delivery | IDM/Personnel comparison is safe and non-destructive |

A rule must not be used to force target-project changes before it reaches at least `reference-demonstrated` and has a documented target-comparison strategy.

## Gate input artifacts

The gate system should use stable generated or source artifacts.

| Artifact | Gate usage |
|---|---|
| generated OpenAPI JSON/YAML | endpoint paths, methods, request bodies, required fields, response schemas, operation IDs, security metadata |
| controller classes | annotation and parameter boundary checks |
| DTO classes | validation annotations, entity leakage, naming convention and schema intent checks |
| test fixtures | positive and negative API behavior checks |
| permission constants/catalog | permission naming, operation mapping and capability checks |
| Catalog-demo tests | reference proof for combined standards |
| version metadata | identify which Springmaster standard version a generated project claims to follow |

The OpenAPI artifact is the preferred API-boundary source of truth for public contracts. Java source scans are supporting gates, not a replacement for OpenAPI contract checks.

## OpenAPI contract gate candidates

The first reusable OpenAPI gate should check stable facts that are visible in generated API docs.

| Standard area | Candidate checks |
|---|---|
| Endpoint contract | canonical paths exist; public `findOne`, `findFirst`, `findLast` endpoints are absent; `/options` is bounded selector vocabulary; `/all` is accepted only as documented complete-result-set vocabulary |
| HTTP methods | create uses `POST`; full update uses `PUT`; optional partial update uses `PATCH`; single delete uses bodyless `DELETE`; structured commands use `POST` or idempotent `PUT` |
| Request bodies | JSON write endpoints declare request bodies where required; single delete has no request body; body-bearing `DELETE` is absent |
| Required fields | create/update/command DTO schemas expose required fields according to Bean Validation and OpenAPI rules |
| Query contract | paged list uses explicit `page`, `size`, `sortBy`, `sortDir` and documented filter parameters; generated `arg0`/`arg1` style parameters are absent |
| Response shapes | paged responses expose Springmaster external paging shape, not Spring Data `Page` internals; response bodies use DTO schemas, not entity schemas |
| Error contract | standard error schema is referenced for `400`, `401`, `403`, `404`, `409` and `500` where applicable |
| External IDs | path IDs and ID properties are strings; IDs are not documented as numeric internal database identifiers |
| Command/relationship endpoints | command paths and DTO names follow command/relationship standard; bulk operations use command DTOs |
| Security metadata | protected management endpoints have documented security requirement once OpenAPI security integration exists |

OpenAPI gates should avoid brittle checks on generated ordering, descriptions or tool-specific formatting unless those fields are explicitly part of the public contract.

## MockMvc behavior gate candidates

MockMvc or equivalent Spring MVC tests should verify behavior that OpenAPI cannot prove reliably.

| Behavior | Candidate tests |
|---|---|
| Positive create/update/detail/list/delete flow | prove canonical endpoint behavior for a reference resource |
| Boundary validation | invalid request body returns `400` with standard error body and `violations` |
| Query validation | invalid `page`, `size`, `sortDir` or unsupported `sortBy` field returns `400` |
| Not-found behavior | unknown ID returns `404` with standard error body |
| Conflict behavior | duplicate business key or version conflict returns `409` |
| Delete behavior | bodyless delete works; delete with body is not required or not accepted as contract |
| Command behavior | command endpoint returns the 000059 default status: `200` with result DTO when meaningful, `204` with no body for simple completion, `201` for created resource, `202` only with status/job/operation DTO |
| Relationship behavior | add/remove relationship returns expected status and error behavior |
| Security behavior | unauthenticated returns `401`; authenticated without permission returns `403` |

The first Catalog-demo API slice should contain a minimal but representative MockMvc contract suite before the slice is treated as canonical.

## Java boundary gate candidates

OpenAPI cannot see every architectural boundary. Later Java gates should check boundary rules from the non-API standards.

| Boundary | Candidate checks |
|---|---|
| Controller boundary | controllers do not inject repositories or `EntityManager`; controllers are not `@Transactional` |
| DTO boundary | controller request/response signatures do not expose JPA entities or Spring Data `Page<DTO>` for new reference APIs |
| Validation boundary | JSON request-body parameters use `@Valid`; validated query DTOs use `@Validated` or equivalent activation |
| Mapping boundary | mapper classes do not inject repositories, services, external clients or `EntityManager`; mappers are not transactional |
| Persistence boundary | repository interfaces stay below service/use-case boundary |
| Security boundary | management operations have permission checks at service/use-case boundary or an explicitly approved equivalent |
| Package boundary | generated reference projects keep application packages, domain packages and Core package ownership distinct |

Reflection/classpath checks are suitable for a first implementation when ArchUnit would be too heavy. ArchUnit can be introduced later when package boundaries are stable.

## Security and permission gate candidates

Security gates should be introduced after a minimal Catalog-demo security model is deliberately chosen.

Candidate checks:

* every management endpoint has an explicit security classification;
* public endpoints are explicitly allowlisted;
* permission names follow `<domain>:<resource>:<operation>`;
* current-user/capability endpoints expose stable DTOs;
* unauthenticated requests map to the 000048 `401` error contract;
* authenticated but unauthorized requests map to the 000048 `403` error contract;
* role-to-permission mappings are tested, but application code avoids checking role names where permission checks are intended.

Until the security implementation exists, documentation and test plans must mark these checks as deferred rather than silently omitting them.

## Gate sequencing

The recommended implementation sequence is:

1. Define this gate concept as documentation-only.
2. Add Catalog-demo readiness criteria to the standard index.
3. Implement the first OpenAPI JSON assertion helper for endpoint paths, request bodies, required fields and error schemas.
4. Implement the first MockMvc contract test suite for CatalogItem.
5. Add lightweight reflection scans for controller and DTO boundary rules.
6. Add security/capability gates once Catalog-demo has a deliberate auth model.
7. Consider ArchUnit only after package boundaries are stable and the first reflection gates have proved useful.
8. Bind mature gates to a Maven quality command.
9. Use read-only comparison reports for IDM and Personnel.
10. Only then consider target-project delivery.

This sequence prevents Springmaster from prematurely forcing existing applications to comply with standards that have not yet been demonstrated in the reference project.

## Catalog-demo readiness rule

Catalog-demo must not become canonical simply by compiling.

The first CatalogItem reference slice becomes a candidate reference only when it has:

* endpoint paths that satisfy the endpoint contract standard;
* DTOs that satisfy the DTO boundary and validation standard;
* generated OpenAPI that satisfies required-field, request-body and response-shape expectations;
* MockMvc tests for positive and negative behavior;
* standard API error responses for validation, not-found and conflict cases;
* no entity or Spring Data leakage at the public API boundary;
* documented security classification, even if implementation is deliberately deferred in the first slice;
* mapping tests or equivalent assertions for detail, list-item and command/result DTOs;
* a clear list of gates that are still deferred.

A slice that compiles but has no contract tests is not a Springmaster reference slice.

## Target-project boundary

This concept does not authorize any target-project change.

Existing projects such as IDM and Personnel may be compared against future gates only after the gates are proven against Catalog-demo. The first target-project interaction must be read-only comparison, not automatic remediation.

## Reporting expectation

A later gate runner should produce a compact report with:

* checked project name and standard version;
* generated OpenAPI artifact path;
* passed, failed and skipped checks;
* explicit deferred checks;
* file/class references for failures;
* whether the report is reference-only or delivery-blocking.

For now, this report format is a design expectation only.

## Current status

As of `000055_springmaster_api_contract_gate_concept`, the gate model is defined but not implemented.

The next suitable implementation step after the readiness plan is either a concrete CatalogItem code-slice plan or a Core/test-utility patch that starts the first OpenAPI contract assertion helper and Catalog-demo-oriented MockMvc contract plan.

## Catalog-demo readiness plan since 000056

Patch `000056_springmaster_catalog_demo_readiness_plan` adds the Catalog-demo readiness matrix under `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md`.

The readiness plan is the first G5 Catalog-demo reference gate artifact. It does not implement checks, but it defines which checks the first CatalogItem slice must satisfy before becoming canonical. The plan also prevents deferred topics from being silently skipped by requiring explicit readiness status for OpenAPI, MockMvc, Java boundary, security and target-comparison gates.



## Query and reference-data consistency since 000058

Patch `000058_springmaster_api_query_reference_data_consistency_standard` resolves the first P0 gate-blocking consistency gap. Patch `000091_springmaster_list_query_export_all_contract` amends that decision for export/batch use cases. Patch `000098_springmaster_count_response_contract_candidate` narrows optional count-only semantics. Query gates must treat `sortBy` as canonical, `sort` as non-canonical for new reference APIs, `/all` as the complete-result-set vocabulary, `/count` and `/search/count` as optional count-only vocabulary, `/options` as the bounded selector vocabulary and `/reference-data` as ADR-backed broader bounded reference data. Ambiguous or silently capped `/all` endpoints and ad-hoc count endpoint names remain gate findings.


## Count response and query-operations evidence since 000103

Patch `000098_springmaster_count_response_contract_candidate` narrowed optional count-only endpoint behavior. Patches `000099` through `000102` provide the reference evidence: Core `CountResponseDTO`, CatalogItem `/count`, Core query-operation interfaces and CatalogItem service adoption.

Gate impact:

- report-only G1 diagnostics may recognize `GET /api/<domain>/<resources>/count` and `POST /api/<domain>/<resources>/search/count` as the only candidate count-only endpoint shapes;
- count response schemas should expose required `totalElements` and avoid incompatible property names such as `count`, `total` or `totalCount`;
- count endpoints should not expose public `page`/`size` controls and should not semantically depend on `sortBy`/`sortDir`;
- filtered and zero-result count behavior is now CatalogItem reference evidence;
- G3 Java-boundary diagnostics may treat service-level `ResultSetQueryOperations` adoption as the preferred typed query contract;
- strict count and query-operation gates remain deferred until the gate implementation itself is stable and explicitly promoted under ADR-0006.


## Error identity and status-code gate readiness since 000059

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` resolves the error identity and status-code narrowing gap from the consistency review.

The first API contract gate tooling seed may now treat these checks as `ready-for-tooling` once the concrete helper technology is selected:

- error responses include required `errorId`;
- error schemas expose or intentionally omit optional `messageKey`, `correlationId`, `traceId` and `localMessage` fields;
- validation violations support public field names and may support `messageKey`;
- create operations default to `201`;
- full update defaults to `200` with body for Catalog-demo;
- bodyless single delete defaults to `204` on success and `404` when already absent;
- delete-multiple defaults to `200` with result DTO when introduced;
- `202` is accepted only when the OpenAPI contract exposes a status/job/operation result.



## ADR-0006 acceptance update

Patch `000062_springmaster_adr_0006_verification_and_gate_strategy` accepts the verification and gate strategy for this concept.

Accepted clarifications:

- the first API contract gate tooling seed must run in `report-only` mode;
- strict execution requires explicit strict-readiness and stable implementation evidence;
- severities are `BLOCKER`, `ERROR`, `WARNING`, `INFO` and `MANUAL_REVIEW`;
- future Maven profiles are `springmaster-gates-report`, `springmaster-gates-strict` and `springmaster-gates-target-compare`;
- detailed output belongs under `target/springmaster-gates/<gate-run-id>/`;
- target-project comparison remains read-only and non-destructive.

This update does not implement gate tooling. It makes the concept ADR-backed for the first report-only tooling seed.

## ADR-0003 Java boundary rule source since 000063

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts the application-layer and transaction-boundary ADR.

Gate impact:

- G3 Java boundary diagnostics may now reference ADR-0003 for controller transaction scans, controller repository scans, controller signature leakage checks, mapper dependency checks and service transaction-policy diagnostics;
- the first implementation must remain report-only unless a later patch explicitly promotes a specific rule to strict mode;
- persistence identity checks may now reference accepted ADR-0004 in report-only mode;
- security permission checks may now reference accepted ADR-0005 in report-only mode;
- Catalog-demo canonicalization checks may now reference accepted ADR-0007 in report-only mode.




## ADR-0004 persistence rule source since 000064

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts the persistence identity and DomainEntity ADR.

Gate impact:

- report-only G3 diagnostics may reference ADR-0004 for opaque ID shape, `DomainEntity` usage, business-key separation, `persistenceVersion`, audit-field ownership and repository-boundary findings;
- OpenAPI and DTO checks may flag numeric public IDs for new reference APIs as non-canonical unless an explicit surrogate-ID exception exists;
- strict persistence gates still require stable implementation, Catalog-demo evidence and explicit strict promotion under ADR-0006;
- security current-user propagation for audit remains deferred to ADR-0005/ADR-0010 relationship.

## ADR-0007 Catalog-demo rule source since 000065

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts the Catalog-demo canonicalization ADR.

Gate impact:

- G5 readiness diagnostics may classify Catalog-demo slices as `legacy-demo-seed`, `candidate-reference-slice`, `canonical-reference-slice` or `deprecated-seed-fragment`;
- report-only checks may verify that canonicalization evidence covers endpoint, DTO, validation, error, application-layer, persistence, mapping, security-classification, gate-evidence and deferral topics;
- strict canonicalization gates still require stable implementation and explicit strict-promotion under ADR-0006;
- target comparison stays read-only and waits for canonical Catalog-demo evidence.

## ADR-0005 security rule source since 000066

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts the security and permission boundary ADR.

Gate impact:

- report-only G4 diagnostics may reference ADR-0005 for endpoint classification, permission naming, role-mapping evidence, authorization-placement hints, current-user/capability contract shape and Catalog-demo `documented-deferred-security` evidence;
- candidate Catalog-demo readiness checks may report unclassified management endpoints, non-canonical permission names and missing deferred-security rationale;
- strict security gates remain deferred until implementation evidence, fixtures, Catalog-demo proof and explicit strict promotion under ADR-0006 exist.

## Report-only seed planning since 000067

Patch `000067_springmaster_report_only_gate_seed_plan` adds the first concrete report-only gate seed plan under `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_SEED_PLAN.md`.

API gate impact:

- G1 HTTP vocabulary and query-parameter diagnostics are the preferred first API contract checks;
- body-bearing single `DELETE`, public `findOne`/`findFirst`/`findLast` vocabulary, complete-result-set `/all`, optional `/count`, bounded `/options`, `sortBy`, generated `arg0`/`arg1` parameter names and status/error evidence are first-scope candidates;
- findings remain non-blocking in report-only mode;
- target-project API comparison remains excluded from the first seed;
- strict API gates require a later explicit promotion patch under ADR-0006.

## Report-only tooling seed after 000068

Patch `000068_springmaster_report_only_gate_tooling_seed` introduces the first executable report-only gate seed.

The seed does not yet implement full OpenAPI contract validation. It does provide a stable report shape and first deterministic diagnostics for rule-source coverage, HTTP/query vocabulary hints, status/error evidence, Java boundary hints, persistence identity hints, security classification evidence and Catalog-demo readiness evidence.

The seed keeps all findings non-blocking and does not scan target projects. This makes the gate concept executable without prematurely converting standards into strict gates.


## Tooling alignment after 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` adds repeatable regression coverage for the first report-only gate seed.

The API contract gate concept remains report-only at this stage. The Maven profile `springmaster-gates-report` may execute the diagnostics, but API findings such as legacy query vocabulary, missing Catalog-demo evidence or non-canonical endpoint hints are still findings, not strict failures.

## Report-only findings baseline after 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` adds the first report-only findings interpretation for API-related gate output.

API-relevant baseline findings are:

- historical missing pageable query evidence is now superseded by CatalogItem candidate evidence for paged list, `/all`, `/count` and typed query operations;
- ad-hoc `Map<String,Object>` error response evidence;
- positive `201 Created` evidence for create;
- missing bodyless delete status-code evidence.

These findings are consistent with the Catalog-demo `legacy-demo-seed` state. They are not strict failures. A future Catalog-demo candidate slice should use them as concrete work items for G1 API evidence.

## Catalog-demo candidate contract planning after 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` binds the report-only G1 findings to a concrete CatalogItem candidate implementation target.

Gate impact:

- G1 query diagnostics may treat the candidate endpoint contract as the expected future evidence for `page`, `size`, `sortBy` and `sortDir`;
- G1 status/error diagnostics may treat standard error bodies, create `201`, update `200`, delete `204` and not-found `404` as candidate evidence targets;
- ambiguous `/all`, ad-hoc count endpoint vocabulary, public `findOne`/`findFirst`/`findLast` vocabulary and body-bearing single `DELETE` remain non-canonical for the candidate slice; complete-result-set `/all` is valid when explicit export/batch/integration evidence exists; optional `/count` is valid when it follows the `totalElements` candidate response shape;
- G5 must not mark the slice canonical merely because the candidate contract is implemented;
- strict API gates remain deferred under ADR-0006.

## Candidate-slice review feedback after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` confirms that the first CatalogItem candidate foundation satisfies the most important G1 API contract expectations at source and behavior-test level.

The review also identifies two standards-to-gate feedback items:

- DTO-boundary diagnostics should eventually detect public request DTOs that expose persistence-facing embeddables such as `Range`;
- G5 readiness diagnostics should recognize explicit candidate evidence before reporting pure `legacy-demo-seed` state.

Both remain report-only concerns. They are not strict gates.



## Candidate evidence input since 000074

Report-only API contract diagnostics may consume machine-readable reference evidence when it is part of the Springmaster reference project itself.

For Catalog-demo, the recognized evidence source is:

```text
PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json
```

The source uses schema marker `springmaster.catalog-demo.candidate-evidence.v1` and declares whether a slice is `legacy-demo-seed`, `candidate-reference-slice` or later `canonical-reference-slice`.

This input does not enable strict gates. It only prevents stale historical text from being interpreted as the current slice state when newer candidate evidence exists.


## JPA count efficiency report-only checks since 000105

Future API and Java-boundary gates may report count-query efficiency findings based on `PROJECT_DOCS/STANDARDS/API/JPA_COUNT_QUERY_EFFICIENCY_REFERENCE.md`. Initial diagnostics should stay report-only and may flag obvious anti-patterns such as `listAll(...).size()`, `repository.findAll(...).size()`, stream counting after entity materialization, DTO mapping inside count methods, or paging/sorting applied to count operations.

These findings must distinguish documentation/runtime-contract violations from implementation-efficiency warnings until strict promotion is explicitly approved under ADR-0006.


## Query contract gate report since 000106

Patch `000106_springmaster_query_contract_gate_report` defines the first concrete report-only artifact for query/list contracts: `reports/api/query-contract-gate-report.json`. The report concept maps the documented standards for paged list, complete-result-set `/all`, optional `/count`, filter parity, sort allowlists, service-level query-operation interfaces and JPA count efficiency into stable finding IDs.

Gate impact:

- query-contract diagnostics now have a named report target and rule catalog;
- the first implementation should emit JSON findings before any Maven-failing strict gate is introduced;
- CatalogItem should be the positive reference fixture for paged list, `/all`, `/count` and `ResultSetQueryOperations`;
- the persistent CatalogItem dedicated Criteria count must be recognized as positive JPA count-efficiency evidence;
- strict enforcement remains deferred until the report schema is stable and promoted under ADR-0006.

## Query contract report implementation since 000107

The query-contract gate has an executable report-only MVP since `000107_springmaster_query_contract_report_tooling_mvp`.

The first implementation is deliberately narrow:

- it is source-based;
- it targets Springmaster CatalogItem as the positive candidate reference fixture;
- it writes one JSON report;
- it does not fail builds on findings;
- it does not scan external target projects;
- it does not replace future OpenAPI, persistent JPA or security/data-scope gates.

This satisfies the report-only implementation milestone from `QUERY_CONTRACT_GATE_REPORT.md` while keeping strict enforcement deferred.

## OpenAPI query-contract evidence since 000109

The query-contract gate evidence now includes a runtime-generated OpenAPI proof for the CatalogItem candidate reference slice.

`CatalogItemOpenApiQueryContractTest` reads `/api-docs` and verifies the public query vocabulary for the paged list, `/all` and `/count` operations. This closes the CatalogItem OpenAPI-evidence gap for the current query/list/count scope while keeping target-project comparison and strict gate promotion deferred.

Gate impact:

- OpenAPI parameter drift can now be detected in the reference project;
- generated parameter names such as `arg0`/`arg1` are explicitly rejected for `/count` evidence;
- `/count` must expose `CountResponseDTO.totalElements` in the OpenAPI schema;
- strict enforcement outside Springmaster remains a later ADR-0006 promotion step.

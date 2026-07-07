# Springmaster Standards

Springmaster standards define conventions and validation rules for backend projects built from or supplied by Springmaster.

Springmaster standards are not project-local notes. They are master-level rules that should be demonstrated in the reference project and verified by tools where possible.

## Current strategy

The standards workstream starts with API conventions extracted from the IDM API-readiness ADR themes.

The first consumer and demonstrator is the `Catalog-demo` reference project. Existing projects such as IDM and Personnel are compared later and are not the first delivery targets.

## Standard categories

Initial categories are:

- API request validation,
- required fields and OpenAPI required properties,
- API list, paging, sorting and filtering,
- command and delete HTTP semantics,
- external ID and OpenAPI boundary,
- DTO and entity contracts,
- package and dependency boundaries,
- patch and export process rules,
- reference implementation rules,
- quality gates.

## API standards since 000044

Patch `000044_springmaster_api_standards_adr_extraction` extracts the first concrete API standards under:

```text
PROJECT_DOCS/STANDARDS/API/
```

The extracted standards are documentation-first. They define what Catalog-demo must demonstrate and what future gates should verify. They do not authorize target-project changes for IDM, Personnel or other existing projects.

Patch `000045_springmaster_api_endpoint_contract_definition_backlog` adds the endpoint-contract definition backlog. It records the still-open decisions for list, all-list, detail, lookup, first/latest/current retrieval, single delete, delete-multiple, state commands, assignments, naming, status codes and OpenAPI gates.

## Enforcement principle

A Springmaster standard should have at least one enforcement path.

Possible enforcement paths are:

- Java interface or reusable support class,
- JUnit integration test,
- OpenAPI contract test,
- ArchUnit rule,
- custom Maven-bound Java test,
- shell/tooling gate,
- reference implementation in Catalog-demo.

If a rule cannot yet be enforced automatically, the standard must say so explicitly and define the intended future gate.

## API endpoint contract standard since 000046

Patch `000046_springmaster_api_endpoint_contract_standard` converts the endpoint-contract backlog into canonical Springmaster endpoint rules for new reference APIs. It defines public API vocabulary, collection/detail/create/update/delete/delete-multiple/search/command endpoint shapes, status-code expectations and future OpenAPI gate targets. Existing target projects remain comparison inputs only.

## Real App Pattern Forensics since 000047

Patch `000047_springmaster_real_app_pattern_forensics` adds `REAL_APP_PATTERN_FORENSICS.md` as the first documented comparison of current IDM and Personnel code patterns against Springmaster's emerging API, Core, service, security and gate strategy.

The document identifies which patterns should be adopted, rejected or deferred before Catalog-demo becomes canonical. It confirms that Catalog-demo should not yet freeze additional domain behavior until the high-priority error, DTO, validation, list/query, command, security and gate standards are resolved.
## API Error Contract Standard since 000048

Patch `000048_springmaster_api_error_contract_standard` adds `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`. It defines the canonical Springmaster API error body, baseline `errorType` vocabulary, status-code mapping, validation violation shape, OpenAPI expectations and Catalog-demo readiness rule for error behavior.

The standard keeps a Springmaster-specific error envelope as the public contract. Framework-native mechanisms such as `ProblemDetail` may be used internally only when the external response still follows the Springmaster contract or a later ADR explicitly changes the public contract.

## DTO Boundary and Validation Standard since 000049

Patch `000049_springmaster_dto_boundary_and_validation_standard` adds `PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md`. It defines canonical DTO roles, Java naming conventions, inbound and outbound controller boundary rules, create/update/command/query DTO expectations, validation activation, entity exposure prohibition, OpenAPI expectations and future reflection/OpenAPI/MockMvc gate targets.

The standard keeps `DTO` as the canonical Java suffix for the current Springmaster foundation because the Core and real-app comparison inputs already use DTO vocabulary. Request and response roles must still be clear through names such as `CatalogItemCreateDTO`, `CatalogItemUpdateDTO`, `CatalogItemListItemDTO`, `CatalogItemOptionDTO` and `CatalogItemDeleteMultipleCommandDTO`.

The next high-priority standards after 000049 are list/query/paging gates, command/relationship endpoint rules, security/permission boundaries and domain/persistence foundation decisions.

## Controller, Service, UseCase and Transaction Standard since 000050

Patch `000050_springmaster_controller_service_usecase_transaction_standard` adds `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md`. It defines the canonical Springmaster layering rules for controllers, query services, command services, simple resource services, use-case handlers, transaction ownership, repository boundaries, mapper boundaries and initial security-placement expectations.

The standard keeps controllers as HTTP boundary adapters and places transaction demarcation at application-service, query-service, command-service or use-case-handler boundaries. It also records future reflection/OpenAPI/MockMvc/ArchUnit gate targets for controller transaction scans, repository injection scans and package dependency checks.

The next high-priority standards after 000050 are domain entity/persistence foundation, command/relationship endpoint specialization, security/permission boundaries, mapping rules and the first reusable API contract gate concept.

## Domain Entity and Persistence Standard since 000051

Patch `000051_springmaster_domain_entity_persistence_standard` adds `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`. It defines the canonical Springmaster foundation rules for `DomainEntity`, opaque API IDs, business keys, repository boundaries, transaction/persistence interaction, auditing, optimistic locking, delete lifecycle implications, tags, metadata and NumberSequence deferral.

The standard keeps the current Core `DomainEntity` as a `@MappedSuperclass` foundation and explicitly prevents Catalog-demo from silently freezing persistence behavior around metadata, business numbers, soft delete, audit-user propagation or repository base interfaces. These topics remain deferred until a dedicated ADR or code patch resolves them. Since patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy`, the identity, `DomainEntity`, business-key, optimistic-locking, audit-field and repository-boundary parts are ADR-backed by accepted ADR-0004.

The next high-priority standards after 000051 are command/relationship endpoint specialization, security/permission boundaries, mapping rules and the first reusable API contract gate concept.

## Security and Permission Boundary Standard since 000052

Patch `000052_springmaster_security_permission_boundary_standard` adds `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md`. It defines the canonical Springmaster rules for endpoint security classification, permission naming, role-to-permission mapping, authorization placement, `@PreAuthorize` usage, current-user/capability endpoints, audit-current-user interaction and future security gates.

The standard makes management APIs secure by default. Public and technical endpoints must be explicit exceptions, while new management resources require operation-level permissions at the service/use-case boundary. Catalog-demo may defer implementation temporarily, but it must not become canonical with accidental unprotected management endpoints.

The next high-priority standards after 000052 are command/relationship endpoint specialization, mapping rules and the first reusable API contract gate concept.



## Command and Relationship Endpoint Standard since 000053

Patch `000053_springmaster_command_relationship_endpoint_standard` adds `PROJECT_DOCS/STANDARDS/API/COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md`. It specializes the API endpoint and command HTTP standards for state transitions, resource commands, collection commands, assignment and relationship endpoints, relationship reads, bulk relationship changes, nested aggregate commands, command DTOs, permission mapping and future gates.

The standard keeps Catalog-demo from normalizing body-bearing `DELETE` operations, ambiguous generic commands, unclassified bulk behavior or unprotected management commands when the demo later introduces relationships, categories, tags, assignments or state transitions.

The next high-priority standards after 000053 are mapping rules and the first reusable API contract gate concept.

## Mapping Standard since 000054

Patch `000054_springmaster_mapping_standard` adds `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md`. It defines canonical Springmaster rules for mapping between API DTOs, application command/query objects, domain entities, read models, relationship summaries, option DTOs and command-result DTOs.

The standard deliberately does not force MapStruct everywhere. MapStruct is preferred for straightforward structural mappings when it improves consistency and strictness; manual mappers remain canonical for complex read models, relationship summaries, command results and visibility-sensitive DTOs. Mappers must not access repositories, own transactions, perform security checks or contain business policy.

The next high-priority standards after 000054 are the first reusable API contract gate concept and later Core/test utilities that make the documented endpoint, DTO, error, security, persistence and mapping standards mechanically verifiable.

## API Contract Gate Concept since 000055

Patch `000055_springmaster_api_contract_gate_concept` adds `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md`. It defines how the documented API and API-adjacent standards should become mechanically verifiable through layered OpenAPI, MockMvc, reflection/classpath, security, Catalog-demo and later target-comparison gates.

The concept keeps the current workstream documentation-only. It explicitly separates immediately documented rules from future gate implementations and prevents existing target projects from being supplied or remediated before Catalog-demo proves the standards.

The next high-priority work after 000055 is to choose the first concrete gate implementation target, most likely OpenAPI contract assertions and Catalog-demo-oriented MockMvc contract tests.

## Catalog-demo Readiness Plan since 000056

Patch `000056_springmaster_catalog_demo_readiness_plan` adds `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md`. It defines the acceptance criteria for making Catalog-demo the canonical Springmaster reference implementation.

The plan connects the documented endpoint, DTO, validation, error, controller/service/transaction, persistence, security, command/relationship, mapping and gate standards to a concrete CatalogItem readiness matrix. It explicitly distinguishes mandatory first-slice behavior from deferred concerns such as complex search, delete-multiple, state transitions, relationships, metadata persistence, NumberSequence and target-project comparison.

The next high-priority work after 000056 is either a concrete CatalogItem code-slice plan or the first gate-tooling seed. Any code implementation must be verified with the required Maven/test validation.


## Standard Consistency and ADR Gap Review since 000057

Patch `000057_springmaster_standard_consistency_and_adr_gap_review` adds `PROJECT_DOCS/STANDARDS/STANDARD_CONSISTENCY_AND_ADR_GAP_REVIEW.md` as the forensic consistency review before the first API contract gate tooling seed.

The review confirms that the current standards are broadly suitable for the intended Springmaster architecture, but not yet mature enough for direct gate implementation. It identifies blocking gaps such as `sort` versus `sortBy`, `/all` versus `/options`/`/reference-data`, OpenAPI naming, error correlation semantics, ADR coverage and test strategy.

The next high-priority work after 000057 is gap closure. Gate tooling should wait until the P0 gaps are resolved or explicitly classified as `ready-for-tooling`.


## Query and Reference Data Consistency Standard since 000058

Patch `000058_springmaster_api_query_reference_data_consistency_standard` adds `PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md`. It closes the first P0 consistency gap from the 000057 review by making `sortBy` the canonical sorting parameter for new reference APIs, treating `sort` as legacy/target-comparison vocabulary, using `/options` for bounded selector data, allowing `/reference-data` only with ADR-backed semantics and marking `/all` as non-canonical for Catalog-demo and new Springmaster-generated APIs.

The next high-priority gap work can now focus on OpenAPI naming, error operational semantics, ADR consolidation, test strategy, configuration/profile standards, database migration standards and observability.


## Error identity and status-code consistency since 000059

`API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md` resolves the error operational identity and first-slice status-code gap before API contract gate tooling starts. It keeps the existing error contract but clarifies `errorId`, optional correlation/trace/message-key fields and deterministic Catalog-demo defaults for update, delete, delete-multiple and command responses.


## ADR Governance and Backlog Alignment since 000060

Patch `000060_springmaster_adr_governance_and_backlog_alignment` adds ADR governance, ADR template requirements and a blocker-aware ADR backlog alignment under `PROJECT_DOCS/ADR/`.

The patch does not accept the planned ADRs yet. It defines how documented standards are promoted into ADR-backed decisions and when strict gates may encode those decisions. The first P0 ADRs to draft are API boundary/endpoint contract, verification/gate strategy, application-layer/transaction boundary, persistence identity/DomainEntity strategy and Catalog-demo canonicalization.

After 000060, the standards are considered ready for ADR drafting, not yet for strict gate implementation.



## ADR-0002 API Boundary Acceptance since 000061

Patch `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepts the API boundary and endpoint contract ADR under `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md`.

This turns the API-boundary standards for endpoints, DTOs, validation, query/reference-data vocabulary, error bodies, status codes, commands and relationship endpoint semantics into an ADR-backed decision for new Springmaster reference APIs. Strict gate execution still requires ADR-0006 and concrete gate implementation evidence.



## ADR-0006 gate strategy update

`000062_springmaster_adr_0006_verification_and_gate_strategy` accepts the verification and gate strategy for Springmaster standards. Standards may now be prepared for report-only gate tooling when their rule source is documented and the finding mode follows ADR-0006. Strict gates still require explicit strict-readiness and any domain-specific ADRs required by the rule.

## ADR-0003 application-layer acceptance since 000063

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts the application-layer and transaction-boundary ADR under `PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md`.

The controller/service/use-case standard is now ADR-backed for new Springmaster reference APIs. Report-only Java boundary diagnostics may reference ADR-0003 for thin-controller, repository-isolation, transaction-placement and mapper-boundary findings. Strict enforcement still requires stable gate implementation, Catalog-demo evidence and explicit strict promotion under ADR-0006.




## ADR-0004 Persistence Identity Acceptance since 000064

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts `PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md`.

This turns the persistence identity and `DomainEntity` standard into an ADR-backed decision for new Springmaster reference APIs and Catalog-demo persistence work. Report-only persistence diagnostics may use ADR-0004 as a rule source. Strict persistence gates remain blocked until implementation evidence, Catalog-demo proof and explicit strict promotion under ADR-0006 exist.

## ADR-0007 Catalog-demo canonicalization since 000065

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts ADR-0007. The standards now treat Catalog-demo in explicit lifecycle states rather than assuming the existing code is canonical.

The current CatalogItem implementation remains `legacy-demo-seed`. A standards-aligned patch may introduce a `candidate-reference-slice`, and only a later evidence-backed patch may declare a `canonical-reference-slice`.

This makes the standard index safe for first report-only G5 readiness diagnostics while keeping strict gates dependent on implementation evidence and ADR-0006 promotion.

## ADR-0005 Security and Permission Boundary Acceptance since 000066

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts `PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md`.

The security and permission boundary standard is now ADR-backed for endpoint classification, permission naming, role-to-permission mapping, authorization placement, current-user/capability endpoints, audit-current-user interaction and Catalog-demo `documented-deferred-security` evidence.

Report-only G4 security diagnostics may use ADR-0005 as a rule source. Strict security gates still require implemented security behavior, tests, Catalog-demo evidence and explicit strict promotion under ADR-0006.

## Report-only Gate Seed Plan since 000067

Patch `000067_springmaster_report_only_gate_seed_plan` adds `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_SEED_PLAN.md`.

The plan maps accepted standards and ADRs into the first non-blocking diagnostic seed. It keeps strict gates, target comparison and generated remediation deferred, while defining concrete gate IDs, finding schema, report files and Catalog-demo evidence behavior.

## Report-only gate tooling seed since 000068

Patch `000068_springmaster_report_only_gate_tooling_seed` adds the first executable standards diagnostics.

The new gate runner is report-only, Springmaster-local and ADR-backed. It writes compact reports under `target/springmaster-gates/<gate-run-id>/` and records findings without failing execution. It does not bind strict gates into the Maven lifecycle and does not scan or modify target projects.


## Report-only Gate Regression after 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` connects the accepted ADR and standards baseline to repeatable report-only validation.

The new regression coverage validates report shape and safety behavior only. It does not promote any standard to a strict gate and does not scan target projects.

## Report-only findings baseline after 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` adds `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_FINDINGS_BASELINE_REVIEW.md`.

The review classifies the first executable gate output. It confirms that the current `12` findings are expected for the non-canonical Catalog-demo seed and that no standard has been promoted to strict enforcement.

## Catalog-demo Candidate Contract Plan after 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` adds `PROJECT_DOCS/DEMO/CATALOG_DEMO_CANDIDATE_SLICE_CONTRACT_PLAN.md`.

The plan translates accepted standards and ADRs into a narrow CatalogItem candidate-slice contract. It does not promote strict gates and does not change Demo implementation. It defines the next code-slice target for canonical API vocabulary, DTO roles, validation, error responses, status codes, application boundaries, persistence identity and security evidence.

## Catalog-demo candidate review after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` compares the first CatalogItem candidate implementation against the accepted Springmaster ADRs and standards.

Outcome:

- the candidate slice is accepted as a foundation;
- canonical status is not granted;
- DTO-boundary cleanup, service update validation symmetry, G5 gate evidence alignment, implemented security, durable persistence and OpenAPI evidence remain open.



## Report-only candidate evidence alignment since 000074

The standards gate concept now allows source-based report-only diagnostics to read machine-readable candidate evidence from the Springmaster reference project. For Catalog-demo this is `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json` with schema `springmaster.catalog-demo.candidate-evidence.v1`.

This keeps the current state deterministic: `CatalogItem` is a `candidate-reference-slice`; Catalog-demo is `not-canonical`; target comparison and target delivery remain blocked.




## Command Precheck Capability Standard since 000082

Patch `000082_springmaster_command_precheck_capability_standard` adds the API standard `PROJECT_DOCS/STANDARDS/API/COMMAND_PRECHECK_ENDPOINT_STANDARD.md` and accepts `PROJECT_DOCS/ADR/ADR-0011-command-precheck-and-capability-boundary.md`.

The standard defines optional backend command prechecks as side-effect-free capability queries for concrete commands. It keeps command policy in the backend, requires precheck and execution to share the same policy/guard and avoids mandatory per-row prechecks for list or bulk UIs.

This patch is logical Springmaster standardization only. It does not supply IDM, Personnel or other target projects.

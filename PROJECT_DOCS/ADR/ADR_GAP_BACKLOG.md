# Springmaster ADR Gap Backlog

## Purpose

This backlog records ADRs that are required to turn documentation-first Springmaster standards into durable architecture decisions and later enforceable gates.

Patch `000060_springmaster_adr_governance_and_backlog_alignment` aligns the backlog with the ADR governance model. It does not accept the ADRs. It defines the order, status and tooling impact of the ADR work that must follow.

## Current ADR coverage

Accepted ADRs currently present:

| ADR | Status | Scope |
|---|---|---|
| `ADR-0001-springmaster-bootstrap.md` | Accepted | Springmaster project bootstrap |
| `ADR-0002-api-boundary-and-endpoint-contract.md` | Accepted | API boundary and endpoint contract for new reference APIs |
| `ADR-0003-application-layer-and-transaction-boundary.md` | Accepted | application layer and transaction boundary |
| `ADR-0004-persistence-identity-and-domainentity-strategy.md` | Accepted | persistence identity and DomainEntity strategy |
| `ADR-0005-security-and-permission-boundary.md` | Accepted | security and permission boundary |
| `ADR-0006-verification-and-gate-strategy.md` | Accepted | verification and gate strategy |
| `ADR-0007-catalog-demo-canonicalization-strategy.md` | Accepted | Catalog-demo canonicalization strategy |

API boundary standards from `000044` through `000059` are now consolidated by accepted `ADR-0002`. Application-layer and transaction-boundary standards from `000050` are now consolidated by accepted `ADR-0003`. Persistence identity and DomainEntity standards from `000051` are now consolidated by accepted `ADR-0004`. Security and permission boundary standards from `000052` are now consolidated by accepted `ADR-0005`. Gate execution semantics are now consolidated by accepted `ADR-0006`. Catalog-demo readiness and canonicalization semantics are now consolidated by accepted `ADR-0007`. Other standards remain documentation-first until their corresponding ADRs are accepted or classified as `ready-for-tooling-without-adr`.

## Planning status model

| Planning status | Meaning |
|---|---|
| `needed` | ADR is required but not yet ready to draft |
| `ready-to-draft` | inputs are sufficiently consolidated for a proposed ADR patch |
| `drafting` | ADR is being prepared |
| `accepted` | ADR exists and has status `Accepted` |
| `deferred` | intentionally postponed |
| `not-needed` | backlog item was closed without ADR because it is not architectural |

## Tooling blocker classes

| Blocker | Meaning |
|---|---|
| `blocks-strict-gates` | strict fail-build gates must wait for accepted ADR |
| `allows-report-only-gates` | report-only diagnostics may be built before ADR acceptance |
| `not-a-tooling-blocker` | ADR is governance-relevant but does not block first tooling seed |

## Prioritized ADR backlog

### ADR-0002: API Boundary and Endpoint Contract

Priority: `P0`

Planning status: `accepted`

Tooling blocker: `no-longer-blocking-for-ADR-0002-rules`; strict enforcement still depends on ADR-0006 and implementation readiness.

Accepted ADR:

- `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md`

Accepted input standards:

- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_HTTP_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md`

Accepted decision scope:

- public endpoint vocabulary;
- collection/detail/create/update/delete contracts;
- command and relationship endpoint semantics;
- `sortBy`, `/options`, explicit complete-result-set `/all`, optional `/count`/`/search/count`, non-canonical ambiguous `/all`, non-canonical ad-hoc count endpoints, and ADR-backed `/reference-data`;
- DTO boundary rules;
- validation boundary;
- public API error contract;
- first-slice status-code defaults;
- external opaque ID boundary.

Remaining deferrals after ADR acceptance:

- operationId/tag/schema/security-scheme naming remains a separate OpenAPI naming standard gap;
- count-only response contract now has Core DTO and CatalogItem behavior evidence; strict gate enforcement remains deferred to ADR-0006/gate implementation readiness;
- security schemes and permission catalog are owned by ADR-0005;
- gate severity, Maven binding and report structure are owned by ADR-0006.

### ADR-0006: Verification and Gate Strategy

Priority: `P0`

Planning status: `accepted`

Tooling blocker: `no-longer-blocking-for-report-only-gate-seed`; strict enforcement still depends on gate implementation readiness and rule-specific ADR coverage.

Accepted ADR:

- `PROJECT_DOCS/ADR/ADR-0006-verification-and-gate-strategy.md`

Accepted input standards:

- `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md`
- `PROJECT_DOCS/STANDARDS/STANDARD_CONSISTENCY_AND_ADR_GAP_REVIEW.md`
- `PROJECT_DOCS/ADR/ADR_GOVERNANCE_AND_BACKLOG_ALIGNMENT.md`

Accepted decision scope:

- G0 through G6 gate layers;
- `report-only`, `strict` and `manual-review` execution modes;
- `BLOCKER`, `ERROR`, `WARNING`, `INFO` and `MANUAL_REVIEW` severities;
- future Maven profile names `springmaster-gates-report`, `springmaster-gates-strict` and `springmaster-gates-target-compare`;
- compact report directory `target/springmaster-gates/<gate-run-id>/`;
- first report-only gate scope;
- strict gate promotion rule;
- target-project comparison as read-only.

Remaining deferrals after ADR acceptance:

- exact Java package and class names for gate utilities;
- exact OpenAPI parser library;
- exact MockMvc fixture API;
- exact ArchUnit timing;
- CI integration;
- target-project remediation or delivery workflows.

### ADR-0003: Application Layer and Transaction Boundary

Priority: `P0`

Planning status: `accepted`

Tooling blocker: `no-longer-blocking-for-report-only-java-boundary-diagnostics`; strict enforcement still depends on gate implementation readiness, Catalog-demo evidence and explicit strict promotion under ADR-0006.

Accepted ADR:

- `PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md`

Accepted input standards:

- `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md` for mapper-boundary placement
- `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md` for authorization-placement relationship only

Accepted decision scope:

- controller responsibility as HTTP boundary adapter;
- simple resource service versus query service versus command service versus use-case handler;
- transaction ownership at application-service/use-case boundary;
- repository and `EntityManager` isolation from controllers;
- mapper boundary and forbidden dependencies;
- security-placement relationship until ADR-0005;
- Java boundary report-only diagnostic candidates.

Remaining deferrals after ADR acceptance:

- exact marker interfaces for query/command/application services;
- exact reflection-scan versus ArchUnit implementation split;
- exact package-level dependency model;
- strict gate promotion;
- permission naming and role mapping, owned by ADR-0005;
- persistence identity and repository base strategy, owned by ADR-0004;
- Catalog-demo canonicalization evidence, owned by ADR-0007.

### ADR-0004: Persistence Identity and DomainEntity Strategy

Priority: `P0`

Planning status: `accepted`

Tooling blocker: `no-longer-blocking-for-report-only-persistence-diagnostics`; strict enforcement still depends on gate implementation readiness, Catalog-demo evidence and explicit strict promotion under ADR-0006.

Accepted ADR:

- `PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md`

Accepted input standards:

- `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/EXTERNAL_ID_OPENAPI_BOUNDARY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/MAPPING_STANDARD.md` for entity-to-DTO boundary relationship
- `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md` for repository and transaction placement relationship

Accepted decision scope:

- default public ID and persistence identity;
- external opaque ID rule;
- `DomainEntity` as mapped-superclass default for standard aggregate roots;
- criteria for internal surrogate IDs;
- business keys as explicit domain fields;
- service-owned ID generation preference;
- `persistenceVersion` optimistic locking;
- technical audit fields;
- repository boundary;
- hard-delete versus lifecycle-command distinction;
- metadata, NumberSequence, outbox, multi-tenancy and Core repository-base deferrals.

Remaining deferrals after ADR acceptance:

- exact Java marker interfaces and scanner implementation for persistence diagnostics;
- Core repository base interface, if later needed;
- metadata persistence ADR;
- NumberSequence persistence ADR;
- audit-current-user provider details, owned by ADR-0005/ADR-0010 relationship;
- database migration and DBTool details, owned by ADR-0009;
- strict persistence gate promotion;
- Catalog-demo canonicalization evidence, owned by ADR-0007.

### ADR-0007: Catalog-demo Canonicalization Strategy

Priority: `P0`

Planning status: `accepted`

Tooling blocker: `no-longer-blocking-for-report-only-catalog-demo-readiness-diagnostics`; strict canonicalization still depends on implementation evidence and explicit strict promotion under ADR-0006.

Accepted ADR:

- `PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md`

Accepted input document:

- `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md`

Accepted decision scope:

- when Catalog-demo becomes canonical;
- lifecycle states `legacy-demo-seed`, `candidate-reference-slice`, `canonical-reference-slice` and `deprecated-seed-fragment`;
- required evidence for the first CatalogItem slice;
- allowed explicit deferrals;
- security classification as a minimum even when enforcement is deferred;
- G5 readiness diagnostics;
- target-project comparison as read-only and later than Catalog-demo proof.

Remaining deferrals after ADR acceptance:

- exact readiness summary file name and schema;
- exact Java marker or annotation for seed/candidate/canonical states;
- exact implementation of G5 diagnostics;
- strict canonicalization gate promotion;
- security enforcement details, owned by ADR-0005;
- target-project remediation or delivery strategy.

### ADR-0005: Security and Permission Boundary

Priority: `P1`

Planning status: `accepted`

Tooling blocker: `no-longer-blocking-for-report-only-security-diagnostics`; strict security gates still depend on implementation evidence, Catalog-demo proof, security fixtures and explicit strict promotion under ADR-0006.

Accepted ADR:

- `PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md`

Accepted input standard:

- `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md`

Accepted decision scope:

- secure-by-default endpoint classification;
- management endpoint permission requirement;
- canonical permission naming with `<domain>:<resource>:<operation>`;
- Catalog-demo first permission vocabulary;
- role-to-permission mapping;
- authorization placement at application operation boundary;
- `@PreAuthorize` and permission-catalog direction;
- current-user and capability endpoint boundaries;
- audit-current-user interaction;
- `documented-deferred-security` and `implemented-management-security` modes for Catalog-demo;
- report-only G4 security diagnostic candidates.

Remaining deferrals after ADR acceptance:

- concrete Spring Security configuration;
- JWT/session/claim mapping;
- CSRF policy;
- Java permission catalog type and constants;
- method-security annotations or permission evaluator;
- role persistence schema;
- tenant/data-scope enforcement and concealment policy;
- current-user provider implementation;
- security test fixtures;
- strict security gate promotion.

### ADR-0008: Configuration and Runtime Profile Strategy

Priority: `P1`

Planning status: `needed`

Tooling blocker: `not-a-tooling-blocker` for first API report-only gates

Input documents:

- `.env.example`
- `PROJECT_DOCS/CONFIG/SPRINGMASTER_ENV_TEMPLATE.env`
- `PROJECT_DOCS/TOOLING/PROJECT_NEW.md`

Decision scope:

- Spring profiles;
- `.env` handling;
- secrets;
- local versus CI behavior;
- OpenAPI generation exposure;
- actuator exposure;
- feature flags.

### ADR-0009: Database Migration and DBTool Strategy

Priority: `P1`

Planning status: `needed`

Tooling blocker: `blocks-strict-gates` for DB migration gates, `not-a-tooling-blocker` for first API report-only gates

Input documents:

- `PROJECT_DOCS/TOOLING/DBTOOL.md`
- `PROJECT_DOCS/TOOLING/PLATFORM_UPDATE.md`
- `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`

Decision scope:

- Liquibase changelog naming;
- rollback policy;
- test database expectations;
- stage diff usage;
- generated versus hand-authored changelogs;
- Catalog-demo persistence proof.

### ADR-0010: Observability and Error Trace Strategy

Priority: `P1`

Planning status: `needed`

Tooling blocker: `not-a-tooling-blocker` for basic error-body checks, `blocks-strict-gates` for observability/logging gates

Input standards:

- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md`

Decision scope:

- correlation and trace propagation;
- log fields;
- audit logging;
- security-sensitive logging;
- client-visible diagnostic fields.

## Near-term execution plan

The next gap patches should create accepted ADRs in this order unless a later patch documents a reason to reorder:

1. `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` - accepted by patch 000065
2. `000066_springmaster_adr_0005_security_and_permission_boundary` - accepted by patch 000066
3. first report-only API/Catalog-demo readiness/security-classification gate tooling seed, if scoped to accepted ADR rules

After these ADRs, a report-only API/Catalog-demo/security diagnostic seed is safer. Strict gates still require implementation evidence and explicit promotion under ADR-0006. Strict gates may still require additional implementation evidence.

## ADR execution rule

A later code or tooling patch may reference a documented standard directly only when the affected rule is classified as `ready-for-tooling` or `ready-for-tooling-without-adr`.

Rules classified as `needs-adr` must not be encoded as strict tooling gates until the corresponding ADR is accepted.

## Updates

### 000058 update

`000058_springmaster_api_query_reference_data_consistency_standard` resolved the first API-boundary ADR gap at standard level. Patch `000091_springmaster_list_query_export_all_contract` amends that decision for export, batch and integration access: a documented complete-result-set `/all` endpoint is canonical, while ambiguous, selector-like, undocumented or silently capped `/all` endpoints remain non-canonical. A dedicated ADR may still be useful later if Springmaster introduces multi-sort, asynchronous export jobs or broad reference-data caching, but Catalog-demo and gate-tooling can now treat `sortBy`, `/options`, ADR-backed `/reference-data`, canonical complete-result-set `/all`, optional count-only and non-canonical ambiguous `/all` as distinct accepted standard decisions. Patch `000103_springmaster_query_operations_contract_closure_review` records that paged list, `/all`, `/count`, Core query interfaces and CatalogItem service adoption are reference-demonstrated at candidate level.

### 000059 update

`000059_springmaster_api_error_identity_and_statuscode_consistency_standard` resolves the API error identity and first-slice status-code gaps at standard level.

ADR impact:

- ADR-0002 can reference the accepted status defaults for create, update, single delete, delete-multiple, state commands and asynchronous commands.
- ADR-0010 remains needed for broader observability implementation, logging infrastructure, MDC, tracing libraries and audit policy, but it no longer blocks first API contract gate tooling for basic error-body checks.

### 000060 update

`000060_springmaster_adr_governance_and_backlog_alignment` aligns this backlog with the ADR governance model and marks ADR-0002, ADR-0006, ADR-0003, ADR-0004 and ADR-0007 as P0 `ready-to-draft` blockers before strict gate tooling or Catalog-demo canonicalization.



### 000061 update

`000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepts ADR-0002 and closes the P0 API-boundary ADR blocker.

ADR impact:

- endpoint, DTO, validation, query/reference-data, error, command and first-slice status-code rules are now ADR-backed for new Springmaster reference APIs;
- report-only API contract tooling may use ADR-0002 as decision reference;
- strict enforcement still waits for ADR-0006 and concrete gate implementation evidence;
- operationId/tag/schema naming remains a separate standard gap;
- security schemes remain owned by ADR-0005.



### 000062 update

`000062_springmaster_adr_0006_verification_and_gate_strategy` accepts ADR-0006 and closes the P0 gate-strategy ADR blocker for report-only API contract gate tooling.

ADR impact:

- gate layers, execution modes, severity vocabulary and report structure are ADR-backed;
- future Maven profile names are now defined;
- first API contract gate tooling must be report-only unless a later patch promotes a gate to strict;
- target-project comparison remains read-only and non-destructive;
- ADR-0003, ADR-0004 and ADR-0007 are now accepted; ADR-0005 remains before strict security enforcement.

## 000063 update

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts ADR-0003.

Resolved backlog impact:

- controller/service/use-case/transaction decisions are now ADR-backed;
- report-only Java boundary diagnostics may reference ADR-0003;
- strict Java boundary gates still require implementation evidence, Catalog-demo proof and explicit strict promotion;
- ADR-0004 and ADR-0007 are accepted; Catalog-demo canonicalization gates still need implementation evidence and strict-promotion before they can block builds.




## 000064 update

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts ADR-0004.

Resolved backlog impact:

- persistence identity and public API identity defaults are now ADR-backed;
- `DomainEntity` remains the mapped-superclass default for standard aggregate roots;
- business keys, internal surrogate-ID criteria, `persistenceVersion`, audit fields and repository boundary are now accepted architecture decisions;
- report-only persistence identity diagnostics may reference ADR-0004;
- strict persistence gates still require implementation evidence, Catalog-demo proof and explicit strict promotion under ADR-0006;
- ADR-0007 is accepted by 000065; declaring Catalog-demo canonical still requires evidence and explicit state transition.

## 000065 update

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts ADR-0007.

Resolved backlog impact:

- Catalog-demo canonicalization states and evidence criteria are now ADR-backed;
- the existing CatalogItem implementation remains `legacy-demo-seed` until a later patch provides candidate or canonical evidence;
- report-only G5 readiness diagnostics may reference ADR-0007;
- strict canonicalization gates still require implementation evidence, Catalog-demo proof and explicit promotion under ADR-0006;
- ADR-0005 is accepted by 000066 before strict security and permission gates.

## 000066 update

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts ADR-0005.

Resolved backlog impact:

- endpoint security classification is now ADR-backed;
- permission naming and the first Catalog-demo permission vocabulary are ADR-backed;
- role-to-permission mapping and authorization-placement rules are ADR-backed;
- `documented-deferred-security` and `implemented-management-security` are accepted Catalog-demo security modes;
- report-only G4 security diagnostics may reference ADR-0005;
- strict security gates still require implementation evidence, security fixtures, Catalog-demo proof and explicit promotion under ADR-0006.

## Report-only seed plan since 000067

Patch `000067_springmaster_report_only_gate_seed_plan` adds the first gate-seed planning artifact after accepted P0 ADRs.

Backlog impact:

- P0 ADR blockers for the first report-only seed are closed by accepted ADRs `ADR-0002`, `ADR-0003`, `ADR-0004`, `ADR-0005`, `ADR-0006` and `ADR-0007`;
- `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_SEED_PLAN.md` becomes the direct input for the next code/tooling patch;
- strict gates, target comparison, configuration/profile gates, DB migration gates and observability gates remain deferred;
- the next implementation patch should be limited to report-only Springmaster-reference diagnostics unless a new ADR changes scope.




### ADR-0011: Command Precheck and Capability Boundary

Priority: `P0`

Planning status: `accepted`

Tooling blocker: `no-longer-blocking-for-report-only-precheck-diagnostics`; strict gates still depend on implementation evidence, Catalog-demo proof or another reference slice and explicit strict promotion under ADR-0006.

Accepted ADR:

- `PROJECT_DOCS/ADR/ADR-0011-command-precheck-and-capability-boundary.md`

Accepted input standard:

- `PROJECT_DOCS/STANDARDS/API/COMMAND_PRECHECK_ENDPOINT_STANDARD.md`

Accepted decision scope:

- command prechecks are optional side-effect-free capability queries;
- prechecks do not replace command execution validation;
- precheck and execution must share the same backend policy or guard;
- canonical resource precheck path is `GET /api/<domain>/<resources>/{id}/commands/<command>/precheck` when no request body is needed;
- `POST .../precheck` is allowed for commands requiring a structured precheck request;
- management command prechecks are management endpoints;
- `200 executable=false` represents concrete target policy/state/dependency blocks for an actor with general permission;
- missing operation permission remains `403`;
- list and bulk controls are not forced into per-item prechecks.

Remaining deferrals after ADR acceptance:

- exact Java package and class names for reusable DTOs and policy decision types;
- exact OpenAPI operationId/tag/schema naming;
- exact MockMvc helper API;
- exact static rule for verifying policy reuse between precheck and execution;
- Catalog-demo reference command that proves the precheck pattern;
- target-project supply to IDM or other applications.


## JPA count query efficiency reference since 000105

Patch `000105_springmaster_jpa_count_query_efficiency_reference` documents the efficient persistent implementation pattern for count-only endpoints and `PagedResponseDTO.totalElements`.

ADR impact:

- ADR-0002 owns the public API contract and count endpoint vocabulary.
- ADR-0003 owns controller/service/query boundary placement and forbids controller-side persistence shortcuts.
- ADR-0004 owns repository/persistence boundaries and durable count-query efficiency.
- ADR-0006 owns future report-only and strict gate promotion for count-query anti-pattern detection.

This closes the documentation gap for JPA count-query efficiency. Runtime proof for a durable CatalogItem repository remains a separate implementation milestone.


## Query Contract Gate Report follow-up since 000106

Patch `000106_springmaster_query_contract_gate_report` narrows the ADR-0006 follow-up for query gates by defining a report-only JSON artifact and stable finding IDs. The ADR gap is no longer the rule catalog itself; the remaining gap is executable implementation, CatalogItem report fixture evidence, generated-application comparison and later strict-gate promotion.

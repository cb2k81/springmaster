# Springmaster Standard Consistency and ADR Gap Review

## Purpose

Patch `000057_springmaster_standard_consistency_and_adr_gap_review` freezes a forensic consistency review before the first API contract gate tooling is implemented.

The review answers four questions:

1. Are the current Springmaster standards internally consistent enough for tooling?
2. Are the standards suitable for the intended architecture, or are they too broad or too narrow?
3. Which essential backend specifications are still missing before Catalog-demo becomes canonical?
4. Which ADRs, Java interfaces and tests should be introduced to make the standards verifiable?

This document is documentation-only. It does not change IDM, Personnel, Contacts, Orders or any other target project. It does not implement Java code, Maven checks, OpenAPI gates, ArchUnit rules, Catalog-demo code or target-project delivery.

## Baseline and reviewed standards

Reviewed baseline:

```text
springmaster_export_full_2026-06-30T06-25-33-202892Z.zip
```

Reviewed state patch:

```text
000056_springmaster_catalog_demo_readiness_plan
```

Reviewed standardization chain:

| Patch | Area |
|---|---|
| `000044` | generic API standards extracted from IDM ADR material |
| `000045` | endpoint-contract definition backlog |
| `000046` | endpoint contract standard |
| `000047` | IDM/Personnel real-app pattern forensics |
| `000048` | API error contract standard |
| `000049` | DTO boundary and validation standard |
| `000050` | controller/service/use-case/transaction standard |
| `000051` | domain entity and persistence standard |
| `000052` | security and permission boundary standard |
| `000053` | command and relationship endpoint standard |
| `000054` | mapping standard |
| `000055` | API contract gate concept |
| `000056` | Catalog-demo readiness plan |

## Executive verdict

Springmaster has a strong documentation-level foundation, but the standards are not yet mature enough for direct gate tooling implementation.

The standards are broadly suitable for the intended architecture because they preserve the important separation between public API contracts, DTOs, application services, persistence, security, mapping and later target-project comparison. The strict rules around DTO boundaries, bodyless single deletes, service-layer transactions and repository isolation are appropriate for Springmaster as a reference platform.

The remaining risk is not lack of direction. The risk is that a tooling seed would encode unsettled details too early. Before Java gate code or Maven-bound checks are added, Springmaster needs a small sequence of gap-resolution patches.

## Maturity classification

| Area | Current maturity | Verdict |
|---|---|---|
| API endpoint shapes | high documentation maturity | query naming resolved by 000058 and complete-result-set `/all` amended by 000091; remaining OpenAPI naming and error/test strategy gaps stay open |
| DTO and validation boundary | high documentation maturity | accepted; ready for later reflection/OpenAPI/MockMvc gates |
| API error contract | good documentation maturity | needs trace/correlation/message-key operational details |
| Application-layer boundary | good documentation maturity | accepted; ready for later Java boundary scans |
| Persistence foundation | medium documentation maturity | accepted as first foundation, but identity strategy needs ADR |
| Security and permissions | medium-to-good documentation maturity | accepted direction, but permission catalog and deferred security minimums need definition |
| Command and relationship endpoints | good documentation maturity | accepted, but result DTO and idempotency details need narrowing before gates |
| Mapping | good documentation maturity | accepted direction, but gateable dependency rules need a concrete implementation approach |
| Gate concept | medium documentation maturity | right layering, but not ready for code until blocking gaps are resolved |
| ADR coverage | low | insufficient for long-term governance |
| Java interfaces/test utilities | low | useful candidates identified, but not yet specified |

## Accepted strict rules

The following rules are strict by design and should remain strict for new Springmaster reference APIs:

| Rule | Review decision | Rationale |
|---|---|---|
| No JPA entities or domain aggregates at controller boundaries | accepted | prevents public contract leakage and makes OpenAPI stable |
| No public `Pageable` controller parameters for new reference APIs | accepted | avoids generated `arg0`/`arg1` style OpenAPI artifacts and Spring Data leakage |
| No public `Page<DTO>` or `Slice<DTO>` response bodies | accepted | keeps external response shape stable and UI-friendly |
| No body-bearing single `DELETE` | accepted | aligns API contracts, OpenAPI and common HTTP client behavior |
| Controllers must not contain business logic | accepted | preserves application-layer separation |
| Controllers must not inject repositories or `EntityManager` | accepted | protects persistence boundaries |
| Controllers must not own transactions | accepted | transaction ownership belongs to services/use cases |
| Mappers must not access repositories, services or external clients | accepted | keeps mapping deterministic and testable |
| Management APIs are protected by default | accepted | prevents Catalog-demo from normalizing accidental public management endpoints |

These rules are suitable for Springmaster because the project is a standards and reference platform, not a lowest-common-denominator example application.

## Blocking consistency gaps before gate tooling

### GAP-API-QUERY-001: `sort` versus `sortBy` - resolved by 000058

Status: `blocking-gate-tooling`

Finding:

Some standards use `sort` as the canonical list sort parameter. Other documents, especially gate and readiness material, use `sortBy`. A gate cannot safely validate both as canonical without weakening the reference contract.

Resolution:

* Use `sortBy` as the canonical Springmaster parameter for new reference APIs.
* Keep `sort` only as a target-comparison or legacy compatibility alias, not as a Catalog-demo standard.
* Align `LIST_FILTER_QUERY_STANDARD.md`, `API_ENDPOINT_CONTRACT_STANDARD.md`, `API_CONTRACT_GATE_CONCEPT.md` and `CATALOG_DEMO_READINESS_PLAN.md` in a dedicated gap patch.

Reasoning:

`sortBy` is explicit, readable for generated OpenAPI and consistent with the existing IDM/Personnel API-readiness vocabulary observed during the real-app comparison. It also distinguishes the selected field from a complete sort expression.

### GAP-API-LIST-002: `/all` versus `/options` and `/reference-data` - resolved by 000058, amended by 000091

Status: `blocking-gate-tooling`

Finding:

The older list/filter/query material mentioned `/all` as a possible all-data endpoint without a precise contract. Patch `000058` rejected that ambiguous use and separated paged management collections, bounded selector data and ADR-backed reference data. Patch `000091` later accepts `/all` again, but only as an explicit complete-result-set contract for frontend export, backend batch and integration consumers.

Current resolution:

* Use `GET /api/<domain>/<resources>` for paged management collections.
* Use `GET /api/<domain>/<resources>/all` only for a complete matching result set with the same documented filters, sorting, security and data-scope predicates as the paged collection and without public `page`/`size` truncation.
* Use `GET /api/<domain>/<resources>/options` for small selector data.
* Allow `/reference-data` only when an ADR defines why the result set is bounded, stable and cacheable.
* Require any `/all` endpoint in future target-project comparison to be classified as `complete-result-set-contract`, `ambiguous-legacy-all`, `selector-like-all`, `silently-capped-all` or another documented compatibility category.

### GAP-API-ERROR-003: Error identifiers and correlation semantics

Status: `resolved-by-000059`

Finding:

The API error contract defines `errorId`, `localMessage` and violations. It does not yet fully define whether `errorId`, correlation ID, trace ID, request ID and message keys are the same or different operational concepts.

Recommended resolution:

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` defines the error-operation addendum:

* `errorId`: required unique error occurrence identifier returned to clients and logs;
* `correlationId`: optional request/distributed correlation value;
* `traceId`: optional technical tracing value when safe to expose;
* `messageKey`: optional stable UI/localization key;
* `message`: required safe fallback message;
* `localMessage`: optional localized/user-facing message;
* unexpected errors must be logged with `errorId` and available correlation context.

### GAP-API-ENDPOINT-004: Update, delete and command result status narrowing

Status: `resolved-by-000059`

Finding:

The endpoint and command standards intentionally allow some status-code variations, for example `200` versus `204` for update/delete or command completion. This is acceptable as documentation but too loose for first Catalog-demo gates.

Recommended resolution:

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` defines first-slice defaults:

* create returns `201` with response body and `Location` when practical;
* full update returns `200` with response body for the Catalog-demo first canonical slice;
* bodyless single delete returns `204` on success and `404` if missing;
* command endpoints return `200` with a command-result DTO when the result has meaningful state;
* simple commands with no meaningful body may return `204`;
* command-created resources return `201`;
* asynchronous commands return `202` only with a status/job/operation DTO;
* delete-multiple returns `200` with result DTO when eventually introduced.

### GAP-DEMO-005: CatalogItem seed non-canonical status

Status: `blocking-demo-canonicalization`

Finding:

The existing embedded CatalogItem seed predates the current standards and differs from the new endpoint, DTO, validation, error, persistence, security and gate expectations.

Recommended resolution:

Before the next CatalogItem code patch, explicitly mark the existing seed as `legacy-demo-seed` and require the first canonical slice to satisfy the Catalog-demo readiness plan. The canonical slice must not inherit non-standard API choices from the seed without deliberate migration.

### GAP-SECURITY-006: Minimum deferred-security evidence

Status: `needs-standard-clarification`

Finding:

The security standard allows `documented-deferred-security` for early Catalog-demo work. That is reasonable, but it must have minimum evidence so it does not become a loophole.

Recommended resolution:

A deferred security classification must include:

* endpoint classification;
* intended permission names;
* intended role mapping or explicit role-deferred marker;
* list of public exceptions;
* future gate expectation;
* reason why implementation is deferred.

### GAP-PERSISTENCE-007: Internal surrogate ID decision criteria

Status: `needs-ADR`

Finding:

The current foundation keeps `id` as the opaque public ID and persistence identity. This is suitable for the first Springmaster foundation, but larger systems may legitimately use separate internal surrogate IDs plus public external IDs.

Recommended resolution:

Create an ADR that keeps the current default but defines criteria for allowing a separate internal ID strategy. The gate tooling must not hard-code a permanent ban on internal surrogate IDs until that ADR exists.

### GAP-OPENAPI-008: OperationId, tag and schema naming

Status: `blocking-openapi-gate-tooling`

Finding:

Endpoint and DTO standards imply stable OpenAPI structure, but operation IDs, tags, schema naming, error schema references and security scheme naming are not yet defined in enough detail for reusable OpenAPI assertions.

Recommended resolution:

Create an OpenAPI naming and schema standard before or together with the first OpenAPI gate helper.

### GAP-TEST-009: Test taxonomy and fixture strategy

Status: `blocking-maven-gate-tooling`

Finding:

The gate concept defines layers G0-G6, but the project still lacks a test strategy standard that maps unit tests, mapper tests, MockMvc tests, OpenAPI tests, integration tests, architecture scans and target-comparison reports to Maven phases and profiles.

Recommended resolution:

Create a test strategy and gate execution standard before binding checks to `mvn test` or a quality profile.

### GAP-CONFIG-010: Configuration, profiles and environment contract

Status: `important-before-demo-runtime`

Finding:

Springmaster has environment and project-new documentation, but no consolidated application configuration standard for Spring Boot profiles, local `.env`, secrets, test database behavior, feature flags, actuator exposure and generated OpenAPI availability.

Recommended resolution:

Create a configuration/profile standard before Catalog-demo becomes runtime-canonical.

### GAP-DB-011: Liquibase and database migration standard

Status: `important-before-persistent-demo`

Finding:

DBTool concepts exist, but a canonical Liquibase naming, changelog, rollback, test database and stage-diff policy for Springmaster-built applications is not yet connected to the Catalog-demo readiness plan.

Recommended resolution:

Create a DB migration standard before implementing the first persistent CatalogItem slice.

### GAP-OBS-012: Observability and audit logging standard

Status: `important-before-production-reference`

Finding:

The error and persistence standards mention operational concepts, but logging, correlation, audit event content, actuator exposure and security-sensitive logging are not yet specified as a Springmaster standard.

Recommended resolution:

Create an observability standard before Catalog-demo is used as a production-style reference.

## Rules that are not too broad

The current standards intentionally avoid forcing a single implementation style in areas where IDM and Personnel differ. This is correct:

| Area | Current position | Review |
|---|---|---|
| UseCaseHandler versus Query/CommandService | both allowed with selection rules | suitable; keeps simple resources simple and complex aggregates explicit |
| MapStruct versus manual mapper | MapStruct preferred for structural mapping; manual allowed for complex read models | suitable; avoids false uniformity |
| Security placement | service/use-case boundary preferred, controller only as coarse HTTP gate | suitable; protects reused operations |
| ArchUnit timing | deferred until package boundaries stabilize | suitable; reflection scans are better first gates |
| Metadata and NumberSequence | deferred | suitable; these are real-app needs but not safe to freeze too early |

## Rules that must not become too narrow

The following areas need ADR-backed flexibility before automated checks become strict:

| Area | Risk | Required guardrail |
|---|---|---|
| Persistence identity | gate could forbid legitimate internal IDs | ADR-0004 must define default and exception criteria |
| Security implementation | gate could require full auth too early | deferred-security must have explicit evidence and expiration |
| Command result shapes | gate could require one DTO for all commands | standard must distinguish no-content, result-body and partial-result cases |
| Mapping style | gate could force MapStruct everywhere | gate should check forbidden dependencies and tests, not mapper technology alone |
| `/reference-data` | gate could block legitimate bounded read models | ADR-backed exception path is needed |

## Missing standard specifications

The following specifications are still needed for a reliable Springmaster backend platform:

| Priority | Specification | Reason |
|---|---|---|
| P0 | API query canonicalization addendum | resolved by 000058 and amended by 000091; `sortBy`, `/options`, ADR-backed `/reference-data`, complete-result-set `/all` and non-canonical ambiguous `/all` are now defined |
| P0 | ADR governance and standards-to-ADR mapping | converts documented standards into durable decisions |
| P0 | OpenAPI naming and schema standard | required before reusable OpenAPI assertions |
| P0 | Test strategy and gate execution standard | required before Maven-bound checks |
| P1 | Permission catalog and capability contract standard | required before security gates |
| P1 | Configuration/profile/environment standard | required before runtime reference applications |
| P1 | Liquibase/DB migration standard | required before persistent Catalog-demo |
| P1 | Error operation and observability addendum | required for operationally useful error/audit behavior |
| P2 | Metadata/KeyValue standard | needed when demo or target apps require dynamic attributes |
| P2 | NumberSequence/business-number standard | needed before business numbers become canonical |
| P2 | Event/outbox/audit-trail standard | needed before reporting/integration patterns become canonical |
| P2 | Tenant/data-scope standard | needed before multi-tenant or scoped data access becomes canonical |
| P2 | API versioning/deprecation standard | needed before target projects are supplied |

## ADR coverage review

Current ADR coverage is insufficient for a reliable architecture baseline.

Only `ADR-0001` exists as an accepted foundational ADR. The later standards document many valid decisions, but they do not yet carry the long-term governance properties of ADRs:

* context and alternatives;
* decision scope;
* rejected options;
* consequences;
* exception criteria;
* relation to Core, Demo, Tooling and target-project comparison.

The ADR backlog is documented separately in:

```text
PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md
```

Minimum ADRs before target-project delivery:

| ADR | Purpose | Priority |
|---|---|---|
| ADR-0002 API Boundary and Endpoint Contract | endpoint, DTO, validation, error and public API vocabulary | P0 |
| ADR-0003 Application Layer and Transaction Boundary | controller/service/use-case/transaction default | P0 |
| ADR-0004 Persistence Identity and DomainEntity Strategy | public ID, persistence identity, optimistic locking and exception criteria | P0 |
| ADR-0005 Security and Permission Boundary | permission model, auth placement and capability concept | P1 |
| ADR-0006 Verification and Gate Strategy | OpenAPI, MockMvc, reflection, ArchUnit and Maven quality gates | P0 |
| ADR-0007 Catalog-demo Canonicalization Strategy | readiness and proof criteria for reference implementation | P0 |
| ADR-0008 Configuration and Runtime Profile Strategy | Spring profiles, env files, secrets, OpenAPI and actuator exposure | P1 |
| ADR-0009 Database Migration and DBTool Strategy | Liquibase, test database, stage diff and migration gates | P1 |
| ADR-0010 Observability and Error Trace Strategy | error IDs, correlation, logging and audit traces | P1 |

## Interface and test utility candidates

The following interfaces and utilities should be specified before they are implemented. They are candidates, not automatic implementation instructions.

### Core/API contracts

| Candidate | Purpose | Gate value |
|---|---|---|
| `ExternalIdentifiable` | expose opaque public ID contract | reflection and DTO/entity boundary checks |
| `ApiErrorResponse` / `ApiViolation` | Java representation of the error contract | MockMvc and OpenAPI error assertions |
| `PagedQuery` / `SortDirection` | canonical page/sort abstraction without Spring Data leakage | query validation and controller-boundary scans |
| `PagedResponseDTO<T>` hardening | stable list response envelope | OpenAPI and MockMvc list assertions |
| `CommandDTO` / `CommandResultDTO` | command boundary classification | OpenAPI schema and command endpoint checks |
| `ReferenceOptionDTO` | `/options` response shape | OpenAPI option endpoint checks |
| `PermissionDescriptor` / `PermissionCatalog` | permission inventory | security gate and capability checks |
| `ApplicationCommandHandler<C,R>` | use-case handler shape | application-layer boundary checks |
| `ApplicationQueryService` / `ApplicationCommandService` markers | explicit service role classification | transaction and repository-boundary scans |
| `BoundaryMapper<S,T>` marker | optional mapper role classification | mapper dependency scans |

### Test and gate utilities

| Candidate | Gate layer | Purpose |
|---|---|---|
| OpenAPI path assertion helper | G1 | verify canonical paths, methods and absence of body-bearing `DELETE` |
| OpenAPI schema assertion helper | G1 | verify required fields, DTO schema names and error schemas |
| OpenAPI query assertion helper | G1 | verify `page`, `size`, `sortBy`, `sortDir` and documented filters |
| MockMvc error assertion helper | G2 | verify standard error envelope and violations |
| MockMvc validation assertion helper | G2 | verify `400` validation behavior |
| PagedResponse assertion helper | G2 | verify list response body shape |
| Controller boundary scan | G3 | detect entities, `Pageable`, `Page<DTO>`, repositories and controller transactions |
| Mapper dependency scan | G3 | detect repositories/services/external clients in mapper classes |
| Security classification scan | G4 | detect unclassified management endpoints |
| Permission catalog assertion helper | G4 | verify operation permissions and capability exposure |

## Gate implementation guardrails

Before the first gate-tooling seed is implemented, every candidate check must be classified as one of:

| Classification | Meaning |
|---|---|
| `ready-for-tooling` | standard is settled enough for implementation |
| `needs-standard-fix` | a documented inconsistency must be resolved first |
| `needs-ADR` | architectural decision is not durable enough yet |
| `demo-only-first` | implement only against Catalog-demo before generalizing |
| `manual-review-only` | rule remains qualitative for now |
| `deferred` | intentionally not implemented in the current phase |

Initial classification:

| Gate candidate | Classification | Reason |
|---|---|---|
| bodyless single delete OpenAPI check | ready-for-tooling | accepted strict rule |
| no public `findOne`/`findFirst`/`findLast` paths | ready-for-tooling | accepted endpoint vocabulary rule |
| no public `Pageable` controller parameter | ready-for-tooling after Java scan design | accepted DTO boundary rule |
| no public `Page<DTO>` response body | ready-for-tooling after Java scan design | accepted DTO boundary rule |
| required fields visible in OpenAPI | ready-for-tooling after schema naming standard | current standard is valid, schema naming still needed |
| query parameters `page`, `size`, `sortBy`, `sortDir` | ready-for-tooling | `sortBy` is canonical since 000058; `sort` is legacy/target-comparison vocabulary |
| ambiguous `/all` detection | ready-for-tooling | ambiguous, selector-like, undocumented or silently capped `/all` is non-canonical; complete-result-set `/all` is accepted when explicit evidence exists |
| error body shape | ready-for-tooling | `errorId`, `correlationId`, `traceId`, `messageKey`, `message` and `localMessage` clarified by 000059 |
| permission classification | demo-only-first | deferred security needs minimum evidence |
| persistence identity | needs-ADR | internal surrogate-ID exception criteria missing |
| mapper dependency scan | ready-for-tooling after package/naming design | accepted rule, implementation detail open |
| ArchUnit package boundaries | deferred | package structure not mature enough for broad ArchUnit yet |
| target-project comparison | deferred | only after Catalog-demo proof |

## Recommended gap work order

The gap work order has been refined by patches `000058` through `000062`.

Resolved or accepted items:

1. `000058_springmaster_api_query_reference_data_consistency_standard`
   * `sortBy` and `/all` versus `/options`/`/reference-data` resolved.
2. `000059_springmaster_api_error_identity_and_statuscode_consistency_standard`
   * error identity and first-slice status-code defaults resolved.
3. `000060_springmaster_adr_governance_and_backlog_alignment`
   * ADR template/index/backlog state established.
4. `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract`
   * API boundary and endpoint decisions accepted as ADR-0002.
5. `000062_springmaster_adr_0006_verification_and_gate_strategy`
   * test/gate execution strategy accepted as ADR-0006.

Next high-priority ADR work before strict gates or Catalog-demo canonicalization:

1. `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy`
2. `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy`
3. `000066_springmaster_adr_0005_security_and_permission_boundary`

A first `springmaster_api_contract_gate_tooling_seed` may now be implemented as report-only diagnostics after the selected next-step decision, but strict gates still require rule-specific readiness and the remaining domain ADRs where applicable.

## Catalog-demo readiness implication

Catalog-demo remains the correct next reference project, but it must not be expanded into canonical domain code until the P0 gaps are resolved or explicitly marked as accepted exceptions.

The existing CatalogItem seed remains useful as a technical seed. It is not a standard-compliant reference slice until it satisfies the readiness plan and the gap resolutions from this review.

## Final status

Springmaster is conceptually mature enough to continue gap closure. It is not yet mature enough to encode all standards into tool checks.

The next phase should not change target projects. It should first close the documented gaps, then implement a minimal gate tooling seed against Catalog-demo only.


## Gap closure update since 000058

Patch `000058_springmaster_api_query_reference_data_consistency_standard` closes the first P0 consistency gap for query vocabulary. Patch `000091_springmaster_list_query_export_all_contract` amends the `/all` decision. The canonical query vocabulary for new reference APIs is now `page`, `size`, `sortBy`, `sortDir` plus documented filters for paged lists; complete-result-set `/all` is canonical for export, batch and integration consumers; ambiguous, selector-like, undocumented or silently capped `/all` remains non-canonical; `/options` is the bounded selector vocabulary; `/reference-data` requires ADR-backed semantics.

This moves the query/reference-data part of the gate matrix from `needs-standard-fix` to `ready-for-tooling`. Remaining P0/P1 gaps include OpenAPI naming, ADR coverage, test strategy, permission catalog, configuration/profile standards, DB migration standards and broader observability implementation standards.


## 000059 update

`000059_springmaster_api_error_identity_and_statuscode_consistency_standard` resolves `GAP-API-ERROR-003` and `GAP-API-ENDPOINT-004` at standard level.

Gate tooling can now rely on:

- required `errorId` semantics;
- optional `correlationId`, `traceId`, `messageKey` and `localMessage` fields;
- full update default `200 OK` with body for Catalog-demo;
- bodyless single delete default `204`/`404` behavior;
- delete-multiple default `200 OK` with result DTO;
- `202 Accepted` only with a status/job/operation contract.


## 000060 ADR governance update

Patch `000060_springmaster_adr_governance_and_backlog_alignment` closes the governance gap identified by this review at documentation level.

Resolved review findings:

- ADR status semantics are now defined in `PROJECT_DOCS/ADR/ADR_GOVERNANCE_AND_BACKLOG_ALIGNMENT.md`.
- New ADRs must follow `PROJECT_DOCS/ADR/ADR_TEMPLATE.md`.
- `ADR_GAP_BACKLOG.md` now distinguishes planning status, priority and tooling blocker class.
- ADR-0002, ADR-0006, ADR-0003, ADR-0004 and ADR-0007 have now been accepted through patches 000061 through 000065.
- Strict gate tooling must not encode ADR-required architectural rules before the corresponding ADR is accepted.
- Report-only tooling remains possible when findings are non-binding and clearly labeled.

Remaining high-priority gaps after 000060:

| Gap | Status | Next action |
|---|---|---|
| OpenAPI operationId/tag/schema naming | open | create dedicated API naming/schema standard or include in ADR-0002 |
| Test and gate execution strategy | accepted | ADR-0006 accepted by 000062 |
| API boundary decision record | accepted | ADR-0002 accepted by 000061 |
| Application layer transaction decision record | accepted | ADR-0003 accepted by 000063 |
| Persistence identity decision record | accepted | ADR-0004 accepted by 000064 |
| Catalog-demo canonicalization decision record | accepted | ADR-0007 accepted by 000065 |
| Security permission decision record | needed | draft after P0 ADRs or before strict security gates |
| Config/profile, DB migration and observability standards | needed | handle after P0 architecture ADRs |

Updated gate-readiness verdict:

- API-boundary documentation-level standards are now backed by accepted ADR-0002; remaining P0 standards are coherent enough for ADR drafting.
- They are not yet sufficient for strict gate implementation.
- A future report-only tooling seed is acceptable after the P0 ADRs are accepted or explicitly scoped to non-binding diagnostics.



## 000061 ADR-0002 acceptance update

Patch `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepts the API boundary and endpoint contract ADR.

Resolved review finding:

- API boundary, endpoint vocabulary, DTO/validation boundary, query/reference-data vocabulary, error contract, command endpoint semantics and first-slice status-code defaults are now ADR-backed for new Springmaster reference APIs.

Gate-readiness impact:

- API-boundary gate candidates can reference ADR-0002 as accepted decision input.
- Strict gate execution still requires ADR-0006 for severity, report structure, Maven binding and fail/report-only behavior.
- OpenAPI operationId/tag/schema naming remains open and must be resolved before strict schema-naming gates.



## 000062 ADR-0006 acceptance update

Patch `000062_springmaster_adr_0006_verification_and_gate_strategy` accepts the verification and gate strategy ADR.

Resolved review finding:

- Gate execution modes, severity vocabulary, report structure, future Maven profile names, fail/report-only behavior and target-comparison policy are now ADR-backed.

Gate-readiness impact:

- A first API contract gate tooling seed may now be implemented as report-only diagnostics.
- Strict gate execution remains blocked per rule until the implementation is stable, tested, report-backed and explicitly promoted.
- Controller/service boundaries are ADR-backed by ADR-0003; persistence, security and Catalog-demo canonicalization strict gates still need their corresponding ADRs.

## 000063 ADR-0003 acceptance update

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts the application-layer and transaction-boundary ADR.

Resolved review finding:

- controller responsibility, service/use-case shape, repository boundary, mapper boundary and transaction ownership are now ADR-backed for new Springmaster reference APIs.

Gate-readiness impact:

- G3 Java boundary diagnostics may reference ADR-0003 in report-only mode.
- Strict controller/service/transaction gates remain blocked until implementation evidence, Catalog-demo proof and explicit strict promotion exist under ADR-0006.
- Persistence identity is now ADR-backed by ADR-0004. Catalog-demo canonicalization is ADR-backed by ADR-0007 after 000065. Security permission remains the next high-priority ADR gap.




## 000064 ADR-0004 acceptance update

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts the persistence identity and DomainEntity ADR.

Resolved review finding:

- persistence identity, public API identity, business-key separation, `DomainEntity` default usage, internal surrogate-ID exception criteria, `persistenceVersion`, audit fields and repository boundary are now ADR-backed for new Springmaster reference APIs.

Gate-readiness impact:

- G3 persistence identity diagnostics may reference ADR-0004 in report-only mode.
- Strict persistence gates remain blocked until implementation evidence, Catalog-demo proof and explicit strict promotion exist under ADR-0006.
- Catalog-demo canonicalization is accepted by ADR-0007 after 000065; strict G5 gates still require implementation evidence and ADR-0006 promotion.

## 000065 ADR-0007 acceptance update

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts the Catalog-demo canonicalization ADR.

Resolved review impact:

- the existing CatalogItem seed is explicitly non-canonical and remains `legacy-demo-seed`;
- a future CatalogItem implementation patch must declare whether it creates a candidate or canonical slice;
- canonicalization requires evidence for endpoint, DTO, validation, error, application-layer, persistence, mapping, security-classification, gate-evidence and deferral topics;
- report-only G5 diagnostics may now use ADR-0007 as rule source;
- security permission details remain owned by ADR-0005.

## ADR-0005 closure since 000066

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` closes the security ADR gap identified by this review.

Resolved for report-only readiness:

- security classification is now ADR-backed;
- permission naming and Catalog-demo first permission vocabulary are ADR-backed;
- authorization placement at service/use-case/application operation boundaries is ADR-backed;
- `documented-deferred-security` evidence is defined for Catalog-demo candidate slices;
- G4 security diagnostics may reference ADR-0005 in report-only mode.

Still deferred:

- concrete Spring Security configuration;
- JWT/session/claim mapping;
- permission catalog Java implementation;
- role persistence;
- tenant/data-scope policy;
- strict security gate promotion.

# Real App Pattern Forensics: IDM and Personnel

## Purpose

This document records the first forensic comparison of the current IDM and Personnel application exports against Springmaster's emerging standards.

The goal is not to supply existing applications. The goal is to identify which patterns Springmaster still has to standardize through ADRs, documents, Java contracts, reusable test utilities or quality gates before Catalog-demo becomes the canonical reference implementation.

## Inputs

| Input | Role in this analysis |
|---|---|
| `springmaster_export_full_2026-06-29T11-26-54-261995Z.zip` | Springmaster baseline after `000046_springmaster_api_endpoint_contract_standard` |
| `idm_export_full_2026-06-29_09-08-52-257Z.zip` | real application comparison input for API-readiness, assignment commands, OpenAPI contract tests and IDM-style use-case handlers |
| `personnel_export_full_2026-06-29_09-04-22-176Z.zip` | real application comparison input for aggregate-rich domain services, staffing commands, metadata, state transitions, security tests and reference-data/capability endpoints |

## Boundary

This analysis is documentation-only.

It does not authorize changes to IDM, Personnel, Contacts, Orders or other target projects. Existing applications remain comparison inputs only. Catalog-demo remains the first intended Springmaster proof target.

## Spring-aligned interpretation rules

Springmaster should use Spring Boot and Spring Framework capabilities deliberately, not blindly.

The following interpretations apply to this analysis:

| Spring capability | Springmaster interpretation |
|---|---|
| Root package and component scanning | keep the application root package above application and core packages; do not let reference projects rely on accidental component discovery |
| `@RequestMapping`, `@GetMapping`, `@PostMapping`, `@PutMapping`, `@PatchMapping`, `@DeleteMapping` | use explicit, stable HTTP contracts; do not expose Java repository vocabulary as public API vocabulary |
| `@RequestBody` with Bean Validation | inbound request DTOs must use Bean Validation and controller methods must activate validation with `@Valid` where JSON request bodies are used |
| Spring MVC exception handling | define one Springmaster API error contract before Catalog-demo exposes canonical errors; evaluate compatibility between existing `ErrorResponse` and Spring Framework Problem Details support |
| MockMvc | use MVC contract tests for request/response behavior without requiring a running HTTP server |
| OpenAPI generation | treat generated OpenAPI as an API boundary artifact that must be tested for required fields, query parameters, request bodies, response schemas and status codes |

## Observed real-application inventory

The inventory below is intentionally descriptive. It does not define the final Springmaster rules by itself.

| Observation | IDM | Personnel | Springmaster implication |
|---|---|---|---|
| Main domain controllers | 9 IDM domain controllers plus system/info controllers | 17 Personnel domain controllers plus system/info controllers | Catalog-demo must demonstrate both simple management resources and aggregate commands |
| Request-body validation | JSON command/create/update request bodies generally use `@Valid @RequestBody` | most write command request bodies use `@Valid @RequestBody`; metadata patch/replace needs explicit standard review | Springmaster must define validation as mandatory for inbound DTOs and test it |
| Paged API response shape | controllers return `PagedResponseDTO` for paged IDM list endpoints | UI-facing controllers still expose Spring `Page<DTO>` in several places | Springmaster should standardize `PagedResponseDTO` or equivalent external DTO, not Spring `Page` as public contract |
| Controller `Pageable` exposure | not exposed in IDM controllers; used behind service/repository boundary | exposed in several Personnel controllers | controller signatures must use explicit query parameters or dedicated query DTOs; `Pageable` stays internal |
| Legacy `/list` paths | IDM uses `/list` for paged lists | Personnel generally uses the collection path for lists | 000046 already makes collection path canonical for new APIs; `/list` is comparison/legacy vocabulary only |
| Single delete | bodyless `DELETE /{id}` and bodyless relationship delete paths exist | bodyless `DELETE /{id}` and nested bodyless deletes exist | carry forward bodyless single delete as standard |
| Delete multiple | no stable reusable delete-multiple pattern found in these exports | no stable reusable delete-multiple pattern found in these exports | keep 000046 command-based delete-multiple standard and prove it first in Catalog-demo |
| Assignment commands | IDM has explicit assignment controllers and OpenAPI tests for bodyless unassign deletes | Personnel has assignment/position-filling commands with richer aggregate semantics | Springmaster needs separate relationship/assignment command rules |
| State transitions | IDM uses endpoint-specific update commands such as activate/deactivate/change-password | Personnel uses `/state/...` controllers for transitions | Springmaster must decide whether `/commands/<command>` is sufficient or whether state-transition command subpaths need a documented specialization |
| Error handling | global `ErrorResponse`; IDM adds domain-scoped 400 handling for invalid query parameter enum/type values | global `ErrorResponse` with error event id and localized message | API error contract is a high-priority missing standard before Catalog-demo becomes canonical |
| Security enforcement | heavy use of `@PreAuthorize`, often in handlers/services | heavy use of `@PreAuthorize`, generally in domain/query/command services | Springmaster should standardize where authorization checks live and how permission catalogs are tested |
| Service style | use-case/handler style is common for commands and assignment operations | query service / command service / domain service style is common for complex aggregates | Springmaster should allow both styles with explicit selection criteria |
| Transaction boundary | many handlers/services are `@Transactional`, with read-only queries separated from commands | domain/query/command services own most transactions | controller methods should not become the standard transaction boundary |
| Mapping | MapStruct exists, but IDM also uses manual/use-case mapping | MapStruct with strict unmapped-target policy appears for simple mappings; manual mappers are used for complex read models | Springmaster should prefer MapStruct for simple DTO mapping and allow manual mappers for projections |
| Metadata | application-local metadata controllers and DTOs exist | metadata is a visible API surface for persons and organisation units | metadata/tagging needs a dedicated Core/API standard, not only DTO marker types |
| Capability/reference endpoints | IDM has auth/current-user style APIs | Personnel has current-user capabilities and reference-data endpoints | Springmaster must distinguish management resources from support/reference endpoints |
| Contract tests | IDM has explicit OpenAPI contract tests for assignment commands, list/filter contracts and required fields | Personnel has request validation and OpenAPI required-field contract tests plus broad security integration tests | Springmaster should extract reusable contract-test helpers and gate categories |

## Pattern decisions for Springmaster

### Adopt as Springmaster direction

| Pattern | Reason |
|---|---|
| Bodyless single `DELETE` | consistent with 000044/000046 and present in both real applications |
| Separate request DTOs and response DTOs | prevents entity leakage and supports OpenAPI required-field visibility |
| `@Valid @RequestBody` on inbound JSON DTOs | aligns with Spring MVC validation and makes request validation testable |
| Stable `PagedResponseDTO`-style response shape | avoids exposing Spring `Page` internals as REST contract |
| Explicit query parameters or query DTOs at controller boundary | avoids generated OpenAPI artifacts from framework-level `Pageable` |
| OpenAPI contract tests | proven valuable in IDM and Personnel for API-readiness |
| MockMvc integration tests for controller behavior | matches the current test style and can become reusable gate infrastructure |
| Permission/security integration tests | necessary before Springmaster can claim management-API readiness |
| Query/command separation for complex aggregates | Personnel demonstrates that rich domains need different service seams than simple CRUD resources |
| Use-case/handler style for granular commands | IDM demonstrates that assignments and permission-sensitive operations benefit from narrow handlers |

### Do not adopt as new canonical Springmaster standard

| Existing pattern | Reason |
|---|---|
| Public `/list` as the canonical paged-list path | retained only as legacy/comparison vocabulary; 000046 makes the collection path canonical |
| Public API names based on `findOne`, `findFirst`, `findLast` | these are repository/service vocabulary and require a domain-specific public name if exposed at all |
| Controller-level `Pageable` as public API boundary | creates weak OpenAPI contracts and leaks framework internals |
| Public `Page<DTO>` response contracts | leaks Spring Data representation and weakens frontend/API stability |
| Unbounded `/all` for management APIs | must not become default; bounded `/options` or explicit reference-data endpoints are safer |
| Local controller-specific error maps | Springmaster needs one canonical error contract |

### Defer until explicit standard/ADR exists

| Topic | Reason for deferral |
|---|---|
| API error contract: existing `ErrorResponse` versus Problem Details adaptation | existing apps use operational `errorId` and localized messages; Spring Framework supports Problem Details, so the decision must be explicit |
| State-transition endpoint specialization | Personnel's `/state/<command>` pattern is useful, but 000046 currently standardizes `/commands/<command>`; this requires reconciliation |
| Relationship/assignment endpoint standard | IDM assignment endpoints and Personnel assignment commands solve related but not identical problems |
| Metadata/tagging persistence and API standard | Springmaster has DTO/Core seeds but no full canonical persistence/API standard yet |
| Permission catalog naming and placement | both apps use permissions extensively, but not with one reusable catalog model |
| NumberSequence/business-key standard | real applications contain business-key and sequence-like needs; Springmaster has not defined the reusable core standard yet |
| Mapping standard | MapStruct and manual mappers both appear; the rule must be conditional rather than absolute |

## Required standards before Catalog-demo becomes canonical

Catalog-demo must not accidentally freeze incomplete or legacy patterns. The following standards should exist before the CatalogItem slice becomes the canonical model for new projects.

| Priority | Standard or ADR | Minimum content |
|---:|---|---|
| 1 | API Error Contract Standard | response shape, status mapping, validation errors, not-found, conflict, access denied, authentication, correlation/error id, OpenAPI representation |
| 2 | DTO Boundary and Validation Standard | inbound/outbound DTO naming, Bean Validation requirement, `@Valid` usage, no entities in public controller bodies, required-field OpenAPI gates |
| 3 | List/Query/Paging Gate Standard | explicit controller parameters, allowed sort fields, `sortDir` enum, page/size constraints, external response DTO, OpenAPI assertions |
| 4 | Command and Relationship Endpoint Standard | create/update/delete/delete-multiple, state transitions, nested aggregate commands, assignment/unassignment rules, status codes |
| 5 | Controller-Service-UseCase Transaction Standard | resolved documentation-first by 000050; defines simple resource service, query/command services, use-case handlers, transaction ownership and repository/controller boundaries |
| 6 | API Error and Request Validation Test Utilities | MockMvc helpers for positive/negative request cases and error response assertions |
| 7 | OpenAPI Contract Test Utilities | reusable schema/path/parameter/requestBody/status-code assertions |
| 8 | Security and Permission Boundary Standard | resolved documentation-first by 000052; defines endpoint classification, permission naming, role mapping, authorization placement, current-user/capability endpoints and future gates |
| 9 | DomainEntity/Persistence Foundation Standard | internal id/external id, optimistic locking, auditing, business key, repository/service seams |
| 10 | Metadata/Tags/Reference Data Standard | metadata endpoint shape, patch/replace semantics, selector/reference-data boundaries |
| 11 | Mapping Standard | MapStruct strict mode for simple mapping; manual mappers for projections; no repository access in mappers |
| 12 | Architecture Gate Backlog | package boundaries, controller dependency rules, entity exposure rules, optional ArchUnit adoption |

## Catalog-demo readiness rules

Catalog-demo may start its canonical CatalogItem API only after the high-priority standards above are resolved at least as documentation-level decisions.

The first CatalogItem API must demonstrate:

* canonical collection list on the resource collection path;
* explicit query parameters or a documented query DTO, not controller-level `Pageable`;
* stable paged response DTO;
* detail by opaque external id;
* create/update request DTO validation;
* bodyless single delete;
* command-based delete-multiple only if a business use case requires it;
* standard error response behavior;
* OpenAPI visibility for required fields, query enums, path parameters, request bodies and status codes;
* MVC/contract tests that fail if the API drifts from the standards.

## Gate backlog derived from real applications

| Gate candidate | Evidence source | First Springmaster target |
|---|---|---|
| OpenAPI required-field assertion helper | IDM and Personnel contract tests | reusable test helper after DTO standard |
| OpenAPI query-parameter assertion helper | IDM list/filter contract tests | list/query gate |
| DELETE request-body absence assertion | IDM assignment command contract test | command/delete gate |
| Status-code matrix assertion | IDM assignment command contract test | endpoint contract gate |
| Controller DTO-boundary reflection scan | real applications rely on DTOs but do not have one generic gate | architecture gate |
| Controller `Pageable` exposure scan | Personnel exposes `Pageable` in selected controllers | architecture/API gate |
| Public `Page<DTO>` response scan | Personnel exposes `Page<DTO>` in selected controllers | architecture/API gate |
| Permission mapping test helper | Personnel role-permission mapping tests | security gate |
| Command security test template | Personnel command security tests | security gate |
| Global error response contract test | both apps use `ErrorResponse` patterns | error contract gate |

## Implementation-sequence recommendation

Recommended next documentation/code sequence after 000051:

1. `000048_springmaster_api_error_contract_standard` is completed as documentation-only.
2. `000049_springmaster_dto_boundary_and_validation_standard` is completed as documentation-only.
3. `000050_springmaster_controller_service_usecase_transaction_standard` is completed as documentation-only.
4. `000051_springmaster_domain_entity_persistence_standard` is completed as documentation-only.
5. `000052_springmaster_security_permission_boundary_standard` is completed as documentation-only.
6. Next, define command/relationship endpoint specialization, mapping rules or the first API contract gate concept.
7. Start Catalog-demo only when the first API slice can follow the endpoint, error, DTO/validation, controller/service/transaction, domain/persistence and security/permission standards.

## Final assessment

IDM contributes the strongest current API-readiness and OpenAPI contract-test patterns. Personnel contributes the strongest aggregate, command, lifecycle, security and reference-data patterns. Springmaster must combine these deliberately.

The next maturity step is therefore not more CatalogItem domain modeling. The next maturity step is to turn the high-priority gaps from this document into Springmaster-owned standards and initial gate concepts.

## 000052 Resolution Note

Patch `000052_springmaster_security_permission_boundary_standard` resolves the security/permission boundary item documentation-first. Remaining high-priority topics are command/relationship endpoint specialization, mapping rules and the first reusable API contract gate concept.


## Command and relationship endpoint resolution since 000053

Patch `000053_springmaster_command_relationship_endpoint_standard` resolves the command/relationship specialization gap identified by this forensics document.

IDM remains the stronger source for bodyless assignment deletes and OpenAPI command checks. Personnel remains the stronger source for richer aggregate commands, state changes and capability/reference-data-style management APIs. Springmaster does not copy either shape directly. It uses the 000046 endpoint baseline plus the 000053 specialization as the new reference rule for Catalog-demo.

Future comparison of IDM and Personnel should classify existing command and relationship endpoints as compatible, transitional or project-specific only after Catalog-demo and reusable command gates exist.

## Mapping standard resolution since 000054

Patch `000054_springmaster_mapping_standard` resolves the mapping-rules gap identified by this forensics document.

IDM remains a comparison input for use-case-oriented mapping around management and assignment APIs. Personnel remains a comparison input for aggregate-rich manual mapping, read-model assembly and security-sensitive response shaping. Springmaster does not copy either application directly. The new mapping standard defines a neutral rule set: deterministic DTO/application/entity mapping, MapStruct where useful, manual mappers where clearer, and strict exclusion of repository access, transaction handling, authorization and business policy from mapper classes.

Future comparison of IDM and Personnel should classify existing mappers as compatible, transitional or project-specific only after Catalog-demo and reusable mapping gates exist.

## Gate concept follow-up since 000055

Patch `000055_springmaster_api_contract_gate_concept` converts the repeated gate findings in this forensic comparison into a dedicated gate concept.

The comparison remains read-only. IDM and Personnel are not target-update recipients. Their current value is to provide examples for future gate candidates, especially OpenAPI contract tests from IDM and aggregate/security behavior tests from Personnel.

The first gate proof must happen in Catalog-demo. Only after the gate model is demonstrated there should Springmaster create read-only comparison reports for IDM and Personnel.

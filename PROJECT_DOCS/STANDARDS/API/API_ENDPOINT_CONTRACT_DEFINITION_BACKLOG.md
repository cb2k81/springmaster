# API Endpoint Contract Definition Backlog

## Status

Accepted as documentation backlog with patch `000045_springmaster_api_endpoint_contract_definition_backlog`.

## Purpose

This document records the endpoint-contract definitions that Springmaster still needs before Catalog-demo is expanded into the canonical reference implementation.

Patch `000044_springmaster_api_standards_adr_extraction` defined the first generic API standards. The current question is narrower: endpoint operations such as list, get-by-id, find-one, first/last lookup, single delete and multiple delete must be sharpened before the demo domain starts to encode accidental or legacy-specific patterns.

This document is a definition backlog, not a finished endpoint standard. It establishes the topics that must become ADRs, standards, interfaces, reference implementations or gates.

## Forensic input

The current IDM and Personnel exports show different but valuable patterns.

IDM is currently the stronger source for API-readiness gates. It demonstrates bodyless single assignment deletes, OpenAPI contract assertions for delete request-body absence, list query enum exposure, date-time range filters and required-field visibility.

Personnel is currently the stronger source for complex domain and aggregate operations. It demonstrates nested aggregate commands, state-transition endpoints, reference-data and current-user capability endpoints, richer query services and repository methods such as `findOne`, `findFirst...OrderBy...` and ordered relationship lookups.

Springmaster currently has an internal CatalogItem seed, but that seed is not yet sufficient as canonical endpoint reference. It does not yet prove the full list/detail/create/update/delete/bulk/search/error/OpenAPI gate matrix.


## Resolution status since 000046

Patch `000046_springmaster_api_endpoint_contract_standard` converts the core backlog items into the first canonical endpoint standard. The remaining backlog purpose is to track future gates, implementation follow-ups and specialized endpoint families that are not yet needed by Catalog-demo.

Resolved into the standard baseline:

- canonical paged collection path,
- bounded options/reference-data distinction,
- detail by opaque external id,
- alternate unique lookup vocabulary,
- prohibition of public `findOne`, `findFirst` and `findLast` vocabulary for management APIs,
- single bodyless delete,
- delete-multiple as collection command,
- state-transition command path pattern,
- complex search baseline,
- OpenAPI operationId and endpoint-gate targets.

Still deferred to later patches:

- structured error-body standard,
- Java interfaces or base classes,
- reusable OpenAPI contract test utilities,
- ArchUnit or reflection gates,
- Catalog-demo implementation,
- comparison and migration strategy for IDM and Personnel.

## Target-project boundary

This backlog does not authorize changes in IDM, Personnel, Contacts, Orders or any other existing target project.

Existing projects are comparison inputs only. Springmaster must extract reusable rules, demonstrate them in Catalog-demo and only later compare the existing apps against the proven standard.

## Endpoint operation taxonomy to define

Springmaster needs a stable operation taxonomy before implementation details are standardized.

| Operation group | Needs definition | Initial direction |
|---|---|---|
| Paged collection list | path shape, query parameters, response shape, sorting, filtering, max page size | mandatory for UI-capable management tables |
| Complete result-set `/all` | allowed use cases, naming, operational risk, frontend export and backend batch semantics | accepted by 000091 when paired with a paged/search query contract and not silently truncated |
| Detail by external id | path shape, status codes, DTO shape, external-id semantics | canonical detail operation for resource APIs |
| Unique lookup / find-one | whether public API exposes lookup by business key, null behavior, conflict behavior | do not expose generic `findOne` vocabulary without domain semantics |
| First / last / latest / current | ordering rule, deterministic tie-breaker, domain naming, alternative via sorted paged list | `first`/`last` repository vocabulary must not leak to external API |
| Create | path, request DTO, response status, response body, location header policy | covered partially by command standard, needs endpoint matrix |
| Replace/update | PUT/PATCH policy, path id vs body id/version, optimistic locking behavior | needs explicit standard before demo update endpoint |
| State transition command | verb naming, PUT vs POST, idempotency, status code, request body policy | Personnel patterns require generic rule |
| Single delete | bodyless delete, path identity, 204/404/idempotency decision, soft/hard delete boundary | already partly standardized, needs detail matrix |
| Multiple delete | no body-bearing DELETE, command endpoint shape, result DTO, partial failure semantics | still open and must be standardized explicitly |
| Assignment add/remove | relationship path naming, add command, remove command, list assignments | IDM gives reusable source material |
| Nested aggregate command | nested path shape, child identity, parent-child conflict behavior | Personnel gives reusable source material |
| Reference data | bounded read model, cacheability, path naming | must not be confused with complete result-set `/all` export/batch semantics |
| Current user capabilities | auth context, response shape, permission exposure | security standard later |
| Complex search | GET query vs POST search command, side-effect-free guarantee, pagination | needs explicit rule for rich filters |

## Public endpoint vocabulary versus Java vocabulary

Springmaster must separate external API language from Java repository/service language.

External endpoints should use resource and domain vocabulary. They should not expose technical method names such as `findById`, `findOne`, `findFirst`, `findLast`, `loadPage` or repository-derived naming.

Internal Java naming remains free to use Spring Data and domain-service conventions, but those names must be translated at the API boundary.

The following distinction must become a standard:

| Concern | External API vocabulary | Java vocabulary |
|---|---|---|
| resource detail | `GET /api/<domain>/<resources>/{id}` | `getById`, `loadById`, `findById`, repository `findById` |
| optional unique lookup | domain-specific lookup path or filter contract | `findOne`, `findByBusinessKey`, `findBy...` |
| latest/current object | `/current`, `/latest` or sorted paged list with `size=1`, depending on domain semantics | `findFirst...OrderBy...`, `findTop...`, service helper |
| ordered collection | paged list with explicit `sortBy` and `sortDir` | repository ordering method or `Pageable` |
| internal first/last helper | no generic public `/first` or `/last` without domain meaning | stream `findFirst`, repository `findFirst...` |

Public `find`, `findOne`, `findFirst` and `findLast` endpoint names are prohibited unless an ADR explicitly defines them for a special integration API. For management/UI APIs, the public contract must state the domain meaning instead of the Java lookup technique.

## List and all-list contract decisions still required

Springmaster must decide whether the canonical list endpoint is the collection path itself or a `/list` subresource.

Current real-app evidence is mixed. IDM uses `/list` endpoints for UI-ready lists. Personnel uses collection paths in several places and also exposes nested collection reads. Springmaster must choose one canonical shape for Catalog-demo and document whether the other is legacy-compatible, discouraged or allowed for specific cases.

The following decisions are still required:

| Decision | Options | Why it matters |
|---|---|---|
| canonical paged list path | `GET /api/<domain>/<resources>` or `GET /api/<domain>/<resources>/list` | OpenAPI/YAML and UI generators need predictable paths |
| bounded selector/reference-data path | `/options`, ADR-backed `/reference-data`, no generic `/all` endpoint | prevents accidental unbounded endpoints |
| list response type | `PagedResponseDTO<T>` only, Spring `Page<T>`, or project-specific wrapper | external contract stability |
| query parameter shape | explicit params only, no raw `Pageable` in controller signatures | OpenAPI readiness |
| default sorting | per endpoint, global default, or mandatory explicit sort | deterministic UI behavior |
| sort field names | external names only, entity property names allowed, or mapping table required | prevents persistence leakage |
| invalid query behavior | reject with `400`, ignore, or default | deterministic client feedback |
| enum filters | enum schema required in OpenAPI or string-only allowed | YAML/UI readiness |
| date/time ranges | `fieldFrom`/`fieldTo`, exact `field`, or domain-specific naming | Personnel/IDM consistency |

## Detail, lookup and not-found decisions still required

The canonical detail operation is expected to be `GET /api/<domain>/<resources>/{id}` with an opaque external string id. The following decisions remain open and must be documented before Catalog-demo becomes reference:

| Decision | Required standard |
|---|---|
| missing id format | whether blank/malformed path ids map to `400` or `404` |
| syntactically valid but unknown id | whether detail returns `404` with standard error body |
| optional unique lookup | whether no match returns `404`, `204`, empty object or optional wrapper |
| duplicate match for unique lookup | whether this is `409`, `500`, or prevented by persistence constraint |
| alternate keys | whether lookup by SKU/business key is path-based or query-based |
| current/latest lookup | explicit domain semantics and deterministic ordering are mandatory |

Catalog-demo must not use `sku` as path identity unless Springmaster decides that SKU is the external id for the resource. If CatalogItem has both an opaque id and a business SKU, the API must demonstrate the difference explicitly.

## Delete contract decisions still required

Single deletes are already partially standardized: no request body, identity in path or query, successful no-body delete may return `204`.

The following details still need a sharper standard:

| Decision | Required standard |
|---|---|
| unknown id on delete | strict `404` versus idempotent `204` |
| soft delete versus hard delete | whether external delete means remove, deactivate, archive or anonymize |
| optimistic locking | whether delete requires version via query parameter, header, or command endpoint |
| authorization failure | consistent `403` behavior and error code |
| child-resource delete | parent id and child id path requirement |
| assignment delete | relationship identity path requirement |
| audit/event behavior | whether delete must emit audit/outbox events later |

## Delete-multiple contract decisions still required

Springmaster must explicitly standardize multiple delete because body-bearing `DELETE` is not allowed for single deletes and should not become the bulk workaround.

Candidate patterns to evaluate:

| Candidate | Shape | Notes |
|---|---|---|
| POST command endpoint | `POST /api/<domain>/<resources>/commands/delete` | clear command semantics, request DTO can contain ids and options |
| POST bulk-delete endpoint | `POST /api/<domain>/<resources>/bulk-delete` | easy for UI, less uniform with other commands |
| DELETE with repeated query ids | `DELETE /api/<domain>/<resources>?id=a&id=b` | bodyless but URL length and partial-failure semantics are problematic |
| async deletion job | `POST /api/<domain>/<resources>/commands/delete` returning `202` and job id | useful for large destructive operations |

The final standard must define at least:

- request DTO shape for ids, version tokens and reason/comment fields,
- atomic versus partial-success behavior,
- result DTO shape with deleted, skipped and failed ids,
- status code matrix for empty id list, unknown ids, conflict, authorization failure and partial failure,
- maximum batch size,
- whether dry-run/preview is allowed,
- OpenAPI gate assertions for command request and response schema,
- audit and security expectations.

Until this standard exists, Catalog-demo must not introduce delete-multiple as an ad hoc endpoint.

## State-transition and command endpoint decisions still required

Personnel uses several state-transition endpoints such as activate, deactivate, submit-for-review, approve and archive. Springmaster needs a generic state-command standard before these patterns are demonstrated.

Required decisions:

| Decision | Required standard |
|---|---|
| HTTP method | whether state transitions use `PUT`, `POST`, or operation-specific rule |
| command body | no body, minimal reason/comment DTO, or domain command DTO |
| idempotency | repeat-safe transitions versus conflict on repeated transition |
| response | no content, updated resource DTO, or command result DTO |
| invalid state | `409 Conflict` with standard error code |
| authorization | command-specific permission naming |
| OpenAPI naming | operationId and tag convention |

## Endpoint naming and path conventions still required

The following naming conventions must be decided before they are encoded in Catalog-demo:

| Topic | Required decision |
|---|---|
| domain segment | `/api/catalog/...`, `/api/demo/catalog/...`, or app-local base path |
| resource names | plural kebab-case, singular exceptions, aggregate child naming |
| operation segments | whether verbs are allowed only under `/commands/...` or also as action subresources |
| relationship paths | parent-child resource path versus assignment-resource path |
| metadata paths | `/metadata`, `/tags`, `/attributes` or separate resource |
| reference data paths | `/api/reference-data/<domain>` versus per-domain `/options` endpoints |
| current-user paths | `/api/current-user/...` versus domain-specific capability endpoints |
| operationId naming | OpenAPI operationId convention for generated clients |

## Gate backlog

The endpoint contract must become enforceable through tests and tooling after the documentary standard is accepted.

| Gate | Purpose | Candidate implementation |
|---|---|---|
| OpenAPI endpoint shape gate | verify paths, methods and absence of forbidden request bodies | JUnit reading `/v3/api-docs` |
| Query parameter gate | verify explicit paging, sorting, filter names, enum exposure and date formats | reusable OpenAPI assertion helper |
| Response schema gate | verify `PagedResponseDTO`, detail DTO, command result DTO | reusable JSON schema assertions |
| Delete gate | verify bodyless single deletes and defined bulk-delete command shape | OpenAPI + MockMvc tests |
| Retrieval vocabulary gate | reject public `/find`, `/find-one`, `/first`, `/last` in management APIs unless allow-listed | OpenAPI path inspection |
| Controller boundary gate | reject entities as request/response DTOs and raw `Pageable` where UI-ready API is expected | ArchUnit or custom reflection test |
| Status-code matrix gate | verify create/update/delete/list/search negative cases | MockMvc contract tests |
| Naming gate | verify kebab-case paths and operationId conventions | OpenAPI inspection |

## ADR backlog

The endpoint workstream needs the following ADRs or standard documents:

1. API endpoint operation taxonomy.
2. Resource path and naming convention.
3. Paged list and bounded all-list contract.
4. Detail, lookup and alternate-key retrieval contract.
5. Single delete and delete-multiple contract.
6. State-transition and command endpoint contract.
7. Assignment and relationship endpoint contract.
8. Complex search and filter contract.
9. API error/status-code contract.
10. OpenAPI endpoint gate and operationId contract.
11. Controller boundary and Java naming convention.

These ADRs may be combined when the scope remains coherent, but they must not be skipped before Catalog-demo is treated as canonical.

## Catalog-demo readiness rule

Catalog-demo may be prepared technically, but the CatalogItem API should not be expanded into a full reference implementation until the endpoint contracts above are decided at least for:

- paged list,
- detail by id,
- create,
- update,
- single delete,
- optional all-list/reference-data distinction,
- lookup by SKU or other alternate key,
- error/status behavior,
- OpenAPI gate expectations.

Delete-multiple, state transitions, assignment commands and complex search may be deferred, but their deferral must be explicit so the demo does not create accidental standards.

## Non-goals

This document does not define final endpoint paths for Catalog-demo.

This document does not change Springmaster Java code.

This document does not require Maven tests.

This document does not change IDM, Personnel or any other existing project.


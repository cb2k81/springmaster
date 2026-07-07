# ADR-0007: Catalog-demo Canonicalization Strategy

Status: Accepted

Date: 2026-06-30

Patch: `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy`

## Context

Springmaster is being built as the canonical maintenance base for shared Backend Foundation, Tooling, Standards, Conventions, Reference Implementations and later Quality Gates. Existing applications such as IDM, Personnel, Contacts and Orders remain comparison inputs only. They must not be supplied or remediated by Springmaster before the reference project has demonstrated the standards.

Catalog-demo already contains an early `CatalogItem` implementation seed. That seed was useful to validate the first Core and Demo slices, but it predates the consolidated API, application-layer, persistence, error, query/reference-data and gate standards. Therefore it must not automatically become the canonical reference pattern merely because it compiles or has tests.

Patch `000056_springmaster_catalog_demo_readiness_plan` introduced readiness criteria. Patches `000058` and `000059` narrowed query, reference-data, error identity and status-code decisions. Patches `000061`, `000062`, `000063` and `000064` accepted the main API, gate, application-layer and persistence ADRs. This ADR defines how Catalog-demo may move from seed code to a canonical Springmaster reference implementation.

## Decision

Catalog-demo becomes canonical only by explicit canonicalization evidence. The first `CatalogItem` slice may be implemented incrementally, but its lifecycle states are fixed:

| State | Meaning |
|---|---|
| `legacy-demo-seed` | existing pre-standard implementation used as historical seed and comparison input |
| `candidate-reference-slice` | implementation intentionally aligned to the standards but not yet fully proven |
| `canonical-reference-slice` | slice has required evidence, readiness summary and accepted deferrals |
| `deprecated-seed-fragment` | old seed behavior that must not be copied into new reference work |

No Java package, endpoint, DTO or test becomes canonical by naming convention alone. Canonical status requires a patch that explicitly states the state transition and records evidence.

## First canonical resource

The first canonical Catalog-demo resource is `CatalogItem` in the `catalog` domain.

The canonical public resource vocabulary is:

| Concern | Decision |
|---|---|
| Domain segment | `demo/catalog` |
| Resource segment | `items` |
| Collection | `GET /api/demo/catalog/items` |
| Detail | `GET /api/demo/catalog/items/{id}` |
| Create | `POST /api/demo/catalog/items` |
| Full update | `PUT /api/demo/catalog/items/{id}` |
| Single delete | bodyless `DELETE /api/demo/catalog/items/{id}` |
| Bounded selector | `GET /api/demo/catalog/items/options` only when a real selector use case exists |
| Complex search | deferred until simple list filters are insufficient |
| Collection command | deferred until a real non-CRUD command exists |

The first canonical slice must use `sortBy` and `sortDir` for sorting. It must not introduce `/all`. It must not introduce `/reference-data` without a later ADR-backed bounded reference-data decision.

## Required canonicalization evidence

A patch may declare the first `CatalogItem` slice canonical only when it provides a compact evidence summary covering these items:

| Evidence area | Minimum evidence |
|---|---|
| Endpoint contract | canonical paths and methods are present; public `findOne`, `findFirst`, `findLast`, `/all` and body-bearing single `DELETE` are absent |
| DTO boundary | public controller request and response types are DTOs; entities and Spring Data `Page` are not exposed as public API bodies |
| Validation | create/update bodies use Bean Validation and are executed through the public HTTP boundary |
| Query contract | list endpoint exposes `page`, `size`, `sortBy`, `sortDir` and documented filters only |
| Error contract | validation, not-found and conflict cases return the accepted standard error body with `errorId` |
| Status codes | create uses `201`; full update uses `200` with DTO; bodyless delete uses `204` on success and `404` when already absent |
| Application boundary | controllers remain thin HTTP adapters; repository and `EntityManager` access stays behind service/use-case boundaries |
| Persistence identity | public IDs are opaque strings; business keys such as `sku` remain explicit domain fields; `persistenceVersion` is used when persistence is active |
| Mapping | mapping is explicit and does not contain repository, authorization, transaction or external-client decisions |
| Security classification | every endpoint is classified; enforcement may be implemented or deliberately deferred with evidence |
| Gate evidence | G0 documentation, G1 OpenAPI or planned OpenAPI evidence, G2 MockMvc behavior tests and relevant G3 diagnostics are recorded |
| Deferrals | every missing standard is explicitly listed with owner, rationale and expected follow-up |

A canonicalization patch must be code/test-aware when it changes implementation. Documentation-only canonicalization is allowed only to define or review readiness, not to claim untested implementation behavior.

## Required first-slice behavior

Before `CatalogItem` is canonical, it must demonstrate at least these behaviors through tests or gate evidence:

- create valid item;
- reject invalid create body;
- retrieve detail by opaque ID;
- return not-found for unknown ID;
- list with paging and canonical sorting parameters;
- reject invalid list query;
- reject duplicate business key with conflict semantics;
- full update with update DTO;
- bodyless delete;
- reject or ignore non-canonical body-bearing single delete as a public contract;
- expose standard error identity fields in error responses.

Security `401` and `403` tests may be deferred only when the slice uses `documented-deferred-security` and records the intended permissions.

## Accepted deferrals for the first canonical slice

The first canonical `CatalogItem` slice may defer the following concerns when the deferral is explicit:

| Deferred concern | Condition |
|---|---|
| Complex search endpoint | absent until a real search use case exists |
| Delete multiple | absent until a real bulk use case exists |
| State transition commands | absent until a lifecycle exists |
| Relationship endpoints | absent until a second related resource exists |
| Nested aggregate commands | absent until a nested aggregate exists |
| `/options` endpoint | absent unless a bounded selector use case exists |
| `/reference-data` endpoint | absent until a dedicated ADR-backed reference-data use case exists |
| Full security enforcement | allowed only as `documented-deferred-security` with endpoint classification and intended permissions |
| OpenAPI generator tooling | may be a planned or report-only artifact before strict promotion |
| ArchUnit | may be deferred in favor of reflection/classpath diagnostics |

A deferral is not valid when it hides a non-canonical replacement. For example, `/all` is not an acceptable placeholder for a deferred `/options` or paged collection contract.

## Gate relationship

This ADR is the rule source for G5 Catalog-demo reference gates.

Report-only gates may now check whether a Catalog-demo slice is still `legacy-demo-seed`, `candidate-reference-slice` or `canonical-reference-slice`. Strict canonicalization gates require:

1. accepted ADR-0002, ADR-0003, ADR-0004, ADR-0006 and this ADR;
2. stable implementation of the relevant gate checks;
3. successful Catalog-demo evidence;
4. explicit strict-promotion under ADR-0006.

The first gate tooling seed should not rewrite Catalog-demo. It should report readiness and gaps.

## Relationship to existing target projects

This ADR does not authorize changes to IDM, Personnel, Contacts, Orders or any other target project.

Existing applications may be used as read-only comparison inputs only after Catalog-demo has a canonical slice and the comparison gate is explicitly scoped. Findings against target projects are diagnostics, not automatic remediation instructions.

## Rejected alternatives

| Alternative | Reason rejected |
|---|---|
| Treat existing CatalogItem seed as canonical immediately | it predates key standards and would normalize accidental behavior |
| Make every standard mandatory before any Catalog-demo code patch | too heavy; candidate slices are useful when clearly labeled |
| Require full security implementation before first canonical slice | security may be deferred when classification and intended permissions are explicit |
| Use target projects as the reference before Catalog-demo | would couple Springmaster to existing application compromises |
| Generate remediation patches for target projects from Catalog-demo readiness | target delivery needs a separate accepted strategy |

## Consequences

- Catalog-demo may now proceed through candidate implementation slices without pretending to be canonical.
- The first canonicalization claim must include explicit evidence and deferrals.
- G5 diagnostics have an accepted rule source.
- Target comparison remains blocked until Catalog-demo evidence exists and a read-only comparison scope is defined.
- Security remains important, but ADR-0005 owns the permission model and enforcement details.

## Follow-up work

- Create or update a concrete CatalogItem implementation plan before changing code.
- Mark existing pre-standard seed behavior as `legacy-demo-seed` where documentation or diagnostics need that distinction.
- Implement first report-only gate helpers only after the chosen scope is explicit.
- Draft ADR-0005 before strict security gates or production-style permission enforcement.



## Implementation planning note after 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` adds the concrete CatalogItem candidate-slice contract plan.

The plan is consistent with this ADR:

- it creates no canonicalization claim;
- it keeps the current implementation as `legacy-demo-seed`;
- it defines a future `candidate-reference-slice` implementation target;
- it requires evidence before G5 readiness changes;
- it keeps target-project comparison blocked.

A later code patch may implement the candidate contract, but only a separate evidence-backed patch may declare `canonical-reference-slice` status.

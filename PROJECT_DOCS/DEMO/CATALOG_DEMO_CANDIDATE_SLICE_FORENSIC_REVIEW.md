# Catalog-demo Candidate Slice Forensic Review

## Purpose

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` reviews the `CatalogItem` candidate foundation introduced by `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation`.

The review compares the implemented slice against:

- `ADR-0002` API Boundary and Endpoint Contract;
- `ADR-0003` Application Layer and Transaction Boundary;
- `ADR-0004` Persistence Identity and DomainEntity Strategy;
- `ADR-0005` Security and Permission Boundary;
- `ADR-0006` Verification and Gate Strategy;
- `ADR-0007` Catalog-demo Canonicalization Strategy;
- `PROJECT_DOCS/DEMO/CATALOG_DEMO_CANDIDATE_SLICE_CONTRACT_PLAN.md`;
- the report-only findings baseline from `000070`.

This review is documentation-only. It does not promote Catalog-demo to canonical status, does not enable strict gates, does not scan target projects and does not change Java, Maven or gate-tooling code.

## Executive verdict

The `CatalogItem` implementation after `000072` is a valid `candidate-reference-slice` foundation, but it is not yet a `canonical-reference-slice`.

The implementation substantially satisfies the `000071` candidate contract:

- the public list endpoint is paged and uses `sortBy`;
- detail uses opaque `id`;
- business-key lookup is explicit as `/by-sku/{sku}`;
- create returns `201 Created` with `Location` based on `id`;
- full update uses `PUT /{id}`;
- single delete is bodyless and returns `204 No Content`;
- response and request DTO roles are explicit;
- standard error-body evidence exists;
- tests and report-only gate validation are present.

The slice remains candidate-only because several canonical blockers are intentionally unresolved: durable persistence, implemented management security, OpenAPI evidence, strict gate promotion, complete DTO-boundary cleanup and final Catalog-demo canonical readiness review.

## Baseline comparison

| Concern | Before `000072` | After `000072` | Review result |
|---|---|---|---|
| Catalog-demo state | `legacy-demo-seed` | `candidate-reference-slice` foundation evidence exists | improved |
| Gate findings | `12` | `9` | improved |
| G1 query evidence | missing/legacy | `page`, `size`, `sortBy`, `sortDir` implemented | satisfied for candidate |
| Detail identity | historical SKU detail | opaque `id` detail plus `/by-sku/{sku}` | satisfied for candidate |
| Create status | incomplete candidate evidence | `201 Created` with `Location` by `id` | satisfied |
| Full update | absent | `PUT /api/demo/catalog/items/{id}` | satisfied |
| Single delete | absent | bodyless `DELETE /api/demo/catalog/items/{id}` | satisfied |
| Error body | legacy/ad-hoc risk | `CatalogApiErrorResponse` with `errorId` | satisfied for candidate |
| Security | not implemented | `documented-deferred-security` evidence | expected deferral |
| Persistence | in-memory | still in-memory | canonical blocker |
| Target projects | excluded | still excluded | correct |

## Report-only gate result after 000072

A deterministic report-only gate run after `000072` produced `9` findings:

| Severity | Count | Interpretation |
|---|---:|---|
| `BLOCKER` | 0 | no blocking gate failure |
| `ERROR` | 0 | no report-only error finding |
| `WARNING` | 1 | expected security deferral |
| `INFO` | 7 | rule-source and positive status evidence |
| `MANUAL_REVIEW` | 1 | Catalog-demo is not canonical |

Gate distribution:

| Gate | Count | Interpretation |
|---|---:|---|
| `SM-G0-RULE-SOURCE-COVERAGE` | 6 | positive ADR rule-source evidence |
| `SM-G1-STATUS-ERROR-CONTRACT` | 1 | create status evidence detected |
| `SM-G4-SECURITY-CLASSIFICATION` | 1 | documented security deferral remains |
| `SM-G5-CATALOG-READINESS-EVIDENCE` | 1 | manual canonicalization review remains |

The reduction from `12` to `9` confirms that the candidate slice closed the earlier query and vocabulary findings. Remaining findings are expected and must not be promoted to strict in the current state.

## ADR-0002 API and DTO-boundary review

### Satisfied candidate evidence

The endpoint contract is consistent with `ADR-0002` for the first candidate foundation:

- `GET /api/demo/catalog/items` returns `PagedResponseDTO<CatalogItemListItemDTO>`;
- query parameters are `page`, `size`, `sortBy` and `sortDir`;
- unsupported `sortBy` values return `400`;
- `GET /api/demo/catalog/items/{id}` uses opaque public identity;
- `GET /api/demo/catalog/items/by-sku/{sku}` is an explicit business-key lookup;
- `POST /api/demo/catalog/items` returns `201 Created`;
- `PUT /api/demo/catalog/items/{id}` returns `200 OK` with the updated DTO;
- `DELETE /api/demo/catalog/items/{id}` is bodyless and returns `204 No Content`;
- ambiguous `/all`, `/list`, public `findOne`/`findFirst`/`findLast`, body-bearing single `DELETE`, `/reference-data`, delete-multiple, search and relationship endpoints are not introduced. Complete-result-set `/all` is accepted only by later candidate evidence from `000092` and `000094`.

### Open issue: request DTO uses persistence-facing `Range`

`CatalogItemCreateDTO` and `CatalogItemUpdateDTO` currently expose `de.cocondo.system.entity.Range` directly. `Range` is an embeddable persistence type. This is acceptable as a transitional candidate foundation only if it remains explicitly tracked.

Before canonical promotion, the public DTO boundary should be cleaned up by introducing a request/response value DTO such as `CatalogItemAvailabilityDTO` or a generic non-persistence API value type. Public request bodies should not depend on JPA-annotated persistence structures.

Classification: `P0 before canonical`, `P1 before deeper DTO-boundary gates`.

## ADR-0003 Application-layer and transaction review

### Satisfied candidate evidence

The controller remains a thin HTTP adapter:

- it injects `CatalogItemService`, not repositories or `EntityManager`;
- it has no transaction demarcation;
- it delegates paging, sorting, create, update, delete and lookup behavior to the service;
- error mapping is kept at the API boundary for the demo slice.

The mapper remains deterministic and has no repository, service, security or transaction dependency.

### Open issue: direct service update validation is asymmetric

Create operations are guarded by both Bean Validation at the HTTP boundary and `CatalogItemValidator` in the service. Update operations are Bean-validated at the controller boundary, but direct service calls can still pass an invalid `CatalogItemUpdateDTO` because the internal validator currently targets only `CatalogItemCreateDTO`.

For the current HTTP candidate slice this is acceptable because controller tests cover invalid update payloads. Before canonical promotion or stricter application-boundary gates, update validation should be enforced at the application-service boundary as well.

Classification: `P0 before canonical`, `P1 before strict G3/G1 behavior gates`.

### Open issue: legacy unpaged service helper remains

`CatalogItemService.list()` still returns an unpaged list. It is not exposed as a public HTTP endpoint, so it does not violate the public API contract. It can nevertheless confuse future source-based diagnostics and should be removed, made test-only, or documented as legacy helper before canonical promotion.

Classification: `P1 cleanup before canonical`.

## ADR-0004 Persistence identity review

### Satisfied candidate evidence

The public resource identity is `String id`, and create `Location` uses the opaque `id`. The business key `sku` remains explicit and receives a separate `/by-sku/{sku}` lookup path.

The candidate uses `persistenceVersion` in response DTO evidence and avoids numeric public ID leakage.

### Deferred canonical evidence

The implementation remains in-memory. It demonstrates boundary semantics, not durable persistence.

Canonical readiness still requires:

- repository or persistence evidence;
- Liquibase or migration evidence where applicable;
- clearer persistence transaction behavior;
- durable uniqueness evidence for `sku`.

Classification: expected canonical blocker.

## ADR-0005 Security review

The candidate foundation correctly records `documented-deferred-security` with intended permissions:

- `catalog:item:read`;
- `catalog:item:create`;
- `catalog:item:update`;
- `catalog:item:delete`.

No implemented Spring Security enforcement exists yet. The remaining G4 warning is therefore correct and expected.

Canonical readiness requires `implemented-management-security` evidence, fixtures and 401/403 behavior tests.

Classification: expected canonical blocker.

## ADR-0006 Gate strategy review

The report-only gate behavior is consistent:

- findings remain non-blocking;
- tool execution is validated;
- gate regression and smoke checks pass;
- `mvn test` and `mvn -Pspringmaster-gates-report test` pass in the applied environment;
- no target project is scanned.

### Open issue: G5 readiness heuristic lags behind candidate evidence

The G5 report still classifies the readiness subject as `legacy-demo-seed`, because the current source-based rule checks for that marker in the readiness plan before recognizing candidate evidence. This is a tooling heuristic limitation, not a CatalogItem implementation failure.

The next gate-tooling alignment should recognize `CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md` and report the state as `candidate-reference-slice` with remaining canonical blockers instead of pure legacy state.

Classification: `P0 for gate evidence quality`, not a strict blocker.

## ADR-0007 Catalog-demo canonicalization review

The slice satisfies the first transition from `legacy-demo-seed` toward `candidate-reference-slice`, but does not satisfy canonicalization.

The following canonical evidence is still missing:

- durable persistence evidence;
- implemented management security;
- OpenAPI operationId, tag, schema and error schema evidence;
- strict gate promotion decision;
- final canonical readiness review;
- target comparison scope and safeguards.

The correct state after this review is:

```text
CatalogItem = candidate-reference-slice foundation
Catalog-demo = not canonical
Target comparison = blocked
Target delivery = blocked
Strict gates = blocked
```

## Findings classification

| ID | Severity | Area | Finding | Next handling |
|---|---|---|---|---|
| `F-073-001` | P0 before canonical | DTO boundary | Request DTOs expose JPA embeddable `Range` | introduce API value DTO |
| `F-073-002` | P0 before canonical | Application validation | Service update path lacks internal validation symmetry | add update validator/service guard |
| `F-073-003` | P1 | Service API | unpaged `CatalogItemService.list()` remains | remove or mark legacy helper |
| `F-073-004` | P0 for gate quality | Gate G5 | G5 still reports legacy despite candidate evidence | align gate rule to evidence file |
| `F-073-005` | expected blocker | Security | security is documented-deferred only | implement management security later |
| `F-073-006` | expected blocker | Persistence | in-memory persistence only | add persistence evidence later |
| `F-073-007` | expected blocker | OpenAPI | no OpenAPI evidence yet | add OpenAPI snapshot/gate later |
| `F-073-008` | expected blocker | Canonicalization | no canonical readiness decision | perform later canonical review |

## Decision

The `CatalogItem` candidate foundation is accepted as a valid candidate baseline for the next iteration.

It is not promoted to canonical. No strict gate is introduced. Target comparison and target delivery remain blocked.

## Recommended next patch

The next patch should be a small code/demo and gate-alignment patch:

```text
000074_springmaster_catalog_demo_candidate_slice_alignment
```

Recommended scope:

1. replace public `Range` exposure in CatalogItem request DTOs with API-facing availability DTO evidence;
2. add service-level update validation symmetry;
3. remove or isolate the legacy unpaged `CatalogItemService.list()` helper if no longer needed;
4. align G5 report-only detection with `CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md`;
5. keep security, durable persistence, OpenAPI and canonical promotion deferred;
6. run Maven tests, gate regression, gate smoke and Full-ZIP export.



## Alignment note after 000074

Patch `000074_springmaster_catalog_demo_candidate_slice_alignment` closes the forensic issue `F-073-004` for the current candidate state.

G5 now recognizes `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json` as machine-readable candidate evidence. The report-only findings baseline is expected to decrease from `9` to `8`:

- G0 rule-source evidence: `6` informational findings;
- G1 status/error evidence: `1` informational finding;
- G4 security classification: `1` warning for `documented-deferred-security`;
- G5 manual review: `0` while candidate evidence remains present and classifiable.

This does not change the canonicalization decision. Catalog-demo remains not canonical.

## Cleanup follow-up after 000075

Patch `000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup` resolves the candidate-slice cleanup findings for public DTO boundary, update validation symmetry and unpaged service helper quarantine/removal.

Resolved items:

| Finding | Status after 000075 | Evidence |
|---|---|---|
| `F-073-001` DTO boundary leaks persistence `Range` | resolved for request DTOs | `CatalogItemAvailabilityDTO` replaces public `Range` exposure |
| `F-073-002` update validation asymmetry | resolved | `CatalogItemValidator.validate(CatalogItemUpdateDTO)` is invoked by service update |
| `F-073-003` unpaged service helper | resolved | `CatalogItemService.list()` removed |

Open canonical blockers remain durable persistence, implemented management security, OpenAPI evidence, canonical readiness review, strict-gate decision and target delivery.

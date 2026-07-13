# Query Operations Contract Closure Review

## Purpose

Patch `000103_springmaster_query_operations_contract_closure_review` records the closure state after patches `000098` through `000102`.

The review answers the former open question whether Springmaster query-controller functions are sufficiently protected by contracts and interfaces. The result is: **yes, for the current candidate-reference-slice maturity level**.

The query functions are now backed by four layers:

1. API standards for endpoint vocabulary and response shapes.
2. Core DTO and query-operation interfaces.
3. CatalogItem executable reference behavior.
4. Targeted and full Maven regression tests.

## Closed scope

The following topics are considered closed for the current Springmaster reference level:

| Topic | Closure evidence |
|---|---|
| Paged list contract | `GET /api/demo/catalog/items`, `PagedResponseDTO`, filter/sort/paging tests |
| Complete result set | `GET /api/demo/catalog/items/all`, shared filter/sort pipeline, empty-result evidence |
| Count-only contract | `GET /api/demo/catalog/items/count`, `CountResponseDTO`, filtered and zero-result tests |
| Count response shape | Core `CountResponseDTO` with required non-negative `totalElements` |
| Query Java contract | Core `PagedResultSetQuery`, `CompleteResultSetQuery`, `CountResultSetQuery`, `ResultSetQueryOperations` |
| Demo service adoption | `CatalogItemService` implements `ResultSetQueryOperations` with Demo-owned query records |
| Controller boundary | `CatalogItemController` remains explicit Spring MVC adapter; no generic controller interface |
| Query DTO ownership | `CatalogItemPagedQuery`, `CatalogItemAllQuery`, `CatalogItemCountQuery` stay in Demo slice |

## Canonical architectural decision

Springmaster does **not** standardize generic Spring-MVC controller inheritance for query endpoints.

The canonical pattern is:

```text
Controller = explicit HTTP/Spring MVC adapter
Service    = typed query-operations contract
Query DTOs = fachliche slice-owned request model
Core       = fachfreie DTOs, query interfaces and list helpers
```

This avoids leaking HTTP paths, security annotations, OpenAPI operation IDs or fachliche filter fields into Core. It also keeps generated and manually implemented application slices flexible while still giving them a typed Java contract.

## Runtime reference

The current reference implementation is the CatalogItem candidate slice:

```text
GET /api/demo/catalog/items
GET /api/demo/catalog/items/all
GET /api/demo/catalog/items/count
```

The service contract is:

```java
ResultSetQueryOperations<
        CatalogItemPagedQuery,
        CatalogItemAllQuery,
        CatalogItemCountQuery,
        CatalogItemListItemDTO>
```

The query records intentionally differ by operation:

| Query record | Allowed public semantics |
|---|---|
| `CatalogItemPagedQuery` | page, size, sortBy, sortDir, sku, name |
| `CatalogItemAllQuery` | sortBy, sortDir, sku, name |
| `CatalogItemCountQuery` | sku, name |

Count-only endpoints must not expose public paging or sorting semantics. `/all` must not expose public paging semantics.

## Verification state

The closure is supported by the last implementation patches:

```text
000098_springmaster_count_response_contract_candidate
000099_springmaster_count_response_dto_core_candidate
000100_springmaster_catalogitem_count_reference_slice
000101_springmaster_query_operations_interface_contract_core
000102_springmaster_catalogitem_query_operations_interface_adoption
```

Patch `000102` was verified with:

```text
git diff --check
mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest
mvn -B -ntp test
./bin/export.sh full --zip
```

The final observed test state after `000102` was:

```text
CatalogItem targeted tests: 33 tests, 0 failures
Full Maven test: 111 tests, 0 failures
```

## Remaining non-closure topics

The closure does not make CatalogItem canonical. The following topics remain deliberately open:

| Topic | Reason |
|---|---|
| Durable persistence/JPA implementation | CatalogItem still uses the in-memory candidate service; JPA count efficiency guidance is documented separately since `000105` |
| Liquibase evidence | no durable CatalogItem table/migration proof yet |
| Implemented management security | security classification exists, enforcement is deferred |
| OpenAPI operation/schema evidence | strict OpenAPI contract evidence is not complete yet |
| Report-only/strict gate implementation | gate concepts exist, but strict promotion remains later work |
| Cursor/keyset pagination | not required for the first candidate slice |
| Async export/job contract | only needed when synchronous `/all` is operationally unsuitable |
| Target-project comparison/delivery | blocked until Catalog-demo has stronger canonical evidence |

## Gate implication

Report-only gates may now treat the query-operations pattern as reference-demonstrated for CatalogItem:

- paged list query evidence exists;
- complete-result-set `/all` evidence exists;
- count-only evidence exists;
- typed query-operation interface adoption exists;
- ambiguous `/all`, public `findOne`/`findFirst`/`findLast`, ad-hoc count names and count endpoints with paging/sorting controls remain findings.

Strict gates are still deferred until the gate implementation itself is stable and explicitly promoted under ADR-0006.

## Outcome

The Query Operations contract is closed at **reference-demonstrated candidate level**.

Future generated applications should use this pattern as the implementation target, but target-project enforcement must remain read-only until the later gate and canonicalization milestones are reached.



## Follow-up after 000105

Patch `000105_springmaster_jpa_count_query_efficiency_reference` closes the documentation gap for efficient persistent count-query implementation. It does not change the candidate runtime status of CatalogItem, because CatalogItem is still an in-memory reference slice.

The closed candidate-level contract therefore consists of:

- endpoint and response semantics;
- Core DTO and query-operation interfaces;
- CatalogItem HTTP and service-contract behavior;
- persistent count-query efficiency guidance for later JPA-backed slices and generated applications.

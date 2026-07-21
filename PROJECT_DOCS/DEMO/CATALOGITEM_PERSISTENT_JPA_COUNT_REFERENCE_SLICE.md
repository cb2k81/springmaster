# CatalogItem persistent JPA query slice

## Historical origin

Patch `000113_springmaster_persistent_jpa_count_reference_slice` introduced
`CatalogItemJpaQueryReference` as a non-runtime reference for the dedicated JPA
count-query pattern. At that time the CatalogItem runtime intentionally remained
in-memory.

## Current status since 000159

Patch `000163_springmaster_catalogitem_persistent_candidate_runtime` replaces the
reference-only class with the registered runtime component:

```text
src/main/java/de/cocondo/platform/demo/catalog/CatalogItemJpaQueryRepository.java
```

`CatalogItemService` now delegates paged list, `/all` and `/count` to this JPA
query repository. The persistent Candidate uses Liquibase-managed tables and the
same predicate family for all three operations.

The runtime contract is:

- paged list executes a data query plus a separate count query for
  `totalElements`;
- `/all` uses the same filters and stable sorting without paging;
- `/count` uses a dedicated `CriteriaQuery<Long>` with `cb.count(root)`;
- count applies no sorting, paging, DTO mapping or entity-list materialization;
- public sorting is allowlisted and receives `id` as deterministic tie-breaker;
- `page`, `size`, `sortBy` and `sortDir` are validated before JPA constructs a
  pageable or criteria query.

The implementation is covered by:

```text
src/test/java/de/cocondo/platform/demo/catalog/CatalogItemJpaQueryRepositoryTest.java
src/test/java/de/cocondo/platform/demo/catalog/CatalogItemPersistenceContractTest.java
src/test/java/de/cocondo/platform/demo/catalog/api/CatalogItemControllerTest.java
```

## Canonicalization boundary

The slice remains `candidate-reference-slice`. Durable H2-backed runtime evidence
is present, but Canonicalization still requires the separately planned
MariaDB/constraint and optimistic-lock qualification, implemented management
security and the explicit ADR-0007 promotion decision. The historical
reference-only state must no longer be reported as the current runtime.

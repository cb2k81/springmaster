---
documentType: concept
status: active
scope: catalog-demo
owner: springmaster-maintainers
validFrom: 2026-07-21
supersedes: none
---
# CatalogItem Persistent Candidate Slice

## State

`CatalogItem` remains a `candidate-reference-slice`. Patch
`000163_springmaster_catalogitem_persistent_candidate_runtime` replaces the in-memory runtime with a transactional JPA implementation, but does not promote the slice to canonical status.

Implemented runtime evidence:

- `CatalogItemRepository` provides Spring Data CRUD and case-insensitive SKU lookup;
- `CatalogItemJpaQueryRepository` implements paged, complete-result-set and count queries through shared Criteria predicates;
- `CatalogItemService` owns read and write transaction boundaries and maps persistence results to DTOs;
- `CatalogItemQuerySupport` validates paging and allow-listed sorting before repository/JPA invocation;
- Liquibase creates the CatalogItem and tag tables;
- Hibernate validates the Liquibase-owned schema in test, dev, build and production profiles;
- every Spring test ApplicationContext receives its own H2 database in MariaDB compatibility mode, with Liquibase enabled;
- `TestDatabaseIsolationContractTest` proves that two simultaneously open test contexts resolve different configured datasource URLs, retain MariaDB compatibility settings, expose different runtime database identities, and both complete Liquibase initialization.

## Identity and optimistic-locking lifecycle

The atomic Core/runtime transition is implemented:

```text
transient CatalogItem       persistenceVersion = null
first successful insert     persistenceVersion = 0
first successful update     persistenceVersion = 1
later successful updates    monotonically increasing
```

The entity keeps an assigned opaque UUID before persistence. Spring Data `Persistable` is not introduced.

## Request-boundary protection

Invalid `page`, `size`, `sortBy` and `sortDir` values are rejected before the JPA adapter is called. The boundary also rejects page/size combinations whose integer result offset would overflow. These failures retain the standard `400 INVALID_REQUEST` response rather than being translated into persistence-layer `500` responses.

## Tests

The patch adds or updates evidence for:

- transient-null, insert-zero, reload-zero, update-one and reload-one version lifecycle;
- persisted tags and detail reload across service transactions;
- persistent create, update, delete, alternate-key lookup, paged list, `/all` and `/count` behavior;
- invalid paging and sorting, including offset overflow;
- Liquibase/JPA context initialization, schema validation and per-ApplicationContext database isolation;
- query/count predicate parity and dedicated count-query structure;
- OpenAPI and global API-error contracts.

## Remaining deferrals

The patch intentionally does not close:

- management-security enforcement;
- stale-version to `409 Conflict` mapping and concurrent-update qualification;
- MariaDB/Testcontainers qualification and DB-collation race behavior for case-insensitive SKU uniqueness;
- canonicalization or strict-gate promotion;
- Maven Core artifact distribution;
- generated-slice rendering or target delivery.

These are existing planned follow-up requirements, not hidden claims of completion.

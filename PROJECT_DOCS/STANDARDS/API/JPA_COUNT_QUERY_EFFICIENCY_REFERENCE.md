# JPA Count Query Efficiency Reference

## Status

Reference API implementation guidance since patch `000105_springmaster_jpa_count_query_efficiency_reference`.

This document complements the Count-only contract in `PROJECT_DOCS/STANDARDS/API/API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md`. It does not introduce a new HTTP endpoint shape. It defines how persistent Spring/JPA implementations should compute the `totalElements` value efficiently and consistently.

## Problem statement

Count-only endpoints and paged list metadata are only useful when the implementation counts the matching result set without materializing it. The following anti-patterns are not acceptable for persistent management APIs:

```java
listAll(query).size();
repository.findAll(specification).size();
repository.findAll(specification).stream().filter(...).count();
repository.findAll(specification).stream().map(mapper::toDto).count();
```

These patterns load entity rows, apply unnecessary sorting or projection work, and may leak performance or authorization defects into count-only calls.

## Canonical implementation rule

A persistent query slice must separate three operations even when they share the same predicate family:

| Operation | Persistent implementation expectation |
|---|---|
| paged list | filtered data query with paging and allowed sorting |
| `/all` | filtered data query with allowed sorting and without paging |
| `/count` | filtered count query without paging, sorting, DTO mapping or export serialization |

The count operation must execute as a repository/query-level count where persistence is involved.

## Predicate reuse

The same business, security and data-scope predicates must be assembled through a shared predicate builder or equivalent shared query construction path.

Recommended slice structure:

```text
<Domain>QueryPredicates
  -> business filters
  -> security predicate
  -> data-scope predicate

<Domain>QueryRepository
  -> findPage(query)
  -> findAllForExport(query)
  -> count(query)
```

The shared predicate builder must not include presentation-only concerns such as sorting, paging, DTO projection or export serialization.

## JPA Criteria reference pattern

For custom JPA Criteria implementations, the count query should use a dedicated `CriteriaQuery<Long>`:

```java
CriteriaBuilder cb = entityManager.getCriteriaBuilder();
CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);
Root<CatalogItem> root = countQuery.from(CatalogItem.class);
Predicate predicate = predicates.toPredicate(root, cb, query);

countQuery.select(cb.count(root));
countQuery.where(predicate);

long totalElements = entityManager.createQuery(countQuery).getSingleResult();
```

Rules:

- do not call `orderBy` on count queries;
- do not apply `setFirstResult` or `setMaxResults` to count queries;
- do not fetch associations solely for count;
- do not map entities to DTOs for count;
- use `countDistinct` when joins can multiply the root rows;
- keep authorization and data-scope predicates in the count predicate;
- document any deliberate approximation or eventual-consistency behavior.

## Spring Data Specification reference pattern

For Spring Data JPA projects, a `Specification<T>`-based implementation is acceptable when the specification represents only the predicate family:

```java
Specification<CatalogItem> spec = CatalogItemSpecifications.from(query, securityScope);
long totalElements = repository.count(spec);
```

The specification used for count must not add fetch joins or sort/order expressions that are required only for data retrieval. If a data query needs fetch joins, the slice should split predicate specification from fetch-plan specification.

## Security and data-scope equivalence

Count results must not reveal hidden data. The count predicate must therefore include the same visibility rules as the corresponding data query:

- tenant or organizational scope;
- ownership or assignment scope;
- lifecycle visibility such as deleted/archived flags;
- permission-derived restrictions;
- stage/environment constraints when applicable.

A stronger permission for count is allowed only when documented explicitly. A weaker count predicate is not allowed.

## Relationship to CatalogItem

The current CatalogItem candidate slice is JPA-backed. `CatalogItemJpaQueryRepository.countRows(...)` is the executable reference: it uses a dedicated `CriteriaQuery<Long>`, shares filter predicates with data queries, and avoids row or DTO materialization.

This reference document therefore applies both to the current candidate runtime and to later generated backend applications.

## Gate candidates

Future report-only gates may flag the following patterns:

- count endpoint implementation calls `/all` or `listAll` and then `.size()`;
- repository `findAll(...).size()` or stream count usage in count methods;
- count methods invoking DTO mappers or export serializers;
- count queries applying page/size/sort semantics;
- count query code that omits documented security/data-scope predicate builders;
- public count endpoints using non-standard names such as `/total` or incompatible response fields.

Strict enforcement remains deferred until the query-contract gate implementation is itself stable and explicitly promoted.


## Report-only gate linkage since 000106

`QUERY_CONTRACT_GATE_REPORT.md` defines the initial finding IDs for count-efficiency diagnostics. The first implementation should report obvious anti-patterns such as `listAll(...).size()` or `repository.findAll(...).size()` as report-only findings before they are promoted to strict build failures.

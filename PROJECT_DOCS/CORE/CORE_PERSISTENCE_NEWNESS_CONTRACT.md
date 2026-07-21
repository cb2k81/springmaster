---
documentType: concept
status: active
scope: core-persistence
owner: springmaster-maintainers
validFrom: 2026-07-21
supersedes: none
---
# Core Persistence Newness Contract

## Decision state

The assigned-ID and optimistic-locking newness contract is implemented together with the persistent CatalogItem candidate runtime. `contracts/core/persistence-newness-contract.json` is the machine-readable source of truth.

Current runtime state:

```text
CatalogItem runtime          transactional JPA candidate
DomainEntity transient ID    assigned opaque UUID
new object before persist    persistenceVersion = null
first successful insert      persistenceVersion = 0
first successful update      persistenceVersion = 1
subsequent updates           monotonically increasing
contract status              implemented
```

The transition is atomic: nullable Core newness, repository/JPA adapter, Liquibase schema and lifecycle tests are delivered together. The application does not implement Spring Data `Persistable`; persistence newness is derived from the nullable `@Version` field while IDs remain assigned before insert.

## Distribution direction

The long-term Core distribution form remains a versioned internal Maven artifact, optionally accompanied by a BOM. Source-copy remains a controlled-pilot path until a dedicated extraction and N-1-consumption capability is fully qualified.

## Boundaries and remaining work

Implemented here:

- nullable transient `persistenceVersion`;
- insert version `0` and first-update version `1` evidence;
- persistent CatalogItem CRUD and query runtime;
- Liquibase-owned schema and Hibernate validation;
- invalid paging and sorting rejected before JPA.

Still deferred:

- stale-version conflict mapping and concurrent-update qualification;
- production-like MariaDB integration tests;
- Core Maven module extraction and publication;
- any generic Core repository base abstraction.

## Rejected shortcuts

- no partial nullable-version transition;
- no Spring Data `Persistable` coupling in the fachfrei Core without a separate ADR;
- no API change to version `1` merely to preserve merge behavior;
- no optimistic-locking exception hidden behind a generic success or retry;
- no physical Maven module split inside this runtime patch.

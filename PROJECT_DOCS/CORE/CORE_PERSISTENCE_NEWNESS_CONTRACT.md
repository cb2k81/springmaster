---
documentType: concept
status: active
scope: core-persistence
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Core Persistence Newness Contract

## Decision state

The target contract is accepted, but the runtime transition is intentionally staged. `contracts/core/persistence-newness-contract.json` is the machine-readable source of truth.

Current accepted compatibility state:

```text
CatalogItem runtime          in-memory
DomainEntity transient ID    assigned opaque UUID
DomainEntity version         eagerly initialized to 0L
contract status              decided
```

Target atomic state:

```text
new object before persist    null
first successful insert      0
first successful update      1
subsequent updates           monotonically increasing
```

The target state may only be introduced together with the persistent CatalogItem repository port/JPA adapter, Liquibase schema and insert/reload/update evidence. A standalone Core field change that leaves the in-memory slice on the old API expectations is forbidden.

## Distribution direction

The long-term Core distribution form is a versioned internal Maven artifact, optionally accompanied by a BOM. Source-copy remains a controlled-pilot path until a dedicated extraction and N-1-consumption capability is fully qualified.

## Rejected shortcuts

- no partial nullable-version transition;
- no Spring Data `Persistable` coupling in the fachfrei Core without a separate ADR;
- no API change to version `1` merely to preserve merge behavior;
- no physical Maven module split inside this recovery.

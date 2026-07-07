# Changelog 000064 - springmaster_adr_0004_persistence_identity_domainentity_strategy

## Zweck

Akzeptiert ADR-0004 für Persistence Identity und DomainEntity Strategy, damit die Persistenzgrundlagen vor Catalog-demo-Kanonisierung und späteren Persistence-Gates nicht nur dokumentiert, sondern als Architekturentscheidung verankert sind.

## Änderungen

Neu:

- `PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md`

Geändert:

- `PROJECT_DOCS/ADR/README.md`
- `PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md`
- `PROJECT_DOCS/ADR/ADR_GOVERNANCE_AND_BACKLOG_ALIGNMENT.md`
- `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md`
- `PROJECT_DOCS/STANDARDS/README.md`
- `PROJECT_DOCS/STANDARDS/STANDARD_CONSISTENCY_AND_ADR_GAP_REVIEW.md`
- `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md`
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`
- `platform/versions/platform.env`

## Ergebnis

- `DomainEntity` bleibt der mapped-superclass default für Standard-Aggregate-Roots.
- Public API IDs bleiben opaque string identifiers.
- Business Keys bleiben explizite Domain-Felder.
- Interne Surrogate IDs sind nur mit expliziten Kriterien zulässig.
- `persistenceVersion`, Audit-Felder und Repository-Boundary sind ADR-backed.
- Report-only Persistence Identity Diagnostics dürfen ADR-0004 als Rule Source verwenden.
- Strict Persistence Gates bleiben abhängig von Implementierungsevidenz, Catalog-demo-Beweis und expliziter Strict-Promotion nach ADR-0006.

## Tests

Kein Maven-Test erforderlich. Der Patch ist documentation-only und ändert keine Java-, Maven-, Tooling-, Template-, Demo-Code- oder Zielprojektdateien.

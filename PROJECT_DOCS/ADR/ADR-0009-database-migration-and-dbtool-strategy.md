---
documentType: adr
status: accepted
scope: database-migration-and-dbtool
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# ADR-0009: Database Migration and DBTool Strategy

## Context

Springmaster included Liquibase and a fail-closed DBTool, but the master changelog was empty and no executable contract governed include order, changeSet identity, destructive changes or generated-project structure.

## Decision

1. Liquibase is the only supported schema-migration mechanism for Springmaster-managed Java backends.
2. `contracts/database/migration-contract.json` is the machine-readable migration contract.
3. `src/main/resources/db/changelog/db.changelog-master.xml` contains explicit includes. Included files live below `db/changelog/changes/` and use monotonically ordered names `db.changelog-NNNN-<name>.xml`.
4. Every changeSet has a repository-unique `id` and an explicit `author`. `runAlways` and `runOnChange` are not accepted for normal schema migrations.
5. Destructive operations require an explicit rollback block and a separately reviewed delivery plan. DBTool destructive database recreation remains disabled unless `APP_DBTOOL_ALLOW_DESTRUCTIVE=true` is set deliberately.
6. Application-start Liquibase execution is disabled by default. A project may enable it explicitly with `APP_LIQUIBASE_ENABLED=true` after its datasource and operational ownership are defined.
7. DBTool `status` performs only static configuration and migration-contract checks. Commands that contact a database remain explicit.
8. Stage validation precedes stage update. Production migration execution is outside this bootstrap DBTool and requires an authorized deployment workflow.
9. Project-New delivers the same master/include structure, contract validator and non-destructive defaults.

## Consequences

- Changelog drift and duplicate changeSet identity fail before a database connection is opened.
- The foundation baseline contains a tag-only changeSet; it does not claim a domain schema.
- This ADR does not authorize automatic production migrations or destructive target-project updates.

## Verification

```bash
cd /opt/cocondo/springmaster || exit 1
./bin/db-migration-contract.sh --check
./bin/db-migration-contract-it.sh
./bin/dbtool.sh status
```

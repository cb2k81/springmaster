# CHANGELOG 000040 - springmaster_core_id_generator_implementation

## Scope

`core`

## Summary

Adds the UUID-based default implementation of the shared `IdGeneratorService` contract to the Springmaster Core.

## Changes

- Add `UuidIdGeneratorService` under `de.cocondo.system.core.id`.
- Add unit tests for UUID format, uniqueness, service-contract implementation and Spring service annotation.
- Add Core documentation for the ID generator implementation slice.
- Update IDM System Core Gap Inventory markdown and JSON to mark `core-id-implementation` as implemented.
- Bump `PLATFORM_VERSION` to `0.13.1-foundation` and `PLATFORM_CORE_VERSION` to `0.3.1`.

## Explicitly Not Included

- No IDM target-project changes.
- No IDM import migration.
- No removal of `de.cocondo.app.system/**`.
- No repository, persistence, Liquibase, Security/JWT, HTTP/Web or event changes.

## Required Validation

```bash
mvn test
python3 -m json.tool PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.json >/dev/null
./bin/export.sh full --zip
```

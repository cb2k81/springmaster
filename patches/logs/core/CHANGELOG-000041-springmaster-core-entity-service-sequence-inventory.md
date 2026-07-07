# CHANGELOG 000041 - springmaster_core_entity_service_sequence_inventory

## Scope

`core`

## Summary

Adds a documentation-only inventory for the persistence/lifecycle-near IDM legacy slice `core-entity-service-and-sequence` before any further Core code is migrated.

## Changes

- Add `PROJECT_DOCS/CORE/CORE_ENTITY_SERVICE_SEQUENCE_INVENTORY.md`.
- Update `IDM_SYSTEM_CORE_GAP_INVENTORY.md` and `.json` with the split decision for entity service, metadata persistence and number sequence areas.
- Update Core README with the new analysis step and the next safe code slice.
- Update Version Policy and `platform.env` to `PLATFORM_VERSION=0.13.2-foundation` while leaving `PLATFORM_CORE_VERSION=0.3.1` unchanged.

## Explicitly Not Included

- No Java code changes.
- No Maven dependency changes.
- No IDM target-project changes.
- No IDM import migration.
- No deletion of `de.cocondo.app.system/**`.
- No KeyValuePair/NumberSequence/Repository/Liquibase changes.

## Required Validation

```bash
python3 -m json.tool PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.json >/dev/null
./bin/export.sh full --zip
```

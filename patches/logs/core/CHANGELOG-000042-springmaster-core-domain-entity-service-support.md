# Changelog 000042 - Springmaster Core Domain Entity Service Support

## Scope

`core`

## Summary

Adds the low-risk DomainEntity service support slice to Springmaster Core without changing persistence mappings, repositories, schema, or target projects.

## Added

- `de.cocondo.system.entity.service.DomainEntityService`
- `de.cocondo.system.entity.service.TagService`
- Unit tests for entity creation and tag operations
- Core documentation for the service-support slice

## Updated

- Core README
- IDM System Core Gap Inventory markdown and JSON
- Entity/Service/Sequence inventory follow-up status
- Springmaster version policy
- Platform version metadata

## Not included

- No IDM target-project change
- No IDM import migration
- No removal of `de.cocondo.app.system/**`
- No DomainEntity mapping change
- No KeyValuePair persistence
- No NumberSequence classes
- No repositories or Liquibase/schema changes

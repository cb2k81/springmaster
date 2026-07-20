# CHANGELOG 000144_springmaster_database_migration_contract

## Purpose

Accept ADR-0009 and add a deterministic Liquibase and DBTool migration contract.

## Changes

- Accept database migration and DBTool strategy ADR
- Add ordered Liquibase master and foundation baseline changeSet
- Add static migration contract and destructive rollback guard
- Make DBTool status validate the migration contract without a database connection
- Propagate migration contract tooling through Project-New

## Qualification

The patch acceptance profile runs a complete Maven test and no export or push.
Bundle-level checks additionally run the relevant contract integration fixtures and Project-New acceptance.

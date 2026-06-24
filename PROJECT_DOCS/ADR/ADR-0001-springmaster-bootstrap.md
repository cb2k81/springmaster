# ADR-0001: Bootstrap springmaster as Platform Source Project

## Status

Accepted

## Context

The target directory `/opt/cocondo/springmaster` initially contains only the project documents under `docs/`.
The IDM export is the technical baseline for future tooling and core migration.

## Decision

Create a small, verifiable Spring Boot project foundation first and avoid copying IDM domain code into the new project.

## Consequences

- Future work can use the local patch system.
- IDM tooling and Java core can be migrated in controlled follow-up patches.
- The first project state is intentionally minimal and does not represent the final platform feature set.

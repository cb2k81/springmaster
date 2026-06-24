# springmaster Bootstrap

## Scope

This document describes the first project state after applying the bootstrap archive.

The bootstrap establishes:

- Maven/Spring Boot project coordinates,
- package root `de.cocondo.platform`,
- minimal runnable application,
- patch tooling entry point,
- export tooling entry point,
- build and DBTool entry points,
- platform version and target registry folders.

## Explicitly not included

The bootstrap does not include:

- IDM domain code,
- migrated Java core classes,
- demo domains,
- full IDM-derived DBTool implementation,
- platform update patch generation.

Those parts must be added by later regular patches after this foundation has been verified.

---
documentType: adr
status: accepted
scope: core-distribution
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# ADR-0013 Core Distribution Strategy

## Context

Springmaster currently delivers Core source files into managed projects. That mechanism is useful for bootstrap and controlled pilots, but it couples target repositories to file-level copying and makes Core upgrades larger than the semantic change.

The current repository is still a single Maven module. A physical module split during the P3 recovery would mix build restructuring with persistence validation and would repeat the scope error that caused the course correction.

## Decision

The long-term canonical distribution form for `de.cocondo.system` is a versioned internal Maven artifact, optionally accompanied by a Springmaster BOM.

The transition rules are:

1. the current source-copy profile remains a documented controlled-pilot path;
2. no target is migrated automatically;
3. the single-module repository remains unchanged during the persistence recovery;
4. a future dedicated module-extraction initiative must prove package closure, dependency boundaries, reproducible publication and N-1 consumption before source-copy can be deprecated;
5. generated business code and project-local tooling continue to be delivered through target-local patch artifacts.

## Consequences

Core semantics must not depend on Springmaster demo packages, target-specific classes or the patch tooling. New Core behavior requires Core tests that remain valid when the package is extracted into an independent artifact.

This ADR does not publish an artifact, create a repository, split the Maven build or modify managed targets. Those are separate capabilities with their own acceptance gates.

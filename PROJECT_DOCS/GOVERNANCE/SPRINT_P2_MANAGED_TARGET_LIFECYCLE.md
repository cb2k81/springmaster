---
documentType: sprint-summary
status: active
scope: p2-managed-target-lifecycle
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# P2 Managed Target Lifecycle

## Objective

Close the controlled delivery lifecycle for existing managed Java backend targets without authorizing mutation of an additional real Fachprojekt.

## Delivered

- atomic target payload, component-version and provenance updates in one patch transaction;
- declarative profile rules as the single source for payload, scope and validation policy;
- a version compatibility matrix with explicit N-1, downgrade and cross-major decisions;
- target-native patch-manifest schema resolution during generation;
- a self-contained second managed-target pilot created under a disposable work directory;
- target-safe tooling selfchecks that skip capabilities not installed in the target.

## Patches

- `000146_springmaster_atomic_managed_target_state`;
- `000147_springmaster_declarative_update_profiles`;
- `000148_springmaster_target_compatibility_matrix`;
- `000149_springmaster_managed_project_lifecycle_pilot`.

## Resulting versions

- foundation: `0.17.0-foundation`;
- Tooling: `0.7.0`;
- Template: `0.3.1`;
- Platform Update: `0.10.0`.

## Safety boundary

The second pilot is generated and updated only below `target/` or an explicitly supplied disposable directory. It is not a registry delivery target and does not authorize mutation of ZDM, IDM, Personnel, Contacts, Orders or any other real Fachprojekt. Real target delivery remains an explicit `target-apply` decision against an enabled descriptor.

## Deferred

A second real target descriptor, fleet-wide migration orchestration, database-data migration and Generated-Slice delivery remain deferred.

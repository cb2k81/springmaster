---
documentType: governance
status: active
scope: platform-versioning
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: legacy-version-policy-patch-journal
---
# Springmaster Version Policy

## Canonical truth

`platform/versions/platform.env` is the canonical current version source. `pom.xml` uses exactly `PLATFORM_VERSION-SNAPSHOT`. Runtime API and Actuator information load the packaged canonical file and contain no copied fallback version.

Historical version changes belong in Git and patch changelogs, not in this living policy.

## Version dimensions

| Variable | Responsibility |
|---|---|
| `PLATFORM_VERSION` | qualified aggregate Springmaster foundation state |
| `PLATFORM_CORE_VERSION` | reusable Java core under `de.cocondo.system` |
| `PLATFORM_TOOLING_VERSION` | patch, export, build, DBTool, project-new and release tooling |
| `PLATFORM_TEMPLATE_VERSION` | generated project skeleton and template contract |
| `PLATFORM_DEMO_VERSION` | demo and reference-slice capabilities |
| `PLATFORM_UPDATE_VERSION` | managed-target planning, generation and delivery contract |
| `PLATFORM_STATE_PATCH` | local patch that established the current version truth |

Only affected dimensions are incremented.

## Semantic impact

- `patch`: compatible correction without a new capability or contract surface.
- `minor`: compatible new capability, contract extension or newly qualified delivery path.
- `major`: incompatible public contract, artifact format or supported upgrade-path change.

During the `0.x` foundation phase, an incompatible change must increment at least the minor component and be called out explicitly in an accepted ADR or governance decision. A `1.0.0` release requires a separate readiness decision.

## Sprint and release operation

Commits and intermediate patches do not each create a released product version. During a sprint, changes record expected semantic impact. The release-closing patch applies the accumulated component increments once, synchronizes `PLATFORM_VERSION` and the Maven SNAPSHOT coordinate, and sets `PLATFORM_STATE_PATCH`.

A release qualification then generates a machine-readable manifest and proposed Git tag. Sprint, commit, `artifactId`, `patchId` and release version remain independent identities.

## Change classification

- Core code/API changes affect `PLATFORM_CORE_VERSION`.
- Patch, export, build, DBTool, project-new or release-tool changes affect `PLATFORM_TOOLING_VERSION`.
- Generated skeleton or project-new output changes affect `PLATFORM_TEMPLATE_VERSION` in addition to tooling when the generator itself changes.
- Demo/reference capability changes affect `PLATFORM_DEMO_VERSION`.
- Managed-target planning, generation, compatibility or apply behavior affects `PLATFORM_UPDATE_VERSION`.
- Documentation-only corrections without current status, contract or governance impact do not increment a version.

Do not increment unrelated components as a bundle convenience.

## Patch and release relationship

`PLATFORM_STATE_PATCH` records provenance, not product identity. Patch Manifest V2 `artifactId` is also transaction provenance and must never replace a component or release version.

A published release is immutable. A correction receives a new semantic version, release manifest and Git tag.

## Managed targets

Every target delivery declares supported source versions, target component versions, required migrations and compatibility status. Applying payload and updating the target's installed version truth is one atomic transaction. A separate version-closure patch is not an accepted steady-state workflow.

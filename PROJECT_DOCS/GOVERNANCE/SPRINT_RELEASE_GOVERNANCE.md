---
documentType: governance
status: active
scope: delivery-lifecycle
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Sprint and Release Governance

## Identity boundaries

Sprint, Git commit, patch artifact and product version are independent identities.

- A sprint is a planning and delivery interval.
- A Git commit is durable repository history.
- A patch artifact is an immutable transaction identified globally by `artifactId` and locally by `patchId`.
- A component or foundation version identifies a qualified, supportable product state.

No identifier is derived automatically from another. Patch numbers are not document versions, release numbers or sprint numbers.

## During a sprint

Every change is classified as documentation, core, tooling, template, demo, platform update or application behavior. The expected semantic impact is recorded as `none`, `patch`, `minor` or `major` for each affected component.

Normal work does not increment released component versions for every intermediate commit. The repository may remain on its next `-SNAPSHOT` coordinate until the release qualification patch establishes the new state.

A sprint may contain several independently accepted patches. Each patch remains small, baseline-bound and revertible. Scope expansion requires a separate patch.

## Sprint summary

A sprint closes with one compact durable summary when it produced a release candidate or a material platform decision. The summary uses `documentType: sprint-summary` and records:

- objective and delivered outcomes;
- accepted patches and affected components;
- qualification commands and results;
- deferred work and technical debt;
- release decision and resulting versions.

Transient command logs, acceptance directories and generated reports are not copied into the summary.

## Release qualification

A release candidate is qualified only from a clean committed Working Tree. The standard command is:

```bash
cd /opt/cocondo/springmaster || exit 1
./bin/release-qualify.sh
```

Qualification runs the documentation gate, Maven tests, tooling selfcheck and a full export with integrity verification. It writes an ignored machine-readable release manifest under `build/releases/`.

The command does not create or push a Git tag. After review, an authorized maintainer creates the exact tag recorded in the manifest. Push remains a separate explicit action.

## Hotfixes

A hotfix receives a patch component version, a new release manifest and a new Git tag. Published versions and existing patch artifacts are immutable.

## Target projects

A managed target update records source release, source commit, global `artifactId`, local target `patchId`, source and target component versions, compatibility result and target qualification evidence. Payload and target version truth must be updated atomically.

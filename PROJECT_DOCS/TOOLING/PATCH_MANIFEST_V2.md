---
documentType: guide
status: active
scope: repository
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Patch Manifest V2

## Purpose

Patch Manifest V2 separates the globally stable artifact identity from the repository-local apply sequence.

## Required identity fields

Every newly produced patch ZIP contains the following fields in `manifest.json`:

```json
{
  "schemaVersion": "springmaster.patch-manifest.v2",
  "artifactId": "urn:uuid:00000000-0000-4000-8000-000000000000",
  "id": "000140_example",
  "patchId": "000140_example",
  "name": "example"
}
```

The example UUID is illustrative only. Real producers must create a new random UUID for every distinct patch artifact.

- `schemaVersion` must be exactly `springmaster.patch-manifest.v2`.
- `artifactId` is the globally stable identity of the immutable ZIP. It is a canonical lowercase, non-nil UUID URN.
- `patchId` is the repository-local sequence and archive identity in the format `000000_name`.
- `id` remains a compatibility alias and must equal `patchId`.
- The archive filename remains `<patchId>.zip`.
- `name` must match the name portion of `patchId`.

## Global and local identity

The same immutable delivery may be assigned different local `patchId` values in different target repositories while retaining its `artifactId`. Within one repository, an `artifactId` may not be archived under a different `patchId`.

Reusing an `artifactId` for changed bytes is prohibited. A rebuilt or modified ZIP is a new artifact and therefore receives a new `artifactId`.

## Migration behavior

Historical V1 archives without `schemaVersion` or `artifactId` remain readable by registry, show and rollback operations. They are legacy provenance and are not rewritten.

After patch `000140_springmaster_patch_artifact_identity_v2`, new incoming V1 artifacts fail closed during live-baseline validation and artifact preflight. Producers embedded in Springmaster must emit V2 before their output is accepted.

## Producers

The contract applies to:

- manually assembled Springmaster patches;
- `project-new` bootstrap evidence;
- Platform Update target patches and compatibility patches;
- test fixtures;
- generated-slice patch blueprints and later assemblers.

## Evidence

Patch logs, artifact-preflight reports and target-apply evidence carry both identities. Durable product documentation must not use either identity as its own document version.

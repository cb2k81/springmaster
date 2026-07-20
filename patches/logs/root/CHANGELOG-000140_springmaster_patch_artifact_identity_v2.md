# 000140_springmaster_patch_artifact_identity_v2

Implements Patch Manifest V2 and closes the global patch-artifact identity decision from ADR-0012.

## Changes

- requires `springmaster.patch-manifest.v2` for every new incoming artifact;
- introduces a canonical UUID-URN `artifactId` independent of the local numeric `patchId`;
- keeps historical V1 archives readable while rejecting newly delivered V1 patches;
- rejects repository-local reuse of one `artifactId` under a different `patchId`;
- propagates both identities through patch logs, artifact-preflight evidence and target-apply evidence;
- upgrades Project-New, Platform Update, test fixtures and Generated-Slice blueprints to the V2 contract;
- documents the migration and updates tooling, template and update component versions.

## Versions

- Platform: `0.14.0-foundation`
- Tooling: `0.4.0`
- Template: `0.2.0`
- Platform Update: `0.9.0`

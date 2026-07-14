# CHANGELOG 000124_springmaster_patch_artifact_preflight_hardening

## Scope

`root`

## Changes

* Adds `patch.sh artifact-preflight` with clean-Git, complete live-hash, payload-hygiene, isolated-worktree apply, exact scope, byte comparison, diff and export gates.
* Adds fail-closed fixtures for stale hashes, trailing whitespace, EOF blank lines, missing final newlines and dirty baselines.
* Preserves and verifies ZIP-declared Git executable classes (`100644`/`100755`) for all payload types, including `.bash`, without rejecting or removing host-specific group-write bits.
* Upgrades full and split export metadata to format version 2 with raw source size/SHA-256 manifests and Git source state.
* Adds optional single-export closure evidence through `--evidence` or `PATCH_EXPORT_EVIDENCE_FILE`.
* Excludes mutable `patches/logs/validation/**` runtime evidence from root and generated-project source exports.
* Adds export integrity verification with positive, tampered-manifest and mutable-validation-path negative fixtures.
* Extends Tooling selfcheck and Maven contract coverage without creating duplicate full exports.
* Keeps Project-New distributions complete by copying and accepting all new Preflight/Integrity tools with canonical portable schema IDs.
* Advances Foundation to `0.13.63-foundation` and Tooling to `0.3.23`.

## Non-goals

* No Core, Demo, generated-slice IR or target-project runtime change.
* No automatic patch commit or push.
* No removal of host-side targeted or full Maven acceptance tests.

# CHANGELOG 000096 - springmaster_patch_manifest_identity_guard

## Scope

Tooling patch for the Springmaster patch system.

## Changes

- Requires explicit `manifest.id` and `manifest.patchId` for all newly applied patch ZIPs.
- Requires `manifest.id == manifest.patchId`.
- Requires the patch archive filename to be exactly `<patchId>.zip`.
- Uses the manifest patch ID as the applied patch archive directory instead of silently deriving the next ID from `manifest.name`.
- Documents the manifest identity contract in the patch system, validation policy and command generation contract.

## Verification target

- `python3 -m py_compile ./bin/patch.py`
- tooling selfcheck
- patch dry-run/apply
- `./bin/patch.sh show latest` must match `000096_springmaster_patch_manifest_identity_guard`
- full ZIP export

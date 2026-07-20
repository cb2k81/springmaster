---
documentType: guide
status: active
scope: platform-update
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Platform Update Version Compatibility

`platform/update/compatibility/platform-compatibility-matrix.json` defines the supported source-version floor for every update profile. Compatibility is checked against the target's current `platform/versions/platform.env` and the current Springmaster master versions.

The policy is fail-closed:

- missing mandatory source versions are rejected;
- source versions below the declared floor are rejected;
- cross-major transitions are rejected;
- downgrades are rejected;
- supported N-1 and same-version transitions pass.

The generation decision is written to `platform/update/compatibility-decision.json`, embedded in managed state and bound into the patch manifest. `target-apply` recomputes the decision and requires it to equal the manifest decision before target mutation.

The existing command `compatibility-plan` concerns target patch-engine/scope compatibility. The command `compatibility-check` concerns component-version compatibility; these are separate gates.

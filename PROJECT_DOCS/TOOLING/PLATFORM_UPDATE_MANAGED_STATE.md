---
documentType: guide
status: active
scope: platform-update
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Platform Update Managed State

Every generated Platform-Update payload carries target component versions and apply provenance in the same target-local patch transaction as the payload.

The managed files are:

```text
platform/versions/platform.env
platform/update/managed-state.json
```

The generator preserves target-local identity and unrelated component versions. It updates only the component associated with the selected profile, records the target-local patch as `PLATFORM_STATE_PATCH`, and sets `PLATFORM_BASELINE_KIND=managed-target`.

`managed-state.json` binds target, profile, global `artifactId`, local `patchId`, source master versions and resulting installed versions. `target-apply` verifies this state after the target accept and before producing closure evidence and the single final export.

A payload without matching state is not a complete managed target update.

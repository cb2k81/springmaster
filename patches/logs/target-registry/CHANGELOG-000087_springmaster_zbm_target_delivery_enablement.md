# 000087 springmaster zbm target delivery enablement

## Summary

Explicitly reclassifies the configured `zbm` target from initialization-only to controlled tooling-delivery mode.

## Changes

- Sets `TARGET_STATUS=DELIVERY_ENABLED` for `platform/update/targets/zbm.env`.
- Sets `TARGET_LIFECYCLE=update-enabled`.
- Sets `TARGET_INITIALIZATION_ALLOWED=false`.
- Sets `TARGET_UPDATE_ALLOWED=true`.
- Sets `TARGET_DELIVERY_ENABLED=true`.
- Narrows `TARGET_ALLOWED_PROFILES` to `tooling` for this first controlled target update step.

## Rationale

The ZBM target path exists at `/opt/cocondo/zbm` and the previous Springmaster platform-update run successfully completed generate, preflight and apply-plan for the `tooling` profile. The actual `target-apply` was correctly blocked by the descriptor guard while `TARGET_DELIVERY_ENABLED=false`.

## Validation

After this patch, `platform-update validate zbm`, `platform-update show zbm`, and the detached `zbm tooling plan` must remain successful before a mutating `zbm tooling apply` is started.

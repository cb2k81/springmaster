# 000086 springmaster zdm target descriptor registration

## Summary

Registers `zdm` as a Springmaster target descriptor so platform-update can plan and inspect target updates for `/opt/cocondo/zdm`.

## Changes

- Adds `platform/update/targets/zdm.env`.
- Keeps target delivery disabled by default via `TARGET_DELIVERY_ENABLED=false`.
- Marks ZDM as `INITIALIZATION_CANDIDATE` until the target project and local patch system are explicitly verified.

## Validation

- `platform-update plan zdm --profile tooling` can now resolve the target descriptor.
- Mutating target delivery remains blocked until the descriptor is explicitly reclassified.

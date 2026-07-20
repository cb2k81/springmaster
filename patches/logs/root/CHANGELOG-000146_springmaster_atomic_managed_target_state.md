# CHANGELOG 000146_springmaster_atomic_managed_target_state

## Purpose

Make managed target payload, installed component versions and delivery provenance one atomic patch transaction.

## Changes

- Add managed target state synthesis and verification
- Embed target component versions and patch provenance in generated target patches
- Persist managed state and target apply evidence as part of the same transaction
- Extend target patch scopes and regression coverage for managed state files

## Qualification

The patch acceptance profile runs a complete Maven test and no export or push.
Bundle-level checks run the relevant managed-state, rules, compatibility and isolated-pilot fixtures.

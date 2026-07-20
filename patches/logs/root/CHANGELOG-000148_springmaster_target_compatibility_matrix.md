# CHANGELOG 000148_springmaster_target_compatibility_matrix

## Purpose

Introduce an explicit compatibility matrix and fail-closed N-1 upgrade decisions for managed targets.

## Changes

- Add a machine-readable platform compatibility matrix
- Evaluate source-to-target component transitions before patch generation and apply
- Persist the compatibility decision in generated target patches and evidence
- Add positive and negative N-1 compatibility fixtures

## Qualification

The patch acceptance profile runs a complete Maven test and no export or push.
Bundle-level checks run the relevant managed-state, rules, compatibility and isolated-pilot fixtures.

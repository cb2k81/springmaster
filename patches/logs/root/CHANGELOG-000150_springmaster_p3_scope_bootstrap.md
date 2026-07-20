# CHANGELOG 000150_springmaster_p3_scope_bootstrap

## Purpose

Expand the fail-closed root scope only for the P3 demo, security, entity and renderer contract paths.

## Changes

- Allow the exact P3 demo and system security/entity source paths in the root scope
- Propagate the same least-privilege scope to Project-New defaults
- Keep all unrelated target and application paths blocked

## Qualification

Artifact preflight and the selected full-test profile must pass. The bundle performs the relevant contract and isolated-pilot checks without push or real-target mutation.

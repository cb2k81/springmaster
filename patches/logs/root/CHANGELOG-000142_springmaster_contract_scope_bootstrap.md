# CHANGELOG 000142_springmaster_contract_scope_bootstrap

## Purpose

Extend the configured Root patch scope for repository instructions, machine-readable contracts and the explicit observability Core boundary required by the P1 cross-cutting closure.

## Changes

- Allow `AGENTS.md` and `contracts/**` through the configured Root scope
- Allow only `GlobalApiExceptionHandler.java` and `de.cocondo.system.observability/**` as additional Core paths
- Propagate the same Root-scope extension to documented and generated environment templates
- Keep the patch engine fail-closed through explicit configured paths

## Qualification

The patch acceptance profile runs a complete Maven test and no export or push.
Bundle-level checks additionally run the relevant contract integration fixtures and Project-New acceptance.

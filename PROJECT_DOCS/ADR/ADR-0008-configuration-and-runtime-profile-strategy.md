---
documentType: adr
status: accepted
scope: configuration-and-runtime-profiles
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# ADR-0008: Configuration and Runtime Profile Strategy

## Context

Springmaster shell tooling, Spring Boot runtime configuration and generated projects previously repeated defaults in several files without one machine-readable contract. This allowed drift between `.env.example`, the documented environment template, the shell loader, Spring properties and the project skeleton.

## Decision

1. `contracts/configuration/environment-contract.json` is the machine-readable contract for project-local environment keys, types, defaults, secret classification and consumers.
2. `.env.example` is the source-controlled local-default file. A local `.env` may override it and is never committed.
3. `bin/lib/core/env.sh` loads `.env.example` first and `.env` second. Tooling must consume the normalized exported variables instead of introducing private defaults.
4. Spring Boot configuration uses environment placeholders for settings shared with shell tooling. Profile-specific YAML files contain only intentional profile overrides.
5. Supported runtime profiles are `dev`, `test`, `build` and `prod`. The default profile is `dev`; production activation must be explicit.
6. Secrets may be represented by non-production local defaults only where existing development tooling requires them. Production secrets have no accepted repository default and must be supplied externally.
7. Project-New renders a project-local copy of the contract and ships the validator. Generated projects must pass the same configuration-contract check.
8. New configuration keys require a contract entry, consumer documentation, tests and the appropriate tooling/template version impact.

## Consequences

- Configuration drift becomes a blocking tooling finding.
- The contract records classification and ownership without turning narrative documentation into a second source of truth.
- This ADR does not introduce a secret manager, remote configuration service or dynamic configuration refresh.
- Target projects adopt the contract only through an explicit Project-New or Platform-Update delivery.

## Verification

```bash
cd /opt/cocondo/springmaster || exit 1
./bin/config-contract.sh --check
./bin/config-contract-it.sh
./bin/project-new-acceptance.sh --skip-generated-maven-test
```

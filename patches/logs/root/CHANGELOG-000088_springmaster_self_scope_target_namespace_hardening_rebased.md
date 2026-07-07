# 000088_springmaster_self_scope_target_namespace_hardening_rebased

Scope: root
Type: tooling-architecture
Baseline: Springmaster after `000087_springmaster_zbm_target_delivery_enablement`.

## Purpose

Harden the separation between Springmaster self-scope, shared core namespace, target-project namespace definitions and project-local configuration.

## Changes

- Load project-local `.env.example` defaults before `.env` overrides in shared shell tooling.
- Let export naming prefer `APP_EXPORT_PROJECT_KEY` / `APP_NAME` before `export.config.json:projectKey`.
- Make patch scopes namespace-aware via `APP_BASE_PACKAGE` and `APP_CORE_PACKAGE`.
- Generate target-local domain/project-key patch scopes for new projects.
- Prevent `platform-update --profile tooling` from delivering target-local defaults such as `.env.example`, `export.config.json` and `PROJECT_DOCS/CONFIG/**`.
- Document the namespace and local configuration contract.

## Rebase note

This patch uses expected baseline hashes from the actual file content. The previous package was generated against text-export separator artefacts and therefore failed the baseline guard correctly.

## Validation

- ZIP integrity check.
- Patch dry-run/apply.
- `python3 -m py_compile bin/patch.py`.
- `bash -n` for changed shell scripts.
- `./bin/project-new-acceptance.sh --skip-generated-maven-test`.
- `./bin/platform-update.sh generate zbm --profile tooling` with forbidden-payload guard.
- `mvn test` on target system.
- Full export.

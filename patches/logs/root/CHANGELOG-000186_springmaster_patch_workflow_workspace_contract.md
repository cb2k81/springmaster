# Patch 000186 - Springmaster Patch Workflow Workspace Contract

## Purpose

Harden the project-owned patch process so terminal-safe operator bundles start canonical patch workers directly, preserve compact project-local logs, and use `patches/work/` as a safe single-current-workflow diagnostic handoff workspace.

## Changes

- Add project-relative operator-log and operator-workspace configuration with tracked-content and symlink guards.
- Prepare and clean the operator workspace fail-closed before every new patch dry-run or accept.
- Keep observer commands non-mutating.
- Add deterministic single-ZIP diagnostic handoff from canonical Toolkit evidence.
- Register `patches/work/**` as a dedicated ignored, temporary, export-excluded directory class and forbid it for Codex.
- Add process, directory and export regression coverage.
- Close the real Springmaster process pilot evidence from accepted patch 000184.
- Advance Springmaster to `0.21.0-foundation`, Tooling to `0.11.0` and state patch `000186`.

## Boundaries

- No automatic accept, commit or push.
- No Codex execution or writable Codex promotion.
- Managed-project rollout remains blocked pending an explicit post-pilot generalization decision.
- The abandoned external D3 candidate using local patch ID `000185` is not part of repository history and must be rebuilt against the accepted post-000186 baseline under a new local patch ID.

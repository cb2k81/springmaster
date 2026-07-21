# 000167_springmaster_patch_run_api_project_local_start_handoff

## Purpose

Close the remaining operational gap between the project-local Patch Run API and ad-hoc terminal wrappers that wrote start output, run IDs or summary pointers into `~/Downloads`.

## Changes

- background `accept` and `verify` support `--format human|env|json` for their start response;
- `--watch` attaches the compact observer directly after the detached child is created;
- `--watch-interval` and `--watch-timeout` configure only the parent observer and are not forwarded to the child;
- every run writes a sanitized project-local `invocation.json` with patch filename, SHA-256, identity and requested options;
- canonical acceptance publication preserves `invocation.json` across self-update compaction;
- absolute incoming artifact paths are not written to the invocation record and are redacted from the background command header;
- `status`, `watch`, `wait`, `result` and `diagnose` reject empty references before path resolution;
- observer commands support explicit `--patch <patch-id>` resolution;
- integrated documentation and `AGENTS.md` define `Downloads` as artifact ingress only;
- Run API integration coverage proves machine-readable start output, integrated watch, invocation evidence, empty-reference rejection, explicit patch resolution and absence of runtime helper files beside incoming ZIPs.

## Git and transaction boundary

The patch does not change Manifest V2, baseline hashes, scope validation, write locking, detached-worktree qualification, exact Git path parity, patch-scoped staging, cherry-pick transfer, rollback compensation or push opt-in semantics. Git remains the durable repository truth.

## Whitespace and efficiency

Whitespace validation remains limited to effective patch paths at apply, staged and qualified-commit boundaries. The change introduces no repository-wide formatting or line-ending normalization and no repeated full-tree whitespace scan.

## Validation

- `python3 -m py_compile bin/patch.py`
- `bash -n bin/patch-run-api-it.sh`
- `git diff --check`
- `bin/patch-run-api-it.sh`
- `bin/tooling-selfcheck.sh --no-export`
- Patch Manifest V2 live-baseline, dry-run and artifact preflight against the reconstructed byte-identical post-000166 baseline

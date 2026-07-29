# CHANGELOG 000194 — Patch Toolkit staging and version closure

## Anlass

Patch `000193` proved the split-staging runtime but failed in the live targeted validator because `bin/codex-pilot-ready.py` still hard-coded Toolkit `1.1.1` while the activation contract and payload declared `1.1.2`.

## Änderungen

- Installs Cocondo Patch Toolkit `1.1.2` with exact split staging for tracked updates/deletions and additions.
- Resolves the expected Toolkit version and runtime digest from the canonical activation contract.
- Validates project env, lock, activation evidence, sidecar and runtime as one version closure.
- Adds negative regression fixtures for project-env, lock and runtime drift.
- Exposes Codex-readiness findings in targeted-validator logs.
- Adds named validation substeps for syntax, targeted, full and release profiles.
- Synchronizes current Governance, ADR, Tooling Baseline and Sprint statements to Toolkit `1.1.2` while preserving historical `1.1.1` provenance.

## Incidentbezug

- Cleanup staging incident: `run-20260728T153249Z-5f8dd710bdcc`.
- Superseded hotfix dry-run: `run-20260729T081344Z-2ab09fa58419` (`000193`).
- Patch `000193` is retained as failed incident evidence and is not reused.

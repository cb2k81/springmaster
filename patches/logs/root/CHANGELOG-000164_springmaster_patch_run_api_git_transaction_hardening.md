# CHANGELOG 000164 — Patch Run API and Git transaction hardening

## Scope

Hardens the Springmaster patch engine and its integrated operating documentation without changing product, demo, target-project or artifact-manifest semantics.

## Runtime changes

- adds canonical `status`, `watch`, `wait`, `result`, `diagnose` and `doctor` commands;
- adds immutable run IDs and atomic temporary `run.json` records;
- makes acceptance start idempotent for already applied and already running artifacts;
- separates timestamped attempts, canonical successful acceptance and verify evidence;
- propagates exact child failure step and root-cause candidates to the parent summary;
- adds explicit `--wait-for-lock` while retaining historical `--wait` compatibility;
- preserves bounded validation log names and compact terminal output;
- stages archive/evidence before live transfer and compensates pre-finalization failures;
- treats post-finalization reporting or push failures as warnings on a durable local acceptance.

## Git and whitespace contract

- captures the clean live baseline HEAD before isolated validation;
- requires qualified child commit parent equality with the live baseline;
- requires exact equality of patch-log, child-commit and live-transfer path sets;
- stages only patch paths and never uses broad repository staging;
- checks applied paths, staged paths and the qualified commit for whitespace errors;
- uses intent-to-add only inside the isolated worktree so new files are checked;
- does not reformat, normalize or repeatedly scan unrelated repository files;
- keeps push status separate and never pushes without explicit `--push`.

## Regression coverage

- introduces `bin/patch-run-api-it.sh` for background acceptance, idempotency, canonical state resolution, verify separation, exact failure propagation, whitespace rejection and doctor/result behavior;
- integrates the new fixture into `bin/tooling-selfcheck.sh`;
- updates transactional acceptance expectations from generic `worktree-validation` to the exact child failure step;
- retains long-selector and normalized-name collision coverage.

## Documentation

- adds `PROJECT_DOCS/TOOLING/PATCH_RUN_API.md`;
- refines ADR-0012 and Patch System, Acceptance, Transaction, Validation, Command Generation and Recovery documentation;
- updates repository working rules in `AGENTS.md` and the documentation index.

## Technical-debt checkpoint

Closed:

- ambiguous latest-summary selection;
- redundant acceptance restart after an already committed patch;
- terminal-dependent polling blocks;
- verify overwriting acceptance evidence;
- generic parent failure classification;
- missing path-parity and patch-scoped whitespace enforcement at all Git boundaries.

Deferred deliberately:

- removing legacy non-commit acceptance mode;
- changing the historical default export behavior;
- splitting `bin/patch.py` into multiple Python modules;
- automatic remote push remediation.

These deferrals are compatibility and modularization work, not blockers for the canonical `--background --wait-for-lock --no-export --commit` workflow.

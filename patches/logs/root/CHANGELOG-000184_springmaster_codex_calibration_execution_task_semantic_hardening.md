# 000184 springmaster Codex calibration execution and task semantic hardening

## Scope

Springmaster-only D1/D2 hardening for controlled Codex calibration execution, operator-command effects, task semantics, evidence and fail-closed run-state handling.

## Summary

- Introduce the active, normative Operator Command Effect Contract for host commands proposed by chat, agents or runbooks. Manual execution no longer counts as authorization of undisclosed effects.
- Require pre-provisioned, writable, non-symlink external worktree, run and artifact roots; the agent-task harness no longer creates configured external roots implicitly.
- Upgrade the Agent Task Contract incompatibly from V1 to V2 with closed change classes, mode semantics, risk- and change-class-driven qualification, maximum net-added-byte limits, a closed evidence set and machine-evaluable completion criteria.
- Make `analysis` and `qualification` non-mutating, forbid critical implementation during calibration and bind modification capabilities to matching change classes.
- Add immutable operator-command-effect and Codex invocation records, exact task/worktree binding, argument parity, scope and environment checks, timestamp and exit-state validation, SHA-256 retention and mutation detection.
- Require the exact safe non-interactive Codex invocation shape with explicit model, `never` approvals, mode-specific sandbox and Linux `bwrap`; reject `--add-dir`, config/profile overrides, full-auto and sandbox-bypass flags.
- Enforce unconditional Codex write denial for operator home and Downloads, integration and Git metadata, external run/artifact roots, other repositories and host temporary directories. Handoff remains a separate trusted operator action.
- Stabilize the export lifecycle fixture by locating ZIP members with Python `zipfile` instead of a `pipefail`-sensitive `unzip | grep -q` pipeline. This closes the false `metadata is not packaged inside the ZIP` failure observed during the first candidate dry-run.
- Fail closed for missing, malformed, mismatched or unknown-status run records and for unsuccessful Codex invocations.
- Extend integration fixtures for non-mutating modes, missing roots, symlink roots, root overlap, malformed run state, unsuccessful invocation, evidence mutation, forbidden commands, risk policy and corrected net-added-byte semantics.
- Keep canonical governance host-neutral: concrete operator handoff paths belong only to external operator bundles, while agent write denial remains semantic and unconditional; this preserves the process-operations static-path contract.
- Register the new contracts, documentation and report-only quality rules in the active inventories and readiness gate.
- Advance Springmaster to `0.20.0-foundation`, Tooling to `0.10.0` and the state patch to this delivery.

## Compatibility decision

Task Contract V2 is intentionally incompatible with V1. V1 tasks are rejected instead of silently upgraded because they lack the semantic and evidence fields required for deterministic calibration. The pilot has not yet authorized writable Codex work and therefore has no accepted V1 task history requiring migration.

## Deliberate stop

This delivery retains `PROJECT_READY`, `NEXT_ACTION=CODEX_CALIBRATION` and `WRITABLE_CODEX_AUTHORIZED=false`. It does not execute Codex, authorize writable calibration, create commits from agent work, integrate results, push, mutate GWC or update managed projects. D3 calibration oracle and task-pack work remains separate.

## Producer qualification

- Python and shell syntax validation
- agent-task semantic and boundary integration fixture
- Codex pilot readiness expected-case fixture
- quality-registry and test-contract fixtures
- documentation and project-directory fixtures
- candidate Codex readiness with zero findings
- Tooling Selfcheck without export
- project-local and portable artifact inspection with payload-equivalence verification

## Required local acceptance qualification

The delivery is a candidate until the project-local artifact has passed the following checks on the real committed baseline:

- project-local checksum, preflight and non-downgradable dry-run
- runtime C1 denial probes for operator-home/Downloads and all non-worktree host write scopes remain required before writable calibration promotion
- Maven `clean verify` through the selected validation profile
- explicit acceptance without push only after the dry-run is green

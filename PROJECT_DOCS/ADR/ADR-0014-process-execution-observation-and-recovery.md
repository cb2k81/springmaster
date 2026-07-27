---
documentId: ADR-0014
title: Process Execution, Observation and Recovery
documentType: adr
status: accepted
authority: normative
scopeLevel: component
scopePaths:
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-24
validFrom: 2026-07-24
lastReviewedAt: 2026-07-24
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# ADR-0014 Process Execution, Observation and Recovery

## Context

Long-running patch, verification and build processes must survive terminal loss and must be recoverable from canonical run evidence. Repeated operational failures showed that static installation paths, linked-worktree `.git` handling, external `nohup` supervisors, interactive `set -e`, large terminal streams and runtime files inside a working tree create false failures and ambiguous recovery states.

The same failure classes occur independently of a target project's business domain. Springmaster therefore needs a project-neutral operational contract before the mechanism can be propagated to managed projects.

## Decision

1. Project root, Git common directory and integration worktree are resolved from Git at runtime. No user name, installation directory or download directory is encoded in generic tooling.
2. A path configured below `.git/` resolves against the Git common directory. This is mandatory for linked worktrees, where `.git` is a file rather than a directory.
3. The configured integration branch identifies exactly one integration worktree through `git worktree list --porcelain`.
4. Patch workers are started directly by `cpatch`; arbitrary detached commands are started directly by `crun`. A second `nohup`, `setsid`, PID file or supervising shell around an already detached Toolkit run is forbidden.
5. `status`, `resume`, `watch`, `wait`, `result`, `diagnose` and `incident` are observers. Losing or interrupting an observer never changes the worker.
6. Observer commands are terminal-safe by default. A terminal worker failure is reported as data and does not return a failing shell exit unless `--strict-exit` is explicit.
7. Mutating patch runs require a clean integration worktree. A dirty feature worktree does not invalidate observation and does not get confused with the integration checkout.
8. Runtime records, operation pointers and incidents live below the Git common directory and never dirty a tracked working tree.
9. Dry-run and accept remain two explicit operator decisions. No outer orchestrator chains both operations.
10. Managed-project rollout stays blocked until the Springmaster pilot proves the required scenarios from the machine-readable process contract.

## Consequences

The canonical operational entrypoint is `bin/process-ops.sh`. It is an adapter over Toolkit Run APIs, not a second process engine. The tool may be copied or packaged later only after its contract and fixtures pass without Springmaster-specific assumptions.

Existing scripts with static paths or nested background supervision are non-canonical. They may be retained as incident evidence, but they are not allowed as production guidance.

## Rejected alternatives

- Static repository and download paths: rejected because they are host- and user-specific.
- Outer polling orchestration around detached Toolkit runs: rejected because it introduces a second, stale state machine.
- Runtime state under `target`, `build` or `Downloads`: rejected as canonical state because cleanup or export behavior can remove it and because tracked-tree pollution remains possible.
- Automatic accept immediately after dry-run: rejected because dry-run review is a deliberate promotion boundary.

## Singleton starts and retry semantics

11. Long-running named operations that must not overlap use a project-neutral singleton key. `process-ops run-start --singleton-key <key>` serializes discovery and start below the configured process-state directory.
12. A repeated start for an active singleton reuses the existing run ID and atomically repairs its pointer. It must not create a second worker.
13. A terminal singleton is returned as existing state. Starting another worker requires the explicit `--restart-terminal` flag.
14. More than one active run for the same singleton key is an incident. The tool fails closed and requires diagnosis rather than selecting one arbitrarily.
15. Canonical pointers are hints to a run ID, not a second state machine. They are written atomically and can be reconstructed from Toolkit run records.

## Accepted clarification: project-local operator evidence

The canonical worker and run state remain below the Git common directory. A project may additionally define project-relative, ignored operator-log and single-current-workflow handoff directories. These directories are not alternate run truth. Patch starts prepare the handoff workspace fail-closed; observers never clean it. Diagnostic upload artifacts are generated from canonical run evidence as exactly one archive, while patch workers continue to be started directly through the `cpatch` Run API.

## Accepted clarification: historical operator-log evidence

The project-relative operator-log root may contain retained tracked historical evidence. Runtime safety is enforced at the exact generated run directory `<operator-log-root>/<patch-id>/<run-id>/`: that directory must be ignored, non-symlinked and free of tracked content. Historical tracked siblings elsewhere below the shared root are compatible and must neither block observers nor be modified by runtime preparation.

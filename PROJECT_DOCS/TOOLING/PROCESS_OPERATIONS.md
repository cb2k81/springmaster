---
documentId: TOOL-PROCESS-OPERATIONS-0001
title: Process Operations Guide
documentType: guide
status: active
authority: informative
scopeLevel: component
scopePaths:
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-24
validFrom: 2026-07-24
lastReviewedAt: 2026-07-24
reviewBy: 2027-01-24
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Process Operations Guide

## 1. Purpose

`bin/process-ops.sh` provides a compact, terminal-safe and project-neutral interface to the Cocondo Toolkit Run API. It resolves Git worktrees and runtime directories dynamically and never supervises a Toolkit worker itself.

## 2. Environment-dependent paths

Inspect the effective paths before operating:

```bash
./bin/process-ops.sh resolve
```

The tool derives:

- current project root from `git rev-parse --show-toplevel`;
- Git common directory from `git rev-parse --path-format=absolute --git-common-dir`;
- integration worktree from `git worktree list --porcelain` and `CPATCH_INTEGRATION_BRANCH`;
- Toolkit run, lock and acceptance roots from project configuration;
- process operation and incident state from `.cocondo/process.env` (`CPROCESS_STATE_DIRECTORY` and `CPROCESS_INCIDENT_DIRECTORY`).

Artifact and worktree roots are intentionally environmental:

```bash
export COCONDO_ARTIFACT_ROOT="<local-artifact-directory>"
export COCONDO_WORKTREE_ROOT="<local-worktree-directory>"
```

Equivalent persistent Git configuration is supported:

```bash
git config cocondo.artifactRoot "<local-artifact-directory>"
git config cocondo.worktreeRoot "<local-worktree-directory>"
```

No generic contract may contain a concrete user home, repository installation path or internal ChatGPT path.

## 3. Patch run

Start exactly one detached dry-run worker:

```bash
./bin/process-ops.sh patch-dry-run <patch.zip> --profile auto
```

The output is compact and includes the canonical `runId`. Observe or resume only through that ID:

```bash
./bin/process-ops.sh status <run-id>
./bin/process-ops.sh watch <run-id>
./bin/process-ops.sh wait <run-id>
./bin/process-ops.sh result <run-id>
```

`Ctrl-C` on `watch` stops only the observer. Default observer exits are terminal-safe. Automation that intentionally needs the worker exit code uses `--strict-exit`.

After an explicitly reviewed `DRY_RUN_SUCCEEDED`, start accept as a separate decision:

```bash
./bin/process-ops.sh patch-accept <patch.zip> --profile auto
```

Never wrap these commands in an additional detached orchestrator and never chain dry-run and accept automatically.

## 4. Generic long-running command

```bash
./bin/process-ops.sh run-start \
  --name release-qualification \
  --cwd . \
  -- ./bin/release-qualify.sh
```

The worker is owned by `crun`. The returned run ID is observed through the same terminal-safe commands.

## 5. Recovery

First query the existing run rather than restarting it:

```bash
./bin/process-ops.sh resume <run-id>
```

For failures, inconsistencies or orphan reconciliation:

```bash
./bin/process-ops.sh diagnose <run-id>
./bin/process-ops.sh incident <run-id>
```

`incident` copies the canonical run record, invocation, log and validation-stage report into the configured incident root below the Git common directory. It does not modify the repository or the worker.

## 6. Working-tree rules

- Mutation checks the clean integration worktree, not the caller's feature worktree.
- Observation is permitted from any linked worktree.
- Operation reports and incidents are outside tracked worktrees.
- A dirty integration worktree blocks `patch-dry-run` and `patch-accept` before `cpatch` is invoked.
- A dirty feature worktree is never silently reset, staged or merged.

## 7. Output policy

Default output contains only identifiers, state, phase, message, exit code and log/report paths. Full JSON and logs stay in canonical run directories. `result --verbose --format json` is the explicit detailed form.

## 8. Rollout gate

The implementation remains Springmaster-pilot-only. Propagation to managed projects is blocked until all scenarios in `contracts/governance/tooling/process-operations-contract.json` pass in the real Springmaster workflow and a separate generalization review confirms that no project-specific behavior was introduced.

## 9. Duplicate-safe named starts

Operations such as qualification, export or delivery preparation that must not overlap use a stable, project-neutral singleton key:

```bash
./bin/process-ops.sh run-start \
  --name qualification \
  --singleton-key qualification \
  --cwd . \
  -- ./bin/release-qualify.sh
```

A repeated invocation while the worker is active returns the same `runId` with `startDisposition=REUSED_ACTIVE`. It does not start another process. A terminal run is reused by default; an intentional retry requires `--restart-terminal`.

Singleton locks and pointers live below `CPROCESS_STATE_DIRECTORY/locks` and `CPROCESS_STATE_DIRECTORY/pointers`. They are resolved through the Git common directory and never through a worktree-local `.git` path.

If more than one active worker is discovered for one singleton key, stop and create an incident. Do not overwrite the pointer and do not choose a run by timestamp.

## 10. Qualification order for new process tooling

A process-tooling change is qualified in this order:

1. syntax and contract validators;
2. sealed test-inventory and fixture registration via `test-contracts`;
3. focused process and activation integration tests;
4. full `tooling-selfcheck --no-export`;
5. detached `cpatch` dry-run;
6. explicit review and accept.

Each stage writes its own log and terminal result. A generic outer `FAILED` state without the failed stage and log reference is insufficient evidence for retry or recovery.

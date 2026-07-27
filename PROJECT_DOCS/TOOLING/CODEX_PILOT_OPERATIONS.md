---
documentId: TOOL-CODEX-PILOT-0001
title: Codex Pilot Pre-Cutover Operations Guide
documentType: guide
status: active
authority: informative
scopeLevel: component
scopePaths:
  - springmaster/engineering
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-25
validFrom: 2026-07-25
lastReviewedAt: 2026-07-27
reviewBy: 2027-01-25
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# Codex Pilot Pre-Cutover Operations Guide

## 1. Boundary

This guide covers preparation up to the first Codex calibration invocation. It does not authorize a writable Codex task.

Before cutover, repository changes continue through `bin/cpatch` and `bin/process-ops.sh`.

## 2. External roots

The operator chooses and provisions three absolute, pairwise distinct paths outside the Springmaster repository and Git common directory. The harness has no default and does not create them.

```bash
: "${COCONDO_WORKTREE_ROOT:?set an explicitly authorized existing directory}"
: "${COCONDO_AGENT_RUN_ROOT:?set an explicitly authorized existing directory}"
: "${COCONDO_ARTIFACT_ROOT:?set an explicitly authorized existing directory}"

test -d "${COCONDO_WORKTREE_ROOT}"
test -d "${COCONDO_AGENT_RUN_ROOT}"
test -d "${COCONDO_ARTIFACT_ROOT}"
```

Provisioning those directories is a separate operator action and must state its own effects. The validation command above reads the three configured paths and writes nothing.

## 3. Project readiness

During patch qualification:

```bash
./bin/codex-pilot-ready.sh project --candidate --check
```

After the accepted patch is committed on the clean integration worktree:

```bash
./bin/codex-pilot-ready.sh project --live --check \
  --out-json patches/logs/validation/codex-pilot/codex-project-readiness.json \
  --out-text patches/logs/validation/codex-pilot/codex-project-readiness.txt
```

Expected result before the first Codex invocation:

```text
CODEX_PILOT_READINESS=PROJECT_READY
NEXT_ACTION=CODEX_CALIBRATION
```

`PROJECT_READY` does not mean `PILOT_WRITE_READY`.

## 4. Agent task preparation

A later calibration task is prepared from an immutable Task Contract V2:

```bash
./bin/agent-task.sh validate /absolute/path/to/task.json
./bin/agent-task.sh prepare /absolute/path/to/task.json
./bin/agent-task.sh status <task-id>
```

Preparation creates a detached worktree and run record outside the repository. It does not start Codex.

Before the manually started calibration run, the operator prepares two JSON files below the explicit `COCONDO_ARTIFACT_ROOT`:

- an operator-command-effect declaration according to `operator-command-effect.schema.json`;
- a Codex invocation record according to `codex-invocation-record.schema.json`.

After the invocation has completed, record both immutable inputs:

```bash
./bin/agent-task.sh record-invocation <task-id> \
  --effect "${COCONDO_ARTIFACT_ROOT:?}/<effect-file>.json" \
  --record "${COCONDO_ARTIFACT_ROOT:?}/<invocation-file>.json"
```

The effect declaration must make the operator-visible effects explicit:

```text
READS: prepared task worktree and explicitly declared read-only inputs
WRITES: none for analysis/qualification; prepared task worktree only for implementation
NETWORK: Codex control plane only; agent shell network disabled
REPOSITORY_MUTATION: none for analysis/qualification; detached task worktree only for implementation
DESTRUCTIVE_ACTIONS: none
DIRECTORY_CREATION: declared task paths only
OVERWRITE: declared task paths only
```


The immutable invocation evidence must show the safe non-interactive shape: `codex exec`, `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, `--json`, explicit `--model`, mode-specific `--sandbox` and `--ask-for-approval never`. Linux records identify `linux-bwrap-read-only` or `linux-bwrap-workspace-write`. `--add-dir`, user/profile configuration overrides, full-auto and sandbox-bypass flags are rejected.

The Codex process never receives write authority for the operator home, operator handoff or download directories, integration checkout, Git common directory, external run or artifact roots, other repositories or host temporary directories. A concrete local handoff path is operator configuration, never a portable agent capability. Copying an accepted artifact there is a separate explicit operator action after the Codex task has ended.

Then run postcheck and qualification:

```bash
./bin/agent-task.sh postcheck <task-id>
./bin/agent-task.sh qualify <task-id>
./bin/agent-task.sh status <task-id>
```

The harness still does not integrate the result.

## 5. Deliberate stop at cutover

`agent-task` has no `run-codex`, `commit`, `merge`, `push` or `integrate` command. `record-invocation` records an already completed explicit operator action; it does not execute Codex. The first invocation still requires a separate operator decision after reviewing live project-readiness evidence and the declared command effects.

## 6. Diagnostics

Operational reports intended for upload may be written below `patches/logs/validation/codex-pilot/`. This path is already ignored, excluded from full exports and classified as runtime diagnostics. Long-lived canonical run state remains below the external agent run root.

## 7. Failure handling

- Do not repair a failed task worktree manually before collecting evidence.
- Run `agent-task status` and `postcheck` first.
- Preserve the external run directory.
- Use explicit `cleanup --discard` only after the result is no longer needed.
- A boundary failure returns the pilot to patch-controlled hardening before another Codex attempt.

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
lastReviewedAt: 2026-07-25
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

Configure absolute paths outside the Springmaster repository and Git common directory:

```bash
export COCONDO_WORKTREE_ROOT="$HOME/cocondo-worktrees/springmaster"
export COCONDO_AGENT_RUN_ROOT="$HOME/cocondo-agent-runs/springmaster"
export COCONDO_ARTIFACT_ROOT="$HOME/cocondo-artifacts/springmaster"
```

All three roots are explicit environment inputs in pilot V1. Hidden fallback locations are intentionally not used.

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

A later calibration task is prepared from an immutable JSON task contract:

```bash
./bin/agent-task.sh validate /absolute/path/to/task.json
./bin/agent-task.sh prepare /absolute/path/to/task.json
./bin/agent-task.sh status <task-id>
```

Preparation creates a detached worktree and run record outside the repository. It does not start Codex.

After a manually started calibration run:

```bash
./bin/agent-task.sh postcheck <task-id>
./bin/agent-task.sh qualify <task-id>
./bin/agent-task.sh status <task-id>
```

The harness still does not integrate the result.

## 5. Deliberate stop at cutover

`agent-task` has no `run-codex`, `commit`, `merge`, `push` or `integrate` command. The first Codex invocation is intentionally outside this pre-cutover patch and requires an explicit operator decision after reviewing live project-readiness evidence.

## 6. Diagnostics

Operational reports intended for upload may be written below `patches/logs/validation/codex-pilot/`. This path is already ignored, excluded from full exports and classified as runtime diagnostics. Long-lived canonical run state remains below the external agent run root.

## 7. Failure handling

- Do not repair a failed task worktree manually before collecting evidence.
- Run `agent-task status` and `postcheck` first.
- Preserve the external run directory.
- Use explicit `cleanup --discard` only after the result is no longer needed.
- A boundary failure returns the pilot to patch-controlled hardening before another Codex attempt.

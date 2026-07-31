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
lastReviewedAt: 2026-07-30
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
- process operation, incident, delivery, artifact-authorization, operator-log and operator-workspace paths from `.cocondo/process.env`; all Git-relative process paths resolve through the Git common directory.

Artifact and detached Git-worktree roots are intentionally environmental. They are unrelated to the project-local operator workspace:

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


## 3.1 Central writer workspace lifecycle

The operator workspace is prepared by one canonical operation before every writer: `patch-dry-run`, `patch-accept`, `diagnose`, `incident`, `diagnostic-handoff` and `delivery-prepare`. The root must already exist; `process-ops` never creates it implicitly.

Preparation is fail-closed:

- an active or unresolvable prior workflow blocks cleanup;
- tracked content, root or content symlinks, nested repositories, mount points and special files block cleanup;
- only safe regular files and directories from a terminal prior workflow are removed;
- the root remains present;
- `WORKSPACE.json` records operation ID, writer, subject, removed top-level entry count and the SHA-256 of the deterministic removal list;
- observers (`status`, `watch`, `wait`, `result`, `resume`) never mutate the workspace.

A direct preflight can be requested through the same facade:

```bash
./bin/process-ops.sh workspace-start --operation diagnose --subject <run-id>
```

A terminal run can be packaged as exactly one deterministic ZIP:

```bash
./bin/process-ops.sh diagnostic-handoff <run-id>
```

The next writer removes that handoff. Canonical run state, locks, deliveries and authorization records remain below the Git common directory.

## 3.2 Explicit artifact-root authorization

Configuration selects a candidate path but grants no write authority. The external root must already exist, be a canonical non-symlink directory, remain outside repository, Git common directory, operator home, Downloads and system temporary locations, and expose explicit write/search permissions.

```bash
./bin/process-ops.sh artifact-root-authorize
./bin/process-ops.sh artifact-root-status
```

Authorization writes only the configured Git-common record. It never creates the external root. The record binds project ID, configured path, canonical path, device and inode. A missing, damaged, ambiguous or mismatching record blocks relative artifact resolution before a worker starts.

## 3.3 Typed delivery inventory and preparation

The resolver reads only typed delivery directories, canonical Toolkit run records and canonical acceptance records. Known historical top-level metadata is explicitly classified as `IGNORE_AND_COUNT`; unknown files, links, special entries and invalid JSON are blocking tool errors. A numeric-only `patchId` from the legacy `cocondo.run-record.v1` format reserves its number only when an allowed patch command, a UUID artifact identity and the canonical full patch ID embedded in the artifact filename agree exactly. Exactly one `cocondo.patch-acceptance.v2` record establishes the canonical owner of a local number. Differently named terminal failed run attempts under that owner are retained as `IGNORE_AND_COUNT` while the accepted record reserves the number. Different delivery identities, non-failed runs, unresolved numeric acceptance records and multiple accepted owners remain blocking errors.

```bash
./bin/process-ops.sh delivery-inventory
./bin/process-ops.sh delivery-next-id --name <canonical-name>
./bin/process-ops.sh delivery-prepare --name <canonical-name> --revision <immutable-revision>
```

`delivery-prepare` stores the immutable preparation record below the Git-common delivery state and invokes the central workspace lifecycle. It does not publish an artifact and does not use an external artifact root. A current delivery can exclude itself exactly once through the explicit `--current-delivery` contract.

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


## 11. Tooling-hardening candidate boundary

The implementation described in sections 3.1 through 3.3 is candidate source until canonical dry-run, separate accept and post-accept verification are complete. `PROJECT_READY` and the passing Process Operations Contract do not by themselves authorize Codex calibration or an external artifact write.

## 12. Verbundene fail-fast Abläufe

Preflight, Writer-Start, leichte Beobachtung und terminales Resultat dürfen in einem Block verbunden werden. Jeder Übergang benötigt Exit-Code `0` und eine eindeutige Stage-Evidence. Der Block stoppt am ersten Fehler und startet keinen Folge-Writer.

Dry-run und Accept, Diagnose und Reparatur sowie ein fehlgeschlagener Run und ein Retry bleiben separate Entscheidungen. Vor einem Retry werden der kanonische Runzustand und vorhandene Logs/Evidence ausgewertet; unverändertes blindes Wiederholen ist verboten.

## 13. Terminalschonende Ausgabe

Standardausgaben enthalten nur Operation-/Stage-ID, Status, Phase, Exit-Code und Log-/Report-/Evidence-Pfade. Große JSON-Inventare, vollständige Validator-Logs und unveränderte Statuswiederholungen bleiben in Dateien. Bei einem Fehler wird höchstens ein begrenzter Tail ausgegeben; die vollständige Ursache bleibt über den Logpfad verfügbar.

## 14. Diagnose-Handoff nach Betriebsart

Vor jedem neuen Writer bereinigt der kanonische Workspace-Lifecycle `patches/work`; Observer desselben Workflows bereinigen nicht. Für einen Online-Chat kann bei unklarem Zielzustand genau ein `diagnostic-<operation-id>.zip` erzeugt werden. Codex verwendet `patches/work` nicht und speichert seine Evidence ausschließlich in externen Run-/Artefakt-Roots.

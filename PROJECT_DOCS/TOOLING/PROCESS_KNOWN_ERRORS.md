---
documentId: TOOL-PROCESS-KNOWN-ERRORS-0001
title: Process Operations Known Errors
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

# Process Operations Known Errors

## Absolute path in a checksum sidecar

**Symptom:** `sha256sum -c` searches for a file below a path that exists only on the producing system.

**Cause:** The sidecar contains an absolute path rather than the artifact basename.

**Recovery:** Recreate the sidecar from the artifact directory with `sha256sum "$(basename <artifact>)"`.

**Prevention:** Portable sidecars contain only a basename. Generic tools and contracts reject concrete home, installation and internal service paths.

## Linked worktree treats `.git` as a directory

**Symptom:** Runtime files are created below an invalid path or a tool cannot find shared runs and locks.

**Cause:** In a linked worktree `.git` is a file. Shared state belongs to the Git common directory.

**Recovery:** Resolve `git rev-parse --path-format=absolute --git-common-dir` and use the canonical run record there.

**Prevention:** All configured `.git/...` paths are resolved against the Git common directory.

## Feature worktree confused with integration worktree

**Symptom:** A valid run is blocked by feature changes, or mutation starts against the wrong checkout.

**Cause:** The caller's current directory was treated as the integration checkout.

**Recovery:** Run `process-ops resolve`, verify `integrationRoot`, and query the existing run ID.

**Prevention:** Integration checkout resolution uses the configured branch and `git worktree list --porcelain`.

## Nested detachment

**Symptom:** An outer process is finished while the Toolkit run is still `RUNNING`, or an outer status file remains stale.

**Cause:** `nohup`, `setsid` or another supervisor was wrapped around an already detached `cpatch` or `crun` worker.

**Recovery:** Ignore the outer state, resolve the canonical Toolkit run ID, then use `status`, `resume`, `diagnose` or `incident`.

**Prevention:** There is exactly one worker owner: the Toolkit Run API.

## Interactive `set -e` closes the terminal

**Symptom:** The login shell exits after a status check reports a non-success worker state.

**Cause:** Shell error mode was enabled globally rather than inside a child script.

**Recovery:** Reopen the shell and query the canonical run ID with `process-ops status`.

**Prevention:** Strict shell options belong in scripts or child shells. Process observers return zero by default for readable terminal states.

## Foreign file in Toolkit lock directory

**Symptom:** Doctor fails while parsing an unrelated lock file as a Toolkit lock record.

**Cause:** A manual `flock` file was created inside the Toolkit-owned lock namespace.

**Recovery:** Confirm that no process holds the foreign lock, preserve incident evidence, and remove only that foreign file.

**Prevention:** External locks are forbidden. Toolkit locks are created only by Toolkit code.

## Blind retry after terminal or observer loss

**Symptom:** Duplicate runs, lock contention or unclear acceptance state.

**Cause:** A new run was started without reconciling the existing run ID.

**Recovery:** `process-ops resume <run-id>`, followed by `diagnose` or `incident` when needed.

**Prevention:** Run ID is the recovery handle. Observer loss never authorizes a restart.

## Excessive terminal output

**Symptom:** Terminal instability, truncated scope output or loss of the useful final state.

**Cause:** Full JSON, complete path maps, Maven logs or test streams were written directly to the terminal.

**Recovery:** Read the canonical `logFile` or operation report.

**Prevention:** Compact output is the default; detailed result output requires `--verbose --format json`.

## Runtime files dirty the repository

**Symptom:** Clean-tree guards fail because process state or logs appear as untracked files.

**Cause:** Runtime state was placed below the working tree.

**Recovery:** Preserve needed evidence, remove transient files, then recheck Git status without resetting user changes.

**Prevention:** Canonical process state and incidents live below the Git common directory.

## Duplicate named start overwrites the useful run pointer

**Symptom:** The same detached operation is started twice. A later, immediately failed run replaces the pointer to an earlier active or successful run.

**Cause:** The launcher created a new `crun` record unconditionally and wrote the pointer after every start. `crun --name` is descriptive and is not a singleton guarantee.

**Recovery:** Enumerate matching Toolkit run records, reconcile their states, preserve all logs, and restore the pointer only when exactly one canonical active run exists. Multiple active runs are an incident.

**Prevention:** Use `process-ops run-start --singleton-key <key>`. Active retries reuse the existing run ID. Terminal retries require `--restart-terminal`.

## New tooling test or fixture is not registered

**Symptom:** `tooling-selfcheck` stops at `TEST_CONTRACTS=FINDINGS`; the report contains `UNREGISTERED_TOOLING` or `UNREGISTERED_FIXTURES`.

**Cause:** A new `*-it.sh`, selfcheck, acceptance/regression entrypoint or `src/test/resources/tooling/**` fixture was added without updating the sealed test inventory and, for fixtures, the fixture contract.

**Recovery:** Register the entrypoint in `contracts/governance/testing/test-inventory-baseline.json`, register source fixtures in both the inventory and `test-fixture-contract.json`, align the owning suite in `test-suite-contract.json`, then run `./bin/test-contracts.sh --check all` and `./bin/test-contracts-it.sh` before the full selfcheck.

**Prevention:** Test code, fixture evidence and their machine-readable registrations are one atomic change. A delivery helper must report the failing qualification stage and preserve its log rather than returning only a generic worker failure.

## Git integration fixture inherits operator configuration

**Symptom:** A tooling integration test fails during fixture bootstrap with a path below `.git/refs`, invokes an unexpected hook, requests credentials, or behaves differently between developer machines.

**Cause:** The temporary Git repository inherited system/global Git configuration, templates, hooks or an experimental reference-storage default from the operator environment.

**Recovery:** Preserve the failed stage log, identify the fixture bootstrap step, and rerun only after isolating `HOME`, `XDG_CONFIG_HOME`, system/global Git configuration and the template directory. Do not create missing `.git/refs/**` directories manually in a repository that may use another reference backend.

**Prevention:** Git integration fixtures use an isolated home/config/template environment and select a deterministic reference backend for the fixture repository through Git configuration. Product code continues to use Git commands and must not inspect file-backend internals such as `.git/refs/heads`.

## Generic outer run reports success before patch result

**Symptom:** the observer reports `Generic command completed`, but no `patchId`, validation stage or canonical patch result is present.

**Cause:** a patch command was wrapped in `process-ops run-start` or another generic detached worker.

**Resolution:** start the patch directly with `process-ops patch-dry-run` or `process-ops patch-accept`, then observe the returned canonical patch `runId`.

## Operator workspace cannot be cleaned

**Symptom:** `OPERATOR_WORKSPACE_*` error before a new patch start.

**Cause:** the configured workspace contains an active workflow, tracked content, a symlink, nested repository, mount point or special file.

**Resolution:** inspect the current `WORKSPACE.json` and canonical run status. Do not bypass cleanup guards. Preserve/upload required diagnostics, then remove the blocking unsafe condition explicitly.
## Historical tracked validation evidence blocks observers

**Symptom:** a canonical patch acceptance succeeds, but a subsequent `status`, `watch`, `result` or diagnostic operation fails with `OPERATOR_LOG_TRACKED_CONTENT`.

**Cause:** the process adapter validates the entire shared operator-log root even though that root contains legitimate historical tracked validation evidence.

**Recovery:** query the canonical run directly with `cpatch`, preserve the successful run ID, and apply the compatibility correction. Do not repeat a successful acceptance.

**Prevention:** allow historical tracked sibling evidence below the shared root. Enforce Git-ignore and tracked-content prohibitions only for the exact generated run directory `<operator-log-root>/<patch-id>/<run-id>/`.


## Artifact root is configured but unauthorized

**Symptom:** `ARTIFACT_ROOT_UNAUTHORIZED`, `ARTIFACT_ROOT_AUTHORIZATION_MISMATCH` or `ARTIFACT_ROOT_CONFIGURATION_AMBIGUOUS` occurs before a worker start.

**Cause:** configuration was mistaken for authorization, the canonical path changed, the inode changed, or environment and Git configuration select different roots.

**Recovery:** stop the writer, inspect `process-ops resolve`, provision one existing allowed root, then run `process-ops artifact-root-authorize`. Never create or authorize a root below Home, Downloads, the repository, the Git common directory or system temporary paths.

**Prevention:** every external artifact writer verifies the exact Git-common authorization record before use.

## Delivery inventory contains an untyped entry

**Symptom:** `DELIVERY_INVENTORY_*`, `DELIVERY_RUN_*` or `DELIVERY_*_IDENTITY_CONFLICT` blocks ID calculation.

**Cause:** an unknown top-level file, link, special file, unreadable record, noncanonical patch ID or conflicting typed identity exists. Six-digit text is never a fallback identity source. A numeric-only legacy run is accepted only when `cocondo.run-record.v1`, an allowed patch command, the UUID artifact identity and the canonical patch ID embedded in `metadata.artifactFile` agree exactly. One canonical acceptance record may own the number and demote only differently named terminal failed run attempts to `IGNORE_AND_COUNT`; delivery conflicts, non-failed runs, unresolved numeric acceptance records and multiple accepted owners remain blocking.

**Recovery:** preserve the entry as evidence and classify or correct its producing workflow. For a historical numeric-only run, verify the immutable run record and artifact filename rather than rewriting either. Do not rename it merely to obtain the desired next number and do not provide a patch ID manually.

**Prevention:** use `process-ops delivery-inventory`, `delivery-next-id` and `delivery-prepare`; known historical metadata patterns remain explicit in the Process Operations Contract.

## Tooling selfcheck substep fails

**Symptom:** `SELF_CHECK_FAILED_SUBSTEP=<id>` and `SELF_CHECK_SUBSTEP_RESULT=<id>:<exit-code>` are emitted.

**Cause:** the named integration or audit substep failed. Its complete stdout/stderr is retained in the path announced by `SELF_CHECK_SUBSTEP_LOG`.

**Recovery:** inspect that deterministic log and fix the exact substep. Do not retry from a generic outer failure and do not hide the diagnostic stream.

**Prevention:** critical substeps use the shared selfcheck-observability library and remain registered in the sealed test inventory.

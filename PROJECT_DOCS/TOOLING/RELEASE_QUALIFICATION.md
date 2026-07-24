---
documentType: guide
status: active
scope: release-tooling
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Release Qualification

## Command

From the fixed repository working directory:

```bash
cd /opt/cocondo/springmaster || exit 1
./bin/release-qualify.sh
```

By default the command derives the numeric release version from `PLATFORM_VERSION`, requires a clean committed Working Tree, and runs:

1. `./bin/documentation-gate.sh --check`
2. `mvn -q test`
3. `./bin/tooling-selfcheck.sh --no-export`
4. `./bin/export.sh full --zip`
5. export integrity verification
6. release-manifest generation

The output manifest is written to:

```text
build/releases/<release-version>/release-manifest.json
```

The release command creates no commit, tag or push. The manifest contains the proposed tag `springmaster-v<release-version>` for explicit review and later execution.

## Diagnostic options

`--no-export`, `--skip-maven` and `--skip-tooling` are diagnostic options. A manifest produced with a skipped gate has qualification status `INCOMPLETE` and is not release evidence.

A different release number can be supplied with `--release-version X.Y.Z`; it must match the numeric prefix of the canonical `PLATFORM_VERSION`.

## Patch Toolkit activation precondition

A complete release qualification additionally requires:

```bash
./bin/ctool-doctor --production --format json
./bin/cpatch doctor --production --format json
./bin/patch-toolkit-activation.sh --check
```

The activation check verifies the immutable Toolkit runtime, production ENV contract, Version Closure, canonical `cpatch` entrypoint and disabled legacy mutation. A release candidate with a failed activation check is not releasable, even when Maven tests pass.

## Process operations qualification

Release qualification requires the process operations contract and integration fixture:

```bash
./bin/process-ops-contract.sh --check
./bin/process-ops-it.sh
```

These checks prove dynamic Git path resolution, linked-worktree integration-root selection, clean integration guards, terminal-safe failed status handling, direct `cpatch`/`crun` delegation, bounded output and absence of static environment paths or nested detachment in the operator implementation.

This qualification does not by itself authorize propagation to managed projects. That rollout remains blocked until the real Springmaster pilot scenarios are recorded as complete in a later evidence update.

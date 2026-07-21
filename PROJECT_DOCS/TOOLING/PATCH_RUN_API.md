---
documentType: guide
status: active
scope: patch-runtime
owner: springmaster-maintainers
validFrom: 2026-07-21
supersedes: none
---
# Patch Run API

## Purpose

The Patch Run API is the canonical local interface for starting, observing, waiting for, diagnosing and reconciling Springmaster patch operations. It replaces ad-hoc `find`, `pgrep`, `tail`, `awk` and summary-selection shell blocks.

Git remains the durable repository truth. Runtime run records are operational evidence only; a successful acceptance is durable only when its qualified Git state, applied archive and canonical acceptance evidence agree.

## Public commands

```bash
./bin/patch.sh status <run-id|patch-id|patch-number|latest> [--format human|env|json]
./bin/patch.sh watch <run-id|patch-id|patch-number|latest> [--interval <seconds>] [--timeout <seconds>]
./bin/patch.sh wait <run-id|patch-id|patch-number|latest> [--interval <seconds>] [--timeout <seconds>]
./bin/patch.sh result <run-id|patch-id|patch-number|latest> [--format human|env|json]
./bin/patch.sh diagnose <run-id|patch-id|patch-number|latest> [--output <file>]
./bin/patch.sh doctor
```

`status` is a one-shot read. `watch` prints only when status or phase changes. `wait` stays silent until a terminal state and returns a stable exit code. `result` is intended for scripts. `diagnose` writes a bounded report instead of streaming large logs to the terminal. `doctor` checks Git, locks, run records, archives and acceptance evidence for contradictions.

## Canonical acceptance flow

```bash
cd /opt/cocondo/springmaster || exit 1

./bin/patch.sh live-baseline /home/cb/Downloads/<patch>.zip
./bin/patch.sh apply --dry-run /home/cb/Downloads/<patch>.zip
./bin/patch.sh artifact-preflight /home/cb/Downloads/<patch>.zip --no-export

./bin/patch.sh accept /home/cb/Downloads/<patch>.zip \
  --background \
  --wait-for-lock \
  --no-export \
  --commit
```

The start command prints a `RUN_ID`. Observe that exact run:

```bash
./bin/patch.sh watch <run-id>
./bin/patch.sh result <run-id>
```

A terminal or SSH session may close after the background start. The run continues independently. Do not start another acceptance merely because the original terminal is gone.

## Lock waiting versus run waiting

`--wait-for-lock` controls only acquisition of the repository write lock. It does not wait for a background acceptance to finish.

```bash
./bin/patch.sh accept <patch.zip> --background --wait-for-lock --commit
./bin/patch.sh wait <run-id>
```

The historical `--wait` option remains a compatibility alias for `--wait-for-lock`; generated commands use the explicit name.

## Idempotent start contract

Before creating a background process, `accept` resolves artifact, patch, archive, acceptance and Git state.

| Existing state | Result |
|---|---|
| Same artifact is already committed and accepted | `ALREADY_APPLIED`, exit 0, no process |
| Same artifact has an active run | `ALREADY_RUNNING`, existing run ID, no process |
| Same patch ID refers to another artifact | fail closed |
| Same artifact ID refers to another patch ID | fail closed |
| Recorded commit is missing from Git | fail closed; run `doctor` |
| Earlier failed run, unchanged baseline, unchanged artifact | explicit retry is permitted |
| Patch content changed | new patch ID and new artifact ID are required |

The latest timestamped summary is never sufficient to decide whether a patch is accepted. Canonical acceptance and Git history take precedence over later redundant failed attempts.

## Run states

```text
RUNNING
WAITING_FOR_LOCK
SUCCESS
APPLIED
ALREADY_RUNNING
ALREADY_APPLIED
FAILED
BUSY
STALE
ABORTED
UNKNOWN
```

`APPLIED` is the canonical aggregate state for a committed accepted patch. A later failed redundant run does not downgrade it.

## Runtime records

Temporary run state is stored below:

```text
patches/runtime/patch-runs/<run-id>/run.json
patches/runtime/patch-runs/by-patch/<patch-id>.json
```

A run record contains at least:

- run ID, command, patch ID, artifact ID and patch SHA-256;
- baseline Git HEAD;
- PID, process group, host and timestamps;
- current status and phase;
- summary and log directory;
- commit and push status when known.

Updates use write-to-temporary-file plus atomic rename. Runtime records are ignored by Git and are not product truth.

## Durable acceptance evidence

A successful acceptance publishes a separate canonical directory:

```text
patches/logs/accept/<patch-id>/accepted.json
patches/logs/accept/<patch-id>/SUMMARY.txt
patches/logs/accept/<patch-id>/child-accept/
```

Individual attempts remain in timestamped run directories. A failed retry must not overwrite `accepted.json` or downgrade the canonical success summary.

`verify` writes to:

```text
patches/logs/validation/<run-id>/
```

Revalidation evidence is intentionally separate from acceptance evidence.

## Git transaction contract

For an effective acceptance:

1. the live Working Tree and index must be clean;
2. the live baseline HEAD is captured before validation;
3. the patch is validated in a detached Git worktree;
4. the qualified child commit must have the captured baseline as its direct parent;
5. patch-log paths, child commit paths and live transfer paths must be exactly equal;
6. only patch paths are staged; `git add .` is forbidden;
7. archive and acceptance data are staged before live transfer;
8. the qualified commit is cherry-picked into the live branch;
9. transfer failure before finalization compensates to the captured baseline and removes staged live evidence;
10. failure after commit, archive and canonical evidence are durable is recorded as a post-accept warning and does not invalidate local acceptance;
11. push status is separate from local acceptance status and never occurs without `--push`.

Without `--commit`, legacy review mode remains available and is reported as `VALIDATED_NOT_COMMITTED`. The normal durable workflow uses `--commit`.

## Efficient whitespace policy

Whitespace checks are correctness checks, not formatting passes. They are deliberately patch-scoped:

1. after apply: `git diff --check -- <patch paths>`;
2. before the qualified commit: `git diff --cached --check -- <patch paths>`;
3. after the child commit: `git show --check <qualified commit>`.

New untracked files are exposed to the first check with intent-to-add inside the isolated worktree. The engine does not scan or reformat unrelated repository files and does not run repeated full-repository whitespace checks. Trailing whitespace and conflict markers fail acceptance with an exact child step; line-ending or formatting normalization is never performed implicitly.

## Terminal-safe operating rules

- Do not set `set -euo pipefail` in a long-lived interactive shell. Use it inside scripts or subshells.
- Do not monitor with `tail -F` or print complete Maven logs in the terminal.
- Do not search for the newest summary as a substitute for `status`.
- Do not infer liveness from a PID alone; the run resolver also checks run metadata and process state.
- Do not restart before `status <patch-id>` and `doctor` have ruled out `APPLIED` and `RUNNING`.
- Use `diagnose` for bounded failure evidence.

## Exit-code contract

| Command result | Exit code |
|---|---:|
| success, applied or already applied | 0 |
| active/running for one-shot result | 3 |
| failed, stale, aborted or contradiction | 1 |
| invalid invocation or unknown target | 2 |
| wait timeout | 4 |

Human output stays compact. Automation should prefer `--format json` or `--format env` and the documented exit codes.

## Required regression coverage

The normal tooling selfcheck includes `bin/patch-run-api-it.sh`. It covers:

- background acceptance and terminal-independent waiting;
- canonical applied resolution;
- duplicate-start idempotency;
- verify/acceptance evidence separation;
- exact child failure propagation;
- patch-scoped whitespace rejection without live mutation;
- doctor and result behavior.

`bin/patch-transactional-accept-it.sh` additionally proves failed/successful worktree transactions, bounded test log names, path parity and Git transfer behavior.

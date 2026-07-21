---
documentType: guide
status: active
scope: patch-recovery
owner: springmaster-maintainers
validFrom: 2026-07-21
supersedes: none
---
# Failed Accept Recovery

## First determine the canonical state

A timestamped failed run is not proof that the patch is unaccepted. Before rollback or retry:

```bash
cd /opt/cocondo/springmaster || exit 1
./bin/patch.sh status <patch-id>
./bin/patch.sh doctor
```

Interpretation:

- `APPLIED` or `ALREADY_APPLIED`: do not retry or roll back merely because a later redundant run failed;
- `RUNNING` or `ALREADY_RUNNING`: observe the existing run with `watch` or `wait`;
- `FAILED` with no live mutation: diagnose; no rollback is required;
- archive applied, acceptance failed and Git commit absent: inconsistent live state; controlled rollback or reconciliation is required;
- `STALE`: run `doctor`, inspect the bounded diagnostic and reconcile before a new start.

Use:

```bash
./bin/patch.sh diagnose <run-id|patch-id>
```

Do not select the newest summary manually and do not infer acceptance from PID state alone.

## Transactional failure invariant

A failed isolated acceptance must leave:

- live `HEAD` unchanged;
- live Working Tree and index unchanged;
- no live applied archive;
- no canonical successful acceptance evidence.

Such a run is diagnostic history and can be retried with the same immutable artifact only when the baseline and artifact are unchanged. If patch content changes, create a new patch ID and artifact ID.

## Invalid legacy or partial state

The following state is invalid unless immutable historical closure reconciliation is registered:

```text
patch archive status = applied
canonical acceptance  = absent or FAILED
Git commit             = absent
```

Recovery:

```bash
./bin/patch.sh rollback <failed-patch-id>
./bin/patch-state-audit.sh --check --require-clean
```

Rollback is complete only when the archive reports `rolled_back`, `ROLLBACK_DONE` exists, failed evidence remains preserved, Git is clean and no later patch depends on the failed live state.

A historical patch later closed by an independently qualified successor commit must be declared in `contracts/governance/patch-state-reconciliations.json`. The registry records why the payload belongs to the committed baseline; it does not rewrite the historical failed run.

## Post-finalization warning

When the qualified Git commit, applied archive and canonical acceptance evidence are already durable, a later reporting or push problem is a post-accept warning. Local acceptance remains successful. Resolve push or reporting separately; do not reset a valid local commit automatically.

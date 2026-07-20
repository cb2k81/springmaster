---
documentType: guide
status: active
scope: patch-recovery
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Failed Accept Recovery

## Invariant

A patch is not accepted merely because its payload was copied into the repository. Acceptance requires successful validation and, when `--commit` is requested, a durable Git commit.

The following state is invalid unless an immutable historical closure reconciliation is registered:

```text
patch archive status = applied
accept summary        = FAILED
Git commit             = absent
```

Before another patch is accepted, the failed patch must be rolled back. The archive and failed acceptance evidence remain preserved; history is not rewritten.

A narrowly scoped exception exists for historical patches that were later closed by an independently qualified successor commit. Such a case must be declared in `contracts/governance/patch-state-reconciliations.json`, bind the observed archive and acceptance states, and reference immutable repository evidence. The registry does not convert the historical FAILED summary into SUCCESS; it records why the applied payload is nevertheless part of the committed baseline.

## Recovery sequence

```bash
cd /opt/cocondo/springmaster || exit 1
./bin/patch.sh rollback <failed-patch-id>
./bin/patch-state-audit.sh --check --require-clean
```

A rollback is complete only when:

- `ROLLBACK_DONE` exists in the archive;
- `patch-log.json` reports `rolled_back`;
- the failed acceptance summary remains available;
- the Git Working Tree is clean;
- no later patch depends on the failed live state.

## Machine-readable audit

`bin/patch-state-audit.sh` compares archive status, rollback markers, acceptance summaries and explicit historical reconciliation evidence. `--require-clean` additionally rejects a dirty Git Working Tree. Tooling selfchecks use the archive invariants without requiring a clean tree because an accepted patch is validated before its commit.

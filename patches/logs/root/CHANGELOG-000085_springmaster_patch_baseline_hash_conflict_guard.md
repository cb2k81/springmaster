# 000085 springmaster patch baseline hash conflict guard

## Summary

- Adds optional manifest-level baseline hash preconditions for patch operations.
- Rejects stale patches with `BASELINE_CONFLICT` during `apply --dry-run` and mutating `apply`.
- Supports `expectedBeforeSha256`, `baseline.expectedBeforeSha256` and `baseline.expectedBefore` manifest forms.
- Keeps already-applied/no-op reaccepts possible by enforcing preconditions only when a patch would make effective changes.
- Extends the patch-system integration fixture with a stale baseline conflict scenario.
- Documents hash preconditions as complement to project-wide write locks.
- Excludes `patches/runtime/**` from Git and text exports so stale runtime locks are not shipped as baseline content.
- Bumps `PLATFORM_TOOLING_VERSION` to `0.3.14` and updates `PLATFORM_STATE_PATCH`.

## Validation

- `python3 -m py_compile bin/patch.py`
- `bash -n bin/*.sh bin/lib/core/*.sh bin/lib/dbtool/*.sh`
- Targeted fixture check for `BASELINE_CONFLICT`, successful dry-run after restoring the expected file state, and no-op dry-run after apply.

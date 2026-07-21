---
documentType: concept
status: active
scope: patch-acceptance
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Transactional Patch Acceptance

## Boundary

`patch.sh accept` validates an effective patch in a detached Git worktree created from the current live `HEAD`.

The isolated worktree performs:

1. live-baseline validation against the detached baseline;
2. patch dry-run and apply;
3. tooling selfcheck;
4. selected tests;
5. full test when required;
6. optional export;
7. a patch-scoped Git commit.

The live repository is not modified during these steps.

## Commit transfer

Only a successful worktree commit whose direct parent equals the original live `HEAD` may be transferred. With `--commit`, the qualified commit is cherry-picked into the live branch. Without `--commit`, the same qualified tree is transferred with `cherry-pick --no-commit` for explicit review.

Patch archive and acceptance evidence are copied to the live repository only after the transfer succeeds.

## Failure invariant

When any worktree step fails:

- live `HEAD` is unchanged;
- the live Working Tree is unchanged;
- no live patch archive is created;
- `show latest` remains the last previously accepted patch;
- failed child logs remain available under the parent acceptance log.

`bin/patch-transactional-accept-it.sh` proves both a failing and a successful transaction against an isolated fixture repository.

## Validation environment isolation

The control variables used by the parent/child transaction protocol are private to the patch engine. They are removed before tooling checks, configured tests, full tests, or exports are started:

```text
PATCH_ACCEPT_WORKTREE_CHILD
PATCH_ACCEPT_LOG_DIR
PATCH_BACKGROUND_CHILD
```

This prevents nested patch fixtures and application tests from accidentally bypassing the public transactional boundary merely because they execute inside an outer validation worktree. The transaction child itself retains its marker; only its validation subprocesses receive the sanitized environment.

`bin/patch-transactional-accept-it.sh` verifies this boundary from both a normal shell and an inherited transaction-child environment.

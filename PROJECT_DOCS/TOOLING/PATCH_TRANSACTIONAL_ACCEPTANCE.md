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

## Bounded validation log names

Configured test selectors are external input and must not become unbounded filesystem names. Selector logs therefore follow these rules:

- the basename is deterministic and at most 120 UTF-8 bytes;
- a short unique selector keeps its readable sanitized basename;
- a long selector or a sanitized-name collision receives a truncated basename with a 12-hex SHA-256 prefix;
- repeated collisions receive a deterministic numeric disambiguator;
- the full original selector remains visible in the log header and command line;
- filename bounding changes diagnostics only and does not change the executed selector, patch scope, apply semantics or commit semantics.

`bin/patch-transactional-accept-it.sh` covers the long selector that previously exceeded the common 255-byte filename limit and also covers two selectors whose sanitized forms collide.

## Technical-debt checkpoint

This correction closes the unbounded validation-log basename defect without changing product code or target-delivery behavior. No new runtime dependency, artifact format or mutable repository state is introduced. The tooling component has patch-level semantic impact; the version policy applies its increment in the release-closing patch rather than in this intermediate change.

The outer transactional summary still reports a child failure as `worktree-validation`; detailed child diagnostics remain under `child-accept/`. Improving first-root-cause propagation is a separate, non-blocking diagnostic enhancement and is not hidden by this change.

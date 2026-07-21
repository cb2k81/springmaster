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

## Run identity and canonical evidence since 000164

Every acceptance attempt receives an immutable run ID and a temporary `run.json`. A successful attempt is published separately as canonical evidence under `patches/logs/accept/<patch-id>/accepted.json`. Timestamped failed or redundant attempts remain diagnostic history but cannot downgrade a committed accepted patch.

Revalidation is separate: `verify` writes under `patches/logs/validation/<run-id>/` and never overwrites canonical acceptance evidence.

## Exact Git path parity

The transaction compares three path sets:

1. effective paths from the child patch archive `patch-log.json`;
2. changed paths in the qualified child commit;
3. changed paths after transfer to the live repository.

All three sets must be exactly equal. The child commit must have the captured live baseline as direct parent. Only patch paths are staged; broad staging such as `git add .` remains prohibited.

Archive and child acceptance evidence are staged before live cherry-pick. A failure before transaction finalization resets the live repository to the captured baseline and removes partially transferred evidence. After qualified commit, archive and canonical evidence are durable, later reporting or push failures are recorded as post-accept warnings and do not invalidate local acceptance. Push status remains independent and requires explicit `--push`.

## Patch-scoped whitespace validation

Whitespace validation is intentionally efficient and path-scoped:

- applied patch paths: `git diff --check -- <paths>`;
- staged patch paths: `git diff --cached --check -- <paths>`;
- qualified commit: `git show --check`.

Intent-to-add is used only in the isolated child so new files are visible to `git diff --check`. The engine does not reformat files, normalize line endings or scan unrelated repository content. Whitespace failure is propagated to the parent as the exact child step and leaves the live repository unchanged.

## Resolved diagnostic debt

The parent summary no longer collapses every child validation failure to `worktree-validation`. It carries the exact child failure step, phase, root-cause candidate and relevant log path. `patch.sh diagnose` produces bounded evidence, while `status`, `watch`, `wait` and `result` remove the need for ad-hoc terminal polling.
## Project-local start handoff since 000167

The detached background child is started without any external pointer or log file. Human callers use `accept ... --watch`; automation captures `--format env` or `--format json` directly and extracts the run ID in memory. `Downloads` remains an ingress for immutable patch ZIPs and is never a runtime state directory.

The parent writes `invocation.json` before spawning the child. The record is atomic, contains only the patch filename and SHA-256 plus requested options, and excludes the absolute source path. Canonical acceptance publication preserves this file. Parent-only options (`--format`, `--watch`, `--watch-interval`, `--watch-timeout`) are removed from the child invocation so no recursive observer is created. Empty run references are rejected before path resolution.

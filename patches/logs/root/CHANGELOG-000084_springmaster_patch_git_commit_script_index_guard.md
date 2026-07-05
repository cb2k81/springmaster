# 000084 springmaster patch git commit script index guard

## Summary

Hardens the generated patch commit helper so it cannot accidentally include pre-staged files from unrelated work.

## Changes

- Adds a generated Git index guard to `git-commit.sh` before patch-specific staging.
- Fails with `GIT_INDEX_DIRTY` when the Git index already contains staged files outside the patch file list.
- Keeps the commit helper limited to the concrete patch file list and continues to avoid `git add .`.
- Extends the patch-system fixture test with a staged foreign-file scenario.
- Documents the Git index guard in the patch workflow and validation policy.
- Advances the Springmaster tooling state marker.

## Validation

- `python3 -m py_compile ./bin/patch.py`
- `bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh`
- `PATCH_SYSTEM_IT_WITH_BACKGROUND=0 ./bin/patch-system-it.sh`

## Notes

This patch does not rewrite existing Git history. It prevents future generated commit helpers from committing files that were already staged before the helper was started.

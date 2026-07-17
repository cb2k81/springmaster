# 000132_springmaster_patch_artifact_preflight_output_collision_repair

## Scope

tooling

## Summary

* Allocate implicit Artifact-Preflight evidence directories atomically with `tempfile.mkdtemp`.
* Preserve readable timestamp and patch identity while adding a collision-resistant suffix.
* Keep explicit `--output` directories exclusive and fail-closed.
* Add a fixed-timestamp allocator regression and two immediate valid preflight invocations.
* Preserve the exact `PATCH_ARTIFACT_WORKTREE_DIRTY` negative contract.

## Qualification contract

* `python3 -m py_compile bin/patch-artifact-preflight.py`
* `bash -n bin/patch-artifact-preflight-it.sh`
* `SpringmasterPatchArtifactPreflightTest`
* complete Springmaster Maven test
* ZBM Core delivery integration with real Maven in an isolated clone
* Tooling Selfcheck
* exact changed-path and live ZBM non-mutation gates
* exactly one final Full-v2 export with integrity verification

The host Resume runner is authoritative for Maven, ZBM delivery, final export and joint `000131`/`000132` closure evidence.

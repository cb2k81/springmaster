# 000104_springmaster_patch_baseline_live_hash_preflight_guard

## Scope

tooling

## Summary

* Add non-mutating `patch.sh live-baseline <patch.zip>` command.
* Run the live baseline preflight automatically at the beginning of `accept`.
* Require complete `baseline.expectedBeforeSha256` coverage for all operations in the live-baseline guard.
* Add explicit error classes for missing, incomplete, unsupported and mismatching live baseline hashes.
* Update the patch-system integration fixture to create identity-valid fixture patches and cover live-baseline success and mismatch cases.
* Document the new guard in the tooling standards.

## Validation

* `python3 -m py_compile bin/patch.py`
* `bash -n bin/patch-system-it.sh`
* `bash -n bin/patch-system-it.sh`
* runner smoke fixture for `live-baseline` success and mismatch
* `./bin/tooling-selfcheck.sh --no-export`
* `git diff --check`
* `./bin/export.sh full --zip`

# 000026 springmaster platform update patch generation plan

## Summary

Adds the first non-invasive target patch ZIP generation mode to `bin/platform-update.sh`.

## Changes

* Adds `platform-update generate <target> --profile <profile> [--dry-run]`.
* Generates target-local plan patch ZIPs under `platform/update/generated/**`.
* Keeps target projects untouched; no writes to `TARGET_PATH`.
* Documents the plan-only generated patch format.
* Updates Platform-Update version to `0.2.0` and overall Foundation version to `0.8.0-foundation`.

## Validation

Required validation: patch accept, shell syntax, Python compile, tooling selfcheck, platform-update dry-run/generate smoke test, full export.

No Maven test is required because no Java code, tests or build configuration are changed.

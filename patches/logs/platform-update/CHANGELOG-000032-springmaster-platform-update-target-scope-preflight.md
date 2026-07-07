# 000032 - springmaster platform update target scope preflight

## Summary

Adds a non-invasive target-scope preflight to the Springmaster platform-update workflow.

## Changes

* Adds `platform-update preflight <target> --zip <generated-patch.zip>`.
* Makes `platform-update apply-plan` run target preflight before writing apply instructions.
* Stores target dry-run logs under `platform/update/manifests/*_preflight.log`.
* Documents the target-scope preflight workflow.
* Updates platform-update version metadata.

## Validation

* Shell syntax check for `bin/platform-update.sh`.
* No Java code and no build configuration changed; no Maven test required.

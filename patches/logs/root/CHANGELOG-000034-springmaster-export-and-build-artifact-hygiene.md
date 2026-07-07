# 000034 - Springmaster Export and Build Artifact Hygiene

## Scope

Springmaster-only export and artifact hygiene. No target project changes.

## Changes

* Hardened `export.config.json` so regular exports exclude:
  * `.git/**`
  * `platform/update/generated/**`
  * `platform/update/manifests/**`
* Removed the broad nested `.env.example` unexclude that could re-include files below `patches/archives/**`.
* Added a root `.gitignore` for generated local artifacts, patch archives, exports and temporary files.
* Added `PROJECT_DOCS/TOOLING/EXPORT_ARTIFACT_HYGIENE.md`.
* Updated Export Tool and Platform Update documentation to distinguish clean baselines from operations/forensic artifacts.
* Updated version metadata to `PLATFORM_VERSION=0.12.1-foundation` and `PLATFORM_TOOLING_VERSION=0.3.7`.

## Validation expectation

Documentation/configuration-only tooling hygiene patch. No Maven test is required.

After apply, a Full-ZIP export should not contain `.git/**`, `target/**`, `build/**`, `tmp/**`, `exports/**`, `patches/archives/**`, `platform/update/generated/**` or `platform/update/manifests/**`.

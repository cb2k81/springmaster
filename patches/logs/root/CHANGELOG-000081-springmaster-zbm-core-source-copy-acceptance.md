# 000081_springmaster_zbm_core_source_copy_acceptance

## Summary

Prepare and document the first controlled Core source-copy acceptance for the generated ZBM backend.

## Changes

* `platform-update generate` now writes generated review documents to scope-compatible paths for Core profiles.
* Core and Core-runtime generated patches synthesize target-local `pom.xml` Core dependencies instead of copying the Springmaster master `pom.xml`.
* The ZBM Core Source-Copy Acceptance is documented as the next bridge before fachlicher service-slice generation.
* Platform version advances to `0.13.42-foundation` and Platform-Update version to `0.8.2`.

## Validation

* Shell syntax validation required for `bin/platform-update.sh`.
* No Maven test is required for Springmaster because no Java code is changed.
* ZBM Core source-copy acceptance is executed by the separate target runner.

# 000074 - springmaster_catalog_demo_candidate_slice_alignment

## Scope

`root`

## Type

Code/tooling + documentation alignment.

## Summary

Aligns the report-only gate seed with the CatalogItem candidate-reference-slice evidence created in 000072 and forensically reviewed in 000073.

## Changes

- Added machine-readable CatalogItem candidate evidence JSON with schema `springmaster.catalog-demo.candidate-evidence.v1`.
- Extended the report-only gate runner to read candidate evidence and expose it in `input-manifest.json` as `catalogDemoEvidence`.
- Updated G5 readiness detection so current candidate evidence takes precedence over historical `legacy-demo-seed` wording in the readiness plan.
- Updated G4 security wording to classify deferred security without referring to the current code as legacy seed.
- Updated gate regression, selfcheck and Maven profile test expectations.
- Documented the new expected findings baseline: `8` findings, `0` G5 manual-review findings.
- Advanced platform version to `0.13.35-foundation` and tooling version to `0.3.10`.

## Validation expectation

- Shell/Python syntax check.
- Report-only gate selfcheck.
- Report-only gate regression.
- Gate smoke with expected `8` findings.
- `mvn -q test`.
- `mvn -q -Pspringmaster-gates-report test`.
- Full ZIP export and export hygiene check.

## Non-goals

- No target-project scans.
- No strict gates.
- No target-project updates.
- No canonical promotion.
- No Demo Java implementation change.
- No Core, Template or Platform-Update code change.

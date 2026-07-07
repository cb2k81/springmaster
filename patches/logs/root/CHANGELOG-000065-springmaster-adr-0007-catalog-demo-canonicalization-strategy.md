# Changelog 000065 - Springmaster ADR-0007 Catalog-demo Canonicalization Strategy

## Scope

`root`

## Type

Documentation-only.

## Summary

Accepted ADR-0007 for Catalog-demo canonicalization. The patch defines the distinction between existing seed code, candidate reference slices and canonical reference slices before Catalog-demo is used as the Springmaster reference implementation or as basis for target-project comparison.

## Added

- `PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md`

## Changed

- ADR index and ADR governance now list ADR-0007 as accepted.
- ADR gap backlog marks Catalog-demo canonicalization as ADR-backed while preserving strict-gate evidence requirements.
- Catalog-demo readiness plan classifies the existing CatalogItem implementation as `legacy-demo-seed`.
- Demo README documents that future implementation patches must explicitly distinguish candidate and canonical slices.
- Gate concept allows report-only G5 readiness diagnostics to reference ADR-0007.
- Standards review and implementation plan record the resolved P0 Catalog-demo canonicalization ADR gap.
- Version policy and `platform.env` advance the foundation state to `0.13.26-foundation`.

## Validation

No Maven test is required because the patch changes documentation and version metadata only. It does not change Java code, Maven configuration, shell tooling, templates, demo implementation or target-project files.

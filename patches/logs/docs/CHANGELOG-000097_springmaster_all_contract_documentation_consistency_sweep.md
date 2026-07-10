# Changelog: 000097_springmaster_all_contract_documentation_consistency_sweep

Scope: docs

## Summary

Align historical Springmaster documentation with the current `/all` contract introduced by `000091` and demonstrated by CatalogItem in `000092`/`000094`.

## Changes

- Clarified that only ambiguous, selector-like, undocumented or silently capped `/all` endpoints are non-canonical.
- Clarified that explicit complete-result-set `/all` endpoints are canonical for frontend export, backend batch and integration consumers.
- Updated ADR-gap, standards, readiness, candidate-plan, forensic-review and report-only gate wording.
- Preserved Catalog-demo status as `candidate-reference-slice`, not `canonical-reference-slice`.

## Verification

- Documentation-only patch.
- `git diff --check` required.
- Patch dry-run/apply and full ZIP export required.

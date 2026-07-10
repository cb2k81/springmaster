# 000098 springmaster count response contract candidate

Scope: docs

## Summary

Defines the candidate API contract for optional count-only endpoints.

## Changes

- Adds `PROJECT_DOCS/STANDARDS/API/API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md`.
- Narrows canonical endpoint shapes to `GET /api/<domain>/<resources>/count` and `POST /api/<domain>/<resources>/search/count`.
- Defines the candidate response shape `{ "totalElements": 0 }`.
- Clarifies that count endpoints reuse list/export filters, security and data-scope predicates.
- Clarifies that pagination and sorting are not count semantics.
- Updates API standard, gate and ADR-gap documentation.
- Records that Core `CountResponseDTO` and CatalogItem count behavior evidence are follow-up work.

## Verification

- Patch identity preflight.
- Patch dry-run.
- Patch apply.
- `git diff --check`.
- Documentation grep for count response contract references.
- Full export.

No Maven test is required because this is documentation-only.

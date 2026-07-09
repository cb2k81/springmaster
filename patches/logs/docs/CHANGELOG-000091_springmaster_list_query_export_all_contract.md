# 000091_springmaster_list_query_export_all_contract

## Scope

Documentation-only API standards patch.

## Purpose

This patch rebases the list/query complete-result-set contract onto the Springmaster baseline after `000090_springmaster_patch_command_generation_contract`.

It accepts `/all` as canonical only for explicit complete result-set retrieval used by frontend export, backend batch jobs and service-to-service integration consumers. Ambiguous, selector-like, undocumented or silently capped `/all` endpoints remain non-canonical findings.

## Changed documents

- `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md`
- `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md`
- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_DEFINITION_BACKLOG.md`
- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_RESULT_SET_EXPORT_ALL_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/LIST_FILTER_QUERY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/README.md`

## Contract summary

- Paged management lists remain `GET /api/<domain>/<resources>`.
- Complete result-set access is `GET /api/<domain>/<resources>/all`.
- Complex search complete access is `POST /api/<domain>/<resources>/search/all`.
- `/all` shares filters, sorting, security and data-scope predicates with the paged query.
- `/all` does not expose `page` or `size` as public pagination controls and must not silently truncate results.
- Empty `/all` results return `200 OK` with `[]`.
- Count remains `PagedResponseDTO.totalElements`; optional count-only endpoints are documented but not mandatory.

## Validation expectation

Documentation-only patch: patch dry-run, patch apply, patch latest and full export are sufficient. No Maven build/test is required.

# Changelog 000048 - springmaster_api_error_contract_standard

## Scope

`root`

## Type

Documentation-only.

## Summary

This patch defines the generic Springmaster API error contract before Catalog-demo becomes the canonical reference API.

## Added

- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`
  - canonical Springmaster error response body,
  - violation item contract,
  - baseline `errorType` vocabulary,
  - status-code mapping,
  - boundary between request validation and domain errors,
  - implementation expectations,
  - OpenAPI expectations,
  - Catalog-demo readiness rule,
  - future gate candidates.

## Changed

- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md`
  - points endpoint failure responses to the new error contract.
- `PROJECT_DOCS/STANDARDS/API/README.md`
  - registers the API error contract standard and updates Catalog-demo expectations.
- `PROJECT_DOCS/STANDARDS/README.md`
  - documents the standardization step and the next DTO/validation priority.
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`
  - records the version increment and rationale.
- `platform/versions/platform.env`
  - updates `PLATFORM_VERSION` to `0.13.9-foundation`.
  - updates `PLATFORM_STATE_PATCH` to `000048_springmaster_api_error_contract_standard`.

## Not changed

- No Java code.
- No Maven build files.
- No Springmaster tooling scripts.
- No templates.
- No demo implementation.
- No IDM, Personnel, Contacts, Orders or other target projects.

## Validation expectation

No `mvn test` is required because this is a documentation-only patch.

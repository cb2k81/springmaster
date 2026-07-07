# Changelog 000046 - Springmaster API Endpoint Contract Standard

## Scope

Documentation-only Springmaster root patch.

## Added

- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md`
  - defines canonical Springmaster endpoint contracts for new reference APIs,
  - standardizes paged list, options/reference data, detail, alternate lookup, create, update, single delete, delete-multiple, state-transition command and complex search patterns,
  - separates public endpoint vocabulary from Java repository/service vocabulary,
  - prohibits public `findOne`, `findFirst` and `findLast` management API vocabulary unless a future ADR explicitly allows it for a special integration API,
  - defines status-code expectations and future OpenAPI/MockMvc/reflection/ArchUnit gate targets.

## Changed

- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_DEFINITION_BACKLOG.md`
  - records which backlog items are resolved into the 000046 baseline standard,
  - keeps gate implementation, structured error standard, Java interfaces and target-project comparison as deferred follow-up work.
- `PROJECT_DOCS/STANDARDS/API/README.md`
  - adds the endpoint contract standard to the API standards index,
  - aligns the Catalog-demo expectation with the new canonical endpoint rules.
- `PROJECT_DOCS/STANDARDS/README.md`
  - records the endpoint contract standard in the standards overview.
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`
  - adds the 000046 version-policy entry.
- `platform/versions/platform.env`
  - sets `PLATFORM_VERSION=0.13.7-foundation`,
  - sets `PLATFORM_STATE_PATCH=000046_springmaster_api_endpoint_contract_standard`.

## Validation

No Java code, shell tooling, Maven build files, templates, demo implementation or target-update payloads were changed.

`mvn test` is not required for this documentation-only patch.

## Target-project boundary

No IDM, Personnel, Contacts, Orders or other target-project files are changed.

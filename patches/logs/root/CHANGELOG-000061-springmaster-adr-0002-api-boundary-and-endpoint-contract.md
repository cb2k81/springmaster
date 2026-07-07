# Changelog: 000061 Springmaster ADR-0002 API Boundary and Endpoint Contract

## Scope

Documentation-only root patch.

## Added

- `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md`
  - accepts the API boundary and endpoint contract as a Springmaster architecture decision.

## Changed

- `PROJECT_DOCS/ADR/README.md`
  - adds ADR-0002 to accepted ADRs;
  - removes ADR-0002 from the planned backlog;
  - documents the gate implication after acceptance.
- `PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md`
  - marks ADR-0002 as accepted;
  - removes ADR-0002 from the near-term execution queue;
  - records remaining deferrals for OpenAPI naming, ADR-0005 and ADR-0006.
- `PROJECT_DOCS/ADR/ADR_GOVERNANCE_AND_BACKLOG_ALIGNMENT.md`
  - records ADR-0002 acceptance without changing the general gate-blocking rule.
- `PROJECT_DOCS/STANDARDS/API/README.md`
  - links API standards to accepted ADR-0002.
- `PROJECT_DOCS/STANDARDS/README.md`
  - records ADR-backed API-boundary status.
- `PROJECT_DOCS/STANDARDS/STANDARD_CONSISTENCY_AND_ADR_GAP_REVIEW.md`
  - marks the API-boundary ADR gap as accepted.
- `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md`
  - records the project state after patch 000061.
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`
  - records version `0.13.22-foundation`.
- `platform/versions/platform.env`
  - sets `PLATFORM_VERSION=0.13.22-foundation`;
  - sets `PLATFORM_STATE_PATCH=000061_springmaster_adr_0002_api_boundary_and_endpoint_contract`.

## Validation

- Documentation-only patch.
- No Java code, Maven configuration, shell tooling, templates, demo code or target-project files changed.
- `mvn test` is not required.
- Existing target projects remain unchanged and are not supplied by this patch.

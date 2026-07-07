# Changelog 000059 - springmaster_api_error_identity_and_statuscode_consistency_standard

## Type

Documentation-only.

## Scope

`root`

## Summary

This patch resolves the Springmaster API error identity and status-code consistency gaps identified by `000057_springmaster_standard_consistency_and_adr_gap_review`.

## Added

- `PROJECT_DOCS/STANDARDS/API/API_ERROR_IDENTITY_STATUSCODE_CONSISTENCY_STANDARD.md`

## Modified

- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_HTTP_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md`
- `PROJECT_DOCS/STANDARDS/API/README.md`
- `PROJECT_DOCS/STANDARDS/README.md`
- `PROJECT_DOCS/STANDARDS/STANDARD_CONSISTENCY_AND_ADR_GAP_REVIEW.md`
- `PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md`
- `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md`
- `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md`
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`
- `platform/versions/platform.env`

## Decisions

- `errorId` is required and identifies one concrete error occurrence.
- `correlationId`, `traceId`, `messageKey` and `localMessage` are optional public error fields unless a later standard makes them mandatory.
- `message` is a safe fallback message and not a machine contract.
- `violations[].messageKey` is allowed for field-level localization.
- Create defaults to `201 Created`.
- Full update defaults to `200 OK` with response DTO for Catalog-demo.
- Single bodyless delete defaults to `204 No Content` on success and `404` when already absent.
- Delete-multiple defaults to `200 OK` with result DTO when introduced.
- `202 Accepted` is allowed only with a deterministic status, job or operation resource.

## Validation

No Maven test is required because the patch changes documentation and version metadata only.

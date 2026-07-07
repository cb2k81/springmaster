# Changelog 000066 - springmaster ADR-0005 Security and Permission Boundary

## Scope

Documentation-only root patch.

## Summary

This patch accepts `ADR-0005-security-and-permission-boundary.md` and aligns the ADR backlog, ADR governance, security standard, Catalog-demo readiness plan, gate concept, standards index, consistency review, implementation plan and version policy.

## Added

- `PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md`

## Modified

- `PROJECT_DOCS/ADR/README.md`
- `PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md`
- `PROJECT_DOCS/ADR/ADR_GOVERNANCE_AND_BACKLOG_ALIGNMENT.md`
- `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md`
- `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md`
- `PROJECT_DOCS/STANDARDS/README.md`
- `PROJECT_DOCS/STANDARDS/STANDARD_CONSISTENCY_AND_ADR_GAP_REVIEW.md`
- `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md`
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`
- `platform/versions/platform.env`

## Decision impact

- Endpoint security classification is ADR-backed.
- Permission naming with `<domain>:<resource>:<operation>` is ADR-backed.
- Catalog-demo first permission vocabulary is ADR-backed.
- Authorization placement at the application operation boundary is ADR-backed.
- `documented-deferred-security` and `implemented-management-security` are accepted Catalog-demo modes.
- Report-only G4 security diagnostics may reference ADR-0005.
- Strict security gates remain deferred until implementation evidence and ADR-0006 strict promotion exist.

## Validation

No Maven test is required because this patch changes documentation and version metadata only.

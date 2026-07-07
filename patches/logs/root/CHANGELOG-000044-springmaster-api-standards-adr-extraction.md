# Changelog 000044: Springmaster API Standards ADR Extraction

## Summary

Extracts generic Springmaster API standards from IDM API-readiness ADR themes and documents them as master-level standards under `PROJECT_DOCS/STANDARDS/API/`.

## Changes

- Adds the generic API Request Validation Standard.
- Adds the generic Required Fields and OpenAPI Required Standard.
- Adds the generic List, Filter and Query Standard for UI-capable management APIs.
- Adds the generic Command HTTP Standard, including the rule that single deletes must not use `DELETE` request bodies.
- Adds the generic External ID and OpenAPI Boundary Standard, including opaque string external IDs and YAML-/UI-readiness rules.
- Updates the API standards index and the Springmaster standards overview.
- Updates `PLATFORM_VERSION` to `0.13.5-foundation` and `PLATFORM_STATE_PATCH` to `000044_springmaster_api_standards_adr_extraction`.
- Records the version rationale in `SPRINGMASTER_VERSION_POLICY.md`.

## Scope boundary

No target project is changed. IDM, Personnel, Contacts and Orders remain outside the delivery path. Catalog-demo is not created or modified by this patch; it remains the intended later demonstrator.

## Validation

Documentation-only patch. Maven tests are not required because no Java code, test code, build configuration, shell tooling or generated project template is changed.

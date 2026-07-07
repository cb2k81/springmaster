# External ID and OpenAPI Boundary Standard

## Status

Accepted as generic Springmaster API standard with patch `000044_springmaster_api_standards_adr_extraction`.

## Purpose

External API identifiers and OpenAPI schemas define the boundary between backend internals and consumers. Springmaster APIs must keep that boundary stable, UI-ready and independent from persistence implementation details.

This standard extracts generic external-ID and OpenAPI-boundary rules from IDM API-readiness ADR material. It does not prescribe IDM-specific identifier names, role concepts, permission concepts or database structures.

## External ID standard

External IDs are opaque string identifiers. API consumers must treat them as tokens, not as numbers, database keys, UUIDs with semantic meaning or parseable composite values.

OpenAPI must expose external IDs as `type: string`. A client must not need to know whether the backend stores the underlying identifier as a UUID, numeric database ID, natural key or generated value.

Controllers must not expose internal database IDs unless the project explicitly declares that value as the public external identifier. Metadata IDs and version IDs may be returned only when they are part of a documented API contract and are safe for client use.

Path variables that identify resources must use stable external names. Domain-specific names such as `catalogItemId` are allowed when they improve clarity. A generic `id` is acceptable for simple resource controllers. Names that reveal persistence implementation details should be avoided.

Request DTOs must not require server-managed IDs for creates. Updates and deletes identify the target through the path unless a documented command contract requires a separate opaque token, version or concurrency value.

## OpenAPI boundary standard

The OpenAPI document is a consumer contract, not an incidental reflection of Java internals. It must expose stable endpoint paths, methods, request schemas, response schemas, query parameters, status codes and required fields.

API controllers must use boundary DTOs for request and response representation. Persistence entities, internal command objects and service-only types should not be exposed directly in generated OpenAPI schemas.

Operation paths must be stable enough for UI generation and manual review. Endpoint names should follow resource-oriented conventions unless a command endpoint is intentionally modeled as a command.

Generated YAML must be reviewable. It must not hide required fields, body-bearing deletes, persistence-only IDs or undocumented query parameters. It should use stable operation IDs once the OpenAPI gate defines the final naming rule.

## YAML and UI readiness

An API is YAML-/UI-ready when the generated OpenAPI contract can be used to build or validate a UI integration without reading backend source code for ordinary endpoint usage.

Minimum readiness means:

- request and response schemas use DTO-oriented names,
- external IDs are strings,
- required fields are visible,
- list query parameters are documented,
- command status codes are stable,
- single deletes do not have request bodies,
- all-data endpoints are distinguishable from paged list endpoints,
- endpoint paths avoid project-internal package or persistence terms.

## Reference implementation expectation

Catalog-demo must first prove this boundary with `CatalogItem`. Existing projects are comparison candidates only after the reference implementation and OpenAPI gate concept exist.

## Future gates

The intended enforcement path is:

1. OpenAPI contract tests that parse generated YAML and assert identifier types, required fields, query parameters and delete-body absence.
2. Controller tests for path-variable behavior and status codes.
3. Optional ArchUnit rules that prevent entity classes from being used as controller request/response bodies.
4. A review gate before generated Springmaster standards are applied to IDM, Personnel or other existing projects.

Until those gates exist, this document defines the intended contract and the generated YAML must be reviewed manually for boundary leaks.

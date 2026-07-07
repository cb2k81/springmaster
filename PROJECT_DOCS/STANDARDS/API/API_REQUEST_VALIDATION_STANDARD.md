# API Request Validation Standard

## Status

Accepted as generic Springmaster API standard with patch `000044_springmaster_api_standards_adr_extraction`. The DTO-specific boundary rules are refined by patch `000049_springmaster_dto_boundary_and_validation_standard`.

## Purpose

Request validation makes API behavior deterministic before a command reaches the domain service. Springmaster APIs must reject invalid command input at the HTTP boundary and must keep that rule visible to the generated OpenAPI contract.

This standard is extracted from IDM API-readiness ADR material as a generic Springmaster rule. It is not an IDM-specific instruction and does not define IDM users, roles, scopes, permissions or assignment endpoints.

## Standard

Every command endpoint that accepts a JSON request body must use a dedicated inbound request DTO. Controllers must not bind persistence entities or domain aggregates directly from external JSON. The canonical DTO role taxonomy, create/update/command/query DTO rules and controller boundary prohibitions are defined in `DTO_BOUNDARY_AND_VALIDATION_STANDARD.md`.

Request DTOs must express structural requirements with Jakarta Bean Validation annotations where the requirement belongs to the API boundary. Required strings must reject blank values, not only `null`. Nested inbound DTOs must be validated recursively when their fields are part of the request contract.

Domain validation remains separate from request-shape validation. Request validation checks whether the incoming representation is complete and syntactically acceptable. Domain validation checks business invariants after mapping into the domain model or command model.

Create and update operations must use separate request DTOs when their required fields differ. A create request must not silently derive required business identifiers from optional fields. An update request must not accept missing identity or version fields unless the endpoint path and the documented update semantics make that omission explicit.

Validation failures must result in a client error response. The default Springmaster target is `400 Bad Request` for invalid request bodies, invalid query values and unsupported list parameters. If a project uses a structured error body, the response must include a stable machine-readable error code and field-level diagnostics where available.

Controllers must not silently default invalid values into valid values. Defaults are allowed only when they are part of the documented API contract, for example a default page index or a default sort direction.

## OpenAPI visibility

Fields that are required by boundary validation must be visible as required fields in the generated OpenAPI document. A backend-only validation rule that is not represented in OpenAPI is a contract gap unless the rule is intentionally documented as non-structural domain validation.

## Reference implementation expectation

Catalog-demo must first demonstrate this standard with `CatalogItem` create and update requests. The reference must include valid command tests and invalid request tests for missing, blank or malformed required fields.

## Future gates

The intended enforcement path is:

1. Controller or integration tests that submit invalid request bodies and assert `400`.
2. OpenAPI contract tests that assert required request properties in generated YAML.
3. Optional reusable test utilities for standard validation assertions.
4. Optional ArchUnit or custom Java tests that reject entity types as controller request bodies.

Until those gates exist, this document is the authoritative rule and Catalog-demo is the expected demonstrator.


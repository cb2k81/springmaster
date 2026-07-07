# Required Fields and OpenAPI Required Standard

## Status

Accepted as generic Springmaster API standard with patch `000044_springmaster_api_standards_adr_extraction`. DTO boundary and validation naming rules are refined by patch `000049_springmaster_dto_boundary_and_validation_standard`.

## Purpose

Required-field handling must be consistent across Java validation, generated OpenAPI YAML and UI consumers. A UI-ready management API is not ready when mandatory backend fields are invisible or ambiguous in the API contract.

This standard generalizes IDM API-readiness ADR material into Springmaster terminology. It deliberately avoids copying IDM-specific DTO names, endpoint names or permission concepts.

## Standard

A field is required at the API boundary when the server rejects a request that omits it. Such fields must be expressed in the request DTO and must be visible in OpenAPI as required schema properties.

Required object, numeric, boolean and date/time properties must reject `null`. Required string properties must reject `null` and blank text when blank text is not a valid business value. String format restrictions such as length, pattern or enum-like value sets must be documented by validation annotations or explicit OpenAPI schema metadata where available.

Required collections must define whether an empty collection is acceptable. If at least one item is mandatory, the request DTO must enforce that rule and the API standard documentation for the endpoint must state it.

Nullable fields are allowed only when `null` has a documented meaning or when the field is optional. A nullable OpenAPI property must not be used to hide a field that is required by backend validation.

Server-generated fields must not appear as required inbound fields. IDs, metadata, audit fields and server-managed version information are either path variables, response-only properties or explicitly documented command inputs.

Response DTOs and request DTOs must be separated when requiredness differs between inbound and outbound representation. Reusing a response DTO as an inbound DTO is not canonical for new Springmaster reference APIs when requiredness, mutability or server-managed fields differ. The role-specific naming and separation rules are defined in `DTO_BOUNDARY_AND_VALIDATION_STANDARD.md`.

## YAML and UI readiness

Generated OpenAPI YAML must be sufficient for UI generation and manual API review. For required fields this means:

- required request properties are visible in the schema,
- field names are stable and match JSON property names,
- server-generated response properties are not misclassified as required request input,
- validation constraints that affect UI forms are represented or explicitly documented,
- endpoint examples do not contradict requiredness.

## Reference implementation expectation

Catalog-demo must demonstrate required-field visibility for `CatalogItem` create and update requests. The first reference tests should assert both HTTP validation behavior and the generated OpenAPI schema once the OpenAPI contract gate is introduced.

## Future gates

The intended enforcement path is:

1. OpenAPI contract tests that parse generated YAML and assert `required` arrays for request schemas.
2. Controller tests for missing and blank required fields.
3. Review-gate checks that compare request DTO validation annotations against OpenAPI schema output.
4. Optional Maven-bound tests that fail on known required-field contract gaps.

Until OpenAPI contract tests exist, required-field changes must be reviewed manually against request DTOs and generated API documentation.


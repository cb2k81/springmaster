# Command HTTP Standard

## Status

Accepted as generic Springmaster API standard with patch `000044_springmaster_api_standards_adr_extraction`.

## Purpose

Command endpoints must use HTTP semantics consistently. This is especially important for assignment operations and deletes, because clients, gateways and generated API tooling do not reliably handle `DELETE` requests with bodies.

This standard generalizes IDM assignment and command ADR material. It does not copy IDM-specific user-role, role-permission or application-scope endpoint contracts.

## Standard

Create commands use `POST` to a collection or command endpoint. Successful creates should return `201 Created` when a new resource is created and the resource identity is known. `200 OK` is acceptable for command-style operations that return a result but do not create a canonical resource. `204 No Content` is acceptable for successful commands that intentionally return no body. Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` defines deterministic first-slice defaults: creates use `201`, full updates use `200` with body, single deletes use `204`, delete-multiple uses `200` with result DTO and `202` requires a status/job/operation resource.

Update commands use `PUT` when the command replaces or updates a known resource identified by the path and the request body represents the update contract. Partial update semantics require explicit documentation and should not be implied accidentally.

Single-resource deletes must use `DELETE` without a request body. Every value required to identify the resource or relationship to delete must be supplied through the path or query parameters. A single delete that requires a complex command body must be modeled as a `POST` command endpoint instead of a body-bearing `DELETE`.

Assignment operations must be modeled as explicit commands or relationship resources. Adding an assignment normally uses `POST`. Removing one specific assignment normally uses a bodyless `DELETE` with path variables that fully identify the assignment. Bulk assignment changes, calculated removals or multi-field delete commands must use `POST` to a command endpoint with an explicit request DTO.

`GET` must not mutate state. `DELETE` must not rely on a JSON request body. `POST` must not be used as a hidden query endpoint unless the endpoint is explicitly documented as a complex search command and remains side-effect free.

Command endpoints must document idempotency expectations. If repeating a command is safe, the response behavior must be deterministic. If repeating a command is not safe, duplicate handling and conflict behavior must be documented.

## Error behavior

The default command error mapping is:

| Situation | HTTP status |
|---|---:|
| invalid command body or invalid command parameters | `400` |
| missing authenticated context | `401` |
| missing authorized context | `403` |
| target resource not found | `404` |
| duplicate resource or conflicting command state | `409` |
| successful single delete with no response body | `204` |
| successful delete-multiple with item feedback | `200` |

Projects may use richer structured error bodies, but the status semantics must remain stable.

## Reference implementation expectation

Catalog-demo must demonstrate standard create, update and delete behavior for `CatalogItem` before Springmaster applies these rules to existing projects. Assignment-style commands are added later only when the demo needs a second object or relationship to show the pattern properly.

## Future gates

The intended enforcement path is:

1. Controller tests for command status codes and bodyless single deletes.
2. OpenAPI contract tests that reject request bodies on single-delete operations.
3. Optional endpoint naming checks for command subresources.
4. Review-gate checks before any assignment pattern is exported to target projects.

Until these gates exist, no Springmaster standard may require IDM, Personnel or another existing project to change its assignment endpoints.


## Specialization since 000053

Patch `000053_springmaster_command_relationship_endpoint_standard` refines this command HTTP baseline for resource commands, collection commands, relationship adds/removes, assignment-style APIs, nested aggregate commands and bulk operations.

The specialization keeps the core rule from this document unchanged: single deletes are bodyless `DELETE` operations, while deletes or relationship changes that need structured input are command endpoints with dedicated DTOs.


## Error identity and status-code consistency since 000059

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` is the status-code narrowing addendum for this command baseline.

For new Springmaster reference APIs:

- full update defaults to `200 OK` with the updated response DTO;
- single bodyless delete defaults to `204 No Content` on success;
- delete-multiple defaults to `200 OK` with a command result DTO;
- `202 Accepted` is valid only with a deterministic status, job or operation resource;
- command failures use the baseline `errorType` vocabulary from `API_ERROR_CONTRACT_STANDARD.md`.

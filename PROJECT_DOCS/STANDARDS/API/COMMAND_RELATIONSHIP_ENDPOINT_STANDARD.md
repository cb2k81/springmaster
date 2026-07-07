# Command and Relationship Endpoint Standard

## Status

Accepted as generic Springmaster command and relationship endpoint standard with patch `000053_springmaster_command_relationship_endpoint_standard`.

## Purpose

This standard specializes the generic endpoint and command HTTP rules for command, assignment, relationship, nested-resource and bulk-operation APIs.

Patch `000046_springmaster_api_endpoint_contract_standard` defines the canonical resource endpoint baseline. Patch `000053` defines how Springmaster reference APIs must model operations that are not simple create, update, detail, list or single delete operations. The standard is documentation-only and does not change IDM, Personnel, Contacts, Orders or any other target project.

Catalog-demo must not introduce relationship, assignment, bulk or state-transition endpoints before these rules are either implemented or explicitly deferred for the demo slice.

## Design principles

Springmaster APIs are resource-oriented where the HTTP method and resource identity are sufficient. They are command-oriented when the operation has domain behavior that cannot be expressed safely as simple CRUD.

Command endpoints must be explicit, named with domain vocabulary and tested as part of the public API contract. They must not hide repository, method or UI implementation vocabulary behind generic names such as `execute`, `process`, `do`, `findFirst`, `removeSelection` or `saveAssignments`.

Relationship endpoints must make relationship identity deterministic. If the relationship can be identified by parent id and child id, those values belong in the path for single relationship deletion. If the relationship itself has a stable identity or attributes, it may be modeled as its own resource.

Bulk operations default to atomic all-or-nothing semantics. Partial success is not the default Springmaster pattern and requires an explicit result DTO plus an ADR or endpoint decision.

## Relationship vocabulary

Springmaster distinguishes the following concepts:

| Concept | Meaning | Typical API shape |
|---|---|---|
| relationship | association between two resources | nested resource or relationship resource |
| assignment | relationship with authorization, ownership or allocation semantics | relationship endpoint or command endpoint |
| relationship resource | association with its own identity or attributes | `/api/<domain>/<relationships>/{id}` |
| nested collection | child view scoped by parent | `/api/<domain>/<parents>/{parentId}/<children>` |
| resource command | behavior against one resource | `/api/<domain>/<resources>/{id}/commands/<command>` |
| collection command | behavior against a collection | `/api/<domain>/<resources>/commands/<command>` |
| relationship command | behavior against a relationship set | nested `/commands/<command>` endpoint |

The API must use domain names. Generic public path fragments such as `/assignments` are allowed only when the domain concept is actually an assignment. Otherwise the relationship should be named after the target relationship, for example roles, scopes, members, memberships, children or positions.

## Command classification

Every command endpoint must be classified before implementation.

| Command type | Standard location | Typical method |
|---|---|---:|
| resource state transition | `/api/<domain>/<resources>/{id}/commands/<command>` | `PUT` or `POST` |
| resource side-effect command | `/api/<domain>/<resources>/{id}/commands/<command>` | `POST` |
| collection bulk command | `/api/<domain>/<resources>/commands/<command>` | `POST` |
| relationship add | nested collection or relationship resource | `POST` |
| relationship remove by identity | nested relationship path | `DELETE` without body |
| relationship bulk command | nested `/commands/<command>` | `POST` |
| complex search | `/api/<domain>/<resources>/search` | `POST`, side-effect free |
| asynchronous command | command endpoint plus status resource | `POST` + status endpoint |

The endpoint standard from 000046 remains authoritative for regular list, detail, create, update and single delete operations. This document only specializes command and relationship cases.

## HTTP method rules for commands

Use `PUT` for idempotent state-setting commands when repeating the same request leads to the same domain state and response behavior.

Use `POST` for non-idempotent commands, commands that create derived resources, commands with side effects such as notification, rotation, recalculation, import, export or batch execution, and bulk commands.

Use `DELETE` only when a single resource or single relationship is fully identified by the path and no request body is needed.

Do not use a `DELETE` request body. If a deletion requires ids, version maps, reasons, dry-run flags or other structured input, model it as a `POST .../commands/<command>` endpoint with a dedicated command DTO.

Do not use `GET` for commands. `GET` must remain side-effect free.

`202 Accepted` is reserved for asynchronous commands that expose a deterministic status, job or operation resource. A command must not return `202` without a way to observe the later result.

## Command naming standard

Command path names use lower-kebab-case domain verbs.

Allowed examples:

| Situation | Command name example |
|---|---|
| activate a resource | `activate` |
| deactivate a resource | `deactivate` |
| archive a resource | `archive` |
| submit for review | `submit-for-review` |
| approve a submitted resource | `approve` |
| reject a submitted resource | `reject` |
| assign multiple related resources | `assign-multiple` |
| remove multiple relationships | `remove-multiple` |
| delete multiple resources | `delete-multiple` |
| recalculate derived values | `recalculate` |
| rotate a secret | `rotate-secret` |

Prohibited as canonical command names:

- technical method names such as `process`, `execute`, `handle`, `run`, `save`, `do`;
- UI action names such as `button-click`, `selected-delete`, `modal-save`;
- repository vocabulary such as `find-one`, `find-first`, `find-last`;
- ambiguous nouns without a verb when behavior changes state.

## Resource state-transition commands

Canonical shape for an idempotent resource transition:

`PUT /api/<domain>/<resources>/{id}/commands/<command>`

Canonical shape for a non-idempotent resource command:

`POST /api/<domain>/<resources>/{id}/commands/<command>`

The command contract must define:

- whether the command is idempotent;
- whether the request body is absent or a dedicated command DTO;
- valid source states and target state;
- success status and response body;
- invalid-state behavior;
- not-found behavior;
- permission name;
- audit/event expectation;
- optimistic-locking expectation if concurrent changes matter.

Default state-transition status behavior:

| Situation | Status |
|---|---:|
| transition applied and representation useful | `200 OK` |
| transition applied and no body needed | `204 No Content` |
| command creates a derived resource | `201 Created` |
| asynchronous command accepted | `202 Accepted` only with status/job/operation DTO |
| unknown resource | `404 Not Found` |
| invalid source state | `409 Conflict` |
| invalid command body | `400 Bad Request` |
| missing authentication or permission | `401` or `403` |

## Relationship read endpoints

A relationship read endpoint is allowed when a UI needs to inspect related resources or assignable choices.

Common shapes:

| Need | Endpoint |
|---|---|
| list current related resources | `GET /api/<domain>/<parents>/{parentId}/<children>` |
| list assignable child options | `GET /api/<domain>/<parents>/{parentId}/<children>/options` |
| read a relationship resource by id | `GET /api/<domain>/<relationships>/{id}` |

Relationship lists that can grow must be paged and must follow the list/query standard. Bounded relationship options may use `/options` and a small option DTO.

The response must not expose join entities or JPA relationship internals. Use dedicated relationship DTOs, child list-item DTOs or option DTOs.

## Add relationship or assignment

Simple add relationship shape:

`POST /api/<domain>/<parents>/{parentId}/<children>`

The request body must be a dedicated DTO, usually containing at least the child external id and optional relationship attributes.

Alternative shape for complex domain behavior:

`POST /api/<domain>/<parents>/{parentId}/<children>/commands/<command>`

Use the command shape when adding the relationship has non-trivial domain rules, bulk behavior, workflow effects, audit reason, validity ranges, derived updates or partial-success semantics.

Default add status behavior:

| Situation | Status |
|---|---:|
| relationship resource created | `201 Created` |
| relationship added without separate representation | `204 No Content`; `200 OK` when a meaningful result DTO is returned |
| parent or child unknown | `404 Not Found` |
| relationship already exists | `409 Conflict` unless idempotent add is explicitly chosen |
| invalid request | `400 Bad Request` |
| missing permission | `403 Forbidden` |

Idempotent add is allowed only when the endpoint explicitly documents repeated calls and response behavior.

## Remove single relationship

When parent id and child id fully identify the relationship, use a bodyless nested delete:

`DELETE /api/<domain>/<parents>/{parentId}/<children>/{childId}`

When the relationship has its own external id, use relationship-resource deletion:

`DELETE /api/<domain>/<relationships>/{id}`

Do not send JSON in the delete body. Delete reason, version maps, effective dates or removal options require a command endpoint.

Default remove status behavior:

| Situation | Status |
|---|---:|
| relationship removed | `204 No Content` |
| parent, child or relationship unknown | `404 Not Found` |
| relationship cannot be removed because of state | `409 Conflict` |
| invalid path/query parameter | `400 Bad Request` |
| missing permission | `403 Forbidden` |

## Bulk relationship commands

Bulk relationship modifications use command endpoints.

Canonical examples:

| Need | Endpoint |
|---|---|
| assign many children to one parent | `POST /api/<domain>/<parents>/{parentId}/<children>/commands/assign-multiple` |
| remove many children from one parent | `POST /api/<domain>/<parents>/{parentId}/<children>/commands/remove-multiple` |
| replace an assignment set | `PUT /api/<domain>/<parents>/{parentId}/<children>/commands/replace` when idempotent |
| delete many resources | `POST /api/<domain>/<resources>/commands/delete-multiple` |

Bulk relationship command DTOs must use opaque external string ids. They may include version maps, validity ranges, reason fields or dry-run flags only when the domain requires them.

Default bulk semantics are atomic all-or-nothing. Partial success requires:

- an explicit endpoint decision or ADR;
- a result DTO with item-level status;
- deterministic error/status mapping;
- clear transaction and audit behavior;
- UI handling expectations.

## Nested aggregate commands

A nested aggregate command modifies an aggregate child through the parent aggregate boundary. It is allowed when the child has no independent lifecycle outside the parent or when the parent aggregate owns the invariant.

Canonical shape:

`POST /api/<domain>/<parents>/{parentId}/<children>/{childId}/commands/<command>`

Use nested aggregate commands sparingly. If the child has an independent lifecycle and identity, prefer a resource endpoint under the child resource and reference the parent through a relation or filter.

The command must document which aggregate owns the transaction and invariant.

## Command DTO and result DTO standard

Command requests use dedicated DTOs. The DTO name should include the resource or relationship and the command name.

Examples:

| Endpoint kind | DTO example |
|---|---|
| delete multiple resources | `CatalogItemDeleteMultipleCommandDTO` |
| activate one resource | `CatalogItemActivateCommandDTO` or no body when no fields are needed |
| assign multiple children | `CatalogCategoryAssignItemsCommandDTO` |
| remove multiple children | `CatalogCategoryRemoveItemsCommandDTO` |
| replace assignment set | `CatalogCategoryReplaceItemsCommandDTO` |
| command result | `CatalogItemDeleteMultipleResultDTO` |

Request DTOs must follow the DTO boundary and validation standard. Required fields must use Bean Validation and must be visible in OpenAPI.

Result DTOs are required when the command result is meaningful to the UI, when delete-multiple is introduced, when partial success is allowed, when an asynchronous operation is started, or when the endpoint returns warnings or derived changes.

## Security and permission mapping

Every management command and relationship operation requires an explicit permission.

Default permission operation names align with public command semantics:

| Endpoint kind | Permission operation example |
|---|---|
| regular create | `create` |
| regular update | `update` |
| regular delete | `delete` |
| delete multiple | `delete-multiple` |
| activate | `activate` |
| archive | `archive` |
| assign relationship | `assign` or domain-specific verb |
| remove relationship | `remove` or domain-specific verb |
| replace relationship set | `replace` |

Permission names follow the security standard: `<domain>:<resource>:<operation>`.

For relationship operations, the resource part must be the resource whose aggregate or management boundary owns the operation. If ownership is ambiguous, the endpoint standard must be resolved by ADR before implementation.

Controller-only security is not sufficient for reusable command behavior. Authorization should be placed at the QueryService, CommandService or UseCaseHandler boundary according to the controller/service/use-case standard.

## Transaction, audit and event expectations

Command endpoints are application-service or use-case operations. Transaction boundaries must not live in controllers.

Write commands normally run in a single transaction. Bulk commands default to one atomic transaction unless the endpoint explicitly defines chunking, partial success or asynchronous processing.

Commands with business relevance should define audit expectations. At minimum, the command standard must decide whether the audit trail records actor, operation, affected resource ids, reason and result.

Event emission is deferred as a concrete implementation standard, but command endpoints must not silently create event semantics without documentation.

## Error and conflict behavior

Command and relationship errors must use the API error contract from 000048.

Default mappings:

| Situation | Status | Error type |
|---|---:|---|
| invalid command body or validation failure | `400` | `VALIDATION_FAILED` |
| invalid path or query parameter | `400` | `INVALID_REQUEST` |
| unsupported query parameter | `400` | `UNSUPPORTED_QUERY_PARAMETER` |
| missing authentication | `401` | `UNAUTHORIZED` |
| missing permission | `403` | `FORBIDDEN` |
| parent, child or resource not found | `404` | `RESOURCE_NOT_FOUND` |
| duplicate relationship | `409` | `CONFLICT` |
| invalid state transition | `409` | `BUSINESS_RULE_VIOLATION` |
| optimistic-locking conflict | `409` | `CONFLICT` |
| unexpected technical failure | `500` | `INTERNAL_ERROR` |

A command must not collapse domain conflicts into generic `400` responses when the request is syntactically valid but invalid for the current domain state.

## OpenAPI and future gates

The intended gate path is:

1. OpenAPI test: no `DELETE` operation has a request body.
2. OpenAPI test: `/commands/<command>` paths use `POST` or `PUT`, not `GET` or body-bearing `DELETE`.
3. OpenAPI test: command request and response schemas are DTOs, not entities.
4. OpenAPI test: operationIds use domain command vocabulary, not generic `execute`/`process` vocabulary.
5. MockMvc test: command status codes follow the documented matrix.
6. Reflection/ArchUnit gate: command controllers do not access repositories directly.
7. Security gate: management commands have explicit permission tests.
8. Transaction gate: write commands execute through service/use-case boundaries.

These gates are future work. Patch 000053 defines the standard only.

## Catalog-demo readiness rule

Catalog-demo may start with simple `CatalogItem` list, detail, create, update and bodyless delete without relationship endpoints.

Before Catalog-demo introduces categories, tags, assignments, memberships, bulk delete, state transitions or nested aggregate commands, the implementation must follow this standard or explicitly document a deferred decision.

Catalog-demo must not become canonical with:

- body-bearing `DELETE` operations;
- generic public `execute` or `process` commands;
- bulk operations without atomicity decision;
- relationship deletes that require hidden body semantics;
- unprotected management commands;
- command DTOs without validation and OpenAPI visibility.

## Existing application boundary

IDM and Personnel remain comparison inputs. This standard does not require either application to change immediately.

Existing endpoint shapes in IDM or Personnel that differ from this standard may later be categorized as compatible, transitional or project-specific after Catalog-demo and gate utilities prove the Springmaster pattern.


## Status-code and error identity consistency since 000059

Patch `000059_springmaster_api_error_identity_and_statuscode_consistency_standard` narrows command status defaults before gate tooling begins.

For new Springmaster reference APIs:

- delete-multiple returns `200 OK` with a result DTO when introduced;
- `204 No Content` remains valid for simple successful commands with no meaningful response body;
- `202 Accepted` is reserved for asynchronous commands with a status/job/operation DTO;
- command errors must use the baseline `errorType` values from `API_ERROR_CONTRACT_STANDARD.md`;
- every error response must include an `errorId`, while `correlationId`, `traceId`, `messageKey` and `localMessage` are optional until observability/i18n standards are implemented.

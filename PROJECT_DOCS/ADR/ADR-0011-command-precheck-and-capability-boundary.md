# ADR-0011: Command Precheck and Capability Boundary

## Status

Accepted

## Date

2026-07-03

## Context

Springmaster is the master project for backend standards, reusable backend foundation, reference implementations and later target-project update workflows. Existing applications such as IDM, Personnel, Contacts and Orders are comparison inputs unless a later update workflow explicitly supplies a target project.

Existing API standards define regular resource endpoints, command endpoints, relationship endpoints, DTO boundaries, security placement, permission naming and command HTTP semantics. They do not yet define a canonical way for a backend to tell a UI whether a concrete command against a concrete target object is currently executable before the user triggers the command.

Management UIs frequently need this information for a better user experience. A delete command may be visible because the actor has the required delete permission, but may still be blocked for a concrete target by policy, object state, data-scope, dependency or lifecycle rules. Example: a user account management UI may allow administrators to delete users in general, while a concrete policy forbids deleting the currently authenticated user's own account.

Such checks must not be implemented only in UI controls. A frontend-only disabled button is not a security boundary and is easily bypassed. The backend must remain the final authority for command execution.

At the same time, evaluating every potential command for every row in a large list would introduce unnecessary overhead. A standard must therefore support optional resource-level prechecks without making them mandatory for every command or list row.

## Decision

Springmaster defines **command prechecks** as optional, side-effect-free backend capability queries for concrete commands.

A command precheck answers this question:

```text
Can the current authenticated actor execute this concrete command for this concrete target now?
```

The decision is:

1. **Prechecks are optional.**
   A command without a documented precheck endpoint remains executable from the precheck perspective when permission and local request construction are satisfied. Command execution still performs final validation.

2. **Prechecks are UX/capability information, not a security replacement.**
   A client must never rely on a precheck as authorization proof. The executing command endpoint must validate permissions, actor context, target existence, object state and policy constraints again.

3. **Precheck and execution must share the same policy.**
   A backend must not implement one rule in a precheck handler and a different rule in the command handler. Both call the same command policy, capability policy or domain/application guard.

4. **Prechecks are resource- or command-specific.**
   The canonical resource-command precheck path is:

   ```text
   GET /api/<domain>/<resources>/{id}/commands/<command>/precheck
   ```

   Commands that need request data for the precheck may use:

   ```text
   POST /api/<domain>/<resources>/{id}/commands/<command>/precheck
   ```

   with a dedicated precheck request DTO.

5. **Bulk/list commands do not require per-item prechecks.**
   List and bulk UIs may use permission, selection state and confirmation only. The backend command execution must handle item-level or aggregate-level rejections according to the existing bulk command standard. Partial success requires an explicit result DTO and endpoint decision.

6. **Precheck endpoints are management endpoints unless explicitly classified otherwise.**
   A precheck for a management command is itself a management endpoint and uses the same operation-level permission or a documented equivalent capability gate.

7. **A successful precheck HTTP status does not imply executable=true.**
   `200 OK` may carry `executable: false` when the caller has the general permission but a concrete policy, state, validation, dependency or data-scope rule blocks the target command.

8. **Permission denial remains an API error.**
   Missing authentication returns `401`. Missing operation permission returns `403`. Unknown targets return `404`. A policy block for a known target and authorized actor returns `200` with `executable: false`, unless a later data-scope concealment ADR decides that selected target existence must be hidden.

## Standard DTO contract

Springmaster accepts the following public response semantics for command prechecks:

```text
CommandPrecheckResponseDTO
  commandId: string
  targetType?: string
  targetId?: string
  executable: boolean
  reasons: CommandPrecheckReasonDTO[]
  warnings?: CommandPrecheckReasonDTO[]
  destructive?: boolean
  confirmationRequired?: boolean
  checkedAt?: string
```

```text
CommandPrecheckReasonDTO
  code: string
  category: permission | policy | state | validation | dependency | data-scope | technical
  severity: blocking | warning | info
  messageKey?: string
  defaultMessage?: string
  parameters?: object
```

A concrete project may add fields only when they do not change these semantics and do not expose internal persistence, security-token or framework implementation details.

## Controller, DTO and policy interface decision

Springmaster should later provide reusable DTO types and a small command-precheck policy/decision abstraction in the shared Java foundation when the codebase is ready for this API support.

Recommended future Java concepts:

```text
CommandPrecheckResponseDTO
CommandPrecheckReasonDTO
CommandPrecheckDecision
CommandPolicy or CommandPrecheckPolicy
```

A generic `@RequestMapping` controller interface is **not** accepted as the first reusable contract. Controller paths, HTTP methods, request DTOs, authorization annotations and OpenAPI operation metadata vary by aggregate and command. The reusable standard belongs in DTOs, policy decisions, test helpers and OpenAPI assertions first. Controllers remain explicit HTTP adapters that delegate to command-specific application services or use cases.

## HTTP behavior

| Situation | Precheck status | Precheck body |
|---|---:|---|
| missing authentication | `401` | standard API error |
| authenticated but missing operation permission | `403` | standard API error |
| target not found | `404` | standard API error |
| actor has general permission and command is allowed | `200` | `executable: true` |
| actor has general permission but concrete target is blocked | `200` | `executable: false` with blocking reason |
| invalid precheck request body or parameter | `400` | standard API error |
| unexpected technical failure | `500` | standard API error |

Command execution keeps the existing command/delete status semantics. A command that was prechecked successfully may still fail during execution because data, permissions or state changed after the precheck.

## Scope

This ADR applies to:

- new Springmaster backend standards;
- Catalog-demo once a command needs target-specific capability information;
- generated project templates once command-precheck support is explicitly introduced;
- future target-project comparison reports and update workflows.

This ADR does **not** automatically change IDM, Personnel, Contacts, Orders or any other target application. Existing applications may implement equivalent behavior independently until Springmaster supplies a later update path.

## Considered alternatives

### Define disabled-state logic only in the frontend

Rejected. A frontend control state is useful UX, but it is not a security or policy boundary. It also duplicates backend rules and creates drift when the command handler changes.

### Make every command require a precheck endpoint

Rejected. Many commands are always executable when the actor has permission and the request is valid. Mandatory prechecks would add boilerplate and latency without value.

### Perform row-level prechecks for every list item

Rejected as default behavior. It is expensive, can become stale quickly and complicates list rendering. List and bulk commands should rely on permission, selection state and backend execution validation unless a concrete bounded use case explicitly opts in.

### Return `403` for every policy-blocked target

Rejected as the default precheck behavior. When the actor has the general operation permission and the target is visible, a precheck is more useful when it returns `200` with a stable blocking reason. `403` remains correct for missing permission or later data-scope concealment policies.

### Create a generic Spring MVC controller interface

Rejected for the first standard. DTOs, policies and tests are reusable. Controller mappings and OpenAPI metadata must remain explicit and command-specific.

## Consequences

Positive consequences:

- UIs can display deterministic disabled states for target-specific command policies without owning the policy.
- Backend command handlers remain the final validation and authorization authority.
- Policy reuse prevents precheck/execution drift.
- Future OpenAPI and MockMvc gates can verify precheck shape and behavior.
- List and bulk command performance remains bounded because per-row prechecks are not mandatory.

Costs and risks:

- Backends that expose prechecks must implement policy reuse carefully.
- Clients must handle stale prechecks and execution-time rejection.
- Reason-code catalogs and localization keys must be governed to avoid ad-hoc messages.
- Strict gates must wait until Catalog-demo or another reference slice proves the pattern.

## Affected standards

This ADR accepts and consolidates:

- `PROJECT_DOCS/STANDARDS/API/COMMAND_PRECHECK_ENDPOINT_STANDARD.md`

It also specializes, without replacing, the existing command, endpoint, DTO, security and error standards:

- `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_HTTP_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/COMMAND_RELATIONSHIP_ENDPOINT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/DTO_BOUNDARY_AND_VALIDATION_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md`
- `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md`

## Verification and gates

Initial enforcement remains documentation-first.

Future report-only and later strict gates should verify:

- OpenAPI exposes precheck endpoints with canonical path shape and response DTO semantics.
- Precheck endpoints do not mutate state.
- Precheck endpoints use explicit request/response DTOs and do not expose entities.
- The execution handler and precheck handler share the same policy or guard collaborator.
- Missing permission maps to `403`; target-specific policy block maps to `200 executable=false`.
- Bulk/list commands are not incorrectly forced into per-row prechecks.

Strict enforcement requires implementation evidence and explicit promotion under ADR-0006.

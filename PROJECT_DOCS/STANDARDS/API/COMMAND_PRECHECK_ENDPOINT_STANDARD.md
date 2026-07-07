# Command Precheck Endpoint Standard

## Status

Accepted as Springmaster command-precheck API standard by `ADR-0011-command-precheck-and-capability-boundary`.

## Purpose

This standard defines optional backend precheck endpoints for concrete commands. A precheck endpoint lets a client ask whether a currently authenticated actor can execute one specific command for one specific target object at the current time.

The standard exists to prevent frontend-only command-control rules from becoming hidden business policy. It also prevents every UI from inventing a different capability DTO, endpoint path and disabled-reason vocabulary.

## Boundary rule

A command precheck is a **side-effect-free capability query**. It is not command execution and it is not an authorization replacement.

Rules:

- command execution must validate the same permission, actor, target, state and policy rules again;
- precheck and execution must call the same policy/guard collaborator;
- a client may use precheck output to disable or annotate a control, but must still handle execution failure;
- a command without precheck remains executable from the precheck perspective when permission and local request construction are satisfied;
- controllers must not implement business precheck logic inline.

## Canonical endpoint shapes

### Resource command precheck without request body

Use `GET` when the target id and authenticated actor contain all information required to evaluate the command.

```text
GET /api/<domain>/<resources>/{id}/commands/<command>/precheck
```

Example:

```text
GET /api/idm/users/{id}/commands/delete/precheck
```

### Resource command precheck with request body

Use `POST` when evaluation requires a command draft, relation id set, transition target, reason, version map or other structured input.

```text
POST /api/<domain>/<resources>/{id}/commands/<command>/precheck
```

The request body must use a dedicated precheck request DTO or the same command request DTO when that is semantically correct and safe.

### Collection command precheck

Collection command prechecks are allowed only when they evaluate one bounded collection command request, not every row in an unbounded list.

```text
POST /api/<domain>/<resources>/commands/<command>/precheck
```

Bulk and list UIs are not required to call per-item prechecks. They may rely on selection state, permission, confirmation and command execution error handling.

## Naming rules

Rules:

- `<command>` uses the same public command vocabulary as the executing endpoint;
- path fragments must use domain command terms, not Java method names;
- `precheck` is the canonical suffix and must not be replaced by `can`, `allowed`, `validate`, `dry-run`, `preview` or `check` unless a command-specific ADR documents different semantics;
- `dry-run` is not a synonym for precheck because dry-run may simulate execution effects and result changes;
- `validate` is not a synonym for precheck because validation may refer only to request shape, not actor/target policy.

## Security classification

A precheck for a management command is a management endpoint.

Rules:

- missing authentication returns `401`;
- missing operation permission returns `403`;
- a known actor with general permission but blocked by concrete target policy receives `200` with `executable: false`;
- target existence and data-scope concealment follow the existing endpoint/security standards;
- prechecks must not expose raw token claims, internal role mappings or persistence details.

## Response DTO

Canonical response semantics:

| Field | Required | Meaning |
|---|---:|---|
| `commandId` | yes | stable public command id, usually the path command segment |
| `targetType` | no | external target type name when useful for clients or logs |
| `targetId` | no | opaque public id of the target when useful and safe |
| `executable` | yes | `true` only when no blocking reason exists at check time |
| `reasons` | yes | blocking/info reason list; empty when executable and no info is needed |
| `warnings` | no | non-blocking warnings that may still be shown before confirmation |
| `destructive` | no | whether the command is destructive |
| `confirmationRequired` | no | whether the client should still require confirmation |
| `checkedAt` | no | server-side timestamp of the decision |

Canonical reason semantics:

| Field | Required | Meaning |
|---|---:|---|
| `code` | yes | stable machine-readable reason code |
| `category` | yes | reason category |
| `severity` | yes | `blocking`, `warning` or `info` |
| `messageKey` | no | stable localization key |
| `defaultMessage` | no | fallback message for logs or early clients |
| `parameters` | no | safe, bounded substitution values |

Allowed reason categories:

```text
permission
policy
state
validation
dependency
data-scope
technical
```

`permission` should be used sparingly in successful `200` precheck responses. Missing operation permission normally returns `403`. Use `permission` in the body only for non-sensitive contextual permission information that is safe to reveal.

## Self-action example

A user management backend may forbid deleting the current user's own account.

Response example:

```json
{
  "commandId": "delete",
  "targetType": "UserAccount",
  "targetId": "9a3d3922-4d1d-4518-a8bb-1a5fe450d0e2",
  "executable": false,
  "destructive": true,
  "confirmationRequired": true,
  "reasons": [
    {
      "code": "IDM_USER_DELETE_SELF_NOT_ALLOWED",
      "category": "policy",
      "severity": "blocking",
      "messageKey": "idm.user.delete.selfNotAllowed",
      "defaultMessage": "The current user account cannot delete itself."
    }
  ]
}
```

The executing delete endpoint must still reject the same self-delete request.

## Status behavior

| Situation | HTTP status | Body |
|---|---:|---|
| executable | `200` | `executable: true` |
| blocked by policy/state/dependency for visible target | `200` | `executable: false` with reason |
| invalid precheck request | `400` | standard API error |
| missing authentication | `401` | standard API error |
| missing operation permission | `403` | standard API error |
| target not found | `404` | standard API error |
| conflict while evaluating a precheck request | `409` | standard API error |
| technical failure | `500` | standard API error |

A client must treat precheck results as stale-capable. Execution may still fail after a successful precheck.

## Policy reuse requirement

The backend must structure command-specific rules so that precheck and execution share the same decision source.

Recommended structure:

```text
<Command>Policy
  evaluate(actor, target, request?) -> CommandPrecheckDecision
  assertAllowed(actor, target, request?) -> void

<Command>PrecheckHandler -> uses <Command>Policy.evaluate(...)
<Command>Handler         -> uses <Command>Policy.assertAllowed(...)
```

Equivalent naming is allowed. The important invariant is that rule drift between precheck and execution is testable and avoided.

## DTO and Java support assessment

A reusable DTO contract is useful and should later be introduced in the Springmaster shared Java foundation once the reference implementation is ready.

Recommended future support:

- `CommandPrecheckResponseDTO`;
- `CommandPrecheckReasonDTO`;
- `CommandPrecheckDecision` or equivalent internal decision type;
- test helpers for executable/blocking decisions;
- OpenAPI assertions for response shape.

A reusable generic Spring MVC controller interface is not recommended as the primary abstraction. The concrete endpoint path, method, security annotation, request DTO and operation id vary per aggregate and command. Controller methods should stay explicit and delegate to command-specific application services or use-case handlers.

## OpenAPI requirements

When a backend exposes a precheck endpoint, OpenAPI must document:

- the endpoint path and method;
- operation id and tags according to the future OpenAPI naming standard;
- `200` response schema with the command precheck DTO semantics;
- `400`, `401`, `403`, `404`, `409` and `500` error responses where applicable;
- request DTO for `POST` prechecks;
- security requirement for management prechecks.

## List and bulk command rule

List pages and bulk controls must not be forced into per-item prechecks by default.

Rules:

- list controls may evaluate only permission, selection state, busy state and confirmation;
- backend execution remains responsible for rejecting forbidden, unknown, stale or policy-blocked items;
- delete-multiple and other bulk commands follow the existing Springmaster bulk command standard;
- partial success is allowed only when the endpoint explicitly returns item-level outcomes and documents the semantics;
- the absence of per-item prechecks must not be treated as a security weakness because execution validation is mandatory.

## Future gates

Future gates should start as report-only and later become strict only after reference evidence exists.

Candidate checks:

1. Precheck endpoints match canonical path shape.
2. Precheck endpoints have no state mutation in controller tests.
3. `GET` prechecks do not require request bodies.
4. Response DTO exposes `commandId`, `executable` and `reasons` semantics.
5. Missing operation permission returns `403` rather than `200 executable=false`.
6. Policy-blocked visible targets return `200 executable=false`.
7. Precheck handler and execution handler reference the same policy/guard collaborator.
8. List/bulk commands are not incorrectly required to declare per-row prechecks.

Until these gates exist, this standard is documentation-first.

## Target-project boundary

This standard does not directly update IDM, Personnel, Contacts, Orders or any other target project. It provides the logical Springmaster standard that future target updates or independent application patches may follow.

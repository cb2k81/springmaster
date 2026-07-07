# CHANGELOG 000082 - springmaster command precheck capability standard

## Scope

Documentation-only root patch.

## Added

- Accepted `ADR-0011-command-precheck-and-capability-boundary.md`.
- Added `COMMAND_PRECHECK_ENDPOINT_STANDARD.md` under API standards.

## Updated

- ADR README lists ADR-0011 as an accepted ADR while keeping ADR-0008 through ADR-0010 reserved for their existing planned topics.
- API standards README links the command-precheck standard.
- Standards README records the command-precheck standardization step.
- Security permission boundary standard receives a short addendum clarifying the relationship between command prechecks, permissions and final command validation.
- ADR gap backlog records ADR-0011 as accepted and documents its accepted scope and deferrals.

## Decision

Command prechecks are optional, side-effect-free backend capability queries. They support UI command-control state but never replace command execution validation. Precheck and command execution must share the same backend policy/guard. List and bulk UIs are not required to perform per-item prechecks.

## Target-project boundary

This patch does not update IDM, Personnel, Contacts, Orders or generated target projects. Springmaster is the logical backend standard source; target-project supply remains a later explicit workflow.

## Validation

Documentation-only. No Maven build or test required by the validation policy.

---
documentId: ADR-0015
title: Controlled AI-Assisted Development Pilot

documentType: adr
status: accepted
authority: normative
scopeLevel: ecosystem
scopePaths:
  - springmaster/engineering
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-25
validFrom: 2026-07-25
lastReviewedAt: 2026-07-25
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# ADR-0015 Controlled AI-Assisted Development Pilot

## Context

The current chat-to-patch workflow provides strong delivery control but makes every development iteration cross the patch-artifact boundary. Small changes therefore repeatedly require export interpretation, patch assembly, transfer, dry-run, qualification and correction. Springmaster is intended to be the canonical source for methods, tooling, contracts and rollout decisions, and it already contains the governance, worktree, patch and generated-slice foundations needed for a controlled local-agent pilot.

A local coding agent can reduce the transport and iteration cost only if it cannot mutate the integration checkout, other repositories or undeclared paths. Model instructions alone are not a sufficient enforcement boundary. The pilot therefore needs a repository-owned contract, external worktrees and run roots, fail-closed pre- and post-checks, immutable task input, deterministic evidence and an explicit cutover decision.

## Decision

1. The first AI-assisted development pilot is restricted to the Springmaster repository. GWC, Personnel and all managed projects remain read-only and outside the writable pilot scope.
2. Until the project readiness gate reports `PROJECT_READY`, Cocondo Patch Toolkit remains the only canonical mutating delivery path for Springmaster.
3. Reaching `PROJECT_READY` authorizes only the start of Codex calibration. It does not authorize unrestricted agent development, automatic integration, push, target mutation or managed-project rollout.
4. Every writable agent task uses a detached disposable Git worktree created from an exact committed Springmaster base commit. The integration worktree is never the agent workspace.
5. Worktree, run, evidence and generated-artifact roots are absolute, externally configured paths outside every tracked Springmaster worktree.
6. Every task is bound to an immutable machine-readable task contract containing task identity, base commit, risk, allowed and forbidden paths, exact qualification commands, evidence requirements and explicit capability flags.
7. Agent tasks may not commit, push, switch branches, mutate `.git`, alter the task contract, change other repositories or write undeclared repository-root files.
8. Network access for agent-executed shell commands is disabled by the Codex sandbox. This boundary must be proven by negative calibration before writable Codex work becomes the pilot default.
9. The harness records pre-state, invocation identity, changed paths, post-state, qualification results and cleanup disposition outside the repository. A missing or inconsistent record blocks integration.
10. Integration remains a separate human-controlled action. The pilot harness does not merge, cherry-pick, commit to `main` or push.
11. The Business Partner dummy domain concept is the first end-to-end pilot input. It is transformed in explicit stages: Fachkonzept, canonical intent, generated-slice specification, application UI specification, GWC implementation manifest and generated application.
12. Codex may not change a pilot input, its acceptance contract and the implementation being evaluated in one task. Oracle, generator and generated output changes are separated.
13. The pilot stops immediately on a real boundary violation, unauthorized write, missing evidence, non-deterministic clean rerun or unexplained integration-worktree drift.
14. Patch artifacts remain the required delivery mechanism before cutover and for later external, recovery, release, audit or cross-project boundaries. Normal Codex implementation iterations after successful calibration use isolated Git worktrees and reviewable diffs.

## Readiness levels

| Level | Meaning | Codex use |
|---|---|---|
| `PRE_CUTOVER` | Governance or harness prerequisites are incomplete. | Forbidden. |
| `PROJECT_READY` | Repository governance, contracts, harness and reference input are qualified. | Calibration may start. |
| `CALIBRATION_REQUIRED` | Project readiness is proven, but Codex sandbox and behavioral boundaries are not yet proven. | Read-only and controlled negative calibration only. |
| `PILOT_WRITE_READY` | Two accepted calibration tasks and all runtime boundary probes succeeded. | Writable Springmaster pilot tasks allowed. |
| `PILOT_COMPLETED` | End-to-end generation, repeatability and evolution criteria succeeded. | Rollout decision may be prepared separately. |

The patch implementing this ADR intentionally stops at `PROJECT_READY`. The first Codex invocation is a later explicit cutover action.

## Consequences

- Springmaster becomes the single development and rollout source for the agent method instead of distributing ad-hoc files across business projects.
- The repository gains a strict project-readiness gate and a non-executing agent-task harness before Codex is invoked.
- Existing report-only engineering governance remains report-only. Strict pilot boundaries are sourced by this accepted ADR and the active AI Agent Development Governance.
- The current Business Partner generated-slice golden fixture remains a technical fixture. It is not treated as the authoritative Fachkonzept or UI specification.
- A successful project-readiness gate is necessary but not sufficient for writable Codex usage.

## Rejected alternatives

- Running Codex directly in the integration checkout: rejected because rollback, scope and foreign-change boundaries would depend on convention.
- Treating `AGENTS.md` as the sole safety mechanism: rejected because instructions are not an operating-system or transaction boundary.
- Piloting simultaneously in GWC, Personnel and Springmaster: rejected because failures and method changes would be distributed and difficult to attribute.
- Letting the agent modify tests, generator and expected output in one task: rejected because it permits self-confirming results.
- Automatically accepting or integrating after a successful agent run: rejected because review and promotion are deliberate boundaries.

## Verification and promotion

Project readiness is evaluated by `bin/codex-pilot-ready.sh project --live --check`. The gate is strict and read-only. Its fixtures must cover positive, finding and tool-error behavior. Writable Codex use requires a later calibration record and a separate explicit promotion change.

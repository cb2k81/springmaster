---
documentId: SPRINGMASTER-MAINTENANCE-RECOVERY
title: Maintenance and Recovery Contract
documentType: guide
status: active
authority: informative
scopeLevel: component
scopePaths:
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-09-02
validFrom: 2026-09-02
lastReviewedAt: 2026-09-02
reviewBy: 2027-03-02
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-006
---

# Maintenance and Recovery Contract

The normative authority is ADR-0020. The machine-readable record contract is `contracts/governance/engineering/maintenance-recovery-contract.json`; this guide explains its supported use. It creates neither a second patch engine nor a general break-glass command.

## Purpose and decision boundary

Maintenance recovery is permitted only when a required standard entrypoint is demonstrably defective, incomplete or unsuitable for its own repair. The repair occurs in an isolated branch or detached worktree at an exact baseline. The `detached` record flag describes which of these two supported isolation forms is used; it is not a requirement to detach. The integration worktree itself remains forbidden. The defective entrypoint is not a bootstrap prerequisite; unaffected repository, language or build verifiers provide the initial safe checks.

The path restores the standard entrypoint. It does not authorize direct `main` mutation, push, cross-project mutation, scope/capability expansion, acceptance, or a false PASS. Integration and delivery remain separate dispositions with their existing human and cpatch boundaries.

## Record

A `springmaster.maintenance-recovery.v1` record captures:

- the defective component, entrypoint, reason code, category and explanation;
- baseline commit, a non-empty integration ref and integration-tree fingerprint plus the isolated branch/worktree binding;
- exact authorized and actually changed repair paths;
- authorized and used capabilities;
- the mandatory prohibitions `direct-main-mutation`, `push` and `cross-project-mutation`, and any observed violation;
- bootstrap commands independent of the defective entrypoint;
- targeted and final qualification executions, with non-empty evidence references for executed outcomes such as `passed`, `passed-with-findings`, `blocked` or `tool-error`;
- integration and delivery disposition;
- recoverability, maintenance eligibility and the smallest safe next action.

Classification reuses change classes and risks from `change-classification-contract.json`. Qualification IDs come from `engineering-profile-contract.json`; execution states come from `engineering-evidence-contract.json`; completion truth remains governed by `engineering-completion-contract.json`. The recovery record cannot redefine these vocabularies.

## Progressive flow

```text
exact baseline + isolated branch / detached worktree
  -> unaffected bootstrap/verifier
  -> edit only authorized repair paths when maintenance is allowed
  -> targeted qualification of the repaired entrypoint
  -> normal full qualification boundary
  -> reviewable integration/delivery disposition only after qualification
```

A recovery that requests an integration or delivery disposition requires targeted and final qualification to be recorded as `passed`; a passed qualification requires exit code `0` and at least one evidence reference. A blocked recovery record may instead keep qualification `blocked` or `not-executed`, but then both integration and delivery disposition remain `not-requested`. A final PASS before targeted PASS, a qualified repair declared non-recoverable or maintenance-disallowed, or a forbidden observed operation makes the record invalid.

## Validation

Validate contracts and a concrete record with:

```bash
./bin/engineering-contracts.sh --check contracts
./bin/engineering-contracts.sh --check maintenance-recovery --input <record.json>
```

`bin/engineering-contracts-it.sh` provides a hermetic canary. It copies an intentionally defective gate into isolated fixture trees, performs an unaffected bootstrap check, repairs only the authorized copy, runs targeted verification and the normal full fixture boundary, and proves the integration tree and unrelated sentinel remain byte-identical. A second positive record proves that an attached isolated branch is as valid as a detached worktree, and a positive blocked record proves fail-closed disposition without false qualification. Negative fixtures reject path and capability expansion, direct-main mutation, push, false PASS, missing final qualification, empty worktree/integration bindings, missing PASS evidence, and contradictory recoverability flags.

## Blocking result

If recovery is not safe, report the defect `reasonCode`, its `PRODUCT|TOOLING|ENVIRONMENT|GOVERNANCE` category, coherent `recoverable` / `maintenanceAllowed` flags, and a non-empty `safeNextAction`. `maintenanceAllowed=true` requires `recoverable=true`. A blocked record may have no actual repair paths and may leave final qualification `not-executed`; it must keep integration and delivery disposition at `not-requested`. Unknown or untrusted state remains fail-closed. A blocked record never broadens authority.

## Lifecycle

| Date | State | Reason |
|---|---|---|
| 2026-09-02 | active | M-001 materialized ADR-0020 as a validated recovery record and hermetic self-repair canary. |
| 2026-09-02 | active | Post-accept review aligned attached-branch vs. detached-worktree semantics, blocked records, evidence references and non-empty baseline/worktree bindings with ADR-0020. |

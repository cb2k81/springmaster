---
documentId: SPRINGMASTER-S006-P0-TOOLING-INVENTORY
title: Sprint 006 P0 Tooling and Recovery Inventory
documentType: report
status: final
authority: evidence
scopeLevel: ecosystem
scopePaths:
  - springmaster/sprints
  - springmaster/engineering
appliesTo:
  - springmaster
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-09-02
validFrom: 2026-09-02
lastReviewedAt: 2026-09-02
reviewBy: 2026-09-30
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-006
---

# Sprint 006 P0 Tooling and Recovery Inventory

## Result

This report materializes the immutable A002 live inventory used to plan M-001. It does not reclassify live state from historical documentation and does not claim Trusted-Host qualification, integration, delivery or acceptance.

```text
P0_INVENTORY_RESULT=READY_FOR_IMPLEMENTATION
PATCH_PRODUCER_GAP_CLASS=VERSION_SKEW+DISTRIBUTION_GAP+ADOPTION_GAP+DOC_GAP+DX_GAP
TRUE_GAP_CURRENT=false
SPRINT_PRODUCER_PRESENT=false
SELF_REPAIR_PATH=partial
STATE_TRUTH_GAP_COUNT=0
P0_BLOCKER_COUNT=0
PROPOSED_M001_PATH_COUNT=10
```

## Authority classification

| Class | Source-bound examples | M-001 treatment |
|---|---|---|
| Safety invariant | no direct `main` mutation, no push, no cross-project mutation, exact scope and truthful qualification | fail-closed and mechanically checked |
| Accepted architecture/product contract | ADR-0020; existing patch, agent and human-accept trust boundaries | reused without competing authority |
| Standard process | isolated worktree, targeted verification, final qualification, separate integration/delivery disposition | represented as a recovery record |
| Guidance/automation | operator sequence and diagnostic wording | documented; creates no new norm |

The distinction is material: recovery may replace a defective process prerequisite, but it may not bypass a safety invariant or silently alter an accepted product contract.

## Gap disposition

The live patch producer is not a true current implementation gap. The observed producer problem is classified as version skew, distribution, adoption, documentation and developer-experience drift. Sprint-specific producer work is absent and belongs to M-002, not M-001. M-001 therefore adds no cpatch producer, supervisor or general break-glass command.

The self-repair path was partial because ADR-0020 authorized recovery but no machine-checkable record and hermetic repair canary existed. M-001 closes that materialization gap through the engineering-contract validator, a record contract, fixtures and an operator guide. State truth has no P0 gap and is not changed here.

## Required record and canary

The maintenance record binds defect identity, reason/category, exact baseline, isolated worktree, paths, capabilities, forbidden operations, unaffected bootstrap, progressive qualification, disposition and actionable recoverability. Its vocabularies reference the four existing engineering contracts.

The positive fixture repairs an intentionally defective copied gate without calling it as the bootstrap prerequisite. It proves:

- only `bin/defective-gate.sh` changes in the isolated fixture;
- the integration fixture tree and unrelated sentinel remain byte-identical;
- the repaired gate passes targeted verification and then the full fixture boundary.

Negative fixtures cover path expansion, capability expansion, direct-main mutation, push, false PASS and missing final qualification.

## Developer-experience baseline

For later before/after field qualification, measure only where useful:

- manual decisions and user interactions;
- separately started tool/test processes;
- time to first actionable result and qualified candidate;
- success/failure evidence file count and byte size;
- manual protocol, manifest and archive construction steps;
- recovery steps until the standard path works again.

These metrics diagnose friction; they are not a mandatory evidence burden for every normal change.

## M-001 scope result

The exact ten proposed paths are sufficient. No accepted authority conflict, external dependency or P0 blocker is present. M-001 remains subject to repository and Trusted-Host qualification; this report records implementation scope and inventory truth, not final acceptance.

## Lifecycle

| Date | State | Reason |
|---|---|---|
| 2026-09-02 | final | Immutable A002 planning inventory and M-001 recovery disposition materialized. |

---
documentId: SPRINGMASTER-SPRINT-004-FIELD-QUALIFICATION
title: Sprint-004 Personnel 000248 Field Qualification Report
documentType: report
status: draft
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-23
validFrom: null
lastReviewedAt: 2026-08-23
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-004
---

# Sprint-004 Personnel 000248 Field Qualification Report

## Bound source

The qualification uses only the immutable Personnel export `personnel_export_full_2026-08-22_15-55-17-917Z.zip`, SHA-256 `541b6f97d22ca6aeb532f6d3f25f6f09fc16591ef7161791b5160a98f6cffb61`, at accepted commit `1094199a84aeb809865d2992ef2aab65d8488226` and patch `000248_personnel_workspace_post_wsf2_contract_guardrails`.

All 17 paths changed by unqualified candidate patch `000249_personnel_workforce_discovery_contract_freeze` are enumerated in the machine-readable evidence and excluded as positive references. Personnel was not accessed or mutated by this task; the authorized prompt evidence supplied the source facts.

## Result

| Case | Springmaster representation | Result |
|---|---|---|
| RW-01 | `EXPECTED_VERSION`, `SINGLE_AGGREGATE`, `OPTIMISTIC` | PASS |
| RW-02 | `EXPECTED_VERSION_SET`, multi-root application orchestration | PASS |
| RW-03 | `MIXED`, complete application-specific lock set/order, post-lock revalidation | PASS |
| RW-04 | `TEMPORAL_READ`, `TEMPORAL_RELATION`, injected business date | PASS |
| RW-05 | `PROJECTION_READ` with explicit response schema | PASS |
| RW-06 | management operation permission plus request target/data visibility | PASS |
| RW-07 | workspace and UI reload state remain outside backend operation/effect semantics | PASS |

The result is 7/7 PASS with no general contract gap, new operation kind, new operation role or Personnel-specific Core dependency. The supplied V3 technical Personnel `operationId` values used by fixtures are source evidence. Fixture `operationKey`, `/api/field-evidence/...` path, resource and permission values are Springmaster evidence mappings and are not claimed as Personnel-published metadata. RW-01 uses an explicitly synthetic technical identity because the accepted input did not supply a CareerGroup operationId.

## Product consequences

- The field-proven business-date semantics are re-authored as the framework-free `de.cocondo.system.time` boundary.
- The field-proven single-version comparison is re-authored without Spring DAO coupling; stale body tokens use the standard 409 adapter.
- Complex-mutation invariants strengthen the active transaction/consistency standard while concrete phases, aggregate orders, lock modes and retry behavior remain application-owned.
- No coordinator, lock manager, temporal framework, workspace runtime or dependency was introduced.

## Evidence and qualification boundary

Machine-readable evidence:

- `contracts/api/evidence/sprint-004/personnel-000248-field-qualification.v1.json`
- `contracts/api/evidence/sprint-004/sprint-004-implementation-result.v1.json`
- `contracts/api/fixtures/sprint-004/fixture-index.v1.json`

The implementation result is intentionally non-terminal: Sprint phase may advance to qualification, while overall status remains active and canonical closure awaits Trusted-Host qualification.

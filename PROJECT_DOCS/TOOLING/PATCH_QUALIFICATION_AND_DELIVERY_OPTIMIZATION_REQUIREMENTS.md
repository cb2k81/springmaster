---
documentId: SPRINGMASTER-PATCH-QUALIFICATION-DELIVERY-OPTIMIZATION-REQ
title: Patch Qualification and Delivery Optimization Requirements
documentType: requirements
status: active
authority: normative
scopeLevel: component
scopePaths:
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-08-30
validFrom: 2026-08-30
lastReviewedAt: 2026-08-30
reviewBy: 2026-10-31
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Patch Qualification and Delivery Optimization Requirements

## Purpose

Springmaster must reduce repeated operator, chat and bundle-specific orchestration without weakening patch, qualification, evidence or human-accept safety. Reusable workflow logic belongs in canonical Springmaster tooling or explicit managed-project extension points instead of being repeatedly reimplemented in delivery ZIPs or project-local shell wrappers.

These requirements consolidate field evidence from Springmaster Sprint 005 and read-only reviews of Personnel and CBIX WebLib. They define a future R5 tooling objective; they do **not** claim that the optimization is already implemented.

## Design principles

1. **Standardize repeatable mechanics.** Preflight, inventory, immutable-input binding, qualification planning, durable observation, result receipts, diagnostics, packaging checks and resume should be callable standard functions where their semantics are generic.
2. **Keep one authority per concern.** No second patch engine, no second durable process supervisor, no duplicate run-state machine and no competing manifest/evidence truth.
3. **Fail closed.** Unknown scope, ambiguous impact, changed inputs or incomplete evidence select stronger qualification or stop; they never silently reduce gates.
4. **Prefer declarative deliveries.** A normal delivery bundle should primarily declare inputs, intended scopes and requested standard operations. It should not embed a bespoke lifecycle implementation.
5. **Cheap failures first.** Deterministic low-cost failures are detected before background workers or expensive test suites start.
6. **Risk is not test breadth by itself.** High governance impact can require strict governance/contract evidence without automatically requiring unrelated runtime suites; broad runtime impact can require full regression even from a small file diff.
7. **Evidence is explicit.** `PASS`, `FAIL`, `SKIPPED_BY_POLICY`, `NOT_REACHED` and reused evidence must remain distinguishable.
8. **Tooling changes are R5.** The optimizer must never use its own reductions to self-qualify its implementation.

## Functional requirements

### OPT-REQ-001 - Canonical impact classification

Qualification planning must combine declared manifest/scope information with the actual Git diff and registered contract/test relationships. Multiple impact classes are allowed. Unknown paths or contradictory declarations escalate fail-closed.

At minimum the model must distinguish documentation/governance, tests-only, configuration/types, domain/application, public API, security, database/migration, build/tooling, patch/release tooling and release closure.

### OPT-REQ-002 - Executable gate policy

The existing engineering change/risk classification, test-suite contracts, gate registry and cpatch scope/risk model must feed one versioned, machine-readable qualification policy. The concrete plan is materialized before execution and records why every gate is required or policy-skipped.

### OPT-REQ-003 - Foreground cheap-fail standard function

Before a costly/durable qualification starts, canonical tooling must be able to perform at least bundle/artifact hash and member checks, baseline/branch/cleanliness checks, manifest/scope validation, shadow/candidate apply where applicable, `git diff --check`, cheap static guards and affected documentation/governance gates.

A cheap deterministic failure must not unnecessarily start a background worker.

### OPT-REQ-004 - Risk-proportional qualification

A proven documentation/governance-only change runs the affected documentation/governance contracts without automatically replaying unrelated application/runtime integration suites. Full regression remains mandatory for Tooling/R5, release closure, public/cross-slice API, security, database/migration, broad shared runtime changes, uncertain impact and explicit compatibility locks.

### OPT-REQ-005 - Contract-based test selection

Test selection must be driven by registered contracts and impact relationships, not simply by the names of changed files. Shared configuration, fixtures, normative documents, public API, security policy and migration inputs can widen the affected set.

### OPT-REQ-006 - Materialized gate decisions and receipts

Each gate result records at least gate ID, decision, policy version, impact classes, reason, execution/reuse source, status, command identity where executed and evidence/log hash. Policy skip is not counted as test PASS.

### OPT-REQ-007 - Canonical durable run/receipt locations

Long-lived run and qualification receipts must live under canonical external/Git-common run or artifact roots. `patches/work/` remains a current diagnostic handoff workspace and cannot be used as durable parent state across downstream writers that may clean it.

Runtime logs created by standard tooling must never make the integration checkout dirty before cpatch/process-ops operations.

### OPT-REQ-008 - Standard observer and result helpers

Standard functions should encapsulate durable start, status/wait/result, strict terminal-state checks and diagnostic handoff. Once a durable run ID exists, an observer failure must not trigger a blind restart. The canonical run state is consulted first.

### OPT-REQ-009 - Direct canonical patch operations

Patch dry-run and patch accept remain direct `process-ops`/cpatch operations. Generic wrappers must not nest them in an additional detached supervisor. Candidate workspace/create uses the Candidate-local cpatch root; inspect/plan/dry-run/accept use the clean integration root.

### OPT-REQ-010 - Delivery packaging allowlist

Final delivery construction must fail closed on undeclared members such as `__pycache__`, `.pyc`, editor backups, temporary logs or secrets. The allowlist/manifest check runs after local syntax/build checks and immediately before deterministic ZIP construction.

### OPT-REQ-011 - Result and export receipt consistency

A final state that claims an external export must carry and verify export path, SHA-256 and required metadata identities. Full export is a policy decision for handoff/release/audit, not an unconditional per-patch side effect.

### OPT-REQ-012 - Safe resume and evidence reuse

A later failed step may resume without blindly replaying already successful expensive gates only when baseline, patch/content, policy, gate inputs and required outputs are cryptographically unchanged. Changed inputs invalidate reuse. A previous failure is never skipped.

Content-addressed per-gate reuse, as demonstrated by CBIX-style input/output attestations, is a P1 optimization after the simpler deterministic planner/receipt layer is proven.

### OPT-REQ-013 - Managed-project overlays

Generic planner, evidence, receipt and process mechanics belong in Springmaster. Managed projects may supply project-specific test groups, impact mappings and policy overlays through defined extension points. They must not fork a competing patch core or evidence lifecycle.

### OPT-REQ-014 - Non-interactive background prerequisites

Background gates cannot wait for interactive password/sudo prompts. Privileged prerequisites are resolved in foreground or fail fast/non-interactive with bounded timeout and explicit failure class.

### OPT-REQ-015 - Standard delivery orchestration interface

Springmaster should expose a compact standard operation for the recurring lifecycle:

```text
preflight -> prepare/bind candidate -> targeted qualification -> cpatch create/inspect/plan -> canonical dry-run -> result/diagnostic receipt
```

The interface must preserve the separate human accept boundary. The goal is to make ordinary delivery bundles mostly declarative and drastically reduce copied shell control logic.

## Required acceptance scenarios for the future R5 implementation

The implementation is not complete until automated fixtures prove at least:

- documentation/governance-only patch: affected governance evidence runs, unrelated full runtime regression is `SKIPPED_BY_POLICY` with reason;
- whitespace/EOF defect: fails before durable background start;
- public API patch: HTTP/security/OpenAPI and full required regression run;
- database/migration patch: migration/DB gates and full regression run;
- tooling patch: classified R5 and fully self-qualified without self-exemption;
- unknown scope/path: escalates or stops fail-closed;
- unexpected delivery member: packaging fails before final ZIP;
- export final state: export receipt fields are complete and hash-verified;
- observer interruption after durable start: canonical run is resumed/observed, not duplicated;
- unchanged expensive gate: reuse only with exact input/policy/output attestation;
- changed baseline, patch or policy: reuse is rejected;
- no nested `setsid`/`nohup`/second supervisor around canonical process-ops ownership.

## Priority

### P0

- executable impact/gate planner using existing Springmaster contracts;
- cheap foreground preflight;
- standard durable observer/result/diagnostic helpers;
- runtime/log/workspace hygiene;
- delivery member allowlist;
- result/export receipt consistency;
- standard delivery orchestration interface.

### P1

- content-addressed per-gate evidence reuse and resume;
- explicit managed-project impact/test overlays;
- shadow/target duplicate-work reduction where identical inputs can be proven.

### P2

- advanced dependency graph or incremental build/test optimization only if the explicit contract/scope matrix proves insufficient.

## Non-goals

This work must not reduce required security, database, release or R5 qualification; invent a parallel Personnel/CBIX/Springmaster patch engine; replace `process-ops`; automate patch accept; or claim PASS for a policy-skipped or reused gate without explicit provenance.

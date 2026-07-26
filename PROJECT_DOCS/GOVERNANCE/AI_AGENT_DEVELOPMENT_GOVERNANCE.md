---
documentId: DOC-GOV-0010
title: AI Agent Development Governance
documentType: governance
status: active
authority: normative
scope: repository
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
reviewBy: 2027-01-25
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# AI Agent Development Governance

## 1. Purpose and scope

This governance defines the controlled local AI-agent development lifecycle for the Springmaster pilot. It applies to analysis, implementation, qualification and review performed with Codex or an equivalent local coding agent.

It does not authorize AI-agent use in GWC, Personnel, generated projects or managed projects. Such adoption requires a separate decision and delivery profile after the Springmaster pilot is completed.

## 2. Canonical boundaries

This governance is canonical for:

- pilot lifecycle and cutover status;
- task-contract requirements;
- agent worktree, run and evidence boundaries;
- separation of input, oracle, implementation and generated result;
- prohibited agent actions;
- calibration, stop and success criteria.

The following sources remain canonical for their existing subjects:

| Subject | Canonical source |
|---|---|
| technical change lifecycle and evidence | Engineering Governance and its report-only contracts |
| Git patch transactions before cutover | ADR-0012 and Cocondo Patch Toolkit contracts |
| process observation and recovery | ADR-0014 and Process Operations Guide |
| API, persistence, security and architecture rules | accepted ADRs and active technical standards |
| test and gate semantics | Test Governance, Quality Gate Governance and their report-only contracts |
| directory and artifact placement | Project Directory Governance and directory contract |

If these sources conflict, the conflict is resolved before the task starts. An agent must not choose a rule silently.

## 3. Pilot lifecycle

### 3.1 PRE_CUTOVER

In `PRE_CUTOVER`:

- Codex execution is forbidden;
- Springmaster changes are delivered through Cocondo Patch Toolkit;
- governance, contracts, harness and reference inputs are implemented and qualified;
- the readiness gate may be run in candidate mode during patch qualification and live mode after integration.

### 3.2 PROJECT_READY

`PROJECT_READY` means all repository-owned prerequisites are proven:

- ADR-0015 is accepted;
- this governance is active;
- pilot and task contracts are valid;
- the agent-task harness and negative fixtures pass;
- the Business Partner pilot input and acceptance contract are frozen;
- pre-cutover mutation remains bound to Cocondo Patch Toolkit;
- the cutover command is still disabled.

This state authorizes only the controlled Codex calibration boundary.

### 3.3 CALIBRATION_REQUIRED

The first Codex activity is not feature development. It consists of:

1. a read-only source and rule audit;
2. a negative boundary calibration in a disposable task worktree;
3. a small implementation task with immutable human-provided oracle;
4. a small generator or validator task with a separately reviewed golden result.

Writable pilot tasks remain blocked until both calibration implementation tasks are accepted and every negative probe is correctly blocked or contained.

### 3.4 PILOT_WRITE_READY

The state may be promoted only by a separate committed change that references immutable calibration evidence. The promotion must not be performed by the Codex task being evaluated.

### 3.5 PILOT_COMPLETED

Completion requires the end-to-end Business Partner chain, three clean deterministic reruns, a controlled V1.1 concept change, preserved manual extension points, complete traceability and measured efficiency improvement without a safety regression.

## 4. Task contract

Every agent task must be defined before worktree creation. The task contract is immutable for the lifetime of the task and contains at least:

- `taskId`, pilot ID, repository ID and mode;
- exact `baseCommit` and integration branch;
- risk class and change classes;
- allowed paths and forbidden paths;
- maximum changed file count and maximum added bytes;
- explicit booleans for test, governance, contract, commit, push and network capabilities;
- exact qualification commands as argument arrays;
- required evidence and completion criteria.

The task contract is stored in the external run root. It is never generated or rewritten inside the task worktree.

A material scope change ends the current task. A new task contract and worktree are required.

## 5. Filesystem and Git boundaries

1. The integration worktree must be clean before task preparation.
2. The task worktree is detached at the exact base commit.
3. The worktree path and run path must be outside the repository and Git common directory.
4. Symbolic links in changed paths are forbidden.
5. `.git` mutation, submodule introduction and nested repository creation are forbidden.
6. Root-level writes are forbidden unless the exact root path is allowed in the task contract.
7. The task must not change its own base commit or create a commit unless a later governance revision explicitly enables it. Pilot V1 sets `mayCommit=false`.
8. Integration `HEAD`, branch and working tree are rechecked after the task.
9. Cleanup never discards a non-empty task worktree implicitly. A review bundle or explicit discard decision is required.

## 6. Command and network boundaries

- Qualification commands are exact argument arrays from the task contract. Shell strings and implicit evaluation are forbidden.
- The harness does not offer a generic arbitrary-command operation.
- Codex shell network access is disabled during the pilot. Network-dependent dependency installation is a separate human-controlled preparation step and is not part of an agent task.
- Push, remote mutation, branch creation, destructive integration-tree Git commands and credential acquisition are forbidden.
- Codex approvals do not replace these boundaries. A request to escape them is a blocked result, not an invitation to approve.

## 7. Evidence

The external run root contains at least:

- immutable task contract and its SHA-256;
- preparation record;
- integration and task-worktree pre-state;
- changed-path and post-state report;
- qualification command records and bounded logs;
- final result and cleanup disposition.

Evidence records use deterministic JSON with UTC timestamps only for event identity. Hash comparison excludes or normalizes volatile timestamps.

No agent evidence, prompt, checksum, run record or generated application is written to the repository root.

## 8. Separation of responsibilities

One task may not simultaneously change:

- Fachkonzept and the implementation derived from it;
- generator and all of its expected outputs without an independent oracle review;
- governance boundary and code relying on the relaxed boundary;
- task harness and its own acceptance evidence;
- implementation and the acceptance criteria used to judge it, unless test modification is explicitly authorized and independently reviewed.

Human approval is mandatory for:

- the frozen Fachkonzept;
- the Application UI Spec before application generation;
- calibration acceptance;
- integration of any writable Codex result;
- promotion to `PILOT_WRITE_READY` and `PILOT_COMPLETED`.

## 9. Business Partner reference input

The active pilot Fachkonzept is `PROJECT_DOCS/DEMO/BUSINESS_PARTNER_CODEX_PILOT_FACHKONZEPT.md`. Its machine-readable acceptance contract is `contracts/pilots/codex/business-partner-pilot-acceptance.json`.

The existing `GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml`, IR and patch blueprint remain technical golden fixtures. They are useful comparison inputs but are not the source of business truth and do not authorize source rendering or target mutation.

## 10. Stop criteria

The pilot stops and returns to `PRE_CUTOVER` or a blocked state when any of the following occurs:

- a write outside the task worktree or declared external run roots;
- integration-worktree mutation or drift;
- another repository is modified;
- an unauthorized network operation succeeds;
- the task contract or evidence is changed by the agent;
- a forbidden path is changed;
- a missing run record, ambiguous result or non-reproducible clean rerun;
- a manual repository repair is required after a run;
- an agent changes the oracle to make its implementation pass without explicit authorization.

The incident is retained outside the repository and addressed through a new patch-controlled hardening change.

## 11. Success measures

Safety targets are absolute:

- zero writes outside the task worktree;
- zero changes to other repositories;
- zero direct agent changes to `main`;
- zero unauthorized commands or network operations;
- zero undeclared changed files;
- zero new repository-root artifacts;
- complete evidence for every task;
- zero manual repository cleanup actions.

After at least five writable pilot tasks, the efficiency targets are:

- at least 30 percent lower elapsed time to a reviewable diff;
- at least 80 percent fewer manual transfer and patch-rebuild steps;
- at least 50 percent fewer manual interventions;
- median review correction rounds not greater than one;
- at least 70 percent first-pass targeted qualification success.

Efficiency never compensates for a safety failure.

## 12. Rollout boundary

This governance has no automatic Project-New or managed-project effect. Later rollout requires:

- a completed Springmaster pilot report;
- a versioned reduced adoption profile;
- target read-only comparison;
- disposable target acceptance;
- explicit authorization for each real target mutation.

## 13. Lifecycle

| Date | Previous | New | Reason |
|---|---|---|---|
| 2026-07-25 | - | active | Springmaster-only pre-cutover governance, strict project-readiness boundary and Codex calibration lifecycle established. |

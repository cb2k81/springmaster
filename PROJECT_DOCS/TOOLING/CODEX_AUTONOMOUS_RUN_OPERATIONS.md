---
documentId: SPRINGMASTER-CODEX-AUTONOMOUS-RUN-OPERATIONS
title: Codex Autonomous Logical Run Operations
documentType: guide
status: active
authority: informative
scopeLevel: component
scopePaths:
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-25
validFrom: 2026-08-30
lastReviewedAt: 2026-08-30
reviewBy: 2027-02-28
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-005
---
# Codex Autonomous Logical Run Operations

`codex-autonomous-run` composes the existing Agent Task V2, Host Sandbox, Change Bundle, `process-ops` and cpatch boundaries into one durable Logical Run. It adds no new security authority. Its normal terminal success is `PREACCEPT` with `nextAction=HUMAN_ACCEPT_REQUIRED`; it has no patch-accept or push operation.

## Immutable input

Create a JSON document conforming to `contracts/governance/agent/codex-autonomous-run-contract.schema.json`. It embeds the complete authorized `springmaster.agent-task.v2` template, original prompt, explicit model, finite attempt/active-time budgets and local cpatch name/title/scope. The runner derives physical IDs as `<logicalRunId>-A001`, `-A002`, and so on. Every authorization/oracle field except `taskId` is byte-compared across attempts.

The external artifact root and task/run/worktree roots must already be configured and authorized for the existing primitives. The integration checkout must be clean on the contract base commit.

## Operator interface

```bash
./bin/codex-autonomous-run.sh start --contract <logical-run.json>
./bin/codex-autonomous-run.sh status <logical-run-id>
./bin/codex-autonomous-run.sh result <logical-run-id>
./bin/codex-autonomous-run.sh resume <logical-run-id>
```

`start` hash-binds the request below `${COCONDO_ARTIFACT_ROOT}/codex-autonomous-runs/<logical-run-id>/` and delegates the outer worker to `process-ops run-start --singleton-key`. Repeating the same start reuses the singleton. A different request under the same ID fails closed. `status` is a read-only state observer. `result` requires a terminal Logical Run. `resume` can reacquire a terminal outer process only while Logical Run state is nonterminal; it reconnects to an already started physical invocation and never prepares or invokes that consumed task ID again. In particular, `invoke-start` may return a durable `runId` while the separately persisted Agent Task still reports `PREPARED` and `codexInvocation=NOT_RECORDED`. The observer follows that durable run to terminal evidence; it does not interpret the lifecycle lag as permission for another invocation.

All commands emit compact JSON containing the Logical Run ID, state, current attempt ordinal/ID where applicable, failure/blocker class, process run ID where applicable, and patch/dry-run identities at Pre-Accept.

## State and evidence

`request.json` and `request.sha256` are immutable. `state.json` is atomically replaced and follows the state schema. Per-attempt contracts, prompts, raw Host evidence and diagnostic qualification logs live under `attempts/A<n>/`; repair packets and change bundles have separate immutable directories. Raw Host evidence is never rewritten.

Ordinary repository-content qualification failures create one packet containing the complete safe diagnostic sweep, bounded log tails, full-log hashes, changed paths, worktree/failure fingerprints and successor/bundle binding. Qualification commands are executed as their declared argv arrays without shell evaluation. A final candidate must pass a complete fresh `agent-task qualify`; partial prior PASS results are not reused.

## Repair and stop classes

Compiler, test, contract, fixture, documentation, Sprint/gate, OpenAPI/golden and deterministic build failures inside fixed scope are repair signals. Successors begin at the original base and receive predecessor bytes only through a schema-conformant immutable Change Bundle. The existing bundle apply verifier checks source/target hashes and normalizes declared `100644`/`100755` modes independent of `umask`.

Terminal blockers include `SCOPE_EXPANSION_REQUIRED`, `CAPABILITY_EXPANSION_REQUIRED`, `ORACLE_CHANGE_REQUIRED`, `SECURITY_BOUNDARY_VIOLATION`, `INTEGRATION_BASE_DRIFT`, `NORMATIVE_DECISION_REQUIRED`, `EXTERNAL_DEPENDENCY_REQUIRED`, `HOST_TOOL_ERROR`, `NONDETERMINISTIC_FAILURE`, `NO_PROGRESS` and `REPAIR_BUDGET_EXHAUSTED`. Malformed/ambiguous evidence is `MALFORMED_EVIDENCE`. Identical failure fingerprints with unchanged bytes stop as `NO_PROGRESS`.

The sole Host false-negative exception is an otherwise FAILED raw invocation with Codex/execution exit 0, completed execution, zero parse errors, at least one completed turn, zero failed turns, and only error items matching `in-process app-server event stream lagged; dropped N events` for positive decimal `N`. The Logical Run records `TRANSPORT_DEGRADED_CONTINUE`; the raw FAILED evidence remains unchanged. Mixed or unknown errors stop as `HOST_TOOL_ERROR`.

## Pre-Accept boundary

After fresh qualification, the trusted worker creates the verified noncanonical Agent Task handoff, materializes and commits a separate candidate, runs cpatch create/inspect/plan, and starts the canonical dry-run through `process-ops`. It verifies that integration `main` remains clean at the original base before persisting `PREACCEPT`.

Human patch acceptance remains a separate operator decision. Automatic patch accept, agent commit, direct integration mutation, push and cross-project mutation are forbidden.

## Proven operating boundaries

The accepted S005 implementation and real self-use canary establish the following operational rules:

- `COCONDO_WORKTREE_ROOT`, `COCONDO_AGENT_RUN_ROOT` and `COCONDO_ARTIFACT_ROOT` are part of the runtime contract for every start, status, result and resume operation. Observers must bind the same external roots as the writer.
- Long-lived operator or delivery receipts must not be stored below writer-owned `patches/work/`. That workspace can be cleaned by downstream canonical writers. Durable run evidence belongs in the existing external run/artifact roots; `patches/work/` remains a current diagnostic handoff workspace.
- Candidate-side `cpatch workspace init` and `cpatch create` must invoke the Candidate-local `bin/cpatch`; using the integration wrapper with only `cwd=candidate` is insufficient because the launcher derives its project root from its own script path.
- `cpatch inspect`, `cpatch plan`, canonical patch dry-run and patch accept run from the clean integration checkout. Patch dry-run and accept are started directly through `process-ops`; they are not nested inside a generic detached worker.
- A transport or observer failure after a durable run was started does not authorize a blind retry. Inspect canonical run and logical-run evidence first; resume or diagnose only according to the persisted state.
- Runtime/log paths created by tooling must be ignored or external by contract. Delivery wrappers must not make the integration checkout dirty before a canonical patch operation.

These rules standardize the boundaries proven during Sprint 005. They do not add acceptance, push, cross-project mutation or agent-write authority.

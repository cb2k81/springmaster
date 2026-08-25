---
documentId: ADR-0019
title: Autonomous Logical-Run Repair Orchestration
documentType: adr
status: accepted
authority: normative
scopeLevel: component
scopePaths:
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-25
validFrom: 2026-08-25
lastReviewedAt: 2026-08-25
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# ADR-0019 Autonomous Logical-Run Repair Orchestration

## Context

Springmaster has proven writable Codex development with immutable V2 agent tasks, detached task worktrees, host-local sandbox qualification, trusted-host qualification, immutable handoff, cpatch dry-run and separate human acceptance. Sprint 004 also exposed the remaining operational bottleneck: ordinary deterministic implementation and qualification failures still required a human to classify the failure, construct a successor task, carry the previous work forward and restart qualification.

That manual repair loop is incompatible with `GOAL-006`. The next architecture step must automate orchestration without weakening the existing filesystem, Git, host, task, patch or acceptance boundaries.

## Decision

1. Springmaster introduces a repository-owned outer **Logical Run** state machine for one authorized development job. One Logical Run may own multiple immutable physical `springmaster.agent-task.v2` attempts.
2. A consumed physical attempt ID is never reinvoked. A repairable failure creates a new successor attempt ID while preserving the immutable history of the failed attempt.
3. Every successor attempt remains bound to the same integration base, task scope, risk class, capabilities and qualification argv arrays. A material change to any of those values is not repair and terminates the Logical Run with an explicit blocker.
4. The previous allowed worktree state is carried to the successor through an immutable `codex-change-bundle`. Carried bytes and executable modes are verified before Codex starts; host materialization normalizes declared modes independently of operator `umask`.
5. Deterministic compiler, test, contract, fixture, documentation, OpenAPI/golden and gate failures attributable to repository content are repair signals by default. Qualification collects the remaining declared commands where safe and writes one immutable failure packet so Codex receives a consolidated failure set.
6. Scope, capability, security, oracle, integration-base, normative-decision, external-dependency and genuine host/tool failures are terminal blockers, not automatic repair candidates.
7. The Logical Run uses finite attempt and active-time budgets plus repeated-fingerprint/no-byte-progress detection. It must not loop indefinitely.
8. A raw host invocation classified `FAILED` may be continued as `TRANSPORT_DEGRADED_CONTINUE` only when machine evidence proves raw Codex exit `0`, completed execution exit `0`, no parse errors, at least one completed turn, no failed turn and every error item exactly matches the known in-process event-stream-lag pattern. Raw host evidence is never rewritten.
9. `process-ops` remains the only owner of durable detached processes. The Logical Run is orchestration, not a second process supervisor. Start/resume must survive terminal loss and VM suspend without duplicate writers.
10. A successful Logical Run automatically advances through fresh trusted qualification, immutable agent-task handoff, trusted candidate commit, `cpatch create`, `cpatch inspect`, `cpatch plan` and canonical patch dry-run.
11. The success boundary is `PREACCEPT` / `HUMAN_ACCEPT_REQUIRED`. Automatic `patch-accept`, push, cross-project mutation and direct agent writes to integration `main` remain forbidden.
12. The first implementation must orchestrate the existing `agent-task`, `codex-host-sandbox`, `codex-change-bundle`, `process-ops` and cpatch primitives without modifying their security semantics. If implementation proves that one of those primitives must change, Sprint 005 stops for explicit re-planning rather than self-relaxing the boundary.

## Consequences

The normal development path changes from human-managed physical attempts to one operator-visible Logical Run. Failed attempts remain first-class immutable evidence, while ordinary repair no longer requires manual task rematerialization or chat-generated recovery operators.

The Logical Run needs versioned contracts for its immutable input, persisted state and repair packet; a repository-owned entrypoint with start/status/result semantics; deterministic integration tests; test-inventory registration; and operator documentation.

Speed is part of correctness: qualification findings should be consolidated, successful work must be carried forward rather than recreated, and only the final canonical qualification must be complete and fresh before handoff.

## Rejected alternatives

- Reinvoking a failed V2 task ID: rejected because it rewrites the meaning of immutable invocation evidence.
- Allowing Codex to write `main` or accept patches: rejected because it collapses the trust boundary.
- Building a second detached-process supervisor: rejected because ADR-0014 already assigns worker ownership to `process-ops`/Toolkit runs.
- Treating every host-oracle failure as product failure: rejected because Sprint 004 demonstrated a known stream-lag transport false negative.
- Recreating predecessor work from prompts: rejected because it wastes time and weakens byte-level provenance.
- Expanding task scope automatically during repair: rejected because authorization changes require a new human decision.

## Verification and adoption

Adoption requires deterministic evidence for at least: first-attempt success; automatic repair successor; consolidated independent qualification failures; scope and host-tool stops; no-progress stop; repair-budget exhaustion; known stream-lag continuation; unknown error blocking; restart/resume without duplicate writer; no reinvocation of consumed task IDs; byte- and mode-exact predecessor carry-forward including `umask 077`; structural preflight for internally inconsistent path sets; unchanged `main` through Pre-Accept; and absence of automatic patch acceptance.

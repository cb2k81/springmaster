---
documentId: TOOL-OPERATOR-EFFECT-0001
title: Operator Command Effect Contract
documentType: standard
status: active
authority: normative
scopeLevel: ecosystem
scopePaths:
  - springmaster/engineering
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-27
validFrom: 2026-07-27
lastReviewedAt: 2026-07-27
reviewBy: 2027-01-27
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# Operator Command Effect Contract

## 1. Purpose

A command proposed by a chat, coding agent, runbook or generated sidecar can exercise the operator's host permissions even when the agent itself is sandboxed. Manual execution is therefore not an implicit authorization of undisclosed effects.

Every generated host command that can write, delete, overwrite, create directories, mutate a repository, use credentials or access a network must be accompanied by an effect declaration before execution.

## 2. Required declaration

The declaration is machine-readable according to:

```text
contracts/governance/agent/operator-command-effect.schema.json
```

It states at least:

- stable command and task identity;
- purpose;
- exact argument array without shell interpolation;
- exact working directory;
- read and write scopes;
- network policy;
- repository-mutation policy;
- destructive actions;
- directory-creation and overwrite policies;
- environment inputs.

The visible operator handoff must summarize the same effects as `READS`, `WRITES`, `NETWORK`, `REPOSITORY_MUTATION`, `DESTRUCTIVE_ACTIONS`, `DIRECTORY_CREATION` and `OVERWRITE`.

## 3. No implicit authority

The following are not authorized output locations unless supplied explicitly by the operator and accepted by the applicable contract:

- `$HOME` and user-specific subdirectories;
- `Downloads`;
- `/tmp` or the current directory;
- the integration checkout;
- another repository;
- a path inferred from an example.

A write-capable path variable has no hidden fallback. A missing path or missing authorization fails closed.

Directory provisioning is a separate operator action. A consumer such as `agent-task` validates configured roots but does not create them.

## 4. Codex calibration profile

For the Springmaster Codex calibration:

- the invocation works in and declares the prepared detached task worktree as a required read scope;
- `analysis` and `qualification` declare `writes=[]` and `repositoryMutation=none`;
- `implementation` declares exactly `writes=[task-worktree]` and `repositoryMutation=task-worktree-only`;
- Codex uses the Linux `bwrap` platform sandbox with no additional writable roots;
- the operator home, `Downloads`, integration worktree, Git common directory, external run and artifact roots, other repositories and host temporary directories are never writable by Codex;
- `--add-dir`, user/profile configuration overrides, full-auto and sandbox-bypass flags are forbidden;
- agent shell network remains disabled; the declared network policy is limited to the Codex control plane;
- directory creation and overwrite are restricted to declared task paths;
- destructive actions are empty;
- invocation source records are staged below the explicit external artifact root by the operator;
- the trusted harness copies and hashes the effect and invocation records into the external run root.

An operator cannot widen the Codex write boundary by declaring another path. Handoff to `Downloads` or another delivery location is a separate trusted operator action after task completion. The effect declaration does not start Codex and does not authorize integration, commit, push or target mutation.

## 5. Failure behavior

Execution or recording stops when:

- a field is missing or unknown;
- an argument array differs from the invocation record;
- the working directory is not the prepared task worktree;
- a write, network or repository scope exceeds the active pilot policy;
- an environment key is outside the allowlist;
- the source evidence is outside the external artifact root;
- existing immutable invocation evidence would be overwritten.

## 6. Relationship to patch commands

`PATCH_COMMAND_GENERATION_CONTRACT.md` remains the specialized contract for patch operations. This document supplies the general host-effect boundary that also applies to non-patch commands and to instructions generated in chat.

---
documentType: concept
status: active
scope: patch-scopes
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Patch Scope Least Privilege

Patch scopes are capability boundaries, not a convenience allowlist for an entire roadmap.

## Springmaster root exception

The project-local Root extension contains only paths that are not covered by the stable built-in scopes and are required by the immediate, accepted work:

```text
AGENTS.md
contracts/**
src/main/java/de/cocondo/platform/demo/**
src/main/java/de/cocondo/system/entity/**
```

The temporary `system/entity` exception is retained only for the accepted persistence-newness recovery patch and must be removed by the closing course-correction patch. HTTP, observability and security changes require their own explicit scope decision instead of a permanent Root exception.

## Generated projects

Project-New targets receive only:

```text
AGENTS.md
contracts/**
```

Springmaster-specific package paths must never be copied into a generated target's `.env.example`. Application and domain source changes use target-local scopes derived from the generated project namespace.

## Expansion rule

A scope is expanded in a dedicated patch, for a named capability and a bounded file set. The expansion is removed when the capability no longer requires it. `bin/patch-scope-least-privilege-it.sh` rejects known Springmaster-path leakage into project templates.

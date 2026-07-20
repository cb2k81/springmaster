---
documentType: governance
status: active
scope: repository
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Documentation Governance

## Purpose

Springmaster separates durable human documentation from contract sources, templates, executable tests, generated evidence and historical patch provenance.

## Durable document types

New durable Markdown files under `PROJECT_DOCS/` use exactly one of these types:

- `governance`
- `adr`
- `concept`
- `guide`
- `requirements`
- `plan`
- `technical-debt`
- `sprint-summary`

Every new durable document starts with front matter containing `documentType`, `status`, `scope`, `owner`, `validFrom` and `supersedes`.

## Artifact boundaries

- Human-maintained durable documentation remains under `PROJECT_DOCS/`.
- Machine-readable contract sources belong under a dedicated contract or template path and are not disguised as narrative documentation.
- Tests and gates remain executable sources under `bin/` or `src/test/`.
- Generated evidence belongs in ignored build or report output unless a specific accepted decision makes a golden fixture part of the repository contract.
- Patch changelogs under `patches/logs/` are historical provenance, not living documentation.

## Transition

The existing Markdown inventory is recorded in `PROJECT_DOCS/TOOLING/documentation-transition-baseline.json`. Existing files may be migrated incrementally. New files are not added to that baseline and must satisfy the metadata contract immediately.

`PROJECT_DOCS/index.md` is the active discoverability index. `bin/documentation-gate.sh --check` verifies new-file metadata and complete index coverage. Legacy metadata findings remain report-only during the transition; missing metadata on new files and index drift fail closed.

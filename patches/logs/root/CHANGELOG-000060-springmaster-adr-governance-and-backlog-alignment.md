# Changelog: 000060_springmaster_adr_governance_and_backlog_alignment

## Type

Documentation-only.

## Scope

`root`

## Baseline

`springmaster_export_full_2026-06-30T08-06-52-878238Z.zip`

## Changes

- Added ADR governance and backlog alignment rules.
- Added a reusable ADR template.
- Updated the ADR index and ADR gap backlog with planning status, priority and tooling blocker classes.
- Marked ADR-0002, ADR-0006, ADR-0003, ADR-0004 and ADR-0007 as P0 ready-to-draft items.
- Clarified that strict gate tooling must not encode ADR-required architectural rules before accepted ADRs exist.
- Updated the standard consistency review, standards README, implementation plan and version policy.
- Updated `platform/versions/platform.env` to `PLATFORM_VERSION=0.13.21-foundation` and `PLATFORM_STATE_PATCH=000060_springmaster_adr_governance_and_backlog_alignment`.

## Validation

No Maven test is required because no Java code, tests, build configuration, tooling, templates, demo code or target-project files are changed.

Expected validation:

- manifest JSON is valid;
- patch applies with docs profile;
- ADR governance, ADR template and ADR backlog files exist;
- version entries are updated;
- full export can be created;
- export ZIP integrity is valid.

## Target projects

No IDM, Personnel, Contacts, Orders or other target-project changes are included or authorized by this patch.

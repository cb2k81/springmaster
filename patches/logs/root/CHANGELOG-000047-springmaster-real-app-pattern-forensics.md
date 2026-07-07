# Changelog: 000047 Springmaster Real App Pattern Forensics

## Type

Documentation-only.

## Scope

`root`

## Baseline

`springmaster_export_full_2026-06-29T11-26-54-261995Z.zip`

## Changes

* Added `PROJECT_DOCS/STANDARDS/REAL_APP_PATTERN_FORENSICS.md`.
* Documented current IDM and Personnel application patterns as Springmaster comparison inputs.
* Derived adopt/reject/defer decisions for API, DTO, validation, error, command, security, service, persistence, mapping and gate topics.
* Added Catalog-demo readiness rules based on the real-app comparison.
* Updated the standards indexes to reference the new forensics document.
* Updated `platform/versions/platform.env` to `PLATFORM_VERSION=0.13.8-foundation` and `PLATFORM_STATE_PATCH=000047_springmaster_real_app_pattern_forensics`.
* Updated the Springmaster version policy with the 000047 version rationale.

## Non-goals

* No Java source changes.
* No Maven, dependency or build changes.
* No tool, template or platform-update changes.
* No target-project changes for IDM, Personnel, Contacts, Orders or other applications.

## Validation expectation

No `mvn test` is required because this patch is documentation-only.

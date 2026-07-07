# Springmaster Reference Project and Standards Strategy

## Status

Accepted with patch `000043_springmaster_reference_project_and_standards_strategy`.

## Purpose

Springmaster is the canonical development and distribution basis for Cocondo backend foundations. It is not only a collection of shell tools and reusable Java Core classes. It also defines standards, conventions, reference implementations and validation gates for future Fachprojekte.

This document records the current adoption strategy after the first Core foundation slices were implemented through patch `000042_springmaster_core_domain_entity_service_support`.

## Decision 1: Existing projects are not the first delivery targets

Existing projects are not supplied by Springmaster for the next validation step. A new reference project is built first.

This applies to IDM, Personnel and any other existing backend project. They remain comparison and later migration candidates, but they are not the first regular consumers of generated Springmaster payloads.

The reason is risk control. A clean-room reference project proves whether the Springmaster Core, tooling, patch process, standards and reference implementations work together without carrying legacy assumptions from IDM or Personnel into the master.

## Decision 2: The reference project is a demo app for all patterns

The reference project is not an empty technical sandbox. It is a demo app for Springmaster patterns.

It must demonstrate Core usage, local patch tooling, API endpoint conventions, DTO contracts, request validation, list and filter contracts, controller patterns, service patterns, repository integration, OpenAPI visibility, tests, export behavior and enforceable quality gates.

The goal is not only to prove that the Core compiles. The goal is to prove that Springmaster can produce a usable backend application pattern that later projects can follow.

## Decision 3: The domain context is Catalog-demo

The reference/demo context is named `Catalog-demo`.

The name deliberately combines both concerns. `Catalog` gives the demo a small but concrete business context. `demo` makes clear that the project exists to demonstrate Springmaster patterns and is not a productive Fachanwendung.

The expected project path is:

```text
/opt/cocondo/catalog-demo
```

This path is intentionally separate from `/opt/cocondo/springmaster`, `/opt/cocondo/idm` and `/opt/cocondo/personnel`.

## Decision 4: CatalogItem is the first pattern object

The first domain object is `CatalogItem`.

`CatalogItem` is small enough to keep the initial reference implementation focused and rich enough to demonstrate the relevant base patterns. The first implementation should cover entity, DTO, create request, update request, mapper, repository, service, controller, validation, list endpoint, paging, sorting, OpenAPI contract, tests and exportability.

Additional demo objects may be added later only when they are needed to demonstrate another Springmaster pattern. Examples are assignment commands, metadata extensions, sequence generation, command endpoints, application info, security boundaries or bulk operations.

## Springmaster as standards provider

Springmaster owns standards and conventions that should apply to future backend Fachprojekte unless a project explicitly documents a deviation.

The standards are expected to cover at least these areas:

- API endpoint structure
- request DTO validation
- required-field visibility in OpenAPI
- create, update, delete and command status codes
- list, paging, sorting and filtering contracts
- external ID boundary
- OpenAPI/YAML readiness rules
- DTO and entity base contracts
- package and dependency boundaries
- patch, export and target-update workflows
- test and quality-gate requirements

The standards must not stay purely documentary. They should be represented through reference implementations, reusable Java contracts where appropriate and enforceable checks.

## Enforcement model

The target model uses several layers.

1. ADRs define the rule.
2. Standards documents generalize the rule outside a single Fachprojekt.
3. Java interfaces and support classes guide implementation where type contracts are useful.
4. Reference implementations in Catalog-demo show the expected pattern.
5. JUnit, OpenAPI contract tests, ArchUnit or custom Java tests verify compliance.
6. Maven quality gates make violations visible before patches are accepted.
7. Platform update payloads distribute proven standards only after review.

Controller URL structures and OpenAPI response semantics should not be enforced exclusively through Java interfaces. They are better verified with contract tests against the generated OpenAPI document and integration tests against the HTTP layer. Java interfaces remain useful for DTO contracts, service contracts, factories, query support and reusable domain abstractions.

## Existing IDM ADRs as source material

The IDM API-readiness ADRs are valid source material for Springmaster standards, but they must be extracted into generic master-level standards.

The IDM-specific context is not copied as a target-project instruction. The reusable rule is extracted, renamed and placed under Springmaster standards documentation.

The first standardization candidates are:

- API request validation and required fields
- list, filter and query contract for UI-capable management APIs
- command and assignment HTTP contract
- external ID and OpenAPI boundary

## Target-project boundary

Target-project changes remain review-gated.

`apply-plan` is a review step and must not mutate a target project. Real target mutations require explicit `target-apply` and, since `000079`, `TARGET_DELIVERY_ENABLED=true` in the target descriptor.

IDM and Personnel are existing/running projects and are deliberately deferred from Springmaster delivery to avoid operational risk. They remain useful as real-project reference material, but not as first delivery targets.

The first planned Springmaster-delivered Java backend target is `zbm`. It starts as an initialization candidate: first create and accept a generated technical Backend-Skeleton, then reclassify it for updates such as Core, Tools and Defaults.

## Next work items

The next planned work item is `000044_springmaster_api_standards_adr_extraction`.

That patch should extract generic Springmaster API standards from the IDM ADR material and place them under `PROJECT_DOCS/STANDARDS/API/`.

The following work item should define the API contract gate concept, including OpenAPI assertions, validation tests, possible ArchUnit rules and reusable contract-test helpers.



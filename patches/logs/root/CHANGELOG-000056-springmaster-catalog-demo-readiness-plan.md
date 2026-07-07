# Changelog 000056 - springmaster_catalog_demo_readiness_plan

## Scope

Documentation-only Springmaster root-scope patch.

## Added

* `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md` defines Catalog-demo readiness criteria before Catalog-demo becomes the canonical reference implementation.
* `patches/logs/root/CHANGELOG-000056-springmaster-catalog-demo-readiness-plan.md` records this patch.

## Changed

* `PROJECT_DOCS/DEMO/README.md` now references the readiness plan and clarifies that existing CatalogItem code is a seed until readiness is proven.
* `PROJECT_DOCS/STANDARDS/README.md` now records the readiness plan as the next bridge from standards to the reference implementation.
* `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md` now references the readiness plan as the first G5 Catalog-demo reference gate artifact.
* `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md` now aligns Phase 5 with Catalog-demo readiness rather than a compile-only demo goal.
* `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md` records the `0.13.17-foundation` version increment.
* `platform/versions/platform.env` sets `PLATFORM_VERSION=0.13.17-foundation` and `PLATFORM_STATE_PATCH=000056_springmaster_catalog_demo_readiness_plan`.

## Validation

No Maven test is required because this patch is documentation-only and does not change Java code, Maven configuration, shell tooling, templates, Catalog-demo implementation or target projects.

Expected validation:

* manifest JSON is valid;
* patch applies with Springmaster patch tooling;
* version metadata contains `PLATFORM_STATE_PATCH=000056_springmaster_catalog_demo_readiness_plan`;
* the readiness plan and linked documentation files exist;
* full export ZIP can be generated and checked.

## Target-project boundary

This patch does not change, supply or remediate IDM, Personnel, Contacts, Orders or any other existing target project.

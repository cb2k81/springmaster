---
documentType: technical-debt
status: active
scope: catalog-demo
owner: springmaster-maintainers
validFrom: 2026-07-21
supersedes: none
---
# CatalogItem Persistent Candidate – Technical Debt Review

## Review scope

This review is the mandatory technical-debt and roadmap checkpoint for
`000163_springmaster_catalogitem_persistent_candidate_runtime`. It evaluates the
smallest complete persistence transition only. Canonicalization is explicitly
outside this patch.

## Qualification correction

The non-accepted `000161_springmaster_catalogitem_persistent_candidate_runtime` artifact exposed a test-environment defect before any full-suite or gate promotion: multiple cached Spring test contexts shared the fixed H2 name `springmaster`. The first context initialized Liquibase successfully; a later context reached the same still-open in-memory database and failed while initializing the Liquibase bookkeeping table.

The non-accepted `000162_springmaster_catalogitem_persistent_candidate_runtime` artifact closed that shared-database defect: all CatalogItem, OpenAPI and controller tests in the targeted run passed. Its newly added regression test nevertheless asserted that H2 JDBC metadata preserves connection URL options such as `MODE=MariaDB`. H2 reports the runtime database identity without those options, so the assertion failed even though isolation and Liquibase initialization worked. This was a test-observation defect, not a persistence-runtime regression.

`000163_springmaster_catalogitem_persistent_candidate_runtime` keeps the isolated datasource configuration and corrects the regression test boundary. The configured datasource URL is used to verify `MODE=MariaDB` and `DATABASE_TO_LOWER=TRUE`; JDBC metadata is used only for the actual runtime database identity. The test keeps two contexts open concurrently, proves distinct configured and runtime identities, and verifies that both Liquibase schemas are usable. The failed `000161` and `000162` evidence remains historical and is not reclassified as an accepted baseline.

## Debt assessment

No new untracked technical debt is accepted by this patch. The implementation
removes the transitional split between the in-memory runtime and the JPA
reference implementation. Runtime, Liquibase schema, query adapter, service
transactions, tests, machine-readable evidence and current documentation now
state the same Candidate behavior.

The following residual risks are explicit planned blockers rather than hidden
completion claims:

| Item | Classification | Required follow-up |
|---|---|---|
| MariaDB collation and case-insensitive SKU uniqueness under races | existing P3 qualification gap | `SM-P3-02` production-like persistence qualification |
| stale optimistic-lock version mapped to a stable `409` contract | existing P3 qualification gap | `SM-P3-02` conflict qualification |
| management authentication and operation-level authorization | existing canonicalization blocker | `SM-P3-03` management security |
| report-only gates and Candidate state | intentional governance boundary | `SM-P3-04` evidence-based promotion |
| Core source-copy distribution | pre-existing platform debt | later Core artifact initiative |
| outer acceptance summary collapses a child test failure to `worktree-validation` | pre-existing tooling diagnostics debt | separate bounded tooling improvement; not a persistence-runtime blocker |

## New dependency and complexity check

`spring-boot-starter-data-jpa` is not an opportunistic framework addition. It
replaces the previous compile-only Spring Data/JPA dependency combination and is
required by the accepted persistence strategy. No additional code generator,
mapper framework or persistence abstraction is introduced.

`CatalogItemQuerySupport` centralizes public paging and sorting validation so
invalid requests cannot reach pageable or criteria construction. This reduces,
rather than duplicates, boundary logic.

## Test and verification checkpoint

The patch is not eligible for acceptance until all required Maven tests and
Springmaster gates run successfully in an environment with Maven and dependency
resolution. Static contract, documentation, migration and artifact preflights
may qualify the patch artifact, but they do not replace executable Java tests. The
first mandatory targeted run includes `TestDatabaseIsolationContractTest` before
the broader HTTP/OpenAPI contexts and the full Maven suite.

## Roadmap alignment

The patch remains aligned with the approved sequence:

1. establish a fully persistent Candidate runtime;
2. qualify MariaDB, constraints, rollback and optimistic-lock conflicts;
3. implement management security;
4. canonicalize only after executable evidence is complete.

Renderer, target delivery and ZBM mutation remain blocked. No later phase is
started by this patch.

# Query Contract Gate Report

Reference report concept since patch `000106_springmaster_query_contract_gate_report`.

This document defines the report-only gate shape for Springmaster query contracts. It turns the documented List, `/all`, `/count`, query-operation interface and JPA count-efficiency standards into a concrete, machine-readable report target without promoting strict build failure yet.

## Purpose

The gate report exists to answer one question for a generated application or reference slice:

```text
Does this resource implement the Springmaster query contract consistently enough to be compared, reviewed and later promoted to a strict gate?
```

The report is deliberately report-only at this stage. A finding is evidence for review, not an automatic rejection of a target project.

## Scope

The first report scope covers management-style list resources that expose at least one of the following operations:

```text
GET  /api/<domain>/<resources>
GET  /api/<domain>/<resources>/all
POST /api/<domain>/<resources>/search
POST /api/<domain>/<resources>/search/all
GET  /api/<domain>/<resources>/count
POST /api/<domain>/<resources>/search/count
```

The report covers:

- paged list operation shape;
- complete-result-set `/all` shape;
- optional count-only shape;
- filter parity between list, `/all` and `/count`;
- sort allowlist and stable sort behavior;
- absence of paging/sort semantics on count-only operations;
- typed `ResultSetQueryOperations` service adoption where Java source is available;
- JPA count efficiency anti-pattern indicators where persistence source is available.

It does not require every resource to provide `/all` or `/count`. It checks them when present and reports missing evidence when a resource claims Springmaster query-contract maturity.

## Report artifact

The first generated artifact should be JSON so it can be consumed by CI, patch logs and future target-project comparison:

```text
reports/api/query-contract-gate-report.json
```

Recommended summary shape:

```json
{
  "schemaVersion": 1,
  "generatedAt": "2026-07-13T00:00:00Z",
  "project": "springmaster",
  "mode": "report-only",
  "source": {
    "openapi": "target/openapi.json",
    "javaSources": "src/main/java",
    "tests": "src/test/java"
  },
  "summary": {
    "resources": 1,
    "findings": 0,
    "errors": 0,
    "warnings": 0,
    "info": 0
  },
  "resources": [],
  "findings": []
}
```

A finding must be stable and reviewable:

```json
{
  "id": "QRY-COUNT-003",
  "severity": "warning",
  "resource": "CatalogItem",
  "operation": "GET /api/demo/catalog/items/count",
  "message": "Count operation exposes sorting parameters.",
  "standard": "API_COUNT_RESPONSE_CONTRACT_CANDIDATE.md",
  "evidence": {
    "file": "src/main/java/.../CatalogItemController.java",
    "symbol": "count"
  }
}
```

## Rule catalog

| Rule ID | Severity | Check | Primary source |
|---|---|---|---|
| `QRY-LIST-001` | error | paged list uses explicit `page`, `size`, `sortBy`, `sortDir` vocabulary where paging/sorting is public | OpenAPI / controller |
| `QRY-LIST-002` | warning | generated parameter names such as `arg0`/`arg1` are visible | OpenAPI |
| `QRY-LIST-003` | warning | list response does not expose Springmaster `PagedResponseDTO`-style metadata | OpenAPI / Java |
| `QRY-ALL-001` | warning | `/all` exists but has paging parameters | OpenAPI / controller |
| `QRY-ALL-002` | warning | `/all` is documented or implemented as a selector/options endpoint instead of complete result set | docs / OpenAPI |
| `QRY-ALL-003` | info | resource has paged list but no complete-result-set endpoint | OpenAPI |
| `QRY-COUNT-001` | warning | count endpoint uses non-canonical path such as `/total` or `/size` | OpenAPI |
| `QRY-COUNT-002` | warning | count response does not expose required `totalElements` | OpenAPI / Java |
| `QRY-COUNT-003` | warning | count endpoint exposes or applies `page`, `size`, `sortBy` or `sortDir` semantics | OpenAPI / controller / Java |
| `QRY-COUNT-004` | warning | count implementation materializes entities or DTOs before counting | Java source |
| `QRY-FILTER-001` | warning | list, `/all` and `/count` do not share the same documented filter family | OpenAPI / query DTOs |
| `QRY-SORT-001` | warning | public sort field is not allowlisted | Java source / tests |
| `QRY-SORT-002` | info | stable tie-breaker evidence is absent | Java source / tests |
| `QRY-OPS-001` | info | service does not implement `ResultSetQueryOperations` or the equivalent typed query contract | Java source |
| `QRY-SEC-001` | warning | count/list/all predicates do not show shared security or data-scope predicate ownership | Java source / docs |

Severity can be raised only after the report has stable evidence on CatalogItem and at least one generated application.

## CatalogItem baseline expectation

The CatalogItem candidate slice should be the first positive evidence target for the report:

| Operation | Expected result |
|---|---|
| paged list | present with `page`, `size`, `sortBy`, `sortDir`, `sku`, `name` |
| `/all` | present with `sortBy`, `sortDir`, `sku`, `name` and no paging semantics |
| `/count` | present with `sku`, `name` and no paging/sorting semantics |
| typed query operations | `CatalogItemService` implements `ResultSetQueryOperations` |
| JPA efficiency | dedicated Criteria count query in the persistent JPA Candidate runtime |

The report must classify the CatalogItem runtime as a transactional JPA Candidate and verify the dedicated Criteria count query without entity-list materialization. MariaDB-specific and concurrent-conflict qualification remain separate promotion gates.

## Promotion path

Promotion should be staged:

1. report-only JSON generation for CatalogItem;
2. report-only comparison for generated applications;
3. stable findings schema and changelog evidence;
4. optional Maven profile that fails only on selected `error` rules;
5. strict target-project enforcement only after ADR-0006 gate promotion.

## Non-goals

This patch does not introduce the executable reporter. It defines the report target, rule catalog and evidence model so the implementation patch can be minimal, deterministic and regression-testable.

## Executable MVP since 000107

Patch `000107_springmaster_query_contract_report_tooling_mvp` implements the first executable report-only gate for the Springmaster reference project.

Command:

```bash
./bin/query-contract-gate-report.sh
```

Default output:

```text
reports/api/query-contract-gate-report.json
```

The MVP is intentionally source-based and deterministic. It currently evaluates the CatalogItem candidate reference slice and records:

- paged list endpoint evidence;
- complete-result-set `/all` endpoint evidence;
- count-only `/count` endpoint evidence;
- shared business filter family `sku`, `name`;
- absence of paging/sort semantics on `/count`;
- `CountResponseDTO` response evidence;
- sort allowlist and stable tie-breaker evidence;
- `ResultSetQueryOperations` service adoption;
- JPA count-efficiency status as `dedicated-criteria-count` for the persistent CatalogItem candidate.

The expected CatalogItem MVP result is `summary.findings = 0`. That does not promote CatalogItem to canonical persistence status. It only proves that the current candidate reference slice satisfies the query-contract shape covered by the MVP.

The implementation remains report-only. Strict build failure, generated-application scanning, OpenAPI parsing, persistent JPA inspection and security/data-scope runtime checks remain later promotion stages.

## CatalogItem golden fixture since 000108

Patch `000108_springmaster_catalogitem_query_contract_report_fixture` promotes the MVP output for the CatalogItem candidate reference slice into a committed golden fixture:

```text
src/test/resources/tooling/query-contract-gate-report.catalogitem.golden.json
```

The fixture freezes the expected report-only output for a deterministic timestamp (`2026-07-13T00:00:00Z`). The regression test compares the generated JSON byte-for-byte against this fixture before checking selected semantic markers. This turns the CatalogItem report from smoke evidence into stable Golden Evidence without changing the report-only runtime mode.

The fixture is intentionally scoped to CatalogItem and to source-based query-contract evidence. It records the persistent JPA count-query structure, but does not by itself prove OpenAPI conformance, management-security enforcement or production-like database qualification.

## OpenAPI query-contract evidence since 000109

Patch `000109_springmaster_query_openapi_contract_evidence` adds separate runtime-generated OpenAPI evidence for the CatalogItem candidate reference slice.

The evidence is intentionally not folded into the source-based report command yet. This separation keeps failure analysis precise:

- `bin/query-contract-gate-report.sh` proves the source/report contract;
- `SpringmasterQueryContractReportTest` proves the committed report fixture;
- `CatalogItemOpenApiQueryContractTest` proves `/api-docs` query vocabulary and count schema exposure.

The OpenAPI evidence verifies the same three query operations as the report fixture:

```text
GET /api/demo/catalog/items
GET /api/demo/catalog/items/all
GET /api/demo/catalog/items/count
```

The count operation must expose only business filters and the `CountResponseDTO.totalElements` response schema. Paging and sorting parameters on `/count` remain invalid OpenAPI evidence.

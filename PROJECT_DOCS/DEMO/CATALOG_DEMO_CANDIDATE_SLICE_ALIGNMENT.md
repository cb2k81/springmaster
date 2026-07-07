# Catalog-demo Candidate Slice Alignment

## Purpose

Patch `000074_springmaster_catalog_demo_candidate_slice_alignment` aligns the report-only gate seed with the `CatalogItem` candidate evidence introduced by `000072` and forensically reviewed by `000073`.

This patch does not promote Catalog-demo to canonical status. It only makes candidate evidence deterministic enough for the gate runner to distinguish current candidate state from historical `legacy-demo-seed` text in the readiness plan.

## Scope

Included:

- machine-readable `CatalogItem` candidate evidence JSON;
- G5 report-only readiness heuristic aligned to the evidence file;
- report input manifest enriched with `catalogDemoEvidence`;
- report-only regression/selfcheck expectations updated for candidate evidence;
- documentation of the reduced report-only findings baseline.

Excluded:

- target-project scans;
- strict gates;
- implemented security;
- durable persistence;
- OpenAPI generation;
- canonical readiness decision;
- DTO-boundary cleanup for availability/range;
- service update validation symmetry.

## Machine-readable evidence

The new evidence file is:

```text
PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json
```

Schema marker:

```text
springmaster.catalog-demo.candidate-evidence.v1
```

Important values:

| Field | Value |
|---|---|
| `slice` | `CatalogItem` |
| `sliceState` | `candidate-reference-slice` |
| `canonicalState` | `not-canonical` |
| `securityMode` | `documented-deferred-security` |
| `targetComparison` | `blocked` |
| `targetDelivery` | `blocked` |

## Gate behavior after 000074

The G5 rule now evaluates current candidate evidence before falling back to readiness-plan historical text.

Expected report-only outcome after this patch:

| Metric | Value |
|---|---:|
| Total findings | `8` |
| `BLOCKER` | `0` |
| `ERROR` | `0` |
| `WARNING` | `1` |
| `INFO` | `7` |
| `MANUAL_REVIEW` | `0` |

Expected gate distribution:

| Gate | Findings | Meaning |
|---|---:|---|
| `SM-G0-RULE-SOURCE-COVERAGE` | `6` | positive ADR rule-source evidence |
| `SM-G1-STATUS-ERROR-CONTRACT` | `1` | positive create `201 Created` evidence |
| `SM-G4-SECURITY-CLASSIFICATION` | `1` | expected deferred security warning |

The previous `SM-G5-CATALOG-READINESS-EVIDENCE` manual review is closed for the current candidate slice. G5 must reappear only if readiness evidence is missing, unclassifiable or falls back to `legacy-demo-seed` without candidate evidence.

## Safety constraints

The alignment remains report-only:

- findings do not fail the build;
- no target project is scanned;
- no target project is modified;
- no strict gate is enabled;
- no canonical status is declared.

## Remaining work

The next work items remain unchanged from the forensic review:

| ID | Priority | Area | Work |
|---|---|---|---|
| `F-073-001` | P0 before canonical | DTO boundary | remove persistence-facing `Range` from public request DTOs |
| `F-073-002` | P0 before canonical | Application validation | add update validation symmetry at service boundary |
| `F-073-003` | P1 before canonical | Service API | remove or quarantine unpaged `CatalogItemService.list()` legacy helper |
| `F-073-005` | expected blocker | Security | implement management security later |
| `F-073-006` | expected blocker | Persistence | add durable persistence later |
| `F-073-007` | expected blocker | OpenAPI | add operation/schema evidence later |
| `F-073-008` | expected blocker | Canonicalization | perform later canonical readiness review |

## Decision

`000074` closes the gate heuristic gap `F-073-004` only.

The `CatalogItem` slice remains a `candidate-reference-slice`. Catalog-demo remains not canonical.

## Follow-up after 000075

`000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup` does not change the gate heuristic introduced by this alignment patch. The expected report-only baseline remains `8` findings and `0` manual-review findings.

The patch improves the underlying candidate evidence by cleaning the DTO boundary and validation symmetry that were intentionally left out of the gate-alignment scope.


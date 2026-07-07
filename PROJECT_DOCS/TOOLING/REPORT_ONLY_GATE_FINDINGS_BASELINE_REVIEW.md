# Springmaster Report-only Gate Findings Baseline Review

## Purpose

Patch `000070_springmaster_report_only_gate_findings_baseline_review` records the first forensic findings baseline for the executable report-only gate tooling introduced by patches `000068` and `000069`.

The review classifies the current `12` findings, separates positive rule-source evidence from expected legacy-seed gaps, and defines how these findings should be treated before Catalog-demo becomes a candidate or canonical reference slice.

This document does not promote any gate to strict mode. It does not change Java code, Maven configuration, tool behavior, Catalog-demo implementation or target-project handling.

## Source and scope

Baseline source:

```text
springmaster_export_full_2026-07-01T05-02-43-448803Z.zip
```

Report command used as reference baseline:

```bash
./bin/springmaster-gates.sh report --run-id 000070-analysis --clean --out-dir target/springmaster-gates
```

Canonical report-only seed:

```text
springmaster.report-only-gate-seed.v1
```

Canonical report schema:

```text
springmaster.report-only-report.v1
```

Scope:

```text
springmaster-reference-only
```

Target projects are explicitly out of scope. The findings baseline reviews Springmaster and Catalog-demo seed evidence only.

## Summary baseline

The current deterministic report contains:

| Metric | Value |
|---|---:|
| Total findings | 12 |
| `BLOCKER` | 0 |
| `ERROR` | 0 |
| `WARNING` | 2 |
| `INFO` | 9 |
| `MANUAL_REVIEW` | 1 |

Gate distribution:

| Gate | Findings | Interpretation |
|---|---:|---|
| `SM-G0-RULE-SOURCE-COVERAGE` | 6 | positive ADR rule-source evidence |
| `SM-G1-QUERY-PARAMETERS` | 1 | expected Catalog-demo legacy-seed gap |
| `SM-G1-STATUS-ERROR-CONTRACT` | 3 | mixed positive and missing Catalog-demo evidence |
| `SM-G4-SECURITY-CLASSIFICATION` | 1 | expected deferred-security warning |
| `SM-G5-CATALOG-READINESS-EVIDENCE` | 1 | expected manual review because Catalog-demo remains `legacy-demo-seed` |

Layer distribution:

| Layer | Findings | Interpretation |
|---|---:|---|
| G0 | 6 | ADR-backed rule-source coverage is present |
| G1 | 4 | API query/status/error evidence is incomplete but diagnostic only |
| G4 | 1 | security remains explicitly deferred for Catalog-demo seed |
| G5 | 1 | Catalog-demo is not yet candidate/canonical |

## Classification model

The first baseline classifies findings into these categories.

| Category | Meaning | Expected action |
|---|---|---|
| `positive-evidence` | the finding proves that a required source or positive marker exists | keep as baseline evidence |
| `expected-legacy-gap` | the finding is a known gap because Catalog-demo is still `legacy-demo-seed` | close when creating the candidate reference slice |
| `candidate-slice-work-item` | the finding should disappear or change severity when Catalog-demo candidate implementation is created | plan in Catalog-demo implementation patch |
| `manual-readiness-decision` | automation cannot promote Catalog-demo without human decision and evidence | keep manual until readiness evidence is complete |
| `tooling-evolution-candidate` | the finding shape is useful but may need better parser/OpenAPI support later | keep report-only until implementation is stronger |

## Finding-by-finding review

| # | Gate | Severity | Subject | Classification | Review |
|---:|---|---|---|---|---|
| 1 | `SM-G0-RULE-SOURCE-COVERAGE` | `INFO` | `ADR-0002` | `positive-evidence` | API boundary rule source is present and can be referenced. |
| 2 | `SM-G0-RULE-SOURCE-COVERAGE` | `INFO` | `ADR-0003` | `positive-evidence` | Application-layer rule source is present and can be referenced. |
| 3 | `SM-G0-RULE-SOURCE-COVERAGE` | `INFO` | `ADR-0004` | `positive-evidence` | Persistence identity rule source is present and can be referenced. |
| 4 | `SM-G0-RULE-SOURCE-COVERAGE` | `INFO` | `ADR-0005` | `positive-evidence` | Security boundary rule source is present and can be referenced. |
| 5 | `SM-G0-RULE-SOURCE-COVERAGE` | `INFO` | `ADR-0006` | `positive-evidence` | Gate strategy rule source is present and can be referenced. |
| 6 | `SM-G0-RULE-SOURCE-COVERAGE` | `INFO` | `ADR-0007` | `positive-evidence` | Catalog-demo canonicalization rule source is present and can be referenced. |
| 7 | `SM-G1-QUERY-PARAMETERS` | `WARNING` | `CatalogItemController` | `expected-legacy-gap` | Current Catalog-demo controller does not expose canonical `page`, `size`, `sortBy`, `sortDir` evidence. This is expected for `legacy-demo-seed`. |
| 8 | `SM-G1-STATUS-ERROR-CONTRACT` | `INFO` | `CatalogItemController` | `expected-legacy-gap` | Current exception response uses ad-hoc `Map<String,Object>`. This is non-canonical but intentionally not blocking while the code is legacy seed. |
| 9 | `SM-G1-STATUS-ERROR-CONTRACT` | `INFO` | `CatalogItemController` | `positive-evidence` | Create endpoint already shows `201 Created` evidence. |
| 10 | `SM-G1-STATUS-ERROR-CONTRACT` | `INFO` | `CatalogItemController` | `candidate-slice-work-item` | Delete status-code evidence is missing. Candidate slice should demonstrate bodyless `DELETE` with `204` and `404`. |
| 11 | `SM-G4-SECURITY-CLASSIFICATION` | `WARNING` | `CatalogItemController` | `expected-legacy-gap` | Implemented security annotations are absent. This is acceptable only while security mode remains `documented-deferred-security`. |
| 12 | `SM-G5-CATALOG-READINESS-EVIDENCE` | `MANUAL_REVIEW` | `Catalog-demo` | `manual-readiness-decision` | Catalog-demo is explicitly still `legacy-demo-seed`; canonicalization evidence is incomplete by design. |

## Interpretation

The findings are internally consistent with the current architecture state.

No `BLOCKER` or `ERROR` finding exists. That is correct because the gate seed is report-only and the current Catalog-demo implementation is explicitly not canonical.

The two `WARNING` findings are expected:

1. missing canonical query evidence for `sortBy` and pageable parameters;
2. missing implemented security evidence for the Catalog-demo controller.

Both warnings point at real gaps, but the gaps are not regressions. They describe the difference between current `legacy-demo-seed` code and the future candidate reference slice.

The `MANUAL_REVIEW` finding is also expected. A tool must not decide that Catalog-demo is canonical merely because files compile or a small subset of checks is green. ADR-0007 requires human-readable readiness evidence before promotion.

## Current gap categories

### Expected legacy-seed gaps

The following findings should remain acceptable until a Catalog-demo candidate implementation patch starts:

- missing `page`, `size`, `sortBy`, `sortDir` evidence;
- ad-hoc `Map<String,Object>` error response;
- missing bodyless delete status-code evidence;
- missing implemented security annotation or permission evidence;
- Catalog-demo state still `legacy-demo-seed`.

### Candidate reference slice work items

A future Catalog-demo candidate patch should target at least:

- paged list endpoint using canonical query vocabulary;
- DTO matrix with create, update, detail, list item and optional option DTO;
- canonical error response DTO and exception handling;
- create/update/delete status-code evidence;
- bodyless single delete;
- explicit security mode, either stronger `documented-deferred-security` evidence or implemented management security;
- readiness evidence file that allows G5 to distinguish candidate from legacy seed.

### Tooling evolution candidates

The current source-based gate seed is useful but deliberately shallow. Later diagnostics may improve precision by adding:

- OpenAPI snapshot discovery;
- parser-backed path, query parameter and schema checks;
- operationId and tag naming checks;
- MockMvc behavior evidence;
- ArchUnit or classpath-backed Java boundary checks;
- dedicated security fixture checks.

These improvements must remain report-only until explicitly promoted under ADR-0006.

## Consistency against ADRs

| ADR | Baseline consistency |
|---|---|
| `ADR-0002` | Current G1 findings correctly reflect API-boundary and status/error gaps without strict enforcement. |
| `ADR-0003` | No current G3 finding appears in the baseline; this means no first-seed source hint was detected, not that all Java boundaries are fully proven. |
| `ADR-0004` | No current persistence identity finding appears; this is not a strict proof. Deeper DTO/OpenAPI checks are deferred. |
| `ADR-0005` | G4 warning correctly records missing implemented security evidence while allowing documented deferral. |
| `ADR-0006` | Report-only mode, non-blocking findings and compact report behavior are consistent. |
| `ADR-0007` | G5 manual review correctly keeps Catalog-demo non-canonical. |

## Baseline decision

The `12` findings are accepted as the first report-only baseline.

This acceptance means:

- the findings are expected and understood;
- the report runner is allowed to continue producing them;
- no strict enforcement is introduced;
- no target project is scanned or modified;
- Catalog-demo is not canonical;
- future candidate work should use this baseline to prove progress.

This acceptance does not mean:

- the warnings are ignored;
- the current Catalog-demo code is standards-compliant;
- `Map<String,Object>` error responses are canonical;
- missing delete/security/query evidence is acceptable for a candidate or canonical reference slice;
- report-only findings are ready to become strict failures.

## Recommended next steps

1. Keep the `12` findings as the initial report-only baseline.
2. Add a compact baseline expectation to future regression documentation, but avoid hard-coding volatile timestamps or absolute paths.
3. Start the Catalog-demo candidate planning slice before deeper strict enforcement.
4. Defer OpenAPI and ArchUnit-based gates until the source-based runner has a stable baseline and Catalog-demo has more evidence.
5. Keep target-project comparison disabled until Catalog-demo candidate evidence exists.

## Exit criteria for closing this baseline

This findings baseline can be replaced when one of these happens:

- Catalog-demo becomes a `candidate-reference-slice` and some legacy-seed findings disappear;
- a later tool patch changes the report schema intentionally;
- OpenAPI or behavior-backed diagnostics replace source-only hints;
- a strict-promotion patch under ADR-0006 changes severity semantics.

Until then, the current baseline is the reference interpretation for the first report-only gate output.

## Candidate slice planning outcome since 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` converts the candidate-slice work items from this findings baseline into a concrete CatalogItem contract plan.

The baseline interpretation after 000071 is:

- the `12` findings remain the accepted report-only baseline until Catalog-demo code changes;
- G1 query/status/error findings are now mapped to the candidate endpoint, DTO, validation, error and status-code contract;
- G4 security classification is mapped to either `documented-deferred-security` evidence or implemented management security;
- G5 manual review is expected to remain until a candidate evidence file exists;
- no rule is strict, and no target-project scan is authorized.

The recommended next code patch is `000072_springmaster_catalog_demo_catalogitem_candidate_slice_foundation`.

## Candidate-slice findings after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` records the first post-candidate report-only interpretation after `000072`.

A report-only gate smoke after the candidate implementation produced `9` findings:

- `0` `BLOCKER`;
- `0` `ERROR`;
- `1` `WARNING`;
- `7` `INFO`;
- `1` `MANUAL_REVIEW`.

Interpretation:

- G0 rule-source findings remain positive evidence;
- the earlier G1 query and public vocabulary findings are closed by the candidate implementation;
- G1 still records positive create-status evidence;
- G4 security remains a warning because security is `documented-deferred-security`;
- G5 remains manual review because Catalog-demo is not canonical and the current source-based heuristic still reports legacy state before recognizing candidate evidence.

The remaining findings are accepted as candidate-phase report-only findings. No rule is strict and no target-project scan is authorized.



## Findings baseline after 000074

Patch `000074_springmaster_catalog_demo_candidate_slice_alignment` aligns G5 readiness detection with machine-readable CatalogItem candidate evidence.

Expected report-only summary after 000074:

| Metric | Value |
|---|---:|
| Total findings | `8` |
| `BLOCKER` | `0` |
| `ERROR` | `0` |
| `WARNING` | `1` |
| `INFO` | `7` |
| `MANUAL_REVIEW` | `0` |

Expected gate distribution:

| Gate | Count | Classification |
|---|---:|---|
| `SM-G0-RULE-SOURCE-COVERAGE` | `6` | positive ADR rule-source evidence |
| `SM-G1-STATUS-ERROR-CONTRACT` | `1` | positive `201 Created` evidence |
| `SM-G4-SECURITY-CLASSIFICATION` | `1` | expected deferred-security warning |

The former G5 manual-review finding is no longer expected for the current candidate slice because `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json` declares `sliceState=candidate-reference-slice` and `canonicalState=not-canonical`.

The reduction from `9` to `8` is a gate-heuristic alignment, not a canonical promotion. Catalog-demo remains not canonical and target-project scans remain excluded.

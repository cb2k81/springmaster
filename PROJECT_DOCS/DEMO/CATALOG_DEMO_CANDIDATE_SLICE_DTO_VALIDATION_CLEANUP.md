# Catalog-demo Candidate Slice DTO Validation Cleanup

## Purpose

Patch `000075_springmaster_catalog_demo_candidate_slice_dto_validation_cleanup` hardens the `CatalogItem` candidate-reference-slice after the forensic review in `000073` and the gate alignment in `000074`.

The patch is a Demo-code cleanup. It does not promote Catalog-demo to canonical status and does not change report-only gate semantics.

## Scope

Included:

- remove persistence-facing `Range` from public create/update request DTOs;
- introduce a public nested request DTO `CatalogItemAvailabilityDTO`;
- map public availability input to the internal `Range` embeddable only inside `CatalogItemMapper`;
- add create/update service-boundary validation symmetry;
- remove the unpaged legacy helper `CatalogItemService.list()`;
- extend mapper, validator, service and controller tests.

Excluded:

- durable persistence;
- Liquibase migration;
- implemented management security;
- OpenAPI operation/schema evidence;
- target-project comparison;
- target-project delivery;
- strict gate promotion;
- canonical readiness declaration.

## DTO boundary decision

Public request DTOs must not expose the persistence-facing `Range` embeddable.

After this patch:

| Public DTO | Availability shape | Persistence type leakage |
|---|---|---|
| `CatalogItemCreateDTO` | `CatalogItemAvailabilityDTO availability` | no `Range` exposure |
| `CatalogItemUpdateDTO` | `CatalogItemAvailabilityDTO availability` | no `Range` exposure |
| `CatalogItemDTO` | flattened `validFrom` / `validTo` response fields | no `Range` exposure |

The domain entity may continue to use `Range` internally. The mapper owns the conversion between public request shape and persistence/domain shape.

## Validation decision

The public HTTP boundary still uses Bean Validation via `@Valid @RequestBody`.

Additional service-boundary validation now applies symmetrically:

| Operation | Service validation |
|---|---|
| create | `CatalogItemValidator.validate(CatalogItemCreateDTO)` |
| update | `CatalogItemValidator.validate(CatalogItemUpdateDTO)` |

The validator checks required text fields, length limits, tag text and chronological availability range.

Invalid availability uses the same standard error flow as other validation failures and remains part of the candidate error-contract evidence.

## Service API decision

The unpaged helper `CatalogItemService.list()` is removed. Internal and test usage must use `listPaged(page, size, sortBy, sortDir)` to keep the candidate slice aligned with the public API contract.

## Gate impact

The report-only gate baseline is expected to remain stable:

| Metric | Expected value after 000075 |
|---|---:|
| Total findings | `8` |
| `BLOCKER` | `0` |
| `ERROR` | `0` |
| `WARNING` | `1` |
| `INFO` | `7` |
| `MANUAL_REVIEW` | `0` |

This patch addresses forensic cleanup findings, not G0/G1/G4 report-only rule counts.

## Remaining canonical blockers

The following items remain before canonical-reference-slice status can be considered:

- durable persistence and repository boundary;
- Liquibase migration/evolution evidence;
- implemented management security;
- OpenAPI operationId/tag/schema evidence;
- canonical readiness review;
- strict-gate promotion decision;
- target-project comparison;
- target-project delivery.

## Decision

`CatalogItem` remains a `candidate-reference-slice`. The DTO boundary and service validation are cleaner and more suitable as reference material for later generator/tooling use, but Catalog-demo remains not canonical.

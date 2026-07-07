# ADR Governance and Backlog Alignment

## Purpose

Patch `000060_springmaster_adr_governance_and_backlog_alignment` defines how Springmaster turns documentation-first standards into durable Architecture Decision Records before strict gate tooling is implemented.

This document is documentation-only. It does not create Java code, Maven gates, OpenAPI helpers, Catalog-demo code, target-project changes or platform-update payloads.

## Scope

This governance applies to Springmaster decisions that affect at least one of the following areas:

- reusable Core contracts under `de.cocondo.system`;
- generated or reference API contracts;
- Catalog-demo canonicalization;
- patch, export, platform-update or gate tooling behavior;
- future comparison or delivery to IDM, Personnel, Contacts, Orders or other target projects.

Project-local implementation notes remain outside ADR scope unless they change a Springmaster standard, Core contract, template, gate or update rule.

## Documentation levels

Springmaster uses four documentation levels. They must not be mixed.

| Level | Purpose | Examples |
|---|---|---|
| Concept | explains a workstream or strategy | version policy, bootstrap concept |
| Standard | defines rules and conventions | API endpoint standard, mapping standard |
| ADR | records an accepted architecture decision and rejected alternatives | API boundary ADR, persistence identity ADR |
| Changelog | records what a patch changed | `patches/logs/root/CHANGELOG-*.md` |

A standard may exist before an ADR while the design is still being consolidated. A strict gate must not encode an ADR-required rule unless the corresponding ADR is accepted or the governance document explicitly classifies the rule as `ready-for-tooling-without-adr`.

## ADR status model

ADR files use one of the following statuses:

| Status | Meaning | Tooling implication |
|---|---|---|
| `Proposed` | draft decision under review | no strict gate may rely on it |
| `Accepted` | decision is binding for new Springmaster reference work | strict or report-only gates may rely on it, depending on the gate concept |
| `Superseded` | replaced by a later ADR | tools must reference the newer ADR |
| `Rejected` | option was considered and rejected | tools must not implement it as standard behavior |
| `Deprecated` | still present for compatibility but not valid for new reference APIs | tools may report legacy usage as warning or target-comparison finding |
| `Deferred` | intentionally postponed | tools must not fail unless a later ADR changes the status |

Backlog entries may additionally use planning states `needed`, `ready-to-draft`, `drafting`, `accepted`, `deferred` or `not-needed`.

## ADR numbering and naming

ADR files are stored under:

```text
PROJECT_DOCS/ADR/
```

Naming convention:

```text
ADR-0002-short-kebab-title.md
```

Rules:

- ADR numbers are monotonic.
- ADR numbers are never reused.
- Superseded ADRs stay in the repository.
- The ADR README is the index and must be updated in the same patch that adds or changes an ADR.
- `ADR_GAP_BACKLOG.md` tracks required ADRs that are not yet accepted.

## ADR template requirement

New ADRs must follow `ADR_TEMPLATE.md` and include at least:

- status;
- date;
- context;
- decision;
- considered alternatives;
- consequences;
- affected standards;
- gate implications;
- exceptions and deferrals.

Short ADRs are allowed when the decision is narrow, but empty headings are not allowed.

## Standards-to-ADR mapping

Each standard-relevant rule is classified using one of these labels:

| Label | Meaning |
|---|---|
| `accepted-standard` | the standard is coherent and may guide Catalog-demo planning |
| `needs-adr` | the rule is architectural and needs an accepted ADR before strict gates |
| `ready-for-tooling` | the rule is stable enough for report-only or strict gate implementation |
| `ready-for-tooling-without-adr` | the rule is technical hygiene and does not need an ADR |
| `deferred` | intentionally postponed |
| `legacy-tolerated` | allowed only for target comparison or migration, not for new reference APIs |
| `not-canonical` | must not be introduced by Catalog-demo or generated Springmaster templates |

The consistency review and ADR backlog must identify the label when a rule is relevant to gate tooling.

## Gate blocking rule

Before `api-contract-gate-tooling` becomes strict, the following must be true:

1. The rule is explicitly documented in a standard.
2. The rule is classified as `ready-for-tooling` or `ready-for-tooling-without-adr`.
3. If the rule is architectural, the corresponding ADR is `Accepted`.
4. The gate has a defined failure level: `fail`, `warn`, `report-only` or `manual-review`.
5. The gate has a compact report target so terminal output remains bounded.

Report-only tooling may be introduced earlier when it does not block builds and clearly labels findings as non-binding.

## Initial blocking ADRs before strict API gate tooling

The following ADRs are required before strict enforcement of the related gates:

| ADR | Priority | Blocks strict gates for |
|---|---|---|
| ADR-0002 API Boundary and Endpoint Contract | P0 | accepted by 000061; no longer an ADR blocker for API-boundary rules |
| ADR-0006 Verification and Gate Strategy | P0 | accepted by 000062; no longer blocks report-only gate tooling seed |
| ADR-0003 Application Layer and Transaction Boundary | P0 | accepted by 000063; no longer an ADR blocker for report-only Java boundary diagnostics |
| ADR-0004 Persistence Identity and DomainEntity Strategy | P0 | accepted by 000064; no longer an ADR blocker for report-only persistence identity diagnostics |
| ADR-0007 Catalog-demo Canonicalization Strategy | P0 | accepted by 000065; no longer an ADR blocker for Catalog-demo readiness diagnostics |
| ADR-0005 Security and Permission Boundary | P1 | accepted by 000066; no longer an ADR blocker for report-only security diagnostics |

ADR-0008, ADR-0009 and ADR-0010 remain important, but they may follow after the first report-only gate seed if the seed does not enforce their domains strictly. ADR-0005 is accepted by patch 000066 for security and permission diagnostics.

## ADR execution order

Recommended next ADR sequence:

1. `ADR-0002-api-boundary-and-endpoint-contract.md` - Accepted by `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract`
2. `ADR-0006-verification-and-gate-strategy.md` - Accepted by `000062_springmaster_adr_0006_verification_and_gate_strategy`
3. `ADR-0003-application-layer-and-transaction-boundary.md` - Accepted by `000063_springmaster_adr_0003_application_layer_transaction_boundary`
4. `ADR-0004-persistence-identity-and-domainentity-strategy.md` - Accepted by `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy`
5. `ADR-0007-catalog-demo-canonicalization-strategy.md` - Accepted by `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy`
6. `ADR-0005-security-and-permission-boundary.md` - Accepted by `000066_springmaster_adr_0005_security_and_permission_boundary`
7. `ADR-0008-configuration-and-runtime-profile-strategy.md`
8. `ADR-0009-database-migration-and-dbtool-strategy.md`
9. `ADR-0010-observability-and-error-trace-strategy.md`

The order may change only when the ADR backlog documents the reason.

## Exception rule

An exception to an accepted ADR must be documented in one of these ways:

- as an explicit exception section inside the ADR;
- as a follow-up ADR;
- as a target-comparison finding that remains non-canonical for new Springmaster reference work.

Project-local exceptions must not be encoded into Springmaster as general rules.

## Catalog-demo implication

Catalog-demo may proceed in planned slices only after the relevant standards and ADRs are clear enough for the slice. A slice that demonstrates only documentation-level behavior must be labeled as non-canonical until the required ADR and gate evidence exists.

## Target-project implication

IDM, Personnel, Contacts, Orders and other existing projects remain comparison inputs only. No ADR created in this workstream authorizes target-project delivery or remediation by itself.



## ADR-0002 acceptance update

Patch `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepts ADR-0002.

The gate-blocking rule remains unchanged: API-boundary rules accepted by ADR-0002 may be used as gate decision inputs, but strict gate execution still requires ADR-0006 to define severity, report structure, Maven binding and fail/report-only behavior.



## ADR-0006 acceptance update

Patch `000062_springmaster_adr_0006_verification_and_gate_strategy` accepts ADR-0006.

The gate-blocking rule is narrowed: report-only API contract tooling may now be implemented against accepted ADR-0002 and ADR-0006 semantics. Strict gate execution still requires rule-specific strict-readiness, stable implementation evidence and any remaining domain ADRs such as ADR-0005 when those areas are enforced. Persistence rules are ADR-backed by ADR-0004 after patch 000064, and Catalog-demo canonicalization rules are ADR-backed by ADR-0007 after patch 000065.

## 000063 update

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts ADR-0003.

Governance impact:

- application-layer and transaction rules now have an accepted ADR rule source;
- report-only Java boundary diagnostics may use ADR-0003 as `ruleSource`;
- strict Java boundary gates still require ADR-0006 strict-promotion evidence;
- ADR-0004 is accepted by patch 000064; ADR-0007 is accepted by patch 000065 and may be used as the G5 readiness rule source.




## ADR-0004 acceptance update

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts ADR-0004.

Governance impact:

- persistence identity, `DomainEntity`, optimistic-locking and repository-boundary rules may now be used as accepted rule sources for report-only diagnostics;
- strict persistence gates still require stable implementation, Catalog-demo evidence and explicit strict-promotion under ADR-0006;
- Catalog-demo canonicalization diagnostics may now reference ADR-0007; strict canonicalization still needs implementation evidence and explicit promotion under ADR-0006.

## ADR-0007 acceptance update

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts ADR-0007.

Governance impact:

- Catalog-demo lifecycle states are decision-backed: `legacy-demo-seed`, `candidate-reference-slice`, `canonical-reference-slice` and `deprecated-seed-fragment`;
- G5 readiness diagnostics may use ADR-0007 as `ruleSource`;
- declaring a CatalogItem slice canonical requires explicit evidence and accepted deferrals;
- target-project comparison remains read-only and waits for canonical Catalog-demo evidence;
- ADR-0005 is accepted by patch 000066; strict permission gates still require implementation evidence and promotion.

## ADR-0005 acceptance update

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts ADR-0005.

Governance impact:

- endpoint classification, permission naming, role-to-permission mapping and authorization-placement rules now have an accepted ADR rule source;
- report-only G4 security diagnostics may use ADR-0005 as `ruleSource`;
- Catalog-demo `documented-deferred-security` evidence is now decision-backed;
- strict security gates still require implemented security behavior, test fixtures, Catalog-demo proof and explicit strict promotion under ADR-0006;
- ADR-0008, ADR-0009 and ADR-0010 remain planned P1 ADRs.

## Report-only gate seed planning since 000067

Patch `000067_springmaster_report_only_gate_seed_plan` follows the accepted ADR set with a documentation-only implementation plan for the first non-blocking gate seed.

Governance impact:

- accepted ADRs `ADR-0002` through `ADR-0007` are sufficient rule sources for report-only diagnostics;
- strict gate execution remains blocked until implementation evidence and explicit promotion exist;
- `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_SEED_PLAN.md` is the planning bridge between ADR governance and the first code/tooling patch;
- later P1 ADRs remain relevant but do not block the first limited report-only seed when their domains are not enforced strictly.

# Springmaster ADRs

Architecture Decision Records document durable Springmaster architecture decisions.

Standards define rules and conventions. ADRs explain why foundational choices are accepted, which alternatives were rejected, which exceptions are allowed and what consequences the decision has for Core, Tooling, Catalog-demo and later target-project comparison.

## Governance documents

| Document | Purpose |
|---|---|
| `ADR_GOVERNANCE_AND_BACKLOG_ALIGNMENT.md` | ADR status model, numbering, standards-to-ADR mapping and gate-blocking rule |
| `ADR_TEMPLATE.md` | required ADR structure for future ADRs |
| `ADR_GAP_BACKLOG.md` | prioritized backlog of required ADRs before strict gates and canonical Catalog-demo usage |

## Current accepted ADRs

| ADR | Status | Topic |
|---|---|---|
| `ADR-0001-springmaster-bootstrap.md` | Accepted | bootstrap Springmaster as platform source project |
| `ADR-0002-api-boundary-and-endpoint-contract.md` | Accepted | API boundary and endpoint contract for new reference APIs |
| `ADR-0003-application-layer-and-transaction-boundary.md` | Accepted | controller, service, use-case, repository and transaction boundaries |
| `ADR-0004-persistence-identity-and-domainentity-strategy.md` | Accepted | persistence identity, DomainEntity, business keys, optimistic locking, audit and repository boundary |
| `ADR-0005-security-and-permission-boundary.md` | Accepted | endpoint security classification, permission naming, role mapping, authorization placement and Catalog-demo security evidence |
| `ADR-0006-verification-and-gate-strategy.md` | Accepted | verification, gate severity, report structure, Maven profile model and target-comparison policy |
| `ADR-0007-catalog-demo-canonicalization-strategy.md` | Accepted | Catalog-demo canonicalization states, evidence, deferrals and target-comparison boundary |
| `ADR-0008-configuration-and-runtime-profile-strategy.md` | Accepted | configuration sources, runtime profiles, secret classification and generated-project contract |
| `ADR-0011-command-precheck-and-capability-boundary.md` | Accepted | optional command precheck endpoints and backend/frontend capability boundary |

| `ADR-0012-patch-transaction-and-evidence-boundary.md` | Accepted | Patch transaction, evidence, retention and export boundary |

## Planned ADR backlog

ADR-0008 is accepted. ADR-0009 and ADR-0010 remain planned; ADR-0011 was accepted out of sequence because command prechecks became an immediate cross-project architecture decision.

| ADR | Priority | Planning status | Topic |
|---|---|---|---|
| ADR-0008 | P1 | accepted | Configuration and Runtime Profile Strategy |
| ADR-0009 | P1 | needed | Database Migration and DBTool Strategy |
| ADR-0010 | P1 | needed | Observability and Error Trace Strategy |
| ADR-0011 | P0 | accepted | Command Precheck and Capability Boundary |

## ADR-0002 update

Patch `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepts the API boundary and endpoint contract ADR. Endpoint, DTO, validation, query/reference-data, error, command and first-slice status-code rules are now ADR-backed for new Springmaster reference APIs. Strict gate execution still requires ADR-0006 for gate severity, report structure and Maven binding.

## Tooling rule

Strict gate tooling must not encode an ADR-required architectural rule until the corresponding ADR is accepted or the governance document explicitly classifies the rule as `ready-for-tooling-without-adr`.

Report-only tooling may be introduced earlier when it does not block builds and clearly labels findings as non-binding.



## ADR-0006 update

Patch `000062_springmaster_adr_0006_verification_and_gate_strategy` accepts the verification and gate strategy ADR. Report-only gate tooling may now be designed against accepted mode, severity and report semantics. Strict gate execution remains limited to rules whose implementation is stable, tested and explicitly promoted.

## ADR-0003 update

Patch `000063_springmaster_adr_0003_application_layer_transaction_boundary` accepts the application-layer and transaction-boundary ADR. Controller, service, use-case, repository, mapper and transaction-placement decisions are now ADR-backed for new Springmaster reference APIs and Catalog-demo implementation work.

Report-only Java boundary diagnostics may reference ADR-0003 as a rule source. Strict Java boundary gates still require stable implementation evidence, Catalog-demo proof and an explicit strict-promotion patch under ADR-0006.




## ADR-0004 update

Patch `000064_springmaster_adr_0004_persistence_identity_domainentity_strategy` accepts the persistence identity and DomainEntity strategy ADR. `DomainEntity`, opaque public IDs, business keys, `persistenceVersion`, audit fields, repository boundary and deferred persistence features are now ADR-backed for new Springmaster reference APIs and Catalog-demo persistence work.

Report-only persistence identity diagnostics may reference ADR-0004 as a rule source. Strict persistence gates still require stable implementation evidence, Catalog-demo proof and explicit strict promotion under ADR-0006.

## ADR-0007 update

Patch `000065_springmaster_adr_0007_catalog_demo_canonicalization_strategy` accepts the Catalog-demo canonicalization ADR. Catalog-demo now has explicit lifecycle states: `legacy-demo-seed`, `candidate-reference-slice`, `canonical-reference-slice` and `deprecated-seed-fragment`.

A CatalogItem slice may be implemented incrementally, but it may be declared canonical only when endpoint, DTO, validation, error, application-layer, persistence, mapping, security-classification, gate-evidence and deferral criteria are documented. Target projects remain read-only comparison inputs and are not changed by this ADR.

## ADR-0005 update

Patch `000066_springmaster_adr_0005_security_and_permission_boundary` accepts the security and permission boundary ADR. Endpoint classification, permission naming, role-to-permission mapping, authorization placement, current-user/capability contracts and Catalog-demo `documented-deferred-security` evidence are now ADR-backed.

Report-only G4 security diagnostics may reference ADR-0005 as a rule source. Strict security gates still require implementation evidence, Catalog-demo security tests, permission catalog behavior and explicit strict promotion under ADR-0006.




## ADR-0011 update

Patch `000082_springmaster_command_precheck_capability_standard` accepts the command precheck and capability boundary ADR. Command prechecks are optional side-effect-free backend capability queries for concrete commands. They support UI control state but never replace execution-time permission and policy validation.

The accepted decision keeps target projects read-only: IDM, Personnel, Contacts and Orders are not updated by this Springmaster standard patch. Any target-project adoption must happen through a later explicit project patch or Springmaster update workflow.

## ADR-0008 update

Patch `000143_springmaster_configuration_contract` accepts the configuration and runtime-profile strategy. The machine-readable environment contract, validator and Project-New propagation are now normative.

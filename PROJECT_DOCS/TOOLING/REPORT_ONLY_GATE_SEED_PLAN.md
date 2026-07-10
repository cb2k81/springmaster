
# Springmaster Report-only Gate Seed Plan

## Purpose

This document defines the first Springmaster report-only gate seed before Java, Maven or parser implementation begins.

The plan converts the accepted ADR baseline into an implementable but non-blocking diagnostic scope. It defines the initial gate IDs, rule sources, report shape, finding schema, evidence markers, Maven profile target picture and Catalog-demo relationship. It does not introduce code, Maven profiles, tests, OpenAPI parsers, ArchUnit rules or target-project changes.

## Baseline

This plan is based on the accepted ADR set after patch `000066_springmaster_adr_0005_security_and_permission_boundary`:

| ADR | Status | Gate relevance |
|---|---|---|
| `ADR-0002` | Accepted | API boundary, endpoints, DTOs, validation, errors, query vocabulary and status codes |
| `ADR-0003` | Accepted | controller, service, use-case, repository, mapper and transaction boundaries |
| `ADR-0004` | Accepted | persistence identity, `DomainEntity`, business keys, optimistic locking, audit and repository boundary |
| `ADR-0005` | Accepted | security classification, permission naming, authorization placement and Catalog-demo security evidence |
| `ADR-0006` | Accepted | gate layers, report-only mode, strict promotion and report structure |
| `ADR-0007` | Accepted | Catalog-demo canonicalization states, evidence and target-comparison block |

The first seed is therefore allowed to produce diagnostics from accepted rule sources. It is not allowed to fail the build for rule findings.

## Non-goals

The first gate seed must not:

- introduce strict gates;
- bind itself into the default Maven lifecycle;
- change target projects;
- generate remediation patches;
- declare Catalog-demo canonical;
- compare IDM, Personnel, Contacts, Orders or any other target project;
- require live databases, external services or running applications;
- introduce security fixtures or role persistence;
- introduce generated project updates.

## Seed identity

Canonical seed identifier:

```text
springmaster.report-only-gate-seed.v1
```

Initial execution mode:

```text
report-only
```

Initial report scope:

```text
springmaster-reference-only
```

Target comparison remains out of scope. Any accidental target-project input must be reported as tool input error, not as a target finding.

## First gate set

The first seed should define these diagnostic gates.

| Gate ID | Layer | Mode | Purpose | Primary rule source |
|---|---|---|---|---|
| `SM-G0-RULE-SOURCE-COVERAGE` | G0 | report-only | verify that findings can point to ADR-backed rule sources | `ADR-0006` |
| `SM-G1-HTTP-VOCABULARY` | G1 | report-only | detect non-canonical public API path vocabulary | `ADR-0002` |
| `SM-G1-QUERY-PARAMETERS` | G1 | report-only | detect query vocabulary drift such as `sort` versus `sortBy` | `ADR-0002` |
| `SM-G1-STATUS-ERROR-CONTRACT` | G1 | report-only | inspect status-code and error-contract evidence where available | `ADR-0002` |
| `SM-G3-APPLICATION-BOUNDARY-HINTS` | G3 | report-only | report controller, transaction, repository and mapper boundary risks | `ADR-0003` |
| `SM-G3-PERSISTENCE-IDENTITY-HINTS` | G3 | report-only | report persistence identity and public-ID risks | `ADR-0004` |
| `SM-G4-SECURITY-CLASSIFICATION` | G4 | report-only | report missing classification and permission evidence | `ADR-0005` |
| `SM-G5-CATALOG-READINESS-EVIDENCE` | G5 | report-only | summarize candidate/canonical evidence for Catalog-demo | `ADR-0007` |

The first implementation may start with a smaller subset if it still writes the same report shape and explicitly marks unsupported gates as `INFO` or omits them with a tool capability note.

## Initial rule candidates

The first implementation should prefer deterministic, low-risk checks.

| Rule ID | Gate ID | Initial severity | Diagnostic only condition |
|---|---|---|---|
| `SM-API-DELETE-BODY-001` | `SM-G1-HTTP-VOCABULARY` | `ERROR` | single-resource `DELETE` appears to require a request body |
| `SM-API-FIND-VOCAB-001` | `SM-G1-HTTP-VOCABULARY` | `WARNING` | public path segment or operation naming exposes `findOne`, `findFirst` or `findLast` |
| `SM-API-ALL-ENDPOINT-001` | `SM-G1-HTTP-VOCABULARY` | `WARNING` | ambiguous, selector-like, undocumented or silently capped `/all` is present; documented complete-result-set `/all` is expected evidence, not a finding |
| `SM-API-OPTIONS-001` | `SM-G1-HTTP-VOCABULARY` | `INFO` | `/options` is present and should be bounded selector evidence |
| `SM-API-SORTBY-001` | `SM-G1-QUERY-PARAMETERS` | `WARNING` | `sort` appears where canonical `sortBy` is expected |
| `SM-API-ARGNAME-001` | `SM-G1-QUERY-PARAMETERS` | `WARNING` | generated query parameter names like `arg0` or `arg1` appear |
| `SM-API-STATUS-001` | `SM-G1-STATUS-ERROR-CONTRACT` | `INFO` | create/update/delete/command status-code evidence is present or missing |
| `SM-API-ERROR-001` | `SM-G1-STATUS-ERROR-CONTRACT` | `INFO` | error shape evidence includes or lacks `errorId`, `errorType`, `message`, `path` and `method` |
| `SM-JAVA-CONTROLLER-REPO-001` | `SM-G3-APPLICATION-BOUNDARY-HINTS` | `WARNING` | controller appears to inject repository or `EntityManager` |
| `SM-JAVA-CONTROLLER-TX-001` | `SM-G3-APPLICATION-BOUNDARY-HINTS` | `WARNING` | controller appears to own a transaction boundary |
| `SM-JAVA-MAPPER-DEPENDENCY-001` | `SM-G3-APPLICATION-BOUNDARY-HINTS` | `WARNING` | mapper appears to use repository, service, security or transaction dependencies |
| `SM-JAVA-ID-LEAK-001` | `SM-G3-PERSISTENCE-IDENTITY-HINTS` | `WARNING` | public DTO or OpenAPI schema appears to leak numeric internal IDs |
| `SM-SEC-CLASSIFICATION-001` | `SM-G4-SECURITY-CLASSIFICATION` | `WARNING` | Catalog-demo endpoint lacks classification evidence |
| `SM-SEC-PERMISSION-001` | `SM-G4-SECURITY-CLASSIFICATION` | `WARNING` | management endpoint lacks intended permission evidence |
| `SM-DEMO-EVIDENCE-001` | `SM-G5-CATALOG-READINESS-EVIDENCE` | `MANUAL_REVIEW` | Catalog-demo candidate lacks readiness/evidence summary |

Even when a rule uses severity `ERROR`, the first seed remains `report-only` and exits successfully when the tool itself runs successfully.

## Report shape

The future implementation must write compact terminal output and detailed report files.

Canonical directory:

```text
target/springmaster-gates/<gate-run-id>/
```

Required files:

| File | Required | Purpose |
|---|---|---|
| `summary.txt` | yes | compact human-readable summary |
| `summary.json` | yes | machine-readable totals and tool metadata |
| `findings.jsonl` | yes | one JSON object per finding |
| `rule-sources.json` | yes | ADRs and standards used for this run |
| `input-manifest.json` | yes | analyzed inputs and unavailable inputs |
| `evidence/` | optional | copied/generated evidence such as OpenAPI snapshots or class metadata |

`summary.txt` must be safe for terminal output. It should include counts by gate and severity, not full finding dumps.

## Finding schema

Every finding object in `findings.jsonl` must include:

| Field | Required | Meaning |
|---|---|---|
| `gateId` | yes | gate identifier, e.g. `SM-G1-QUERY-PARAMETERS` |
| `ruleId` | yes | stable rule identifier |
| `layer` | yes | `G0` through `G6` |
| `mode` | yes | initially always `report-only` |
| `severity` | yes | `BLOCKER`, `ERROR`, `WARNING`, `INFO` or `MANUAL_REVIEW` |
| `ruleSource` | yes | ADR or standard path |
| `subject` | yes | endpoint, class, schema or evidence subject |
| `message` | yes | compact human-readable statement |
| `remediation` | no | suggested remediation |
| `path` | no | HTTP path, if applicable |
| `method` | no | HTTP method, if applicable |
| `className` | no | Java class, if applicable |
| `memberName` | no | method or field, if applicable |
| `expected` | no | expected value |
| `actual` | no | actual value |

The schema is deliberately JSONL-friendly so future scripts, CI jobs and review tools can consume it without loading a large JSON document.

## Rule-source registry for the seed

The first implementation must emit the used rule sources in `rule-sources.json`.

Minimum registry entries:

| Rule source | Required for seed |
|---|---|
| `PROJECT_DOCS/ADR/ADR-0002-api-boundary-and-endpoint-contract.md` | yes |
| `PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md` | yes |
| `PROJECT_DOCS/ADR/ADR-0004-persistence-identity-and-domainentity-strategy.md` | yes |
| `PROJECT_DOCS/ADR/ADR-0005-security-and-permission-boundary.md` | yes |
| `PROJECT_DOCS/ADR/ADR-0006-verification-and-gate-strategy.md` | yes |
| `PROJECT_DOCS/ADR/ADR-0007-catalog-demo-canonicalization-strategy.md` | yes |
| `PROJECT_DOCS/STANDARDS/API/API_ENDPOINT_CONTRACT_STANDARD.md` | optional but recommended |
| `PROJECT_DOCS/STANDARDS/API/API_QUERY_REFERENCE_DATA_CONSISTENCY_STANDARD.md` | optional but recommended |
| `PROJECT_DOCS/STANDARDS/API/API_ERROR_CONTRACT_STANDARD.md` | optional but recommended |
| `PROJECT_DOCS/STANDARDS/CONTROLLER_SERVICE_USECASE_TRANSACTION_STANDARD.md` | optional but recommended |
| `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md` | optional but recommended |
| `PROJECT_DOCS/STANDARDS/SECURITY_PERMISSION_BOUNDARY_STANDARD.md` | optional but recommended |
| `PROJECT_DOCS/DEMO/CATALOG_DEMO_READINESS_PLAN.md` | optional but recommended |

A missing rule source is a tool setup problem and may make the tool exit non-zero, because findings would otherwise be ungrounded.

## Input sources

The first seed may consume these Springmaster-local inputs:

- generated or committed OpenAPI JSON/YAML, if available;
- Java source files under the Springmaster repository;
- compiled classes, if a later implementation chooses classpath/reflection scanning;
- Catalog-demo readiness documentation;
- ADR and standard documents listed above.

The first seed must not require live target projects. It must not scan `/opt/cocondo/idm`, `/opt/cocondo/personnel`, `/opt/cocondo/contacts` or `/opt/cocondo/orders`.

## Maven profile target picture

The first code/tooling implementation may introduce a dedicated script first, but the canonical future Maven profile remains:

```text
springmaster-gates-report
```

A future invocation may become:

```text
mvn -P springmaster-gates-report verify
```

or a wrapper may call Maven after preparing inputs. The default `mvn test` lifecycle must not be made stricter by the first seed.

The future profile must run in report-only mode and must not fail because it found rule findings. It may fail only when the gate tool itself cannot run or cannot write a reliable report.

## Catalog-demo relationship

The first seed supports Catalog-demo readiness; it does not canonicalize Catalog-demo.

Catalog-demo remains:

```text
legacy-demo-seed
```

until a later implementation patch creates a candidate slice with evidence. The gate seed may report missing evidence, but it must not change the state to `candidate-reference-slice` or `canonical-reference-slice`.

## Exit behavior

Report-only execution exits successfully when:

- inputs were readable;
- rule sources were known;
- reports were written;
- findings, including `ERROR` findings, were recorded successfully.

Report-only execution may exit non-zero when:

- the tool cannot parse its mandatory inputs;
- the report directory cannot be written;
- required ADR rule sources are missing;
- the tool crashes before writing summary files;
- invalid arguments or unsupported mode are passed.

## Acceptance criteria for the first code/tooling patch

The next code/tooling patch that implements this plan must prove at least:

1. a deterministic report directory is created under `target/springmaster-gates/`;
2. `summary.txt`, `summary.json`, `findings.jsonl`, `rule-sources.json` and `input-manifest.json` are written;
3. the terminal summary remains compact;
4. rule findings do not make report-only execution fail;
5. tool execution failures are distinguishable from rule findings;
6. at least one G1 and one G0 diagnostic are implemented;
7. no target project is scanned or modified;
8. a validation command produces a Full ZIP export path after patch application.

## Deferred implementation topics

Deferred beyond the first code/tooling seed:

- strict gate profile;
- target-comparison profile;
- OpenAPI operationId/tag/schema-name strictness;
- security fixture execution;
- role/permission persistence;
- ArchUnit dependency;
- automatic remediation;
- generated target delivery;
- default lifecycle binding.

## Implementation status after 000068

Patch `000068_springmaster_report_only_gate_tooling_seed` implements the first standalone report-only seed.

Implemented files:

- `bin/springmaster-gates.py`
- `bin/springmaster-gates.sh`
- `bin/springmaster-gates-selfcheck.sh`
- `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_TOOLING.md`

The implementation writes the required report files under `target/springmaster-gates/<gate-run-id>/`, keeps the scope at `springmaster-reference-only`, rejects target-project input and exits successfully when report-only findings are recorded.

The implementation deliberately remains source-based and low-risk. OpenAPI parser integration, Maven profile binding, target comparison, strict gates and Catalog-demo candidate/canonical promotion remain deferred.


## Regression and Maven profile status after 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` promotes the report-only seed from standalone script validation to repeatable regression coverage.

Implemented after 000069:

- `bin/springmaster-gates-regression.sh` validates the report shape, schema markers, JSON/JSONL structure and safety behavior.
- `summary.json`, `rule-sources.json` and `input-manifest.json` carry the stable report schema marker `springmaster.report-only-report.v1`.
- A JUnit regression test executes the script during `mvn test`.
- Maven profile `springmaster-gates-report` enables an additional profile-specific report run with run id `maven-profile`.
- Target-project input rejection is covered as a regression rule.
- Duplicate report directory rejection without `--clean` is covered as a regression rule.

Still deferred:

- strict gate profile;
- target comparison profile;
- OpenAPI parser backed diagnostics;
- ArchUnit backed Java boundary diagnostics;
- Catalog-demo candidate/canonical promotion.

## Findings baseline status after 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` records the first forensic interpretation of the executable report output from the 000068/000069 tooling seed.

The baseline accepts the current `12` report-only findings as expected for the current state:

- G0 ADR rule-source findings are positive evidence.
- G1 query and status/error findings describe Catalog-demo `legacy-demo-seed` gaps.
- G4 security classification warning is valid only while deferred security remains documented.
- G5 manual review is required because Catalog-demo is not yet candidate or canonical.

The review does not introduce strict gates, target scans, implementation changes or Maven behavior changes.

## Catalog-demo candidate contract plan after 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` does not change the gate seed behavior. It defines how the Catalog-demo G1, G4 and G5 report-only findings should be addressed by the next candidate implementation patch.

Seed impact:

- the current `12` findings remain the accepted baseline until Catalog-demo code changes;
- future G1 evidence should come from canonical `page`, `size`, `sortBy`, `sortDir`, standard error bodies and bodyless delete;
- future G4 evidence should come from documented endpoint classification and permission vocabulary, or implemented management security;
- future G5 evidence should come from an explicit `candidate-reference-slice` evidence file;
- target-project comparison remains excluded.

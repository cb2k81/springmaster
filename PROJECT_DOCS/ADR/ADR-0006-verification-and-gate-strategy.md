# ADR-0006: Verification and Gate Strategy

## Status

Accepted

## Date

2026-06-30

## Context

Springmaster is becoming the master/reference project for backend foundation, standards, conventions, reference implementations and verifiable quality gates.

Patches `000044` through `000059` documented and harmonized the first API, DTO, validation, error, endpoint, command, mapping, persistence, security and Catalog-demo readiness standards. Patch `000060_springmaster_adr_governance_and_backlog_alignment` established ADR governance. Patch `000061_springmaster_adr_0002_api_boundary_and_endpoint_contract` accepted the first API boundary ADR.

The remaining risk before API contract gate tooling is not lack of standards. The risk is encoding rules too early, too strictly or without stable report semantics. Gate tooling must therefore distinguish report-only diagnostics, strict build-failing checks and manual-review findings.

Existing applications such as IDM, Personnel, Contacts and Orders remain comparison inputs only. They must not be changed by a Springmaster gate. Target-project comparison is read-only until Catalog-demo has proven the standards and a later delivery decision exists.

## Decision

Springmaster adopts a layered verification strategy for standards and reference implementations.

### Gate layers

| Layer | Name | Purpose | First status |
|---|---|---|---|
| G0 | Documentation gate | prove that a rule is documented and ADR-backed when required | active through patch review |
| G1 | OpenAPI contract gate | verify public paths, methods, request bodies, query parameters, schemas, required fields, errors and status codes | report-only first |
| G2 | MVC behavior gate | verify runtime HTTP behavior with MockMvc or equivalent Spring MVC integration tests | reference-demo first |
| G3 | Java boundary gate | verify controller, DTO, mapper, repository, transaction and entity boundary rules by reflection/classpath scan or ArchUnit | report-only first |
| G4 | Security gate | verify authentication, authorization, permission and capability contracts | deferred until ADR-0005 |
| G5 | Catalog-demo reference gate | prove that the reference implementation satisfies the standards as an integrated slice | required before canonicalization |
| G6 | Target comparison gate | compare existing projects read-only against Springmaster standards | report-only only until target delivery is explicitly authorized |

A gate must identify its layer and rule source in every finding.

### Gate execution modes

Springmaster uses three execution modes:

| Mode | Meaning | Exit behavior |
|---|---|---|
| `report-only` | diagnostic, non-binding and suitable before a rule is fully strict-ready | exits successfully when the tool itself runs successfully, even if findings exist |
| `strict` | binding quality gate for rules that are accepted, implemented and stable | exits non-zero on `BLOCKER` or `ERROR` findings |
| `manual-review` | produces evidence for a human decision where full automation would be brittle or premature | exits successfully unless the tool itself fails |

The first API contract gate tooling seed must be `report-only`. Strict execution is allowed only after the specific gate has reference evidence from Catalog-demo or a later ADR/document explicitly marks it strict-ready.

### Finding severity

Gate findings use this severity vocabulary:

| Severity | Meaning | Strict-mode effect |
|---|---|---|
| `BLOCKER` | rule violation that invalidates canonical reference status or strict gate execution | fail |
| `ERROR` | clear violation of an accepted, mechanically checkable rule | fail |
| `WARNING` | likely issue, legacy tolerance, target-comparison finding or deferred rule | do not fail |
| `INFO` | informational evidence or positive/neutral diagnostic | do not fail |
| `MANUAL_REVIEW` | human decision required because automation cannot safely decide | do not fail automatically |

`BLOCKER` must be used sparingly. A documentation-only or report-only finding must not be escalated to `BLOCKER` unless an ADR or readiness document explicitly says the missing evidence blocks the next phase.

### Canonical future Maven profiles

When gate tooling becomes Maven-bound, Springmaster uses these canonical profile names:

| Profile | Purpose | Default strictness |
|---|---|---|
| `springmaster-gates-report` | run supported gates in report-only mode | non-blocking |
| `springmaster-gates-strict` | run only gates explicitly marked strict-ready | build-blocking on `BLOCKER` and `ERROR` |
| `springmaster-gates-target-compare` | read-only comparison against existing target projects | non-blocking |

The profiles are not introduced by this ADR. A later code/tooling patch may introduce them. Until then, shell scripts or test utilities may be used if they keep the same mode semantics and report structure.

### Report structure

Gate output must keep terminal output compact. Detailed findings go to files.

Canonical future report directory:

```text
target/springmaster-gates/<gate-run-id>/
```

Required report files for implemented gate runs:

| File | Purpose |
|---|---|
| `summary.txt` | compact human-readable summary suitable for terminal excerpt |
| `summary.json` | machine-readable count by gate, layer, severity and mode |
| `findings.jsonl` | one JSON object per finding |
| `evidence/` | optional copied/generated evidence such as OpenAPI snapshots or extracted controller metadata |

Each finding must include at least:

- `gateId`;
- `layer`;
- `mode`;
- `severity`;
- `ruleSource`;
- `subject`;
- `message`.

Optional fields may include `path`, `method`, `operationId`, `className`, `memberName`, `expected`, `actual` and `remediation`.

### First report-only gate scope

The first report-only API contract tooling seed may inspect only rules that are already documented and ADR-backed or explicitly classified as diagnostic.

Allowed first checks:

- body-bearing single `DELETE` detection;
- public endpoint path vocabulary findings such as public `findOne`, `findFirst`, `findLast` path segments;
- query parameter findings for `page`, `size`, `sortBy`, `sortDir` and generated `arg0`/`arg1` style parameters;
- `/all` path reporting as non-canonical for new reference APIs;
- `/options` recognition as bounded selector vocabulary;
- required-field and request-body evidence where the generated OpenAPI shape is stable enough;
- standard error response evidence for common error statuses;
- DTO/entity leakage hints where schema names or Java signatures make this safely detectable.

The first tooling seed must not strictly fail on:

- OpenAPI operationId naming;
- tag naming;
- schema naming;
- security scheme completeness;
- permission catalog completeness;
- persistence identity details;
- Catalog-demo canonicalization status;
- target-project deviations.

Those areas require additional ADRs, standards, Catalog-demo evidence or later strict-readiness decisions.

### Strict gate promotion rule

A report-only gate may be promoted to strict only when all of the following are true:

1. The rule source is an accepted ADR or explicitly marked `ready-for-tooling-without-adr`.
2. The gate implementation is stable and tested.
3. Catalog-demo demonstrates the rule, unless the rule is tool-internal and independent of demo code.
4. The gate has deterministic pass/fail criteria.
5. The gate writes compact reports.
6. The promotion is documented by a patch with changelog and version metadata.

### Fail-fast behavior

Strict gates should aggregate findings and write reports before failing. Fail-fast is allowed only for tool execution failures that make the report unreliable, such as missing input artifact, invalid OpenAPI JSON, unsupported runtime or corrupted classpath metadata.

Report-only gates must distinguish tool execution failures from rule findings. A report-only gate may exit non-zero when the gate cannot run at all, but not merely because it found non-binding findings.

### Target comparison policy

G6 target comparison remains read-only. It may identify deviations in IDM, Personnel, Contacts, Orders or other target projects, but it must not generate remediation patches, target updates or delivery payloads unless a later ADR and explicit user approval authorize that workflow.

Target-comparison reports must label findings as `target-comparison`, not as Springmaster reference violations.

## Scope

This ADR applies to:

- Springmaster gate concepts;
- future Springmaster API contract tooling;
- future Maven gate profiles;
- future Catalog-demo gate evidence;
- future read-only target comparison.

This ADR does not introduce Java code, Maven profiles, OpenAPI parsers, MockMvc tests, ArchUnit rules, shell tools, Catalog-demo implementation or target-project changes.

## Affected standards

This ADR accepts and narrows:

- `PROJECT_DOCS/STANDARDS/API/API_CONTRACT_GATE_CONCEPT.md`
- `PROJECT_DOCS/STANDARDS/STANDARD_CONSISTENCY_AND_ADR_GAP_REVIEW.md`
- `PROJECT_DOCS/ADR/ADR_GOVERNANCE_AND_BACKLOG_ALIGNMENT.md`
- `PROJECT_DOCS/ADR/ADR_GAP_BACKLOG.md`

It depends on accepted `ADR-0002-api-boundary-and-endpoint-contract.md` for API-boundary rule sources.

It does not replace future ADRs for application-layer boundaries, persistence identity, Catalog-demo canonicalization, security/permissions, configuration, DB migrations or observability.

## Considered alternatives

### Make all documented standards strict immediately

Rejected. The standards are extensive, but not all have Catalog-demo evidence, tool implementation evidence or accepted ADR coverage. Strict tooling now would likely create brittle checks and false confidence.

### Keep all gates permanently manual

Rejected. Springmaster must become a verifiable reference project. Manual review remains useful, but core API and boundary contracts need mechanical evidence.

### Bind the first gate tooling directly into default `mvn test`

Rejected for the first tooling seed. Default `mvn test` should remain stable until the first gates prove themselves in report-only mode. Later strict profiles may be bound into quality workflows deliberately.

### Use ArchUnit first

Rejected as the first step. ArchUnit may be useful later, but initial gates should prioritize OpenAPI and MockMvc because they verify public API contracts with less dependence on package heuristics.

### Use target-project comparison as the first strict gate

Rejected. Existing projects are comparison inputs only. Catalog-demo must prove the standards before target comparison can become meaningful.

## Consequences

Positive consequences:

- The first gate tooling can be introduced safely as report-only diagnostics.
- Strict gates have a defined promotion path.
- Terminal output remains bounded through report files.
- Maven profile names are defined before implementation.
- Target-project comparison remains non-destructive.
- Gate findings can reference accepted ADRs and standards.

Costs and constraints:

- More documentation work is required before strict enforcement.
- The first tooling seed must avoid overreaching into unresolved domains.
- Some useful checks remain warning/report-only until Catalog-demo and later ADRs provide stronger evidence.

## Gate implications

This ADR enables the next tooling seed to implement report-only G1/G2/G3 diagnostics.

Strict gates remain blocked for individual rule areas until their strict-promotion criteria are met. In particular:

- API-boundary rules may reference ADR-0002, but strict execution requires implemented and tested gates.
- Controller/service/transaction boundary strict gates still require ADR-0003.
- Persistence strict gates still require ADR-0004.
- Catalog-demo canonicalization still requires ADR-0007.
- Security strict gates still require ADR-0005.

## Exceptions and deferrals

Deferred:

- exact Java package and class names for gate utilities;
- exact OpenAPI parser library;
- exact MockMvc fixture API;
- exact ArchUnit adoption timing;
- exact CI integration;
- target-project remediation or delivery workflows.

Allowed exception:

- A later patch may introduce a small standalone report-only tool before Maven profiles exist, as long as it follows this ADR's mode, severity and report semantics.

## Supersession

This ADR does not supersede ADR-0001 or ADR-0002.

A later ADR may supersede this ADR if Springmaster replaces the gate execution model, Maven profile model or target-comparison policy.

## Report-only gate seed plan since 000067

Patch `000067_springmaster_report_only_gate_seed_plan` adds `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_SEED_PLAN.md` as the implementation planning document for the first non-blocking gate seed.

Clarifications for the first implementation:

- the first seed identity is `springmaster.report-only-gate-seed.v1`;
- the first scope is `springmaster-reference-only`;
- target comparison remains excluded;
- report-only execution must exit successfully when findings are recorded and reports are written;
- tool execution failures remain distinct from rule findings;
- first implementation may start with a subset of G0/G1/G3/G4/G5 diagnostics, but must write the canonical report files;
- strict promotion remains unavailable until a later patch explicitly promotes selected rules under this ADR.

## Implementation note after 000068

Patch `000068_springmaster_report_only_gate_tooling_seed` introduces the first standalone implementation of this ADR's report-only seed strategy.

The implementation is intentionally limited to `report-only` mode and `springmaster-reference-only` scope. It writes `summary.txt`, `summary.json`, `findings.jsonl`, `rule-sources.json` and `input-manifest.json` below `target/springmaster-gates/<gate-run-id>/`.

The implementation does not introduce strict enforcement, Maven profile binding, target-project comparison, OpenAPI parser dependency, ArchUnit dependency or automatic remediation. Rule findings remain non-blocking. Tool setup/runtime errors remain blocking for the tool invocation.


## Implementation note after 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` adds regression coverage and a Maven profile for the first report-only seed.

The accepted interpretation of this ADR remains unchanged:

- `springmaster-gates-report` is report-only.
- Rule findings do not fail the build in report-only mode.
- Tool setup/runtime errors fail validation.
- Target-project input remains rejected by the first seed.
- Strict gate promotion still requires a later explicit patch and evidence.

The report schema marker for the first seed is:

```text
springmaster.report-only-report.v1
```

## Findings baseline note after 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` records the first interpretation baseline for the report-only gate output.

The baseline confirms that a report-only run may contain non-zero findings and still be successful when the tool itself runs correctly. The current `12` findings include no `BLOCKER` and no `ERROR`. The two warnings and one manual-review finding are treated as expected Catalog-demo legacy-seed evidence, not as strict failures.

This note does not promote any rule to strict mode. Strict promotion still requires explicit readiness and a later patch under this ADR.

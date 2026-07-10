# Springmaster Report-only Gate Tooling

## Purpose

Patch `000068_springmaster_report_only_gate_tooling_seed` introduces the first executable Springmaster gate seed.

The tool implements the report-only planning scope from `PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_SEED_PLAN.md` without changing Java application behavior, Maven defaults, Catalog-demo state or target projects.

## Commands

Primary command:

```bash
./bin/springmaster-gates.sh report
```

Deterministic selfcheck:

```bash
./bin/springmaster-gates-selfcheck.sh
```

The wrapper delegates to:

```text
bin/springmaster-gates.py
```

## Supported mode and scope

The first seed supports exactly one mode:

```text
report-only
```

The first seed supports exactly one scope:

```text
springmaster-reference-only
```

Target-project input is intentionally rejected. The tool must not scan or modify IDM, Personnel, Contacts, Orders or any other configured target project.

## Report directory

Each run writes:

```text
target/springmaster-gates/<gate-run-id>/
```

Required report files are:

- `summary.txt`
- `summary.json`
- `findings.jsonl`
- `rule-sources.json`
- `input-manifest.json`

`summary.txt` is compact and terminal-safe. Detailed findings are written to `findings.jsonl`.

## Implemented first-seed diagnostics

The first implementation is source-based and deterministic. It does not require a running application, generated OpenAPI file, database, compiled classes or target project.

Implemented diagnostics include:

| Gate | Rule examples | Source |
|---|---|---|
| `SM-G0-RULE-SOURCE-COVERAGE` | required accepted ADR rule sources are present | `ADR-0006` |
| `SM-G1-HTTP-VOCABULARY` | ambiguous `/all`, bounded `/options`, `findOne`/`findFirst`/`findLast` path vocabulary hints; complete-result-set `/all` must be classified separately | `ADR-0002` |
| `SM-G1-QUERY-PARAMETERS` | `sort` versus `sortBy`, missing Catalog-demo query evidence | `ADR-0002` |
| `SM-G1-STATUS-ERROR-CONTRACT` | status-code and ad-hoc error response evidence | `ADR-0002` |
| `SM-G3-APPLICATION-BOUNDARY-HINTS` | controller repository/transaction hints and mapper dependency hints | `ADR-0003` |
| `SM-G3-PERSISTENCE-IDENTITY-HINTS` | numeric public DTO id leakage hints | `ADR-0004` |
| `SM-G4-SECURITY-CLASSIFICATION` | Catalog-demo security-classification evidence | `ADR-0005` |
| `SM-G5-CATALOG-READINESS-EVIDENCE` | Catalog-demo candidate/canonical evidence summary | `ADR-0007` |

All findings are non-blocking in report-only mode.

## Exit behavior

A report-only run exits with status `0` when:

- required ADR rule sources are present;
- inputs are readable;
- the report directory can be written;
- report files are produced.

Rule findings with severities such as `ERROR`, `WARNING` or `MANUAL_REVIEW` do not fail report-only execution.

The tool may exit non-zero when:

- an unsupported mode or scope is requested;
- target-project input is provided;
- required rule sources are missing;
- the report directory already exists and `--clean` is not used;
- report files cannot be written.

## Validation

Patch `000068` must be validated with at least:

```bash
bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh
python3 -m py_compile ./bin/patch.py ./bin/springmaster-gates.py
./bin/springmaster-gates-selfcheck.sh
mvn test
```

The selfcheck proves that the tool writes all required report files, that JSON files are parseable, that `findings.jsonl` is non-empty, that G0 and G1 diagnostics exist, and that required ADR rule sources are present.

## Non-goals

The first tooling seed does not implement:

- strict gates;
- strict Maven lifecycle binding;
- OpenAPI parser integration;
- ArchUnit integration;
- security fixtures;
- target-project comparison;
- generated remediation patches;
- Catalog-demo candidate or canonical promotion.

## Next implementation topics

Likely follow-up topics are:

1. OpenAPI snapshot discovery and parser-backed G1 diagnostics.
2. Dedicated report schema documentation and fixtures.
3. JSON schema stabilization for report files.
4. Better Java boundary parsing or ArchUnit-backed G3 diagnostics.
5. Catalog-demo candidate-slice evidence generation.


## Regression and Maven profile after 000069

Patch `000069_springmaster_report_only_gate_regression_and_maven_profile` hardens the first executable report-only gate seed without changing its scope or severity semantics.

New regression command:

```bash
./bin/springmaster-gates-regression.sh
```

The regression command validates:

- Shell and Python syntax for gate tooling entry points.
- Required report files: `summary.txt`, `summary.json`, `findings.jsonl`, `rule-sources.json`, `input-manifest.json`.
- Report schema marker `springmaster.report-only-report.v1`.
- Required finding fields in `findings.jsonl`.
- G0 rule-source coverage, G1 API diagnostics and G5 Catalog-demo readiness evidence.
- Duplicate report-run rejection without `--clean`.
- Target-project input rejection.
- Custom report output directory handling.

New Maven profile:

```bash
mvn -q -Pspringmaster-gates-report test
```

The profile sets `springmaster.gates.report.enabled=true` and `springmaster.gates.report.runId=maven-profile`. It runs the gate tool through JUnit regression coverage in report-only mode. Rule findings remain non-blocking; tool setup/runtime errors fail the test because an unreliable report must not be accepted.

The default `mvn test` lifecycle still validates the regression script but does not convert report-only findings into strict build failures.

## Findings baseline after 000070

Patch `000070_springmaster_report_only_gate_findings_baseline_review` classifies the first deterministic report-only findings baseline under:

```text
PROJECT_DOCS/TOOLING/REPORT_ONLY_GATE_FINDINGS_BASELINE_REVIEW.md
```

The accepted baseline contains `12` findings:

- `0` `BLOCKER`
- `0` `ERROR`
- `2` `WARNING`
- `9` `INFO`
- `1` `MANUAL_REVIEW`

This baseline is intentionally not a strict gate. The warnings and manual-review finding are expected while Catalog-demo remains `legacy-demo-seed`. They become implementation work items only when a future patch creates a `candidate-reference-slice` or explicitly promotes a rule under ADR-0006.

## Candidate slice planning after 000071

Patch `000071_springmaster_catalog_demo_candidate_slice_contract_plan` keeps the executable gate tooling unchanged.

The report runner should continue to produce report-only findings while Catalog-demo is still `legacy-demo-seed`. The candidate plan defines the expected future evidence for a CatalogItem `candidate-reference-slice`, but it does not promote any rule to strict mode and does not change target-project handling.

## Candidate-slice interpretation after 000073

Patch `000073_springmaster_catalog_demo_candidate_slice_forensic_review` does not change gate tooling, but it records a new interpretation of the report-only output after the CatalogItem candidate foundation.

Observed report-only state after `000072`:

- `9` findings;
- G1 query/vocabulary candidate issues reduced;
- G4 security warning remains expected while security is documented-deferred;
- G5 manual review remains expected, but its current legacy-state wording is a source-based heuristic limitation.

The next gate-tooling alignment should make G5 read `PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.md` before treating Catalog-demo as pure `legacy-demo-seed`.



## Candidate evidence alignment since 000074

Since `000074_springmaster_catalog_demo_candidate_slice_alignment`, the report-only runner includes `catalogDemoEvidence` in `input-manifest.json`.

The evidence is read from:

```text
PROJECT_DOCS/DEMO/CATALOGITEM_CANDIDATE_SLICE_EVIDENCE.json
```

Schema marker:

```text
springmaster.catalog-demo.candidate-evidence.v1
```

G5 now evaluates current candidate evidence before historical readiness-plan text. When `sliceState` is `candidate-reference-slice` and `canonicalState` is `not-canonical`, G5 does not emit a manual-review finding. Missing, unclassifiable or pure `legacy-demo-seed` evidence still produces `SM-G5-CATALOG-READINESS-EVIDENCE` as `MANUAL_REVIEW`.

# Generated Slice Spec Fixture Gate

**Patch:** `000123_springmaster_generated_slice_spec_fixture_gate`
**Status:** executable strict fixture gate
**Scope:** Springmaster Tooling, tests and Generated Slice contract evidence

## 1. Purpose

The Generated Slice Spec Fixture Gate turns the documentation contract from
`000122_springmaster_generated_slice_spec_contract` into executable evidence.

The gate validates the neutral golden Slice-Spec
`administration.business-partner` before an Intermediate Representation or a
patch-blueprint generator is allowed to consume the contract.

It does not generate Java files, target-project files or target-project patch
archives.

## 2. Command

```bash
./bin/generated-slice-spec-fixture-gate-report.sh
```

Default input:

```text
PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml
```

Default output:

```text
reports/tooling/generated-slice-spec-fixture-gate-report.json
```

A deterministic test invocation can set the timestamp:

```bash
./bin/generated-slice-spec-fixture-gate-report.sh \
  --out target/generated-slice-spec-fixture-gate.json \
  --generated-at 2026-07-14T00:00:00Z
```

The process exits with `0` only when the report contains zero findings. Any
parse or contract violation returns a non-zero exit code after writing the
report.

## 3. Dependency and YAML profile

The gate uses only the Python standard library. It does not depend on a
system-wide or virtual-environment `PyYAML` installation.

The supported YAML profile is intentionally strict and deterministic:

* mappings with simple string keys;
* indentation in multiples of two spaces;
* sequences;
* sequence items containing scalars or mappings;
* UTF-8 strings, quoted strings, booleans, null values and integers.

The following features are rejected fail-closed:

* tab indentation;
* anchors and aliases;
* tags;
* flow mappings and flow sequences;
* block scalar syntax;
* duplicate mapping keys;
* unsupported document markers or ambiguous indentation.

This profile is sufficient for `GeneratedServiceSlice` contract version `1`.
A later contract version may introduce a declared parser dependency, but must
not silently broaden parser behavior.

## 4. Validation groups

The JSON report records twelve deterministic check groups:

| Check | Contract evidence |
|---|---|
| `SPEC-PARSE` | strict YAML subset parses successfully |
| `SPEC-TOPLEVEL` | all eleven required top-level fields, `specVersion: 1`, correct `kind` |
| `SPEC-METADATA` | slice identity and candidate-reference metadata |
| `SPEC-PACKAGE` | neutral module package and explicit Demo-package prohibition |
| `SPEC-RESOURCE` | external id, display field and unique business key |
| `SPEC-QUERY` | list, `/all`, `/count`, filters, sort allowlist and pagination |
| `SPEC-DETAIL` | detail by id and unique alternate lookup |
| `SPEC-WRITE` | create, update, bodyless delete and success statuses |
| `SPEC-DTO` | distinct CreateDTO/UpdateDTO, explicit fields and validation metadata |
| `SPEC-ERROR` | global Core error response and explicit `400`/`404`/`409` families |
| `SPEC-REPORTS` | Query, Detail, Write and Request Validation evidence families |
| `SPEC-DELIVERY` | patch-ZIP output and no direct target-project mutation |

## 5. Report contract

Schema version:

```text
springmaster.generated-slice-spec-fixture-gate-report.v1
```

The report contains:

* contract document, input path and input SHA-256;
* check status for every validation group;
* normalized API-surface evidence;
* DTO-boundary evidence;
* normalized error status families;
* required report families;
* patch-only delivery evidence;
* deterministic findings with path, expected value and actual value.

The committed golden report is:

```text
src/test/resources/tooling/generated-slice-spec-fixture-gate.business-partner.golden.json
```

## 6. Failure semantics

The gate is strict for its fixture contract. Representative finding families:

| Finding | Meaning |
|---|---|
| `SPEC-PARSE-*` | invalid or unsupported YAML input |
| `SPEC-TOPLEVEL-*` | missing, unexpected or invalid root contract field |
| `SPEC-PACKAGE-*` | Demo package reuse is not forbidden or is actively used |
| `SPEC-QUERY-*` | list/all/count contract is incomplete |
| `SPEC-DETAIL-*` | detail or alternate lookup contract is incomplete |
| `SPEC-WRITE-*` | create/update/delete contract is incomplete |
| `SPEC-DTO-*` | inbound DTO or validation metadata is inconsistent |
| `SPEC-ERROR-*` | global error contract or status family is incomplete |
| `SPEC-REPORTS-*` | required evidence family is not declared |
| `SPEC-DELIVERY-*` | delivery is not patch-only or bypasses target verification |

Negative tests prove fail-closed behavior for missing top-level fields, Demo
package reuse, delete request bodies, missing `409 CONFLICT` mapping and
unsupported YAML flow syntax.

## 7. Boundary to later generator phases

This gate validates the input fixture only. It deliberately does not provide:

* a generator Intermediate Representation;
* a Java source renderer;
* a patch-blueprint renderer;
* a target-project apply action;
* ZBM-specific assumptions.

The next generator phase may consume only a Slice-Spec that passes this gate.
Patch `000124_springmaster_patch_artifact_preflight_hardening` closes the separate P0 delivery-process boundary. The next generator phase is `000125_springmaster_generated_slice_intermediate_representation`.

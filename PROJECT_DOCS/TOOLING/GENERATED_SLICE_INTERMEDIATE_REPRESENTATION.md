# Generated Slice Intermediate Representation

**Patch:** `000125_springmaster_generated_slice_intermediate_representation`
**Status:** executable candidate contract
**Input:** validated `GeneratedServiceSlice` contract version `1`
**Output schema:** `springmaster.generated-service-slice-ir.v1`

## 1. Purpose

The Generated Slice Intermediate Representation (IR) is the deterministic,
domain-neutral boundary between the human-reviewed Slice-Spec YAML and later
generator renderers.

```text
GeneratedServiceSlice YAML
  -> strict YAML subset parser
  -> generic contract-v1 validation
  -> normalized Generated Slice IR
  -> later patch-blueprint dry-run
```

The IR is generator input. It is not Java source, a target-project file tree, a
patch archive or permission to mutate a target project.

## 2. Neutrality rules

The IR must remain reusable for different domains and resources.

Binding rules:

* active packages must not use a forbidden package prefix;
* `de.cocondo.platform.demo` remains an explicit forbidden prefix;
* no CatalogItem class, route or package is inferred by the transformer;
* the resource, DTO names, API path and business keys come only from the input
  Slice-Spec;
* Spec provenance metadata is not promoted into generator semantics;
* a synthetic `masterdata.supplier` test proves that the transformer is not
  locked to the BusinessPartner golden fixture;
* ZBM-specific packages, paths and business semantics are not part of the IR.

The BusinessPartner YAML remains the committed golden input, not a hard-coded
renderer template.

## 3. Canonical top-level sections

The JSON property order is part of the deterministic golden contract:

```text
schemaVersion
source
metadata
packages
resource
query
detail
write
model
validation
errorContract
reports
delivery
```

| Section | Purpose |
|---|---|
| `source` | input contract, path, raw-byte SHA-256, version, kind and slice id |
| `metadata` | candidate status and owner; no generator-specific source assumptions |
| `packages` | active package boundaries and forbidden prefixes |
| `resource` | domain, resource identity, display field, external id and business keys |
| `query` | shared filters, sorting, pagination and list/all/count operations |
| `detail` | detail-by-id and unique alternate lookup operations |
| `write` | create, update and bodyless delete operations |
| `model` | entity name, DTO names and normalized field capabilities/constraints |
| `validation` | inbound DTO and Bean Validation/OpenAPI alignment rules |
| `errorContract` | global Core error response and normalized status mappings |
| `reports` | required Query, Detail, Write and Validation evidence families |
| `delivery` | patch-ZIP-only target delivery and verification duties |

## 4. Normalization rules

### 4.1 Paths and operations

Every operation contains:

* a stable operation `key`;
* HTTP method;
* relative path from the Slice-Spec;
* absolute path derived from `apiSurface.basePath`;
* response shape;
* request DTO and success status where applicable.

List, `/all` and `/count` consume one shared query model. The operation-level
`inherits` array makes filter, sorting and pagination parity explicit without
copying those settings into multiple divergent structures.

### 4.2 Fields and DTOs

Slice-Spec field flags are normalized into:

```json
{
  "required": {
    "create": true,
    "update": false
  },
  "constraints": {
    "maxLength": 64
  },
  "capabilities": {
    "filterable": true,
    "sortable": true,
    "businessKey": true
  }
}
```

CreateDTO and UpdateDTO remain distinct and neither may equal the domain entity
name.

### 4.3 Error and evidence families

HTTP status mappings are sorted numerically. The canonical `400`, `404` and
`409` families and all required error types are preserved. All four report
families remain explicit and required.

## 5. Determinism

The tool uses only Python standard-library functionality and the strict parser
from the executable Slice-Spec fixture gate.

The output has:

* no timestamp;
* no environment-dependent absolute path for repository-local inputs;
* stable property and sequence ordering;
* exactly one final newline;
* a raw input-Spec SHA-256;
* byte-identical output for repeated runs against identical input.

Default invocation:

```bash
./bin/generated-slice-ir.sh
```

Deterministic test invocation:

```bash
./bin/generated-slice-ir.sh \
  --spec PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml \
  --out target/generated-slice-ir.business-partner.json
```

Committed golden IR:

```text
src/test/resources/tooling/generated-slice-ir.business-partner.golden.json
```

## 6. Fail-closed invariants

The transformer rejects the input without writing an IR file when:

* the strict YAML subset cannot be parsed;
* contract-v1 sections are missing or reordered;
* active packages use a forbidden prefix;
* list/all/count, detail, lookup or write operations are incomplete;
* filter or sort keys do not reference fields with matching capabilities;
* alternate lookups do not match unique business keys;
* CreateDTO and UpdateDTO collapse into one type or use the entity;
* the global error/status family is incomplete;
* evidence reports are not all required;
* delivery allows direct target mutation.

## 7. Boundary to `000126`

Patch `000125` creates no target-project paths and no patch ZIP for a generated
slice. The next phase may consume only the canonical IR and must remain a
non-mutating dry-run:

```text
000126_springmaster_generated_slice_patch_blueprint_dry_run
```

That patch must derive expected files, scopes, tests and reports from the IR,
without reading CatalogItem implementation packages and without writing to a
target repository.

## 8. Blueprint consumer after `000126`

Patch `000126_springmaster_generated_slice_patch_blueprint_dry_run` is the first
consumer of `springmaster.generated-service-slice-ir.v1`.

It reads only the canonical IR JSON and projects target-neutral path templates,
planned artifacts, API operations, tests, report gates and delivery blockers.
It does not reopen Slice-Spec YAML, infer patterns from Demo sources, render
source files or create a patch archive.

The committed boundary is documented in:

```text
PROJECT_DOCS/TOOLING/GENERATED_SLICE_PATCH_BLUEPRINT_DRY_RUN.md
```

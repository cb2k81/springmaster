# Generated Slice Patch Blueprint Dry-run

**Patch:** `000126_springmaster_generated_slice_patch_blueprint_dry_run`
**Status:** executable planning contract
**Input schema:** `springmaster.generated-service-slice-ir.v1`
**Output schema:** `springmaster.generated-service-slice-patch-blueprint.v1`

## 1. Purpose

The Patch Blueprint Dry-run is the deterministic planning boundary between the
canonical Generated Slice IR and a later target-bound renderer.

```text
Generated Slice IR
  -> canonical IR validation
  -> target-neutral package/path projection
  -> planned artifacts, API operations, tests, reports and delivery gates
  -> JSON blueprint only
```

Patch `000126` does not render Java source, create `manifest.json`, create a
patch ZIP, inspect a target repository or mutate target files. The word
"patch" in this phase describes the future archive plan, not an archive that
already exists.

## 2. Input boundary

The tool consumes only canonical IR JSON:

```text
src/test/resources/tooling/generated-slice-ir.business-partner.golden.json
```

Binding rules:

* no Slice-Spec YAML is read;
* no CatalogItem or Demo implementation file is read;
* the IR schema must be exactly
  `springmaster.generated-service-slice-ir.v1`;
* the complete canonical IR section order is required;
* the IR validator from `bin/generated-slice-ir.py` remains authoritative;
* all four report families and the patch-only delivery boundary remain
  mandatory.

The default command is:

```bash
./bin/generated-slice-patch-blueprint.sh
```

A deterministic explicit invocation is:

```bash
./bin/generated-slice-patch-blueprint.sh \
  --ir src/test/resources/tooling/generated-slice-ir.business-partner.golden.json \
  --out target/generated-slice-patch-blueprint.business-partner.json
```

## 3. Canonical blueprint sections

The JSON property order is part of the golden contract:

```text
schemaVersion
source
projection
patch
artifacts
apiOperations
tests
reports
delivery
blockers
summary
```

| Section | Contract |
|---|---|
| `source` | IR path, raw-byte SHA-256, IR/spec provenance and Slice ID |
| `projection` | target-neutral package suffix and unresolved target bindings |
| `patch` | root scope, archive layout, target-live baseline policy and dry-run-only state |
| `artifacts` | planned Java, test, evidence and changelog paths; no rendered bytes |
| `apiOperations` | normalized list/all/count/detail/lookup/create/update/delete plan |
| `tests` | source-test duties, report gates and target delivery gates |
| `reports` | all four required executable API contract families |
| `delivery` | explicit no-mutation/no-render/no-ZIP boundary for `000126` |
| `blockers` | unresolved target, persistence, security and authorization decisions |
| `summary` | deterministic counts and zero-mutation evidence |

## 4. Target-neutral projection

The IR module package is split into:

```text
IR base package:       de.cocondo.platform
IR module package:     de.cocondo.platform.administration.businesspartner
module suffix:         administration.businesspartner
module path suffix:    administration/businesspartner
```

The blueprint does not copy the Springmaster base package to a target project.
It emits templates instead:

```text
${targetBasePackage}.administration.businesspartner
${targetBasePackagePath}/administration/businesspartner
```

Required target bindings are explicit:

* `targetProjectKey`;
* `targetBasePackage`;
* `targetBasePackagePath`;
* `targetPatchId`;
* `targetBaselineHead`;
* `targetBaselineSha256ByPath`.

These values must come from a current target baseline and the target project's
local configuration. Springmaster does not hard-code project-local scopes or
paths.

## 5. Planned artifact surface

For the BusinessPartner golden IR, the candidate blueprint plans:

```text
9 Java sources
4 Java tests
1 generated-slice evidence document
1 target patch changelog
```

The source categories are:

* REST Controller;
* Application Service;
* Domain model;
* Read, ListItem, Create and Update DTOs;
* Mapper;
* Service-boundary Validator.

The test categories are:

* Controller API/error contract;
* Application service behavior;
* DTO/domain mapping;
* Boundary and business validation.

Every artifact has state `planned-not-rendered`. Paths must be unique, safe,
repository-relative templates and free of active Demo/CatalogItem projections.

## 6. API, reports and delivery gates

The blueprint preserves the eight management operations from the IR:

```text
list
all
count
byId
alternate lookup
create
update
delete
```

It also requires:

* Query Contract Report;
* Detail/Lookup Contract Report;
* Write API Contract Report;
* Request Validation/OpenAPI Gate Report;
* target artifact preflight;
* target patch dry-run;
* explicit authorization before apply;
* targeted tests and full Maven test;
* `git diff --check`;
* target Full-ZIP export and export-integrity check.

## 7. Intentional blockers

IR version 1 does not contain enough information to render a deployable target
slice safely. The blueprint therefore blocks later rendering until the pilot
resolves:

| Blocker | Reason |
|---|---|
| Target baseline | target HEAD and raw-byte preconditions are unknown |
| Target package | project-specific base package is unknown |
| Persistence | IR v1 has no candidate-store or durable persistence contract |
| Security | IR v1 has no deferred/implemented security contract |
| Apply authorization | user approval is required after target dry-run and tests |

No default persistence or security implementation is inferred. This avoids
turning missing semantics into hidden technical debt.

## 8. Determinism and fail-closed behavior

The output contains no timestamp and has exactly one final newline. Repeated
runs against byte-identical IR must produce byte-identical blueprint bytes.

The tool fails without writing the output when:

* the IR is invalid JSON;
* the IR schema is unsupported;
* canonical IR sections are missing or reordered;
* the module package is not below the IR base package;
* a report family is not required;
* direct target mutation is permitted;
* planned artifact paths collide or are unsafe;
* source rendering or patch archive generation is enabled in phase `000126`.

## 9. Golden and neutrality evidence

Committed golden blueprint:

```text
src/test/resources/tooling/generated-slice-patch-blueprint.business-partner.golden.json
```

The tests additionally project a synthetic Supplier IR. This proves that
resource names, DTO names, routes and module paths come from the IR rather than
BusinessPartner or CatalogItem implementation assumptions.

The test suite also compares Git status before and after blueprint generation.
Only the explicitly selected ignored output path may be written; target source,
test, documentation and patch trees remain untouched.

## 10. Boundary to `000127`

Patch `000126` closes blueprint planning, not target delivery. The next phase
is:

```text
000127_springmaster_zbm_generated_slice_pilot_plan
```

That phase may define the ZBM target inputs, package binding, persistence and
security decision points, target-local patch scope and acceptance gates. It may
not apply a ZBM patch without a current ZBM baseline and explicit user
instruction.

## 11. ZBM pilot boundary after `000127`

Patch `000127_springmaster_zbm_generated_slice_pilot_plan` resolves the planning
questions around the first target-bound pilot without weakening the blockers in
this blueprint.

The ZBM plan requires:

* a current and integritätsgeprüft ZBM Full-ZIP baseline;
* forensic architecture, API, persistence, security and scope qualification;
* a reviewed pilot-aggregate decision;
* a complete target-binding record;
* a generic renderer and patch assembler qualified before target delivery;
* target-local artifact preflight, dry-run and isolated tests;
* explicit user authorization before any live apply.

The Springmaster descriptor currently permits only the `tooling` Platform-Update
profile. The plan neither expands that allow-list nor authorizes `target-apply`.
The BusinessPartner blueprint remains reference evidence and is not an automatic
ZBM domain decision.

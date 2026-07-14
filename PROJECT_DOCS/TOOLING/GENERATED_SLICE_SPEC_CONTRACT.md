# Generated Slice Spec Contract

**Patch:** `000122_springmaster_generated_slice_spec_contract`
**Status:** executable contract, fixture-gate-backed since `000123`
**Reference maturity:** follows `000121_springmaster_generated_slice_api_pattern_adoption_plan`

## 1. Purpose

This document defines the **Generated Slice Spec Contract** used by Springmaster to describe a future generated service slice before generator code creates files or target-project patch archives.

The contract turns the API pattern maturity from Query, Detail/Lookup, Write, Request Validation/OpenAPI and the global Error Contract into an explicit, reviewable Slice-Spec model.

The Slice-Spec is not a target-project patch and not generated Java code. It is the authoritative input contract for later generator phases.

## 2. Contract boundary

A Generated Slice Spec describes one management-style resource slice.

It defines:

* resource identity and package naming;
* API path and operation families;
* DTO shapes and validation rules;
* query/filter/sort/pagination semantics;
* detail and alternate-key lookup semantics;
* write semantics for create, update and delete;
* global error contract usage;
* OpenAPI and report evidence expectations;
* patch-generation boundaries.

It must not define:

* concrete target-project apply actions;
* direct file mutation in target projects;
* Springmaster Demo package reuse;
* domain-specific business logic hidden inside generic templates;
* bulk, state or relationship commands unless explicitly marked as a later extension family.

## 3. Minimum YAML structure

The canonical exchange format is YAML. A JSON representation may be derived mechanically from the same structure, but YAML is the human-review format.

```yaml
specVersion: 1
kind: GeneratedServiceSlice
metadata:
  sliceId: administration.business-partner
  status: candidate-reference-slice
  owner: springmaster
  sourceReference: catalogitem-pattern-family

packageModel:
  basePackage: de.cocondo.platform
  modulePackage: de.cocondo.platform.administration.businesspartner
  corePackage: de.cocondo.system
  forbiddenPackagePrefixes:
    - de.cocondo.platform.demo

resource:
  domain: administration
  resourceName: businessPartner
  collectionName: businessPartners
  externalId:
    field: id
    type: string
  displayField: name
  businessKeys:
    - name: code
      field: code
      unique: true
      lookupPath: /by-code/{code}

apiSurface:
  basePath: /api/administration/business-partners
  query:
    list:
      enabled: true
      method: GET
      path: ""
      pagination: offset
      sorting:
        allowlist:
          - code
          - name
        default:
          sortBy: code
          sortDir: asc
      filters:
        - code
        - name
    all:
      enabled: true
      method: GET
      path: /all
    count:
      enabled: true
      method: GET
      path: /count
  detail:
    enabled: true
    method: GET
    path: /{id}
  alternateLookups:
    - name: byCode
      method: GET
      path: /by-code/{code}
      unique: true
  write:
    create:
      enabled: true
      method: POST
      path: ""
      successStatus: 201
      locationHeader: detail
    update:
      enabled: true
      method: PUT
      path: /{id}
      successStatus: 200
    delete:
      enabled: true
      method: DELETE
      path: /{id}
      successStatus: 204
      requestBody: forbidden

model:
  entity:
    name: BusinessPartner
  dto:
    read: BusinessPartnerDTO
    listItem: BusinessPartnerListItemDTO
    create: BusinessPartnerCreateDTO
    update: BusinessPartnerUpdateDTO
  fields:
    - name: code
      type: string
      requiredOnCreate: true
      requiredOnUpdate: false
      maxLength: 64
      filterable: true
      sortable: true
      businessKey: true
    - name: name
      type: string
      requiredOnCreate: true
      requiredOnUpdate: true
      maxLength: 255
      filterable: true
      sortable: true
    - name: description
      type: string
      requiredOnCreate: false
      requiredOnUpdate: false
      maxLength: 1000
      filterable: false
      sortable: false

validation:
  requestBodiesRequireValidAnnotation: true
  entitiesAsRequestBody: forbidden
  beanValidationToOpenApiRequiredAlignment: required
  invalidRequestErrorType: VALIDATION_FAILED

errorContract:
  handler: global-core
  responseType: ApiErrorResponse
  requiredErrorTypes:
    - VALIDATION_FAILED
    - INVALID_REQUEST
    - RESOURCE_NOT_FOUND
    - CONFLICT
    - INTERNAL_ERROR
  expectedStatusMappings:
    - status: 400
      errorTypes:
        - VALIDATION_FAILED
        - INVALID_REQUEST
    - status: 404
      errorTypes:
        - RESOURCE_NOT_FOUND
    - status: 409
      errorTypes:
        - CONFLICT

reports:
  queryContract: required
  detailLookupContract: required
  writeApiContract: required
  requestValidationOpenApiGate: required

delivery:
  outputMode: patch-zip
  targetApply: forbidden-in-springmaster
  targetPatchDryRun: required-before-apply
  targetMavenTest: required-after-apply
  targetFullExport: required-after-apply
```

## 4. Required top-level fields

| Field | Required | Meaning |
|---|---:|---|
| `specVersion` | yes | Contract version. Current value: `1`. |
| `kind` | yes | Must be `GeneratedServiceSlice`. |
| `metadata` | yes | Review and maturity metadata. |
| `packageModel` | yes | Java package boundaries and forbidden package prefixes. |
| `resource` | yes | Domain/resource identity and keys. |
| `apiSurface` | yes | Enabled operation families and paths. |
| `model` | yes | Entity/DTO/field model. |
| `validation` | yes | DTO boundary and request validation rules. |
| `errorContract` | yes | Required global error contract integration. |
| `reports` | yes | Required report-only evidence families. |
| `delivery` | yes | Patch-output and target-project delivery boundaries. |

## 5. API surface rules

A management-style Generated Slice has the following baseline API surface unless explicitly opted out with a documented reason:

```text
GET    /api/<domain>/<resources>
GET    /api/<domain>/<resources>/all
GET    /api/<domain>/<resources>/count
GET    /api/<domain>/<resources>/{id}
POST   /api/<domain>/<resources>
PUT    /api/<domain>/<resources>/{id}
DELETE /api/<domain>/<resources>/{id}
```

Rules:

* `query.list`, `query.all` and `query.count` must share the same business filters, permission predicates and data-scope predicates.
* `query.count` must not materialize rows only to count them.
* `detail` uses the opaque external id and returns `404 RESOURCE_NOT_FOUND` when missing.
* `alternateLookups` are optional and only allowed for unique alternate keys.
* `write.delete.requestBody` is `forbidden` for single-resource delete.
* `write.create.locationHeader` points to the `detail` endpoint.

## 6. DTO and validation rules

The Slice-Spec must make DTO boundaries explicit.

Required rules:

* Create and update request bodies use inbound DTOs, never entities.
* Request body controller parameters require `@Valid`.
* `requiredOnCreate` and `requiredOnUpdate` fields must map to Bean Validation constraints.
* Bean Validation required fields must align with OpenAPI `required` lists.
* `maxLength` must align with Bean Validation and OpenAPI schema constraints.
* Invalid DTO requests return the global `400 VALIDATION_FAILED` error response.
* `errorContract.expectedStatusMappings` makes the required `400`, `404` and `409` families machine-readable.

## 7. Error contract rules

Generated slices must use the global Core API Error Contract.

Required mappings:

| Case | HTTP status | errorType |
|---|---:|---|
| Bean Validation failure | `400` | `VALIDATION_FAILED` |
| Invalid query parameter | `400` | `INVALID_REQUEST` |
| Missing detail resource | `404` | `RESOURCE_NOT_FOUND` |
| Duplicate business key | `409` | `CONFLICT` |
| Unexpected internal failure | `500` | `INTERNAL_ERROR` |

A generated slice must not create local error response DTOs or controller-local error contracts.

Contract version `1` must explicitly declare the following status families in `errorContract.expectedStatusMappings`:

```text
400 -> VALIDATION_FAILED, INVALID_REQUEST
404 -> RESOURCE_NOT_FOUND
409 -> CONFLICT
```

## 8. Report evidence rules

The following report families are required for a candidate generated management slice:

```text
queryContract
 detailLookupContract
writeApiContract
requestValidationOpenApiGate
```

The concrete future generator may produce report fixtures or report inputs, but the Slice-Spec must declare that these evidence families are required.

## 9. Delivery rules

Generated Slice delivery is patch-based.

Allowed:

* generate a target-local patch ZIP;
* generate a target-local runner;
* generate evidence files and review reports;
* require target dry-run, apply, Maven test, diff check and full export.

Forbidden:

* direct target-project file mutation by Springmaster;
* copying `de.cocondo.platform.demo` packages into target projects;
* hiding package or API deviations in generator code;
* applying target patches without target-local patchsystem verification.

## 10. Candidate acceptance criteria

A Generated Slice Spec is acceptable when:

* all required top-level fields exist;
* operation-family opt-outs are explicit and justified;
* `/all` and `/count` are present for management slices or explicitly opted out;
* DTO required fields are explicit for create and update;
* the global error contract is selected and `400`/`404`/`409` status families are explicit;
* report evidence families are declared;
* delivery is patch-ZIP based;
* Demo packages are explicitly forbidden for target delivery.

## 11. Relationship to CatalogItem

CatalogItem remains the candidate reference for the current API pattern families.

It is not a template to copy. The generator must derive neutral artifacts from the Slice-Spec and reusable Core/Tooling contracts, not from `de.cocondo.platform.demo.catalog` package names.

## 12. Executable fixture gate since 000123

Patch `000123_springmaster_generated_slice_spec_fixture_gate` adds the strict executable contract evidence documented in:

```text
PROJECT_DOCS/TOOLING/GENERATED_SLICE_SPEC_FIXTURE_GATE.md
```

The gate parses the YAML fixture with a dependency-free strict YAML profile, validates all required API/DTO/Error/Report/Delivery families, writes a deterministic JSON report and fails with a non-zero exit code on findings.

## 13. Next step

The P0 process boundary is closed by `000124_springmaster_patch_artifact_preflight_hardening`. The next implementation step is:

```text
000125_springmaster_generated_slice_intermediate_representation
```

After P0 closure, the generator sequence continues with the neutral Intermediate Representation and the patch-blueprint dry-run.

## Artifact qualification after 000124

Any later generated-slice patch ZIP must pass `patch.sh artifact-preflight` against the committed source `HEAD`. `expectedBeforeSha256` values must come from raw repository bytes or the export metadata `fileManifest`, never from reconstructed text-export content.

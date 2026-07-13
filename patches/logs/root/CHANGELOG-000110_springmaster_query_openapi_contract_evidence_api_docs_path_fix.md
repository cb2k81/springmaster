# 000109a - springmaster_query_openapi_contract_evidence_api_docs_path_fix

## Scope

root

## Summary

Repairs the CatalogItem OpenAPI query-contract evidence introduced by `000109` by aligning the executable test and documentation with the Springmaster-local Springdoc endpoint `/api-docs`.

## Reason

The project configures:

```yaml
springdoc:
  api-docs:
    path: /api-docs
```

Therefore `/v3/api-docs` is not exposed in the current Springmaster runtime. The failing `CatalogItemOpenApiQueryContractTest` used the Springdoc default path and received HTTP 404.

## Verification

- manifest identity preflight
- live-baseline preflight against current working tree after `000109`
- patch dry-run
- patch apply
- patch show latest identity check
- query-contract report smoke run
- targeted Maven test `CatalogItemOpenApiQueryContractTest`
- targeted Maven test `SpringmasterQueryContractReportTest`
- full Maven test
- git diff --check
- full zip export

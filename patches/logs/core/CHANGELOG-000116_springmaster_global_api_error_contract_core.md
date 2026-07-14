# Changelog 000116_springmaster_global_api_error_contract_core

Scope: core

## Summary

Introduces the reusable System-Core runtime implementation of the Springmaster API error contract. CatalogItem migration is intentionally left to the follow-up demo-scope patch.

## Added

- `de.cocondo.system.http.ApiErrorResponse`
- `de.cocondo.system.http.ApiViolationDTO`
- `de.cocondo.system.http.ApiErrorType`
- `de.cocondo.system.http.ApiErrorIdGenerator`
- `de.cocondo.system.http.GlobalApiExceptionHandler`
- `de.cocondo.system.exception.ResourceNotFoundException`
- `PROJECT_DOCS/CORE/CORE_GLOBAL_API_ERROR_CONTRACT.md`
- Targeted tests for Core error DTOs, error ID generation, global handler behavior and ResourceNotFoundException.

## Changed

- EntityAlreadyExistsException now carries a stable default message key.
- Demo and API documentation now identify the Core-owned error DTOs as the active reference.
- Platform version state advances to `000116_springmaster_global_api_error_contract_core`.

## Verification

Required runner verification:

```text
ApiErrorResponseTest
ApiErrorIdGeneratorTest
GlobalApiExceptionHandlerTest
CoreExceptionTypesTest
CatalogItemOpenApiQueryContractTest
SpringmasterQueryContractReportTest
full mvn test
git diff --check
full zip export
```

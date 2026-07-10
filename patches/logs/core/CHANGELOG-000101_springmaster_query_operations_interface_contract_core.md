# 000101_springmaster_query_operations_interface_contract_core

Scope: core

## Summary

Introduces fachfreie Core interfaces for canonical query operations.

## Changes

- Added `PagedResultSetQuery`.
- Added `CompleteResultSetQuery`.
- Added `CountResultSetQuery`.
- Added `ResultSetQueryOperations` composite interface.
- Added contract tests for typed paged/all/count operations.
- Documented the architecture boundary: no generic Spring MVC controller interfaces in Core.
- Increased `PLATFORM_CORE_VERSION` to `0.3.5` and `PLATFORM_VERSION` to `0.13.49-foundation`.

## Verification

- targeted Maven test: `ResultSetQueryOperationsTest`
- full Maven test
- full zip export

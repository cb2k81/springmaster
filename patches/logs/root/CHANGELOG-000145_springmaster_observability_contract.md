# CHANGELOG 000145_springmaster_observability_contract

## Purpose

Accept ADR-0010, implement HTTP correlation and close the P1 runtime-contract foundation.

## Changes

- Accept observability and error trace strategy ADR
- Add reusable validated HTTP correlation and MDC lifecycle
- Harden Actuator and default error endpoint exposure
- Add observability contract tooling and HTTP tests
- Close P1 with synchronized foundation, Core, Tooling and Template versions

## Qualification

The patch acceptance profile runs a complete Maven test and no export or push.
Bundle-level checks additionally run the relevant contract integration fixtures and Project-New acceptance.

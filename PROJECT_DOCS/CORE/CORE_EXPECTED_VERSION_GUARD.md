---
documentId: CORE-EXPECTED-VERSION-GUARD-001
title: Core Expected Version Guard
documentType: architecture-concept
status: active
authority: normative
scopeLevel: platform
scopePaths:
  - springmaster/standards
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-23
validFrom: 2026-08-23
lastReviewedAt: 2026-08-23
reviewBy: 2026-11-23
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-004
---

# Core Expected Version Guard

## Status and purpose

`ExpectedVersionGuard` is the framework-free comparison primitive for body-bound optimistic-lock tokens. It validates one resource identity and one expected/actual version pair without repository, JPA, HTTP, Spring DAO or domain dependencies.

## Runtime contract

`requireMatch(resourceType, resourceId, actualVersion, expectedVersion)` applies these rules:

- blank resource type or ID is an invalid request and raises `IllegalArgumentException`;
- a missing or negative expected version is an invalid request and raises `IllegalArgumentException`;
- a missing actual version or mismatch raises `ExpectedVersionConflictException`;
- a match returns normally.

The client-facing conflict message is generic and does not expose resource identifiers or actual/expected numeric values. The global API adapter maps `ExpectedVersionConflictException` to HTTP `409` and `ApiErrorType.CONFLICT`. This mapping is independent from `If-Match` responses `412` and `428`.

An `EXPECTED_VERSION_SET` remains application-owned orchestration of multiple calls to this single-pair primitive. The Core does not provide a multi-aggregate coordinator, lock manager or retry runtime.

## Verification

`ExpectedVersionGuardTest` covers matching, missing actual, mismatch, missing/negative expected version and blank identity. `GlobalApiExceptionHandlerTest` proves the canonical 409 envelope.

## Version impact

This additive public Core capability has minor impact on `PLATFORM_CORE_VERSION` and the aggregate foundation version. Canonical version truth remains deferred to Trusted-Host Sprint-004 closure.

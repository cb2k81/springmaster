---
documentId: CORE-BUSINESS-DATE-BOUNDARY-001
title: Core Business Date Boundary
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

# Core Business Date Boundary

## Status and purpose

`BusinessDateProvider` is the framework-free Core boundary for application use cases that require a controlled business date. It separates business-date decisions from audit timestamps and uncontrolled system time.

## Runtime contract

```text
BusinessDateProvider.currentDate() -> LocalDate
ClockBusinessDateProvider(Clock) -> non-null Clock required
ClockBusinessDateProvider.currentDate() == LocalDate.now(injectedClock)
```

The adapter has only `java.time` dependencies. It has no Spring annotation, persistence coupling, domain calendar rules, holiday logic or implicit default clock. Applications own construction and injection of the appropriate `Clock` and provider.

## Verification and scope

`ClockBusinessDateProviderTest` uses fixed instants and explicit zones to prove deterministic date derivation and null rejection. This boundary does not create a temporal framework or define effective-dating storage semantics.

## Version impact

This additive public Core capability has minor impact on `PLATFORM_CORE_VERSION` and the aggregate foundation version. Canonical version truth remains deferred to Trusted-Host Sprint-004 closure.

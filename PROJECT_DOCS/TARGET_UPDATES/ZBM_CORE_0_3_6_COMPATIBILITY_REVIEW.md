# ZBM Core 0.3.6 Compatibility Review

## 1. Decision

The committed ZBM baseline after `000014_zbm_tooling_cutover_version_truth_closure` is compatible with the Springmaster System Core `0.3.6`.

Springmaster may enable the existing target-bound profile `core` for `zbm`. This decision authorizes generation, producer preflight, target dry-run and isolated sandbox qualification only. A live ZBM apply remains a separate, explicit user decision after a green sandbox closure.

## 2. Authoritative baselines

| Project | Git HEAD | Latest patch | Relevant version | Dirty |
|---|---|---|---|---:|
| Springmaster | `c99205e5f61736db6ca0eee5e9ed90cfb77760ee` | `000130_springmaster_tooling_cutover_delivery_guard` | Core `0.3.6` | no |
| ZBM | `92789c65e197b8ca1294552a9e065d5a0d609aeb` | `000014_zbm_tooling_cutover_version_truth_closure` | Core `0.3.2` | no |

Both supplied full exports use export format v2, expose clean Git evidence and contain raw-byte manifests whose file entries match the reconstructed repository bytes. VM wall-clock timestamps are not used as a compatibility or ordering authority.

## 3. Exact Core delta

The comparison under `de.cocondo.system` yields:

| Area | New | Modified | Deleted |
|---|---:|---:|---:|
| Production Core | 11 | 2 | 0 |
| Core tests | 5 | 3 | 0 |

Production changes:

```text
src/main/java/de/cocondo/system/dto/CountResponseDTO.java
src/main/java/de/cocondo/system/exception/EntityAlreadyExistsException.java
src/main/java/de/cocondo/system/exception/ResourceNotFoundException.java
src/main/java/de/cocondo/system/http/ApiErrorIdGenerator.java
src/main/java/de/cocondo/system/http/ApiErrorResponse.java
src/main/java/de/cocondo/system/http/ApiErrorType.java
src/main/java/de/cocondo/system/http/ApiViolationDTO.java
src/main/java/de/cocondo/system/http/GlobalApiExceptionHandler.java
src/main/java/de/cocondo/system/list/PagedQuerySupport.java
src/main/java/de/cocondo/system/query/CompleteResultSetQuery.java
src/main/java/de/cocondo/system/query/CountResultSetQuery.java
src/main/java/de/cocondo/system/query/PagedResultSetQuery.java
src/main/java/de/cocondo/system/query/ResultSetQueryOperations.java
```

A dry generation against the reconstructed ZBM baseline produced 23 effective patch operations: 13 production-Core paths, eight Core-test paths, one target-local Core update report and one Core changelog. No `pom.xml` operation was necessary.

## 4. API and source compatibility

### `EntityAlreadyExistsException`

The existing one-argument constructor remains available. The message-key constructor and getter are additive. Existing ZBM source and tests remain source-compatible.

### `PagedQuerySupport`

The existing paging and sort-direction methods remain available. The sort-direction parser additionally trims surrounding whitespace. Allowlist resolution, stable Spring Data sorting and stable in-memory comparators are additive.

### New Core contracts

`CountResponseDTO`, the typed query-operation interfaces and the global API-error types are new contracts. They do not replace an existing ZBM type.

### ZBM usage

Current ZBM fachlicher code imports only `de.cocondo.system.entity.DomainEntity`. It does not use the changed exception, paging, query or HTTP-error types. No ZBM fachlicher source migration is required for the Kernel cutover.

## 5. Runtime compatibility

`ZbmApplication` already scans both:

```java
@SpringBootApplication(scanBasePackages = {
        "de.cocondo.zbm",
        "de.cocondo.system"
})
```

The new `ApiErrorIdGenerator` and `GlobalApiExceptionHandler` therefore become active Core components. ZBM has no competing `@ControllerAdvice`; the activation is intentional and establishes the Springmaster global API-error envelope before fachliche REST endpoints are added.

The Core defaults currently use stable `springmaster.*` message-key values. Fachliche exceptions may supply project-specific keys through the explicit constructors. Any future change of the common default namespace is a Springmaster Core decision and must not be implemented as a ZBM-local fork.

## 6. Dependency compatibility

The committed ZBM POM already provides the compile and test dependencies used by Core `0.3.6`:

```text
spring-boot-starter-web
jakarta.persistence-api
jakarta.validation-api
spring-data-commons
spring-boot-starter-test
```

The existing Platform-Update Core dependency synthesizer therefore produces no `pom.xml` delta. The Springmaster master POM must not be copied into ZBM.

A real Bean Validation provider is still absent. This remains an explicit AP6 Persistence/Validation blocker, but it does not prevent compilation, context startup or the isolated Core `0.3.6` cutover tests. The Kernel cutover must not claim Validation Runtime maturity.

## 7. Architecture boundary

The `core` profile is restricted to:

```text
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
PROJECT_DOCS/CORE/PLATFORM_UPDATES/<target-patch-id>.md
patches/logs/core/CHANGELOG-<target-patch-id>.md
```

It must not contain:

```text
src/main/java/de/cocondo/zbm/**
src/test/java/de/cocondo/zbm/**
src/main/java/de/cocondo/platform/**
PROJECT_DOCS/DEMO/**
PROJECT_DOCS/TOOLING/**
Liquibase changes
Security configuration
```

## 8. Delivery decision

The ZBM descriptor is extended only from:

```env
TARGET_ALLOWED_PROFILES=tooling-cutover
```

to:

```env
TARGET_ALLOWED_PROFILES=tooling-cutover,core
```

No Generated-Slice, domain, defaults or broad root profile is authorized.

The next target patch is expected to be:

```text
000015_springmaster_platform_update_core_for_zbm
```

The existing `core` profile intentionally does not alter target-local version metadata. After a successful Core live apply, Gate G3 remains open until a separate ZBM version-truth closure records `PLATFORM_CORE_VERSION=0.3.6`.

## 9. Mandatory qualification

Before any live Core apply:

1. generate the target-bound Core patch from the committed Springmaster baseline;
2. run Producer Artifact Preflight;
3. repeat the live ZBM dry-run;
4. apply only in an isolated Git clone/worktree;
5. run Core-targeted tests;
6. run ZBM Domain regression tests;
7. run the complete Maven test suite;
8. verify the global API-error Spring context;
9. verify exact changed-path parity;
10. create and verify exactly one ZBM Full-v2 closure export;
11. prove that the live ZBM repository remained unchanged.

## 10. Stop conditions

Stop without live mutation if:

- either repository is dirty or has an unexpected HEAD/Latest Patch;
- the generated patch contains `pom.xml` or ZBM fachlicher paths without a new review;
- any baseline hash is incomplete or differs from the live target;
- Core-targeted, Domain, Full Maven, Spring context, export or evidence gates fail;
- the generated profile is not exactly `core`;
- more than one target export is produced.

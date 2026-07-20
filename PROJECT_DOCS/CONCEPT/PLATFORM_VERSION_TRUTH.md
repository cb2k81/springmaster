---
documentType: concept
status: active
scope: platform-versioning
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Platform Version Truth

## Canonical source

`platform/versions/platform.env` is the canonical source for the Springmaster foundation and component versions.

The Maven project version is the build artifact coordinate. During development it must equal `PLATFORM_VERSION` plus `-SNAPSHOT`. A contract test rejects drift.

## Runtime projection

Maven packages the unchanged canonical file as:

```text
META-INF/springmaster/platform.env
```

`PlatformVersionProperties` loads that classpath resource. The platform API and the Actuator info contributor project the same values; neither keeps a fallback version constant.

## Documentation rule

Living documentation references the canonical file instead of copying the current numeric version. Historical patch changelogs may retain the version that was true when they were written.

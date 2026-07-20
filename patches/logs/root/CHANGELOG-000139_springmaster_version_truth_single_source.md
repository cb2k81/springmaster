# 000139 – Springmaster version truth single source

## Scope

- package `platform/versions/platform.env` unchanged as a runtime classpath resource;
- remove the bootstrap fallback version from application configuration and controller code;
- project all component versions through the platform API and Actuator info;
- align the Maven snapshot coordinate with the canonical foundation version;
- add tests that reject runtime-resource and Maven-version drift;
- replace the obsolete bootstrap README status.

## Validation

```bash
mvn -q -Dtest=PlatformVersionPropertiesTest,SpringmasterApplicationTests test
mvn -q test
```

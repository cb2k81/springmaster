# springmaster

`springmaster` is the Cocondo Java/Spring Boot platform source project.

It has three roles:

1. **Tooling Source** for patch, export, build and database tooling.
2. **Platform Core** for shared Java backend building blocks.
3. **Demo Application** for validating the reusable core in executable examples.

## Bootstrap status

This repository state is the project foundation only. It provides:

- a minimal Spring Boot application under `de.cocondo.platform.app`,
- manifest-based patch tooling,
- a conservative export tool,
- basic build and DBTool entry points,
- platform/version and target-registry folders,
- initial project documentation placeholders.

The IDM-derived full tooling baseline, Java core and demo domains are added in later, regular patches.

## First local commands

```bash
cp .env.example .env
./bin/patch.sh list
./bin/export.sh full --zip
./bin/dbtool.sh status
mvn test
```
## Reference Project and Standards Strategy

Since `000043_springmaster_reference_project_and_standards_strategy`, Springmaster is explicitly responsible for reusable backend standards and conventions in addition to tooling, Core code and reference implementations.

Existing projects are not supplied first. The next validation target is the clean-room `Catalog-demo` reference project with `CatalogItem` as the first pattern object.

See:

```text
PROJECT_DOCS/CONCEPT/SPRINGMASTER_REFERENCE_PROJECT_AND_STANDARDS_STRATEGY.md
PROJECT_DOCS/STANDARDS/README.md
PROJECT_DOCS/STANDARDS/API/README.md
```


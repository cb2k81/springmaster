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

# springmaster

`springmaster` is the Cocondo Java/Spring Boot platform source project.

It provides four connected capabilities:

1. **Tooling Source** for patch, export, build, DBTool, project-new, gates and platform updates.
2. **Platform Core** for reusable Java backend building blocks under `de.cocondo.system`.
3. **Reference Application** for executable API and architecture patterns.
4. **Standards Source** for contracts, decisions and managed-project delivery.

## Current maturity

The repository is an advanced foundation with controlled tooling and Core delivery pilots. Candidate reference slices, deferred security, report-only gates and target-delivery restrictions remain explicit until their evidence is complete.

The canonical foundation and component versions are stored only in:

```text
platform/versions/platform.env
```

Runtime `/api/platform/info`, Actuator `/actuator/info` and the Maven artifact version are checked against that contract.

## First local commands

```bash
cd /opt/cocondo/springmaster || exit 1
cp .env.example .env
./bin/patch.sh list
./bin/export.sh full --zip
./bin/dbtool.sh status
mvn test
```

Repository-wide working rules are defined in `AGENTS.md`. The active documentation inventory starts at `PROJECT_DOCS/index.md`.

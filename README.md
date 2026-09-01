# springmaster

## Leitprinzip: Standardisieren, unterstützen, nicht blockieren

Springmaster standardisiert wiederkehrende Architektur-, Governance-, Qualitäts- und Delivery-Entscheidungen, damit Fachprojekte **weniger** projektspezifische Komplexität tragen müssen. Standards und Tools sollen sichere Wege vereinfachen, nicht funktionierende Projektentwicklung durch vermeidbare Prozesskopplung blockieren.

Dazu trennt Springmaster harte Safety-/Trust-Boundary-Regeln von bevorzugten Tool- und Prozesspfaden. Defektes Tooling besitzt einen kontrollierten Recovery-Weg; Qualification ist risikobasiert und progressiv; das Patchsystem bleibt ein Delivery-/Acceptance-Mechanismus und ist nicht automatisch der normale lokale Development Hot Path. Die dauerhafte Entscheidung steht in `PROJECT_DOCS/ADR/ADR-0020-enabling-governance-and-recoverable-tooling.md`.


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

## Managed target lifecycle

Springmaster validates target updates through declarative profile rules, an explicit compatibility matrix and atomic managed-state evidence. The P2 pilot proves tooling and Core upgrades on a disposable second target; real target mutation remains descriptor-bound and explicitly authorized.

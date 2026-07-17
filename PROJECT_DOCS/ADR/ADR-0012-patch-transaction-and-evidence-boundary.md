# ADR-0012: Patch Transaction and Evidence Boundary

## Status

Accepted

## Context

Springmaster besitzt starke Patchartefakt- und Sandboxprüfungen. Patchidentität, Acceptance-Evidence, Exporte und operative Logs dürfen dennoch nicht zu einer zweiten Produktwahrheit oder obligatorischen Kette für jede Änderung werden.

## Decision

1. Das Patchsystem ist ein Transaktionsmechanismus; Git bleibt die dauerhafte Repositoryhistorie.
2. Neue Patchartefakte führen zusätzlich zur lokalen `patchId` eine eindeutige, sequenzunabhängige `artifactId`.
3. Die lokale numerische `patchId` dient nur der Apply-Reihenfolge und wird nicht in fachliche Standards, ADR-Entscheidungen oder Dokumentversionen übernommen.
4. Validation-, Acceptance- und Background-Run-Daten sind temporär und nicht Bestandteil der normalen Baseline.
5. Full-Exports werden nur für Handoff, Release oder Audit explizit angefordert.
6. Das Manifest ist die Transaktionswahrheit. Die aktuelle Changelogpflicht ist eine Legacy-Übergangsregel.
7. Prüfungen werden risikobasiert gewählt. Vollständige Maven-, Fresh-Clone- und Zielprojektprüfungen bleiben für Tooling-, Plattform-, Core- und Releaseänderungen verbindlich, nicht für jede redaktionelle Änderung.

## Consequences

- Exportprofile werden in Baseline, Patch Context und Audit getrennt.
- Der nächste Patchsystemschritt ist eine minimale Legacy-Engine-Anpassung, kein paralleler Shadow-Core.
- Dauerhafte Acceptance-Evidence wird nur erzeugt, wenn der Nachweis nicht einfach reproduzierbar oder releasekritisch ist.

## Rejected alternatives

- obligatorische Closure-Evidence für jeden Lauf;
- Vorgängerexport als allgemeine Folgerun-Precondition;
- vollständiger Export als Bestandteil jedes erfolgreichen Apply;
- dreifach vendierter gemeinsamer Core vor Governance- und Retention-Cutover.

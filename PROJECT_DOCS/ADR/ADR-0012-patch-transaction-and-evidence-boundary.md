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

## Implementation status

Patch `000140_springmaster_patch_artifact_identity_v2` implements Decision 2 with Patch Manifest V2. New artifacts use a canonical UUID URN as global `artifactId`; the numeric `patchId` remains repository-local. Historical V1 archives remain readable but no new V1 artifact is accepted.

## Consequences

- Exportprofile werden in Baseline, Patch Context und Audit getrennt.
- Der nächste Patchsystemschritt ist eine minimale Legacy-Engine-Anpassung, kein paralleler Shadow-Core.
- Dauerhafte Acceptance-Evidence wird nur erzeugt, wenn der Nachweis nicht einfach reproduzierbar oder releasekritisch ist.

## Rejected alternatives

- obligatorische Closure-Evidence für jeden Lauf;
- Vorgängerexport als allgemeine Folgerun-Precondition;
- vollständiger Export als Bestandteil jedes erfolgreichen Apply;
- dreifach vendierter gemeinsamer Core vor Governance- und Retention-Cutover.
## Accepted operational refinement: isolated acceptance

An effective patch acceptance is executed in a detached Git worktree. Validation failure does not mutate the live repository or create a live applied archive. Only a qualified patch commit whose parent is the live baseline may be transferred into the live branch. This refinement closes the previously observed `applied`-but-failed state gap without changing patch artifact identity.

## Accepted operational refinement: private transaction environment

Patch-engine control variables are private implementation state. A transaction child may use them to prevent recursive wrapping of its own `accept`, but tooling checks, Maven tests, configured tests, and exports must run with those variables removed. Nested fixtures therefore exercise the public transaction contract rather than inheriting an outer engine bypass.
## Accepted operational refinement: run API, idempotency and Git parity

Patch `000164_springmaster_patch_run_api_git_transaction_hardening` introduces a canonical local Run API. Every attempt has an immutable run ID and atomic temporary run record. Successful acceptance evidence is published separately from timestamped attempts; verification evidence is stored separately and cannot overwrite acceptance.

Acceptance start is idempotent for the same artifact: already applied and already running states return the existing durable or active state without creating another process. Git remains the durable truth. The patch log, qualified child commit and live transfer must contain exactly the same path set, and the qualified commit must descend directly from the captured live baseline.

Whitespace checks are patch-scoped and performed once at the applied, staged and qualified-commit boundaries. The engine does not reformat or repeatedly scan unrelated repository files. A pre-finalization transfer failure is compensated to the captured baseline; a post-finalization reporting or push failure remains a warning on a locally successful acceptance.

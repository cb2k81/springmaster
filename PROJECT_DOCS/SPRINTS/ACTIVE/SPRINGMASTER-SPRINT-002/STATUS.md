---
documentId: SPRINGMASTER-SPRINT-002-STATUS
title: Codex Calibration and Business Partner End-to-End Pilot – Status
documentType: sprint-status
status: active
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-28
validFrom: 2026-07-28
lastReviewedAt: 2026-07-30
reviewBy: 2026-08-21
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-002
sprintPhase: execution
overallStatus: blocked
lastDriftResult: stop-and-replan
lastDriftAt: 2026-07-30
expectedVersionImpact: minor
---

# Codex Calibration and Business Partner End-to-End Pilot – Status

## Aktueller Stand

Die dauerhafte Zielquelle und der vollständige aktive Sprintvertrag sind angelegt. Akzeptierte Source-Baseline ist `c5c5846176d92c34b19b7a7827d7264c1923805f` mit Plattform `0.21.1-foundation`, Tooling `0.11.3`, Patch Toolkit `1.1.2` und State Patch `000196_springmaster_directory_governance_runtime_audit_closure`.

```text
FORMAL_REPOSITORY_READINESS=PROJECT_READY
NEXT_LIFECYCLE_STATE=CODEX_CALIBRATION
NEXT_ACTION_EXECUTABLE=false
NEXT_ACTION_BLOCKER=TOOLING_HARDENING
WRITABLE_CODEX_AUTHORIZED=false
```

`PROJECT_READY` bleibt der formale Repositoryzustand. Die tatsächliche Vorbereitung oder Ausführung von `CODEX_CALIBRATION` ist wegen neu erkannter Tooling-Blocker ausgesetzt. Der frühere D3-Kandidat und die Payloads der Versuche `000197` bis `000200` werden nicht weiterverwendet. Kalibrierungs-Tasks und Oracles dürfen erst nach akzeptierter Härtung gegen den dann tatsächlichen Live-Commit neu erzeugt werden.

Der vollständige Tooling-Härtungscandidate ist inzwischen implementiert und der Live-Resolver hat `000201_springmaster_tooling_hardening_cut` mit `UNKNOWN_ENTRY_COUNT=0` bestimmt. Der Candidate schließt die Versionen auf Platform `0.22.0-foundation` und Tooling `0.12.0`; er bleibt `NOT_ACCEPTED`. Der operative Blocker besteht jetzt aus vollständiger Regression, breiter Qualification, kanonischem Dry-run, separatem Accept und Post-Accept-Verifikation, nicht mehr aus fehlender Implementierung oder Patch-ID-Auflösung.

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| M-001 | completed | Kanonische Zielquelle, vier aktive Sprintdokumente und Indexeinträge; Qualification durch Documentation Gate, Sprint Gate, Payload- und Patch-Preflight. |
| M-002 | blocked | Neuer Task-/Oracle-Schnitt erst nach akzeptierter Tooling-Härtung gegen die dann aktuelle Live-Baseline zulässig. |
| M-003 | planned | Keine Codex-Ausführung und keine Write-Promotion im Initialisierungsschnitt. |
| M-004 | planned | Business-Partner-Fachkonzept und Acceptance Contract sind vorhanden; Contract-Kette und disposable App noch nicht ausgeführt. |
| M-005 | planned | Repeatability-, V1.1-, Effizienz- und Closure-Evidence stehen aus. |

## Blocker und Erkenntnisse

Der frühere Status „kein Projekt-Readiness-Blocker“ vom 28. Juli 2026 ist fachlich überholt. Formal bleibt das Repository `PROJECT_READY`; operativ blockiert `TOOLING_HARDENING` den Übergang zu `CODEX_CALIBRATION`.

Aktuelle P0-/P1-Blocker:

- die implementierte zentrale Workspace-Lifecycle-, Artefakt-Root-Autorisierungs-, Inventory- und Selfcheck-Lösung muss noch die vollständige positive und negative Regressionsmatrix bestehen;
- der breite Tooling-Selfcheck und die risikogerechten Projektprofile einschließlich der vier kritischen sichtbaren Selfcheck-Result-Marker stehen noch aus;
- der Candidate ist noch nicht durch kanonischen Dry-run, separates Review, expliziten Accept und Post-Accept-Export in `main` integriert;
- der Legacy-Pfad unter `/home/cb/Downloads/cocondo-artifacts` bleibt ohne exakten Git-common Authorization Record unzulässig und wird vom Candidate fail-closed vor Workerstart blockiert;
- bis zur akzeptierten Closure bleiben `NEXT_ACTION_EXECUTABLE=false` und `WRITABLE_CODEX_AUTHORIZED=false`.

Die Versuche `000197` bis `000200` sind keine akzeptierten Source-Änderungen:

| Versuch | Ergebnis | Status für die Baseline |
|---|---|---|
| `000197` | Dry-run scheiterte an einer vermischten portablen und Runtime-Prüfung des Workspaces. | Incident-Evidence; nicht akzeptiert |
| `000198` | Vorbereitung gelang, zielgerichteter Dry-run scheiterte; der Artefaktpfad lag noch unter Downloads und der konkrete Selfcheck-Substep war zunächst verdeckt. | Incident-Evidence; nicht akzeptiert |
| `000199` | Workspace-Reset entfernte Altbestand, der Lauf wurde jedoch wegen fortbestehender Artefaktroot-Problematik als fehlgeschlagen superseded. | Incident-Evidence; nicht akzeptiert |
| `000200` | Vorbereitung scheiterte, weil eine historische `accept-discovery.env`-Datei als Delivery-Verzeichnis klassifiziert wurde. | Incident-Evidence; nicht akzeptiert |

Keine Payload dieser Versuche darf als implementierte Funktion, Candidate-Quelle oder akzeptierte Baseline verwendet werden.

## Drift-Bewertung

Ergebnis: `stop-and-replan`.

Der Lifecycle-Vertrag `PROJECT_READY -> CODEX_CALIBRATION` bleibt formal konsistent. Die operative Ausführung war jedoch gegenüber dem tatsächlichen Host- und Toolingzustand zu optimistisch dokumentiert. Sprint Brief, Solution Plan, Completion Report, Codex Operations Guide und Project Directory Governance werden deshalb auf denselben Hardening-Blocker ausgerichtet. Vor Candidate-Dry-run, Accept, Kalibrierung, Write-Promotion, Qualification und Closure ist jeweils eine erneute Driftprüfung erforderlich.

## Risiken und technische Schulden

- Legacy-Read-only-Patchvalidatoren und die kanonische Toolkit-Scope-Registry verwenden unterschiedliche Konfigurationsquellen; der Härtungsschnitt muss die kanonische Quelle beibehalten, ohne Scopegrenzen zu erweitern.
- Der vollständige P0-Schnitt muss Workspace-Lifecycle, Artefakt-Autorisierung, typisiertes Inventory und harnessgebundene Ausführung gemeinsam schließen; Selfcheck-Observability ist Bestandteil derselben Qualification.
- Die Project Directory Governance bleibt bis zur belastbaren technischen Closure `draft` und darf keine eigenständige neue Schreibberechtigung begründen.
- Die reale Codex-Runtime und deren Denial-Probes sind noch nicht als aktuelle Acceptance-Evidence vorhanden.
- Application UI Spec und GWC Implementation Manifest besitzen noch keinen in diesem Sprint qualifizierten End-to-End-Nachweis.
- Der Sprintzeitraum ist eine Steuerungsannahme; bei Überschreitung ist eine aktuelle Driftbewertung zwingend.

## Versionswirkung

Der Tooling-Härtungscandidate ist als kompatibler `minor`-Impact klassifiziert. Der final zusammenhängende Candidate setzt Platform `0.22.0-foundation`, Tooling `0.12.0` und `PLATFORM_STATE_PATCH=000201_springmaster_tooling_hardening_cut`. Diese Werte sind noch kein akzeptierter Releasezustand; sie werden erst durch den separaten kanonischen Accept zur Live-Wahrheit.

## Nächster kontrollierter Schritt

Der version- und resolvergeschlossene Candidate `000201_springmaster_tooling_hardening_cut` wird jetzt gegen die vollständige positive und negative Regressionsmatrix sowie den breiten Tooling-Selfcheck und die risikogerechten Projektprofile qualifiziert. Erst danach folgen kanonischer Dry-run, separates Review, expliziter Accept, Post-Accept-Verifikation und erneute Live-Readiness. Vorher erfolgt kein Codex-Aufruf.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | active | Erste kanonische Statusquelle für Sprint 002 angelegt; M-001 abgeschlossen, Kalibrierung noch nicht gestartet. |
| 2026-07-30 | active | blocked | Status auf Tooling-Härtung vor Kalibrierung korrigiert; `000197` bis `000200` als nicht akzeptierte Incident-Evidence klassifiziert. |
| 2026-07-30 | blocked | blocked | Candidate `000201` implementiert, Live-Inventory konfliktfrei aufgelöst und Version Closure auf `0.22.0-foundation` / `0.12.0` gesetzt; vollständige Qualification und Acceptance bleiben offen. |

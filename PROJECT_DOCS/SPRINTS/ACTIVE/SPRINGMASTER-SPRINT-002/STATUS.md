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
lastReviewedAt: 2026-08-14
reviewBy: 2026-08-21
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-002
sprintPhase: execution
overallStatus: active
lastDriftResult: accepted
lastDriftAt: 2026-08-14
expectedVersionImpact: minor
---

# Codex Calibration and Business Partner End-to-End Pilot – Status

## Codex Cutover Acceptance – 2026-08-13

Diese Sektion ist der aktuelle Cutover-Nachweis und supersediert ältere Aussagen in diesem Statusdokument, nach denen Host-Qualification, Codex-Kalibrierung oder Write-Promotion noch ausstehen. A002 wurde als fehlgeschlagener Calibration-Attempt unveränderlich geschlossen; der konkrete Change-Bundle-Read-Scope-Defekt wurde mit `000214_codex-host-change-bundle-read-scope-correction` kanonisch korrigiert. A003 wurde auf der korrigierten Baseline vollständig neu ausgeführt. Der erste Cutover-Recovery-Promotion-Kandidat wurde vor Commit und Artefakterzeugung fail-closed gestoppt, weil `codex-pilot-ready-it.sh` seine PROJECT_READY-Positive-Fixture implizit vom aktuellen Repository-Lifecycle erbte und deshalb auf einem bereits auf `PILOT_WRITE_READY` gesetzten Kandidaten deterministisch fehlschlug. Die Promotion macht diese Fixture lifecycle-neutral; der produktive Readiness-Vertrag selbst wird dadurch nicht abgeschwächt. Die reale Host-Qualification und alle mechanischen Confinement-Probes sind PASS. Zwei unabhängige A003-Implementierungskalibrierungen wurden qualifiziert, über unveränderliche Handoffs in getrennten kanonischen Dry-run-/Accept-Läufen integriert und als `000215_codex-calibration-implementation-1-a003`, `000216_codex-calibration-implementation-2-a003` akzeptiert. Das Confinement-Evidence-Manifest `5765d4d07c4f2ed4a012c9be4a1e01981d570368f474f45baf5c506b95a988f8` ist live verifiziert. Die separate Promotion setzt den Lifecycle konsistent auf `PILOT_WRITE_READY`/`PROMOTED` und autorisiert kontrollierte Codex-Pilot-Tasks. M-002 und M-003 sind damit für den Codex Cutover erfüllt; M-004 und M-005 bleiben eigenständiger Sprint-Folgebedarf.


## Aktueller Stand

Der Codex-Cutover ist kanonisch abgeschlossen. Der Harness-Fix `000214_codex-host-change-bundle-read-scope-correction`, die beiden A003-Kalibrierungspatches `000215_codex-calibration-implementation-1-a003` und `000216_codex-calibration-implementation-2-a003` sowie die separate Promotion `000218_codex-cutover-write-promotion` sind akzeptiert. Die finale Live-Qualification endete mit `CODEX_CUTOVER_ACCEPTED` auf `main`-HEAD `60c99cf05330806d2cf14efd50d70fa7f98adf74`.

Die maschinenlesbare Pilotwahrheit ist `contracts/governance/agent/codex-pilot-contract.json` Version `1.7.0`. Sie setzt den Lifecycle auf `PILOT_WRITE_READY`/`PROMOTED`, autorisiert kontrollierte Codex-Pilot-Tasks und lässt die vertrauenswürdigen Integrationsgrenzen unverändert bestehen.

```text
FORMAL_REPOSITORY_READINESS=PILOT_WRITE_READY
CUTOVER_LIFECYCLE=PROMOTED
NEXT_ACTION=CODEX_PILOT_TASK
NEXT_ACTION_EXECUTABLE=true
NEXT_ACTION_BLOCKER=NONE
WRITABLE_CODEX_AUTHORIZED=true
PILOT_WRITE_READY=true
```

Die aktuelle Post-Cutover-Versionswahrheit ist Platform `0.24.0-foundation`, Tooling `0.14.1`, Maven `0.24.0-foundation-SNAPSHOT`, Toolkit `1.1.4` und `PLATFORM_STATE_PATCH=000219_patch-toolkit-python310-portability`. Der State-Patch bleibt nach Version Policy die Quelle der aktuellen Versionswahrheit; die anschließende reine Dokumentationssynchronisierung verändert ihn nicht.

M-002 und M-003 sind abgeschlossen. Der nächste kontrollierte fachliche Slice ist M-004, der Business-Partner-End-to-End-Pilot; M-005 bleibt anschließend für Repeatability, V1.1-Evolution und Sprint-Closure vorgesehen.

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| M-001 | completed | Kanonische Zielquelle, vier aktive Sprintdokumente und Indexeinträge; Qualification durch Documentation Gate, Sprint Gate, Payload- und Patch-Preflight. |
| M-002 | completed | A003-Task-Pack gegen die korrigierte akzeptierte Baseline materialisiert; reale Analysis, Host-Qualification und plan-/hashgebundene Task-Evidence PASS. |
| M-003 | completed | Zwei unabhängige A003-Implementierungen qualifiziert und als `000215`/`000216` separat akzeptiert; Confinement live verifiziert; Write-Promotion `000218` akzeptiert; final `CODEX_CUTOVER_ACCEPTED`. |
| M-004 | planned | Business-Partner-Fachkonzept und Acceptance Contract sind eingefroren; Contract-Kette und disposable App werden als nächste reale Codex-Pilotumsetzung geplant. |
| M-005 | planned | Repeatability-, V1.1-, Effizienz- und Closure-Evidence stehen nach M-004 aus. |

## Blocker und Erkenntnisse

Die früheren Cutover-Blocker sind geschlossen. A001 und A002 bleiben unveränderliche Failure-/Incident-Evidence; A003 ist die erfolgreiche Kalibrierung auf der korrigierten Baseline. Die Promotion `000218_codex-cutover-write-promotion` autorisiert reguläre, weiterhin taskvertraglich begrenzte Codex-Pilot-Tasks.

Aktuell besteht kein P0-/P1-Cutover-Blocker. Vor M-004 gelten weiterhin die normalen Pilotgrenzen:

- jeder reale Codex-Task bindet einen exakten `baseCommit`, erlaubte Pfade, Capabilities, Qualification und Evidence;
- Codex schreibt nur in den vom Harness vorbereiteten detached Task-Worktree;
- Handoff, Candidate-Integration, kanonischer Patch, Dry-run und Accept bleiben getrennte vertrauenswürdige Operatorgrenzen;
- GWC, Personnel, IDM und gemanagte Projekte bleiben read-only Referenzquellen, solange kein ausdrücklich autorisierter separater Flow anderes festlegt;
- Sprint 003 bleibt bis zur Sprint-002-Closure beziehungsweise einem expliziten disjunkten Amendment gesperrt.

Die Versuche `000197` bis `000200`, A001 und A002 dürfen nicht als erfolgreiche Baseline oder als wiederverwendbare Invocation interpretiert werden. Ihre Evidence bleibt historisch erhalten.

## Drift-Bewertung

Ergebnis: `accepted`.

Der Cutover-Drift ist mit der akzeptierten Promotion und finalen Live-Qualification geschlossen. Die bisherige Planung wird nicht verworfen, sondern auf den noch offenen Sprintteil fokussiert: M-002/M-003 sind erfüllt; M-004 wird der nächste Slice; M-005 und die Sprint-Closure folgen danach. Diese Fortschreibung ist in `SPRINT_BRIEF.md` als `AMEND-001` dokumentiert.

## Risiken und technische Schulden

- Die erste reale Post-Cutover-Feature-Umsetzung mit Codex ist noch nicht qualifiziert; M-004 muss deshalb in kleine, vorab oracle- und scopegebundene Tasks zerlegt werden.
- Application UI Spec und GWC Implementation Manifest besitzen noch keinen in diesem Sprint qualifizierten End-to-End-Nachweis.
- Repeatability, V1.1-Evolution, Effizienzvergleich und Sprint-Closure stehen weiterhin aus.
- Der Sprintzeitraum ist eine Steuerungsannahme; bei Überschreitung ist eine aktuelle Driftbewertung zwingend.

## Versionswirkung

Aktuelle Versionswahrheit: Platform `0.24.0-foundation`, Tooling `0.14.1`, Maven `0.24.0-foundation-SNAPSHOT`, Toolkit `1.1.4`, State Patch `000219_patch-toolkit-python310-portability`. Der nachgelagerte Post-Cutover-Dokumentationsschnitt ändert keine weitere Produkt-, Tooling-, Core-, Demo-, Template- oder Platform-Update-Semantik und löst daher keinen zusätzlichen Komponenten- oder Foundation-Bump aus.

## Nächster kontrollierter Schritt

M-004 wird sorgfältig vor der ersten realen Feature-Invocation geplant. Zuerst werden Business-Partner-Fachkonzept und Acceptance Contract in eine kleine deterministische Contract-/Intent-Kette zerlegt; danach werden Task Contract, erlaubte Pfade, Oracles, Qualification Commands, Evidence und Handoff-Grenzen vollständig eingefroren. Erst dann wird der erste reale Codex-Pilot-Task auf einer sauberen akzeptierten Baseline vorbereitet.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | active | Erste kanonische Statusquelle für Sprint 002 angelegt; M-001 abgeschlossen, Kalibrierung noch nicht gestartet. |
| 2026-07-30 | active | blocked | Status auf Tooling-Härtung vor Kalibrierung korrigiert; `000197` bis `000200` als nicht akzeptierte Incident-Evidence klassifiziert. |
| 2026-07-30 | blocked | blocked | Candidate `000201` implementiert, Live-Inventory konfliktfrei aufgelöst und Version Closure auf `0.22.0-foundation` / `0.12.0` gesetzt; vollständige Qualification und Acceptance bleiben offen. |
| 2026-07-31 | blocked | blocked | Acceptance von `000201` nachvollzogen; aktueller Blocker auf kanonische Acceptance von `000203`, reale Host-Qualification und Kalibrierung fortgeschrieben. |
| 2026-08-01 | blocked | blocked | Acceptance von `000203` aus dem kanonischen Delivery-Inventory bestätigt; nächster Abschnitt auf Post-Accept-Live-Readiness, Host-Qualification und plan-gebundene Kalibrierung fortgeschrieben. |
| 2026-08-13 | blocked | active | A003-Kalibrierung, zwei getrennte Calibration-Accepts, live verifizierte Confinement-Evidence und Promotion `000218` abgeschlossen; `CODEX_CUTOVER_ACCEPTED`, nächster Slice M-004. |
| 2026-08-14 | active | active | Post-Cutover-Tooling-Portabilität mit `000219` geschlossen; diese Dokumentationssynchronisierung bildet die Zielwahrheit für die abschließende `POST_CUTOVER_DEVELOPMENT_BASELINE_READY`-Qualification ab; M-004 bleibt nächster fachlicher Slice. |

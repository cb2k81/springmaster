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
lastReviewedAt: 2026-08-13
reviewBy: 2026-08-21
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-002
sprintPhase: execution
overallStatus: blocked
lastDriftResult: stop-and-replan
lastDriftAt: 2026-08-01
expectedVersionImpact: minor
---

# Codex Calibration and Business Partner End-to-End Pilot – Status

## Codex Cutover Acceptance – 2026-08-13

Diese Sektion ist der aktuelle Cutover-Nachweis und supersediert ältere Aussagen in diesem Statusdokument, nach denen Host-Qualification, Codex-Kalibrierung oder Write-Promotion noch ausstehen. A002 wurde als fehlgeschlagener Calibration-Attempt unveränderlich geschlossen; der konkrete Change-Bundle-Read-Scope-Defekt wurde mit `000214_codex-host-change-bundle-read-scope-correction` kanonisch korrigiert. A003 wurde auf der korrigierten Baseline vollständig neu ausgeführt. Der erste R5-Promotion-Kandidat wurde vor Commit und Artefakterzeugung fail-closed gestoppt, weil `codex-pilot-ready-it.sh` seine PROJECT_READY-Positive-Fixture implizit vom aktuellen Repository-Lifecycle erbte und deshalb auf einem bereits auf `PILOT_WRITE_READY` gesetzten Kandidaten deterministisch fehlschlug. Die Promotion macht diese Fixture lifecycle-neutral; der produktive Readiness-Vertrag selbst wird dadurch nicht abgeschwächt. Die reale Host-Qualification und alle mechanischen Confinement-Probes sind PASS. Zwei unabhängige A003-Implementierungskalibrierungen wurden qualifiziert, über unveränderliche Handoffs in getrennten kanonischen Dry-run-/Accept-Läufen integriert und als `000215_codex-calibration-implementation-1-a003`, `000216_codex-calibration-implementation-2-a003` akzeptiert. Das Confinement-Evidence-Manifest `5765d4d07c4f2ed4a012c9be4a1e01981d570368f474f45baf5c506b95a988f8` ist live verifiziert. Die separate Promotion setzt den Lifecycle konsistent auf `PILOT_WRITE_READY`/`PROMOTED` und autorisiert kontrollierte Codex-Pilot-Tasks. M-002 und M-003 sind damit für den Codex Cutover erfüllt; M-004 und M-005 bleiben eigenständiger Sprint-Folgebedarf.


## Aktueller Stand

Die Tooling-Härtung `000201_springmaster_tooling_hardening_cut` und die Codex-Cutover-Foundation `000203_springmaster_codex_cutover_foundation` sind kanonisch akzeptiert. `93ab563cc1e82bc801907399602fe04e6d37e2f7` ist der historische Accept-Commit von `000203_springmaster_codex_cutover_foundation`; der operative Integrationsstand ist immer der aktuell saubere `main`-HEAD und darf nicht aus dieser historischen Evidence abgeleitet werden. Platform `0.23.0-foundation` und Tooling `0.13.0` beschreiben die Foundation-Baseline von `000203`, nicht einen festgeschriebenen aktuellen HEAD.

Die vorliegende Stabilisierung bindet `agent-task prepare` unter `PROJECT_READY` fail-closed an den materialisierten Calibration Plan, erzeugt gültige Calibration Tasks und verhindert die Übernahme eines Host-`PATH` in die äußere Codex-Sandbox. Sie autorisiert weder reguläre Feature-Tasks noch schreibende Codex-Nutzung.

```text
FORMAL_REPOSITORY_READINESS=PROJECT_READY
NEXT_LIFECYCLE_STATE=CODEX_CALIBRATION
NEXT_ACTION=POST_ACCEPT_LIVE_READINESS_AND_HOST_QUALIFICATION
NEXT_ACTION_EXECUTABLE=true
NEXT_ACTION_BLOCKER=NONE
WRITABLE_CODEX_AUTHORIZED=false
PILOT_WRITE_READY=false
```

`PROJECT_READY` bleibt der formale Repositoryzustand. Der nächste zulässige Operatorabschnitt umfasst Post-Accept-Live-Readiness, hostgebundene Bubblewrap-Qualification und die Materialisierung des Calibration Task Packs gegen den akzeptierten Live-Commit. Reale Codex-Aufrufe bleiben auf die kanonische Kalibrierung begrenzt. Die Versuche `000197` bis `000200` bleiben ausschließlich Incident-Evidence und werden nicht wiederverwendet.

## Teilziele

| ID | Status | Evidence oder Blocker |
|---|---|---|
| M-001 | completed | Kanonische Zielquelle, vier aktive Sprintdokumente und Indexeinträge; Qualification durch Documentation Gate, Sprint Gate, Payload- und Patch-Preflight. |
| M-002 | in-progress | Materializer, Host-Sandbox und Calibration-Harness sind vorhanden; das autoritative Task-Pack wird nach bestandener Post-Accept-Live-Readiness und Host-Qualification gegen den akzeptierten Live-Commit materialisiert. |
| M-003 | blocked | Reale Host-Qualification, zwei akzeptierte Kalibrierungsaufgaben und separate Write-Promotion stehen aus. |
| M-004 | planned | Business-Partner-Fachkonzept und Acceptance Contract sind vorhanden; Contract-Kette und disposable App noch nicht ausgeführt. |
| M-005 | planned | Repeatability-, V1.1-, Effizienz- und Closure-Evidence stehen aus. |

## Blocker und Erkenntnisse

Die früheren Blocker `TOOLING_HARDENING` und `CODEX_CUTOVER_FOUNDATION_ACCEPTANCE` sind durch die kanonischen Acceptances von `000201` und `000203` geschlossen. Formal bleibt das Repository `PROJECT_READY`; der nächste kontrollierte Abschnitt ist operativ ausführbar, ohne dadurch schreibende Codex-Nutzung zu autorisieren.

Aktuelle P0-/P1-Blocker:

- die Live-Readiness muss gegen den akzeptierten Commit und explizit autorisierte externe Roots erneut ausgeführt werden;
- Host-Inspection und alle mechanischen Confinement-Probes müssen auf dem realen DEV-System bestehen;
- das Calibration Task Pack muss gegen den akzeptierten Commit materialisiert werden; unter `PROJECT_READY` dürfen nur dessen bytegenau registrierte Tasks vorbereitet werden;
- zwei implementierende Kalibrierungsaufgaben müssen über Handoff, Candidate, `cpatch create`, separaten Dry-run und separaten Accept qualifiziert werden;
- die Promotion zu `PILOT_WRITE_READY` bleibt eine eigene committed Entscheidung; bis dahin gelten `WRITABLE_CODEX_AUTHORIZED=false` und `PILOT_WRITE_READY=false`.

Die Versuche `000197` bis `000200` sind keine akzeptierten Source-Änderungen:

| Versuch | Ergebnis | Status für die Baseline |
|---|---|---|
| `000197` | Dry-run scheiterte an einer vermischten portablen und Runtime-Prüfung des Workspaces. | Incident-Evidence; nicht akzeptiert |
| `000198` | Vorbereitung gelang, zielgerichteter Dry-run scheiterte; der Artefaktpfad lag noch unter Downloads und der konkrete Selfcheck-Substep war zunächst verdeckt. | Incident-Evidence; nicht akzeptiert |
| `000199` | Workspace-Reset entfernte Altbestand, der Lauf wurde jedoch wegen fortbestehender Artefaktroot-Problematik als fehlgeschlagen superseded. | Incident-Evidence; nicht akzeptiert |
| `000200` | Vorbereitung scheiterte, weil eine historische `accept-discovery.env`-Datei als Delivery-Verzeichnis klassifiziert wurde. | Incident-Evidence; nicht akzeptiert |

Keine Payload dieser Versuche darf als implementierte Funktion, Candidate-Quelle oder akzeptierte Baseline verwendet werden.

## Drift-Bewertung

Ergebnis: `controlled-resume`.

Der Lifecycle-Vertrag `PROJECT_READY -> CODEX_CALIBRATION` ist formal und technisch konsistent. Die Acceptances von `000201` und `000203` erlauben die kontrollierte Wiederaufnahme mit Post-Accept-Live-Readiness und Host-Qualification. Vor Kalibrierung, Write-Promotion, Business-Partner-Pilot, Qualification und Closure bleibt jeweils eine erneute Driftprüfung erforderlich.

## Risiken und technische Schulden

- Die reale Codex-Runtime und deren Denial-Probes sind noch nicht als aktuelle Acceptance-Evidence vorhanden.
- Application UI Spec und GWC Implementation Manifest besitzen noch keinen in diesem Sprint qualifizierten End-to-End-Nachweis.
- Der Sprintzeitraum ist eine Steuerungsannahme; bei Überschreitung ist eine aktuelle Driftbewertung zwingend.

## Versionswirkung

`000201_springmaster_tooling_hardening_cut` und `000203_springmaster_codex_cutover_foundation` sind akzeptiert. Die aktuelle Versionswahrheit bleibt Platform `0.23.0-foundation`, Tooling `0.13.0` und `PLATFORM_STATE_PATCH=000203_springmaster_codex_cutover_foundation`. Die Stabilisierung ist ein kompatibler Tooling-Patch innerhalb dieser Foundation und führt keine Release- oder Write-Promotion durch.

## Nächster kontrollierter Schritt

Als nächster kontrollierter Schritt wird das Calibration Task Pack gegen den aktuell sauberen `main`-HEAD materialisiert und geprüft. Unmittelbar vor einer realen Codex-Invocation müssen Live-Readiness, Host-Inspection und mechanische Confinement-Probes für genau diesen aktuellen HEAD erfolgreich sein. `PROJECT_READY` autorisiert keine reguläre schreibende Codex-Nutzung; `PILOT_WRITE_READY` bleibt einer separaten Promotion vorbehalten.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | – | active | Erste kanonische Statusquelle für Sprint 002 angelegt; M-001 abgeschlossen, Kalibrierung noch nicht gestartet. |
| 2026-07-30 | active | blocked | Status auf Tooling-Härtung vor Kalibrierung korrigiert; `000197` bis `000200` als nicht akzeptierte Incident-Evidence klassifiziert. |
| 2026-07-30 | blocked | blocked | Candidate `000201` implementiert, Live-Inventory konfliktfrei aufgelöst und Version Closure auf `0.22.0-foundation` / `0.12.0` gesetzt; vollständige Qualification und Acceptance bleiben offen. |
| 2026-07-31 | blocked | blocked | Acceptance von `000201` nachvollzogen; aktueller Blocker auf kanonische Acceptance von `000203`, reale Host-Qualification und Kalibrierung fortgeschrieben. |
| 2026-08-01 | blocked | blocked | Acceptance von `000203` aus dem kanonischen Delivery-Inventory bestätigt; nächster Abschnitt auf Post-Accept-Live-Readiness, Host-Qualification und plan-gebundene Kalibrierung fortgeschrieben. |

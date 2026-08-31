---
documentId: SPRINGMASTER-SPRINT-005-BRIEF
title: Autonomous Repair Loop V1 - Sprint Brief
documentType: sprint-brief
status: archived
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-25
validFrom: 2026-08-25
lastReviewedAt: 2026-08-30
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINGMASTER-SPRINT-005
sprintStart: 2026-08-25
targetCompletion: 2026-09-07
---

# Autonomous Repair Loop V1 - Sprint Brief

## Sprintziel

Sprint 005 implementiert `GOAL-006`: Ein freigegebener fachlicher Entwicklungsauftrag wird als genau ein operator-sichtbarer Logical Run geführt. Normale deterministische Implementierungs- und Qualification-Fehler werden innerhalb unveränderter Autorisierungsgrenzen automatisch an einen neuen immutable Codex-Attempt zurückgeführt, bis der Auftrag `PREACCEPT` erreicht oder ein explizites Stop-Kriterium eintritt.

Der Sprint automatisiert Orchestrierung. Er ersetzt oder lockert nicht die bewährten Sicherheitsprimitiven `agent-task` V2, Codex Host Sandbox, Change Bundle, `process-ops`, cpatch oder die menschliche Patch-Accept-Grenze.

## Strategischer Bezug

- Primärziel: `GOAL-006` autonome agentische Entwicklung bis Pre-Accept.
- `GOAL-007` bleibt Folgeziel: S005 muss den Logical Run projektneutral genug schneiden, dass S006 ihn als Managed Development Platform transportieren kann, ohne S006 vorwegzunehmen.
- Der Codex-Cutover gilt erst dann als effizient, wenn normale Repair-Zyklen keine menschliche Task-/Operator-Neuerzeugung mehr benötigen.
- Sicherheit, Evidence und Human Accept bleiben unverändert harte Grenzen.

## Ausgangslage und Baseline

Kanonische Post-Sprint-004-Baseline:

```text
BRANCH=main
HEAD=59d18c34d398c9ec6836d2ab3c0bfefebe83072e
SPRINT004_RESULT=DOD_QUALIFIED
PLATFORM_VERSION=0.26.0-foundation
PLATFORM_CORE_VERSION=0.6.0
PLATFORM_TOOLING_VERSION=0.15.0
PLATFORM_STATE_PATCH=000249_s004-trusted-closure
ACTIVE_SPRINT_COUNT=0
```

Sprint 004 hat die fachliche Agentenentwicklung, Trusted Qualification, Handoff, Candidate, cpatch und Dry-run grundsätzlich bewiesen. Beobachtete manuelle Recovery-Klassen waren insbesondere ein Codex-Stream-Lag-False-Negative, successor-attempt-Erzeugung nach deterministischen Sprint-Gate-Findings, `umask 077`-bedingte Modematerialisierung sowie zwei chatseitige Closure-Operatorfehler durch fragile Textannahmen und inkonsistente Pfadmengen.

## Problemstellung und Stakeholder

Der vorhandene Harness schützt das Repository zuverlässig, aber die Orchestrierung zwischen physischen Attempts ist noch menschlich. Das erzeugt unnötige Wartezeit, Chat-Roundtrips, Recovery-Operatoren und das Risiko, bei jedem Folgeattempt Scope, Evidence oder Arbeitsstand inkonsistent zu rekonstruieren.

Stakeholder sind Springmaster-Maintainer, Entwickler künftiger Fachanwendungen, Architektur-/Security-Reviewer und Betreiber des qualifizierten DEV-Hosts.

## Anforderungen

| ID | Verbindliche Anforderung |
|---|---|
| `S005-REQ-001` | Ein autorisierter Auftrag besitzt genau eine stabile Logical-Run-ID und intern höchstens endlich viele immutable V2-Attempts. |
| `S005-REQ-002` | Ein gestarteter oder aufgezeichneter physischer Attempt wird niemals erneut invoked. |
| `S005-REQ-003` | Successor-Attempts behalten Base Commit, Integration Branch, Risk Class, Change Classes, erlaubte/verbotene Pfade, Capabilities und Qualification argv arrays unverändert. |
| `S005-REQ-004` | Eine materielle Änderung dieser Autorisierung beendet den Logical Run mit einem expliziten Stop-/Replan-Grund. |
| `S005-REQ-005` | Vorherige erlaubte Arbeitsbytes werden ausschließlich über ein immutable, hashgebundenes Codex Change Bundle in den Successor übertragen. |
| `S005-REQ-006` | Carry-forward prüft Bytes und POSIX-Modi; deklarierte Modi werden hostseitig unabhängig von `umask` deterministisch materialisiert. |
| `S005-REQ-007` | Compiler-, Test-, Contract-, Fixture-, Documentation-, Sprint-/Gate-, OpenAPI-/Golden- und deterministische Build-Fehler im Scope sind standardmäßig Repair-Signale. |
| `S005-REQ-008` | Mehrere unabhängige Qualification-Findings werden soweit sicher möglich in einem Failure Packet konsolidiert. |
| `S005-REQ-009` | Jedes Failure Packet bindet Logical Run, Attempt-Ordinal, Base, Worktree-Fingerprint, Changed Paths, Postcheck, Qualification-Ergebnisse, Log-SHA-256, bounded Log Tails, Failure Fingerprint und Successor-ID. |
| `S005-REQ-010` | `SCOPE_EXPANSION_REQUIRED`, `CAPABILITY_EXPANSION_REQUIRED`, `ORACLE_CHANGE_REQUIRED`, Security Boundary, Base Drift, normative Entscheidung, externe Abhängigkeit und echter Host-/Toolfehler werden nicht automatisch repariert. |
| `S005-REQ-011` | Der Loop besitzt ein endliches `maxAttempts`-Budget und aktive Zeitbudgets. |
| `S005-REQ-012` | Wiederholter identischer Failure Fingerprint ohne Byte-Fortschritt endet fail-closed als No-Progress. |
| `S005-REQ-013` | Bekannter Event-Stream-Lag darf nur unter den exakt in ADR-0019 definierten maschinengeprüften Bedingungen als `TRANSPORT_DEGRADED_CONTINUE` klassifiziert werden. |
| `S005-REQ-014` | Raw Host Evidence wird bei Stream-Lag oder anderer Degradation niemals von FAILED zu PASS umgeschrieben. |
| `S005-REQ-015` | `process-ops` bleibt alleiniger Owner langlebiger Worker; der Logical Run führt keine zweite `nohup`-/PID-/Supervisor-State-Machine ein. |
| `S005-REQ-016` | Start/Resume über Singleton-Semantik erzeugt nach Terminalverlust oder VM Suspend keinen zweiten Logical-Run-Writer. |
| `S005-REQ-017` | Der repository-native Einstieg besitzt mindestens Start-, Status- und Result-/Resume-Semantik mit maschinenlesbarer persistierter State Evidence. |
| `S005-REQ-018` | Final erfolgreiche Qualification ist vollständig und frisch; frühere Teil-PASS werden nicht als finale Qualification wiederverwendet. |
| `S005-REQ-019` | Nach finaler Qualification erfolgen Handoff, Trusted Candidate, cpatch create/inspect/plan und kanonischer Dry-run automatisch. |
| `S005-REQ-020` | Der terminale Normalerfolg ist `PREACCEPT` / `HUMAN_ACCEPT_REQUIRED`. |
| `S005-REQ-021` | Automatischer `patch-accept`, Push, Agent-Commit, Cross-Project-Mutation und direkter Agent-Schreibzugriff auf `main` bleiben verboten. |
| `S005-REQ-022` | Integration `main` bleibt vom Logical-Run-Start bis Pre-Accept auf der gebundenen Baseline sauber und unverändert. |
| `S005-REQ-023` | Neue Tooling-Tests und Fixtures werden vollständig in Test-Inventar und Fixture Contract registriert; keine A001-artige Scope-Lücke zwischen Testdatei und Pflichtinventar. |
| `S005-REQ-024` | Die Regression-Suite deckt first-pass success, repair successor, zwei konsolidierte Findings, Scope Stop, Host Tool Stop, No-Progress, Budget Exhaustion, Stream-Lag, unbekannten Codex-Fehler, Restart/Resume und Attempt-Reinvoke-Verbot ab. |
| `S005-REQ-025` | Die Regression-Suite deckt byte-/mode-exakten Carry-forward einschließlich `umask 077` sowie strukturelle Erkennung widersprüchlicher interner Pfadmengen ab. |
| `S005-REQ-026` | Der Normalpfad benötigt nach Logical-Run-Start bis Pre-Accept `HUMAN_REPAIR_ACTIONS=0`. |
| `S005-REQ-027` | Die Implementierung verändert die Sicherheitssemantik von `agent-task`, `codex-host-sandbox`, `process-ops` und cpatch nicht. Wird eine solche Änderung notwendig, ist `stop-and-replan` verpflichtend. |
| `S005-REQ-028` | Code, Contracts, Tests, Tooling-Dokumentation, Sprintstatus und Completion Evidence treffen vor Product Accept dieselbe nicht-terminale Aussage; Sprint-Closure und finale Version Truth bleiben Trusted-Host-Aufgabe. |

## Qualitätsanforderungen

- Standardbibliothek bevorzugen; keine neue Runtime-Dependency.
- Deterministisches JSON, stabile Failure-/State-Codes und explizite Exit-Codes.
- Keine Shell-Evaluierung von Qualification Commands; argv arrays bleiben unverändert.
- Persistierte Evidence bleibt außerhalb des Repository-Worktrees und ist crash-/resume-fähig.
- Bounded Logs für Prompt-Feedback, vollständige Logs bleiben hashgebundene Evidence.
- Tests simulieren Worker und Codex deterministisch; echte Netzwerkabhängigkeit ist nicht Teil der Regression-Suite.
- Kompakte Operatorausgabe: Logical Run, aktueller Attempt, State, letzter Failure/Blocker und Pre-Accept-Patchidentität.

## In Scope

- neuer repository-native Logical-Run-Orchestrator unter `bin/`;
- versionierte Logical-Run-/State-/Failure-Packet-Verträge unter `contracts/governance/agent/`;
- neue deterministische Tooling-ITs und erforderliche Fixtures;
- Test-Inventar-/Fixture-Registrierung;
- Tooling-Dokumentation für Start, Status, Resume, Failure Classification und Pre-Accept;
- nicht-terminale Aktualisierung von Sprint-005-Status und Completion Report während der Implementierung;
- ein implementierungsnaher ADR-0019-konformer Schnitt über vorhandene Agent-/Host-/Process-/Patch-Primitiven.

## Out of Scope

- Änderung der Sicherheitssemantik oder des Contract V2 von `agent-task`;
- Änderung der Bubblewrap-/Credential-/Host-Autorisierungsgrenzen;
- Änderung von `process-ops`-Workerownership oder cpatch-Accept-Semantik;
- automatischer Patch-Accept oder Push;
- Mutation von Personnel, GWC oder anderen Managed Targets;
- Portierung auf Fachanwendungen; das ist S006;
- Real-World-Fachanwendungsnachweis; das ist S007;
- vollständige Neuarchitektur des bestehenden Codex-Harness.

## Constraints und Abhängigkeiten

- ADR-0012, ADR-0014, ADR-0015, ADR-0016 und ADR-0019 bleiben bindend.
- Host `c046125370249d5e8a42208d` ist bereits qualifiziert; keine erneute Host-Kalibrierung ohne neue Defektevidence.
- Der bestehende `process-ops run-start --singleton-key`-Mechanismus ist der vorgesehene Owner für den langlebigen Logical-Run-Worker.
- Der Bootstrap zur Implementierung von S005 darf noch den vorhandenen one-shot Agent-Task-Pfad verwenden; erst der akzeptierte S005-Produktstand wird kanonischer autonomer Runner.

## Risiken

- Der äußere Automat könnte unbeabsichtigt zu einem zweiten Prozess-Supervisor werden.
- Failure Classification könnte echte Host-/Security-Probleme fälschlich als Produktrepair behandeln.
- Zu breite Successor-Prompts könnten Scope Drift erzeugen.
- Wiederverwendung alter Qualification-PASS könnte eine nicht-frische finale Evidence vortäuschen.
- Zu enge Tests könnten nur den S005-Bootstrap statt allgemeine Failure-Klassen beweisen.

## Definition of Ready

- [x] Sprint 004 ist `DOD_QUALIFIED`, akzeptiert und archiviert.
- [x] `GOAL-006` und `GOAL-007` sind kanonisch persistiert.
- [x] Post-S004-Baseline `59d18c34d398c9ec6836d2ab3c0bfefebe83072e` ist sauber exportiert und hashgebunden.
- [x] ADR-0019 definiert die Logical-Run-Architektur vor Codex-Implementierung.
- [x] Reale Failure-Klassen aus Sprint 004 sind als verpflichtende Regressionen benannt.
- [x] Out-of-scope-Sicherheitsprimitiven und Human-Accept-Grenze sind explizit fixiert.

## Definition of Done

- [ ] `ONE_LOGICAL_RUN=true` und `FAILED_ATTEMPT_REINVOKE=false` sind automatisiert bewiesen.
- [ ] `ORDINARY_REPAIR_REQUIRES_HUMAN=false` ist durch einen automatischen Successor-Test bewiesen.
- [ ] `QUALIFICATION_FAILURES_CONSOLIDATED=true` ist durch mindestens zwei unabhängige Findings bewiesen.
- [ ] `BYTE_EXACT_WORK_CARRY_FORWARD=true` und Mode-Normalisierung unter `umask 077` sind bewiesen.
- [ ] `MAX_ATTEMPTS_FINITE=true` und `NO_PROGRESS_DETECTION=true` sind bewiesen.
- [ ] `PROCESS_OPS_OWNS_DURABLE_EXECUTION=true` und Suspend/Resume ohne Duplicate Writer sind bewiesen.
- [ ] Stream-Lag-False-Negative wird exakt klassifiziert; unbekannte Fehler bleiben blocking.
- [ ] Finale Qualification ist frisch und vollständig.
- [ ] Handoff, Candidate, cpatch create/inspect/plan und Dry-run laufen automatisch bis `PREACCEPT`.
- [ ] `MAIN_AGENT_WRITABLE=false` und `AUTOMATIC_PATCH_ACCEPT=false` sind negative Tests.
- [ ] Test Contracts, Test Inventory, Documentation Gate, Sprint Gate und relevante Tooling-Regressionen sind PASS.
- [ ] Ein echter S005-Logical-Run-Canary erreicht vor Product Accept ohne menschliche Repair-Aktion `PREACCEPT`.
- [ ] Trusted Host bestätigt Scope, Evidence, SemVer-Wirkung und Product cpatch vor separatem Human Accept.

## Messbare Teilziele

| ID | Ergebnis | Anforderungen | Acceptance | Evidence | Owner | Status |
|---|---|---|---|---|---|---|
| M-001 | Logical-Run Contracts und repository-native Entry Points | REQ-001..006, REQ-017 | Schema-/CLI-Tests PASS | Contracts, tool IT | Codex + Trusted Host | planned |
| M-002 | Failure Classification, Repair Packet, Budget und Progress | REQ-007..014 | repair/stop fixtures PASS | failure packet fixtures | Codex + Trusted Host | planned |
| M-003 | Durable Attempt Orchestration und Resume | REQ-015..018 | singleton/resume/no-reinvoke PASS | process-bound IT | Codex + Trusted Host | planned |
| M-004 | Automatischer Handoff-to-Preaccept-Pfad | REQ-019..022 | candidate/cpatch/dry-run mock+integration PASS | preaccept IT | Codex + Trusted Host | planned |
| M-005 | vollständige Regressionen und Effizienznachweis | REQ-023..027 | verpflichtende Failure-Matrix PASS; human repair 0 | test inventory, reports | Trusted Host | planned |
| M-006 | Product Accept und Sprint Closure | REQ-028 | final qualification, human accept, version closure | cpatch/accept/closure evidence | Maintainer | planned |

## SemVer-Auswirkung

Erwartung vor Implementierung:

```text
PLATFORM_TOOLING_VERSION=minor
PLATFORM_VERSION=minor
PLATFORM_CORE_VERSION=none
PLATFORM_TEMPLATE_VERSION=none
PLATFORM_DEMO_VERSION=none
PLATFORM_UPDATE_VERSION=none
```

Konkrete Werte und `PLATFORM_STATE_PATCH` werden erst nach akzeptiertem S005-Produktpatch in der Trusted-Host-Closure gebunden.

## Stop- und Abbruchkriterien

`stop-and-replan`, wenn mindestens eines eintritt:

1. `agent-task` V2, Host Sandbox, `process-ops` oder cpatch müssten ihre Sicherheitssemantik ändern;
2. automatische Repair-Fortsetzung benötigt Scope-/Capability-/Oracle-Erweiterung;
3. ein echter Host-, Credential-, Sandbox- oder Security-Defekt wird nachgewiesen;
4. Integration Base driftet während des Logical Runs;
5. eine neue Runtime-Dependency oder Netzwerkabhängigkeit wird erforderlich;
6. ein normativer Architekturentscheid außerhalb ADR-0019 wird benötigt;
7. die finale Human-Accept-Grenze könnte nicht getrennt gehalten werden;
8. der Mechanismus ist nur Springmaster-spezifisch implementierbar und verhindert die geplante S006-Portabilität.

Normale deterministische Implementierungs- und Qualification-Fehler innerhalb des fixierten Scopes sind ausdrücklich keine Stop-Kriterien.

## Amendments

Keine.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-25 | - | active | Post-S004-Cutover-Ziel GOAL-006 wird als nächster kontrollierter Sprint aktiviert. |

---
documentId: SPRINGMASTER-SPRINT-005-PLAN
title: Autonomous Repair Loop V1 - Solution Plan
documentType: plan
status: active
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-25
validFrom: 2026-08-25
lastReviewedAt: 2026-08-25
reviewBy: 2026-09-07
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-005
---

# Autonomous Repair Loop V1 - Solution Plan

## Lösungsoptionen und Auswahl

Gewählt wird ein neuer repository-native Outer Orchestrator, der vorhandene Sicherheitsprimitiven unverändert zusammensetzt. Der langlebige Worker wird über `process-ops run-start --singleton-key` gestartet; physische Codex-Ausführungen bleiben `agent-task`-V2-Attempts über `codex-host-sandbox invoke-start`; Work-Carry-Forward verwendet `codex-change-bundle`; Promotion verwendet Handoff, Candidate und cpatch.

Nicht gewählt werden Reinvocation verbrauchter Tasks, ein zweiter Prozess-Supervisor, direkte Main-Mutation, automatische Acceptance oder ein Umbau des Host-Harness im selben Sprint.

## Architektur- und Contract-Auswirkungen

Geplant sind neue versionierte Verträge für immutable Logical-Run-Input, persistierten Logical-Run-State und Failure Packets. Der Orchestrator besitzt keine neue Sicherheitsautorität; er darf nur bereits autorisierte Primitive aufrufen und deren maschinenlesbare Evidence auswerten.

ADR-0019 ist vor Implementierungsstart akzeptiert und damit normative Architekturquelle. Bestehende ADR-0012/0014/0015/0016 bleiben unverändert bindend.

## Slices und Reihenfolge

1. **S005-A001 – Contracts und Orchestrator Foundation:** CLI/State, Attempt-ID-Generierung, persistente Evidence, Preflight und reine Mock-First-Pass-Route.
2. **S005-A001 – Repair Engine:** Classification, konsolidiertes Failure Packet, Change-Bundle-Carry-Forward, Budget/No-Progress, Stream-Lag-Regel.
3. **S005-A001 – Durable Execution:** process-ops singleton start/resume, Recovery nach Observer-/VM-Unterbrechung, Duplicate-Writer-Schutz.
4. **S005-A001 – Pre-Accept Promotion:** finale frische Qualification, Handoff, Candidate, cpatch create/inspect/plan und Dry-run; kein Accept.
5. **Trusted Host:** vollständige Regressionen und ein realer Canary. Deterministische Produktfehler im A001-Output rechtfertigen einen neuen immutable Successor-Task nur im Bootstrap; ab akzeptiertem S005-Produktstand übernimmt der neue Logical Run diese Funktion selbst.
6. **Trusted Closure:** Product Accept, SemVer und Sprintarchivierung bleiben außerhalb Codex.

## Teststrategie und Zwischenverifikationen

Der neue `bin/codex-autonomous-run-it.sh` muss vollständig isolierte Git-/Run-/Artifact-Roots verwenden und alle in Sprint Brief REQ-024/025 geforderten positiven und negativen Fälle deterministisch simulieren. Neue Fixtures werden vor Qualification im Test Fixture Contract und Test Inventory registriert.

Zwischenverifikationen starten eng mit Contract-/CLI-/IT-Tests und erweitern danach auf `test-contracts`, Agent-/Change-Bundle-/Process-ITs, Documentation/Sprint Gate und das breite Tooling-/Build-Profil. Die finale Trusted-Host-Qualification ist frisch und vollständig.

## Messkriterien

Zielmarker:

```text
ONE_COMMAND_START=true
ONE_LOGICAL_RUN_ID=true
ORDINARY_REPAIR_REQUIRES_HUMAN=false
FAILED_ATTEMPT_REINVOKE=false
AUTOMATIC_SUCCESSOR_ATTEMPTS=true
QUALIFICATION_FAILURES_CONSOLIDATED=true
BYTE_EXACT_WORK_CARRY_FORWARD=true
MAX_ATTEMPTS_FINITE=true
NO_PROGRESS_DETECTION=true
PROCESS_OPS_OWNS_DURABLE_EXECUTION=true
VM_SUSPEND_RESUME_SUPPORTED=true
FINAL_QUALIFICATION_FRESH_AND_COMPLETE=true
AUTOMATIC_HANDOFF=true
AUTOMATIC_CANDIDATE=true
AUTOMATIC_CPATCH_CREATE_INSPECT_PLAN=true
AUTOMATIC_PATCH_DRY_RUN=true
MAIN_AGENT_WRITABLE=false
AUTOMATIC_PATCH_ACCEPT=false
SUCCESS_BOUNDARY=PREACCEPT
```

## Migration und Rollback

Es gibt keine Datenmigration. Der neue Runner ist additiv. Solange sein Product Patch nicht akzeptiert ist, bleibt der bestehende one-shot Agent-Task-Prozess kanonisch. Bei Blocker oder fehlgeschlagener Qualification wird der Candidate verworfen; bestehende Host-/Agent-/Patch-Primitiven bleiben unverändert verwendbar.

## Tool- und Gate-Einsatz

Mindestens:

```text
./bin/codex-autonomous-run-it.sh
./bin/agent-task-it.sh
./bin/codex-change-bundle-it.sh
./bin/codex-host-sandbox-it.sh
./bin/process-ops-it.sh
./bin/test-contracts.sh all --check
./bin/test-contracts-it.sh
./bin/documentation-gate.sh --check-all
./bin/sprint-gate.sh --mode all --check
./bin/tooling-selfcheck.sh
mvn -q test
mvn -q clean verify
```

Die genaue immutable Qualification-Liste des Codex-Tasks wird vor Task-Preparation festgelegt und darf während Repair nicht geändert werden.

## Dokumentations- und Registerauswirkungen

Dauerhaft erwartet: ADR-0019, Tooling-Betriebsdokumentation, neue Agent-Contracts, Test Inventory/Fixture Contract und Dokumentationsindex. Sprint `STATUS.md` und `COMPLETION_REPORT.md` dürfen im Codex-Task nur nicht-terminal aktualisiert werden. Sprint Brief und Solution Plan bleiben frozen inputs.

## Versionswirkung

Erwartet werden ein Tooling-Minor und ein Foundation-Minor. Keine Core-, Demo-, Template- oder Update-Version wird allein durch S005 erhöht. Finale Werte werden erst in der Trusted-Host-Closure gesetzt.

## Patch- oder Commitsequenz

1. S005-Aktivierung und ADR-0019 als separater Governance-cpatch, Dry-run, Human Accept.
2. Ein scopegebundener Codex-Implementierungstask auf der akzeptierten S005-Baseline.
3. Trusted-Host-Qualification und, falls im Bootstrap erforderlich, immutable Successor-Attempts ohne Reinvoke.
4. S005-Produkt-cpatch, Dry-run, Human Accept.
5. Trusted-Host-Version-/Sprint-Closure als separater Patch.

## Unsicherheiten und Entscheidungszeitpunkte

- Falls der vorhandene `process-ops run-start` die notwendige Durable-Worker-Semantik nicht ausreichend trägt, ist das ein Stop-/Replan-Punkt und keine implizite process-ops-Änderung.
- Falls cpatch-Promotion nicht ohne neue Autorität aus dem Orchestrator heraus steuerbar ist, endet der Automationsscope bei einem explizit dokumentierten Trusted-Step; ein automatischer Accept bleibt trotzdem verboten.
- Portabilitätsdetails für fremde Projektadapter werden in S006 entschieden; S005 darf keine Springmaster-only Hardcodings einführen, die diese Stufe verhindern.

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-08-25 | - | active | ADR-0019 und GOAL-006 in einen kontrollierten Implementierungsplan überführt. |

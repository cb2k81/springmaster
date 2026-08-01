---
documentId: TOOL-CODEX-PILOT-0001
title: Codex Pilot Pre-Cutover Operations Guide
documentType: guide
status: active
authority: informative
scopeLevel: component
scopePaths:
  - springmaster/engineering
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-07-25
validFrom: 2026-07-25
lastReviewedAt: 2026-08-01
reviewBy: 2027-01-25
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# Codex Pilot Pre-Cutover Operations Guide

## 1. Boundary

This guide covers preparation up to the first Codex calibration invocation. It does not authorize a writable Codex task.

Before cutover, repository changes continue through `bin/cpatch` and `bin/process-ops.sh`.

## 2. External roots

The operator chooses and provisions three absolute, pairwise distinct paths outside the Springmaster repository and Git common directory. The harness has no default and does not create them.

```bash
: "${COCONDO_WORKTREE_ROOT:?set an explicitly authorized existing directory}"
: "${COCONDO_AGENT_RUN_ROOT:?set an explicitly authorized existing directory}"
: "${COCONDO_ARTIFACT_ROOT:?set an explicitly authorized existing directory}"

test -d "${COCONDO_WORKTREE_ROOT}"
test -d "${COCONDO_AGENT_RUN_ROOT}"
test -d "${COCONDO_ARTIFACT_ROOT}"
```

Provisioning those directories is a separate operator action and must state its own effects. The validation command above reads the three configured paths and writes nothing.

## 3. Project readiness and operational hold

During patch qualification:

```bash
./bin/codex-pilot-ready.sh project --candidate --check
```

After the accepted patch is committed on the clean integration worktree:

```bash
./bin/codex-pilot-ready.sh project --live --check \
  --out-json patches/logs/validation/codex-pilot/codex-project-readiness.json \
  --out-text patches/logs/validation/codex-pilot/codex-project-readiness.txt
```

The committed readiness contract still reports the formal lifecycle result:

```text
CODEX_PILOT_READINESS=PROJECT_READY
NEXT_ACTION=CODEX_CALIBRATION
WRITABLE_CODEX_AUTHORIZED=false
```

For the current sprint, `NEXT_ACTION=CODEX_CALIBRATION` names the next lifecycle state; it is not an executable operator authorization. Tooling hardening `000201_springmaster_tooling_hardening_cut` is accepted. The current operational state is:

```text
FORMAL_REPOSITORY_READINESS=PROJECT_READY
NEXT_LIFECYCLE_STATE=CODEX_CALIBRATION
NEXT_ACTION=POST_ACCEPT_LIVE_READINESS_AND_HOST_QUALIFICATION
NEXT_ACTION_EXECUTABLE=true
NEXT_ACTION_BLOCKER=NONE
WRITABLE_CODEX_AUTHORIZED=false
PILOT_WRITE_READY=false
```

`000203_springmaster_codex_cutover_foundation` is canonically accepted and provides the repository-side confinement, host-qualification and calibration foundation at Platform `0.23.0-foundation` and Tooling `0.13.0`. Attempts `000197` through `000200` remain incident evidence only.

Live readiness must now be rerun with explicitly authorized existing roots against accepted commit `93ab563cc1e82bc801907399602fe04e6d37e2f7`. Host inspection and mechanical probes must then pass on the actual DEV system before the calibration task pack is materialized. `PROJECT_READY` does not mean `PILOT_WRITE_READY`.

## 4. Agent task preparation

Only after the operational hold above has been lifted, a calibration task is prepared from an immutable Task Contract V2. While the committed lifecycle is `PROJECT_READY`, `agent-task prepare` accepts only task files whose exact path and SHA-256 are registered in the sibling materialized `calibration-plan.json`:

```bash
./bin/agent-task.sh validate /absolute/path/to/task.json
./bin/agent-task.sh prepare /absolute/path/to/task.json
./bin/agent-task.sh status <task-id>
```

Preparation creates a detached worktree and run record outside the repository. It does not start Codex.

Before the manually started calibration run, the operator prepares two JSON files below the explicit `COCONDO_ARTIFACT_ROOT`:

- an operator-command-effect declaration according to `operator-command-effect.schema.json`;
- a Codex invocation record according to `codex-invocation-record.schema.json`.

After the invocation has completed, record both immutable inputs:

```bash
./bin/agent-task.sh record-invocation <task-id> \
  --effect "${COCONDO_ARTIFACT_ROOT:?}/<effect-file>.json" \
  --record "${COCONDO_ARTIFACT_ROOT:?}/<invocation-file>.json"
```

The effect declaration must make the operator-visible effects explicit:

```text
READS: prepared task worktree and explicitly declared read-only inputs
WRITES: none for analysis/qualification; prepared task worktree only for implementation
NETWORK: Codex control plane only; agent shell network disabled
REPOSITORY_MUTATION: none for analysis/qualification; detached task worktree only for implementation
DESTRUCTIVE_ACTIONS: none
DIRECTORY_CREATION: declared task paths only
OVERWRITE: declared task paths only
```


The immutable invocation evidence must show the safe non-interactive shape: `codex exec`, `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, `--json`, explicit `--model`, mode-specific `--sandbox` and `--ask-for-approval never`. Linux records identify `linux-bwrap-read-only` or `linux-bwrap-workspace-write`. `--add-dir`, user/profile configuration overrides, full-auto and sandbox-bypass flags are rejected.

The Codex process never receives write authority for the operator home, operator handoff or download directories, integration checkout, Git common directory, external run or artifact roots, other repositories or host temporary directories. A concrete local handoff path is operator configuration, never a portable agent capability. Copying an accepted artifact there is a separate explicit operator action after the Codex task has ended.

Then run postcheck and qualification:

```bash
./bin/agent-task.sh postcheck <task-id>
./bin/agent-task.sh qualify <task-id>
./bin/agent-task.sh status <task-id>
```

The harness still does not integrate the result.

## 5. Deliberate stop at cutover

`agent-task` has no `run-codex`, `commit`, `merge`, `push` or `integrate` command. `record-invocation` records an already completed explicit operator action; it does not execute Codex. The first invocation still requires a separate operator decision after an accepted tooling-hardening cut, fresh live project-readiness evidence, a newly generated task pack and review of the declared command effects.

## 6. Diagnostics

Operational reports intended for upload may be written below `patches/logs/validation/codex-pilot/`. This path is already ignored, excluded from full exports and classified as runtime diagnostics. Long-lived canonical run state remains below the external agent run root.

## 7. Failure handling

- Do not repair a failed task worktree manually before collecting evidence.
- Run `agent-task status` and `postcheck` first.
- Preserve the external run directory.
- Use explicit `cleanup --discard` only after the result is no longer needed.
- A boundary failure returns the pilot to patch-controlled hardening before another Codex attempt.

## 8. Patch-Handoff nach qualifizierter Implementierung

Eine qualifizierte Implementierungsaufgabe wird nicht direkt integriert. Der Operator erzeugt zunächst den unveränderlichen, nicht kanonischen Handoff:

```bash
./bin/agent-task.sh handoff <task-id>
./bin/agent-task.sh status <task-id>
```

Der Handoff liegt unter `${COCONDO_ARTIFACT_ROOT}/codex-handoffs/<task-id>/`, bindet den Base-Commit und die exakte Pfadmenge und besteht einen isolierten Apply-Check. Er enthält ausdrücklich keine Patch-ID und keine Delivery-ID.

Danach endet die Agentautorität. Der Operator übernimmt den Handoff in einen getrennten Candidate, committed dort den geprüften Scope und verwendet anschließend den normalen `cpatch`-Prozess mit getrenntem Dry-run und Accept.

## 9. Live-Confinement-Abnahme auf dem DEV-System

Die äußere Sandbox verwirft die geerbte Umgebung. Ihr `PATH` ist fest auf `/usr/local/bin:/usr/bin:/bin` gesetzt; der Operator- beziehungsweise Host-`PATH` wird nicht übernommen.

Vor `PILOT_WRITE_READY` müssen reale Codex-Aufrufe die Evidence nach `contracts/governance/agent/codex-confinement-contract.json` erzeugen. Der Abschluss wird ausschließlich aus einem externen Evidence-Root geprüft:

```bash
./bin/codex-confinement-check.sh verify \
  --evidence "${COCONDO_ARTIFACT_ROOT:?}/codex-confinement/<run-id>" \
  --live \
  --check
```

Erwarteter Zustand:

```text
CODEX_CONFINEMENT_STATUS=PASS
WRITABLE_CODEX_AUTHORIZED=false
PILOT_WRITE_READY=false
NEXT_ACTION=SEPARATE_PROMOTION_REVIEW
```

Ein Fixture-PASS ersetzt diesen Live-Lauf nicht. Die Negativproben müssen auf dem tatsächlichen DEV-System mit der real installierten Codex-CLI versucht worden sein.

## 10. Terminalschonende verkettete Abläufe

Ein fail-fast Operatorblock darf erfolgreiche Preflights direkt mit Taskvorbereitung, Invocation, Postcheck, Qualification, Handoff und leichter Statusbeobachtung verbinden. Er gibt nur Stage-Start, Stage-Result, IDs sowie Log-/Evidence-Pfade aus. Vollständige Logs und JSON-Inventare werden nicht in das interaktive Terminal gestreamt.

Nicht automatisch verbunden werden:

- Dry-run und Accept;
- Diagnose und Reparatur;
- fehlgeschlagener Run und Retry;
- Codex-Handoff und Candidate-Integration.

## 11. Portabler Host-Bootstrap und Kalibrierung

Die Repository-Foundation stellt folgende kanonische Entrypoints bereit:

```bash
./bin/codex-host-sandbox.sh inspect --out <inspect.json>
./bin/codex-host-sandbox.sh probe --task-worktree <prepared-worktree> --out <probe.json>
./bin/codex-host-sandbox.sh invoke --task-id <analysis-task-id> --prompt <prompt.txt> --model <model> --out <invocation.json>
./bin/codex-host-sandbox.sh qualify --inspect <inspect.json> --probe <probe.json> --analysis-invocation <invocation.json> --out <host-qualification.json> --check
./bin/codex-calibration.sh materialize --out <task-pack> --baseline <commit>
./bin/codex-calibration.sh assemble --manifest <assembly.json> --out <confinement-evidence>
```

`inspect`, `probe` und `invoke` müssen auf demselben Host und Baseline-Commit laufen. Die Host-Evidence ist nicht portabel. Die zwei Implementierungstasks werden erst nach Host-PASS vorbereitet, jeweils über `agent-task` qualifiziert und als nicht kanonischer Handoff übergeben. Dry-run und Accept bleiben getrennte Operatoraktionen.

Historische, inaktive Worktrees und alte Diagnosearchive werden nicht im Cutover-Foundation-Lauf bereinigt und sind kein Readiness-Blocker. Der Harness blockiert weiterhin aktive Runs, Locks, Pfadüberschneidungen und unklare Autorität.

## Lifecycle

| Date | Change |
|---|---|
| 2026-08-01 | Acceptance of `000203` reflected; next operator stage set to Post-Accept Live Readiness, host qualification and plan-bound calibration. |

## 12. Patch-ID-freies Change Bundle im Task-Worktree

Für eine ausdrücklich autorisierte Implementierungsaufgabe kann der Operator ein unveränderliches Bundle unter dem externen Artefakt-Root bereitstellen und beim realen Codex-Aufruf binden:

```bash
./bin/codex-host-sandbox.sh invoke \
  --task-id <task-id> \
  --prompt <prompt.txt> \
  --model <model> \
  --change-bundle "${COCONDO_ARTIFACT_ROOT:?}/codex-change-bundles/<bundle>.zip" \
  --out <invocation.json>
```

Der Prompt darf Codex anschließend ausschließlich zum folgenden Befehl anweisen:

```bash
./bin/codex-change-bundle.sh apply
```

Die Schnittstelle prüft den vorbereiteten Task Contract, den detached Base-Commit, den externen Artefakt-Root, alle Pfade, Source-/Target-Hashes und Modi, bevor sie Bytes im Task-Worktree ändert. Eine erneute Ausführung ist nur bei vollständig erreichtem Zielzustand idempotent. Gemischte oder gedriftete Zustände blockieren.

Das Bundle ersetzt weder Qualification noch Handoff. Insbesondere sind folgende Fähigkeiten nicht enthalten:

- Commit oder Branchänderung;
- Candidate- oder Integrationsmutation;
- Patch-/Delivery-ID-Vergabe;
- `cpatch create`;
- Patch-Dry-run;
- Patch-Accept.

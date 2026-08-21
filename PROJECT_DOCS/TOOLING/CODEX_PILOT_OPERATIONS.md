---
documentId: TOOL-CODEX-PILOT-0001
title: Codex Pilot Operations Guide
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
lastReviewedAt: 2026-08-14
reviewBy: 2027-01-25
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---
# Codex Pilot Operations Guide

## 1. Boundary

This guide covers governed Codex pilot operation on Springmaster before and after write promotion. The current repository lifecycle is `PILOT_WRITE_READY`/`PROMOTED` after the accepted cutover promotion `000218_codex-cutover-write-promotion` and final live qualification `CODEX_CUTOVER_ACCEPTED`.

Write promotion authorizes only task-contract-bound pilot work in harness-created detached task worktrees. It does not authorize direct writes to the integration checkout, patch acceptance by Codex, push, mutation of managed projects or bypass of the trusted operator integration path. The post-cutover operator baseline uses Cocondo Patch Toolkit `1.1.5` / Platform Tooling `0.14.2`; `000222_patch-toolkit-staged-path-parity` corrects rename-sensitive staged-path inventory without changing the promoted Codex authorization model or trusted operator boundary.

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

On the clean integration worktree:

```bash
./bin/codex-pilot-ready.sh project --live --check \
  --out-json patches/logs/validation/codex-pilot/codex-project-readiness.json \
  --out-text patches/logs/validation/codex-pilot/codex-project-readiness.txt
```

On an already registered host, the promoted contract reports:

```text
CODEX_PILOT_READINESS=PILOT_WRITE_READY
NEXT_ACTION=CODEX_PILOT_TASK
WRITABLE_CODEX_AUTHORIZED=true
HOST_WRITE_AUTHORIZED=true
PILOT_WRITE_READY=true
```

On a clean but not yet registered workstation, the same project lifecycle deliberately reports:

```text
CODEX_PILOT_READINESS=PILOT_WRITE_READY
NEXT_ACTION=CODEX_HOST_CALIBRATION
WRITABLE_CODEX_AUTHORIZED=false
HOST_WRITE_AUTHORIZED=false
PILOT_WRITE_READY=true
```

The second state is not a project regression. It means the repository is ready but this physical host still requires its own qualification and accepted promotion.

The source of truth is `contracts/governance/agent/codex-pilot-contract.json` version `1.8.0`. `pilot.currentLifecycle=PILOT_WRITE_READY`, `pilot.cutoverLifecycle=PROMOTED` and `writePromotion.decision=CODEX_CUTOVER_ACCEPTED`. The historical primary promotion remains registered in `writeAuthorizations`. The project lifecycle is global, while writable authorization is evaluated for the current host.

Historical `PROJECT_READY` and `CODEX_CALIBRATION` output remains relevant when reconstructing pre-promotion evidence or a new calibration attempt, but it is not the current operational state. A successful readiness result never grants authority outside the task contract and harness boundaries.

## 4. Agent task preparation

A post-promotion pilot task is prepared from an immutable Task Contract V2 after its scope, baseline, capabilities, qualification commands, evidence requirements and completion criteria have been reviewed:

```bash
./bin/agent-task.sh validate /absolute/path/to/task.json
./bin/agent-task.sh prepare /absolute/path/to/task.json
./bin/agent-task.sh status <task-id>
```

Preparation creates a detached worktree and run record outside the repository. It does not start Codex. Under global `PILOT_WRITE_READY`, regular pilot task contracts may be prepared only when the current host is present in the committed `writeAuthorizations` registry. The sibling `calibration-plan.json` byte-binding remains the fail-closed authorization rule for initial `PROJECT_READY` calibration; an unregistered post-promotion host uses the host-bound `springmaster.codex-calibration-plan.v2` requalification variant instead.

The governed host harness creates immutable operator-effect and invocation evidence for real Codex execution. When evidence must be recorded explicitly, `agent-task record-invocation` binds the already completed operator action; it never starts Codex itself.

The effect declaration must keep the operator-visible effects explicit:

```text
READS: prepared task worktree and explicitly declared read-only inputs
WRITES: none for analysis/qualification; prepared task worktree only for implementation
NETWORK: Codex control plane only; agent shell network disabled
REPOSITORY_MUTATION: none for analysis/qualification; detached task worktree only for implementation
DESTRUCTIVE_ACTIONS: none
DIRECTORY_CREATION: declared task paths only
OVERWRITE: declared task paths only
```

The Codex process never receives write authority for the operator home, operator handoff or download directories, integration checkout, Git common directory, external run or artifact roots, other repositories or host temporary directories. A concrete local handoff path is operator configuration, never a portable agent capability. Copying an accepted artifact there is a separate explicit operator action after the Codex task has ended.

Only after `codex-host-sandbox invoke` itself reports `PASS` may the operator run postcheck and qualification:

```bash
./bin/agent-task.sh postcheck <task-id>
./bin/agent-task.sh qualify <task-id>
./bin/agent-task.sh status <task-id>
```

`invoke=PASS` requires both raw Codex process exit `0` and a fail-closed validation of the complete JSONL event stream. Codex `error` items, `turn.failed`, malformed JSONL or incomplete command executions make the governed invocation fail even if the outer Codex process exits `0`. Analysis and qualification modes additionally require every terminal command execution to succeed with exit code `0`. Implementation mode deliberately treats terminal command failures/non-zero exits as iterative development evidence: they are counted in `commandExecutionFailedCount`, but they do not fail the invocation when the turn completes normally, no error event occurs, every started command terminates with an integer exit code, and the outer Codex process exits `0`. Implementation mode still requires at least one terminally completed `command_execution`. The validation record is immutable host evidence next to stdout/stderr.

The harness still does not integrate the result.

## 5. Deliberate stop at the integration boundary

`agent-task` has no `commit`, `merge`, `push`, `integrate` or patch-accept capability. A successful writable Codex task ends at qualification and, for implementation, at an immutable non-canonical handoff. Candidate integration, canonical patch creation, Dry-run and Accept remain separate trusted operator actions.

`PILOT_WRITE_READY` therefore removes the pre-cutover prohibition on regular governed pilot tasks; it does not collapse any integration or acceptance boundary.

## 6. Diagnostics

Operational reports intended for upload may be written below `patches/logs/validation/codex-pilot/`. This path is already ignored, excluded from full exports and classified as runtime diagnostics. Long-lived canonical run state remains below the external agent run root.

## 7. Failure handling

- Do not repair a failed task worktree manually before collecting evidence.
- Run `agent-task status` first and preserve the external run directory plus host invocation evidence.
- Run `postcheck` only when `codex-host-sandbox invoke` reported `PASS`. A failed governed invocation is disposed from its actual recorded state; do not advance it through postcheck or qualification merely to make cleanup possible.
- Use explicit `cleanup --discard` only after the result is no longer needed; a clean failed-invocation worktree may be terminalized through the normal incomplete-cleanup disposition while retaining evidence.
- A boundary or invocation-oracle failure returns the pilot to patch-controlled hardening before another Codex attempt.
- A failed real invocation is not retried under the same task ID. Retain its immutable invocation/JSONL evidence and clean the disposable worktree only after separate disposition. For calibration, materialize the next numbered attempt after any required hardening. For post-cutover feature work, create a new task contract and task ID only after the cause is classified and the baseline is revalidated.
- Host inspection must prove DNS and HTTPS reachability to the Codex control plane from the outer `bwrap` boundary before a new calibration attempt is materialized. If `/etc/resolv.conf` resolves below `/run`, the harness keeps `/run` private and copies only the resolver file into private scratch for read-only re-exposure at the original sandbox path.

### 7.1 Prepared task invalidated before Codex invocation

When `main` advances after `prepare`, the old task cannot pass postcheck against its recorded integration pre-state. If no Codex invocation has been recorded and the detached task worktree is still clean, terminalize the task without deleting its Evidence:

```bash
./bin/agent-task.sh abandon-before-invocation <task-id> \
  --reason integration-head-advanced
```

Expected status is `ABANDONED_BEFORE_INVOCATION`. The old task ID and run directory remain immutable. Materialize the replacement plan with a higher explicit attempt number:

```bash
./bin/codex-calibration.sh materialize \
  --out "${COCONDO_ARTIFACT_ROOT:?}/codex-calibration/<current-head>/A002" \
  --baseline "$(git rev-parse HEAD)" \
  --attempt 2
```

Do not manually remove or rebase the old worktree, do not reuse its Task ID and do not copy its active run state to another host. Codex still receives write access only to the newly prepared detached task worktree.

## 8. Patch-Handoff nach qualifizierter Implementierung

Eine qualifizierte Implementierungsaufgabe wird nicht direkt integriert. Der Operator erzeugt zunächst den unveränderlichen, nicht kanonischen Handoff:

```bash
./bin/agent-task.sh handoff <task-id>
./bin/agent-task.sh status <task-id>
```

Der Handoff liegt unter `${COCONDO_ARTIFACT_ROOT}/codex-handoffs/<task-id>/`, bindet den Base-Commit und die exakte Pfadmenge und besteht einen isolierten Apply-Check. Er enthält ausdrücklich keine Patch-ID und keine Delivery-ID.

Danach endet die Agentautorität. Der Operator übernimmt den Handoff in einen getrennten Candidate, committed dort den geprüften Scope und verwendet anschließend den normalen `cpatch`-Prozess mit getrenntem Dry-run und Accept.

## 9. Live-Confinement-Abnahme auf dem DEV-System

The cutover confinement acceptance was completed on the real DEV system with real Codex. Its immutable evidence remains part of the write-promotion basis and must not be rewritten or reinterpreted.

For historical or requalification use, the live verifier remains:

```bash
./bin/codex-confinement-check.sh verify \
  --evidence "${COCONDO_ARTIFACT_ROOT:?}/codex-confinement/<run-id>" \
  --live \
  --check
```

Before the accepted promotion, a confinement PASS intentionally still reported:

```text
CODEX_CONFINEMENT_STATUS=PASS
WRITABLE_CODEX_AUTHORIZED=false
PILOT_WRITE_READY=false
NEXT_ACTION=SEPARATE_PROMOTION_REVIEW
```

That output describes the confinement evidence boundary, not the current promoted repository lifecycle. The current authorization is established only by the separate accepted promotion and the live project-readiness contract. Host or baseline changes that invalidate required evidence must be requalified fail-closed before a new writable task proceeds.

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
./bin/codex-calibration.sh materialize --out <task-pack> --baseline <commit> --attempt <n> --host-requalification
./bin/codex-calibration.sh assemble --manifest <assembly.json> --out <confinement-evidence>
```

`inspect`, `probe` und `invoke` müssen auf demselben Host und Baseline-Commit laufen. Die Host-Evidence ist nicht portabel. `inspect` bindet zusätzlich die erfolgreich capability-geprobte Codex-Sandbox-Command-Form; nur die im Host-Qualification-Contract gelisteten Formen sind zulässig.

Für einen zusätzlichen Desktop oder Laptop wird `--host-requalification` verwendet. Der Plan bindet die aktuelle Host-ID und erzeugt zwei host-/attempt-spezifische unveränderliche Change Bundles für die Implementierungs-Canaries. Die zwei Implementierungstasks werden erst nach Host-PASS vorbereitet, jeweils über `agent-task` qualifiziert und als nicht kanonischer Handoff übergeben. Jeder Handoff durchläuft separat Candidate, Dry-run und Accept. Erst ein weiterer Trusted-Operator-Promotion-Schnitt darf den Host zur Registry hinzufügen; derselbe Promotion-Schnitt entfernt die temporären Canary-Dateien aus dem aktuellen Tree.

Eine Host-Promotion ist additiv. Sie darf vorhandene `writeAuthorizations` weder ersetzen noch deren Evidence auf den neuen Host übertragen. Desktop und Laptop benötigen daher jeweils eigene Qualification- und Promotion-Evidence.

Historische, inaktive Worktrees und alte Diagnosearchive werden nicht im Cutover-Foundation-Lauf bereinigt und sind kein Readiness-Blocker. Der Harness blockiert weiterhin aktive Runs, Locks, Pfadüberschneidungen und unklare Autorität.

## Lifecycle

| Date | Change |
|---|---|
| 2026-08-01 | Acceptance of `000203` reflected; next operator stage set to Post-Accept Live Readiness, host qualification and plan-bound calibration. |
| 2026-08-13 | Cutover completed; current lifecycle is `PILOT_WRITE_READY`/`PROMOTED`, regular governed pilot tasks are allowed while integration and accept boundaries remain trusted-operator-only. |
| 2026-08-14 | Post-cutover operator tooling advanced to Toolkit `1.1.4` / Tooling `0.14.1` through `000219`; governed Codex lifecycle and trusted integration boundaries are unchanged. |
| 2026-08-17 | Multi-host authorization model added: global project readiness is separated from host-local write authorization; additional hosts use host-bound requalification and separate additive promotion. |
| 2026-08-14 | Staged-path inventory advanced to Toolkit `1.1.5` / Tooling `0.14.2` through `000222`; exact manifest parity and trusted integration boundaries remain unchanged. |
| 2026-08-20 | Durable autonomous invocation added: `invoke-start` delegates to `process-ops`/`crun`, records `STARTED` before Codex launch, streams evidence, and uses suspend-aware active-time budgets without widening sandbox authority. |

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
## Private Codex home permission-profile hardening

The host harness owns the complete ephemeral private `CODEX_HOME` used by governed Codex invocations. It copies only the required credential and generates the only active runtime configuration. Analysis and qualification extend `:read-only`; implementation extends `:workspace`; nested sandbox commands receive an explicit deny rule for `/run/codex-home/auth.json`.

A governed real invocation therefore must not suppress the harness configuration with `--ignore-user-config` and must not replace it through legacy `--sandbox`/`-s`, direct `--permission-profile`/`-P`, `--config`/`-c` or `--profile`/`-p` overrides. The outer Linux bubblewrap boundary remains authoritative for host confinement; the generated Permission Profile is defense in depth and credential confinement. The 20 live mechanical probe expectations remain unchanged.

The calibration fixture checker is bound to the exact versioned instruction fixtures and accepts each task independently in either its untouched baseline state or its exact `CALIBRATION_TASK_n=PASS` target state. This is required because both implementation tasks are qualified separately against the same A001 baseline before either handoff is canonically accepted.

## Deterministic host-requalification plan input

For `CODEX-HOSTCAL-ANALYSIS-*`, the sibling host-requalification plan is not discovered by the agent. `agent-task prepare` records `calibrationPlanPath` and `calibrationPlanSha256`; `codex-host-sandbox invoke` revalidates them and binds the exact file read-only to `/run/codex-input/calibration-plan.json`. The sandbox environment contains `SPRINGMASTER_CODEX_CALIBRATION_PLAN` with exactly that value. The prompt must read this input directly and must not search other repository, worktree, home, temporary or host filesystem locations for calibration plans.

## 13. Durable autonomous Codex invocation

For autonomous tasks that can outlive an observer terminal or a host suspend/resume cycle, the canonical start operation is `invoke-start`, not the foreground compatibility `invoke`:

```bash
./bin/codex-host-sandbox.sh invoke-start \
  --task-id <task-id> \
  --prompt <prompt.txt> \
  --model <model> \
  --active-timeout-seconds 21600 \
  --no-progress-timeout-seconds 3600 \
  --out <durable-start.json>
```

`invoke-start` delegates process ownership to `process-ops run-start` with a stable task-derived singleton key. The returned `processRunId` is the canonical observer handle. A second start with the identical immutable request reuses the same active or terminal run; a conflicting request fails closed. Never pass `--restart-terminal` for an agent task and never automatically allocate a second Codex process after a terminal invocation.

Observe or reconnect without affecting the worker:

```bash
./bin/process-ops.sh status <processRunId>
./bin/process-ops.sh watch <processRunId>
./bin/process-ops.sh result <processRunId> --verbose
```

Closing the observer terminal or suspending the VM does not authorize a retry. After resume, use the same `processRunId`. `stdout` is streamed as `codex.stdout.jsonl`, `stderr` as `codex.stderr.log`, and `heartbeat.json` is atomically replaced below the task's external invocation-evidence directory. The heartbeat records active elapsed time, excluded scheduling/suspend gaps, byte counts, worktree progress, process IDs, boot ID, and last progress.

The agent-task invocation lifecycle is:

```text
NOT_RECORDED -> STARTED -> RECORDED
```

`STARTED` is persisted before the real Codex process is launched. Therefore an actually attempted invocation can no longer be treated as an uninvoked prepared task. `abandon-before-invocation` is allowed only from `NOT_RECORDED`. Timeouts, signals, non-zero Codex exits and governed JSONL failures retain start, stream, heartbeat and terminal invocation evidence and do not trigger automatic reinvocation.

The default autonomous budget is six hours of credited active time. Large gaps between heartbeat ticks receive only the bounded active-time credit declared by the host qualification contract; the remainder is excluded. The optional no-progress budget is measured on the same active clock. No operating procedure may require disabling host/VM suspend or changing user power-management settings.

The foreground `invoke` command remains for bounded compatibility and calibration flows, but it uses the same start-evidence, streaming, heartbeat and active-time semantics. The Bubblewrap, Codex permission-profile, external-root, integration-worktree, Git and trusted-operator boundaries remain unchanged.
## Recovery-Preservation für historisch gestartete, nicht aufgezeichnete Invocations

Wenn ein älterer Harness einen real gestarteten Codex-Prozess wegen eines Host-Timeouts nicht als Invocation aufgezeichnet hat, darf der betroffene Task nicht erneut invoked werden. Ist sein detached Worktree zugleich ein benötigter Recovery-Seed, wird er mit `agent-task preserve-recovery` terminalisiert, ohne Worktree oder Evidence zu löschen.

Der Befehl ist ausschließlich für `PREPARED / NOT_RECORDED` zulässig, verlangt einen dirty Worktree am unveränderten Task-Base, einen inzwischen fortgeschrittenen sauberen Integrations-HEAD, die erwartete Changed-Path-Anzahl und eine externe Dossier-SHA-256-Bindung. Ergebnis ist `RECOVERY_PRESERVED_INCOMPLETE` mit `reinvocationAllowed=false`, persistentem Worktree-Fingerprint und `newAttemptRequired=true`. Dieser Terminalzustand zählt nicht mehr als aktiver Pilot-Task und erlaubt dadurch den expliziten Nachfolge-Attempt.

`cleanup` ist für `RECOVERY_PRESERVED_INCOMPLETE` fail-closed verboten, damit der Recovery-Worktree nicht versehentlich entfernt wird.

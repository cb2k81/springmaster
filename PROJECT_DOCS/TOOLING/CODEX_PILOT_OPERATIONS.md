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

The promoted contract reports:

```text
CODEX_PILOT_READINESS=PILOT_WRITE_READY
NEXT_ACTION=CODEX_PILOT_TASK
WRITABLE_CODEX_AUTHORIZED=true
PILOT_WRITE_READY=true
```

The source of truth is `contracts/governance/agent/codex-pilot-contract.json` version `1.7.0`. `pilot.currentLifecycle=PILOT_WRITE_READY`, `pilot.cutoverLifecycle=PROMOTED` and `writePromotion.decision=CODEX_CUTOVER_ACCEPTED`. The promotion was accepted only after two independent A003 calibration patches and live confinement evidence.

Historical `PROJECT_READY` and `CODEX_CALIBRATION` output remains relevant when reconstructing pre-promotion evidence or a new calibration attempt, but it is not the current operational state. A successful readiness result never grants authority outside the task contract and harness boundaries.

## 4. Agent task preparation

A post-promotion pilot task is prepared from an immutable Task Contract V2 after its scope, baseline, capabilities, qualification commands, evidence requirements and completion criteria have been reviewed:

```bash
./bin/agent-task.sh validate /absolute/path/to/task.json
./bin/agent-task.sh prepare /absolute/path/to/task.json
./bin/agent-task.sh status <task-id>
```

Preparation creates a detached worktree and run record outside the repository. It does not start Codex. Under `PILOT_WRITE_READY`, regular pilot task contracts may be prepared according to the contract and scope rules. The sibling `calibration-plan.json` byte-binding remains the special fail-closed authorization rule for the pre-promotion `PROJECT_READY` lifecycle and for calibration reconstruction.

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

After the invocation, run postcheck and qualification:

```bash
./bin/agent-task.sh postcheck <task-id>
./bin/agent-task.sh qualify <task-id>
./bin/agent-task.sh status <task-id>
```

The harness still does not integrate the result.

## 5. Deliberate stop at the integration boundary

`agent-task` has no `commit`, `merge`, `push`, `integrate` or patch-accept capability. A successful writable Codex task ends at qualification and, for implementation, at an immutable non-canonical handoff. Candidate integration, canonical patch creation, Dry-run and Accept remain separate trusted operator actions.

`PILOT_WRITE_READY` therefore removes the pre-cutover prohibition on regular governed pilot tasks; it does not collapse any integration or acceptance boundary.

## 6. Diagnostics

Operational reports intended for upload may be written below `patches/logs/validation/codex-pilot/`. This path is already ignored, excluded from full exports and classified as runtime diagnostics. Long-lived canonical run state remains below the external agent run root.

## 7. Failure handling

- Do not repair a failed task worktree manually before collecting evidence.
- Run `agent-task status` and `postcheck` first.
- Preserve the external run directory.
- Use explicit `cleanup --discard` only after the result is no longer needed.
- A boundary failure returns the pilot to patch-controlled hardening before another Codex attempt.
- A failed real invocation is not retried under the same task ID. Run `postcheck`, retain the failure evidence and clean the disposable worktree only after disposition. For calibration, materialize the next numbered attempt after any required hardening. For post-cutover feature work, create a new task contract and task ID only after the cause is classified and the baseline is revalidated.
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
./bin/codex-calibration.sh assemble --manifest <assembly.json> --out <confinement-evidence>
```

`inspect`, `probe` und `invoke` müssen auf demselben Host und Baseline-Commit laufen. Die Host-Evidence ist nicht portabel. Die zwei Implementierungstasks werden erst nach Host-PASS vorbereitet, jeweils über `agent-task` qualifiziert und als nicht kanonischer Handoff übergeben. Dry-run und Accept bleiben getrennte Operatoraktionen.

Historische, inaktive Worktrees und alte Diagnosearchive werden nicht im Cutover-Foundation-Lauf bereinigt und sind kein Readiness-Blocker. Der Harness blockiert weiterhin aktive Runs, Locks, Pfadüberschneidungen und unklare Autorität.

## Lifecycle

| Date | Change |
|---|---|
| 2026-08-01 | Acceptance of `000203` reflected; next operator stage set to Post-Accept Live Readiness, host qualification and plan-bound calibration. |
| 2026-08-13 | Cutover completed; current lifecycle is `PILOT_WRITE_READY`/`PROMOTED`, regular governed pilot tasks are allowed while integration and accept boundaries remain trusted-operator-only. |
| 2026-08-14 | Post-cutover operator tooling advanced to Toolkit `1.1.4` / Tooling `0.14.1` through `000219`; governed Codex lifecycle and trusted integration boundaries are unchanged. |
| 2026-08-14 | Staged-path inventory advanced to Toolkit `1.1.5` / Tooling `0.14.2` through `000222`; exact manifest parity and trusted integration boundaries remain unchanged. |

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

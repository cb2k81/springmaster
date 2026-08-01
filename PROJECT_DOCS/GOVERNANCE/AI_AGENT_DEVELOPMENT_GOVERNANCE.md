---
documentId: DOC-GOV-0010
title: AI Agent Development Governance
documentType: governance
status: active
authority: normative
scope: repository
scopeLevel: ecosystem
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
# AI Agent Development Governance

## 1. Purpose and scope

This governance defines the controlled local AI-agent development lifecycle for the Springmaster pilot. It applies to analysis, implementation, qualification and review performed with Codex or an equivalent local coding agent.

It does not authorize AI-agent use in GWC, Personnel, generated projects or managed projects. Such adoption requires a separate decision and delivery profile after the Springmaster pilot is completed.

## 2. Canonical boundaries

This governance is canonical for:

- pilot lifecycle and cutover status;
- task-contract requirements;
- agent worktree, run and evidence boundaries;
- separation of input, oracle, implementation and generated result;
- prohibited agent actions;
- calibration, stop and success criteria.

The following sources remain canonical for their existing subjects:

| Subject | Canonical source |
|---|---|
| technical change lifecycle and evidence | Engineering Governance and its report-only contracts |
| Git patch transactions before cutover | ADR-0012 and Cocondo Patch Toolkit contracts |
| process observation and recovery | ADR-0014 and Process Operations Guide |
| API, persistence, security and architecture rules | accepted ADRs and active technical standards |
| test and gate semantics | Test Governance, Quality Gate Governance and their report-only contracts |
| directory and artifact placement | Project Directory Governance and directory contract |

If these sources conflict, the conflict is resolved before the task starts. An agent must not choose a rule silently.

## 3. Pilot lifecycle

### 3.1 PRE_CUTOVER

In `PRE_CUTOVER`:

- Codex execution is forbidden;
- Springmaster changes are delivered through Cocondo Patch Toolkit;
- governance, contracts, harness and reference inputs are implemented and qualified;
- the readiness gate may be run in candidate mode during patch qualification and live mode after integration.

### 3.2 PROJECT_READY

`PROJECT_READY` means all repository-owned prerequisites are proven:

- ADR-0015 is accepted;
- this governance is active;
- pilot and task contracts are valid;
- the agent-task harness and negative fixtures pass;
- the Business Partner pilot input and acceptance contract are frozen;
- pre-cutover mutation remains bound to Cocondo Patch Toolkit;
- the cutover command is still disabled.

This state authorizes only the controlled Codex calibration boundary.

### 3.3 CALIBRATION_REQUIRED

The first Codex activity is not feature development. It consists of:

1. a read-only source and rule audit;
2. a negative boundary calibration in a disposable task worktree;
3. a small implementation task with immutable human-provided oracle;
4. a small generator or validator task with a separately reviewed golden result.

Writable pilot tasks remain blocked until both calibration implementation tasks are accepted and every negative probe is correctly blocked or contained.

### 3.4 PILOT_WRITE_READY

The state may be promoted only by a separate committed change that references immutable calibration evidence. The promotion must not be performed by the Codex task being evaluated.

### 3.5 PILOT_COMPLETED

Completion requires the end-to-end Business Partner chain, three clean deterministic reruns, a controlled V1.1 concept change, preserved manual extension points, complete traceability and measured efficiency improvement without a safety regression.

## 4. Task contract and semantic enforcement

Every agent task must be defined before worktree creation. The task contract is immutable for the lifetime of the task and contains at least:

- `taskId`, pilot ID, repository ID and mode;
- exact `baseCommit` and integration branch;
- risk class and change classes;
- allowed paths and forbidden paths;
- maximum changed file count and maximum net added bytes relative to the exact base commit;
- explicit booleans for test, governance, contract, commit, push and network capabilities;
- exact qualification commands as argument arrays;
- required evidence and machine-evaluable completion criteria.

The task contract is stored in the external run root. It is never generated or rewritten inside the task worktree.

A material scope change ends the current task. A new task contract and worktree are required.

Task Contract V2 enforces the declared semantics:

- `analysis` and `qualification` are non-mutating modes. Both require zero change limits and fail when any changed path is detected;
- `implementation` may change only declared paths and remains subject to explicit capability flags;
- risk classes determine mandatory qualification command IDs;
- change classes are closed and add their own mandatory qualification command IDs;
- `critical` implementation tasks are forbidden during calibration;
- enabled test, governance and contract capabilities require the matching change class;
- the required evidence set is closed and evaluated before qualification completion and again after cleanup;
- completion requires a passing postcheck, all qualification commands, complete invocation evidence and an explicit cleanup disposition.

### 4.1 Compatibility decision

Task Contract V2 is an intentional incompatible pilot-contract revision. V1 tasks are rejected rather than migrated implicitly because they do not declare the closed evidence set, machine-evaluable completion criteria, risk-driven qualification or the corrected net-added-byte limit. The pilot is still pre-write and has no accepted V1 task history that requires an upgrade path. This governance decision authorizes the corresponding Springmaster and Tooling minor-version increments.

## 5. Filesystem and Git boundaries

1. The integration worktree must be clean before task preparation.
2. The task worktree is detached at the exact base commit.
3. The worktree, run and artifact roots must be explicitly provisioned before the task starts, writable, pairwise distinct and outside the repository and Git common directory. The harness validates them and never creates these roots implicitly.
4. Symbolic links in changed paths are forbidden.
5. `.git` mutation, submodule introduction and nested repository creation are forbidden.
6. Root-level writes are forbidden unless the exact root path is allowed in the task contract.
7. The task must not change its own base commit or create a commit unless a later governance revision explicitly enables it. Pilot V1 sets `mayCommit=false`.
8. Integration `HEAD`, branch and working tree are rechecked after the task.
9. Cleanup never discards a non-empty task worktree implicitly. A review bundle or explicit discard decision is required.

## 6. Command, invocation and network boundaries

- Qualification commands are exact argument arrays from the task contract. Shell strings and implicit evaluation are forbidden.
- The harness does not offer a generic arbitrary-command operation.
- Every generated operator command with host effects follows `PROJECT_DOCS/TOOLING/OPERATOR_COMMAND_EFFECT_CONTRACT.md`. Manual execution does not authorize undisclosed writes, directory creation, overwrite, network use or repository mutation.
- Codex execution remains an explicit operator action. Before qualification, `agent-task record-invocation` stores an immutable operator-command-effect declaration and Codex invocation record from the external artifact root into the external run root.
- The invocation record binds task ID, exact argument array, working directory, Codex CLI version, model, sandbox profile, approval policy, environment-key allowlist, timestamps, exit status and exit code.
- The operator-command-effect declaration is mode-specific: `analysis` and `qualification` declare no write scope and no repository mutation; `implementation` declares only `task-worktree` and `task-worktree-only`. It may not declare destructive actions, external directory creation or integration-repository mutation.
- Codex runs non-interactively through `codex exec` with ephemeral state, ignored user configuration and repository rules, JSON event output, approval policy `never` and a mode-specific sandbox (`read-only` or `workspace-write`). The model is an explicit argument and part of immutable evidence.
- Linux calibration requires the platform sandbox implementation `bwrap`. Additional writable directories, `--add-dir`, profile/config overrides, full-auto and all sandbox-bypass flags are forbidden.
- The operator home, `Downloads`, integration worktree, Git common directory, external run root, external artifact root, other repositories and host temporary directories are unconditional agent write denials. An operator declaration cannot grant these scopes to Codex. Handoff or publication is a separate trusted operator action outside the agent lifecycle.
- Codex shell network access is disabled during the pilot. Network-dependent dependency installation is a separate human-controlled preparation step and is not part of an agent task.
- Push, remote mutation, branch creation, destructive integration-tree Git commands and credential acquisition are forbidden.
- Codex approvals do not replace these boundaries. A request to escape them is a blocked result, not an invitation to approve.

## 7. Evidence

The external run root contains at least:

- immutable task contract and its SHA-256;
- preparation record;
- integration and task-worktree pre-state;
- operator-command-effect declaration and SHA-256;
- Codex invocation record and SHA-256;
- changed-path and post-state report;
- qualification command records and bounded logs;
- final result and cleanup disposition.

Evidence records use deterministic JSON with UTC timestamps only for event identity. Hash comparison excludes or normalizes volatile timestamps.

No agent evidence, prompt, checksum, run record or generated application is written to the repository root.

## 8. Separation of responsibilities

One task may not simultaneously change:

- Fachkonzept and the implementation derived from it;
- generator and all of its expected outputs without an independent oracle review;
- governance boundary and code relying on the relaxed boundary;
- task harness and its own acceptance evidence;
- implementation and the acceptance criteria used to judge it, unless test modification is explicitly authorized and independently reviewed.

Human approval is mandatory for:

- the frozen Fachkonzept;
- the Application UI Spec before application generation;
- calibration acceptance;
- integration of any writable Codex result;
- promotion to `PILOT_WRITE_READY` and `PILOT_COMPLETED`.

## 9. Business Partner reference input

The active pilot Fachkonzept is `PROJECT_DOCS/DEMO/BUSINESS_PARTNER_CODEX_PILOT_FACHKONZEPT.md`. Its machine-readable acceptance contract is `contracts/pilots/codex/business-partner-pilot-acceptance.json`.

The existing `GENERATED_SLICE_SPEC_GOLDEN_BUSINESS_PARTNER.yaml`, IR and patch blueprint remain technical golden fixtures. They are useful comparison inputs but are not the source of business truth and do not authorize source rendering or target mutation.

## 10. Stop criteria

The pilot stops and returns to `PRE_CUTOVER` or a blocked state when any of the following occurs:

- a Codex write outside the task worktree, including operator home, `Downloads`, integration worktree, Git common directory, external run or artifact roots, other repositories or host temporary directories;
- integration-worktree mutation or drift;
- another repository is modified;
- an unauthorized network operation succeeds;
- the task contract or evidence is changed by the agent;
- a forbidden path is changed;
- a missing run record, ambiguous result or non-reproducible clean rerun;
- a manual repository repair is required after a run;
- an agent changes the oracle to make its implementation pass without explicit authorization.

The incident is retained outside the repository and addressed through a new patch-controlled hardening change.

## 11. Success measures

Safety targets are absolute:

- zero writes outside the task worktree;
- zero changes to other repositories;
- zero direct agent changes to `main`;
- zero unauthorized commands or network operations;
- zero undeclared changed files;
- zero new repository-root artifacts;
- complete evidence for every task;
- zero manual repository cleanup actions.

After at least five writable pilot tasks, the efficiency targets are:

- at least 30 percent lower elapsed time to a reviewable diff;
- at least 80 percent fewer manual transfer and patch-rebuild steps;
- at least 50 percent fewer manual interventions;
- median review correction rounds not greater than one;
- at least 70 percent first-pass targeted qualification success.

Efficiency never compensates for a safety failure.

## 12. Rollout boundary

This governance has no automatic Project-New or managed-project effect. Later rollout requires:

- a completed Springmaster pilot report;
- a versioned reduced adoption profile;
- target read-only comparison;
- disposable target acceptance;
- explicit authorization for each real target mutation.

## 14. Codex-Live-Confinement und Patch-Handoff

### 14.1 Getrennte Betriebsarten

Der Online-Chat und ein lokaler Codex-Run verwenden dieselbe Patch-Governance, aber unterschiedliche Handoff-Kanäle:

- Der Online-Chat liefert vorverifizierte Patchpakete und kann bei einem unklaren DEV-Zustand genau ein aktuelles Diagnosearchiv unter `patches/work/diagnostic-<operation-id>.zip` anfordern.
- Codex darf `patches/work` weder lesen noch schreiben. Seine Verträge, Invocation-Records, Logs und Resultate liegen ausschließlich unter den explizit provisionierten externen Run- und Artefakt-Roots.

### 14.2 Technische Schreibgrenze

Codex erhält nur Schreibrechte im vorbereiteten detached Task-Worktree. Folgende Bereiche bleiben hostseitig schreibgeschützt und werden durch reale Negativproben geprüft:

- Projekt- und Integrations-Checkout;
- andere Worktrees und Repositories;
- Git-Common-Verzeichnis;
- `patches/work`, Operator-Home und Downloads;
- externe Run- und Artefakt-Roots;
- Host-Temp und Pfade außerhalb des Task-Worktrees.

Ein Promptverbot ist keine ausreichende Kontrolle. Der tatsächliche Versuch muss auf dem DEV-System technisch scheitern oder der gesamte Task muss fail-closed verworfen werden.

### 14.3 Nicht kanonischer Patch-Handoff

Nach `QUALIFIED` darf nur der vertrauenswürdige Harness-Befehl `agent-task handoff` für Implementierungsaufgaben einen binären Git-Diff erzeugen. Der Handoff:

- bindet Task-ID, Base-Commit, Pfadmenge, Datei-Hashes und Patch-SHA-256;
- besteht einen isolierten Apply-Check;
- enthält weder Patch-ID noch Delivery-ID;
- besitzt keine Commit-, Integrations- oder Accept-Autorität;
- ist kein kanonisches Patchartefakt.

Der Handoff wird anschließend durch einen getrennten Operatorprozess in einen Candidate übernommen. Erst aus committed Candidate-Refs darf `cpatch create` das kanonische Artefakt erzeugen. Dry-run und Accept bleiben getrennte Operatorentscheidungen.

### 14.4 Prepare-Autorisierung vor der Promotion

Solange der committed Pilot-Lifecycle `PROJECT_READY` ist, darf `agent-task prepare` ausschließlich Taskverträge akzeptieren, die bytegenau in einem unmittelbar benachbarten, materialisierten `calibration-plan.json` registriert sind. Task-ID, Modus, Baseline, relativer Dateipfad und SHA-256 müssen übereinstimmen. Ein beliebiger formal gültiger Task Contract ohne diese Bindung wird fail-closed abgelehnt.

Nach einer separaten committed Promotion zu `PILOT_WRITE_READY` darf der Harness reguläre Pilot-Tasks gemäß Task Contract, Scope- und Qualification-Regeln vorbereiten. Ein unbekannter Lifecycle autorisiert keine Taskvorbereitung. Die reine Operation `agent-task validate` bleibt eine statische Vertragsprüfung und ist keine Ausführungsfreigabe.

### 14.5 Live-Abnahme und Promotion

Vor jeder Umstellung auf schreibende Codex-Entwicklung muss `codex-confinement-check --live --check` auf dem tatsächlichen DEV-System mit realem Codex bestehen. Die Evidence umfasst alle verpflichtenden Denial-Probes, zwei unabhängige qualifizierte Implementierungsaufgaben mit Patch-Handoff, getrennte Dry-runs sowie unveränderten Integration- und Git-Common-Zustand.

Ein PASS autorisiert keine automatische Promotion. Bis zu einem separaten akzeptierten Promotion-Schnitt bleiben:

```text
WRITABLE_CODEX_AUTHORIZED=false
PILOT_WRITE_READY=false
DIRECT_CODEX_INTEGRATION_WRITE=false
CODEX_PATCH_ACCEPT_AUTHORIZED=false
```


## 15. Lifecycle

| Date | Previous | New | Reason |
|---|---|---|---|
| 2026-07-27 | - | active | Mode-specific Codex sandbox, exact safe invocation shape and unconditional operator-home/Downloads write denial added; handoff remains a separate trusted operator action. |
| 2026-07-25 | - | active | Springmaster-only pre-cutover governance, strict project-readiness boundary and Codex calibration lifecycle established. |
| 2026-07-27 | active | active | Task Contract V2, explicit-root behavior, operator-effect declaration, immutable invocation evidence and fail-closed task semantics added. |
| 2026-07-30 | active | active | Live Codex confinement, immutable patch handoff and separate promotion boundary added. |
| 2026-07-31 | active | active | `agent-task prepare` vor `PILOT_WRITE_READY` an den materialisierten Calibration Plan gebunden. |
| 2026-08-01 | active | active | Acceptance von `000203` reflektiert; plan-gebundene Kalibrierung bleibt von regulärer Write-Promotion getrennt. |

## 16. Portabler Hostvertrag und minimaler Cutover-Pfad

Springmaster verteilt über Git die ausführbaren Verträge, nicht die Freigabe eines Rechners. Jeder Host erzeugt eigene, nicht portable Evidence für Betriebssystem, Architektur, Codex-Version, Bubblewrap-Profil, Root-Auflösung und reale Probe-Ergebnisse.

Die technische Grenze ist zweischichtig:

1. `bin/codex-host-sandbox.sh` erzwingt über eine äußere Linux-Bubblewrap-Sandbox ausschließlich den Task-Worktree als modeabhängig schreibbaren Root und blendet beziehungsweise schützt Integration, Git-common, andere Worktrees, Operator-Home, Downloads, `patches/work`, externe Run-/Artefakt-Roots und Host-Temp.
2. Codex läuft zusätzlich mit `read-only` beziehungsweise `workspace-write`, `--ask-for-approval never` und ohne zusätzliche Write-Roots.

Der minimale Cutover-Pfad besteht aus Host-Inspection, 20 mechanischen Grenzproben, einem realen read-only Codex-Lauf, zwei unabhängigen Implementierungsaufgaben mit unveränderlichem Patch-Handoff, je einem getrennten kanonischen Dry-run und Accept sowie einer nachgelagerten Evidence-Prüfung. Erst ein weiterer akzeptierter Promotion-Schnitt darf die Hostfreigabe aktivieren.

Sekundäre Aufräumarbeiten an inaktiven Worktrees, historischen Diagnosearchiven, Exportkomfort oder Terminaldarstellung liegen außerhalb dieses kritischen Pfads, sofern sie keinen aktiven Writer, Lock, Scope-Konflikt oder Sicherheitsbefund darstellen.

## 17. Unveränderliche Codex Change Bundles

Ein Codex Change Bundle ist ein nicht kanonisches, patch-ID-freies Eingabeartefakt für genau eine vorbereitete Implementierungsaufgabe. Es darf ausschließlich über `bin/codex-change-bundle.sh apply` im detached Task-Worktree materialisiert werden.

Das Bundle:

- liegt read-only unter dem externen Artefakt-Root;
- bindet Task-ID, Repository-ID und exakten Base-Commit;
- enthält ausschließlich deklarative Dateioperationen mit Source-/Target-SHA-256 und Git-Modus;
- muss vollständig innerhalb der `allowedPaths` des unveränderlichen Task Contracts liegen;
- enthält keine Kommandos, Patch-ID, Delivery-ID oder Accept-Autorität;
- darf weder Integration, Git-common, `patches/work`, andere Worktrees noch externe Evidence verändern.

`codex-host-sandbox invoke --change-bundle <bundle.zip>` stellt ausschließlich die Bundle- und Task-Contract-Pfade als read-only Umgebungswerte bereit. Auch nach erfolgreicher Anwendung bleiben Postcheck, Qualification, `agent-task handoff`, kontrollierte Candidate-Anwendung, `cpatch create`, separater Dry-run und separater Accept zwingend.

Ein Change Bundle autorisiert keine schreibende Codex-Ausführung. Vor `PILOT_WRITE_READY` sind weiterhin nur die ausdrücklich freigegebenen Kalibrierungsaufgaben zulässig.

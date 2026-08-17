---
documentId: ADR-0016
title: Host-Local Multi-Host Codex Authorization

documentType: adr
status: accepted
authority: normative
scopeLevel: ecosystem
scopePaths:
  - springmaster/engineering
  - springmaster/standards/build-tooling
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-17
validFrom: 2026-08-17
lastReviewedAt: 2026-08-17
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: SPRINT-003
---
# ADR-0016 Host-Local Multi-Host Codex Authorization

## Context

ADR-0015 established that Codex write authority is proven by host-local confinement evidence and is activated only by a separate accepted promotion. The first cutover encoded that promotion as one `writePromotion.hostId`. After the project reached `PILOT_WRITE_READY`, this single-host representation created two safety and operability gaps:

1. a second independently qualified workstation could not be added without conceptually replacing the first promoted host; and
2. `agent-task prepare` treated the global `PILOT_WRITE_READY` lifecycle as sufficient authorization and did not independently verify that the current host had been promoted.

Springmaster must support normal development from more than one workstation without making host evidence portable. The repository also has to tolerate compatible Codex CLI generations whose inner-sandbox command surface differs, while keeping the outer Bubblewrap boundary authoritative and fail-closed.

## Decision

1. `PILOT_WRITE_READY` remains a repository-wide project lifecycle. It means the project and harness are ready for governed writable Codex use, not that every machine is authorized to write.
2. Writable Codex authorization is host-local and is represented by an explicit `writeAuthorizations` registry in the committed pilot contract. The historical `writePromotion` remains the primary cutover evidence and must remain an active registry entry.
3. Each registry entry is an independently accepted host promotion. Host IDs are unique. Confinement evidence is non-portable and may never be copied, inherited or inferred from another host.
4. `agent-task prepare` computes the current host identity. In a post-promotion lifecycle, normal pilot tasks are accepted only when that host has an active registry entry.
5. An unregistered host may prepare only tasks byte-bound to a sibling host-requalification calibration plan. A normal feature task on an unregistered host fails closed even when the global lifecycle is `PILOT_WRITE_READY`.
6. Host requalification requires the same safety evidence class as the original cutover: host inspection, all required mechanical probes, a real read-only Codex invocation, exactly two independently qualified implementation calibrations, separate handoffs, separate canonical dry-runs and separate canonical accepts.
7. The two host-calibration implementation tasks use host- and attempt-bound canary paths. Their target bytes are supplied through immutable Codex Change Bundles. A later separate trusted-operator promotion adds the host authorization and removes that host's temporary canary paths from the current tree. Git history remains the acceptance provenance.
8. Host qualification must bind the Codex CLI version and the successfully probed inner-sandbox command form. The active contract permits only explicitly listed safe forms. The harness probes them fail-closed and records the selected form in inspect, probe and qualification evidence.
9. Supporting more than one Codex sandbox command form does not relax confinement. The outer Linux Bubblewrap profile, private Codex home, approval policy, path restrictions, network restrictions and trusted operator integration boundaries remain unchanged.
10. Desktop and laptop may therefore be simultaneously authorized only after each machine has completed its own qualification and separate accepted promotion. Adding one host does not revoke or mutate another host's evidence.

## Consequences

- Project readiness and host write authorization become separate machine-readable facts.
- `codex-pilot-ready --live` may report `PILOT_WRITE_READY=true` while `HOST_WRITE_AUTHORIZED=false`; in that state the only permitted next action is host calibration.
- The original promoted host remains valid after migration to the registry.
- A newly installed or materially changed host cannot gain write authority merely by checking out a promoted Springmaster commit.
- Compatible Codex CLI generations can be qualified by capability instead of by an unreviewed version-number assumption.
- A laptop and desktop can both be normal Springmaster Codex development hosts once both have independent accepted authorization entries.

## Rejected alternatives

- Reusing the first host's promotion on another machine: rejected because host evidence is explicitly non-portable.
- Replacing `writePromotion.hostId` whenever another workstation is promoted: rejected because only one workstation would remain representable and historical authority would become ambiguous.
- Treating global `PILOT_WRITE_READY` as sufficient at task prepare: rejected because a fresh checkout on an unqualified host would gain writable task preparation.
- Hard-coding one Codex CLI version or one sandbox syntax without probing: rejected because CLI syntax is an implementation detail that can evolve independently of the confinement contract.
- Weakening or removing the inner sandbox smoke test: rejected because nested sandbox behavior remains required defense in depth.

## Verification and promotion

The contract and harness tests must prove at minimum:

- the original promoted host remains registered;
- a live unregistered host is project-ready but not write-authorized;
- a second registered host is write-authorized without removing the first;
- normal task preparation is denied on an unregistered host;
- a host-bound requalification task is allowed only when its sibling plan matches host ID, baseline, task path and SHA-256;
- both accepted Codex sandbox command forms pass the same confinement contract;
- unsupported command forms fail closed;
- promotion remains a separate trusted-operator accepted change and never follows automatically from qualification.

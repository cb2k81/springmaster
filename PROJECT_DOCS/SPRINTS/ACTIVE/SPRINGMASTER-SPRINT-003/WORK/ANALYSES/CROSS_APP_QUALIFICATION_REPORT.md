---
documentId: S003-CROSS-APP-QUALIFICATION
title: Sprint 003 Cross-App Qualification Report
documentType: report
status: final
authority: evidence
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-08-20
validFrom: 2026-08-20
lastReviewedAt: 2026-08-20
reviewBy: 2026-08-31
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-003
---
# Sprint 003 Cross-App Qualification Report

The 28-fixture suite qualifies twelve positive references/contracts and all sixteen required negative diagnostics. Managed projects were not accessed or changed.

| Source | Provenance | Qualified statement | Explicit boundary |
|---|---|---|---|
| Springmaster | full-export reference, SHA-256 `2e6f53a8e1bbb3c24e0de0b5ce322a5cdae62411ea53678ee30f0306a88f71fd`, Git `d3bcc9b83f68d215ad8d8be39bb0a53e3e95203b` | accepted M-001 baseline and current Sprint-003 reference state | A005 recovery seed remains non-canonical; A006 is separately governed |
| IDM | immutable reference, SHA-256 `ef71001c9ef25a6b2739ca4eda77737f743f08aa82b04c29901bc0fdb57abe0b` | scoped relations, target authorization, shared precheck/capability/execution guard | no IDM migration |
| Personnel | immutable reference, SHA-256 `78e0e5b782b9555fd964c9ae21660f1e1a8d7aa445847595f4c23a7a6d2000bb` | expected version sets, temporal projection, aggregate graph and mixed locking | concrete lock phases remain application-specific |
| Contacts | immutable selected snapshot, SHA-256 `134384de9bf91f8a6b208cc62823b5b99af60beb6dd0b7e4779c56e1778c67cc` | optimistic `persistenceVersion` and Spring Batch background-job lifecycle | Contacts does not prove `SNAPSHOT_TOKEN` |
| GWC | immutable reference, hash unavailable (`null`) | v1.1 compatibility, Standard Page/Workspace separation and compiler/IR binding | no assertion about live GWC |
| Snapshot Token | synthetic contract | D04 producer/consumer semantics | not attributed to Contacts |
| Generic Bulk | synthetic contract | complete synchronous/asynchronous contract and negative rules | no generic runtime |
| UI Spec 1.2 | synthetic contract | additive `operationKey` binding and deterministic v1.1 alias | no GWC rollout claim |

Result: no contradictory cross-application finding. All target maturities stop at `CONTRACTED`, `DEFINED` or `REFERENCE_IMPLEMENTED`.

---
documentId: SPRINGMASTER-SPRINT-006-PLAN
title: Governance & Tooling Simplification / Managed Project Recovery - Solution Plan
documentType: plan
status: active
authority: directive
scopeLevel: project
scopePaths:
  - springmaster/sprints
appliesTo:
  - springmaster
owner: springmaster-maintainers
createdAt: 2026-09-01
validFrom: 2026-09-01
lastReviewedAt: 2026-09-02
reviewBy: 2026-09-30
supersedes: []
supersededBy: null
temporary: true
sprintId: SPRINGMASTER-SPRINT-006
---

# Governance & Tooling Simplification / Managed Project Recovery - Solution Plan

## Lösungsoptionen und Auswahl

### Option A - Bestehende Governance-/Toolchain unverändert nur weiter automatisieren

Verworfen. Dadurch würde die heute beobachtete Komplexität lediglich schneller und portabler reproduziert. Personnel- und ZBM-Erfahrung zeigen, dass zusätzliche Automation ohne einfacheren Happy Path das Produktziel nicht erfüllt.

### Option B - Governance-/Patchregeln lokal umgehen

Verworfen. Ad-hoc-Bypässe würden Safety Invariants, Reproduzierbarkeit und gemeinsame Standards schwächen und erneut projektspezifische Sonderwege erzeugen.

### Option C - Enabling Governance, Current Tooling Convergence und getrennte Engineering-/Delivery-Flows

Ausgewählt. Sicherheits- und Trust-Boundaries bleiben erhalten; vorhandene kanonische Producer-/State-Wahrheit wird zuerst gegen aktuelle versionierte Quellen bewiesen. Nur reale Model-, Caller-, Distribution-, Adoption-, Documentation-, DX-, Runner- oder Source-Diff-Gaps werden geschlossen. Erst diese konvergierte Toolchain wird portabel gemacht.

## Architektur- und Contract-Auswirkungen

- ADR-0020 wird praktische Authority für Enabling Governance, Self-Recovery, progressive Qualification und Development-/Delivery-Trennung.
- Der vorhandene kanonische Patch-Artifact-Producer, seine Caller und der Preflight verwenden dieselbe versionierte Artifact-Contract-Quelle; ein zweiter Producer wird nicht eingeführt.
- Patch-/Tooling-State wird zuerst entlang der versionierten Truth-Kette von Git HEAD über Plattform-/Toolingversion bis State Patch nachgewiesen; bei eindeutiger Wahrheit entsteht kein zweiter State Store.
- Managed Projects verwenden project-owned versioniertes Tooling; Springmaster ist Producer/Releasequelle, keine Runtime-Abhängigkeit.
- Runner erhalten gemeinsame Semantik für required success, expected failure, Phase, Capture, Diagnose und Ergebnisabschluss.
- Source-Diff-, Runtime-Artefakt- und Final-Cleanliness-Semantik werden getrennt.
- Environment, DBTool und Build-Side-Effects werden als portable Tooling-Verträge präzisiert.
- Der Backend-Consumer-Handoff wird projektneutral, versioniert, content-addressed und additiv aus autoritativen Backendquellen abgeleitet; UI-Semantik und objektbezogene Authorization/RLS bleiben außerhalb seiner Authority.

## ADR- und Standardbedarf

ADR-0020 deckt die strategische Entscheidung ab. Weitere ADRs sind nur erforderlich, wenn ein Umsetzungsschnitt eine bestehende Trust Boundary, Patch-Transaktionssemantik, Managed-Project-Ownership oder andere akzeptierte Architekturentscheidung materiell ändert.

Detailverträge können als Tooling-/Managed-Project-Standards oder maschinenlesbare Contracts entstehen. Keine neue Norm wird nur in einem Runner oder Changelog versteckt.

## Slices und Reihenfolge

### M-001 - Governance-/Tooling-Reibungsinventur und Recovery Contract

Status: `completed` nach vollständiger Trusted-Host-Qualification, Acceptance 000267 und Post-Accept-Contract-Review.

- Safety Invariants, Architekturverträge, Standardprozesse und Guidance klassifizieren.
- Personnel-/ZBM-Feldbefunde source-bound erfassen.
- Developer-Interaction-, Teststart-, Laufzeit-, Evidence-Größen- und Recovery-Metriken definieren.
- Maintenance-/Recovery-Vertrag inklusive erlaubter und verbotener Operationen materialisieren.
- Umsetzungsschnitt: bestehende Engineering-Contracts um `maintenance-recovery` erweitern; kein Repair-Executor, cpatch-Producer, Supervisor oder allgemeines Break-glass-Tool.
- Positive Canary: absichtlich defektes kopiertes Gate über unabhängigen Bootstrap im isolierten Fixture reparieren, targeted und anschließend am normalen vollständigen Fixture-Boundary prüfen; Integration und fremde Dateien bleiben byte-identisch.
- Positive/negative Oracles: detached worktree und attached isolated branch sind zulässig; ein blockierter Record bleibt ohne Integrations-/Delivery-Disposition valide. Pfad-/Capability-Ausweitung, direkte Main-Mutation, Push, falscher PASS, fehlende finale Qualification vor Disposition, leere Baseline-/Worktree-Bindings, fehlende PASS-Evidence und widersprüchliche Recoverability werden fail-closed abgelehnt.

### M-002 - Current Tooling Convergence: Producer, State Truth, Runner und Source Diff

M-002 beginnt zwingend mit `M-002-A001 Current-State Inventory`. Die Inventur bindet aktuelle versionierte Quellen und bestimmt `TRUE_GAP_CURRENT` separat für Producer, Artifact Model/Contract, Caller, Distribution/Adoption, State Truth, Runner und Source Diff. Erst danach werden konkrete writable Slices festgelegt.

- den vorhandenen kanonischen `cpatch create`-Pfad und seine Artifact-Contract-Quelle nachweisen;
- nur nachgewiesene Model-, Caller-, Distribution-, Adoption-, Documentation- oder DX-Gaps schließen und alle Caller auf dieselbe versionierte Contract-Quelle konvergieren;
- State Truth für Fresh Checkout beweisen und nur reale Distribution-/Adoption-Gaps beziehungsweise falsche Zielprojekt-Komponentenstände schließen, ohne zweiten State Store;
- reale Runner-Gaps in `required success`, `expected failure`, Capture, Phase, Diagnose und Rollback-Evidence bestimmen und anschließend gezielt schließen;
- reale Source-Diff-Gaps für semantische, artefaktbewusste und Locale-unabhängige Mengenvergleiche bestimmen und anschließend gezielt schließen.

### M-003 - Engineering/Delivery Separation, Progressive Qualification and Compatibility Lock

Engineering:

```text
Branch / Worktree -> Change -> targeted verification -> required broader qualification -> Commit
```

Delivery:

```text
qualified Commit -> artifact-build/create -> preflight/plan -> dry-run -> Human Accept
```

- cpatch bleibt an der Trust Boundary;
- progressive Qualification und proportionale Evidence implementieren;
- Result-/Diagnostic-Phase unabhängig vom Follow-Exit sicherstellen;
- `patches/work` current-only und `patches/logs` durable durchsetzen.
- Changes als additiv/opt-in oder separat migrationspflichtig klassifizieren und bestehende Public Contracts/Compatibility Locks regressionsprüfen;
- einen versionierten Backend-Consumer-Handoff zunächst report-only aus autoritativen Backendquellen ableiten, ohne UI-Semantik oder Client-Authorization zu erzeugen.

### M-004 - Project-local DEV and Fresh-Checkout Portability

- `.env.example`/`.env` selective-sync mit Secret-Erhalt;
- DBTool-Adminmodi `sudo|socket|password` oder funktional äquivalent;
- generischer DEV-Bootstrap;
- Fresh Schema -> Liquibase -> Hibernate validate -> Integration Tests;
- Build/Package/Deploy getrennte Side Effects;
- Fresh Checkout ohne/mit lokaler Config;
- project-lokal installierte Tools, Contracts und Consumer-Handoff-Pakete ohne Springmaster-/GWC-Nachbarcheckout qualifizieren;
- externe Contract-Versionen explizit und content-addressed binden.

Der vollständige `install/update/repair/rollback`-Lifecycle gehört primär zu M-006, nicht zu M-004.

### M-005 - Personnel/ZBM Non-Regression Field Qualification

Personnel:

- einen realen kleinen Produktfehler/Change korrekt diagnostizieren und qualifizieren;
- bestehende Public Contracts und lokale Compatibility Locks unverändert nachweisen oder eine separate Migration verlangen;
- nicht-fachliche Schritte, wiederholte Starts, Shadow-/Evidence-Größe und Recovery-Kosten gegenüber aktueller P3-Evidence messen.

ZBM:

- aktuellen Blocker read-only inventarisieren und klassifizieren;
- project-owned Handoff/Tooling und reduzierte Nachbarcheckout-Abhängigkeit qualifizieren;
- `UNSUPPORTED` wahrheitsgemäß fail-closed/report-only behandeln;
- bestehenden Public Contract und lokalen Compatibility Lock unverändert nachweisen oder eine separate Migration verlangen.

### M-006 - Managed Project Adoption and Lifecycle

- Project Adapter und Capability-/Profile-Adoption;
- Adoption Record/Managed State und Compatibility Decision;
- install/update/repair/rollback des project-owned Stands;
- project-scoped Runs/Worktrees/Evidence/Artifacts;
- Deviations und Target-Apply-Grenze;
- keine fremden Projektcheckouts als generische Gate-Voraussetzung.

### M-007 - GWC Cross-Repository Conformance and Adoption Evidence

Nur wenn P0/P1 nicht verzögert werden:

- `SPRINGMASTER_CONFORMANT` und `GWC_CONFORMANT` als capability- und Contract-Version-spezifische Aussagen trennen;
- die aktuelle GWC-owned Contract-Version explizit und content-addressed binden, ohne UI Spec 1.2 als aktuelle GWC-Produktwahrheit vorauszusetzen;
- den Backend-Consumer-Handoff gegen diese Version prüfen, ohne volle GWC-Produktion oder UI-Codegeneration zu behaupten;
- positive und negative Compatibility-Fälle sowie Personnel-/ZBM-Evidence erfassen;
- P2/report-only bleiben, kein Productive Source Overwrite ausführen und Strict erst nach bestehender Promotion-Governance erwägen.

## Reihenfolge und Abhängigkeiten

1. M-001 schafft Authority, Feldbaseline und Recovery-Vertrag.
2. M-002 beweist zuerst den Current State und schließt ausschließlich daraus abgeleitete reale Producer-/State-/Runner-/Source-Diff-Gaps.
3. M-003 trennt Engineering und Delivery, reduziert Qualification-/Evidence-Aufwand und etabliert additive Compatibility sowie den report-only Backend-Consumer-Handoff.
4. M-004 macht Tools, Contracts und Handoff DEV-/Fresh-Checkout-fähig und project-lokal qualifizierbar.
5. M-005 beweist Non-Regression und Nutzen an Personnel und ZBM.
6. M-006 führt den feldbewährten Stand in Managed Adoption und den vollständigen Lifecycle über.
7. M-007 bleibt nachgeordnet/report-only, bindet die aktuelle GWC-owned Contract-Version und darf P0/P1 nicht blockieren.

## Teststrategie und Zwischenverifikationen

Jeder Slice startet mit kleinster aussagekräftiger Verifikation und erweitert bis zur Integrationsgrenze. Tooling-Slices benötigen positive, negative, Tool-Error- und Recovery-Fixtures. M-002-A001 muss vor jedem writable M-002-Slice dessen `TRUE_GAP_CURRENT` belegen. Für den vorhandenen Producer, seine Caller und den Validator sind insbesondere Contract-/Format-Parität, Baseline-/Hash-Konflikte, Delete/New/Modify, Pfade/Berechtigungen und deterministischer Rebuild zu testen.

Für Runner werden expected-success/expected-failure, ERR-Trap-Interaktion, Phasenstatus, Follow-/Result-Trennung und Diagnose-vor-Rollback getestet. Source-Diff-Fixtures laufen mindestens unter `LC_ALL=C` und einer UTF-8-Locale.

Für M-001 validiert `engineering-contracts-it.sh` den Recovery Record hermetisch. Die defekte Gate-Kopie ist keine Bootstrap-Voraussetzung; erst nach isolierter Reparatur wird sie targeted und über den normalen vollständigen Fixture-Boundary aufgerufen. Hash- und Sentinel-Prüfungen sichern die unveränderte Integration und nicht autorisierte Nachbarpfade. Zusätzliche Contract-Cases sichern die ADR-0020-Parität für attached isolated branches, blockierte Records, Evidence-Referenzen und Recoverability-Zustände.

Fresh-Checkout-Qualification deckt Checkout ohne `.env`, lokal gebootstrapte `.env`, Secret-Erhalt, DB-Setup, Build ohne Deployment und fehlende notwendige lokale Secrets mit actionable Diagnose ab.

## Messkriterien

Vorher/Nachher werden für repräsentative Changes mindestens erfasst:

- Benutzerinteraktionen / notwendige manuelle Entscheidungen;
- Anzahl separater Tool-/Teststarts;
- Time-to-first-actionable-result;
- Time-to-qualified-candidate;
- Größe und Dateianzahl von Success-/Failure-Evidence;
- Anzahl manueller Protokoll-/Manifest-/ZIP-Schritte;
- Recovery-Schritte bis wieder arbeitsfähiger Zustand.

Die Metriken sind Evidence für Vereinfachung, keine neue permanente Pflicht für jeden normalen Projektchange.

## Migration und Rollback

- Bestehende Tooling-Versionen bleiben bis zur qualifizierten neuen Version reproduzierbar.
- Producer-/Caller-/Runner-Anpassungen werden gegen die bestehende versionierte Contract- und Validator-Wahrheit qualifiziert; kein zweiter Producer, kein zweiter State Store und kein Big-Bang-Umschreiben historischer Archive.
- Managed Projects aktualisieren versioniert und kontrolliert; Update/Repair besitzt expliziten Rollback-/Recovery-Pfad.
- Ein fehlgeschlagener Slice darf den vorherigen qualifizierten Projekt-/Toolingstand nicht unbrauchbar machen.
- Environment-Sync verändert keine unbekannten lokalen Keys/Secrets destruktiv.

## Tool- und Gate-Einsatz

- Gates werden nach realem Risiko und Phase klassifiziert: Source, Delivery, Runtime oder Release.
- Report-only bleibt Default, bis Promotion-Kriterien erfüllt sind.
- Ein Validatorfehler liefert actionable Details; der Standardweg nutzt möglichst einen Producer/Scaffold, der denselben Vertrag kennt.
- Full Qualification wird an definierten Integrations-/Release-Grenzen ausgeführt, nicht reflexiv bei jedem Explorationsschritt.
- Cross-Project-Kompatibilität gehört in Springmaster-/Releasequalification, nicht in jeden normalen Zielprojektlauf.

## Dokumentations- und Registerauswirkungen

Zu pflegen sind mindestens:

- ADR-0020 / zugehörige Tooling- und Managed-Project-Standards;
- Projektziele/Roadmap;
- AGENTS/Development-/Operations-Guides;
- Tooling-/Capability-/Gate-Register und Version Truth;
- S006 Brief, Plan, Status, Completion und Field Qualification Evidence;
- Managed-Project-Adoption-/Update-Dokumentation.

## Versionswirkung

Erwartet sind `PLATFORM_TOOLING_VERSION=minor`, `PLATFORM_UPDATE_VERSION=minor` und daraus gegebenenfalls `PLATFORM_VERSION=minor`. Core/Template/Demo werden nur erhöht, wenn ein tatsächlicher S006-Schnitt diese Komponenten verändert. Finale Werte entstehen ausschließlich aus akzeptierten Changes und Version Policy.

## Patch- oder Commitsequenz

Patchnummern werden live vergeben; Sprintplanung erfindet keine IDs.

| Schnitt | Inhalt |
|---|---|
| S006-01 | Recovery Contract, Regelklassifikation, Feld-/DX-Baseline |
| S006-02 | Current-State Inventory und daraus nachgewiesene Producer-/State-/Runner-/Source-Diff-Konvergenz |
| S006-03 | Engineering-/Delivery-Trennung, Progressive Qualification, Compatibility Lock und report-only Backend Consumer Handoff |
| S006-04 | project-lokale Env/DBTool/Build/Fresh-Checkout-/Tool-/Contract-/Handoff-Portabilität |
| S006-05 | Personnel-/ZBM-Non-Regression-Field-Qualification |
| S006-06 | Managed-Project-Adoption und install/update/repair/rollback-Lifecycle |
| S006-07 | optionale report-only GWC-Cross-Repository-Conformance gegen aktuelle GWC-owned Contract-Version |
| S006-Closure | Full Qualification, Version Truth, Completion, Archivierung |

## Unsicherheiten und Entscheidungszeitpunkte

- Die konkrete ZBM-Live-Root-Cause wird nicht aus dem Handoff erfunden; sie wird im Feldslice belegt.
- M-002-A001 entscheidet für jedes Teilproblem, ob ein aktueller Gap besteht; ohne `TRUE_GAP_CURRENT=true` entsteht kein writable Implementierungsslice.
- Der genaue gemeinsame Artifact-Contract-Bindungspunkt für alle Caller wird erst nach Inventur der aktuellen cpatch-/Toolkit-Grenzen festgelegt; der vorhandene Producer bleibt kanonisch.
- Ob einzelne alte Gates entfernt, herabgestuft oder nur mit Producer/Recovery ergänzt werden, hängt von ihrer realen Risiko-/Authority-Klassifikation ab.
- GWC-Conformance bleibt P2 und kann ohne falsche Reifeaussage deferriert werden.
- Materielle Änderung einer akzeptierten Trust-/Patch-/Managed-Project-ADR löst `stop-and-replan` aus.

## Lifecycle

| Datum | Ereignis | Entscheidung |
|---|---|---|
| 2026-09-01 | Solution Framing | Enabling Governance, kanonische Producer und getrennte Engineering-/Delivery-Flows als S006-Lösungsrichtung bestätigt. |
| 2026-09-02 | M-001 implementation candidate | ADR-0020 als bestehender Engineering-Recovery-Record mit hermetischer Self-Repair-Canary und negativen Scope-/Capability-/Truth-Oracles materialisiert. |
| 2026-09-02 | M-001 accepted and review-hardened | Trusted-Host-Qualification und Acceptance 000267 abgeschlossen; Post-Accept-Review richtet Branch/Worktree-, Blocking-, Evidence- und Recoverability-Semantik exakt an ADR-0020 aus. |
| 2026-09-02 | AMEND-001 accepted | M-002 bis M-007 auf Current-State-first, additive Compatibility, versionierten Backend-Consumer-Handoff, project-lokale Portabilität, Managed Adoption/Lifecycle und Contract-Version-spezifische GWC-Evidence rebaselined. |

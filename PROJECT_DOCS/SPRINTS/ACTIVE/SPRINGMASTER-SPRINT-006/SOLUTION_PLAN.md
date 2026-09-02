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
lastReviewedAt: 2026-09-01
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

### Option C - Enabling Governance, kanonische Producer und getrennte Engineering-/Delivery-Flows

Ausgewählt. Sicherheits- und Trust-Boundaries bleiben erhalten; Standardfälle erhalten kanonische Producer/Runner, kontrollierte Recovery und progressive Qualification. Erst diese vereinfachte Toolchain wird portabel gemacht.

## Architektur- und Contract-Auswirkungen

- ADR-0020 wird praktische Authority für Enabling Governance, Self-Recovery, progressive Qualification und Development-/Delivery-Trennung.
- Patch Artifact Builder und Preflight teilen ein kanonisches Datenmodell beziehungsweise eine gemeinsame Contract-Quelle.
- Patch-/Tooling-State erhält eine versionierte Truth-Kette von Git HEAD über Plattform-/Toolingversion bis State Patch.
- Managed Projects verwenden project-owned versioniertes Tooling; Springmaster ist Producer/Releasequelle, keine Runtime-Abhängigkeit.
- Runner erhalten gemeinsame Semantik für required success, expected failure, Phase, Capture, Diagnose und Ergebnisabschluss.
- Source-Diff-, Runtime-Artefakt- und Final-Cleanliness-Semantik werden getrennt.
- Environment, DBTool und Build-Side-Effects werden als portable Tooling-Verträge präzisiert.

## ADR- und Standardbedarf

ADR-0020 deckt die strategische Entscheidung ab. Weitere ADRs sind nur erforderlich, wenn ein Umsetzungsschnitt eine bestehende Trust Boundary, Patch-Transaktionssemantik, Managed-Project-Ownership oder andere akzeptierte Architekturentscheidung materiell ändert.

Detailverträge können als Tooling-/Managed-Project-Standards oder maschinenlesbare Contracts entstehen. Keine neue Norm wird nur in einem Runner oder Changelog versteckt.

## Slices und Reihenfolge

### M-001 - Governance-/Tooling-Reibungsinventur und Recovery Contract

- Safety Invariants, Architekturverträge, Standardprozesse und Guidance klassifizieren.
- Personnel-/ZBM-Feldbefunde source-bound erfassen.
- Developer-Interaction-, Teststart-, Laufzeit-, Evidence-Größen- und Recovery-Metriken definieren.
- Maintenance-/Recovery-Vertrag inklusive erlaubter und verbotener Operationen materialisieren.
- Umsetzungsschnitt: bestehende Engineering-Contracts um `maintenance-recovery` erweitern; kein Repair-Executor, cpatch-Producer, Supervisor oder allgemeines Break-glass-Tool.
- Positive Canary: absichtlich defektes kopiertes Gate über unabhängigen Bootstrap im isolierten Fixture reparieren, targeted und anschließend am normalen vollständigen Fixture-Boundary prüfen; Integration und fremde Dateien bleiben byte-identisch.
- Negative Oracles: Pfad-/Capability-Ausweitung, direkte Main-Mutation, Push, falscher PASS und fehlende finale Qualification werden fail-closed abgelehnt.

### M-002 - Kanonischer Producer, Patch-State-Truth, Runner und Source-Diff

- kanonischen Patch Artifact Builder auf gemeinsamer Model-/Contract-Quelle implementieren;
- `new`/`modified`/`deleted`, Before-Hashes, Artifact-ID und Layout aus Candidate/Ziel ableiten;
- State Truth für Fresh Checkout vereinheitlichen;
- `run_required`, `run_expected_failure`, `run_capture`, `phase`, `fail`, `diagnose` oder funktional äquivalente gemeinsame Semantik bereitstellen;
- Gate-/Scope-Mengen semantisch und Locale-unabhängig vergleichen.

### M-003 - Development Hot Path und Progressive Qualification

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

### M-004 - DEV-/Build-Portabilität und project-owned Tooling

- `.env.example`/`.env` selective-sync mit Secret-Erhalt;
- DBTool-Adminmodi `sudo|socket|password` oder funktional äquivalent;
- generischer DEV-Bootstrap;
- Fresh Schema -> Liquibase -> Hibernate validate -> Integration Tests;
- Build/Package/Deploy getrennte Side Effects;
- Fresh Checkout ohne/mit lokaler Config;
- install/update/repair/rollback eines im Projekt versionierten Toolingstands ohne Springmaster-Nachbarcheckout.

### M-005 - Personnel- und ZBM-Recovery-Qualification

Personnel:

- realen Produktfehler/Change korrekt diagnostizieren und qualifizieren;
- nicht-fachliche Schritte, wiederholte Starts, Shadow-/Evidence-Größe und Recovery-Kosten gegenüber aktueller P3-Evidence messen.

ZBM:

- aktuellen Blocker read-only inventarisieren und klassifizieren;
- Normal-/Recovery-Pfad schließen;
- anschließenden realen Change mit project-owned Tooling und neuem Happy Path qualifizieren.

### M-006 - Portable Managed Development Foundation

- Project Adapter und Capability-/Profile-Auswahl;
- Compatibility Plan/Preflight;
- install/update/repair/rollback;
- project-scoped Runs/Worktrees/Evidence/Artifacts;
- keine fremden Projektcheckouts als generische Gate-Voraussetzung.

### M-007 - GWC Conformance Profile

Nur wenn P0/P1 nicht verzögert werden:

- `SPRINGMASTER_CONFORMANT` und `GWC_CONFORMANT` trennen;
- Capability-Menge deklarieren;
- OpenAPI/operationKey/UI-Spec-Bindung prüfen;
- report-only positive/negative Evidence;
- Strict erst nach bestehender Promotion-Governance.

## Reihenfolge und Abhängigkeiten

1. M-001 schafft Authority, Feldbaseline und Recovery-Vertrag.
2. M-002 behebt die heute größten Producer-/State-/Runner-/Gate-Reibungen.
3. M-003 trennt Engineering und Delivery und reduziert Qualification-/Evidence-Aufwand.
4. M-004 macht die vereinfachte Toolchain DEV-/Fresh-Checkout-fähig und projekt-autonom.
5. M-005 beweist Nutzen an Personnel und ZBM.
6. M-006 abstrahiert erst den feldbewährten Stand zur Managed-Project-Plattform.
7. M-007 bleibt nachgeordnet/report-only und darf P0/P1 nicht blockieren.

## Teststrategie und Zwischenverifikationen

Jeder Slice startet mit kleinster aussagekräftiger Verifikation und erweitert bis zur Integrationsgrenze. Tooling-Slices benötigen positive, negative, Tool-Error- und Recovery-Fixtures. Für Producer/Validator sind insbesondere Format-Parität, Baseline-/Hash-Konflikte, Delete/New/Modify, Pfade/Berechtigungen und deterministischer Rebuild zu testen.

Für Runner werden expected-success/expected-failure, ERR-Trap-Interaktion, Phasenstatus, Follow-/Result-Trennung und Diagnose-vor-Rollback getestet. Source-Diff-Fixtures laufen mindestens unter `LC_ALL=C` und einer UTF-8-Locale.

Für M-001 validiert `engineering-contracts-it.sh` den Recovery Record hermetisch. Die defekte Gate-Kopie ist keine Bootstrap-Voraussetzung; erst nach isolierter Reparatur wird sie targeted und über den normalen vollständigen Fixture-Boundary aufgerufen. Hash- und Sentinel-Prüfungen sichern die unveränderte Integration und nicht autorisierte Nachbarpfade.

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
- Neue Producer/Runner werden zunächst parallel gegen bestehende Validatoren qualifiziert; kein Big-Bang-Umschreiben historischer Archive.
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
| S006-02 | Artifact Producer, State Truth, Runner-/Source-Diff-Grundlagen |
| S006-03 | Engineering-/Delivery-Trennung, Progressive Qualification, Evidence-Lifecycle |
| S006-04 | Env/DBTool/DEV-Bootstrap/Build/Fresh-Checkout/project-owned Tooling |
| S006-05 | Personnel-/ZBM-Field Qualification |
| S006-06 | Managed-Project-Portability-Foundation |
| S006-07 | optional report-only GWC-Conformance-Profil |
| S006-Closure | Full Qualification, Version Truth, Completion, Archivierung |

## Unsicherheiten und Entscheidungszeitpunkte

- Die konkrete ZBM-Live-Root-Cause wird nicht aus dem Handoff erfunden; sie wird im Feldslice belegt.
- Der genaue interne Ort des gemeinsamen Patch Artifact Models wird nach Inventur der aktuellen cpatch-/Toolkit-Grenzen entschieden.
- Ob einzelne alte Gates entfernt, herabgestuft oder nur mit Producer/Recovery ergänzt werden, hängt von ihrer realen Risiko-/Authority-Klassifikation ab.
- GWC-Conformance bleibt P2 und kann ohne falsche Reifeaussage deferriert werden.
- Materielle Änderung einer akzeptierten Trust-/Patch-/Managed-Project-ADR löst `stop-and-replan` aus.

## Lifecycle

| Datum | Ereignis | Entscheidung |
|---|---|---|
| 2026-09-01 | Solution Framing | Enabling Governance, kanonische Producer und getrennte Engineering-/Delivery-Flows als S006-Lösungsrichtung bestätigt. |
| 2026-09-02 | M-001 implementation candidate | ADR-0020 als bestehender Engineering-Recovery-Record mit hermetischer Self-Repair-Canary und negativen Scope-/Capability-/Truth-Oracles materialisiert. |

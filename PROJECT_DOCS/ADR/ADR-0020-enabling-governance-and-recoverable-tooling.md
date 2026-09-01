---
documentId: ADR-0020
title: Enabling Governance and Recoverable Tooling
documentType: adr
status: accepted
authority: normative
scopeLevel: ecosystem
scopePaths:
  - springmaster/engineering
  - springmaster/standards/build-tooling
  - springmaster/managed-projects
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-09-01
validFrom: 2026-09-01
lastReviewedAt: 2026-09-01
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# ADR-0020 Enabling Governance and Recoverable Tooling

## Kontext

Springmaster verfolgt Standardisierung, Wiederverwendung, belastbare Qualität und kontrollierte KI-gestützte Entwicklung. Die bisherigen Sprints haben dafür starke Fail-Closed-, Evidence-, Patch-, Gate- und Trust-Boundary-Mechanismen aufgebaut. Diese Mechanismen sind wertvoll, wenn sie reale Risiken kontrollieren.

Die Feldnutzung zeigt zugleich eine zweite Qualitätsdimension: Governance und Tooling können selbst zur Entwicklungsbarriere werden, wenn normale Änderungen unnötig durch Delivery-Mechanismen geführt werden, Diagnose- und Evidence-Aufwand unverhältnismäßig wächst oder ein defektes Werkzeug nur mit genau demselben Werkzeug repariert werden dürfte. Ein solcher Zustand widerspricht dem Zweck von Springmaster als Standardisierungs- und Unterstützungsplattform.

Springmaster benötigt deshalb neben Sicherheit, Determinismus und Nachweisbarkeit eine ausdrückliche Produktregel für Nutzbarkeit und Wiederherstellbarkeit.

## Entscheidung

### 1. Leitprinzip

Für Springmaster und gemanagte Projekte gilt:

> **Standardisieren, unterstützen, nicht blockieren.**

Governance, Standards, Gates und Tooling sind Mittel zur verlässlichen und vereinfachten Projektumsetzung. Sie sind nicht Selbstzweck. Ein Standardweg SOLL die Zahl projektspezifischer Entscheidungen, manueller Kommandos und Recovery-Schritte gegenüber einem lokalen Sonderweg reduzieren.

### 2. Regelhierarchie

Technische Vorgaben werden nach ihrer Funktion unterschieden:

1. **Safety Invariants** schützen Integrität, Berechtigungen, Secrets, Trust Boundaries und fremde Änderungen. Sie bleiben fail-closed.
2. **Akzeptierte Architektur- und Produktverträge** definieren verbindliche Semantik und dürfen nicht stillschweigend umgangen werden.
3. **Standard-Prozess- und Toolpfade** sind bevorzugte, qualifizierte Umsetzungsmechanismen. Sie dürfen nicht allein durch ihre Existenz zu unveränderlichen Architekturgrenzen werden.
4. **Guidance und Automation** sollen Arbeit vereinfachen und dürfen keine neue normative Produktwahrheit erfinden.

Ein Tool oder Gate DARF keine strengere fachliche oder prozessuale Verpflichtung erzeugen, als aus einer akzeptierten normativen Quelle ableitbar ist.

### 3. Kein Self-Lock der Governance

Kein Governance-Mechanismus DARF eine funktionsfähige Instanz seiner selbst als einzigen zulässigen Weg für seine eigene Reparatur voraussetzen.

Ist ein vorgeschriebener Standardpfad defekt, unvollständig oder nachweislich ungeeignet, MUSS ein unterstützter Maintenance-/Recovery-Pfad existieren. Dieser Pfad darf das betroffene Tooling in einem isolierten Branch oder Worktree direkt reparieren, sofern mindestens folgende Grenzen eingehalten werden:

- keine direkte unkontrollierte Mutation von `main`;
- kein automatischer Push;
- keine Ausweitung von Scope, Capability oder Berechtigung ohne explizite Autorisierung;
- keine Übernahme fremder Änderungen;
- keine falsche PASS-, Qualification- oder Acceptance-Aussage;
- gezielte Verifikation der Reparatur vor Integration;
- vollständige erforderliche Qualification spätestens an der Integrations- oder Delivery-Grenze.

Der Recovery-Pfad ist kein Bypass der Safety Invariants, sondern ein kontrollierter Weg zur Wiederherstellung des Standardpfads.

### 4. Patchsystem und Git

Git bleibt die dauerhafte Entwicklungshistorie. Das Patchsystem bleibt ein qualifizierter Transaktions- und Delivery-Mechanismus für Trust Boundaries, Cross-Repository-Lieferungen, kontrollierte Acceptance und vergleichbare Integrationssituationen.

Für normale lokale Entwicklung ist ein Patchartefakt jedoch **nicht generell Teil des Development Hot Path**. Soweit keine spezifische akzeptierte Regel für einen Risikofall etwas anderes verlangt, ist der bevorzugte lokale Ablauf:

```text
Branch / Worktree
  -> Änderung
  -> gezielte Verifikation
  -> risikogerechte breitere Qualification
  -> Commit
```

Ein cpatch wird erzeugt, wenn eine echte Delivery-, Acceptance- oder Target-Mutationsgrenze erreicht wird oder der konkrete Auftrag ausdrücklich ein Patchartefakt verlangt.

### 5. Progressive Qualification

Qualification MUSS risikobasiert und progressiv ausführbar sein. Der Normalfall beginnt mit der kleinsten aussagekräftigen Prüfung und erweitert die Breite bis zur für die Integrationsgrenze erforderlichen vollständigen Qualification.

Typische Stufen sind:

```text
Syntax / Static
  -> betroffene Tests
  -> betroffener Slice
  -> Contract-/Integration-Gates
  -> Full Qualification an der Integrations-/Release-Grenze
```

Eine strengere frühe Prüfung bleibt zulässig, wenn Risiko, Contract oder konkrete Evidence sie erfordern. Sie ist jedoch zu begründen und darf nicht nur aus historischer Tooling-Kopplung entstehen.

### 6. Proportionale Evidence

Evidence dient dazu, Entscheidungen, Fehler und Qualification reproduzierbar zu erklären. Sie soll nicht unnötig das Repository, historische Archive, Buildausgaben oder bereits unveränderliche Evidence replizieren.

- Erfolgsfälle sollen kompakte, deterministische Evidence erzeugen.
- Fehlerfälle dürfen reichhaltigere Diagnosepakete erzeugen.
- Historische Exporte, `.git`-Objekte, alte Patcharchive und fremde Buildartefakte werden nur aufgenommen, wenn sie für die konkrete Diagnose erforderlich sind.
- Bestehende unveränderliche Evidence wird bevorzugt referenziert statt kopiert.

### 7. Actionable Blocking

Jeder erwartbare harte Block SOLL maschinenlesbar mindestens klassifizieren:

- Ursache beziehungsweise `reasonCode`;
- Kategorie wie `PRODUCT`, `TOOLING`, `ENVIRONMENT` oder `GOVERNANCE`;
- ob der Zustand recoverable ist;
- den kleinsten sicheren nächsten Schritt;
- ob der Maintenance-/Recovery-Pfad zulässig ist.

Unbekannte oder nicht vertrauenswürdige Zustände dürfen weiterhin fail-closed bleiben. Fail-closed bedeutet jedoch nicht diagnosearm oder ohne Recovery-Vertrag.

### 8. Managed Projects

Ein gemanagtes Projekt darf Springmaster-Fähigkeiten granular adoptieren. Die Adoption eines Standards oder Tools DARF unabhängige Fachentwicklung nicht allein deshalb blockieren, weil ein nicht benötigter Springmaster-Mechanismus fehlt oder defekt ist.

Die Portable Managed Development Platform MUSS daher sowohl den qualifizierten Normalpfad als auch Update-, Repair- und Recovery-Lifecycle des Toolings berücksichtigen.

Ein veröffentlichter Tooling-Stand MUSS im Zielprojekt aus den dort versionierten Komponenten selbstständig nutzbar sein. Ein normaler Projektworkflow DARF keinen Springmaster-Nachbarcheckout, kein fremdes Projekt und kein nicht versioniertes historisches Springmaster-Artefakt als Laufzeitvoraussetzung benötigen. Springmaster ist Producer, Integrations- und Releasequelle; das Zielprojekt bleibt operativ autonom.

### 9. Kanonische Producer statt Protokollrekonstruktion

Wird ein maschinenlesbares Artefakt oder ein strukturierter Prozess für den Standardweg verlangt, MUSS Springmaster einen kanonischen Erzeugungsweg bereitstellen oder den Zustand direkt aus einer versionierten Quelle erzeugen können. Ein strenger Validator allein ist kein vollständiger Developer Contract.

Insbesondere gilt für Patch-/Delivery-Artefakte:

- Producer und Validator SOLLEN dasselbe interne Datenmodell verwenden;
- Scope, `new`/`modified`/`deleted`, Before-Hashes, Artifact-Identität und Layout werden vom Producer aus dem tatsächlichen Candidate/Zielzustand abgeleitet;
- der Happy Path darf keine manuelle Rekonstruktion von Manifesten, ZIP-Layouts oder historischen Patch-Metadaten verlangen;
- ein Fresh Checkout muss Tooling-/Patch-State aus versionierten Quellen eindeutig rekonstruieren können.

Dasselbe Prinzip gilt sinngemäß für Sprint-/Governance-Scaffolds: Ein Gate darf nicht zum primären Mechanismus werden, mit dem Entwickler durch wiederholtes Scheitern das zulässige Dokumentformat erraten.

### 10. Runner- und Gate-Ergonomie

Gemeinsame Runner müssen erwartete Erfolgs- und Fehlersemantik explizit modellieren, Phasen präzise benennen und die autoritative Ergebnisphase auch dann ausführen, wenn ein Follow-/Watch-Schritt fehlschlägt. Gate-/Scope-Prüfungen vergleichen semantische Mengen und Source-Änderungen; sie dürfen nicht von Arraypositionen, Locale oder bewusst erzeugten Laufartefakten abhängen.

Ein erwarteter negativer Test ist ein erfolgreicher Testfall und darf nicht allein durch einen globalen Shell-`ERR`-Handler als Laufabbruch klassifiziert werden.

## Konsequenzen

- `GOAL-008` verankert Developer Productivity, Recoverability und Enabling Governance als dauerhaftes Projektziel.
- Sprint 006 priorisiert Governance- und Tooling-Vereinfachung vor weiterer Automatisierungsbreite.
- Bestehende Safety Invariants, Human-Accept-Grenzen und Cross-Project-Schutz werden nicht gelockert.
- Bestehende Tooling- oder Governance-Regeln, die einen unnötigen Self-Lock erzeugen, werden in eigenen qualifizierten S006-Schnitten vereinfacht oder abgelöst.
- Strenge Artefakt-/Dokumentverträge erhalten kanonische Producer oder Scaffolds, bevor ihre Protokollkenntnis zum normalen Entwicklerweg wird.
- Managed Projects erhalten projekt-eigene versionierte Tooling-Stände; Springmaster bleibt keine notwendige Laufzeit- oder Nachbarcheckout-Abhängigkeit.
- Report-only und strict bleiben evidence-basierte Gate-Eigenschaften; diese ADR ist keine pauschale Abschaltung bestehender Gates.
- Das Ziel ist nicht weniger Qualität, sondern weniger nicht-fachliche Reibung bei gleicher oder besserer Vertrauenswürdigkeit.

## Abgelehnte Alternativen

### Bestehende Mechanismen unverändert nur weiter automatisieren

Abgelehnt. Dadurch würde die bestehende operative Komplexität lediglich schneller und portabler reproduziert.

### Allgemeiner Break-glass ohne Qualifikation

Abgelehnt. Recovery darf Safety Invariants und abschließende Qualification nicht umgehen.

### Patchsystem vollständig abschaffen

Abgelehnt. Es bleibt an echten Delivery- und Trust Boundaries sinnvoll und schützt dort reale Integritätsanforderungen.

## Qualification-Erwartung

Die Entscheidung gilt als praktisch qualifiziert, wenn Sprint 006 mindestens nachweist:

```text
STANDARD_PATH_SIMPLER_THAN_LOCAL_WORKAROUND=true
NORMAL_DEVELOPMENT_PATCH_HOT_PATH_REQUIRED=false
TOOL_SELF_REPAIR_WITHOUT_SELF_DEPENDENCY=true
MAINTENANCE_RECOVERY_PATH_QUALIFIED=true
CANONICAL_PATCH_ARTIFACT_PRODUCER=true
PATCH_STATE_TRUTH_UNIFIED=true
PROJECT_OWNED_TOOLING_AUTONOMY=true
RUNNER_EXPECTED_FAILURE_SEMANTICS=true
SOURCE_DIFF_GATE_SEMANTIC=true
PROGRESSIVE_QUALIFICATION=true
EVIDENCE_IS_PROPORTIONAL=true
BLOCKING_STATE_HAS_RECOVERY_PATH=true
SECURITY_INVARIANTS_WEAKENED=0
UNAUTHORIZED_TARGET_MUTATIONS=0
UNINTENDED_PUSHES=0
```

## Referenzen

- `PROJECT_DOCS/GOVERNANCE/SPRINGMASTER_PROJECT_GOALS.md`
- `PROJECT_DOCS/GOVERNANCE/SPRINT_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/PROJECT_DIRECTORY_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/MANAGED_PROJECT_GOVERNANCE.md`
- `PROJECT_DOCS/ADR/ADR-0012-patch-transaction-and-evidence-boundary.md`
- `PROJECT_DOCS/ADR/ADR-0019-autonomous-logical-run-repair-orchestration.md`

## Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-09-01 | - | accepted | Enabling Governance, Tool-Recovery, progressive Qualification und die Trennung von Development Hot Path und Delivery Boundary als dauerhafte Architekturregel festgelegt. |

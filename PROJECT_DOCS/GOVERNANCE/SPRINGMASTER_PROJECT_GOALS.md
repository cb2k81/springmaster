---
documentId: DOC-GOAL-0001
title: Springmaster Project Goals
documentType: goal
status: active
authority: directive
scopeLevel: ecosystem
scopePaths:
  - springmaster/governance
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-28
validFrom: 2026-07-28
lastReviewedAt: 2026-08-24
reviewBy: 2027-01-28
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Springmaster Project Goals

## 1. Zweck und Geltungsbereich

Dieses Dokument ist die dauerhafte kanonische Quelle für die allgemeinen Ziele des Springmaster-Projekts. Sprint Briefs, Roadmaps und Completion Reports referenzieren diese Ziele, dürfen sie aber nicht als einzige aktuelle Quelle führen oder still umdeuten.

Springmaster ist die zentrale Entwicklungs-, Qualitäts- und Verteilungsbasis für Cocondo-Backend-Grundlagen. Die Ziele gelten für die Weiterentwicklung von Springmaster sowie profilgerecht für Project-New, erzeugte Anwendungen und kontrolliert gemanagte Projekte.

## 2. Zielsystem

### GOAL-001: Zentrale Tool- und Systemkern-Entwicklung

Springmaster entwickelt und qualifiziert fachfreie, wiederverwendbare Systemkern-Bausteine sowie projektneutrales Tooling zentral.

Erwartete Ergebnisse:

- eine eindeutige kanonische Implementierung für wiederverwendbaren Core und gemeinsame Werkzeuge;
- versionierte Verträge, Tests und Evidence für jede verteilbare Fähigkeit;
- keine Aufnahme projektspezifischer Fachlogik in den Core oder in generisches Tooling;
- nachvollziehbare Komponenten- und Foundation-Versionen.

### GOAL-002: Steuerung der Aktualisierung gemanagter Projekte

Springmaster stellt kontrollierte, baselinegebundene und nachvollziehbare Verfahren bereit, um Abweichungen gemanagter Projekte zu analysieren, Updates zu planen und ausdrücklich freigegebene Änderungen sicher auszuliefern.

Erwartete Ergebnisse:

- read-only Vergleich und Kompatibilitätsplanung als Standard;
- Mutation ausschließlich über autorisierte, transaktionale Updatepfade;
- projektspezifische Konfiguration und Abweichungen bleiben sichtbar;
- kein unbelegter automatischer Rollout aus dem Springmaster-Checkout.

### GOAL-003: Templating für neue Projekte

Springmaster liefert einen reproduzierbaren, schlanken und qualifizierten Ausgangspunkt für neue Projekte.

Erwartete Ergebnisse:

- deterministische Project-New-Erzeugung mit eigenständiger Projektidentität;
- Materialisierung nur der für das Zielprofil erforderlichen Verträge und Werkzeuge;
- klare Extension Points statt versteckter Kopplung an den Springmaster-Checkout;
- Fresh-Project-Acceptance als verpflichtende Evidence für Templateänderungen.

### GOAL-004: Pattern und Verträge

Springmaster definiert belastbare Architektur-, API-, Persistenz-, Sicherheits-, Tooling- und Ausführungsverträge und belegt sie durch Referenzimplementierungen oder explizit abgegrenzte Candidate-Slices.

Erwartete Ergebnisse:

- dauerhafte Entscheidungen in akzeptierten ADRs und normativen Standards;
- maschinenlesbare Contracts dort, wo eine deterministische Prüfung erforderlich ist;
- eindeutige Trennung zwischen Candidate, Reference, Canonical und Deferred;
- keine Vertragswahrheit ausschließlich in Changelogs, Sprints oder temporären Arbeitsdokumenten.

### GOAL-005: Qualitätsanforderungen und Standards für Fachapplikationen

Springmaster stellt angemessene Qualitätsanforderungen, Standards, Testprofile und Evidence-Verträge für Spring-Boot-Fachapplikationen bereit.

Erwartete Ergebnisse:

- risikobasierte, reproduzierbare Verifikation mit getrennten Tool Errors und Findings;
- report-only als Standard, bis eine Regel nachweisbar strict-ready ist;
- konsistente Anforderungen für Code, Tests, Dokumentation, Sicherheit, Daten und Betrieb;
- transparente technische Schulden, Deferrals und Releaseentscheidungen.

### GOAL-006: Autonome agentische Entwicklung bis Pre-Accept

Springmaster stellt einen äußeren, deterministischen Zustandsautomaten bereit, der einen fachlichen Entwicklungsauftrag als einen Logical Run führt und Codex innerhalb des vorab autorisierten Lösungsraums selbstständig implementieren, prüfen, diagnostizieren und reparieren lässt. Normale deterministische Produktfehler sind Repair-Signale und keine menschlichen Stop-Kriterien.

Erwartete Ergebnisse:

- ein fachlicher Auftrag benötigt im Normalpfad genau einen menschlichen Start und bleibt über interne immutable Attempts hinweg ein Logical Run;
- verbrauchte physische Agent-Task-IDs werden nicht erneut invoked; reparierbare Fehler erzeugen automatisch einen gebundenen Successor-Attempt mit byte- und mode-exaktem Arbeitsstand sowie maschinenlesbarem Failure Packet;
- Compiler-, Test-, Contract-, Fixture-, Dokumentations- und Gate-Fehler innerhalb des autorisierten Scopes werden ohne menschliche Repair-Aktion an Codex zurückgeführt; mehrere Findings einer Qualification werden soweit möglich konsolidiert;
- Trusted-Host-Postcheck und Qualification liefern deterministisches Feedback an den äußeren Automaten; bekannte reine Transportdegradation darf nicht als Produktfehler umklassifiziert werden;
- No-Progress-Erkennung, endliches Repair-Budget und explizite Stop-Klassen verhindern Endlosschleifen; Scope-, Capability-, Security-, Oracle-, Base- oder echte Host-Grenzen bleiben fail-closed;
- ein erfolgreicher Logical Run erzeugt automatisch immutable Handoff-Evidence, einen qualifizierten Candidate, einen kanonischen cpatch und einen vollständig bestandenen Patch-Dry-run;
- Codex erhält weder Schreibrecht auf `main` noch `patch-accept`-, Push- oder Cross-Project-Mutationsrechte. Der Normalpfad endet bei `PREACCEPT`; die Integration bleibt eine menschliche Trust Boundary.

### GOAL-007: Portable Managed Development Platform für Fachanwendungen

Springmaster macht Host-, Governance-, Harness- und Tooling-Fähigkeiten für kontrollierte agentische Entwicklung als versionierte Managed Development Platform auf abgeleitete und gemanagte Fachanwendungen übertragbar. Der Nutzen ist erst belegt, wenn dieselbe kontrollierte Autonomie außerhalb von Springmaster auf einer realen Fachanwendung funktioniert.

Erwartete Ergebnisse:

- der qualifizierte Host Runtime Layer bleibt projektunabhängig und kann mehrere autorisierte Projekte bedienen; eine vollständige Host-Requalification pro Fachprojekt ist im Normalfall nicht erforderlich;
- projektlokale Governance-, Control-Plane-, Harness-, Contract- und Tooling-Bestandteile sind versioniert und über den kontrollierten Springmaster-Platform-Update-Pfad installierbar und aktualisierbar;
- ein expliziter Project-Adapter-Vertrag bindet Projektidentität, erlaubte Scopes, Buildsystem, Qualification Commands, Testprofile und projektspezifische Gates, ohne Springmaster-spezifische Fachannahmen in Zielprojekte zu kopieren;
- neue Projekte und bestehende Fachanwendungen können die Managed Development Platform deterministisch bootstrapen; spätere Plattformupdates werden über Compatibility-Plan, Preflight, Dry-run und autorisierte Target-Mutation ausgerollt;
- Zielprojekt-Evidence, Worktrees, Runs und Artefakte bleiben projektbezogen namespaced; Cross-Project-Writes, direkte Springmaster-Mutation aus einem Target und ungeprüfte globale Rollouts bleiben verboten;
- mindestens eine reale abgeleitete Fachanwendung muss einen echten fachlichen Logical Run einschließlich mindestens eines automatisch reparierten Fehlers bis `PREACCEPT` nachweisen; der fachliche Patch bleibt auch dort einer separaten menschlichen Accept-Entscheidung unterworfen.

## 3. Zielbeziehungen und Priorisierung

Die sieben Ziele sind gleichrangige Bestandteile des Projektauftrags. Ein Sprint darf ein Ziel priorisieren, muss Auswirkungen auf die übrigen Ziele jedoch bewerten. Sicherheit, Nachvollziehbarkeit und Vertragskonsistenz haben Vorrang vor kurzfristiger Geschwindigkeit.

Bei Zielkonflikten gilt:

1. akzeptierte ADRs und Sicherheitsregeln werden nicht still überstimmt;
2. dauerhafte Produktwahrheit wird vor lokaler Prozess- oder Patchprovenienz gepflegt;
3. ein kleiner, vollständig qualifizierter Schnitt ist einem breiten, teilweise belegten Schnitt vorzuziehen;
4. fehlende Evidence führt zu Deferred, Blocked oder Candidate, nicht zu einer unbelegten Reifeaussage.

## 4. Nicht Gegenstand

Nicht aus diesen Zielen ableitbar sind:

- eine Freigabe zur automatischen Mutation gemanagter Projekte;
- eine pauschale Canonicalization von Demo- oder Candidate-Code;
- eine allgemeine Codex- oder Agent-Schreibfreigabe;
- die Einführung neuer Abhängigkeiten, Generatoren oder Strict Gates ohne eigene Entscheidung und Evidence;
- das Ersetzen projektlokaler Fachentscheidungen durch Springmaster-Defaults.

## 5. Steuerungs- und Abnahmekriterien

Die Zielerreichung wird über konkrete Sprintanforderungen, messbare Teilziele, Gate-Evidence, Versionsentscheidungen und Completion Reports bewertet. Jeder aktive Sprint muss seinen strategischen Bezug auf mindestens eines der Ziel-IDs `GOAL-001` bis `GOAL-007` ausweisen.

Eine Zielaussage gilt nur dann als erreicht, wenn Code, Contracts, Tests, Evidence und aktuelle Dokumentation dieselbe Aussage tragen. Historische Changelogs und archivierte Sprints sind Nachweise, aber keine aktuelle Zielquelle.

### 5.1 Abnahmekriterien für den Codex-Cutover

Der Codex-Cutover gilt nicht bereits deshalb als erfolgreich, weil Springmaster selbst schreibend mit Codex entwickelt werden kann. Er ist erst dann als realer Plattformnutzen qualifiziert, wenn `GOAL-006` und `GOAL-007` gemeinsam nachgewiesen sind.

Für den normalen fachlichen Entwicklungspfad gelten mindestens folgende Erfolgskriterien:

- `ONE_LOGICAL_RUN=true`: ein freigegebener Auftrag bleibt über automatische Repair-Attempts hinweg ein logischer Lauf;
- `HUMAN_REPAIR_ACTIONS=0`: normale Compiler-, Test-, Contract-, Dokumentations- und Gate-Fehler erfordern keine menschliche Reparatursteuerung;
- `AUTONOMOUS_TO_PREACCEPT=true`: der äußere Automat führt erfolgreiche Arbeit selbstständig bis zum kanonischen Patch-Dry-run;
- `HUMAN_ACCEPT_REQUIRED=true`: der finale Patch-Accept bleibt bewusst außerhalb der Agentenautonomie;
- `PORTABLE_MANAGED_DEVELOPMENT=true`: dieselbe Governance-/Harness-/Tooling-Fähigkeit kann versioniert auf ein Zielprojekt übertragen und aktualisiert werden;
- `PROVEN_ON_REAL_DERIVED_APPLICATION=true`: mindestens eine reale Fachanwendung hat den vollständigen agentischen Normalpfad erfolgreich durchlaufen.

Ein ausschließlich auf Springmaster erbrachter Nachweis ist damit notwendige Foundation-Evidence, aber kein vollständiger Cutover-Erfolg.

### 5.2 Geplante Nachweisfolge

Die derzeit vorgesehene Reihenfolge für die nächsten Entwicklungs- und Nachweisstufen ist:

1. **Autonomous Repair Loop V1**: der äußere Logical-Run-Automat automatisiert Failure Classification, Failure Packets, Successor Attempts, Resume, No-Progress-Erkennung, vollständige Trusted Qualification und den Weg bis `PREACCEPT`;
2. **Portable Managed Development Platform**: Governance, Control Plane, Harness, Tooling und Project Adapter werden als installier- und aktualisierbare Plattformfähigkeit für Zielprojekte qualifiziert;
3. **Real-World Cutover Qualification**: eine echte Fachanwendung übernimmt diese Plattform und beweist einen fachlichen Auftrag mit automatischer Fehlerreparatur bis `PREACCEPT`.

Diese drei Nachweisstufen sind aktuell für Sprint 005 bis Sprint 007 vorgesehen. Die konkreten Sprintzuschnitte dürfen nach Sprint-Governance angepasst werden; die Abhängigkeit der Nachweise bleibt jedoch bestehen: Autonomie vor Portabilität, Portabilität vor dem Real-World-Cutover-Nachweis.

## 6. Referenzen

- `README.md`
- `AGENTS.md`
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_REFERENCE_PROJECT_AND_STANDARDS_STRATEGY.md`
- `PROJECT_DOCS/GOVERNANCE/ENGINEERING_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/MANAGED_PROJECT_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/QUALITY_GATE_GOVERNANCE.md`
- `PROJECT_DOCS/GOVERNANCE/SPRINT_GOVERNANCE.md`
- `PROJECT_DOCS/TOOLING/CODEX_PILOT_OPERATIONS.md`
- `PROJECT_DOCS/TARGET_UPDATES/TARGET_REGISTRY.md`

## 7. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-28 | nicht kanonisch persistiert | active | Die fünf allgemeinen Projektziele aus historischen Sprint- und Projektkontexten werden als dauerhafte Zielquelle konsolidiert. |
| 2026-08-24 | active | active | `GOAL-006` und `GOAL-007` ergänzen autonome agentische Entwicklung bis Pre-Accept und die portable Managed Development Platform als verbindliche Cutover-Ziele; die nächste Nachweisfolge und messbare Cutover-Abnahme werden festgelegt. |

---
documentId: DOC-GOV-0008
title: Managed Project Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/managed-projects
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-23
validFrom: null
lastReviewedAt: null
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Managed Project Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie Springmaster neue Projekte initialisiert, bestehende Projekte als gemanagte Projekte registriert, Springmaster-Stände adoptiert, lokale Ergänzungen und Abweichungen behandelt sowie kontrollierte Updates plant und ausführt.

Sie bestimmt:

- Projektprofile, Target-Identität und Lifecycle,
- Adoption statt unkontrollierter Kopie,
- Project-New-Governance-Baseline,
- lokale Erweiterungen und Managed-Project-Deviations,
- read-only Bestands-, Drift- und Kompatibilitätsprüfung,
- Update-Profile und Zielprojektfreigaben,
- Grenzen zwischen Planung, Artefakterzeugung und Mutation,
- transaktionalen Target Apply und Closure-Evidence,
- Rückführung lokaler Abweichungen.

Sie gilt für Springmaster, die Project-New-Template-Quelle, Fresh Projects, registrierte Managed Projects und disposable Pilotprojekte. Für menschliche, automatisierte und KI-gestützte Ausführung gelten dieselben Verträge und Freigaben.

Ein Projekt wird nicht allein durch kopierte Springmaster-Dateien zum Managed Project. Erforderlich sind explizite Registrierung, identifizierbare Adoption und ein qualifizierter Lifecycle.

## 2. Abgrenzung und kanonische Verantwortung

Diese Governance ist die kanonische Quelle für Managed-Project-Identität, Adoption, lokale Deviations, read-only Prüfung, Updateplanung, Mutationsautorisierung und Zielprojekt-Closure.

| Nicht hier geregelt | Kanonische Quelle |
|---|---|
| Dokumenttypen, Status und Archivierung | Documentation Governance |
| Root-Allowlist, Pfadprofile und Extension Points | Project Directory Governance |
| technischer Lifecycle eines Changes | Engineering Governance |
| Rule-, Gate-, Waiver- und Findings-Semantik | Quality Gate Governance |
| Teststufen und Test Completion | Test Governance |
| externe Dependency-Aufnahme | Dependency Governance |
| konkrete Java-, Test- und Tooling-Regeln | Standards und ADRs |
| Sprintscope und Sprintabschluss | Sprint Governance |
| SemVer und Releasefreigabe | Release and Version Governance |
| konkrete Platform-Update-CLI | Build and Tooling Standard, Contracts und Development Guide |

Ein Engineering-Waiver ersetzt keine Managed-Project-Deviation. Eine Deviation autorisiert weder Tool Errors noch Zielprojektmutation.

## 3. Begriffe und Grundsätze

| Begriff | Bedeutung |
|---|---|
| Project-New | kontrollierte Materialisierung eines neuen Projektprofils |
| Fresh Project | akzeptiertes Ergebnis eines Project-New-Laufs |
| Managed Project | registriertes Projekt mit Adoption und kontrolliertem Update-Lifecycle |
| Target Descriptor | deklarative Quelle für Identität, Pfad, Lifecycle und erlaubte Profile |
| Adoption | nachvollziehbare Übernahme benannter Springmaster-Stände |
| Local Extension | zulässige Ergänzung innerhalb eines Extension Points |
| Deviation | befristete lokale Abweichung von einem adoptierten Vertrag |
| Update Profile | deklarative Payload- und Prüfklasse einer Lieferung |
| Compatibility Decision | maschinenlesbarer Befund einer konkreten Quell-, Ziel- und Profilkombination |
| Target Apply | einziger Platform-Update-Vorgang mit Mutationsrecht |
| Managed State | atomarer Nachweis installierter Versionen und Provenienz |
| Closure Evidence | Nachweis von Apply, Zieltests, Commit und Export |

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

### 3.1 Adoption statt Kopie

Managed Projects übernehmen identifizierbare Regel-, Contract-, Tooling- und Komponentenstände. Unkontrollierte, unabhängig gepflegte Kopien von Springmaster-Governance oder Standards sind nicht zulässig.

Physische Kopien sind nur erlaubt, wenn lokale Ausführung oder Offline-Nachweis sie erfordern, Herkunft und Version eindeutig sind und keine parallele manuelle Pflege entsteht.

### 3.2 Read-only als Standard

Bestandsaufnahme, Validierung, Planung, Generierung, Preflight, Compatibility Plan und Apply Plan sind read-only gegenüber dem Zielprojekt. Nur ein ausdrücklich autorisierter Target Apply darf mutieren.

### 3.3 Lokale Wahrheit schützen

Springmaster darf Fachlogik, Secrets, lokale Contracts, Konfiguration, Extension Points und genehmigte Deviations nicht still überschreiben. Update-Profile unterscheiden Springmaster-owned, target-owned und gemeinsam kontrollierte Inhalte.

### 3.4 Planung ist keine Autorisierung

Sprintplan, Compatibility Plan, Apply Plan, Patch-ZIP und erfolgreicher Preflight gewähren allein keine Mutationserlaubnis.

### 3.5 Keine implizite Flottenfreigabe

Freigaben gelten nur für das benannte Target, Profil, Artefakt und die geprüfte Baseline. Jedes weitere Projekt benötigt eine eigene Qualifikation.

## 4. Projektprofile, Target-Identität und Lifecycle

### 4.1 Projektprofile

| Profil | Rolle |
|---|---|
| `springmaster` | Quelle für Governance, Core, Tooling, Templates und Update-Regeln |
| `project-new-template-source` | Springmaster-interne Materialisierungsquelle; kein eigenes Projekt |
| `generated-project` | eigenständiges Ergebnis von Project-New |
| `managed-project` | registriertes Projekt mit kontrollierter Adoption und Updates |
| `disposable-pilot` | isoliertes Testprojekt ohne Delivery-Recht für reale Targets |

Springmaster ist nicht Eigentümer projektspezifischer Fachlogik oder Secrets. Änderungen der Template-Quelle wirken nicht automatisch auf bestehende Projekte.

### 4.2 Managed-Project-Voraussetzungen

Ein Projekt wird erst als Managed Project registriert, wenn mindestens vorliegen:

- stabile Target-Identität und verifizierter Projektpfad,
- bekannte Git- und Exportbaseline,
- identifizierbare Governance- und Komponentenadoption,
- deklarierter Lifecycle und erlaubte Update-Profile,
- lokales Patch-, Test- und Exportverfahren,
- Owner und Freigabeverantwortung.

### 4.3 Target Descriptor

Jedes registrierte Managed Project MUSS einen eindeutigen Target Descriptor besitzen. Dieser enthält mindestens:

- Target-Name, Pfad, Anwendungsname und Basisnamespace,
- Lifecycle,
- Initialisierungs-, Update- und Delivery-Freigaben,
- exakte Profil-Allowlist,
- Owner- oder Kontaktreferenz,
- Statusnotiz.

Der Descriptor ist die kanonische Springmaster-Quelle der Delivery-Freigabe. Markdown-Dokumente dürfen ihn erklären, aber nicht überschreiben.

### 4.4 Lifecycle

Mindestens folgende fachliche Zustände müssen unterscheidbar sein:

| Lifecycle | Bedeutung |
|---|---|
| `initialization-candidate` | Project-New-Initialisierung zulässig |
| `initialized` | Initialisierung akzeptiert; Update noch nicht freigegeben |
| `update-enabled` | zugelassene Profile dürfen geplant und nach Freigabe geliefert werden |
| `existing-deferred` | nur read-only registriert |
| `delivery-suspended` | frühere Freigabe vorübergehend entzogen |
| `retired` | keine weiteren Springmaster-Updates |

Die technische Enumeration wird im Target-Descriptor-Contract geführt. Bestehende Werte werden migrationsverträglich zugeordnet.

Initialisierung, Update-Planung und Delivery bleiben getrennte Freigaben. `TARGET_DELIVERY_ENABLED=true` umgeht weder Profil-Allowlist noch Kompatibilität, Preflight, Tests oder konkrete Apply-Autorisierung.

### 4.5 Lifecycle-Änderung

Eine Lifecycle-Änderung benötigt aktuellen read-only Befund, Begründung, Owner, Profilentscheidung, Risiko- und Rückrollbewertung, Descriptor-Änderung und Acceptance-Evidence. Ein Planungsdokument allein genügt nicht.

## 5. Adoption und Project-New

### 5.1 Adoption Record

Ein Managed Project MUSS seine Adoption maschinenlesbar dokumentieren. Der Record enthält mindestens:

- Target-Identität,
- adoptierte Springmaster-Version oder Git-Commit,
- Governance-, Standard- und Contract-Stände,
- installierte Komponenten- und Tooling-Versionen,
- angewendete Update-Profile,
- lokale Ergänzungen und aktive Deviations,
- letzte erfolgreiche Validierung,
- vorherige Adoption oder Managed State.

Angaben wie „aktuell“ oder „entspricht Springmaster“ sind nicht ausreichend. Provenienz wird mindestens über Commit, Komponenten-Version, Artifact-ID oder Patch-ID belegt.

### 5.2 Granulare Adoption

Adoption erfolgt nach Artefaktfamilie oder Komponente. Ein Projekt muss nicht jede Springmaster-Komponente oder jedes Profil übernehmen. Mindestens unterscheidbar sind Governance/Contracts, Core Runtime, Core Tests, Tooling, Defaults, Templates und Platform Update.

Lokal materialisierte normative Quellen werden als adoptiert oder abgeleitet gekennzeichnet. Lokale Abweichungen erfolgen nur als zulässige Ergänzung, registrierte Deviation oder Upstream-Änderung.

### 5.3 Minimaler Project-New-Harness

Project-New MUSS einen für `generated-project` geeigneten minimalen Harness erzeugen:

- gültige Projekt- und Dokumentationsstruktur,
- initialen Dokumentationsindex,
- Adoption Record mit Template- und Springmaster-Provenienz,
- lokales Directory-Profil,
- anwendbare Contracts und Gates,
- Deviation- und Risikoregister oder registrierte leere Ausgangsstände,
- Patch-, Test- und Exportfähigkeit,
- lokale Konfigurationsvorlagen ohne Secrets.

### 5.4 Keine Vollkopie der Master-Dokumentation

Project-New SOLL nicht die vollständige Springmaster-Governance, alle Standards, Demo-, Planungs- oder Target-Dokumente kopieren. Materialisiert werden lokal ausführbare Contracts und Tools, projektspezifische Einstiege, Adoption/Deviation-Nachweise und ausdrücklich freigegebene Templates. Andere normative Quellen werden versioniert referenziert.

### 5.5 Fresh-Project-Acceptance

Ein Fresh Project ist erst akzeptiert, wenn es ohne manuelle Reparatur:

- die erwartete Struktur besitzt,
- den vorgesehenen Build und die anwendbaren Tests besteht,
- Governance- und Directory-Gates besteht,
- einen vollständigen Export erzeugt,
- keine unbekannten oder abgelaufenen Deviations enthält,
- Adoption und Versionen maschinenlesbar ausweist.

Nach der Initialisierung ist das Projekt eine eigenständige Baseline. Weitere Änderungen erfolgen über den Managed-Project-Lifecycle und nicht durch erneute blinde Template-Materialisierung.

## 6. Lokale Ergänzungen und Deviations

### 6.1 Lokale Ergänzung

Eine Local Extension ist zulässig, wenn sie:

- innerhalb eines registrierten Extension Points liegt,
- keine adoptierte Regel still aufhebt,
- eindeutigen Scope und Owner besitzt,
- lokal geprüft wird,
- auf mögliche Upstream-Eignung bewertet wird.

Ein lokaler Standard darf Springmaster spezialisieren, aber nicht widersprüchlich neu definieren. Widersprüche benötigen eine Deviation oder Upstream-Änderung.

### 6.2 Pflicht zur Deviation

Jede lokale Abweichung von einer adoptierten Governance, ADR, einem Standard, Contract, Directory-Vertrag oder einer Dependency-Policy benötigt eine Managed-Project-Deviation.

Pflichtangaben:

- `deviationId` und Target,
- verletzte Regel oder Contract-Version,
- Scope und konkrete Abweichung,
- Begründung, Risiko und Kompensation,
- Owner,
- Erstellungs-, Review- und Ablaufdatum,
- Rückführungs- oder Migrationsplan,
- Freigabereferenz.

### 6.3 Freigabe und Wirkung

Eine Deviation benötigt Target Owner sowie Springmaster-Maintainer oder Owner der betroffenen Regelquelle. Security-, Datenintegritäts-, Lizenz-, Runtime- oder Public-API-Abweichungen benötigen zusätzlich die vorgesehene Fachfreigabe.

Eine gültige Deviation kann ein bekanntes lokales Finding erklären. Sie autorisiert keine Mutation, ersetzt keine Compatibility Decision, heilt keinen Tool Error und hebt keine unabhängige Sicherheits- oder Releasefreigabe auf.

### 6.4 Ablauf und Updatekonflikt

Abgelaufene oder unvollständige Deviations MÜSSEN blockieren. Verlängerungen benötigen erneute Risikoanalyse, aktualisierten Rückführungsplan und erneute Freigabe.

Trifft ein Update auf eine aktive Deviation, weist der Plan genau eine Entscheidung aus:

- Payload respektiert die Deviation,
- Update beseitigt sie,
- sie wird angepasst und erneut freigegeben,
- Update ist blockiert.

## 7. Read-only Managed-Project-Prüfung

### 7.1 Mindestumfang

Die read-only Prüfung ermittelt ohne Zielmutation mindestens:

- Descriptor und Projektidentität,
- Projektpfad und Zugriffsrechte,
- Git-Status, Commit und Branch,
- Export- und Patchfähigkeit,
- Adoption Record und Managed State,
- installierte Komponenten- und Tooling-Versionen,
- Governance-, Contract-, Directory-, Dependency- und Build-Drift,
- anwendbare Gates und Tests,
- lokale Ergänzungen und Deviations,
- Baseline-Hashes betroffener Payload-Pfade,
- Konfigurations- und Secrets-Grenzen.

### 7.2 Schreibgrenze

Read-only Kommandos dürfen ausschließlich in registrierte Springmaster-Build-, Report- oder temporäre Arbeitsbereiche schreiben. Sie DÜRFEN im Zielprojekt keine Datei erstellen, ändern, löschen, formatieren oder normalisieren.

### 7.3 Ergebnis

Der Befund unterscheidet mindestens:

- `eligible-for-planning`,
- `eligible-with-findings`,
- `deferred`,
- `blocked`,
- `tool-error`.

Findings und Tool Errors werden nach Quality Gate Governance getrennt behandelt.

## 8. Update-Profile und Kompatibilität

### 8.1 Deklarative Profile

Jede Lieferung MUSS genau einem registrierten Update-Profil entsprechen. Es definiert mindestens:

- Payload-Pfade oder Erzeugungsmodus,
- Patch-Scope,
- Accept- und Testprofil,
- betroffene Komponenten-Versionen,
- Kompatibilitätsquelle,
- Zieltests und erlaubte Projektprofile.

Reservierte oder unbekannte Profile dürfen nicht geliefert werden. Das Profil muss im Target Descriptor ausdrücklich zugelassen sein.

### 8.2 Compatibility Decision

Vor Patchgenerierung oder spätestens vor Target Apply MUSS eine maschinenlesbare Compatibility Decision vorliegen. Sie bewertet:

- Quell- und Zielversion,
- Downgrade und Major-Grenzen,
- Mindestquellversion,
- erforderliche Zwischenmigrationen,
- Target- und Profilidentität,
- lokale Konflikte und Deviations.

Ältere Governance-, Contract- oder Komponentenstände gelten nicht automatisch als unterstützt. Unterstützung besteht nur durch explizite Matrix oder qualifizierten Migrationspfad. N-1 ist profilbezogene Evidence, keine globale Zusage.

Downgrades und Cross-Major-Updates sind standardmäßig verboten. Ausnahmen benötigen ausdrückliche Architektur- und Migrationsentscheidung sowie qualifizierte Evidence.

## 9. Planung und Patchartefakt

### 9.1 Update-Plan

Ein Update-Plan enthält mindestens:

- Target und Baseline,
- Profil und gewünschtes Ergebnis,
- Quell- und Zielversionen,
- Payload-Pfade und Contracts,
- Compatibility Decision,
- lokale Konflikte und Deviations,
- Tests, Gates, Rückroll- und Closure-Anforderungen,
- geplante Patch- und Artifact-Identität.

`plan`, `generate`, `preflight`, `compatibility-plan` und `apply-plan` verändern kein Zielprojekt. Sie schreiben ausschließlich in registrierte Springmaster-Arbeitsbereiche.

Ein Apply Plan darf keine eigenständig ausführbare Mutationslogik erzeugen. Reale Mutation bleibt Target Apply vorbehalten.

### 9.2 Scope und Baseline

Der Plan verwendet den kleinsten vollständigen Payload-Scope. Jede Mutation oder Löschung besitzt einen vollständigen Vorzustands-Hash oder eine eindeutige Missing-Precondition.

### 9.3 Transferartefakt

Springmaster erzeugt ein Patchartefakt für das lokal qualifizierte Patchsystem des Zielprojekts. Direktes Kopieren in reale Targets ist nicht zulässig.

Das Manifest enthält mindestens Artifact-ID, Patch-ID, Target, Profil, Scope, Operationen, Baseline-Preconditions, Quell-/Zielversionen, Compatibility-Referenz, Test-/Acceptprofil und Provenienz.

Target-spezifische Konfiguration darf nur über registrierte Syntheseregeln entstehen. Springmaster-Dotenv-Dateien, absolute Pfade, lokale Defaults oder Secrets dürfen nicht ungeprüft übernommen werden.

Die Existenz des ZIPs oder ein erfolgreicher Artifact Preflight ist keine Apply-Freigabe.

## 10. Autorisierung und Target Apply

### 10.1 Einziger Mutationsweg

`target-apply` ist der einzige Platform-Update-Befehl, der ein registriertes Zielprojekt verändern darf. Andere Tools dürfen Zielmutation nicht unter anderem Namen oder als Nebenwirkung einführen.

### 10.2 Voraussetzungen

Vor Target Apply müssen mindestens erfüllt sein:

1. gültiger Target Descriptor,
2. Update- und Delivery-Freigabe,
3. zugelassenes Profil,
4. Compatibility Decision `PASS`,
5. bekannte und zulässige Zielbaseline,
6. Ziel-lokaler Live-Baseline-Preflight,
7. Dry-run und Artifact Preflight,
8. Bewertung aktiver Deviations,
9. definierte Zieltests und Closure-Pflichten,
10. ausdrückliche Autorisierung des konkreten Apply.

Die Autorisierung gilt genau für Target, ZIP-SHA-256, Artifact-ID, Patch-ID, Profil und Baseline. Eine generelle Delivery-Freigabe oder frühere Autorisierung genügt nicht.

Ein Dirty Target ist standardmäßig blockiert. Ausnahmen setzen vollständige Identifikation, Scope-Isolation und ausdrückliche Zielprojektfreigabe voraus.

## 11. Transaktion und Closure

### 11.1 Ziel-lokale Transaktion

Target Apply MUSS das qualifizierte Patchsystem des Zielprojekts verwenden. Baseline, Operationen, Tests, Evidence und Commit bilden einen kontrollierten Vorgang.

Ein Fehlschlag darf keinen uneindeutigen Teilstand hinterlassen. Das Verfahren führt vollständig zum Erfolg oder stellt den qualifizierten Vorzustand wieder her beziehungsweise markiert den Zielstand eindeutig als blockiert.

Nach Fehlern darf nicht still mit geänderten Parametern, reduzierten Tests oder angepassten Dateien wiederholt werden. Jeder neue Versuch benötigt neue Baselineprüfung und Evidence.

Managed State und Patchhistorie müssen eine erneute Anwendung desselben bereits installierten Artefakts erkennen.

### 11.2 Zieltests

Nach Apply werden die im Profil und Zielprojekt vorgeschriebenen Tests und Gates im Zielprojekt ausgeführt. Springmaster-Tests allein beweisen keine erfolgreiche Zielintegration.

### 11.3 Managed State

Komponenten-Versionen, Profil, Artifact-ID, Patch-ID, Compatibility Decision und Provenienz werden atomar aktualisiert. Eine Version gilt nicht als installiert, wenn Payload, Tests oder Managed State nicht gemeinsam erfolgreich abgeschlossen sind.

### 11.4 Commit, Export und Evidence

Ein qualifizierter Apply erzeugt entsprechend dem Zielverfahren:

- klar abgegrenzten Git-Commit,
- erforderlichen Closure-Export,
- maschinenlesbare Apply-Evidence,
- kompakten Abschlussstatus.

Ein Push benötigt separate ausdrückliche Freigabe.

Closure-Evidence enthält mindestens Target und Ausgangscommit, Patch-/Artifact-Identität, Profil, Compatibility Decision, Operationen, Preflight-/Test-/Gate-Ergebnisse, Managed State, installierte Versionen, Zielcommit, Exportreferenz sowie offene Findings und Deviations.

## 12. Drift, Konflikte und Rückführung

### 12.1 Drift und Konflikte

Read-only Prüfung und Updateplan unterscheiden mindestens Governance-, Contract-, Directory-, Dependency-, Tooling-, Versions-, Source-, Deviation- und Testdrift.

Konflikte werden klassifiziert als:

- automatisch zusammenführbar,
- lokale Ergänzung bleibt erhalten,
- Deviation erforderlich,
- Migration erforderlich,
- manuelle Entscheidung erforderlich,
- Update blockiert.

Ein Tool darf lokale Änderungen nicht aufgrund von Pfadgleichheit, Zeitstempel oder vermuteter Springmaster-Autorität überschreiben.

### 12.2 Rückführung

Deviations sollen abgebaut werden. Der Rückführungsplan kann Target-Anpassung, Springmaster-Extension-Point, Upstream-Übernahme oder kontrollierte Ablösung der Regel vorsehen.

Eine lokale Lösung wird nur upstream übernommen, wenn sie allgemein wiederverwendbar ist, zum Springmaster-Scope passt, eigene Anforderungen und Tests besitzt und keine projektspezifische Semantik einschleppt.

Eine Deviation wird erst geschlossen, wenn Zielstand, Findings, Adoption und Managed State aktualisiert und die Rückführung geprüft sind.

## 13. Mehrere Zielprojekte

Jedes Zielprojekt benötigt eigene Baseline, Descriptor-/Profilprüfung, Compatibility Decision, Autorisierung, Patch- und Closure-Evidence.

Eine spätere Fleet-Orchestrierung darf diese zielweise Qualifikation nicht ersetzen. Pilotziel, Reihenfolge und Stop-Kriterien werden vorab festgelegt. Ein Fehler an einem Ziel darf nicht automatisch zur Mutation weiterer Ziele führen.

## 14. Technische Ableitungen

Diese Governance erfordert mindestens folgende Contracts oder gleichwertige Quellen:

- Target-Descriptor-Contract,
- Governance-Adoption-Contract,
- Managed-Project-Deviation-Contract,
- Update-Profile-Contract,
- Compatibility-Matrix,
- Managed-State-Schema,
- Target-Apply-Evidence-Schema.

Die bestehenden Quellen unter `platform/update/targets`, `platform/update/rules`, `platform/update/compatibility` und `platform/update/tools` sind die technische Baseline. Neue Contracts werden migrationsverträglich angebunden und nicht als parallele Wahrheit eingeführt.

## 15. Gates und Acceptance

Ein Managed-Project-Gate prüft mindestens Descriptor, Adoption, Managed State, Profil-Allowlist, Compatibility Decision, Deviations, Governance-/Directory-/Dependency-Drift und Pflicht-Evidence.

Erforderliche Prüfarten:

- read-only Einzelprojektprüfung,
- vollständiger Target-Audit,
- Fresh-Project-Acceptance,
- disposable Managed-Project-Pilot,
- Target-Apply-Closure-Prüfung.

Positive und negative Fixtures decken mindestens gültiges Fresh Project, update-enabled Target, deferred Target, unerlaubtes Profil, abgelaufene Deviation, Downgrade/Cross-Major, Dirty Target, Hashkonflikt, Tool Error und atomaren erfolgreichen Target Apply ab.

## 16. Übergang und Bestandsprojekte

Aktuelle Target-Deskriptoren und der bestehende Platform-Update-Harness bleiben Ausgangsbasis. Diese Governance reklassifiziert keine bestehenden Projekte automatisch und gewährt keinem weiteren Projekt Delivery-Rechte.

Projekte ohne vollständigen Adoption Record werden read-only inventarisiert. Fehlende Adoption darf nicht aus Dateiinhalten vermutet und als bestätigt dargestellt werden.

Einführung:

1. Target- und Adoption-Inventar,
2. Contract- und Descriptor-Konsolidierung,
3. read-only Driftprüfung,
4. Fresh-Project- und disposable Pilot-Evidence,
5. report-only Managed-Project-Gate,
6. projektspezifische Compatibility Qualification,
7. gezielte Strict-Promotion,
8. explizite Freigabe weiterer realer Targets.

## 17. Kanonische Ausgaben

Diese Governance erzeugt oder kontrolliert:

- Managed-Project-Profil und Lifecycle,
- Adoption Record,
- Managed-Project-Deviation,
- Fresh-Project-Governance-Baseline,
- read-only Managed-Project-Befund,
- Update- und Kompatibilitätsplan,
- konkrete Mutationsautorisierung,
- Managed State und Target-Apply-Closure-Evidence.

Sie besitzt keine konkreten Java-Regeln, Testschwellen, Dependency-Listen, Releaseversionen oder allgemeinen Directory-Allowlist-Werte.

## 18. Abnahmekriterien

Diese Governance ist vollständig umgesetzt, wenn:

1. jedes Managed Project Descriptor und Owner besitzt,
2. Adoption und installierte Stände maschinenlesbar nachvollziehbar sind,
3. Project-New einen minimalen gültigen Harness erzeugt,
4. Fresh Projects ihre Acceptance bestehen,
5. lokale Ergänzung und Deviation eindeutig getrennt sind,
6. Deviations vollständig, befristet und prüfbar sind,
7. abgelaufene Deviations blockieren,
8. read-only Prüfungen keine Zielprojektdatei verändern,
9. Profile deklarativ und target-spezifisch erlaubt sind,
10. Kompatibilität Downgrade, Cross-Major und Migration behandelt,
11. Planung und Generierung keine Mutation autorisieren,
12. nur Target Apply mutieren kann,
13. jeder Apply eine konkrete Autorisierung besitzt,
14. Zielbaseline, Preflight und Zieltests verpflichtend sind,
15. Managed State, Versionen und Provenienz atomar aktualisiert werden,
16. Closure-Evidence Commit und Export belegt,
17. aktive Deviations bei Planung und Apply respektiert werden,
18. lokale Projektwahrheit nicht still überschrieben wird,
19. mehrere Targets einzeln qualifiziert werden,
20. weitere reale Targets nur nach eigener Compatibility Review freigegeben werden.


## 19. Technischer Umsetzungsstand

Die erste Project-New-Materialisierung des minimalen Governance-Harness umfasst:

- projektlokales `AGENTS.md` und einen V2-Dokumentationsindex,
- Governance Adoption und maschinenlesbaren Adoption Record,
- registrierte leere Deviation- und Risikoausgangsstände,
- initialen Managed State,
- Documentation-, Directory- und Sprint-Contracts,
- report-only Gates und vollständige Fixture-Sätze,
- freigegebene Governance- und Sprint-Templates,
- einen projektlokalen Tooling-Selfcheck,
- Fresh-Project-Acceptance ohne manuelle Reparatur.

Die Materialisierung erfüllt damit die Project-New-Anteile aus 5.3 und 5.5. Sie aktiviert keine Strict Gates und registriert das erzeugte Projekt nicht automatisch als Managed Project. Vor einer vollständigen Umsetzung dieser Governance bleiben insbesondere offen:

- ein eigenständiger Managed-Project-Deviation-Contract für reale Zielprojekte,
- read-only Managed-Project-Befund und Zielprojektpilot,
- Compatibility Decisions und profilbezogene Updateplanung,
- autorisierte Target-Apply-Closure mit Managed-State-Aktualisierung,
- weitere reale Target-Acceptance.

## 20. Referenzen

- Documentation Governance
- Project Directory Governance
- Engineering Governance
- Quality Gate Governance
- Test Governance
- Dependency Governance
- Sprint Governance
- Release and Version Governance
- ADR-0012 Patch Transaction and Evidence Boundary
- Target Registry
- Platform Update README
- Platform Update Profile Rules
- Platform Compatibility Matrix

## 21. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | – | draft | Volltext aus Governance-Anforderungen und bestehendem Managed-Project-/Platform-Update-Harness abgeleitet |
| 2026-07-23 | draft | draft | Minimaler Project-New-Governance-Harness und Fresh-Project-Acceptance technisch materialisiert; Managed-Project-Pilot bleibt offen |

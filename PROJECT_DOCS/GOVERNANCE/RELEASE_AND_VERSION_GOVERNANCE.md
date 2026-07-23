---
documentId: DOC-GOV-0009
title: Release and Version Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/release-versioning
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

# Release and Version Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie Springmaster Versionswirkungen bewertet, einen qualifizierten Releasekandidaten bildet, Releases freigibt und veröffentlichte Zustände unveränderbar nachweist.

Sie bestimmt insbesondere:

- die voneinander unabhängigen Versions- und Provenienzidentitäten,
- die kanonischen Versionsquellen,
- die Springmaster-Versionsdimensionen,
- die SemVer-Bewertung von Änderungen,
- die Trennung von Versionsempfehlung, Version Closure und Releasefreigabe,
- Release Readiness und Release Qualification,
- Releaseentscheidung, Tagging und Veröffentlichung,
- Artefaktprovenienz und Unveränderbarkeit,
- Hotfixes und nachträgliche Korrekturen,
- Auswirkungen auf Project-New und gemanagte Projekte.

Sie gilt für Springmaster sowie profilgerecht für erzeugte und gemanagte Projekte. Für menschliche, automatisierte und KI-gestützte Ausführung gelten dieselben Versionsquellen, Qualifikationsanforderungen und Freigabegrenzen.

Ein Patch, Commit, Sprintabschluss oder erfolgreicher Build ist für sich allein kein Release.

## 2. Abgrenzung und kanonische Verantwortung

Diese Governance ist die kanonische Quelle für Versionsdimensionen, SemVer-Impact, Version Closure, Release Readiness, Release Qualification, Releaseentscheidung, Hotfixes und Releaseprovenienz.

| Nicht hier geregelt | Kanonische Quelle |
|---|---|
| technischer Lifecycle eines Changes | Engineering Governance |
| Sprintscope, Sprint-DoD und Sprintabschluss | Sprint Governance |
| Teststufen und Test Completion | Test Governance |
| Rule-, Gate-, Findings- und Waiver-Semantik | Quality Gate Governance |
| Dependency-Aufnahme und Dependency-Lifecycle | Dependency Governance |
| Build-, CLI-, Export- und Tooling-Implementierung | Build and Tooling Standard |
| Adoption, Kompatibilitätsplanung und Target Apply | Managed Project Governance |
| konkrete öffentliche Java-API-Fläche | Java Architecture Standard und API-Compatibility-Contract |
| Patchtransaktion und Patchartefaktidentität | ADR-0012 und Patch Manifest V2 |
| Dokumentstatus, Supersession und Archivierung | Documentation Governance |

Diese Governance darf technische Prüfkommandos und vorhandene Werkzeuge referenzieren. Sie definiert jedoch keine konkurrierende Implementierung ihrer CLI-, Report- oder Exit-Code-Verträge.

## 3. Normative Begriffe und Identitäten

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

| Begriff | Bedeutung |
|---|---|
| Version Impact | erwartete SemVer-Wirkung einer Änderung auf eine Versionsdimension |
| Version Recommendation | während Change oder Sprint geführte, noch nicht angewendete Impact-Empfehlung |
| Version Closure | atomare Festlegung der Versionswerte für einen Releasekandidaten |
| Release Candidate | sauberer, committed und versionsgeschlossener Stand zur Qualifikation |
| Release Readiness | fachliche und technische Voraussetzungen für den Start einer vollständigen Qualification |
| Release Qualification | reproduzierbare Prüfung eines konkreten Releasekandidaten |
| Release Decision | ausdrückliche Freigabe, Ablehnung oder Zurückstellung des Kandidaten |
| Release Manifest | maschinenlesbarer Nachweis von Version, Commit, Qualification und vorgeschlagenem Tag |
| Published Release | freigegebener und durch unveränderbare Releaseidentität veröffentlichter Stand |
| Hotfix | eng begrenzte Korrektur eines veröffentlichten Stands |

Folgende Identitäten bleiben unabhängig:

- Sprint-ID,
- Requirement-ID,
- Document-ID und ADR-ID,
- Change- und Teilziel-ID,
- Git-Commit,
- Patch-ID,
- Patch-`artifactId`,
- Komponenten-Version,
- aggregierte Plattform-Version,
- Release-Version,
- Git-Tag,
- Export- und Distributionsartefakt.

Keine dieser Identitäten DARF automatisch aus einer anderen abgeleitet oder als deren Ersatz verwendet werden. Insbesondere sind Patchnummer, Sprintnummer und Releaseversion voneinander unabhängig.

## 4. Kanonische Versionswahrheit

### 4.1 Primäre Quelle

`platform/versions/platform.env` ist die kanonische Quelle der aktuellen Springmaster-Plattform- und Komponentenstände.

Lebende Dokumentation referenziert diese Datei und kopiert keine aktuellen numerischen Werte als zweite Wahrheit. Historische Reports und Changelogs dürfen den zum Erstellungszeitpunkt gültigen Stand festhalten.

### 4.2 Maven-Projektion

Während der Entwicklung MUSS die Maven-Projektversion dem kanonischen `PLATFORM_VERSION` mit angehängtem `-SNAPSHOT` entsprechen.

Die Laufzeitprojektion MUSS die unveränderte kanonische Versionsdatei verwenden. Fallback-Konstanten oder manuell kopierte Versionswerte in Anwendungscode, Konfiguration oder API-Controllern sind nicht zulässig.

Ein Release unter dieser Governance ist zunächst ein qualifizierter Springmaster-Quell-, Export- und Distributionsstand. Eine zukünftige Veröffentlichung nicht-snapshotbasierter Maven-Artefakte benötigt einen eigenen akzeptierten Publikationsvertrag.

### 4.3 Provenienzquelle

`PLATFORM_STATE_PATCH` bezeichnet den lokalen Patch, der die aktuelle Versionswahrheit hergestellt hat. Der Wert ist Provenienz und keine Produktversion.

Patch-ID und Patch-`artifactId` dürfen weder Komponenten- noch Releaseversionen ersetzen.

### 4.4 Konsistenz

Versionsquelle, Maven-Koordinate, Laufzeitprojektion, Release Manifest und dokumentierte Releaseentscheidung MÜSSEN auf denselben Releasekandidaten verweisen.

Ein Widerspruch blockiert Version Closure oder Release Qualification.

## 5. Versionsdimensionen

Springmaster führt mindestens folgende Dimensionen:

| Variable | Verantwortung |
|---|---|
| `PLATFORM_VERSION` | aggregierter qualifizierter Springmaster-Foundation-Stand |
| `PLATFORM_CORE_VERSION` | wiederverwendbarer Java Core unter `de.cocondo.system` |
| `PLATFORM_TOOLING_VERSION` | Patch-, Export-, Build-, DBTool-, Project-New-, Gate- und Release-Tooling |
| `PLATFORM_TEMPLATE_VERSION` | generierter Projektskeleton und Templatevertrag |
| `PLATFORM_DEMO_VERSION` | Demo- und Referenz-Slice-Fähigkeiten |
| `PLATFORM_UPDATE_VERSION` | Managed-Project-Planung, Kompatibilität, Generierung und Delivery |
| `PLATFORM_STATE_PATCH` | Provenienz der aktuellen Versionsfestlegung |

Nur betroffene Dimensionen werden erhöht. Eine pauschale Erhöhung aller Komponenten ist nicht zulässig.

`PLATFORM_VERSION` ist keine mathematische Ableitung einer einzelnen Komponentenversion. Sie bezeichnet den aggregierten qualifizierten Foundation-Stand und wird bei einer releasewirksamen Änderung entsprechend dem höchsten relevanten Gesamtimpact erhöht.

Neue Versionsdimensionen benötigen:

- einen eigenständigen, dauerhaft relevanten Lifecycle,
- eine kanonische Verantwortungsgrenze,
- eine maschinenlesbare Quelle,
- Qualifikations- und Kompatibilitätsregeln,
- eine Governance- oder Architekturentscheidung.

## 6. SemVer-Impact

### 6.1 Impactklassen

Für jede betroffene Dimension wird genau einer der folgenden Impacts geführt:

| Impact | Bedeutung |
|---|---|
| `none` | keine releasewirksame Vertrags- oder Fähigkeitsänderung |
| `patch` | kompatible Korrektur ohne neue Fähigkeit oder Vertragsfläche |
| `minor` | kompatible neue Fähigkeit, Vertragserweiterung oder neu qualifizierter Lieferpfad |
| `major` | inkompatible öffentliche Vertrags-, Artefaktformat- oder Upgradepfadänderung |

Bei mehreren Änderungen gilt je Dimension der höchste verbleibende Impact.

### 6.2 Foundation-Phase `0.x`

Während der Foundation-Phase `0.x` bleibt `major` die fachliche Kennzeichnung einer inkompatiblen Änderung. Numerisch wird eine solche Änderung mindestens durch den nächsten Minor-Stand dargestellt und MUSS ausdrücklich in einer akzeptierten ADR oder Governance-Entscheidung benannt werden.

Eine Freigabe `1.0.0` benötigt eine separate Readiness-Entscheidung. Sie wird nicht allein durch Erreichen eines bestimmten Funktionsumfangs oder einer Patchnummer ausgelöst.

### 6.3 Kompatibilität

Kompatibilität wird aus der Sicht der unterstützten Konsumenten bewertet. Dazu gehören je nach Scope:

- Java- und HTTP-Verträge,
- maschinenlesbare Contracts und Schemas,
- Tool-CLI und Reportformate,
- Patch- und Distributionsartefakte,
- Templates und generierte Projektstruktur,
- Managed-Project-Updateprofile und Migrationspfade.

Eine Änderung ist nicht allein deshalb kompatibel, weil Springmaster selbst kompiliert.

### 6.4 Rücknahme vor Release

Wird eine noch unveröffentlichte Änderung vollständig zurückgenommen und verbleibt keine Vertrags-, Daten-, Migrations- oder Evidence-Wirkung, kann ihre Versionsempfehlung entfallen.

Nach Veröffentlichung wird ein Release niemals rückwirkend umversioniert. Jede Korrektur erhält eine neue Version.

## 7. Zuordnung von Änderungen zu Versionsdimensionen

| Änderung | Mindestens zu bewertende Dimension |
|---|---|
| Core-Code oder veröffentlichter Core-Vertrag | Core und Plattform |
| Patch-, Export-, Build-, DBTool-, Gate- oder Release-Tool | Tooling und Plattform |
| Project-New-Generator | Tooling und Plattform; Template zusätzlich bei geändertem Output |
| Projektskeleton oder Templatevertrag | Template und Plattform |
| Demo- oder Referenzfähigkeit | Demo und Plattform |
| Managed-Project-Planung, Kompatibilität oder Delivery | Update und Plattform |
| aktive Governance-, Standard- oder Contract-Semantik | Plattform; zusätzlich die ausführbar betroffene Komponente |
| Runtime- oder Build-Dependency | betroffene Komponente und Plattform |
| reine informative oder redaktionelle Korrektur | `none`, sofern keine Status-, Vertrags- oder Governancewirkung entsteht |
| Draft-Dokument ohne aktive Regelwirkung | grundsätzlich `none`, sofern kein Tooling- oder Contractverhalten geändert wird |

Eine Governance- oder Standardänderung ohne eigene Komponentenimplementierung kann die aggregierte Plattform-Version verändern, ohne jede Komponenten-Version zu erhöhen.

Ändert eine normative Quelle zugleich ausführbares Gate-, Template-, Tooling- oder Updateverhalten, MUSS die entsprechende Komponenten-Version bewertet werden.

## 8. Version Recommendation während Changes und Sprints

Jeder releasewirksame Change führt den erwarteten Impact je betroffener Dimension als Empfehlung.

Die Empfehlung:

- wird aus Scope, Vertrag und Konsumentenwirkung abgeleitet,
- ist Bestandteil der Engineering-Evidence,
- wird bei Drift oder Scopeänderung aktualisiert,
- wird im Sprintstatus aggregiert,
- wird im Completion Report begründet,
- erhöht noch keine Versionsdatei.

Ein Sprintabschluss empfiehlt den resultierenden Impact. Er legt weder die endgültige Version noch eine Releasefreigabe fest.

Fehlt für eine materiell releasewirksame Änderung eine begründete Versionsempfehlung, ist der Change nicht engineering-complete.

## 9. Version Closure

### 9.1 Zweck

Version Closure legt die für einen Releasekandidaten geltenden Versionswerte atomar fest.

Sie erfolgt erst, wenn:

- der Kandidat fachlich und technisch vollständig abgegrenzt ist,
- alle enthaltenen Changes und Sprints geschlossen oder bewusst ausgeschlossen sind,
- die akkumulierten Impacts geprüft sind,
- keine ungeklärte Versions- oder Kompatibilitätsdrift besteht.

### 9.2 Release-closing Change

Ein begrenzter Release-closing Change:

1. wendet die bestätigten Komponenten-Inkremente genau einmal an,
2. erhöht `PLATFORM_VERSION` passend zum aggregierten Releaseimpact,
3. synchronisiert die Maven-Snapshot-Koordinate,
4. setzt `PLATFORM_STATE_PATCH`,
5. aktualisiert erforderliche Kompatibilitäts- und Releasecontracts,
6. führt die zugehörigen Version- und Konsistenzprüfungen aus.

Ein Release-closing Change darf keine unabhängigen Features, Refactorings oder fachfremden Bereinigungen enthalten.

### 9.3 Kein Release ohne neue Version

Ein neuer veröffentlichter Release benötigt eine neue Releaseversion. Ist kein releasewirksamer Impact vorhanden, wird kein künstlicher Release nur zur Archivierung eines Commits erzeugt.

### 9.4 Änderungen nach Closure

Jede inhaltliche Änderung nach Version Closure macht den bisherigen Kandidaten ungültig. Danach sind Impact, Version Closure und Qualification erneut auszuführen.

## 10. Release Readiness

Ein Releasekandidat ist ready für vollständige Qualification, wenn mindestens gilt:

- der Working Tree ist sauber und committed,
- Version Closure ist vollständig und konsistent,
- Engineering Completion der enthaltenen Changes ist nachgewiesen,
- erforderliche Sprint-Closures liegen vor,
- anwendbare strict-Gates sind bestanden,
- keine Tool Errors bestehen,
- erforderliche Tests und Test Completion sind bestanden,
- Dependency-, Lizenz- und Vulnerability-Befunde sind freigabefähig,
- aktive Dokumentation, ADRs, Standards und Contracts sind konsistent,
- offene Waiver, Deviations, Deferrals und Findings sind für den Release bewertet,
- erforderliche Migrations- und Rückrollpfade sind dokumentiert,
- Project-New- und Managed-Project-Auswirkungen sind bewertet,
- ein vollständiger Qualification-Lauf ist technisch ausführbar.

Ein dokumentierter Sprintabschluss allein begründet keine Release Readiness.

## 11. Release Qualification

### 11.1 Grundsätze

Qualification wird gegen einen konkreten sauberen Git-Commit und die geschlossene Versionswahrheit ausgeführt.

Ein vollständiger Lauf MUSS mindestens nachweisen:

- Documentation Gate,
- anwendbare Quality Gates,
- vollständigen Maven-Qualifikationslauf,
- Tooling-Selfcheck,
- erforderliche Test- und Acceptance-Profile,
- SBOM-Erzeugung,
- Full Export und Integritätsprüfung,
- Versions- und Manifestkonsistenz,
- Project-New-Acceptance, wenn Template oder Generator betroffen sind,
- Managed-Project-Kompatibilität und erforderliche read-only Piloten, wenn Update- oder Deliveryverträge betroffen sind.

Der Build and Tooling Standard bestimmt die technischen Ausführungs- und Reportverträge. Solange der bestehende `release-qualify.sh` nur `mvn test` statt des vollständigen Buildvertrags ausführt, ist für V2-Releaseevidence zusätzlich `mvn clean verify` nachzuweisen oder das Werkzeug vor Aktivierung dieser Governance anzupassen.

### 11.2 Diagnostische Auslassungen

Optionen wie `--skip-maven`, `--skip-tooling` oder `--no-export` sind ausschließlich diagnostisch.

Ein Manifest mit ausgelassener Pflichtprüfung:

- MUSS als unvollständig gekennzeichnet werden,
- DARF nicht als Releasefreigabeevidence verwendet werden,
- DARF keinen Tag- oder Publish-Schritt autorisieren.

### 11.3 Reproduzierbarkeit

Qualification MUSS folgende Identitäten und Quellen festhalten:

- Releaseversion,
- `platform.env`-Werte,
- Git-Commit,
- vorgeschlagenen Git-Tag,
- ausgeführte Checks und deren Status,
- Export- und Artefakthashes,
- Release-Manifest- und Contractversion,
- relevante SBOM- und Kompatibilitätsnachweise.

Absolute lokale Pfade sind keine portable Releaseidentität.

## 12. Release Manifest und Qualification-Status

Das Release Manifest ist die maschinenlesbare Evidence einer konkreten Qualification. Es ersetzt weder die normative Releaseentscheidung noch den Git-Tag.

Mindestens folgende Qualification-Status müssen unterscheidbar sein:

| Status | Bedeutung |
|---|---|
| `QUALIFIED` | alle verpflichtenden Qualification-Prüfungen bestanden |
| `INCOMPLETE` | mindestens eine Pflichtprüfung ausgelassen oder noch nicht vollständig |
| `FAILED` | Qualification ausgeführt, aber mindestens eine blockierende Prüfung fehlgeschlagen |
| `TOOL_ERROR` | Qualification oder Manifest konnte nicht verlässlich erzeugt werden |

Der bestehende Manifestvertrag V1 kennt technisch `QUALIFIED` und `INCOMPLETE`. `FAILED` und `TOOL_ERROR` werden bis zu einer Contract-Erweiterung durch den fehlgeschlagenen Qualification-Lauf und dessen Evidence repräsentiert; sie dürfen nicht als erfolgreiches Manifest materialisiert werden.

Ein Release Manifest MUSS unverändert an den qualifizierten Commit gebunden sein. Eine Regeneration nach Änderungen erzeugt neue Evidence und erfordert erneute Qualification.

## 13. Releaseentscheidung

### 13.1 Entscheidungswerte

Nach vollständiger Qualification wird der Kandidat ausdrücklich bewertet als:

- `approved`,
- `deferred`,
- `rejected`.

`approved` setzt `QUALIFIED` voraus. Ein `INCOMPLETE`-Kandidat kann nur `deferred` oder `rejected` werden.

### 13.2 Freigabeverantwortung

Eine Releasefreigabe benötigt einen autorisierten Springmaster-Maintainer. Zusätzliche Freigaben bleiben erforderlich, wenn der Release:

- eine akzeptierte ADR voraussetzt,
- kritische Security- oder Datenwirkung besitzt,
- eine neue Managed-Project-Deliveryklasse eröffnet,
- eine Major- oder `1.0.0`-Entscheidung enthält.

Die Freigabe MUSS den konkreten Commit, die Releaseversion und das Release Manifest identifizieren. Eine allgemeine Sprint- oder Patchfreigabe genügt nicht.

### 13.3 Restpunkte

Nicht blockierende Findings, Waiver und Deferrals dürfen nur übernommen werden, wenn:

- ihre Releasewirkung bewertet ist,
- Owner und Reviewdatum bestehen,
- keine falsche Security-, Persistence-, Compatibility- oder Reifebehauptung entsteht,
- die Quality Gate Governance sie zulässt.

## 14. Tagging, Veröffentlichung und Unveränderbarkeit

### 14.1 Tagging

Das Release Manifest schlägt den exakten Tag `springmaster-v<release-version>` vor.

Der Tag wird erst nach Releasefreigabe erzeugt. Tagging und Push bleiben getrennte, ausdrückliche Aktionen.

Ein Tag MUSS auf genau den qualifizierten und freigegebenen Commit zeigen. Bereits verwendete Release-Tags dürfen nicht umgebogen oder wiederverwendet werden.

### 14.2 Veröffentlichung

Die Veröffentlichung umfasst nur ausdrücklich freigegebene Artefakte. Ein Full Export ist nicht automatisch ein öffentliches Binärrelease, und ein Git-Tag publiziert nicht automatisch Maven-Artefakte.

Jede Distributionsform benötigt:

- eindeutige Releaseversion,
- Source-Commit und Tag,
- Artefakthash,
- Release Manifest,
- SBOM, soweit anwendbar,
- definierten Ablage- und Retentionpfad.

### 14.3 Unveränderbarkeit

Veröffentlichte Releases, Tags, Manifeste und Patchartefakte sind unveränderbar.

Ein neu gebautes oder in Bytes verändertes Artefakt erhält eine neue Artefaktidentität. Eine inhaltliche Produktkorrektur erhält zusätzlich eine neue Releaseversion.

### 14.4 Keine zweite Produktwahrheit

Release Manifest, Export, SBOM und Release Notes sind Evidence und Distribution. Die aktuelle Entwicklungswahrheit bleibt in Git und den kanonischen Versionsquellen.

## 15. Hotfixes und Korrekturen

Ein Hotfix:

- startet von einem eindeutig identifizierten veröffentlichten Stand,
- besitzt einen eng begrenzten Korrekturscope,
- bewertet jede betroffene Versionsdimension neu,
- erhält eine neue Releaseversion, ein neues Manifest und einen neuen Tag,
- durchläuft alle für Risiko und Scope verpflichtenden Integritäts-, Security- und Vertragsprüfungen.

Ein kompatibler Hotfix verwendet in der Regel `patch`. Enthält die Korrektur eine neue Fähigkeit oder inkompatible Wirkung, gilt der tatsächliche höhere Impact; die Bezeichnung Hotfix reduziert ihn nicht.

Eine beschleunigte Behandlung darf nicht auslassen:

- saubere Baseline,
- Version Closure,
- betroffene Regressionstests,
- Documentation- und Quality-Gates,
- Tool-Error-Behandlung,
- Artefakt- und Exportintegrität,
- ausdrückliche Releaseentscheidung.

Nicht anwendbare breite Prüfungen können risikobasiert begründet entfallen. Pflichtprüfungen des betroffenen Vertrags dürfen nicht übersprungen werden.

## 16. Project-New und Templates

Ändert ein Release Project-New oder erzeugte Projektinhalte, müssen mindestens bewertet und qualifiziert werden:

- `PLATFORM_TOOLING_VERSION`,
- `PLATFORM_TEMPLATE_VERSION`,
- Fresh-Project-Erzeugung,
- Build, Tests und Governance-Gates des erzeugten Projekts,
- installierte Versions- und Adoptionsevidence,
- Migrationswirkung für bereits erzeugte Projekte.

Eine Generatoränderung ohne Outputänderung betrifft nicht automatisch die Template-Version. Eine Output- oder Templatevertragsänderung betrifft die Template-Version auch dann, wenn der Generatorcode unverändert bleibt.

## 17. Gemanagte Projekte und Kompatibilität

Ein Springmaster-Release gewährt keine implizite Kompatibilität für alle gemanagten Projekte.

Für jede unterstützte Kombination aus:

- Quellrelease,
- Target-Baseline,
- Updateprofil,
- Komponentenständen,
- Migrationspfad

muss die Kompatibilität durch Matrix oder qualifizierten Plan ausgewiesen sein.

Downgrades und Cross-Major-Übergänge sind standardmäßig verboten. Unterstützung älterer Governance- oder Contract-Stände besteht nur, wenn sie ausdrücklich beschrieben und getestet ist.

Ein Release mit Änderung an `PLATFORM_UPDATE_VERSION` MUSS die betroffenen Kompatibilitätsprofile und mindestens einen geeigneten read-only Zielprojektbefund qualifizieren. Eine reale Target-Mutation bleibt ein separater autorisierter Vorgang.

Target Apply aktualisiert Payload und Managed State einschließlich installierter Versionen atomar. Eine nachgelagerte, unabhängige Version-Closure im Zielprojekt ist kein zulässiger Regelbetrieb.

## 18. Technische Ableitungen und Evidence

Diese Governance wird mindestens durch folgende technische Quellen und Artefakte konkretisiert:

- `platform/versions/platform.env`,
- Maven-Version- und Runtime-Projektionsprüfung,
- Release-Qualification-Contract,
- Release-Manifest-Schema,
- Kompatibilitätsmatrix und Compatibility Decisions,
- SBOM und Artefakthashes,
- `release-qualify.sh` und `release-manifest.py`,
- Fresh-Project- und Managed-Project-Qualification-Evidence.

Ein künftiger `release-qualification-contract` MUSS mindestens definieren:

- verpflichtende Checks je Releaseprofil,
- Status- und Aggregationssemantik,
- Manifestfelder und Schema-Version,
- Evidence- und Retentionanforderungen,
- Tag- und Publish-Voraussetzungen,
- zulässige diagnostische Auslassungen.

Technische Contracts konkretisieren Werte und Formate. Sie dürfen keine von dieser Governance abweichende Freigabelogik etablieren.

## 19. Übergang und Supersession

### 19.1 Bestehende Quellen

Bis zur Aktivierung dieser Governance bleiben folgende Quellen gültig:

- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`,
- `PROJECT_DOCS/GOVERNANCE/SPRINT_RELEASE_GOVERNANCE.md`,
- `PROJECT_DOCS/CONCEPT/PLATFORM_VERSION_TRUTH.md`,
- `PROJECT_DOCS/TOOLING/RELEASE_QUALIFICATION.md`,
- `platform/versions/platform.env`,
- Release-Manifest- und Qualification-Tooling.

Bei Aktivierung soll diese Governance die normative Versions- und Release-Semantik aus `SPRINGMASTER_VERSION_POLICY.md` und `SPRINT_RELEASE_GOVERNANCE.md` konsolidiert ablösen. `PLATFORM_VERSION_TRUTH.md` bleibt als technisches Konzept zur kanonischen Quelle bestehen. `RELEASE_QUALIFICATION.md` bleibt als praktischer Guide bestehen und wird an den aktiven Contract angepasst.

Die Supersession darf erst erfolgen, wenn:

- alle relevanten Aussagen reconciled sind,
- die Dokumentstatus atomar aktualisiert werden,
- der Index aktualisiert ist,
- Release-Tooling und Contracts die aktiven Pflichtprüfungen abbilden,
- positive, negative und Tool-Error-Fixtures bestehen.

### 19.2 Aktuelle Implementierungslücken

Vor Aktivierung sind mindestens zu schließen oder ausdrücklich zu deferieren:

- vollständiger Maven-Release-Lauf gegenüber der aktuellen `mvn test`-Baseline,
- explizite Release-Contract- und Manifest-Schema-Governance,
- definierte Release-Evidence-Retention,
- öffentliche Core-API-Fläche für Kompatibilitätsgarantien,
- Vulnerability-Fristen und Freigabekriterien,
- gegebenenfalls erweiterte Manifeststatus für `FAILED` und `TOOL_ERROR`.

Diese Lücken machen den Draft nicht widersprüchlich. Sie verhindern jedoch eine unbelegte V2-Releasequalifikationsbehauptung.

## 20. Offene Entscheidungen

| Decision ID | Entscheidung | Blockiert |
|---|---|---|
| `GOV-DEC-012` | öffentliche Core-API mit Kompatibilitätsgarantie | API-Compatibility-Contract und Major-Bewertung |
| `GOV-DEC-016` | Behebungs- und Reviewfristen je Vulnerability-Kritikalität | Security- und Releasefreigabekriterien |
| `GOV-DEC-017` | kleinster reproduzierbarer Dependency-, License- und Vulnerability-Toolstack | vollständiges Dependency-/Release-Gate |
| `GOV-DEC-023` | dauerhafter portabler Ablage- und Retentionpfad für Releaseevidence | Release-Qualification-Contract und Publish-Prozess |

Die Releasefreigabe durch einen autorisierten Springmaster-Maintainer sowie die Versionswirkung von Draft-, Governance- und Contractänderungen sind mit dieser Governance entschieden.

## 21. Kanonische Ausgaben und Abnahmekriterien

Diese Governance erzeugt oder kontrolliert ausschließlich:

- Versionsquellen- und Dimensionsmodell,
- SemVer-Impact und Versionszuordnung,
- Version Recommendation und Version Closure,
- Release Readiness und Release Qualification,
- Releaseentscheidung,
- Tagging-, Veröffentlichungs- und Unveränderbarkeitsregeln,
- Hotfix- und Korrekturregeln,
- Releasewirkung auf Project-New und gemanagte Projekte.

Sie besitzt keine konkreten Testfälle, Toolimplementierungen, Dependency-Listen, Directory-Allowlist oder Target-Mutationskommandos.

Die Governance ist abnahmefähig, wenn:

1. alle Versions- und Provenienzidentitäten getrennt sind,
2. `platform.env` als kanonische Versionsquelle feststeht,
3. alle bestehenden Versionsdimensionen eindeutig zugeordnet sind,
4. jede Änderung einen SemVer-Impact erhalten kann,
5. Draft, Sprintempfehlung, Version Closure und Releasefreigabe getrennt sind,
6. ein Release nur von sauberem committed Stand qualifiziert wird,
7. vollständige Qualification und diagnostische Auslassung unterscheidbar sind,
8. Tool Errors und unvollständige Evidence keinen Release autorisieren,
9. Release Manifest, Tag und Veröffentlichung getrennt sind,
10. veröffentlichte Releases und Artefakte unveränderbar sind,
11. Hotfixes keine Integritäts- oder Sicherheitsprüfung umgehen,
12. Project-New- und Managed-Project-Auswirkungen verpflichtend bewertet werden,
13. bestehende Version- und Releasequellen kontrolliert supersediert werden können,
14. technische Contracts und Tooling eindeutig ableitbar sind.

## 22. Referenzen

- Documentation Governance
- Engineering Governance
- Sprint Governance
- Quality Gate Governance
- Test Governance
- Dependency Governance
- Managed Project Governance
- Build and Tooling Standard
- Java Architecture Standard
- ADR-0012 Patch Transaction and Evidence Boundary
- Platform Version Truth
- Springmaster Version Policy
- Sprint and Release Governance
- Release Qualification
- Patch Manifest V2
- Platform Update Version Compatibility

## 23. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | - | draft | Konsolidierter Entwurf für Versionswirkung, Release Qualification und Freigabe erstellt |

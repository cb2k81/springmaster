---
documentId: DOC-GOV-0002
title: Project Directory Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/project-structure
appliesTo:
  - springmaster
  - project-new
  - generated-projects
  - managed-projects
owner: springmaster-maintainers
createdAt: 2026-07-22
validFrom: null
lastReviewedAt: null
reviewBy: null
supersedes: []
supersededBy: null
temporary: false
sprintId: null
---

# Project Directory Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt die physische Struktur von Springmaster, Project-New, erzeugten Projekten und gemanagten Projekten.

Sie bestimmt:

- zulässige Root-Dateien und Root-Verzeichnisse,
- kanonische Eigentümerpfade für Inhalts- und Artefaktklassen,
- zulässige Dateitypen und Unterstrukturen,
- Source-, Generated-, Runtime-, Temporary-, Historical- und Migrationspfade,
- kontrollierte Extension Points,
- Regeln gegen Duplikate, Parallelstrukturen und Arbeitsreste,
- den Prozess für Strukturänderungen und Migrationen,
- Anforderungen an den maschinenlesbaren Directory Contract und das Directory Gate.

Die Governance schützt den realen Bestand vor Strukturdrift. Sie verlangt keine sofortige Idealstruktur: technisch gekoppelte Bestandsablagen werden zunächst klassifiziert und nur in eigenen qualifizierten Änderungsschnitten migriert.

## 2. Nicht Gegenstand

Nicht hier geregelt werden:

- Dokumenttypen, Metadaten und Dokumentstatus: Documentation Governance,
- Java-Package-, Layer- und Sichtbarkeitsregeln: Java Architecture Standard,
- allgemeine Gate-, Finding-, Baseline- und Promotion-Semantik: Quality Gate Governance,
- Testmethodik und Fixture-Inhalte: Test Governance und Testing Standard,
- fachliche Inhalte einzelner Contracts oder Templates,
- Managed-Project-Adoption und Deviations im Detail: Managed Project Governance.

Diese Governance besitzt die physische Pfadzuordnung. Die inhaltliche Bedeutung verbleibt bei der jeweils zuständigen Governance, ADR, Standard- oder Contract-Quelle.

## 3. Grundsätze

### 3.1 Default Deny

Neue Root-Inhalte, nicht registrierte Verzeichnisse und neue Inhaltsklassen sind standardmäßig verboten. Zulässig sind nur:

- im Directory Contract registrierte Pfade,
- registrierte Extension Points,
- definierte generierte oder temporäre Pfade,
- einzeln erfasste Übergangspfade einer kontrollierten Directory Transition Baseline.

Physische Existenz in einem Export oder Arbeitsverzeichnis begründet keine Zulässigkeit.

### 3.2 Ein kanonischer Eigentümerpfad

Jede Inhalts- und Artefaktklasse besitzt genau einen kanonischen Eigentümerpfad. Andere Pfade dürfen sie nur als registrierte Ableitung, Distribution, Test-Fixture, vendorte Ressource oder historische Momentaufnahme enthalten.

Manuell parallel gepflegte Wahrheiten sind nicht zulässig.

### 3.3 Bestand vor Idealstruktur

Vor einer Verschärfung oder Migration müssen tatsächlicher Git-Bestand, Aufrufer, Export- und Patchkopplungen, Tests, Project-New und Platform Update geprüft werden.

Ein Zielbild darf einen funktionsfähigen Bestand nicht allein wegen einer idealisierten Pfadordnung blockieren.

### 3.4 Source, Generated und Runtime trennen

Versionierte Quellen, erzeugte Artefakte, Runtime-Zustände und temporäre Arbeitsstände müssen durch Pfad, Contract und Git-Regeln unterscheidbar sein.

Ein generierter oder temporärer Pfad darf nicht still zum Source-Pfad werden.

### 3.5 Read-only-Prüfung

Directory Gates dürfen Quelldateien nicht automatisch verschieben, umbenennen, löschen oder normalisieren. Strukturkorrekturen erfolgen nur durch einen sichtbaren Engineering- oder Migrationsschnitt.

### 3.6 Profilgerechte Struktur

Springmaster, Template-Quelle, erzeugtes Projekt und gemanagtes Projekt verwenden gemeinsame Prinzipien, aber nicht zwingend denselben Verzeichnisbaum.

## 4. Projektprofile

| Profil | Zweck | Besondere Strukturwirkung |
|---|---|---|
| `springmaster-source` | Tooling Source, Platform Core, Referenzanwendung, Standard- und Update-Quelle | darf Springmaster-spezifische Tooling-, Template-, Patch- und Update-Bereiche besitzen |
| `project-new-template-source` | in Springmaster eingebettete Quelle für neue Projekte | wird nur über Project-New materialisiert; ist kein eigenes Repositoryprofil |
| `generated-project` | frisch erzeugtes Fachprojekt | enthält nur lokale Build-, Source-, Test-, Contract- und Governance-Grundlagen |
| `managed-project` | bestehendes adoptiertes Projekt | darf registrierte lokale Ergänzungen und genehmigte Deviations besitzen |

Jeder Contract-Eintrag muss angeben, für welche Profile er gilt. Ein Springmaster-Pfad ist nicht automatisch in einem erzeugten oder gemanagten Projekt zulässig.

Der aktuelle Template-Source-Pfad `PROJECT_DOCS/TEMPLATES/project-skeleton/` bleibt während der Transition gültig. Eine Verschiebung ist ein eigener Migrationsschnitt.

## 5. Machine-Readable Project Directory Contract

### 5.1 Kanonischer Vertrag

Die technisch prüfbaren Strukturregeln werden in einem maschinenlesbaren Project Directory Contract geführt. Für die Transition ist der bestehende Contract-Bereich zu verwenden, beispielsweise:

```text
contracts/governance/project-directory-contract.json
```

Pro Profil und Version darf nur ein aktiver kanonischer Vertrag gelten.

### 5.2 Mindestinhalt

Der Contract definiert mindestens:

- Schema- und Contract-Version,
- Projektprofile,
- erlaubte Root-Dateien und Root-Verzeichnisse,
- Bereichsdeskriptoren und Unterverzeichnismuster,
- erlaubte und verbotene Dateitypen,
- Pfad- und Lifecycle-Klassen,
- Commit- und Generierungsregeln,
- kanonische Eigentümerpfade,
- Extension Points,
- zulässige Ableitungen und Duplikate,
- Naming-, Case- und Symlink-Regeln,
- Directory Transition Baseline und Managed-Project-Deviations.

### 5.3 Bereichsdeskriptor

Jeder registrierte Bereich besitzt mindestens:

- Bereichs-ID und Pfadmuster,
- Zweck und Owner,
- anwendbare Projektprofile,
- erlaubte Inhalts- und Dateitypklassen,
- Pfadklasse und Lifecycle,
- Source-, Generated- oder Runtime-Eigenschaft,
- Commitfähigkeit,
- Unterverzeichnis- und Extension-Point-Regel,
- kanonische Herkunft bei Ableitungen.

Toolskripte, Exportprofile, `.gitignore`, Buildprofile und Gates müssen aus dem Contract ableitbar oder dagegen prüfbar sein. Sie dürfen keine zweite Strukturregel etablieren.

## 6. Root-Allowlist

### 6.1 Verifizierte sichtbare Ausgangsbasis

Der verifizierte Springmaster-Snapshot enthält:

```text
AGENTS.md
README.md
export.config.json
pom.xml
PROJECT_DOCS/
bin/
contracts/
docs/
patches/
platform/
src/
```

Die endgültige Root-Allowlist muss vor Aktivierung gegen `git ls-files`, den tatsächlichen Working Tree und versteckte Root-Dateien geprüft werden.

### 6.2 Versteckte Dateien

Versteckte Root-Dateien sind nur einzeln oder über enge Contract-Muster zulässig. Allgemeine Freigaben wie `.*` sind nicht erlaubt.

Lokale Secrets wie `.env` sind nicht commitfähig. Öffentliche Beispiele wie `.env.example` benötigen einen registrierten Zweck.

### 6.3 Generierte Root-Pfade

Erzeugte oder lokale Root-Pfade können zulässig sein, ohne Source-Bereiche zu sein. Der bestehende Tooling-Vertrag verwendet insbesondere:

```text
target/
build/
tmp/
exports/
```

Diese Pfade müssen als generated oder temporary registriert und durch Git-Hygiene abgesichert sein.

### 6.4 Neue Root-Inhalte

Ein neuer Root-Pfad benötigt:

1. eigenständigen Zweck und Owner,
2. Inhalts-, Dateityp-, Lifecycle- und Commitregeln,
3. Begründung gegen vorhandene Bereiche und Extension Points,
4. Auswirkungen auf Export, Patch-Scopes, Project-New und Managed Projects,
5. Contract- und Gate-Anpassung,
6. gegebenenfalls ADR oder Governance-Änderung.

Ein neuer Root-Pfad darf nicht als Nebenwirkung eines fachlichen Patches entstehen.

## 7. Kanonische Springmaster-Bereiche

| Bereich | Kanonischer Zweck | Besondere Regel |
|---|---|---|
| Root-Dateien | repositoryweite Einstiege und Konfiguration | jede weitere Datei einzeln registrieren |
| `PROJECT_DOCS/` | menschlich gepflegte Projektdokumentation | Dokumentsemantik folgt Documentation Governance |
| `contracts/` | versionierte maschinenlesbare Verträge und Registries | neue Familie nur bei eigenständigem Scope und Lifecycle |
| `bin/` | repositoryweite ausführbare Einstiegspunkte und gemeinsame Bibliotheken | flacher Bestand mit `bin/lib/` bleibt zunächst erhalten |
| `src/main/` | Produktcode und Runtime-Ressourcen | Package-Regeln folgen Java Architecture Standard |
| `src/test/` | Testcode, Fixtures und Testressourcen | Tooling-Fixtures bevorzugt unter `src/test/resources/tooling/` |
| `platform/` | Plattformversionen, Distributions- und Update-Quellen | komponentenlokale `tools/` und `tests/` sind zulässig |
| `patches/` | Patch-Quellen, Runtime-Artefakte und Legacy-Provenienz | Unterbereiche müssen getrennt klassifiziert werden |
| `docs/` | bestehender Legacy-Dokumentbereich | `legacy-accepted`, für neue dauerhafte Wahrheiten `forbidden-new` |

### 7.1 Root-Dateien

Der aktuelle sichtbare Bestand verwendet:

- `AGENTS.md` als kompakten Arbeits- und Sicherheitseinstieg,
- `README.md` als Projektübersicht,
- `pom.xml` als Maven-Buildvertrag,
- `export.config.json` als Exportkonfiguration.

### 7.2 `PROJECT_DOCS/`

Neue technische Contract Sources, Templates oder Runtime-Evidence dürfen nicht unter `PROJECT_DOCS/` entstehen, sofern ein aktiver Contract sie nicht ausdrücklich als qualifizierte Übergangsklasse oder technische Ableitung zulässt.

Die physische Zuordnung von Dokumenttypen zu Unterpfaden steht im Directory Contract; Dokumenttyp und Lifecycle stehen in der Documentation Governance.

### 7.3 `contracts/`

Bestehende Familien sind:

```text
configuration/
core/
database/
governance/
observability/
```

Ein einzelner neuer Vertrag rechtfertigt nicht automatisch eine neue Familie.

### 7.4 `bin/` und komponentenlokales Tooling

Die Governance-Einführung organisiert `bin/` nicht pauschal in neue Unterbäume um. Komponentenlokale Implementierungen dürfen beim Owner der Komponente liegen; `platform/update/tools/` und `platform/update/tests/` sind dafür ein bestehendes Muster.

### 7.5 `patches/`

Der Contract muss mindestens unterscheiden zwischen:

- versionierten Patch-Templates und Toolquellen,
- historischer Legacy-Provenienz wie `patches/logs/**/CHANGELOG-*.md`,
- lokalen oder generierten Pfaden wie `patches/runtime/`, `patches/archives/`, `patches/logs/accept/` und `patches/logs/validation/`.

Physische Präsenz im Snapshot beweist keine Commitfähigkeit.

### 7.6 `docs/`

Die vorhandenen Dokumente werden einzeln als Migration nach `PROJECT_DOCS/`, historisches Archiv oder dauerhaft separater Bestand entschieden. Jede Verschiebung muss Exportprofile, Patch-Scopes, Index und Referenzen mitändern.

## 8. Pfadklassen und Canonical Ownership

### 8.1 Pfadklassen

Jeder registrierte Pfad besitzt eine primäre Pfadklasse:

| Pfadklasse | Bedeutung |
|---|---|
| `canonical-source` | manuell gepflegte kanonische Quelle |
| `canonical-generated` | deterministisch erzeugte kanonische Ableitung |
| `extension-point` | kontrolliert erweiterbarer Bereich |
| `legacy-accepted` | bestehender Übergangsbestand ohne Zielbestätigung |
| `migration-candidate` | bestehender Pfad mit geplantem Zielwechsel |
| `runtime-observed` | zulässiger lokaler Runtime- oder Evidence-Pfad |
| `temporary` | kurzfristiger Arbeitsstand mit Bereinigungspflicht |
| `historical` | unveränderliche historische Provenienz |
| `forbidden-new` | bestehende Instanzen toleriert, neue verboten |

Pfadklasse, Commitfähigkeit und tatsächliches Git-Tracking sind getrennte Eigenschaften.

### 8.2 Inhaltsklassen

Der Contract muss kanonische Owner mindestens für folgende Klassen benennen:

- Dokumentation, ADRs und Standards,
- maschinenlesbare Contracts,
- Produktcode und Runtime-Ressourcen,
- Testcode und Test-Fixtures,
- Project-New-Templates,
- Platform-Update-Regeln und Target-Deskriptoren,
- Patch-Toolquellen und Provenienz,
- Reports, Exporte und Buildausgaben.

### 8.3 Ableitungen

Eine abgeleitete Kopie ist nur zulässig, wenn sie:

- einen kanonischen Ursprung nennt,
- technisch erzeugt oder ausdrücklich qualifiziert ist,
- nicht parallel manuell gepflegt wird,
- eine definierte Aktualisierungs- und Löschregel besitzt.

Project-New und Platform Update dürfen Inhalte in andere Zielpfade materialisieren. Die Quell-zu-Ziel-Zuordnung muss in Template- oder Update-Contracts eindeutig sein.

Vendorte Inhalte benötigen Herkunft, Version, Lizenz, Updateverantwortung und lokalen Owner.

## 9. Extension Points

Ein Extension Point definiert:

- Unterpfadmuster und Naming-Regel,
- erlaubte Inhalts- und Dateitypen,
- Owner-Regel,
- gegebenenfalls maximale Verschachtelung,
- Verbot konkurrierender kanonischer Inhalte,
- erforderliche Registrierung oder automatische Ableitbarkeit.

Mögliche Extension Points sind nach Contract-Prüfung insbesondere:

- fachliche Unterbereiche in `PROJECT_DOCS/STANDARDS/`,
- Contract-Familien unter `contracts/`,
- zugelassene Source-Namespaces,
- Fixture-Familien unter `src/test/resources/tooling/`,
- Komponentenbereiche unter `platform/update/`.

Ein Unterverzeichnis innerhalb eines Extension Points darf keine neue Inhaltsklasse oder Autorität einführen, die vom übergeordneten Bereich nicht gedeckt ist.

## 10. Naming, Dateitypen und technische Hygiene

### 10.1 Namen

Namen müssen stabil, eindeutig und zum Bereich passend sein. Verboten sind insbesondere:

- `final-final`, `new`, `copy`, `tmp2`,
- unregistrierte Revisionskopien,
- Backups mit `.bak`, `.old`, `.orig`, `.copy`,
- Editor- und Betriebssystemartefakte.

Dokument-, ADR-, Sprint- und Reportnamen konkretisiert die jeweils zuständige Governance.

### 10.2 Case-Regeln

Der Contract definiert die Case-Regel je Bereich. Pfade, die sich nur durch Groß-/Kleinschreibung unterscheiden, sind verboten.

### 10.3 Dateitypen

Erlaubte und verbotene Dateitypen werden pro Bereich registriert. Die Endung allein beweist keine korrekte Inhaltsklasse: JSON kann beispielsweise Contract, Fixture oder generierte Evidence sein.

### 10.4 Leere Verzeichnisse

Leere Source-Verzeichnisse sollen nicht vorsorglich angelegt werden. Erforderliche Platzhalter wie `.gitkeep` müssen ausdrücklich zugelassen sein.

### 10.5 Symlinks

Symlinks sind standardmäßig verboten. Eine Ausnahme benötigt eine explizite Allowlist und muss sicherstellen, dass Ziel, Scope, Sandbox-, Export-, Patch- und Update-Verhalten deterministisch und sicher sind. Defekte oder externe Symlinks sind unzulässig.

## 11. Temporäre, generierte und lokale Artefakte

Temporäre und generierte Artefakte dürfen nur in registrierten Pfaden entstehen. Dazu gehören abhängig vom Profil insbesondere:

```text
target/
build/
tmp/
exports/
patches/runtime/
patches/archives/
patches/logs/accept/
patches/logs/validation/
platform/update/generated/
platform/update/manifests/
```

Für jeden Pfad muss geregelt sein, ob Inhalte:

- nie committed werden dürfen,
- nur als qualifizierte Evidence commitfähig sind,
- oder als deterministische Ableitung versioniert werden.

Eine `.gitignore`-Regel ersetzt diese Klassifikation nicht.

Runtime- und temporäre Pfade benötigen eine Retention- oder Bereinigungsregel. Fehlt ein vorgesehener Runtime-Pfad oder ist er nicht beschreibbar, darf ein Tool nicht in Source- oder Dokumentationsbereiche ausweichen; es muss fail closed reagieren.

## 12. Duplikate und Parallelstrukturen

Das Directory Gate muss mindestens erkennen können:

- byte-identische Dateien in nicht erlaubten Source-Pfaden,
- nahezu identische Markdown-Dokumente mit konkurrierender Autorität,
- kopierte Contract Sources und Templates,
- mehrere aktive Dateien mit demselben Zweck,
- parallele Verzeichnisbäume gleicher Verantwortung,
- gleiche Namen mit konkurrierender Autorität,
- nicht deklarierte Ableitungen.

Zulässige technische Duplikate sind insbesondere Golden Fixtures, generierte Distributionen, qualifizierte Template-Ausgaben, vendorte Ressourcen, historische Momentaufnahmen und Duplicate-Testfixtures. Sie benötigen deklarierte Herkunft und dürfen nicht parallel manuell gepflegt werden.

Semantische Ähnlichkeit ist ein Reviewindikator. Sie darf nicht allein automatisch eine fachliche Identität behaupten oder Dateien löschen.

## 13. Strukturänderungen und Migrationen

### 13.1 Änderungsklassen

| Änderung | Mindestprozess |
|---|---|
| Datei in bestehendem zulässigem Pfad | normaler Engineering-Prozess und Directory Gate |
| Unterverzeichnis in Extension Point | Naming-, Ownership- und Contract-Prüfung |
| neue Inhaltsklasse | Governance- oder Standardreview und Contract-Änderung |
| neuer Root-Bereich | Governance- und Contract-Änderung, gegebenenfalls ADR |
| Verschiebung kanonischer Inhalte | Migrationsplan und Consumerprüfung |
| Änderung generierter Pfade | Tool-, Git-, Retention- und Exportprüfung |
| lokale Managed-Project-Abweichung | Managed-Project-Deviation |

### 13.2 Pflichtanalyse

Vor einer kanonischen Pfadverschiebung sind mindestens zu prüfen:

- Git-Tracking und Working Tree,
- Code- und Skriptreferenzen,
- Maven- und Buildkonfiguration,
- Exportprofile,
- Patch-Scopes und Manifeste,
- Tests und Fixtures,
- Project-New und Fresh-Project-Acceptance,
- Platform Update und Target-Deskriptoren,
- Dokumentationsindex und Links,
- Managed-Project-Adoption.

### 13.3 Migrationsplan

Ein Migrationsplan enthält Quell- und Zielpfad, Ownerwechsel, Consumer, Reihenfolge, Übergangsregel, Rückrollstrategie, Gates, Tests und den Abbau der Directory Transition Baseline.

Die Migration soll atomar erfolgen. Unvermeidbare Zwischenzustände müssen ausdrücklich unterstützt, eindeutig gerichtet und zeitlich begrenzt sein.

Dauerhafte parallele Alt- und Neupfade sind nicht zulässig. Temporäre Aliase benötigen kanonische Richtung, Owner, Ablaufdatum und Schutz gegen manuelle Doppelpflege.

## 14. Bestands- und Transition-Regeln

### 14.1 Directory Transition Baseline

Der aktuelle Bestand wird für die Gate-Einführung in einer maschinenlesbaren Directory Transition Baseline erfasst. Sie darf nur einzeln identifizierte Abweichungen enthalten und keine ganzen Root-Bereiche pauschal ausnehmen.

Neue Instanzen eines `forbidden-new`- oder `migration-candidate`-Musters müssen unabhängig vom Bestandsstatus erkannt werden. Die allgemeine Baseline-Semantik regelt die Quality Gate Governance.

### 14.2 Technische Dateien unter `PROJECT_DOCS/`

Der verifizierte Bestand enthält technische Dateien unter:

```text
PROJECT_DOCS/CONFIG/
PROJECT_DOCS/CORE/
PROJECT_DOCS/DEMO/
PROJECT_DOCS/TEMPLATES/
PROJECT_DOCS/TOOLING/
```

Diese Instanzen werden einzeln als kanonische technische Übergangsquelle, Golden Fixture, Directory Transition Baseline oder Migrationskandidat klassifiziert.

Neue technische Dateien unter `PROJECT_DOCS/` sind nur bei ausdrücklicher Contract-Freigabe zulässig. Die Directory Transition Baseline darf nicht erweitert werden, um neue Fehlplatzierungen aufzunehmen.

### 14.3 Gekoppelte Bestandspfade

Folgende Bereiche dürfen nicht beiläufig verschoben oder reorganisiert werden:

- `PROJECT_DOCS/TEMPLATES/project-skeleton/`,
- `PROJECT_DOCS/CONFIG/`,
- `PROJECT_DOCS/CONCEPT/`,
- `PROJECT_DOCS/PLANNING/`,
- `PROJECT_DOCS/OPERATIONAL/`,
- `docs/`,
- `contracts/governance/`,
- `bin/`,
- `platform/update/`,
- `src/test/resources/tooling/`.

Ihre Migration muss alle Aufrufer, Exportprofile, Patch-Scopes, Tests und gegebenenfalls Project-New oder Platform Update gemeinsam behandeln.

### 14.4 Bestehende Dokumentbereiche

Die vorhandenen `PROJECT_DOCS`-Unterbereiche bleiben während der Dokumentationsmigration zulässig und werden nach Inhalt, Autorität, Lifecycle und technischem Typ klassifiziert, nicht pauschal verschoben.

`docs/` bleibt bis zur Einzelentscheidung seiner Bestandsdokumente `legacy-accepted` und für neue dauerhafte Projektwahrheiten `forbidden-new`.

## 15. Project Directory Gate

### 15.1 Prüfumfang

Das Gate prüft mindestens:

- Root-Allowlist und Root-Dateien,
- registrierte Pfade, Unterverzeichnisse und Dateitypen,
- Pfad- und Lifecycle-Klassen,
- technische Spezifikationen unter Dokumentationspfaden,
- temporäre und generierte Dateien außerhalb registrierter Pfade,
- unregistrierte Verzeichnisse,
- Backup-, Copy-, Editor- und Case-Artefakte,
- Symlinks,
- Canonical Ownership,
- Byte-Duplikate und deklarierte Ableitungen,
- potenzielle semantische Parallelstrukturen,
- neue Verstöße gegen Directory Transition Baseline,
- ungültige oder abgelaufene Managed-Project-Deviations.

### 15.2 Modi

Das Gate unterstützt mindestens:

- `changed`: neue, geänderte, gelöschte und verschobene Pfade sowie direkt betroffene Ownership- und Duplicate-Beziehungen,
- `all`: vollständiger Repository- oder Projekt-Audit,
- `report`: deterministische Reportausgabe ohne Quelländerung.

Konkrete Kommandonamen stehen im Tooling-Vertrag.

Der Changed-Modus muss auch Änderungen am Contract, an der Baseline und an Deviations sowie Duplikatwirkungen gegenüber unveränderten Dateien berücksichtigen.

Der All-Modus ist mindestens erforderlich für Root- und Pfadmigrationen, Directory-Contract-Änderungen, Strict-Promotion, Release/Audit sowie Fresh- und Managed-Project-Qualifikation.

### 15.3 Effizienz und Sicherheit

Das Gate muss read-only, raw-byte-sicher und deterministisch arbeiten. Es trennt Tool Error von Findings, begrenzt teure Vollscans im Changed-Modus und verändert keine Quelldateien.

### 15.4 Fixtures

Mindestens erforderlich sind positive und negative Fixtures für:

- gültige Root- und Extension-Point-Nutzung,
- unerlaubten Root-Pfad und falschen Dateityp,
- technische Datei unter Dokumentation,
- temporäre Datei im Source-Bereich,
- Backup- und Case-Kollision,
- defekten oder externen Symlink,
- unzulässiges Duplikat und zulässige Ableitung,
- Bestandsfinding gegenüber neuem Finding,
- abgelaufene Deviation.

## 16. Project-New und gemanagte Projekte

### 16.1 Project-New

Project-New muss für `generated-project` eine gültige Root-, Dokumentations-, Contract-, Source-, Test- und Git-Hygiene-Struktur erzeugen. Springmaster-spezifische Parallelstrukturen dürfen nicht allein durch Vererbung entstehen.

Ein frisch erzeugtes Projekt muss das vorgesehene Directory Gate ohne manuelle Reparatur bestehen.

### 16.2 Managed Projects

Ein gemanagtes Projekt weist adoptierte Strukturversion, lokale Extension Points, Ergänzungen und Deviations maschinenlesbar aus.

Springmaster muss seine Struktur read-only prüfen können. Prüfung, Planung und Kompatibilitätsanalyse dürfen keine Dateien anlegen, verschieben oder korrigieren.

Strukturänderungen im Zielprojekt dürfen nur über einen expliziten Plan und autorisierten Apply-Prozess erfolgen.

## 17. Kanonische Ausgaben und Abnahmekriterien

### 17.1 Kanonische Ausgaben

Diese Governance erzeugt oder kontrolliert ausschließlich:

- Projektprofile,
- Root-Allowlist-Prinzipien,
- Bereichs-, Pfad- und Lifecycle-Klassen,
- Canonical Ownership und Extension Points,
- Strukturänderungs- und Migrationsprozess,
- Anforderungen an Directory Contract, Directory Transition Baseline und Directory Gate.

### 17.2 Abnahmekriterien

Die Governance ist inhaltlich vollständig, wenn:

1. jedes Projektprofil eigenständig modellierbar ist,
2. neue Root-Pfade standardmäßig verboten sind,
3. jeder Bereich Zweck, Owner, Inhalt, Lifecycle und Commitregel erhalten kann,
4. jede Inhaltsklasse genau einen kanonischen Owner besitzt,
5. Source, Generated, Runtime, Temporary und Historical unterscheidbar sind,
6. Extension Points Erweiterung ohne Parallelwahrheit erlauben,
7. Duplikate und zulässige Ableitungen unterscheidbar sind,
8. Naming-, Case-, Backup- und Symlink-Regeln technisch ableitbar sind,
9. Migrationen alle relevanten Consumer berücksichtigen,
10. der reale Bestand ohne Big-Bang-Umbau modelliert werden kann,
11. neue Fehlplatzierungen trotz Directory Transition Baseline erkannt werden,
12. Project-New ein gültiges reduziertes Profil erzeugt,
13. gemanagte Projekte read-only prüfbar sind,
14. changed-, all- und report-fähige Gates ableitbar sind,
15. keine Zuständigkeit der Documentation, Quality Gate oder Managed Project Governance dupliziert wird.

### 17.3 Technischer Umsetzungsstand

Die report-only Erstimplementierung umfasst:

- `contracts/governance/project-structure/project-directory-contract.json`,
- `contracts/governance/project-structure/directory-transition-baseline.json`,
- `bin/project-directory-gate.py` und den Shell-Einstieg,
- positive und negative Integrationsfixtures,
- `all`, `changed` und deterministische Reportausgabe,
- getrennte Transition- und neue Findings sowie Tool Errors.

Die Project-New-Materialisierung erzeugt zusätzlich ein reduziertes `generated-project`-Profil, eine leere Directory Transition Baseline und den lokalen Directory-Gate-Harness. Die Fresh-Project-Acceptance belegt, dass das erzeugte Projekt ohne manuelle Reparatur und ohne Transition Findings besteht.

Vor einer Aktivierung oder Strict-Promotion bleiben offen:

- der Managed-Project-Deviation-Contract und read-only Zielprojektpilot,
- getrennte Migrationspläne für gekoppelte Legacy-Pfade,
- Abbau der Directory Transition Baseline,
- Promotionentscheidung nach Quality Gate Governance.

## 18. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Volltext auf Basis des verifizierten Springmaster-Bestands |
| 2026-07-23 | draft | draft | Report-only Directory Contract, Transition Baseline, Gate und Fixtures technisch abgeleitet; Aktivierung bleibt offen |
| 2026-07-23 | draft | draft | Project-New-Materialisierung und Fresh-Project-Acceptance für das Profil `generated-project` ergänzt |

## Patch workflow runtime areas

`patches/logs/accept/**`, `patches/logs/validation/**`, `patches/runtime/**`, `patches/archives/**` and `patches/work/**` are generated runtime areas and must not be committed as normal source.

`patches/work/**` has the narrower role of a single-current-workflow operator handoff workspace. It is safely cleared before a new patch dry-run or accept, not by observers within the same workflow. It is excluded from exports and duplicate analysis. Symlinks, nested repositories, tracked files, mount points or special files make cleanup fail closed.

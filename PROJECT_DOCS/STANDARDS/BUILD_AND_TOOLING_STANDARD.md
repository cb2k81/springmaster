---
documentId: DOC-STD-0004
title: Build and Tooling Standard
documentType: standard
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/standards/build-tooling
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

# Build and Tooling Standard

## 1. Zweck und Geltungsbereich

Dieser Standard definiert die konkreten Qualitäts-, Sicherheits- und Schnittstellenregeln für den Maven-Build sowie für Bash-, Python- und repositoryweites Tooling in Springmaster.

Er gilt insbesondere für:

- `pom.xml` und Maven-Profile,
- ausführbare Einstiegspunkte unter `bin/`,
- gemeinsam genutzte Shell-Bibliotheken,
- Python-CLI-Werkzeuge und Validatoren,
- Tooling unter `platform/update/`,
- Project-New-Tooling und erzeugte Tooling-Baselines,
- Build-, Export-, Patch-, DBTool-, Gate- und Release-Werkzeuge,
- maschinenlesbare Reports, Logs und Exit-Semantik.

Für menschliche, automatisierte und KI-gestützte Entwicklung gelten dieselben Regeln. Ein Werkzeug ist Teil des Engineering-Harness und darf keine von Governance, ADRs, Standards oder Contracts unabhängige Regelquelle bilden.

## 2. Abgrenzung und kanonische Verantwortung

Dieser Standard ist die kanonische Quelle für die technische Gestaltung und Ausführung von Build- und Repository-Tooling.

| Gegenstand | Kanonische Quelle |
|---|---|
| Engineering-Profile und Änderungslifecycle | Engineering Governance |
| Gate-Modi, Findings, Tool Errors, Baselines und Waiver | Quality Gate Governance |
| Aufnahme von Maven-Plugins, Libraries und externen CLI-Werkzeugen | Dependency Governance |
| Teststufen und erforderliche Testevidence | Test Governance |
| konkrete Testcode-Regeln | Testing Standard |
| Pfade, generierte und temporäre Bereiche | Project Directory Governance |
| Patchtransaktion und dauerhafte Evidence-Grenze | ADR-0012 und Patch-Tooling-Verträge |
| Gate-Layer und Strict-Promotion | ADR-0006 und Quality Gate Governance |
| Releaseentscheidung und Artefaktversionierung | Release and Version Governance |
| fachliche Semantik einzelner Tools | jeweilige Tooling-Contracts, ADRs und Fachstandards |

Dieser Standard regelt nicht die fachliche Bedeutung einzelner Patch-, Export-, DB-, API- oder Platform-Update-Befehle. Er regelt deren gemeinsame technische Qualität, Sicherheit und Schnittstellenform.

## 3. Normative Begriffe und Regelmodell

Die Schlüsselwörter **MUSS**, **DARF NICHT**, **SOLL**, **SOLL NICHT** und **KANN** werden normativ verwendet.

Jede technisch relevante Regel besitzt eine stabile Rule ID mit dem Präfix `BTOOL`.

| Prüfbarkeitsklasse | Bedeutung |
|---|---|
| `automated` | deterministisch über Build, Source, CLI-Fixture oder Report prüfbar |
| `partially-automated` | Werkzeug prüft Struktur oder Indikatoren; semantische Bewertung bleibt erforderlich |
| `manual-review` | Verständlichkeit, Angemessenheit oder Migrationswirkung muss geprüft werden |
| `architectural-review` | Änderung berührt einen grundlegenden Build-, Distributions- oder Tooling-Vertrag |

Toolkonfigurationen und Maven-Plugin-Defaults sind keine eigenständigen Normquellen. Der Quality Rule Catalog ordnet Rule IDs ihrer technischen Prüfung zu.

## 4. Verifizierte Ausgangsbasis

Der aktuelle Springmaster-Bestand verwendet:

- Java 21 und Maven,
- Spring Boot Dependency Management,
- explizit versionierte Maven-Plugins,
- Surefire als aktuelle Java-Testausführung,
- CycloneDX im `verify`-Lifecycle,
- ein report-only Maven-Profil `springmaster-gates-report`,
- flache ausführbare Einstiegspunkte unter `bin/`,
- Shell-Bibliotheken unter `bin/lib/`,
- Bash mit `set -euo pipefail`,
- Python-CLI-Tools überwiegend mit `argparse`,
- kompakte Konsolenausgabe und detaillierte Reportdateien,
- positive, negative und Tool-Error-Integration-Fixtures für zentrale Toolfamilien.

Diese Baseline ist kein Freibrief für neue Abweichungen. Bestehende Sonderformen werden bei Änderungen geprüft und kontrolliert migriert; es erfolgt keine pauschale Tooling-Reorganisation.

## 5. Maven-Buildvertrag

### 5.1 Grundregeln

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-MVN-001` | Der Standard-Build MUSS aus einem sauberen Checkout mit dokumentierter JDK- und Maven-Voraussetzung reproduzierbar aufrufbar sein. | `automated` |
| `BTOOL-MVN-002` | Java-Release, Source-Encoding und Reporting-Encoding MÜSSEN zentral im Maven-Build definiert sein. | `automated` |
| `BTOOL-MVN-003` | Build-Plugins MÜSSEN über eine genehmigte Version oder eine genehmigte Versionsquelle verfügen. Implizit wechselnde Pluginversionen sind nicht zulässig. | `automated` |
| `BTOOL-MVN-004` | Dependencies und Plugins unterliegen der Dependency Governance. Eine POM-Änderung allein gilt nicht als vollständige Einführung. | `partially-automated` |
| `BTOOL-MVN-005` | Der Default-Lifecycle DARF keine geheimen Zugangsdaten, produktiven Dienste oder destruktiven externen Operationen benötigen. | `partially-automated` |
| `BTOOL-MVN-006` | `mvn clean verify` MUSS der kanonische vollständige Maven-Qualifikationslauf für POM-, Build-, Dependency- und Release-Artefaktänderungen sein, solange kein spezifischerer aktiver Vertrag gilt. | `automated` |
| `BTOOL-MVN-007` | Maven-Ausgaben und erzeugte Artefakte MÜSSEN in registrierten Build- oder Reportpfaden liegen. | `automated` |
| `BTOOL-MVN-008` | Der Build DARF keine Source-, Governance- oder Contract-Dateien stillschweigend normalisieren oder verändern. | `automated` |
| `BTOOL-MVN-009` | Ein Build-Erfolg darf nicht behauptet werden, wenn ein gebundenes Plugin oder ein verpflichtender Prüfschritt nicht ausgeführt werden konnte. | `automated` |
| `BTOOL-MVN-010` | Maven-Aufrufe in Automation SOLLEN nicht-interaktiv und mit begrenzter, reproduzierbarer Ausgabe erfolgen. | `partially-automated` |

### 5.2 Profile

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-MVN-011` | Maven-Profile MÜSSEN einen klaren Zweck besitzen und dürfen keine voneinander abweichende Produktsemantik verstecken. | `manual-review` |
| `BTOOL-MVN-012` | Ein Profilname MUSS stabil, dokumentiert und seiner Enforcement-Wirkung eindeutig zugeordnet sein. | `automated` |
| `BTOOL-MVN-013` | Report-only- und Strict-Profile DÜRFEN nicht dieselbe technische Konfiguration mit nur informell unterschiedlicher Interpretation verwenden. | `partially-automated` |
| `BTOOL-MVN-014` | Das Aktivieren eines Profils DARF keine unautorisierte Zielprojektmutation oder produktive Deployment-Operation auslösen. | `automated` |
| `BTOOL-MVN-015` | Test-Suite-Trennung, Coverage und zusätzliche Qualitätsplugins werden erst nach akzeptiertem Contract und Dependency Review in Profile gebunden. | `partially-automated` |

### 5.3 Artefakte und SBOM

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-MVN-016` | Veröffentlichte Buildartefakte MÜSSEN eindeutig zur Source-Baseline und Version zuordenbar sein. | `automated` |
| `BTOOL-MVN-017` | SBOM-Erzeugung MUSS für den Release- oder Auditprozess reproduzierbar sein; eine SBOM ersetzt keine Dependency-Genehmigung. | `automated` |
| `BTOOL-MVN-018` | Distributionsarchive DÜRFEN nur registrierte Inhalte aufnehmen. Runtime-, lokale Environment- oder unqualifizierte Evidence-Dateien sind ausgeschlossen. | `automated` |
| `BTOOL-MVN-019` | Ein Distributionsskript MUSS das erwartete Primärartefakt eindeutig ermitteln und bei Mehrdeutigkeit oder Fehlen fail-closed abbrechen. | `automated` |

## 6. Bash-Standard

### 6.1 Skriptstruktur

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-BASH-001` | Ausführbare Bash-Skripte beginnen mit `#!/usr/bin/env bash` und `set -euo pipefail`. | `automated` |
| `BTOOL-BASH-002` | Ein Skript MUSS sein Verzeichnis und den Projektroot robust aus `BASH_SOURCE[0]` ableiten. Das aktuelle Working Directory ist keine zuverlässige Root-Quelle. | `automated` |
| `BTOOL-BASH-003` | Gemeinsame Environment-, Logging- und Fehlerfunktionen MÜSSEN über bestehende Bibliotheken wie `bin/init.env.sh` beziehungsweise `bin/lib/**` wiederverwendet werden, sofern deren Vertrag passt. | `partially-automated` |
| `BTOOL-BASH-004` | Variablenexpansionen, Pfade und Argumente MÜSSEN grundsätzlich gequotet werden. Beabsichtigtes Word-Splitting oder Globbing muss lokal erkennbar sein. | `automated` |
| `BTOOL-BASH-005` | Temporäres Deaktivieren von `errexit` MUSS lokal begrenzt sein und den tatsächlichen Exit-Code, insbesondere bei Pipelines, korrekt sichern. | `partially-automated` |
| `BTOOL-BASH-006` | Shell-Funktionen verwenden `local` für lokale Variablen, soweit keine bewusste Export- oder Rückgabesemantik besteht. | `automated` |
| `BTOOL-BASH-007` | Komplexe Datenverarbeitung, JSON-Manipulation oder Transaktionslogik SOLL in Python oder einer bestehenden spezialisierten Implementierung liegen statt in fragilen Shell-Pipelines. | `manual-review` |
| `BTOOL-BASH-008` | Neue Wrapper SOLLEN bestehende kanonische Einstiegspunkte delegieren und dürfen keine konkurrierende Implementierung derselben Toolsemantik schaffen. | `manual-review` |

### 6.2 Portabilität und Abhängigkeiten

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-BASH-009` | Ein Skript MUSS benötigte externe Befehle vor der Mutation über einen zentralen oder gleichwertigen Preflight prüfen. | `automated` |
| `BTOOL-BASH-010` | Nicht allgemein verfügbare GNU-, Linux- oder distributionsspezifische Optionen benötigen einen dokumentierten Plattformvertrag oder eine portable Alternative. | `partially-automated` |
| `BTOOL-BASH-011` | Externe Shell-Werkzeuge unterliegen der Dependency Governance; ihre bloße Verfügbarkeit auf einem Entwicklerrechner ist keine zulässige Voraussetzung. | `partially-automated` |
| `BTOOL-BASH-012` | Neue Skripte MÜSSEN mit `bash -n` prüfbar sein. | `automated` |

### 6.3 Traps und Cleanup

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-BASH-013` | Ein Skript, das temporäre Ressourcen, Locks oder Worktrees erzeugt, MUSS deren Cleanup für Erfolg, Fehler und Signalabbruch definieren. | `partially-automated` |
| `BTOOL-BASH-014` | Cleanup DARF bereits finalisierte oder fremde Ressourcen nicht entfernen. Eigentum und Scope müssen eindeutig sein. | `manual-review` |
| `BTOOL-BASH-015` | Cleanup-Fehler DÜRFEN den ursprünglichen Tool Error nicht verdecken; sie werden separat berichtet. | `partially-automated` |

## 7. Python-Standard

### 7.1 CLI- und Modulstruktur

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-PY-001` | Neue Python-CLI-Werkzeuge verwenden `argparse` oder eine genehmigte gemeinsame CLI-Abstraktion. | `automated` |
| `BTOOL-PY-002` | CLI-Parsing, fachliche Verarbeitung und Dateisystemmutation SOLLEN soweit sinnvoll getrennte Funktionen oder Module bilden. | `manual-review` |
| `BTOOL-PY-003` | Der Programmeinstieg MUSS über eine erkennbare `main`-Funktion oder einen gleichwertigen kontrollierten Einstieg erfolgen. | `automated` |
| `BTOOL-PY-004` | Python-Quelldateien verwenden UTF-8 und müssen mit `python3 -m py_compile` prüfbar sein. | `automated` |
| `BTOOL-PY-005` | Die Python-Standardbibliothek ist zu bevorzugen. Neue Third-Party-Pakete benötigen Dependency Review und reproduzierbare Installation. | `partially-automated` |
| `BTOOL-PY-006` | Catch-all-Exception-Handler dürfen nur an einer Prozessgrenze verwendet werden und müssen Ursache, Exit-Semantik und Diagnose erhalten. | `partially-automated` |
| `BTOOL-PY-007` | Library-Funktionen DÜRFEN nicht unkontrolliert `sys.exit` aufrufen; Exit-Entscheidungen gehören an die CLI-Grenze. | `partially-automated` |

### 7.2 Daten und Determinismus

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-PY-008` | JSON wird explizit als UTF-8 gelesen und geschrieben. Maschinenlesbare Ausgabe MUSS deterministische Schlüsselreihenfolge und definierte Zeilenendensemantik verwenden, wenn sie gehasht oder als Fixture geprüft wird. | `automated` |
| `BTOOL-PY-009` | Pfade werden mit `pathlib.Path` oder einer gleichwertig sicheren Abstraktion behandelt; ungeprüfte Stringkonkatenation für sicherheitsrelevante Pfade ist nicht zulässig. | `partially-automated` |
| `BTOOL-PY-010` | Zeitstempel, UUIDs und Zufall dürfen Golden Fixtures oder fachliche Resultate nicht instabil machen. Volatile Felder sind kontrolliert zu erzeugen oder für Regressionen zu normalisieren. | `partially-automated` |
| `BTOOL-PY-011` | Hashes für Source-Baselines MÜSSEN aus den rohen Bytes stammen, nicht aus gerenderten, normalisierten oder erneut serialisierten Darstellungen. | `automated` |
| `BTOOL-PY-012` | Ein Parser MUSS ungültige, unvollständige oder unerwartete Eingaben fail-closed behandeln und darf keine stillen Defaultwerte erfinden, die Sicherheit oder Scope erweitern. | `automated` |

## 8. CLI-Verträge

### 8.1 Argumente und Hilfe

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-CLI-001` | Jeder öffentliche Tool-Einstieg MUSS eine stabile Usage- oder Help-Ausgabe besitzen. | `automated` |
| `BTOOL-CLI-002` | Unbekannte Argumente, fehlende Pflichtwerte und ungültige Kombinationen MÜSSEN mit einer eindeutigen Diagnose und einem Nicht-Erfolgs-Exit enden. | `automated` |
| `BTOOL-CLI-003` | Mutierende und read-only Befehle MÜSSEN in Benennung, Help und Verhalten unterscheidbar sein. | `automated` |
| `BTOOL-CLI-004` | Standardwerte dürfen den Scope oder die Mutationswirkung nicht still erweitern. | `automated` |
| `BTOOL-CLI-005` | Absolute lokale Pfade SOLLEN nicht in dauerhafte oder portable Evidence übernommen werden; Artefaktname, relative Projektpfade, IDs und Hashes sind zu bevorzugen. | `partially-automated` |

### 8.2 stdout, stderr und Ausgabeformate

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-CLI-006` | Normale menschenlesbare Statusausgabe geht auf stdout; Fehlerdiagnosen gehen auf stderr. | `automated` |
| `BTOOL-CLI-007` | Maschinenlesbare Modi MÜSSEN ein dokumentiertes, parsebares Format liefern und dürfen nicht mit zusätzlichen freien Konsolenmeldungen vermischt werden. | `automated` |
| `BTOOL-CLI-008` | Unterstützt ein Tool `human`, `env` oder `json`, müssen dieselben fachlichen Felder und Statuswerte konsistent abgebildet werden. | `automated` |
| `BTOOL-CLI-009` | Die Standardkonsole SOLL kompakt bleiben; vollständige Diagnostik gehört in registrierte Report- oder Logdateien. | `partially-automated` |
| `BTOOL-CLI-010` | Secrets, Tokens, Passwörter und vollständige sensible Connection Strings DÜRFEN weder stdout, stderr noch Reports erreichen. | `automated` |

### 8.3 Exit-Semantik

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-CLI-011` | Exit `0` bedeutet, dass das Werkzeug technisch erfolgreich ausgeführt wurde und die Enforcement-Semantik keinen Blocker erzeugt hat. | `automated` |
| `BTOOL-CLI-012` | Tool Errors, ungültige Nutzung und blockierende Findings MÜSSEN technisch unterscheidbar sein. Konkrete Exit-Code-Bereiche werden im Tool-CLI-Contract festgelegt. | `automated` |
| `BTOOL-CLI-013` | Report-only Findings allein DÜRFEN keinen Tool-Error-Exit erzeugen. | `automated` |
| `BTOOL-CLI-014` | Ein Tool darf einen Kindprozess-Exit nur dann unverändert weiterreichen, wenn dessen Semantik Teil des öffentlichen Toolvertrags ist; andernfalls muss es ihn eindeutig übersetzen. | `partially-automated` |
| `BTOOL-CLI-015` | Ein abgebrochener, unvollständiger oder nicht verlässlich ausgewerteter Lauf DARF nicht als Erfolg enden. | `automated` |

## 9. Environment und Konfiguration

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-CFG-001` | Projektlokale Environment-Werte werden über den registrierten Environment-Contract und gemeinsame Loader eingelesen. | `automated` |
| `BTOOL-CFG-002` | `.env` ist lokal und darf nicht versioniert oder in Zielprojekte kopiert werden. Eine `.env.example` enthält keine Secrets. | `automated` |
| `BTOOL-CFG-003` | Konfigurationspriorität und Herkunft MÜSSEN eindeutig sein. Ein Tool darf denselben Wert nicht aus mehreren Quellen mit stiller, undokumentierter Priorität beziehen. | `partially-automated` |
| `BTOOL-CFG-004` | Fehlende sicherheits- oder mutationsrelevante Konfiguration führt fail-closed zum Abbruch. Unsichere Fallbacks sind nicht zulässig. | `automated` |
| `BTOOL-CFG-005` | Environment-Werte werden vor Nutzung validiert und normalisiert. Pfade, Namen, Booleans, Ports und Enums benötigen definierte Formate. | `automated` |
| `BTOOL-CFG-006` | Springmaster-lokale Defaults DÜRFEN nicht ungeprüft in Project-New oder gemanagte Projekte propagiert werden. | `partially-automated` |
| `BTOOL-CFG-007` | Private Tool- oder Transaktionsvariablen DÜRFEN nicht unbeabsichtigt an öffentliche Kindprozesse, Tests oder Exporte vererbt werden. | `automated` |

## 10. Dateisystem, temporäre Daten und Atomicity

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-FS-001` | Tools dürfen nur Pfade lesen oder verändern, die durch ihren Vertrag und die Project Directory Governance erlaubt sind. | `automated` |
| `BTOOL-FS-002` | Eingabepfade MÜSSEN normalisiert und gegen Traversal, unerlaubte Symlinks und Scope-Escape geprüft werden. | `automated` |
| `BTOOL-FS-003` | Temporäre Daten liegen ausschließlich in registrierten Runtime-, Build- oder Temp-Pfaden und werden nach Erfolg oder Fehler kontrolliert bereinigt. | `automated` |
| `BTOOL-FS-004` | Dauerhafte Dateien SOLLEN atomar über temporäre Datei, Flush und Rename publiziert werden, wenn ein Teilzustand schädlich wäre. | `partially-automated` |
| `BTOOL-FS-005` | Ein Werkzeug DARF keine bestehende Datei überschreiben, bevor Vorzustand, Eigentum und erwartete Baseline geprüft wurden. | `automated` |
| `BTOOL-FS-006` | Löschen, Ersetzen und Verschieben benötigen explizite Scope- und Existenzsemantik; fehlende oder zusätzliche Dateien dürfen nicht still toleriert werden, wenn sie den Vertrag verändern. | `automated` |
| `BTOOL-FS-007` | Datei- und Verzeichnismodi müssen so restriktiv sein wie der Zweck erlaubt. Ausführbarkeit wird nur für tatsächliche Einstiegspunkte gesetzt. | `automated` |
| `BTOOL-FS-008` | Generated-, Runtime- und Acceptance-Artefakte DÜRFEN nicht unbeabsichtigt committed werden. | `automated` |

## 11. Mutierende Tools und Sicherheit

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-MUT-001` | Mutierende Tools MÜSSEN vor der ersten Mutation einen vollständigen Fail-Closed-Preflight durchführen. | `automated` |
| `BTOOL-MUT-002` | Der Preflight MUSS Identität, Scope, Baseline, Pfade, Berechtigungen, Konflikte und erforderliche Tools prüfen, soweit sie für die Operation relevant sind. | `partially-automated` |
| `BTOOL-MUT-003` | Eine Dry-run-, Plan- oder Preflight-Operation DARF das Ziel nicht verändern. | `automated` |
| `BTOOL-MUT-004` | Destruktive Operationen benötigen eine ausdrücklich benannte Aktion und eine zusätzliche Freigabebedingung; generische Standardbefehle dürfen nicht destruktiv sein. | `automated` |
| `BTOOL-MUT-005` | Mehrschrittige Mutationen MÜSSEN transaktional, atomar oder mit geprüftem Rollback beziehungsweise Kompensationsplan ausgeführt werden. | `partially-automated` |
| `BTOOL-MUT-006` | Ein fehlgeschlagener Lauf DARF keinen unklaren Zwischenzustand als erfolgreich oder angewendet markieren. | `automated` |
| `BTOOL-MUT-007` | Fremde oder bereits vorhandene Änderungen DÜRFEN nicht übernommen, zurückgesetzt, überschrieben oder committed werden. | `automated` |
| `BTOOL-MUT-008` | Git-Push, produktives Deployment und Zielprojektmutation benötigen jeweils eine separate ausdrückliche Freigabe. | `automated` |
| `BTOOL-MUT-009` | Zielprojekte sind für Analyse-, Plan-, Generate- und Compatibility-Befehle read-only. Mutation erfolgt nur über den dafür autorisierten Befehl. | `automated` |
| `BTOOL-MUT-010` | Least Privilege gilt für Patchscope, Dateisystemrechte, Datenbankrechte und Zielprojektzugriff. | `partially-automated` |

## 12. Determinismus und Reproduzierbarkeit

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-DET-001` | Gleiche Baseline, Eingaben, Contract- und Toolversionen MÜSSEN zum gleichen fachlichen Resultat führen. | `automated` |
| `BTOOL-DET-002` | Verzeichnisiteration, JSON-Ausgabe, Manifest- und Reportlisten MÜSSEN deterministisch sortiert sein. | `automated` |
| `BTOOL-DET-003` | Locale, Zeitzone, Uhr und zufällige IDs dürfen fachliche Vergleiche nicht implizit verändern. | `partially-automated` |
| `BTOOL-DET-004` | Volatile Run-Daten werden von dauerhaft vergleichbaren Ergebnisdaten getrennt. | `automated` |
| `BTOOL-DET-005` | Ein Tool MUSS seine relevante Input-Baseline, Contractversion und Toolversion im Report identifizierbar machen. | `automated` |
| `BTOOL-DET-006` | Netzwerkabhängige Prüfungen müssen Cache-, Offline- und Fehlersemantik dokumentieren; ein nicht erreichbarer externer Dienst darf nicht als fachliches Pass interpretiert werden. | `partially-automated` |
| `BTOOL-DET-007` | Automation DARF nicht durch Auswahl der „neuesten“ Datei anhand unsicherer Verzeichnissortierung gesteuert werden. Kanonische Pointer, IDs oder Toolbefehle sind zu verwenden. | `automated` |

## 13. Reports, Logs und Evidence

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-RPT-001` | Maschinenlesbare Reports MÜSSEN ein versioniertes Schema oder einen stabilen Report-Marker besitzen. | `automated` |
| `BTOOL-RPT-002` | Ein Report trennt Laufstatus, Tool Errors, Findings, Warnungen und Evidence-Referenzen. | `automated` |
| `BTOOL-RPT-003` | Reports MÜSSEN atomar publiziert werden, wenn Konsumenten sie während oder nach dem Lauf lesen können. | `automated` |
| `BTOOL-RPT-004` | Reportpfade müssen projektlokal, registriert und aus Run- oder Gate-Identität ableitbar sein. | `automated` |
| `BTOOL-RPT-005` | Rohlogs dürfen umfangreich sein; Summary und Standardkonsole MÜSSEN begrenzt und handlungsorientiert bleiben. | `partially-automated` |
| `BTOOL-RPT-006` | Reports dürfen keine absoluten externen Ingresspfade oder Secrets als dauerhafte Vertragsdaten speichern. | `automated` |
| `BTOOL-RPT-007` | Acceptance-, Verify-, Validation-, Audit- und Release-Evidence bleiben semantisch getrennt. Ein späterer Fehlversuch darf erfolgreiche Acceptance nicht überschreiben. | `automated` |
| `BTOOL-RPT-008` | Generierte Evidence ersetzt keine Git-Historie und keine normative Regelquelle. | `manual-review` |
| `BTOOL-RPT-009` | Source-Hash-Evidence verwendet Raw-Byte-Hashes und weist Hashalgorithmus sowie Baseline aus. | `automated` |

## 14. Tooling-Tests und Selfchecks

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-TST-001` | Jede geänderte Shell-Datei MUSS mindestens `bash -n` bestehen; jede geänderte Python-Datei mindestens `python3 -m py_compile`. | `automated` |
| `BTOOL-TST-002` | Öffentliche CLI-Verträge benötigen positive, negative und ungültige-Nutzungs-Fixtures. | `automated` |
| `BTOOL-TST-003` | Mutierende Tools benötigen zusätzlich Fixtures für Baseline-Mismatch, Pfad-Escape, Berechtigungsfehler, Teilfehler, Rollback oder Kompensation und Wiederholung. | `automated` |
| `BTOOL-TST-004` | Report-only Tools benötigen getrennte Fixtures für Findings und Tool Errors. | `automated` |
| `BTOOL-TST-005` | Golden Reports dürfen nur bei beabsichtigter Vertragsänderung aktualisiert und durch einen Regressionstest abgesichert werden. | `automated` |
| `BTOOL-TST-006` | Ein repositoryweiter Tooling-Selfcheck MUSS Syntax, zentrale Contracts, zentrale Integration-Fixtures und optionale Capability-Erkennung abdecken. | `automated` |
| `BTOOL-TST-007` | Optionales Tooling darf nur dann übersprungen werden, wenn die Capability für das Projektprofil tatsächlich nicht installiert ist. Ein vorhandener, aber fehlerhafter Einstieg ist ein Fehler. | `automated` |
| `BTOOL-TST-008` | Änderungen an Patch-, Export-, Project-New-, Gate- oder Platform-Update-Tooling benötigen die fachlich passende Integration- oder Regression-Suite. | `automated` |
| `BTOOL-TST-009` | Selfchecks dürfen keine produktiven oder nicht autorisierten externen Ziele verändern. | `automated` |
| `BTOOL-TST-010` | Laufzeitintensive Suites müssen in Engineering-Profilen eindeutig eingeordnet sein; ein Timeout darf nicht als erfolgreicher Skip gelten. | `partially-automated` |

## 15. Kompatibilität und Änderung von Toolverträgen

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-COMP-001` | Öffentliche CLI-Befehle, Argumente, Exit-Semantik und Reportfelder gelten als Verträge und dürfen nicht still inkompatibel geändert werden. | `partially-automated` |
| `BTOOL-COMP-002` | Inkompatible Änderungen benötigen Migrationshinweis, Versionsbewertung und Anpassung aller internen Konsumenten. | `partially-automated` |
| `BTOOL-COMP-003` | Deprecated Optionen oder Felder benötigen eine dokumentierte Übergangsfrist und dürfen keine abweichende Semantik neben dem Nachfolger entwickeln. | `partially-automated` |
| `BTOOL-COMP-004` | Wrapper, Project-New und Platform Update müssen die Version des übernommenen Tooling-Vertrags identifizierbar machen. | `automated` |
| `BTOOL-COMP-005` | Ein Tool darf Legacy-Artefakte nur lesen, wenn das Format eindeutig erkannt und die Ausgabe nicht als aktueller Schreibvertrag verwendet wird. | `automated` |
| `BTOOL-COMP-006` | Neue Artefakte werden ausschließlich im aktuellen akzeptierten Format geschrieben. | `automated` |

## 16. Project-New und gemanagte Projekte

| Rule ID | Regel | Prüfbarkeit |
|---|---|---|
| `BTOOL-PROJ-001` | Project-New MUSS nur die für das Zielprofil erforderlichen Tooling-Einstiegspunkte, Libraries, Contracts und Konfigurationen erzeugen. | `automated` |
| `BTOOL-PROJ-002` | Ein frisch erzeugtes Projekt MUSS seine Tooling-Syntax, Kerncontracts und vorgesehenen Builds ohne manuelle Reparatur bestehen. | `automated` |
| `BTOOL-PROJ-003` | Projektlokale Tokens, Pfade und Defaults müssen beim Generieren vollständig aufgelöst oder bewusst als dokumentierte Platzhalter erhalten bleiben. | `automated` |
| `BTOOL-PROJ-004` | Springmaster-spezifische absolute Pfade, Secrets, `.env`-Werte, Runtime-Artefakte und lokale Defaults dürfen nicht in Zielprojekte kopiert werden. | `automated` |
| `BTOOL-PROJ-005` | Gemanagte Projekte adoptieren eine identifizierbare Tooling-, Contract- und Standardversion. | `automated` |
| `BTOOL-PROJ-006` | Lokale Tooling-Erweiterungen benötigen einen registrierten Extension Point; Abweichungen von adoptierten Regeln benötigen eine Deviation. | `partially-automated` |
| `BTOOL-PROJ-007` | Read-only-Kompatibilitätsprüfungen müssen CLI-, Contract-, Dependency-, Pfad- und Reportdrift erkennen können, ohne das Ziel zu mutieren. | `automated` |
| `BTOOL-PROJ-008` | Platform Update darf Tooling nur über planbare, baseline-geprüfte und transaktionale Updates liefern. | `automated` |

## 17. Technische Ableitungen

Aus diesem Standard werden mindestens abgeleitet:

- Build and Tooling Rule Catalog Entries,
- Maven Build Contract,
- Tool CLI Contract,
- Tool Report Contract,
- Tool Environment Contract,
- Tooling-Selfcheck-Contract,
- positive, negative und Tool-Error-Fixtures,
- Project-New-Tooling-Acceptance,
- Managed-Project-Tooling-Compatibility-Report.

Vorgesehene Contract-Familie:

```text
contracts/governance/build-tooling-contract.json
contracts/governance/tool-cli-contract.json
contracts/governance/tool-report-contract.json
```

Die endgültige Dateiaufteilung richtet sich nach unabhängigem Lifecycle und Project Directory Governance. Bestehende Tooling-Contracts werden referenziert oder kontrolliert migriert, nicht unbesehen dupliziert.

## 18. Offene Entscheidungen

| Decision ID | Entscheidung | Blockiert |
|---|---|---|
| `GOV-DEC-007` | kleinste geeignete Kombination aus Checkstyle, PMD, SpotBugs und weiteren Java-Prüfmitteln | Java-Quality-Toolintegration |
| `GOV-DEC-013` | konkrete standardisierte Exit-Code-Bereiche für öffentliche CLIs | Tool CLI Contract |
| `GOV-DEC-015` | technische Trennung von Unit-, Integration- und Acceptance-Suites | Maven-Testprofile und Suite Contract |
| `GOV-DEC-017` | kleinster reproduzierbarer Dependency-, License- und Vulnerability-Toolstack | Dependency- und Release-Gates |

Die Grundregeln für Maven, Bash, Python, CLI-Semantik, Mutation, Reports und Selfchecks sind mit diesem Standard entschieden.

## 19. Übergang und Bestandsmigration

1. Bestehende Tools bleiben an ihren aktuellen kanonischen Pfaden; dieser Standard verlangt keine pauschale Verschiebung in neue Unterverzeichnisse.
2. Bestehende CLI- und Reportverträge werden inventarisiert und den Rule IDs sowie Contracts zugeordnet.
3. Neue Prüfregeln starten entsprechend Quality Gate Governance report-only, sofern sie nicht bereits stabil und strict-ready sind.
4. Abweichungen werden nicht durch pauschale Suppressions verdeckt. Bestandsfindings werden behoben, qualifiziert baselined oder als Debt registriert.
5. Project-New wird erst nach stabilen Contracts und Acceptance-Fixtures angepasst.
6. Gemanagte Projekte werden zunächst read-only verglichen; Tooling-Mutation erfolgt erst über den autorisierten Updateprozess.

## 20. Abnahmekriterien

Dieser Standard ist inhaltlich vollständig, wenn:

1. Maven-Build, Profile und Artefakte eindeutig geregelt sind,
2. Bash- und Python-Regeln die bestehende Toolstruktur ohne unnötige Reorganisation abbilden,
3. CLI-, stdout/stderr- und Exit-Semantik technisch ableitbar sind,
4. Findings und Tool Errors getrennt bleiben,
5. mutierende Tools fail-closed, scope-begrenzt und transaktional arbeiten,
6. Environment, Secrets, Pfade und temporäre Daten sicher geregelt sind,
7. Reports deterministisch, versioniert und atomar publizierbar sind,
8. positive, negative, Tool-Error- und Rollback-Fixtures ableitbar sind,
9. Compatibility und Deprecation kontrolliert sind,
10. Project-New ohne Springmaster-lokale Artefakte qualifiziert werden kann,
11. Managed Projects read-only auf Tooling-Drift geprüft werden können,
12. offene Toolprodukt- und Grenzwertentscheidungen nicht still vorweggenommen werden.

## 21. Kanonische Ausgaben

Dieser Standard erzeugt oder kontrolliert ausschließlich:

- Maven-Build-, Profil- und Artefaktregeln,
- Bash- und Python-Toolgestaltung,
- öffentliche CLI-, Exit- und Ausgabeformate,
- Environment-, Pfad-, Temp- und Mutationssicherheit,
- Determinismus, Reports, Logs und Tool-Evidence,
- Tooling-Tests, Selfchecks und Compatibility,
- technische Project-New- und Managed-Project-Tooling-Regeln.

Nicht zu seinen kanonischen Ausgaben gehören fachliche Toolsemantik, Gate-Enforcement, konkrete Dependency-Genehmigungen, konkrete Teststufen, Repository-Pfadklassen oder Releaseentscheidungen.

## 22. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-23 | – | draft | Erstentwurf aus AGENTS.md, Maven-Baseline, bestehenden Tooling-Verträgen, ADR-0006, ADR-0012 und verifiziertem Bash-/Python-Bestand |

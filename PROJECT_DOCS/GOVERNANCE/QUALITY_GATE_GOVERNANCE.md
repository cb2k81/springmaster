---
documentId: DOC-GOV-0004
title: Quality Gate Governance
documentType: governance
status: draft
authority: normative
scope: repository
scopeLevel: ecosystem
scopePaths:
  - springmaster/quality-gates
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

# Quality Gate Governance

## 1. Zweck und Geltungsbereich

Diese Governance regelt, wie normative technische Regeln registriert, geprüft, ausgewertet, schrittweise verschärft und kontrolliert ausgenommen werden.

Sie bestimmt:

- Quality Rules, Rule IDs und Prüfbarkeitsklassen,
- Gate-Layer, Enforcement- und Scope-Modi,
- Findings, Severity, Tool Errors und Gate-Ergebnisse,
- `report-only`, `manual-review` und `strict`,
- Rule Lifecycle und Strict Promotion,
- Findings-Baselines, Waiver und Suppressions,
- Gate-Reports, Fixtures und Harness-Selbstprüfung,
- Einführung neuer Prüfwerkzeuge sowie Propagation.

Sie gilt für technische und systematische Prüfungen von Code, Architektur, Tests, Contracts, Dokumentation, Verzeichnisstruktur, Dependencies, Tooling, Templates und Lieferartefakten.

Ihre Aktivierung promotet keine bestehende Regel automatisch zu `strict`.

## 2. Kanonische Verantwortung und Abgrenzung

Diese Governance ist die kanonische Quelle für das allgemeine Regel-, Gate-, Finding-, Promotion-, Baseline- und Waiver-Modell.

| Nicht hier geregelt | Kanonische Quelle |
|---|---|
| erforderliches Engineering-Profil eines Changes | Engineering Governance |
| konkrete Coding-, Architektur-, Test- oder Buildregel | zuständiger Standard oder ADR |
| konkrete Severity einer Fachregel | zuständige normative Quelle; Abbildung im Rule Catalog |
| Teststufen, Coverage und Testabschluss | Test Governance und Testing Standard |
| Genehmigung externer Abhängigkeiten | Dependency Governance |
| Dokumentations- und Directory-Fachregeln | Documentation beziehungsweise Project Directory Governance |
| Managed-Project-Deviations | Managed Project Governance |
| numerische Exit-Codes | Build and Tooling Standard und Exit-Code-Contract |
| Kommandos und Bedienabläufe | Development Guide und Tooling |

Ein Tool DARF keine Governance-Verstöße für unregistrierte Regeln erzeugen. Diagnosen ohne normative Quelle müssen ausdrücklich als technische Diagnose, nicht als Regelverstoß, erscheinen.

## 3. Bestehende Entscheidungsbasis

ADR-0006 „Verification and Gate Strategy“ bleibt die akzeptierte Architekturentscheidung für:

- Gate-Layer G0 bis G6,
- `report-only`, `strict` und `manual-review`,
- `BLOCKER`, `ERROR`, `WARNING`, `INFO` und `MANUAL_REVIEW`,
- die Trennung von Findings und Tool-Ausführungsfehlern,
- schrittweise Strict Promotion,
- read-only Target Comparison.

Diese Governance operationalisiert die Entscheidung. Eine grundlegende Änderung der Layer- oder Enforcement-Strategie benötigt eine ADR-Änderung oder Ablösung.

Der vorhandene Report-only-Gate-Seed und `springmaster-gates-report` bleiben ein gültiger Übergangsbestand.

## 4. Grundsätze

### 4.1 Normative Quelle vor Prüfung

Die technische Kette lautet:

```text
normative Regel
-> stabile Rule ID
-> Rule-Catalog-Eintrag
-> Implementierung
-> Fixtures und Selfcheck
-> report-only Qualifikation
-> ausdrückliche Strict Promotion
```

Normative Quelle, Catalog, Tool und Report besitzen unterschiedliche Aufgaben und dürfen einander nicht ersetzen.

### 4.2 Automatisierung nach Prüfbarkeit

Deterministisch entscheidbare Struktur-, Syntax-, Dependency-, Package- und Pfadregeln SOLLEN algorithmisch geprüft werden.

Semantische Dokumentations-, Test- und Architekturfragen KÖNNEN durch manuelle oder KI-gestützte Reviews ergänzt werden. Sie müssen als teilweise automatisiert oder manuell ausgewiesen werden.

### 4.3 Leichtgewichtige Toolauswahl

Für eine Regel wird die kleinste hinreichende, lokal reproduzierbare und wartbare Lösung gewählt. Neue Tools benötigen einen konkreten Regelbedarf sowie Bewertung von Überschneidung, Laufzeit, Dependencies, Fehlalarmen und Propagation.

Zentrale Dienste wie SonarQube können Trends ergänzen. Blockierende Kernregeln SOLLEN im Repository lokal reproduzierbar bleiben.

### 4.4 Findings und Tool Errors

Ein Finding setzt eine korrekt ausgeführte Prüfung voraus. Ein Tool Error bedeutet, dass Ausführung oder Ergebnis unzuverlässig ist.

Ein Tool Error DARF niemals als bestanden, toleriert oder lediglich report-only gelten.

### 4.5 Read-only und Determinismus

Gates DÜRFEN versionierte Quellen oder Zielprojekte nicht automatisch verändern. Zulässig sind nur registrierte Reports und temporäre Ausgaben.

Gleiche Baseline, Eingaben, Regeln und Toolversionen MÜSSEN zum selben fachlichen Ergebnis führen. Konsolenausgaben bleiben kompakt; Details gehören in Reports.

## 5. Quality Rule Model

### 5.1 Rule ID und Catalog

Jede technisch geprüfte Regel benötigt eine stabile `ruleId`. Tool-interne Standard-IDs können ergänzen, aber keine Springmaster Rule ID ersetzen.

Der Quality Rule Catalog enthält mindestens:

| Attribut | Inhalt |
|---|---|
| Identität | Rule ID, Titel, Owner |
| Quelle | normative Quelle und Abschnitt |
| Einordnung | Scope, Layer, Prüfbarkeitsklasse, Severity |
| Wirkung | Lifecycle, unterstützte Enforcement-Modi, Ausnahmefähigkeit |
| Umsetzung | Tool oder Reviewverfahren, erforderliche Evidence |
| Propagation | Project-New- und Managed-Project-Relevanz |

Der Catalog ist eine technische Registry, keine zweite normative Regelquelle.

### 5.2 Prüfbarkeitsklassen

| Klasse | Bedeutung |
|---|---|
| `automated` | vollständig deterministisch durch Tool entscheidbar |
| `partially-automated` | Tool liefert belastbare Indikatoren; Bewertung bleibt erforderlich |
| `manual-review` | systematische verantwortete Prüfung erforderlich |
| `architectural-review` | übergreifende Architekturabwägung erforderlich |

Eine Heuristik DARF nicht als vollständige Automatisierung dargestellt werden.

### 5.3 Severity

| Severity | Bedeutung |
|---|---|
| `BLOCKER` | verletzt zentrale Integrität oder verhindert die behauptete Qualifikation |
| `ERROR` | klarer Verstoß gegen eine akzeptierte, technisch entscheidbare Regel |
| `WARNING` | relevante Abweichung, Übergang oder noch nicht strict-reife Regel |
| `INFO` | positive, neutrale oder erläuternde Evidence |
| `MANUAL_REVIEW` | verantwortete Entscheidung erforderlich |

`BLOCKER` benötigt eine ausdrückliche normative Grundlage.

Severity und Enforcement-Modus sind getrennt. Ein `ERROR` in `report-only` blockiert den Toollauf nicht allein durch seine Severity.

## 6. Gate Model

### 6.1 Gate-Layer

| Layer | Verantwortungsbereich |
|---|---|
| `G0` | normative Quellen, Dokumentation und Regelabdeckung |
| `G1` | öffentliche API- und OpenAPI-Verträge |
| `G2` | Laufzeit- und MVC-Verhalten |
| `G3` | Java-, Package-, Layer-, Persistenz- und Komponentengrenzen |
| `G4` | Security-, Authentisierungs-, Autorisierungs- und Permission-Verträge |
| `G5` | integrierte Referenz- und Template-Qualifikation |
| `G6` | read-only Vergleich gemanagter Zielprojekte |

Jedes Gate und Finding weist mindestens einen Layer aus. Eine neue fachlich unabhängige Layerklasse benötigt eine Architekturentscheidung.

G6 DARF ohne spätere ausdrückliche Lieferentscheidung keine Zielprojekte ändern oder Remediation-Artefakte erzeugen.

### 6.2 Gate-Registry

Jedes Gate besitzt eine stabile `gateId` und einen Deskriptor mit mindestens:

- Name, Owner, Layer und Zweck,
- unterstützten Enforcement- und Scope-Modi,
- Eingaben, Voraussetzungen und geprüften Rule IDs,
- Report-Schema und Exit-Semantik,
- Fixture- und Selfcheck-Referenzen,
- Read-only- und Side-Effect-Eigenschaften.

### 6.3 Enforcement-Modi

| Modus | Wirkung |
|---|---|
| `report-only` | Regeln werden ausgeführt und berichtet; Findings blockieren den Toollauf nicht allein aufgrund ihrer Regelwirkung |
| `strict` | anwendbare strict-Regeln blockieren bei `BLOCKER` oder `ERROR` |
| `manual-review` | erzeugt Evidence für eine verantwortete Entscheidung; nur Ausführungsfehler blockieren den Toollauf |

Ein Gate darf nur qualifizierte und registrierte Modi anbieten.

### 6.4 Scope-Modi

- `changed`: zuverlässig ermittelte geänderte Elemente,
- `affected`: vollständig betroffene Module oder Contract-Familien,
- `all`: vollständiger registrierter Bestand,
- `target-compare`: read-only G6-Vergleich.

`changed` ist nur zulässig, wenn indirekte Auswirkungen zuverlässig ermittelt werden. Andernfalls ist mindestens `affected` erforderlich.

Ein Kommando wie `report` ist eine Operation und kein Enforcement-Modus.

## 7. Findings, Ergebnisse und Aggregation

### 7.1 Finding-Schema

Jedes Finding enthält mindestens:

- `gateId`, `ruleId`, Layer, Modus und Severity,
- normative Regelquelle,
- Subject und verständliche Nachricht.

Soweit anwendbar kommen Pfad oder Symbol, Erwartung und Istwert, Remediation, Fingerprint sowie Baseline-, Waiver- oder Suppression-Referenz hinzu.

Neue baselinierbare oder suppressierbare Regeln MÜSSEN stabile Finding-Fingerprints erzeugen.

### 7.2 Fachliche Gate-Ergebnisse

| Ergebnis | Bedeutung |
|---|---|
| `passed` | korrekt ausgeführt; keine relevanten offenen Findings |
| `passed-with-findings` | korrekt ausgeführt; nur nicht blockierende Findings |
| `blocked` | blockierendes Finding oder fehlende Pflichtentscheidung |
| `tool-error` | Ausführung oder Ergebnis nicht verlässlich |
| `not-applicable` | nach registrierter Scope-Regel nicht anwendbar |
| `not-executed` | vorgesehen, aber nicht ausgeführt |

Bestehende Reports mit `status: SUCCESS` bleiben während der Schema-Transition gültig, sofern Findings und Toolerfolg eindeutig getrennt erkennbar sind.

### 7.3 Aggregation

Bei Aggregation gilt grundsätzlich:

```text
tool-error
-> blocked
-> verpflichtendes not-executed
-> passed-with-findings
-> passed
```

Kein Aggregator darf `tool-error`, `blocked` oder ein verpflichtendes `not-executed` zu `passed` reduzieren. `not-applicable` benötigt eine registrierte Scope-Begründung.

Eine technisch erfolgreiche `manual-review`-Ausführung beendet eine erforderliche Engineering-Entscheidung nicht automatisch.

## 8. Report-only und Strict

### 8.1 Report-only

Eine anwendbare report-only-Regel MUSS ausgeführt und ausgewertet werden. `report-only` bedeutet nicht optional.

Findings werden als neu, bekannt, verändert oder entfallen bewertet und im Abschluss angemessen zusammengefasst. Sie blockieren den Toollauf nicht allein aufgrund der report-only Regelwirkung.

Ein Finding kann dennoch eine behauptete Qualifikation widerlegen, wenn es unabhängig davon eine bereits strict geltende Regel, zentrale Sicherheitsgrenze oder fehlerhafte Evidence betrifft.

### 8.2 Strict

Eine Regel ist nur strict, wenn der Rule Catalog dies nach akzeptierter Promotion ausweist.

Im Strict-Modus blockieren `BLOCKER` und `ERROR`. `WARNING`, `INFO` und `MANUAL_REVIEW` blockieren nicht automatisch; verpflichtende Reviewentscheidungen können Engineering Completion dennoch offenhalten.

Strict-Gates SOLLEN fachliche Findings aggregieren und Reports schreiben, bevor sie fehlschlagen. Fail-fast ist nur zulässig, wenn ein Ausführungsfehler keinen verlässlichen Report erlaubt.

## 9. Rule Lifecycle und Strict Promotion

### 9.1 Lifecycle

```text
proposed
-> implemented-report-only
-> qualified-report-only
-> strict
-> deprecated
-> retired
```

Eine proposed-Regel kann `rejected` oder `withdrawn` werden.

| Status | Mindestbedeutung |
|---|---|
| `proposed` | Regelbedarf beschrieben; keine verbindliche Gate-Wirkung |
| `implemented-report-only` | Quelle, Rule ID, Scope, erste Implementierung und Fehlertrennung vorhanden |
| `qualified-report-only` | Fixtures, Grenzfälle, Determinismus, Fehlalarmbewertung und Referenzausführung nachgewiesen |
| `strict` | ausdrückliche Promotion vollständig erfüllt |
| `deprecated` | Übergang mit Nachfolgeregel und Frist |
| `retired` | nicht mehr ausgeführt; historisch nachvollziehbar |

### 9.2 Strict Promotion

Die sechs Kriterien aus ADR-0006 sind zwingend:

1. akzeptierte Regelquelle oder ausdrückliche Tooling-Freigabe,
2. stabile und getestete Implementierung,
3. Referenzevidence durch Catalog-demo oder geeignete unabhängige Toolreferenz,
4. deterministische Pass-/Fail-Kriterien,
5. kompakte und verlässliche Reports,
6. dokumentierte Promotion mit Patch- und Versionswirkung.

Vor Aktivierung müssen außerdem:

- Bestandsfindings behoben, als Debt erfasst oder kontrolliert baselined sein,
- Waiver technisch validierbar sein,
- Project-New-Auswirkungen geprüft sein,
- Managed-Project-Auswirkungen und Übergang bewertet sein.

Promotion erfolgt pro Regel oder fachlich geschlossener Regelgruppe.

### 9.3 Keine implizite Promotion

Keine Promotion entsteht allein durch Plugin-, CI-, Maven-, Severity- oder Suppression-Änderung. Jedes bestehende Gate bleibt bis zur ausdrücklichen Entscheidung in seinem dokumentierten Status.

## 10. Findings-Baselines

Eine Findings-Baseline trennt bekannte Bestandsverstöße von neuen oder veränderten Findings. Sie erklärt bekannte Findings nicht für behoben.

Der bestehende Baseline-Review aus Patch 000070 ist historische Interpretationsevidence und unterdrückt keine Findings.

Eine technisch wirksame Baseline benötigt mindestens:

- ID, Owner, Rule IDs und Scope,
- stabile Finding-Fingerprints,
- Begründung, Risiko und Genehmigung,
- Erstellungs- und Reviewdatum,
- Abbau- oder Migrationsplan.

Eine reine Finding-Anzahl ist unzulässig. Baselinete Findings bleiben sichtbar. Neue oder veränderte Findings werden nicht automatisch toleriert.

Eine Baseline DARF nicht still erweitert werden. Eine abgelaufene oder zum Regelstand unpassende Baseline ist ungültig und darf keine erfolgreiche Strict-Qualifikation ermöglichen.

## 11. Waiver und technische Suppressions

### 11.1 Waiver

Ein Waiver erlaubt eine befristete Abweichung von einer geltenden technischen Regel im kleinsten möglichen Scope.

Er enthält mindestens:

- `waiverId`, Rule ID und Scope,
- Abweichung, Begründung, Risiko und Kompensation,
- Owner, Erstellungsdatum und Ablauf- oder Reviewdatum,
- Rückführungsplan und Genehmigungsreferenz.

Der Rule Catalog legt fest, ob eine Regel ausnahmefähig ist. Zentrale Integritäts- oder Sicherheitsregeln können nicht ausnahmefähig sein oder eine gesonderte Architekturentscheidung erfordern.

Nicht zulässig sind unbefristete oder ownerlose Waiver, Waiver ohne Rule ID, pauschale Profilabschaltung, Waiver für Tool Errors sowie repositoryweite Waiver ohne übergreifende Entscheidung.

Ein abgelaufener Waiver MUSS blockierend gemeldet werden.

### 11.2 Suppression

Eine Suppression ist nur der technische Mechanismus zur Unterdrückung oder Umklassifizierung eines konkreten Findings.

Sie MUSS:

- auf einen gültigen Waiver oder eine Findings-Baseline verweisen,
- den kleinsten technisch möglichen Scope besitzen,
- auf Existenz, Gültigkeit und Ablauf geprüft werden.

Inline-Suppressions ohne nachvollziehbare Regel- und Genehmigungsreferenz sind unzulässig. Die Syntax regelt der zuständige Standard oder Toolcontract.

Eine lokale Managed-Project-Abweichung benötigt eine Deviation und wird nicht als Springmaster-Waiver geführt.

## 12. Reports und Exit-Semantik

### 12.1 Reportfamilie

Der vorhandene Orchestrator verwendet:

```text
target/springmaster-gates/<gate-run-id>/
  summary.txt
  summary.json
  findings.jsonl
  rule-sources.json
  input-manifest.json
  evidence/
```

Spezialisierte Gates dürfen ergänzen, müssen aber in das gemeinsame Ergebnis- und Finding-Modell aggregierbar sein.

### 12.2 Mindestinhalt

Reports weisen mindestens aus:

- Schema-, Gate-, Regel- und Toolversionen,
- Run-ID, Baseline, Scope und Enforcement-Modus,
- Eingaben sowie ausgeführte und nicht anwendbare Regeln,
- Findings und Tool Errors,
- Baseline-, Waiver- und Suppression-Referenzen,
- fachliches Gesamtergebnis.

Volatile Werte dürfen Regressionstests nicht fachlich instabil machen. Sie werden kontrolliert oder von Golden-Vergleichen getrennt.

Die Konsole enthält kompakt Gate oder Profil, Scope, Modus, Ergebnis, relevante Finding-Zahlen, Tool-Error-Hinweis und Reportpfad.

### 12.3 Exit-Semantik

Der technische Exit muss mindestens erfolgreiche Ausführung, blockierende Strict-Findings, Tool-/Konfigurationsfehler und ungültige Nutzung unterscheiden.

Numerische Codes werden zentral im Build and Tooling Standard und Exit-Code-Contract festgelegt.

Report-only- und Manual-review-Läufe dürfen wegen nicht blockierender Findings nicht mit einem Tool-Error-Code enden.

## 13. Fixtures und Harness-Selbstprüfung

Für jede strict-fähige automatisierte Regel bestehen mindestens:

- positiver und negativer Fall,
- relevanter Grenzfall,
- Tool-Error- oder ungültiger Eingabefall, soweit anwendbar.

Für Baselines, Waiver und Suppressions werden zusätzlich Ablauf, Scope und unbekannte Referenz geprüft.

Jede Gate-Familie besitzt einen reproduzierbaren Selfcheck oder Contract Test für:

- Startbarkeit und Eingabevalidierung,
- Reportdateien und Schema,
- Finding-Pflichtfelder, Modi und Severity,
- Exit-Semantik und Tool-Error-Trennung,
- deterministische Wiederholung,
- Schutz vor Quellmutation.

Änderungen an Rule Catalog, Gate, Report-Schema, Baseline- oder Waiverlogik benötigen positive und negative Regressionstests. Golden Fixtures werden nur bei beabsichtigter Vertragsänderung aktualisiert.

Der Orchestrator prüft zusätzlich unbekannte Rule IDs, fehlende Quellen, abgelaufene Waiver oder Baselines, unregistrierte Suppressions und Ergebnisaggregation.

## 14. Einführung neuer Regeln und Tools

### 14.1 Neue Regel

Eine neue Regel benötigt:

1. normative Aussage und Owner,
2. Rule ID, Scope, Layer, Prüfbarkeitsklasse und Severity,
3. Tool- oder Reviewzuordnung,
4. Fixtures und Evidence-Anforderung,
5. Rule-Catalog-Eintrag,
6. grundsätzlich report-only Qualifikation vor Strict-Aktivierung.

### 14.2 Neues Tool

Ein neues Tool oder Plugin benötigt:

- konkrete Rule-ID-Familie und nachgewiesene Lücke bestehender Mittel,
- Dependency- und Lizenzprüfung,
- reproduzierbare lokale Ausführung,
- Owner und begrenzte Konfiguration,
- Tool-Error-, Report-, Fixture- und Selfcheck-Integration,
- Bewertung von Laufzeit, Wartung und Propagation.

Ein Tool wird nicht allein eingeführt, weil es allgemein als Best Practice gilt.

Prüfen mehrere Tools dieselbe Regel, muss ein kanonisches Finding- und Aggregationsverhalten Doppelmeldungen vermeiden.

## 15. Project-New und gemanagte Projekte

Eine für erzeugte Projekte geltende strict-Regel MUSS vor Aktivierung durch Fresh-Project-Acceptance nachgewiesen sein.

Project-New liefert nur die für das erzeugte Projektprofil geltenden Regeln, Contracts und Gate-Einstiege. Springmaster-spezifische Prüfungen werden nicht unkontrolliert kopiert.

Gemanagte Projekte adoptieren einen identifizierbaren Rule-Catalog- und Gate-Vertragsstand. Lokale Ergänzungen benötigen Extension Points; lokale Abweichungen eine Managed-Project-Deviation.

Target Comparison bleibt read-only und grundsätzlich report-only, bis eine spätere Architektur- und Lieferentscheidung anderes autorisiert. Findings werden als Target-Comparison-Findings gekennzeichnet.

## 16. Technische Ableitungen und Transition

### 16.1 Contracts

Innerhalb der bestätigten Contract-Struktur werden mindestens benötigt:

```text
contracts/governance/quality-rule-catalog.json
contracts/governance/gate-result-contract.json
contracts/governance/quality-waiver-contract.json
contracts/governance/findings-baseline-contract.json
```

Ein eigener Gate-Registry- oder Report-Schema-Contract entsteht nur bei eigenständigem Owner, Version oder Lifecycle.

Die Contracts definieren IDs, Status, Layer, Modi, Severity, Pflichtattribute, Aggregation, Fingerprints, Ausnahme- und Ablaufreferenzen sowie Schemaversionen.

### 16.2 Migrationsarme Einführung

Der vorhandene Report-only-Seed, seine Selfchecks, Regressionstests und das Maven-Profil bleiben gültig. Sie werden nicht allein wegen zukünftiger Contract-Namen umgebaut.

`springmaster.report-only-report.v1` bleibt gültig, bis ein qualifizierter Migrationsschnitt ein neues Schema einführt. Zukünftige fachliche Gate-Ergebnisse werden zunächst auf die bestehende `SUCCESS`- und Finding-Semantik abgebildet.

Der Baseline-Review aus Patch 000070 bleibt historische Evidence. Eine technisch wirksame Baseline entsteht erst mit dem Baseline Contract.

Kein bestehendes Gate wird durch diese Governance strict.

### 16.3 Technischer Umsetzungsstand

Slice `S-02` des Pilotsprints `SPRINGMASTER-SPRINT-001` materialisiert erstmals den zentralen Quality Rule Catalog und die Gate Registry.

Der report-only Stand umfasst:

- `contracts/governance/quality/quality-rule-catalog.json`,
- `contracts/governance/quality/gate-registry.json`,
- den read-only Validator `bin/quality-registry.py`,
- positive, negative und Tool-Error-Fixtures unter `src/test/resources/tooling/quality-registry-v1/`.

Registriert sind die qualifizierten Regeln der Documentation-, Project-Directory-, Sprint- und Test-Contract-Gates sowie die in S-01 implementierten Engineering-Profil- und Completion-Regeln.

Slice `S-04` materialisiert `engineering-qualification-gate-v1` als read-only, report-only Gate. Die bestehenden Engineering-Regeln erhalten damit eine produktive Gatezuordnung; vier zusätzliche `ENG-QUAL`-Regeln prüfen Record-Identität, erforderliche registrierte Checks, Completion-/Tool-Error-Konsistenz und Registry-Wiring. Das Gate wertet Evidence aus, führt registrierte Gates aber nicht selbst aus.

Der Catalog enthält Titel und normative Quellenreferenzen, aber keinen duplizierten Regeltext. Die Gate Registry bleibt auf `report-only`, read-only und Reportdateien als einzige Side Effects begrenzt. Keine Regel und kein Gate wird durch diesen Umsetzungsstand `strict`.

### 16.4 Pilotabschluss und Enforcement-Entscheidung

Der Engineering Qualification Pilot schließt mit 72 eindeutig registrierten Quality Rules und sechs Gate-Deskriptoren. Alle im Pilot erzeugten oder zugeordneten Gates bleiben `report-only`. Die technische Integration und Fixture-Abdeckung ist qualifiziert; eine Strict-Promotion wurde weder beantragt noch erteilt.

Strict-, Project-New- und Managed-Project-Aktivierung bleiben getrennte Folgeentscheidungen. Der Aktivierungs- und Impact-Nachweis ist `PROJECT_DOCS/TOOLING/ENGINEERING_QUALIFICATION_ACTIVATION_RECOMMENDATION.md`.

## 17. Abnahmekriterien

Diese Governance ist vollständig, wenn:

1. jede geprüfte Regel eine normative Quelle und Rule ID benötigt,
2. Prüfbarkeitsklassen algorithmische und semantische Prüfungen trennen,
3. Layer, Enforcement- und Scope-Modus eindeutig sind,
4. Findings und Tool Errors getrennt bleiben,
5. Report-only verbindlich, aber nicht automatisch blockierend ist,
6. Strict Promotion ADR-0006 erfüllt,
7. Baselines fingerprint-basiert und kontrolliert sind,
8. Waiver befristet und Suppressions referenziert sind,
9. Reports Regeln, Inputs, Findings und Ausführungsfehler nachvollziehbar ausweisen,
10. positive, negative und Tool-Error-Fixtures vorgesehen sind,
11. der Harness seine Contracts und Ausnahmezustände selbst prüft,
12. neue Tools nur für registrierte Regeln eingeführt werden,
13. Project-New und Managed Projects kontrolliert propagiert werden,
14. der bestehende Report-only-Harness ohne Big-Bang-Migration fortgeführt werden kann.

## 18. Lifecycle

| Datum | Vorher | Nachher | Grund |
|---|---|---|---|
| 2026-07-22 | – | draft | Konsolidierter Erstentwurf auf Basis von ADR-0006 und aktuellem Gate-Harness |
| 2026-07-23 | draft | draft | S-04 registriert das qualifizierte report-only Engineering-Qualification-Gate ohne Strict-Promotion. |
| 2026-07-23 | draft | draft | Pilotabschluss bestätigt 72 Rules und sechs report-only Gates; keine Strict-Promotion. |

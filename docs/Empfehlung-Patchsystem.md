# Empfehlung zur Weiterentwicklung des Patchsystems im Springmaster-Projekt

## Zielsetzung

Das Patchsystem des Springmaster-Projekts hat sich als zentrale Grundlage für die Verteilung von Änderungen auf nachgelagerte Projekte etabliert. Es ermöglicht reproduzierbare, nachvollziehbare und versionierte Anpassungen über standardisierte Patch-Archive.

Im praktischen Einsatz zeigt sich jedoch, dass die eigentliche Patch-Anwendung inzwischen deutlich robuster ist als die anschließende Verifikation. Ein erheblicher Teil der manuellen Arbeit entfällt auf:

* Ausführen projektspezifischer Tests
* Umleitung von Konsolenausgaben in Logdateien
* Analyse von Buildfehlern
* Extraktion relevanter Fehlermeldungen
* Erzeugung von Exporten
* Dokumentation des Abnahmeergebnisses

Diese Schritte werden aktuell projektabhängig manuell ausgeführt und führen zu langen Kommando-Stacks sowie uneinheitlichen Vorgehensweisen.

Ziel dieser Empfehlung ist die Erweiterung des Patchsystems um einen standardisierten Abnahme-Workflow.

---

# Beobachtungen aus der Praxis

Bei der Integration eines Patches in das Contacts-Projekt trat folgendes Muster auf:

1. Patch erfolgreich erstellt
2. Patch erfolgreich angewendet
3. Buildfehler im projektspezifischen Test
4. Fehlerausgabe verschwindet im normalen Terminal-Output
5. Zusätzliche Kommandos erforderlich:

    * tee
    * tail
    * grep
    * erneute Testläufe
6. Manuelle Analyse der eigentlichen Fehlerursache

Der tatsächliche Fehler war fachlich klein (XML statt JSON im MockMvc-Test), die Analyse erforderte jedoch mehrere zusätzliche Schritte.

Der Aufwand entstand nicht durch die Patchlogik selbst, sondern durch die fehlende Standardisierung der Patch-Abnahme.

---

# Empfehlung A – Einführung eines Patch-Abnahme-Workflows

## Neuer Befehl

```bash
./bin/patch.sh accept <patch.zip>
```

Der Befehl soll einen vollständigen Abnahmeprozess kapseln.

---

## Beispiel

```bash
./bin/patch.sh accept \
  /home/cb/Downloads/000123_example.patch.zip \
  --test BatchJobControllerTest \
  --full-test \
  --export
```

---

## Ablauf

### Phase 1

Patchprüfung

```text
- Existenzprüfung
- Dry-Run
- Konsistenzprüfung
```

---

### Phase 2

Patchanwendung

```text
- Apply
- Aktualisierung der Patch-Historie
- Ausgabe des aktuellen Patchstands
```

---

### Phase 3

Gezielte Verifikation

Falls angegeben:

```bash
--test BatchJobControllerTest
```

Ausführung:

```bash
mvn test -Dtest=BatchJobControllerTest
```

Die Ausgabe wird automatisch gespeichert:

```text
patches/logs/<patch-id>/test.log
```

---

### Phase 4

Fehleranalyse

Bei Fehlern sollen automatisch relevante Zeilen extrahiert werden:

Suche nach:

```text
ERROR
FAILURE
Exception
Caused by:
```

Beispiel:

```text
========================
ERROR SUMMARY
========================

BatchJobControllerTest

Caused by:
No value at JSON path "$[0].definitionId"
```

Dadurch entfällt das manuelle Arbeiten mit:

```bash
tail
grep
tee
```

---

### Phase 5

Vollständige Tests

Optional:

```bash
--full-test
```

führt aus:

```bash
mvn test
```

Auch diese Ausgabe wird gespeichert.

---

### Phase 6

Export

Optional:

```bash
--export
```

führt aus:

```bash
./bin/export.sh --zip
```

und gibt direkt den erzeugten Exportpfad aus.

---

# Empfehlung B – Separater Verify-Modus

Zusätzlich wird ein Verifikationsmodus empfohlen.

## Beispiel

```bash
./bin/patch.sh verify latest
```

oder

```bash
./bin/patch.sh verify 000123_example
```

---

## Zweck

Erneute Ausführung von:

* Tests
* Export
* Konsistenzprüfungen

ohne erneute Patch-Anwendung.

Dies ist insbesondere nützlich bei:

* CI-Problemen
* Folgevalidierungen
* Regressionstests
* Nachträglichen Baseline-Exporten

---

# Empfehlung C – Strukturierte Build-Logs

Aktuell entstehen Build-Logs häufig nur temporär im Terminal.

Empfohlen wird:

```text
patches/logs/<patch-id>/
```

mit:

```text
apply.log
test.log
full-test.log
export.log
summary.log
```

Dadurch werden alle Informationen dauerhaft projektintern archiviert.

---

# Empfehlung D – Fehlerzusammenfassung

Nach Abschluss der Verifikation sollte automatisch eine Kurzfassung erzeugt werden.

Beispiel:

```text
Patch-ID:
000123_example

Status:
FAILED

Test:
BatchJobControllerTest

Ursache:
No value at JSON path "$[0].definitionId"

Datei:
BatchJobControllerTest.java:50
```

bzw.

```text
Patch-ID:
000123_example

Status:
SUCCESS

Tests:
27 erfolgreich

Export:
contacts_export_full_2026-06-24_12-07-23-665Z.zip
```

---

# Nutzen

Die vorgeschlagene Erweiterung bietet folgende Vorteile:

* deutlich kürzere Benutzerkommandos
* einheitliche Patch-Abnahme in allen Projekten
* automatische Fehlerdiagnose
* dauerhafte Build- und Testprotokolle
* weniger manuelle Analysearbeit
* bessere Nachvollziehbarkeit von Patch-Integrationen
* direkte Wiederverwendbarkeit in allen vom Springmaster versorgten Projekten

---

# Empfehlung

Es wird empfohlen, die Erweiterungen nicht zuerst in einzelnen Fachprojekten umzusetzen, sondern direkt im Springmaster-Projekt zu implementieren.

Da Springmaster die Referenzimplementierung für das gemeinsame Tooling darstellt, profitieren anschließend sämtliche angebundenen Projekte automatisch von den Verbesserungen.

Die Priorität dieser Erweiterung wird als hoch eingeschätzt, da sie die tägliche Arbeit mit Patches vereinfacht und gleichzeitig die Transparenz sowie die Qualität der Patch-Abnahme erhöht.

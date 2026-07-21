# 000160_springmaster_patch_accept_bounded_validation_log_names

## Ziel

Begrenzt die Dateinamen konfigurierter Testselektor-Logs im Patch-Acceptance-Runner, damit lange Maven-Testselektoren nicht vor Testbeginn mit `OSError: [Errno 36] File name too long` abbrechen.

## Änderungen

- Test-Log-Basenamen sind deterministisch auf 120 UTF-8-Bytes begrenzt.
- Lange Selektoren erhalten einen gekürzten lesbaren Anteil und ein 12-stelliges SHA-256-Präfix.
- Nach der Normalisierung kollidierende oder wiederholte Selektoren werden ohne Überschreiben disambiguiert.
- Der vollständige Selektor bleibt im Logkopf und im ausgeführten Kommando erhalten.
- Die transaktionale Acceptance-IT enthält den realen langen CatalogItem-Selektor sowie zwei normalisiert kollidierende Selektoren.
- Workflow- und Acceptance-Dokumentation beschreiben den neuen Diagnosevertrag.

## Verifikation

- `python3 -m py_compile bin/patch.py`
- `bash -n bin/patch-transactional-accept-it.sh`
- gezielter Helper-Test für lange, kollidierende und wiederholte Selektoren
- `bin/patch-transactional-accept-it.sh` erreicht `PATCH_TRANSACTIONAL_ACCEPT_IT=PASS`
- `bin/documentation-gate.sh --check`
- `bin/documentation-gate-it.sh`
- `git diff --check`

## Technische Schulden und Planbezug

Der zuvor unbeschränkte Logdateiname ist geschlossen. Es werden keine Runtime-Abhängigkeit, kein neues Patchformat und keine Zielprojektmutation eingeführt. Die äußere Parent-Summary meldet Child-Fehler weiterhin allgemein als `worktree-validation`; eine verbesserte Root-Cause-Weitergabe bleibt als getrennte, nicht blockierende Diagnoseverbesserung offen. Die Tooling-Version wird gemäß Version Policy erst im release-schließenden Patch erhöht.

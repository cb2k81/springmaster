# 000165 — Patch Run API legacy evidence compatibility

## Anlass

Patch `000164_springmaster_patch_run_api_git_transaction_hardening` wurde erfolgreich akzeptiert und als Commit übernommen. Die abschließende Prüfung zeigte jedoch zwei Integrationslücken:

1. `patch.sh doctor` bewertete alle historischen, vor Einführung der Run API angewendeten Patches ohne kanonische `accepted.json`-Evidence als Fehler. Dadurch entstand auf dem realen Repository ein falsches `FAIL` mit 133 Findings, obwohl Working Tree, aktueller Commit und aktuelle Acceptance konsistent waren.
2. Ein Bootstrap-Beobachter hielt einen temporären, zeitgestempelten `SUMMARY.txt`-Pfad fest. Nach erfolgreicher Selbstaktualisierung und Veröffentlichung der kanonischen Acceptance war dieser Attempt-Pfad nicht mehr vorhanden. Die neue Status-API konnte den Patchzustand zwar über die Patch-ID auflösen, Run-ID, Artifact-ID und Aktualisierungszeit wurden aus der kanonischen Evidence aber noch nicht vollständig übernommen.

## Änderungen

- Einführung des expliziten Run-API-Cutovers bei Patchnummer `000164`.
- `doctor` aggregiert ältere angewendete Patches ohne kanonische Acceptance in genau eine historische Warnung.
- Für angewendete Patches ab dem Cutover bleibt fehlende kanonische Acceptance ein Fehler.
- `status`, `watch`, `wait` und `result` lesen `accepted.json` als dauerhafte Quelle für Run-ID, Artifact-ID, Commitstatus und Zeitstempel.
- Eine ursprüngliche Run-ID wird auch nach Entfernung oder Kompaktierung des temporären Attempt-Verzeichnisses zur kanonischen Acceptance aufgelöst.
- Dokumentation und `AGENTS.md` untersagen dauerhafte Pointer auf temporäre Attempt-Summaries und beschreiben die Cutover-Semantik.
- Der Run-API-Integrationstest deckt historische Doctor-Kompatibilität, post-Cutover-Fehler und Statusauflösung nach Evidence-Kompaktierung ab.

## Git- und Transaktionswirkung

- Keine Änderung an Patch-Apply, Patch-Payload oder Git-Transferpfaden.
- Keine implizite Migration oder Erzeugung historischer Acceptance-Dateien.
- Historische Git- und Patcharchiv-Wahrheit bleibt unverändert.
- Neue unvollständige Transfers werden weiterhin fail-closed erkannt.

## Whitespace und Effizienz

- Keine Repository-weite Formatierung oder Normalisierung.
- Geänderte Dateien werden weiterhin ausschließlich über pfadbegrenzte `git diff --check`, `git diff --cached --check` und `git show --check` geprüft.
- Die 133 historischen Einzelmeldungen werden zu einer Warnung mit Zähler verdichtet.

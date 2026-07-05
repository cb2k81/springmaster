# CHANGELOG 000082 springmaster patch runtime locking background git rollback

## Summary

Härtet das Springmaster-Patchsystem als portable Patch-Engine für Springmaster und Zielprojekte.

## Changes

- Ergänzt projektweiten Write-Lock für mutierende `accept`, `apply`, `verify` und `rollback` Läufe.
- Ergänzt `--wait`, `--lock-timeout` und `--background` für lange Accept-/Verify-Läufe.
- Schreibt zusätzlich `SUMMARY.txt` und `STATUS.txt` neben `summary.log`.
- Erzeugt nach erfolgreichem Accept ein patchbezogenes `git-commit.sh` ohne `git add .`.
- Macht Test-, Export- und Tooling-Selfcheck-Kommandos projektlokal über `.env` konfigurierbar.
- Stellt Maven-Defaults auf `mvn -B -ntp ...` um.
- Ergänzt `bin/patch-system-it.sh` als Fixture-Test für Apply, Accept, Rollback, Lock-Busy und optional Background.
- Dokumentiert Runtime-Härtung, Zielprojekt-Portabilität, kompakte Konsole und Rollback-Testpflicht.
- Erhöht `PLATFORM_TOOLING_VERSION` auf `0.3.12`.

## Validation

- `python3 -m py_compile ./bin/patch.py`
- `bash -n ./bin/*.sh ./bin/lib/core/*.sh ./bin/lib/dbtool/*.sh`
- `PATCH_SYSTEM_IT_WITH_BACKGROUND=0 ./bin/patch-system-it.sh`

Der optionale Background-Fixturepfad ist im Testskript enthalten und kann mit `PATCH_SYSTEM_IT_WITH_BACKGROUND=1` aktiviert werden.

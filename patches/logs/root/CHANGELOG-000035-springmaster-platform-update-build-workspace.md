# 000035_springmaster_platform_update_build_workspace

## Scope

Springmaster-only tooling/documentation patch. No target project changes.

## Änderungen

- `bin/platform-update.sh` schreibt generierte Operationsartefakte standardmäßig nach `build/platform-update/**`.
- `platform-update generate` setzt den Standard-Workspace vor der Generierung zurück.
- `platform-update workspace` zeigt die aktuellen Workspace-Pfade an.
- Dokumentation grenzt permanente `platform/update/**`-Definitionen von temporären Build-/Transferartefakten ab.
- Versionsstand auf `PLATFORM_UPDATE_VERSION=0.6.1` und `PLATFORM_STATE_PATCH=000035_springmaster_platform_update_build_workspace` gesetzt.

## Validierung

- `./bin/patch.sh apply --dry-run`
- `./bin/patch.sh apply`
- `bash -n bin/platform-update.sh`
- `python3 -m py_compile bin/patch.py`
- `./bin/platform-update.sh workspace`
- `./bin/platform-update.sh generate idm --profile core --dry-run`
- `./bin/platform-update.sh generate idm --profile core`
- Full-ZIP-Export-Hygieneprüfung gegen ausgeschlossene Build-/Operationsartefakte

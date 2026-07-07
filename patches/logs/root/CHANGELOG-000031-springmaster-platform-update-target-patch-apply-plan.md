# 000031 – Springmaster Platform Update Target Patch Apply Plan

## Typ

Platform-Update-/Tooling-Patch.

## Änderungen

* `bin/platform-update.sh` erhält den Befehl `apply-plan`.
* Für generierte Zielprojekt-Patch-ZIPs können Markdown-Plan und manuell ausführbares Shell-Skript erzeugt werden.
* Die Planerzeugung bleibt nicht-invasiv und schreibt nicht nach `TARGET_PATH`.
* Der `platform-update`-Scope umfasst künftig `PROJECT_DOCS/TOOLING/PLATFORM_UPDATE*.md`.
* Die Platform-Update-Version steigt auf `0.4.0`.

## Validierung

Erwartete Validierung über:

```bash
./bin/patch.sh accept /home/cb/Downloads/000031_springmaster_platform_update_target_patch_apply_plan.zip
./bin/platform-update.sh generate idm --profile core
./bin/platform-update.sh apply-plan idm --zip platform/update/generated/<generated>.zip
```

`mvn test` ist nicht erforderlich, da kein Java-Code und keine Maven-/Build-Konfiguration geändert werden.

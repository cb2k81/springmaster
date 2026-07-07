# 000030 - springmaster patch project local scope env

## Typ

Tooling / Patchsystem

## Änderungen

* Ergänzt das Patchsystem um projektlokale Scope- und Pfaderweiterungen aus `.env`.
* Unterstützt zusätzliche Pfade für bestehende Scopes über `PATCH_SCOPE_<SCOPE>_EXTRA_PATHS`.
* Unterstützt zusätzliche lokale Scopes über `PATCH_LOCAL_SCOPES` und `PATCH_SCOPE_<SCOPE>_PATHS`.
* Dokumentiert die Regel, dass projektspezifische Zusatzbereiche nicht zentral in Springmaster hart kodiert werden.
* Aktualisiert `.env.example`, das Springmaster-Env-Template und das Project-Skeleton-Env-Template.

## Versionierung

* `PLATFORM_VERSION=0.9.2-foundation`
* `PLATFORM_TOOLING_VERSION=0.3.6`
* `PLATFORM_STATE_PATCH=000030_springmaster_patch_project_local_scope_env`

## Validierung

Tooling-Patch ohne Java-/Build-Konfigurationsänderung. Standardabnahme über:

```bash
./bin/patch.sh accept /home/cb/Downloads/000030_springmaster_patch_project_local_scope_env.zip
```

`accept` führt Dry-run, Apply, Tooling-Selfcheck und Full-ZIP-Export aus.

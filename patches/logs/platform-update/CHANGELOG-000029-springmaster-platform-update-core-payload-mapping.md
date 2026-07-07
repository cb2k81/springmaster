# 000029 - Springmaster Platform Update Core Payload Mapping

## Scope

`platform-update`

## Änderungen

* `platform-update generate --profile core` erzeugt nun Zielprojekt-Patch-ZIPs mit realem Core-Payload.
* Der Core-Payload umfasst:
  * `src/main/java/de/cocondo/system/**`
  * `src/test/java/de/cocondo/system/**`
  * `PROJECT_DOCS/CORE/**`
* Für Profile ohne Payload-Mapping bleibt die Generierung plan-only.
* Die Generierung bleibt nicht-invasiv und schreibt nicht in Zielprojektpfade.
* `PLATFORM_UPDATE_VERSION` wird auf `0.3.0` erhöht.

## Validierung

* `bash -n bin/platform-update.sh`
* `python3 -m py_compile bin/patch.py`
* `./bin/platform-update.sh generate idm --profile core --dry-run`
* `./bin/platform-update.sh generate idm --profile core`
* Kontrolle des generierten ZIPs auf `manifest.json`, `files/src/main/java/de/cocondo/system/**`, `files/src/test/java/de/cocondo/system/**`, `files/PROJECT_DOCS/CORE/**` und `logs/**`

# CHANGELOG 000023 - springmaster patch accept workflow hardening

## Zweck

Härtet den in `000022` eingeführten Patch-Abnahme-Workflow.

## Änderungen

* `patch.sh accept` und `patch.sh verify` verwenden standardmäßig das Profil `auto`.
* Full-ZIP-Export ist für Accept/Verify standardmäßig aktiv.
* Vollständiger Maven-Test wird automatisch aktiviert, wenn Java-Code, Tests oder Build-Konfiguration betroffen sind.
* Profile `auto`, `docs`, `tooling` und `code` werden unterstützt.
* Optionen `--no-full-test` und `--no-export` erlauben explizite Abweichungen.
* `tooling-selfcheck.sh` erzeugt im Standard nur noch einen Full-ZIP-Export.
* Tooling- und Versionierungsdokumentation wurden synchronisiert.

## Version

```text
PLATFORM_VERSION=0.6.1-foundation
PLATFORM_TOOLING_VERSION=0.3.1
PLATFORM_STATE_PATCH=000023_springmaster_patch_accept_workflow_hardening
```

## Validierung

Tooling-Patch ohne Java-Code- oder Maven-Build-Konfigurationsänderung.

Erforderlich:

```bash
./bin/patch.sh accept <patch.zip>
```

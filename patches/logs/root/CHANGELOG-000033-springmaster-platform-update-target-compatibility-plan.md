# 000033_springmaster_platform_update_target_compatibility_plan

## Zweck

Ergänzt die Platform-Update-Mechanik um einen nicht-invasiven Target-Compatibility-Plan.

## Auslöser

Der Zielprojekt-Preflight für `idm` meldete:

```text
Unbekannter Patch-Scope im manifest.json: core
```

Damit ist der generierte Core-Payload-Patch fachlich korrekt, aber das Zielprojekt-Patchsystem ist noch nicht kompatibel.

## Änderungen

* `bin/platform-update.sh` erhält den Befehl `compatibility-plan`.
* Der Befehl erzeugt ein Compatibility-ZIP unter `platform/update/generated/**`.
* Der Befehl erzeugt Plan- und Skriptartefakte unter `platform/update/manifests/**`.
* Zielprojekte werden nicht automatisch verändert.
* Projektspezifische Zusatz-Scopes und Zusatzpfade bleiben in der `.env` des Zielprojekts.

## Version

```text
PLATFORM_VERSION=0.12.0-foundation
PLATFORM_UPDATE_VERSION=0.6.0
PLATFORM_STATE_PATCH=000033_springmaster_platform_update_target_compatibility_plan
```

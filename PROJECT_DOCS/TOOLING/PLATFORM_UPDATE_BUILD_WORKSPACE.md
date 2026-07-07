# Platform-Update Build Workspace

## Zweck

Springmaster erzeugt Zielprojekt-Patches, Preflight-Logs, Apply-Pläne und Compatibility-Pläne künftig in einem dedizierten Build-/Transferbereich:

```text
build/platform-update/**
```

Dieser Bereich ist ein Operationsartefakt. Er gehört nicht zur regulären Springmaster-Baseline und wird durch die Export-Hygiene ausgeschlossen.

## Verzeichnisstruktur

```text
build/platform-update/
  generated/   # generierte Zielpatch-ZIPs
  manifests/   # Review-Pläne und Review-Env-Dateien, keine target-mutierenden Skripte
  logs/        # ausgabearme Target-Apply-Logs und Summary-Dateien
  payload/     # reserviert für vorbereitete Payload-Staging-Dateien
```

## Überschreibregel

Der Standardlauf von `platform-update generate` setzt den Workspace zurück, bevor neue Transferartefakte erzeugt werden. Dadurch bleiben alte Zielpatches, alte Pläne und alte Logs nicht versehentlich als aktueller Arbeitsstand liegen.

Benutzerdefinierte Ausgabeverzeichnisse über `--output` bleiben möglich und werden nicht automatisch gelöscht.

## Permanente Platform-Update-Dateien

Dauerhaft versioniert bleiben nur Definition, Dokumentation und Zielregistry:

```text
platform/update/targets/**
platform/update/README.md
platform/versions/platform.env
PROJECT_DOCS/TOOLING/PLATFORM_UPDATE*.md
PROJECT_DOCS/TARGET_UPDATES/**
```

Nicht dauerhaft versioniert sind:

```text
build/platform-update/**
platform/update/generated/**      # Legacy-Ausgabeort, nicht mehr Standard
platform/update/manifests/**      # Legacy-Ausgabeort, nicht mehr Standard
```

## Sicherheitsregel

Der Workspace darf Zielprojekt-Artefakte enthalten, aber Springmaster verändert Zielprojekte dadurch nicht. Zielprojekt-Änderungen bleiben an einen expliziten Review- und Apply-Schritt gebunden.




## Review-Gate-Abgrenzung seit 000036

`build/platform-update/manifests/**` enthält nur Review-Artefakte. Dateien aus diesem Bereich dürfen nicht mehr als ausführbare Zielprojektänderung verstanden werden. Die reale Zielprojektänderung liegt ausschließlich im Befehl `platform-update target-apply` und wird vollständig nach `build/platform-update/logs/**` protokolliert.


## Payload-Profil-Abgrenzung seit 000037

Der Build-Workspace enthält generierte Zielpatches für einzelne Payload-Profile. Dabei ist der Workspace weiterhin nur Ablageort, nicht Architekturentscheidung. Welche Dateien ein Zielpatch enthält, bestimmt das gewählte Profil, zum Beispiel `core-runtime`, `core-tests`, `core-docs` oder `tooling`.

Reguläre Exports schließen `build/platform-update/**` weiterhin vollständig aus.

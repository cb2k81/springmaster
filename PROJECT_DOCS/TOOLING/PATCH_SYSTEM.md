# Patch System

## Zweck

Das Patchsystem verarbeitet manifestbasierte Patch-ZIPs und protokolliert jede Anwendung unter `patches/archives/**`.

## Kommandos

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
./bin/patch.sh list
./bin/patch.sh show latest
./bin/patch.sh rollback --dry-run latest
./bin/patch.sh rollback latest
```

## Patch-Format

```text
manifest.json
files/**
logs/CHANGELOG-*.md
```

Optional:

```text
delete/**
```

## Erweiterte Scopes seit 000003

Zusätzlich zu den Bootstrap-Scopes sind vorbereitet:

* `templates`
* `planning`
* `target-registry`
* `platform-update`

Damit können spätere Patches die Project-Skeleton-, Planungs- und Zielprojektbereiche ohne Umgehung des Patchsystems pflegen.

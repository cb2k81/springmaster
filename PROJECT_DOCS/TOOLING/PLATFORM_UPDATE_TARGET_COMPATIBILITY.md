# Platform Update Target Compatibility

## Zweck

Dieses Dokument beschreibt den Target-Compatibility-Schritt für generierte Springmaster-Zielpatches.

## Ausgangsbefund

Ein Zielprojekt kann beim Preflight blockieren, wenn dessen lokales Patchsystem den generierten Scope noch nicht kennt, zum Beispiel:

```text
Fehler: Unbekannter Patch-Scope im manifest.json: core
```

## Befehl

```bash
./bin/platform-update.sh compatibility-plan <target> --zip <generated-patch.zip>
```

Der Befehl erzeugt nicht-invasiv:

```text
build/platform-update/generated/*_springmaster_platform_update_compatibility_for_<target>.zip
build/platform-update/manifests/*_compatibility_plan.md
build/platform-update/manifests/*_compatibility_plan.env
```

Es wird seit `000036` kein ausführbares Compatibility-Apply-Skript mehr erzeugt.

## Nicht-invasives Verhalten

Springmaster verändert das Zielprojekt nicht. Der erzeugte Plan ist ein Review-Gate. Die reale Zielprojektänderung erfolgt erst nach expliziter Ausführung von:

```bash
./bin/platform-update.sh target-apply <target> --zip <compatibility-patch.zip>
```

## Inhalt des Compatibility-ZIPs

Das generierte Compatibility-ZIP aktualisiert im Zielprojekt nur:

```text
bin/patch.py
bin/patch.sh
PROJECT_DOCS/PLATFORM_UPDATES/<compatibility-id>.md
```

Der Patch verwendet bewusst den Scope `root`, damit er auch von älteren Zielprojekt-Patchsystemen angenommen werden kann, die den Scope `core` noch nicht kennen.

## Projektlokale Scope-Regel

Fachprojekt-spezifische Zusatz-Scopes und Zusatzpfade werden nicht in Springmaster hart kodiert. Sie gehören in die `.env` des Zielprojekts:

```env
PATCH_LOCAL_SCOPES=reporting
PATCH_SCOPE_REPORTING_PATHS=src/main/java/com/example/reporting/**;src/test/java/com/example/reporting/**
PATCH_SCOPE_REPORTING_LOG_DIR=reporting
```

## Folgeablauf

Nach erfolgreicher Compatibility-Anwendung wird der ursprüngliche generierte Zielpatch erneut geprüft:

```bash
cd /opt/cocondo/springmaster
ZIP="$(ls -1t build/platform-update/generated/*_springmaster_platform_update_core_for_zbm.zip | head -n 1)"
./bin/platform-update.sh preflight zbm --zip "$ZIP"
./bin/platform-update.sh apply-plan zbm --zip "$ZIP"
```

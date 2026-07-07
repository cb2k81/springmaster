# Platform Update Patch Generation Plan

## Zweck

Patch `000026_springmaster_platform_update_patch_generation_plan` ergänzt die Platform-Update-Grundlage um eine erste ZIP-Erzeugung.

Der Modus bleibt bewusst nicht-invasiv: Zielprojekte werden nicht direkt verändert. Seit `000029_springmaster_platform_update_core_payload_mapping` kann das Profil `core` aber erstmals echte Core-Payload-Dateien in ein generiertes Zielprojekt-Patch-ZIP übernehmen.

## Neuer Befehl

```bash
./bin/platform-update.sh generate <target> --profile core
```

Beispiel:

```bash
./bin/platform-update.sh generate zbm --profile core
```

Der Befehl erzeugt ein target-lokales Plan-Patch-ZIP unter:

```text
platform/update/generated/*.zip
```

## Dry-run

```bash
./bin/platform-update.sh generate zbm --profile core --dry-run
```

Der Dry-run gibt Zielpfad, Profil, geplanten ZIP-Pfad und Payload-Pfade aus, erzeugt aber kein ZIP.

## Inhalt des generierten Zielpatches

Das erzeugte ZIP folgt dem vorhandenen Patchformat:

```text
manifest.json
files/**
logs/CHANGELOG-<id>.md
```

Für Profile ohne Payload-Mapping bleibt der Patch plan-only und verwendet im Zielprojekt weiterhin den Scope `root`.

Für `--profile core` verwendet der generierte Patch den Scope `core` und enthält seit dem Payload-Splitting Runtime + Tests, aber keine Master-Core-Dokumentation:

```text
files/src/main/java/de/cocondo/system/**
files/src/test/java/de/cocondo/system/**
files/PROJECT_DOCS/PLATFORM_UPDATES/<id>.md
logs/CHANGELOG-<id>.md
```

Für Defaults steht seit `000079` ein eigenes Profil zur Verfügung:

```bash
./bin/platform-update.sh generate zbm --profile defaults
```

Dieses Profil überträgt Baseline-Konfigurationsdefaults wie `.env.example`, `export.config.json` und `PROJECT_DOCS/CONFIG/SPRINGMASTER_ENV_TEMPLATE.env`.

## Abgrenzung

Noch nicht enthalten:

* keine automatische Initialisierung neuer Zielprojekte
* keine Migration von projektspezifischen `pom.xml`-Anpassungen
* keine automatische Anwendung im Zielprojekt
* keine automatische produktive Freigabe bestehender Projekte
* `target-apply` bleibt zusätzlich durch `TARGET_DELIVERY_ENABLED=true` geschützt

Diese Einschränkungen sind Absicht. Patch `000026` beweist nur die technische ZIP-Erzeugung und das Format des Zielprojektpatches.

## Nächster Schritt

Ein späterer Patch kann auf diesem Format aufsetzen und für Profile wie `core` oder `tooling` echte Payload-Dateien in generierte Zielprojektpatches aufnehmen.


## Hinweis zur Patch-Historie

Bei der praktischen Anwendung wurde das `000026`-ZIP einmal erneut akzeptiert und dadurch als No-op-Patch `000027` archiviert. Dieser Eintrag bleibt historisch erhalten, ändert aber keine Dateien. Die fachliche Platform-Update-Generation bleibt der Stand von `000026`; die nächste fachliche Erweiterung setzt nach der Tooling-Härtung in `000028` mit `000029` fort.


## Stand nach 000029

Patch `000029_springmaster_platform_update_core_payload_mapping` ergänzt das erste echte Payload-Mapping. Für das Profil `core` wird der aktuelle Springmaster-Core in das generierte Zielprojekt-Patch-ZIP kopiert.

Der Generator bleibt bewusst konservativ:

* Er erzeugt nur ein ZIP unter `platform/update/generated/**`.
* Er schreibt nicht in `TARGET_PATH`.
* Er akzeptiert den Zielpatch nicht automatisch im Zielprojekt.
* Er prüft noch nicht, ob das Zielprojekt den Scope `core` bereits unterstützt.

Damit kann die Payload-Struktur inspiziert und kontrolliert in Zielprojekten getestet werden, ohne den Zielprojektzustand automatisch zu verändern.

## Hinweis zur Patchnummer nach Core-Payload-Mapping

Das Core-Payload-Mapping wurde im lokalen Projekt als Patch `000028_springmaster_platform_update_core_payload_mapping` angewendet. Nachfolgende Platform-Update-Patches bauen auf diesem Zustand auf. Der No-op-Schutz für `accept` wurde anschließend separat mit `000029_springmaster_patch_accept_noop_guard_and_state_alignment` ergänzt.


## Stand nach 000031 – Apply-Plan für Zielpatches

Patch `000031_springmaster_platform_update_target_patch_apply_plan` ergänzt den Befehl:

```bash
./bin/platform-update.sh apply-plan <target> --zip <generated-patch.zip>
```

Damit kann für ein bereits generiertes Zielprojekt-Patch-ZIP ein prüfbarer Apply-Plan erzeugt werden. Der Apply-Plan besteht aus:

```text
build/platform-update/manifests/*_apply_plan.md
build/platform-update/manifests/*_apply_plan.env
```

Der Plan bleibt konservativ. Springmaster erzeugt seit dem Review-Gate kein ausführbares Apply-Skript mehr und verändert das Zielprojekt nicht. Die tatsächliche Anwendung erfolgt ausschließlich über `platform-update target-apply` und nur bei explizit aktivierter Delivery im Ziel-Deskriptor.

## Preflight vor Apply-Plan seit 000032

Nach der ZIP-Erzeugung kann das Zielprojekt nicht-invasiv geprüft werden:

```bash
cd /opt/cocondo/springmaster
ZIP="$(ls -1t platform/update/generated/*_springmaster_platform_update_core_for_zbm.zip | head -n 1)"
./bin/platform-update.sh preflight zbm --zip "$ZIP"
```

`apply-plan` führt diese Prüfung automatisch aus und erstellt nur dann Plan- und Skriptartefakte, wenn der Ziel-Dry-run erfolgreich ist.


## Target Compatibility Plan seit 000033

Der Befund `Unbekannter Patch-Scope im manifest.json: core` bedeutet, dass das Zielprojekt noch nicht auf dem Patchsystem-Stand ist, den generierte Core-Payload-Patches erwarten.

Patch `000033_springmaster_platform_update_target_compatibility_plan` ergänzt dafür den Befehl:

```bash
./bin/platform-update.sh compatibility-plan <target> --zip <generated-patch.zip>
```

Der Befehl erzeugt einen nicht-invasiven Plan und ein Kompatibilitäts-ZIP. Erst nach bewusster Ausführung des erzeugten Skripts im Zielprojekt soll der ursprüngliche Core-Payload-Patch erneut per `preflight` geprüft werden.



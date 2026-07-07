# Platform Update Target Scope Preflight

## Zweck

Patch `000032_springmaster_platform_update_target_scope_preflight` ergänzt den Platform-Update-Workflow um eine nicht-invasive Zielprojektprüfung.

Vor einem Apply-Plan muss geprüft werden, ob das Zielprojekt den im generierten Patch manifestierten Scope unterstützt und ob sein lokales Patchsystem den Patch per Dry-run akzeptiert.

## Neuer Befehl

```bash
cd /opt/cocondo/springmaster
ZIP="$(ls -1t platform/update/generated/*_springmaster_platform_update_core_for_zbm.zip | head -n 1)"
./bin/platform-update.sh preflight zbm --zip "$ZIP"
```

## Verhalten

Der Befehl liest aus dem generierten ZIP:

```text
manifest.id
manifest.name
manifest.scope
```

Danach wird im Zielprojekt ausgeführt:

```bash
cd <TARGET_PATH>
./bin/patch.sh apply --dry-run <generated-patch.zip>
```

Die Ausgabe wird in Springmaster unter `platform/update/manifests/*_preflight.log` gespeichert. Das Zielprojekt wird nicht verändert.

## Integration in `apply-plan`

`apply-plan` führt die Preflight-Prüfung automatisch aus.

Bei Erfolg werden Plan- und Skriptdatei erzeugt. Bei Fehlern wird kein Apply-Plan erzeugt. Typische Fehler sind:

* Zielpfad existiert nicht.
* `bin/patch.sh` fehlt im Zielprojekt.
* `bin/patch.sh` ist nicht ausführbar.
* Das Zielprojekt unterstützt den Patch-Scope aus `manifest.json` noch nicht.
* Der Ziel-Dry-run erkennt Konflikte.

## Bedeutung für Zielprojekte

Der Preflight stellt sicher, dass ein generierter Zielpatch nicht erst beim manuellen Anwenden im Zielprojekt scheitert. Insbesondere für `core`-Payload-Patches wird sichtbar, ob das Zielprojekt bereits den Scope `core` und projektspezifische Scope-Erweiterungen aus `.env` unterstützt.



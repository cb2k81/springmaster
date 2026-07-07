# 000024 - Springmaster Patch Accept Export Hygiene

## Typ

Tooling-Patch

## Ziel

Reduziert unnötige Export-Duplikate im Patch-Abnahme-Workflow.

## Änderungen

* `bin/tooling-selfcheck.sh` unterstützt `--export` und `--no-export`.
* `bin/patch.py` ruft den Tooling-Selfcheck innerhalb von `accept`/`verify` mit `--no-export` auf.
* Der zentrale Export-Schritt des Accept-/Verify-Workflows bleibt erhalten und erzeugt den Full-ZIP-Export weiterhin standardmäßig.
* Die Tooling-Version wird auf `0.3.2` erhöht.
* Dokumentation und Umsetzungsplan werden auf die Export-Hygiene seit `000024` ausgerichtet.

## Nicht enthalten

* Kein Java-Code.
* Keine Maven-/Build-Konfigurationsänderung.
* Keine Änderung an Core-, Demo-, Template- oder Platform-Update-Version.
* Keine Target-Update-Mechanik.

## Validierung

Empfohlen:

```bash
./bin/patch.sh accept /home/cb/Downloads/000024_springmaster_patch_accept_export_hygiene.zip
```

Der Patch ist ein Tooling-Patch. `mvn test` ist nicht erforderlich, weil weder Java-Code noch Build-Konfiguration betroffen sind.

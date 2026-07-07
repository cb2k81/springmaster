# 000025 - springmaster platform update foundation

## Scope

root

## Änderungen

* `bin/platform-update.sh` vom Placeholder zu einem konservativen Foundation-Tool ausgebaut.
* Zielprojekt-Registry kann gelistet, angezeigt und validiert werden.
* Nicht-invasive Update-Pläne können unter `platform/update/manifests/**` erzeugt werden.
* `platform-update`-Scope in Patchsystem und Exportprofil für atomare Versionsänderungen vorbereitet.
* Platform-Update-Version auf `0.1.0` und Gesamtversion auf `0.7.0-foundation` erhöht.

## Abgrenzung

* keine Zielprojekt-Patch-ZIP-Erzeugung
* kein Schreiben in Zielprojektpfade
* kein automatisches Anwenden im Zielprojekt
* kein Java-Code und kein Maven-Test erforderlich

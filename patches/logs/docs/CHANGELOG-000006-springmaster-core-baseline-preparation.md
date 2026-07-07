# Changelog – 000006 springmaster core baseline preparation

## Scope

`docs`

## Änderungen

* IDM-System-Core aus dem Referenzexport klassifiziert.
* Maschinenlesbares Core-Kandidatenmanifest ergänzt.
* Migrationsregeln für den Platform Core dokumentiert.
* Core-README aktualisiert.
* Umsetzungsplan auf den nächsten Basic-Core-Slice fortgeschrieben.

## Nicht enthalten

* keine Java-Code-Übernahme
* keine Maven-Dependency-Änderung
* keine Demo-Domäne
* keine Security-/JPA-/JWT-Aktivierung

## Validierung

Vorgesehen:

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
./bin/patch.sh show latest
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
```

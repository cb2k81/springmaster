# CHANGELOG 000005 – springmaster project-new tool foundation

## Zweck

Dieser Patch operationalisiert die erste deterministische Projektanlage aus dem versionierten Project Skeleton.

## Änderungen

* ergänzt `bin/project-new.sh`
* ergänzt `PROJECT_DOCS/TOOLING/PROJECT_NEW.md`
* aktualisiert das Project-Skeleton-Manifest und dessen README
* aktualisiert zentrale Template-Dateien für `.env.example`, `.gitignore`, `README.md` und `export.config.json`
* aktualisiert `docs/Masterkonzept.md`
* aktualisiert `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md`

## Abgrenzung

* keine Core-Migration
* keine Demo-Domäne
* keine Zielprojekt-Update-Erzeugung
* kein Überschreiben bestehender Zielprojekte

## Verifikation

```bash
./bin/project-new.sh --help
rm -rf /tmp/springmaster-sample
./bin/project-new.sh create --dry-run --name sample --path /tmp/springmaster-sample
./bin/project-new.sh create --name sample --path /tmp/springmaster-sample
(cd /tmp/springmaster-sample && ./bin/patch.sh list && ./bin/export.sh full --zip && ./bin/dbtool.sh status)
```

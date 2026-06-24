# Project-New Tool

## Zweck

`bin/project-new.sh` erzeugt neue Cocondo Java-Backend-Projekte aus dem versionierten Springmaster Project Skeleton.

Das Tool ist konservativ ausgelegt: Ein bestehendes nicht-leeres Zielverzeichnis wird nicht überschrieben.

## Standardaufrufe

```bash
./bin/project-new.sh --help
./bin/project-new.sh create --dry-run --name sample --path /tmp/springmaster-sample
./bin/project-new.sh create --name sample --path /tmp/springmaster-sample
```

## Parameter

| Parameter | Pflicht | Bedeutung |
|---|---:|---|
| `--name` | ja | Projektname, z. B. `sample` |
| `--path` | ja | Zielpfad, muss leer oder noch nicht vorhanden sein |
| `--artifact-id` | nein | Maven `artifactId`, Default: `--name` |
| `--group-id` | nein | Maven `groupId`, Default: `de.cocondo.<name ohne Bindestriche>` |
| `--base-package` | nein | Java-Basispaket, Default: `groupId` |
| `--application-class` | nein | Spring-Boot-Application-Klasse, Default: `<NamePascalCase>Application` |
| `--port` | nein | HTTP-Port, Default: `8080` |
| `--db-name` | nein | Datenbankname, Default: Projektname mit `_` statt `-` |
| `--stage-db-name` | nein | Stage-/Build-Datenbankname, Default: `<db-name>_build` |

## Erzeugte Bestandteile

Das Zielprojekt enthält:

* Maven-/Spring-Boot-Basis
* minimale Application und `/api/platform/info`
* `.env.example`, aber keine `.env`
* `bin/patch.sh` / `bin/patch.py`
* `bin/export.sh`
* `bin/dbtool.sh`
* `bin/build.sh`
* `bin/tooling-selfcheck.sh`
* `platform/versions/platform.env`
* Bootstrap-Nachweis unter `PROJECT_DOCS/BOOTSTRAP/`
* registrierten Bootstrap-Eintrag unter `patches/archives/000001_project_new_bootstrap/`

## Verifikation eines erzeugten Projekts

```bash
cd /tmp/springmaster-sample
./bin/patch.sh list
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
./bin/dbtool.sh status
mvn test
```

## Abgrenzung

Das Tool erzeugt noch keine fachliche Demo-Domäne und überträgt keinen Platform Core. Diese Bestandteile folgen in separaten, validierten Patches.

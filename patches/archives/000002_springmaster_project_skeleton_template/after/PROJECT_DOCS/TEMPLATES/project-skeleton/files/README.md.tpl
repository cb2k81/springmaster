# __PROJECT_NAME__

`__PROJECT_NAME__` ist ein Cocondo Java-Backend-Projekt, erzeugt aus dem Springmaster Project Skeleton.

## Basisdaten

```text
GROUP_ID=__GROUP_ID__
ARTIFACT_ID=__ARTIFACT_ID__
BASE_PACKAGE=__BASE_PACKAGE__
HTTP_PORT=__HTTP_PORT__
DB_NAME=__DB_NAME__
STAGE_DB_NAME=__STAGE_DB_NAME__
PLATFORM_VERSION=__PLATFORM_VERSION__
CORE_VERSION=__CORE_VERSION__
TOOLING_VERSION=__TOOLING_VERSION__
```

## Standardprüfung

```bash
./bin/patch.sh list
./bin/export.sh full --zip
./bin/dbtool.sh status
mvn test
```

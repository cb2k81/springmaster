# Build Tool

## Zweck

`bin/build.sh` führt einen lokalen, reproduzierbaren Build aus und erzeugt ein Runtime-ZIP unter `target/dist/`.

## Standardkommando

```bash
./bin/build.sh
```

## Ablauf

1. Umgebung über `bin/init.env.sh` laden.
2. `mvn clean verify` ausführen.
3. Spring-Boot-JAR unter `target/` ermitteln.
4. Runtime-ZIP unter `target/dist/${APP_NAME}.zip` erzeugen.
5. Build-Zusammenfassung nach `tmp/build.summary` schreiben.

## Lokale Ausrichtung

Remote-Deployment bleibt in dieser Tooling-Baseline deaktiviert. Falls `APP_BUILD_REMOTE_DEPLOY_ENABLED=true` gesetzt ist, wird lediglich eine Warnung ausgegeben.

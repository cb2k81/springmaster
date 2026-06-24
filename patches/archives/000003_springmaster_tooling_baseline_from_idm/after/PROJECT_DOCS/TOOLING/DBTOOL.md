# DBTool

## Zweck

`bin/dbtool.sh` bündelt die Datenbank- und Liquibase-Kommandos für lokale Entwicklung und Build-/Stage-Validierung.

## Nicht destruktive Kommandos

```bash
./bin/dbtool.sh env
./bin/dbtool.sh status
./bin/dbtool.sh changelogs
./bin/dbtool.sh validate-stage
./bin/dbtool.sh update-stage
```

`status` prüft Konfiguration und Changelog-Datei, öffnet aber keine Datenbankverbindung.

## Destruktive Kommandos

```bash
./bin/dbtool.sh rebuild-dev
./bin/dbtool.sh rebuild-stage
```

Diese Kommandos sind gesperrt, solange nicht explizit gesetzt ist:

```bash
APP_DBTOOL_ALLOW_DESTRUCTIVE=true
```

MariaDB-Admin-Zugang wird über `APP_DB_ADMIN_USER` und `APP_DB_ADMIN_PASS` gelesen.

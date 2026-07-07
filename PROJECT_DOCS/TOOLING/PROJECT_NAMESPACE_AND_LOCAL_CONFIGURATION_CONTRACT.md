# Project Namespace and Local Configuration Contract

## Zweck

Springmaster unterscheidet strikt zwischen dem Master-/Self-Scope und den
projektlokalen Zielprojekt-Scopes. Gemeinsames Tooling darf in Zielprojekten
keine technischen Projektparameter überschreiben oder hart kodieren.

## Namespace-Regel

| Rolle | Standard |
|---|---|
| Springmaster-App | `de.cocondo.platform.app` |
| Springmaster-Demo | `de.cocondo.platform.demo` |
| Gemeinsamer technischer Core | `de.cocondo.system` |
| Zielprojekt-Fach-/App-Namespace | `APP_BASE_PACKAGE`, z. B. `de.cocondo.zbm` |

Der Core bleibt in Springmaster und Zielprojekten unter `de.cocondo.system`.
Projektfachlichkeit liegt nicht im Springmaster-Core und nicht unter
`de.cocondo.platform`, sondern unter dem projektlokalen `APP_BASE_PACKAGE`.

## Lokale Konfiguration

Diese Werte sind projektlokal und werden aus `.env.example` und optional `.env`
gelesen:

```env
APP_NAME=<technical-project-name>
APP_EXPORT_PROJECT_KEY=<technical-project-name>
APP_BASE_PACKAGE=<target-base-package>
APP_CORE_PACKAGE=de.cocondo.system
APP_DEV_DB_NAME=<target-db-name>
APP_STAGE_DB_NAME=<target-stage-db-name>
PATCH_LOCAL_SCOPES=<target-local-scopes>
```

Ladereihenfolge:

1. `.env.example` liefert generierte lokale Defaults.
2. `.env` überschreibt diese Defaults für die konkrete Runtime.

Damit funktionieren neue Projekte ohne `.env`, bleiben aber lokal übersteuerbar.

## Export-Regel

`bin/export.sh` bestimmt den Export-Key in dieser Reihenfolge:

1. `APP_EXPORT_PROJECT_KEY`
2. `APP_NAME`
3. `export.config.json:projectKey`
4. Repository-Verzeichnisname

Dadurch bleibt der ZIP-Name projektlokal korrekt, selbst wenn ein altes oder
versehentlich übertragenes `export.config.json` noch `springmaster` enthält.

## Patch-Scope-Regel

`bin/patch.py` liest Scope-Parameter ebenfalls aus `.env.example` und danach
`.env`. Tool-Updates dürfen deshalb nicht voraussetzen, dass Zielprojekte eine
`.env` besitzen.

Die Standardscope-Pfade für `app` und `demo` werden aus `APP_BASE_PACKAGE`
abgeleitet. Der Core-Scope wird aus `APP_CORE_PACKAGE` abgeleitet und bleibt
standardmäßig `de.cocondo.system`.

Neue Zielprojekte erhalten zusätzlich projektlokale Scopes:

```env
PATCH_LOCAL_SCOPES="domain;<project-key>"
PATCH_SCOPE_DOMAIN_PATHS="src/main/java/<base-package>/**;src/test/java/<base-package>/**;src/main/resources/db/**;PROJECT_DOCS/CONCEPT/**;PROJECT_DOCS/DOMAIN/**"
PATCH_SCOPE_<PROJECT_KEY>_PATHS="src/main/java/<base-package>/**;src/test/java/<base-package>/**;src/main/resources/db/**;PROJECT_DOCS/CONCEPT/**;PROJECT_DOCS/DOMAIN/**"
```

Zusätzlich erkennt `patch.py` den impliziten Scope aus
`APP_PATCH_PROJECT_SCOPE`, `APP_EXPORT_PROJECT_KEY` oder `APP_NAME`. Wenn dafür
keine expliziten Pfade gepflegt sind, verwendet das Tooling konservative Pfade
unter `APP_BASE_PACKAGE`, `src/main/resources/db/**` und fachlichen
`PROJECT_DOCS/**`-Bereichen.

## Tool-Update-Regel

Das Platform-Update-Profil `tooling` liefert nur gemeinsames Tooling aus:

```text
bin/patch.py
bin/patch.sh
bin/export.sh
bin/init.env.sh
bin/tooling-selfcheck.sh
bin/lib/**
PROJECT_DOCS/TOOLING/**
```

Es liefert ausdrücklich nicht:

```text
.env.example
export.config.json
PROJECT_DOCS/CONFIG/**
```

Diese Dateien gehören zum expliziten Profil `defaults` und sind reviewpflichtig,
weil sie Zielprojektparameter wie Projektname, Datenbanknamen, Export-Key und
Patch-Scopes enthalten.

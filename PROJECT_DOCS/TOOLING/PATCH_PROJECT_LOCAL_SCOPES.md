# Patch Project-Local Scopes

## Zweck

Patch `000030_springmaster_patch_project_local_scope_env` erlaubt projektlokale Erweiterungen des Patch-Scope-Modells über die jeweilige `.env.example` und optional `.env`.

Springmaster definiert weiterhin nur die gemeinsamen Standardscope-Regeln. Fachprojektspezifische Zusatzbereiche dürfen nicht zentral in `bin/patch.py` hart kodiert werden. Sie gehören in die `.env.example` des jeweiligen Projekts und können lokal über `.env` überschrieben werden.

## Erweiterung bestehender Scopes

Ein vorhandener Standardscope kann projektspezifisch ergänzt werden. Beispiel:

```env
PATCH_SCOPE_DEMO_EXTRA_PATHS=src/main/java/com/example/demo/**;src/test/java/com/example/demo/**
```

Die zusätzlichen Pfade werden zu den eingebauten Scope-Pfaden addiert. Die eingebauten Regeln werden nicht ersetzt.

## Zusätzliche lokale Scopes

Ein Projekt kann eigene Scopes registrieren:

```env
PATCH_LOCAL_SCOPES=reporting
PATCH_SCOPE_REPORTING_PATHS=src/main/java/com/example/reporting/**;src/test/java/com/example/reporting/**
PATCH_SCOPE_REPORTING_LOG_DIR=reporting
```

`PATCH_SCOPE_<NAME>_LOG_DIR` ist optional. Ohne Angabe wird der Scope-Name als Log-Verzeichnis verwendet. Das Patchsystem ergänzt automatisch:

```text
patches/logs/<log-dir>/**
```

## Namenskonvention

Für Variablennamen wird der Scope normalisiert:

```text
reporting          -> PATCH_SCOPE_REPORTING_PATHS
customer-ui        -> PATCH_SCOPE_CUSTOMER_UI_PATHS
app.customer       -> PATCH_SCOPE_APP_CUSTOMER_PATHS
```

Scope-Namen dürfen Buchstaben, Ziffern, Punkt, Unterstrich und Bindestrich enthalten.

## Pfadliste

Pfade werden in `.env` mit Semikolon getrennt:

```env
PATCH_SCOPE_REPORTING_PATHS=src/main/java/com/example/reporting/**;src/test/java/com/example/reporting/**;PROJECT_DOCS/REPORTING/**
```

Absolute Pfade, `~` und `..` bleiben verboten.

## Grenzen

Diese Funktion ist für projektlokale Scope-/Pfaderweiterungen gedacht. Sie ist nicht dafür gedacht, die gemeinsamen Springmaster-Standards zu überschreiben. Gemeinsame Scopes wie `core`, `demo`, `platform-update` bleiben im Tooling definiert und werden nur bei Bedarf projektlokal ergänzt.

## Validierung

`accept` und `verify` verwenden dieselben Scope-Regeln wie `apply`. Dadurch gelten lokale `.env`-Erweiterungen deterministisch in Dry-run, Apply, Accept und Verify.



## Contract-Hinweis nach Namespace-Härtung

Das Patchsystem lädt `.env.example` als projektlokale Defaults und danach `.env` als Override. Neue Zielprojekte erhalten einen generischen `domain`-Scope und einen technischen Scope mit dem Projekt-Key, z. B. `zbm`. Siehe `PROJECT_DOCS/TOOLING/PROJECT_NAMESPACE_AND_LOCAL_CONFIGURATION_CONTRACT.md`.

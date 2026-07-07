# Platform-Update Payload Profiles

## Zweck

`000037_springmaster_platform_update_payload_profiles` trennt die bisher zu breite `core`-Übertragung in explizite Payload-Profile.

Ziel ist, dass ein technischer Core-Transfer nicht automatisch die vollständige Springmaster-Masterdokumentation in Zielprojekte kopiert.

## Profile

| Profil | Manifest-Scope | Inhalt |
|---|---|---|
| `core` | `core` | Kompatibles Standardprofil: Runtime + Tests, aber keine Master-Core-Dokumentation |
| `core-runtime` | `core` | `src/main/java/de/cocondo/system/**` |
| `core-tests` | `core` | `src/test/java/de/cocondo/system/**` |
| `core-docs` | `docs` | `PROJECT_DOCS/CORE/**` nur bei expliziter Anforderung |
| `platform-update-doc` | `docs` | Nur generierte Zielprojekt-Update-Dokumentation unter `PROJECT_DOCS/PLATFORM_UPDATES/**` |
| `tooling` | `tooling` | Gemeinsames Shell-/Patch-/Export-Tooling und Tooling-Dokumentation |
| `defaults` | `root` | Baseline-Konfigurationsdefaults: `.env.example`, `export.config.json`, `PROJECT_DOCS/CONFIG/SPRINGMASTER_ENV_TEMPLATE.env` |
| `demo` | `demo` | Reserviert für spätere Demo-Payload-Regeln |
| `platform-update` | `platform-update` | Reserviert für spätere Platform-Update-Payload-Regeln |

## ZBM-Standard seit 000079

Für das erste geplante Zielprojekt `zbm` wird zwischen Initialisierung und Update unterschieden.

Nach erfolgreicher Initialisierung ist der technische Update-Standard:

```text
core-runtime + core-tests + tooling + defaults + platform-update-doc
```

Das Kompatibilitätsprofil `core` bildet weiterhin Runtime + Tests als kombinierten Payload ab. Die Zielprojekt-Update-Dokumentation wird weiterhin bei jedem generierten Patch automatisch erzeugt. `tooling` und `defaults` werden bewusst getrennt, damit Patch-/Export-Tooling und Basis-Konfiguration gezielt aktualisiert werden können.

Nicht automatisch übertragen wird:

```text
PROJECT_DOCS/CORE/**
```

Diese Masterdokumentation bleibt in Springmaster und wird nur über `--profile core-docs` explizit übertragen.

## Sicherheitsregel

Payload-Profile steuern nur, welche Dateien in ein generiertes Zielpatch-ZIP geschrieben werden. Sie verändern kein Zielprojekt. Zielprojektänderungen bleiben weiterhin ausschließlich an den Review-Gate und den expliziten Befehl `platform-update target-apply` gebunden.

## Beispiele

```bash
./bin/platform-update.sh generate zbm --profile core-runtime
./bin/platform-update.sh generate zbm --profile core-tests
./bin/platform-update.sh generate zbm --profile core
./bin/platform-update.sh generate zbm --profile core-docs
./bin/platform-update.sh generate zbm --profile platform-update-doc
./bin/platform-update.sh generate zbm --profile tooling
./bin/platform-update.sh generate zbm --profile defaults
```

## Abgrenzung

Die Profile lösen noch keine fachliche Migration alter Zielprojektpakete aus. Bestehende Projekte wie IDM und Personnel werden durch dieses Profil-Splitting nicht bereinigt und nicht aktualisiert. Sie sind bewusst als nicht belieferbare Referenzen zurückgestellt. Eine spätere Migration und Bereinigung alter Zielprojekt-Core-Reste bleibt ein eigener, explizit freizugebender Schritt.





## Scope-kompatible Review-Dokumente seit 000081

Generierte Zielprojekt-Patches legen ihre Review-Dokumente nun scope-kompatibel ab.

Für Core-Profile bedeutet das:

```text
PROJECT_DOCS/CORE/PLATFORM_UPDATES/<generated-update-id>.md
```

Damit kann ein generiertes Core-Patch-ZIP mit Manifest-Scope `core` durch das lokale Zielprojekt-Patchsystem validiert werden, ohne eine Scope-Verletzung durch allgemeine Plattform-Update-Dokumentation zu erzeugen.

Für `core` und `core-runtime` wird zusätzlich eine target-lokale `pom.xml` synthetisiert. Diese ergänzt die minimalen Core-Abhängigkeiten im Zielprojekt, ohne die Springmaster-Master-`pom.xml` zu übertragen.

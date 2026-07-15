# Platform Update Tool

## Zweck

`bin/platform-update.sh` ist die Grundlage für spätere Updates von Zielprojekten aus dem Springmaster-Masterprojekt heraus.

Patch `000025_springmaster_platform_update_foundation` führt bewusst nur einen konservativen Planungsmodus ein. Zielprojekte werden nicht verändert.

## Kommandos

```bash
./bin/platform-update.sh list
./bin/platform-update.sh show zbm
./bin/platform-update.sh validate zbm
./bin/platform-update.sh validate all
./bin/platform-update.sh plan zbm --profile core
./bin/platform-update.sh generate zbm --profile core --dry-run
./bin/platform-update.sh generate zbm --profile core
./bin/platform-update.sh preflight zbm --zip "$ZIP"
./bin/platform-update.sh apply-plan zbm --zip "$ZIP"
./bin/platform-update.sh target-apply zbm --zip "$ZIP"
```

## Target lifecycle seit 000079

Seit `000079_springmaster_zbm_target_registry_and_lifecycle_alignment` unterscheidet Springmaster explizit zwischen Initialisierung und Update:

| Modus | Zweck | Beispiel |
|---|---|---|
| Initialisierung | Neues Java-Backend-Projekt aus dem Master-Skeleton erzeugen | `zbm` per `project-new` anlegen |
| Update | Spätere Master-Payloads in ein bereits akzeptiertes Zielprojekt übertragen | Core, Tools, Defaults, optionale Doku |

`zbm` ist das erste geplante Springmaster-belieferte Zielprojekt. Laufende Projekte wie IDM und Personnel sind bewusst zurückgestellt und in der Target Registry als nicht belieferbar markiert.

Die reale Zielprojektänderung über `target-apply` ist zusätzlich durch `TARGET_DELIVERY_ENABLED=true` abgesichert. Ohne diese explizite Freigabe bricht `target-apply` ab, auch wenn ein Ziel-Deskriptor vorhanden ist.


## List

`list` zeigt alle Zielprojekt-Deskriptoren aus:

```text
platform/update/targets/*.env
```

## Show

`show <target>` gibt einen Zielprojekt-Deskriptor aus. Unterstützt sind nur sichere Target-Namen mit Buchstaben, Zahlen, Punkt, Unterstrich und Bindestrich.

## Validate

`validate <target|all>` prüft die Deskriptorstruktur:

* `TARGET_NAME` ist gesetzt und syntaktisch sicher.
* `TARGET_STATUS` ist gesetzt.
* `TARGET_PATH` ist absolut.
* Falls der lokale Zielpfad existiert, wird ein lokales `bin/patch.sh` erwartet.

Unverifizierte oder lokal nicht vorhandene Zielpfade werden als Warnung ausgegeben, weil Zielprojekte nicht immer auf derselben Maschine gemountet sein müssen.

## Plan

`plan <target>` erzeugt eine Plan-Datei im Build-Workspace unter:

```text
build/platform-update/manifests/*_plan.env
```

Der Plan enthält Zielprojekt, Profil und aktuelle Master-Versionen. Er ist ein reines Planungsartefakt und verändert kein Zielprojekt.

Unterstützte Profile seit `000037`:

```text
core
core-runtime
core-tests
core-docs
platform-update-doc
tooling
demo
platform-update
```

`core` ist ein kompatibles Standardprofil für Runtime + Tests. Die vollständige Master-Core-Dokumentation wird nicht mehr automatisch mit `core` übertragen, sondern nur explizit mit `core-docs`.

## Generate

`generate <target>` erzeugt ein target-lokales Plan-Patch-ZIP im überschreibbaren Build-Workspace unter:

```text
build/platform-update/generated/*.zip
```

Bei Standardausgabe wird `build/platform-update/**` vor dem Generierungslauf zurückgesetzt. Benutzerdefinierte Ausgaben per `--output` werden nicht automatisch gelöscht.

Seit `000037_springmaster_platform_update_payload_profiles` sind technische Core-Payloads und Masterdokumentation getrennt:

```text
core-runtime        src/main/java/de/cocondo/system/**
core-tests          src/test/java/de/cocondo/system/**
core-docs           PROJECT_DOCS/CORE/**
platform-update-doc generierte PROJECT_DOCS/PLATFORM_UPDATES/<update-id>.md
tooling             gemeinsames Shell-/Patch-/Export-Tooling
defaults            .env.example, export.config.json, PROJECT_DOCS/CONFIG/SPRINGMASTER_ENV_TEMPLATE.env
```

Das Profil `core` bleibt als Standard-Kombination für `core-runtime + core-tests` erhalten. Es enthält bewusst nicht mehr `PROJECT_DOCS/CORE/**`. Zielprojekte werden weiterhin nicht direkt verändert; reale Anwendung erfolgt nur nach Review mit `target-apply`.

Für eine Vorschau ohne ZIP-Erzeugung:

```bash
./bin/platform-update.sh generate zbm --profile core --dry-run
```

## Apply-Plan

`apply-plan <target> --zip <generated-patch.zip>` erzeugt einen expliziten Review-Gate-Plan unter:

```text
build/platform-update/manifests/*_apply_plan.md
build/platform-update/manifests/*_apply_plan.env
```

Der Befehl ist weiterhin nicht-invasiv:

* Springmaster schreibt nur Review-Artefakte unter `build/platform-update/manifests/**`.
* Das Zielprojekt wird nicht verändert.
* Es wird bewusst kein ausführbares Zieländerungs-Skript erzeugt.
* Die reale Zieländerung ist ausschließlich über `target-apply` vorgesehen.

Beispiel:

```bash
./bin/platform-update.sh preflight zbm --zip "$ZIP"
./bin/platform-update.sh apply-plan zbm --zip "$ZIP"
./bin/platform-update.sh target-apply zbm --zip "$ZIP"
```

`target-apply` kopiert den generierten Zielpatch später nach `tmp/platform-updates/**` im Zielprojekt, ruft dort das lokale Patchsystem auf und schreibt die vollständige Ausgabe nach `build/platform-update/logs/**`. Im Terminal erscheinen nur Status, Logpfad und Exportpfad.

## Abgrenzung

Noch nicht enthalten:

* keine automatische Initialisierung bestehender Zielprojekte
* kein automatisches Anwenden im Zielprojekt
* `apply-plan` erzeugt nur Review-Artefakte, keine ausführbaren Zieländerungs-Skripte
* `target-apply` ist blockiert, solange `TARGET_DELIVERY_ENABLED` nicht explizit `true` ist
* keine Transformationsregeln für projektspezifische `pom.xml`-Änderungen
* keine automatische produktive Freigabe für IDM, Personnel oder andere laufende Projekte

Diese Einschränkung ist bewusst gewählt, damit die Target-Update-Mechanik zunächst sicher über Registry, Validierung, Planartefakte und generierte Plan-Patch-ZIPs eingeführt wird.

## Target-Scope-Preflight seit 000032

`platform-update preflight` prüft ein generiertes Zielpatch-ZIP gegen das lokale Patchsystem des Zielprojekts, bevor ein Apply-Plan erstellt wird.

Der Befehl führt im Zielprojekt nur den Patch-Dry-run aus:

```bash
cd /opt/cocondo/springmaster
ZIP="$(ls -1t build/platform-update/generated/*_springmaster_platform_update_core_for_zbm.zip | head -n 1)"
./bin/platform-update.sh preflight zbm --zip "$ZIP"
```

`apply-plan` führt diese Preflight-Prüfung automatisch aus und bricht ab, wenn das Zielprojekt den benötigten Patch-Scope oder das lokale Patchsystem noch nicht unterstützt. Zielprojekte werden dabei nicht verändert.


## Target Compatibility Plan seit 000033

Wenn `preflight` meldet, dass das Zielprojekt einen generierten Patch-Scope noch nicht kennt, darf der Nutzpatch nicht angewendet werden. Stattdessen wird ein Compatibility-Plan erzeugt:

```bash
cd /opt/cocondo/springmaster
ZIP="$(ls -1t /opt/cocondo/springmaster/build/platform-update/generated/*_springmaster_platform_update_core_for_zbm.zip | head -n 1)"
./bin/platform-update.sh compatibility-plan zbm --zip "$ZIP"
```

Der Befehl erzeugt nicht-invasiv:

```text
build/platform-update/generated/*_springmaster_platform_update_compatibility_for_<target>.zip
build/platform-update/manifests/*_compatibility_plan.md
build/platform-update/manifests/*_compatibility_plan.env
```

Das erzeugte Kompatibilitäts-ZIP aktualisiert im Zielprojekt nur das lokale Patchsystem (`bin/patch.py`, `bin/patch.sh`). Die reale Anwendung erfolgt seit `000036` erst nach Review über `target-apply`. Projektspezifische zusätzliche Scopes und Pfade bleiben weiterhin Aufgabe der Zielprojekt-`.env`; sie werden nicht zentral in Springmaster hart kodiert.

## Export-Hygiene seit 000034

Die unter `platform/update/generated/**` und `platform/update/manifests/**` entstehenden Dateien sind Operations-/Review-Artefakte. Sie bleiben mit den bestehenden Befehlen kompatibel, werden aber aus regulären Full-ZIP-Baselines ausgeschlossen.

Damit gilt:

```text
Springmaster-Quellbaseline != Platform-Update-Arbeitsbereich
```

Ein späterer Patch führt dafür einen dedizierten, überschreibbaren Workspace unter `build/platform-update/**` ein. Dieser Workspace ist ebenfalls aus regulären Exports ausgeschlossen.



## Build-Workspace seit 000035

Seit `000035_springmaster_platform_update_build_workspace` schreibt `platform-update.sh` generierte Operationsartefakte standardmäßig nach:

```text
build/platform-update/**
```

Der Bereich ist überschreibbar und aus regulären Full-ZIP-Baselines ausgeschlossen. `platform/update/**` bleibt damit der dauerhafte Definitions- und Dokumentationsbereich; Zielpatch-ZIPs, Preflight-Logs, Apply-Pläne und Compatibility-Pläne sind Build-/Review-Artefakte.

Der aktuelle Workspace kann angezeigt werden mit:

```bash
./bin/platform-update.sh workspace
```




## Review-Gate seit 000036

Seit `000036_springmaster_platform_update_review_gate` ist die Zielprojekt-Anwendung hart vom Review-Plan getrennt:

```text
generate -> preflight -> apply-plan -> review -> target-apply
```

`apply-plan` erzeugt nur noch Review-Artefakte (`*.md`, `*.env`). Der Befehl erzeugt kein ausführbares Apply-Skript mehr und verändert Zielprojekte nicht.

Der einzige Platform-Update-Befehl, der ein Zielprojekt verändern darf, ist:

```bash
./bin/platform-update.sh target-apply <target> --zip <generated-patch.zip>
```

`target-apply` führt erneut einen Preflight aus, kopiert den Patch in das Zielprojekt, ruft dort `./bin/patch.sh accept` auf und schreibt die vollständige Ausgabe nach `build/platform-update/logs/**`. Terminalausgaben bleiben ausgabearm: `OK` oder `FAILED`, Logpfad und Exportpfad.


## Payload-Profile seit 000037

`generate --profile <profil>` verwendet nun getrennte Payload-Profile. Damit kann Springmaster technische Runtime-Dateien, Tests, Masterdokumentation und Tooling getrennt in Zielpatch-ZIPs aufnehmen.

Der wichtigste Schnitt ist der Core-Schnitt:

```text
core          = core-runtime + core-tests
core-runtime  = src/main/java/de/cocondo/system/**
core-tests    = src/test/java/de/cocondo/system/**
core-docs     = PROJECT_DOCS/CORE/**
```

Für `zbm` ist nach erfolgreicher Initialisierung der technische Update-Standard `core` beziehungsweise explizit `core-runtime + core-tests`; dazu kommen bei Bedarf `tooling` und `defaults`. Die vollständige Springmaster-Core-Dokumentation bleibt im Masterprojekt und wird nur über `core-docs` bewusst übertragen.

Details: `PROJECT_DOCS/TOOLING/PLATFORM_UPDATE_PAYLOAD_PROFILES.md`.




## First target alignment since 000079

The first planned target project is `zbm` at `/opt/cocondo/zbm` with intended base package `de.cocondo.zbm`. It starts as `INITIALIZATION_CANDIDATE`: planning and descriptor validation are allowed, but update delivery is disabled until the generated target has passed its own acceptance baseline.

Existing projects are intentionally kept out of the delivery path:

* `idm`: `DEFERRED_EXISTING_PROJECT_NO_DELIVERY`
* `personnel`: `DEFERRED_EXISTING_PROJECT_NO_DELIVERY`
* `contacts`: `TO_VERIFY_NO_DELIVERY`
* `orders`: `TO_VERIFY_NO_DELIVERY`

This keeps the next Springmaster work focused on safe generation instead of retrofitting running applications.



## Core-Source-Copy-Acceptance seit 000081

Für den ersten realen Zielprojekt-Test `zbm` wird `platform-update generate --profile core` als Core-Source-Copy-Acceptance verwendet.

Wichtige Regeln:

* Das generierte Patch-ZIP hat Manifest-Scope `core`.
* Der Review-Plan wird unter `PROJECT_DOCS/CORE/PLATFORM_UPDATES/**` abgelegt, damit er durch den Core-Scope gedeckt ist.
* `src/main/java/de/cocondo/system/**` und `src/test/java/de/cocondo/system/**` werden übertragen.
* `de.cocondo.platform.*` und Demo-Code werden nicht übertragen.
* Für `core` und `core-runtime` wird eine target-lokale `pom.xml` mit den minimal notwendigen Core-Compile-Abhängigkeiten ohne DataSource-Autokonfiguration synthetisiert.
* `TARGET_DELIVERY_ENABLED=false` bleibt für `zbm` bestehen; der Acceptance-Test verwendet nach Review das lokale Patchsystem von `zbm` und nicht `target-apply`.

Beispiel:

```bash
cd /opt/cocondo/springmaster
./bin/platform-update.sh generate zbm --profile core
ZIP="$(ls -1t build/platform-update/generated/*_springmaster_platform_update_core_for_zbm.zip | head -n 1)"
./bin/platform-update.sh preflight zbm --zip "$ZIP"
cd /opt/cocondo/zbm
./bin/patch.sh apply --dry-run "$ZIP"
./bin/patch.sh apply "$ZIP"
mvn test
./bin/export.sh full --zip
```




## Local Configuration Protection

Das Profil `tooling` darf Zielprojektparameter nicht überschreiben. `.env.example`, `export.config.json` und `PROJECT_DOCS/CONFIG/**` gehören nicht zum regulären Tooling-Payload, sondern ausschließlich zum expliziten Profil `defaults`. Das gemeinsame Tooling liest Projektname, Export-Key, Datenbanknamen, Namespace und Patch-Scopes aus der Zielprojektkonfiguration.

## Delivery-Contract Closure seit 000129

Seit `000129_springmaster_platform_update_delivery_contract_closure` erzeugt
`platform-update generate` target-gebundene Patchartefakte statt
zeitstempelbasierter Plan-Patches.

Verbindlich sind:

- ein sauberer registrierter Target-Git-Stand;
- ein durch `TARGET_ALLOWED_PROFILES` freigegebenes Profil;
- die nächste sechsstellige Patchnummer des Zielprojekts;
- identische Werte für Archivname, `manifest.id` und `manifest.patchId`;
- vollständige `baseline.expectedBeforeSha256`-Werte aus den Rohbytes des Targets;
- Entfernung byte- und modusgleicher Operationen;
- ein Springmaster Producer Artifact Preflight in einer isolierten Target-Worktree;
- genau ein Target-`accept` und damit genau ein finaler Target-Export.

Für den Bootstrap eines älteren Target-Patchsystems verwendet der Producer den
aktuellen Springmaster-Patch-Engine explizit. Dies qualifiziert das Artefakt,
installiert den Engine aber nicht im Target.

Der vollständige Vertrag steht in:

```text
PROJECT_DOCS/TOOLING/PLATFORM_UPDATE_DELIVERY_CONTRACT_CLOSURE.md
```

## Tooling-Cutover-Delivery-Vertrag seit 000130

`target-apply` überlässt Test- und Exportentscheidungen nicht mehr impliziten
Defaults des Zielprojekts. Das in `manifest.requires.profile` gebundene Profil
bestimmt Accept-Profil und Full-Test-Pflicht.

Für den initialen Tooling-Cutover gilt:

```text
generate --profile tooling-cutover
→ dependency-complete Tooling
→ target-sicher synthetisierte export.config.json
→ Producer Artifact Preflight
→ Target Dry-run
→ accept --profile tooling --full-test --no-export
→ genau ein target-apply Closure-Export
→ Exportintegrität mit --require-evidence
```

Das Ziel-Accept muss `STATUS=SUCCESS`, `PROFILE=tooling`, `FULL_TEST=True`,
`EXPORT=False` und `LATEST_EXPORT=-` nachweisen. Anschließend erzeugt nur
`target-apply` den Full-v2-Export. Springmaster-Projektvariablen werden vor
Target-Kommandos explizit durch die Target-Bindings ersetzt.

Die vollständige Policy steht in
`PROJECT_DOCS/TOOLING/TOOLING_CUTOVER_DELIVERY_GUARD.md`.

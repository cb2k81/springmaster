# Platform Update Target Review Gate

## Zweck

Dieses Dokument beschreibt den seit `000036_springmaster_platform_update_review_gate` verbindlichen Review-Gate-Ablauf für Zielprojekt-Updates.

Springmaster darf Zielprojekt-Patches generieren und gegen das Zielprojekt per Dry-run prüfen. Die reale Zielprojektänderung darf aber erst nach explizitem Review über einen separaten Befehl erfolgen.

## Ablauf

```text
generate
preflight
apply-plan
review
target-apply
```

## Nicht-invasive Schritte

Diese Befehle verändern Zielprojekte nicht:

```bash
./bin/platform-update.sh generate <target> --profile core
./bin/platform-update.sh preflight <target> --zip <generated-patch.zip>
./bin/platform-update.sh apply-plan <target> --zip <generated-patch.zip>
./bin/platform-update.sh compatibility-plan <target> --zip <generated-patch.zip>
```

`apply-plan` erzeugt nur Review-Artefakte:

```text
build/platform-update/manifests/*_apply_plan.md
build/platform-update/manifests/*_apply_plan.env
```

Es wird bewusst kein ausführbares `*_apply_plan.sh` mehr erzeugt.

## Explizite Zielprojekt-Anwendung

Die reale Zielprojektänderung erfolgt ausschließlich über:

```bash
./bin/platform-update.sh target-apply <target> --zip <generated-patch.zip>
```

`target-apply` führt erneut einen Preflight aus, kopiert den Patch in das Zielprojekt, ruft dort das lokale Patchsystem mit `./bin/patch.sh accept` auf und erzeugt anschließend einen Zielprojekt-Full-Export, sofern `bin/export.sh` vorhanden ist.

## Ausgabearme Logs

`target-apply` schreibt die vollständige Ausgabe nach:

```text
build/platform-update/logs/*_target_apply.log
```

Im Terminal werden nur die kompakten Steuerinformationen ausgegeben:

```text
Status
Target
Patch-ID
Patch-Scope
Source ZIP
Target ZIP
Preflight-Log
Target-Apply-Log
Export-Pfad
```

Stacktraces und Buildausgaben bleiben im Log.

## Sicherheitsregel

`apply-plan` ist ein Review-Gate, kein Apply-Schritt. Wer ein Zielprojekt verändert, muss ausdrücklich `target-apply` ausführen.



## Delivery descriptor guard since 000079

Since `000079_springmaster_zbm_target_registry_and_lifecycle_alignment`, `target-apply` is not sufficient by itself. A real target mutation additionally requires the target descriptor to state:

```env
TARGET_DELIVERY_ENABLED=true
```

If this flag is missing or set to any value other than `true`, `target-apply` aborts before copying or applying the generated patch.

This deliberately protects existing/running projects. `idm` and `personnel` are configured as `DEFERRED_EXISTING_PROJECT_NO_DELIVERY`; `contacts` and `orders` remain non-delivery references. The first planned Springmaster-delivered project is `zbm`, initially configured as `INITIALIZATION_CANDIDATE` with delivery disabled until generated-project acceptance is complete.

## Initialization versus update

The review gate applies only to updates of an already initialized target project.

| Lifecycle | Tooling path | Target mutation |
|---|---|---|
| Initialization | `project-new` / future generated-project workflow | Creates a new project after explicit project-init decision |
| Update | `generate -> preflight -> apply-plan -> review -> target-apply` | Applies Core, Tools, Defaults or docs payloads to an accepted target |

For `zbm`, the next workflow is initialization first. Core, Tools and Defaults updates become eligible only after the generated `zbm` baseline has passed acceptance and the descriptor is deliberately reclassified.

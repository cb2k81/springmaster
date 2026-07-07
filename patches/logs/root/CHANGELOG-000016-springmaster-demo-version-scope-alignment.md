# 000016 - springmaster demo version scope alignment

## Typ

Tooling-/Policy-Ausrichtung ohne Java-Code.

## Änderungen

* Der Patch-Scope `demo` darf künftig `platform/versions/platform.env` und `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md` ändern.
* Das Exportprofil `demo` enthält künftig die Versionsdatei und die Version Policy.
* Der reguläre Kommandoabschluss wird auf einen Full-ZIP-Export begrenzt. Full-Parts-Baseline-Exporte bleiben optional.
* `PLATFORM_VERSION` wird auf `0.3.1-foundation` erhöht.
* `PLATFORM_TOOLING_VERSION` wird auf `0.2.2` erhöht.
* `PLATFORM_BASELINE_KIND` wird auf `full-zip` gesetzt.

## Nicht enthalten

* kein Java-Code
* keine Maven-/Build-Änderung
* keine Demo-Domäne
* kein Maven-Test erforderlich

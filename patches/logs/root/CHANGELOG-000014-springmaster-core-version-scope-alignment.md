# 000014 - Springmaster Core Version Scope Alignment

## Zweck

Der Patch schließt eine Scope-Lücke zwischen Version Policy und Patchsystem.

Core-Code- und Core-API-Erweiterungen müssen gemäß Version Policy die zentrale Versionsdatei aktualisieren. Der bisherige Scope `core` erlaubte `platform/versions/platform.env` jedoch nicht.

## Änderungen

- `bin/patch.py`: Scope `core` erlaubt nun zusätzlich `platform/versions/platform.env` und die Version Policy.
- `platform/versions/platform.env`: Tooling-Version wird auf `0.2.1` erhöht und der State-Patch auf `000014` gesetzt.
- `PROJECT_DOCS/CONCEPT/SPRINGMASTER_VERSION_POLICY.md`: Scope-Unterstützung für Core-Versionierung dokumentiert.
- `PROJECT_DOCS/TOOLING/PATCH_SYSTEM.md`: Core-Scope-Erweiterung dokumentiert.
- `PROJECT_DOCS/TOOLING/PATCH_VALIDATION_POLICY.md`: Validierung von Core-Patches mit Versionsdatei dokumentiert.
- `PROJECT_DOCS/TOOLING/TOOLING_BASELINE.md`: Tooling-Stand nach `000014` dokumentiert.
- `PROJECT_DOCS/PLANNING/SPRINGMASTER_IMPLEMENTATION_PLAN.md`: nächster Code-Patch auf `000015` verschoben.

## Validierung

- Patch-Dry-run
- Patch-Apply
- Shell-Syntaxprüfung
- Python-Kompilierung von `bin/patch.py`
- Laden von `platform/versions/platform.env`
- Tooling-Selfcheck
- Full-ZIP-Export
- Full-Parts-Baseline-Export

Kein Maven-Test, da kein Java-Code und keine Build-Konfiguration geändert werden.

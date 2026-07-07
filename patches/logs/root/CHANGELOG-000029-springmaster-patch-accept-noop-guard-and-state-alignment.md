# 000029 - springmaster patch accept noop guard and state alignment

## Kategorie

Tooling / Patchsystem

## Zweck

Dieser Patch zieht den No-op-Schutz für `patch.sh accept` nach und korrigiert den Steuerungsstand nach der tatsächlichen lokalen Anwendung des Platform-Update-Core-Payload-Mappings als Patch `000028`.

## Änderungen

* `bin/patch.py` prüft den Dry-run vor dem Apply auf wirksame Änderungen.
* Wiederholtes Accept bereits angewendeter Patches erzeugt keinen neuen Patch-Eintrag mehr.
* Reaccepts bereits angewendeter Patches enden mit Status `ALREADY_APPLIED`.
* `platform/versions/platform.env` wird auf `PLATFORM_VERSION=0.9.1-foundation`, `PLATFORM_TOOLING_VERSION=0.3.5` und `PLATFORM_STATE_PATCH=000029_springmaster_patch_accept_noop_guard_and_state_alignment` gesetzt.
* Tooling-, Patchsystem-, Validierungs- und Planungsdokumentation werden entsprechend aktualisiert.

## Validierung

Kein Java-Code und keine Maven-Build-Konfiguration betroffen. Erforderlich sind Patch-Accept, Shell-/Python-Tooling-Prüfung und Full-ZIP-Export über den Accept-Workflow.

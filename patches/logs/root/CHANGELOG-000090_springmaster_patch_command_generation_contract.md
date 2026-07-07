# 000090 - Springmaster Patch Command Generation Contract

## Scope

`root`

## Inhalt

- Ergänzt `PROJECT_DOCS/TOOLING/PATCH_COMMAND_GENERATION_CONTRACT.md` als zentrale Kurzregel für künftig generierte Patch-Kommandos.
- Verankert `accept --commit` als Standard für generierte Patch-Abschlüsse und `--push` als explizite Veröffentlichung.
- Dokumentiert das Verbot von `git add .` für normale Patch-Abschlüsse.
- Präzisiert Documentation-, Tooling- und Code-Patch-Standards in der Validation Policy.
- Ergänzt `.gitignore`, damit neue Accept-/Validation-Laufzeitlogs nicht mehr den Git-Preflight verschmutzen.

## Validierung

Documentation-/Tooling-Policy-Patch ohne Java-/Build-Änderung. Erwartete Validierung: Patch-Accept mit Profil `tooling`, Shell-/Python-/Tooling-Prüfung, Full-ZIP-Export und opt-in Git-Commit.

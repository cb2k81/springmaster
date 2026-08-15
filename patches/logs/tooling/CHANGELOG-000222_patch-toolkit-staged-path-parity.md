# 000222_patch-toolkit-staged-path-parity

## Anlass

Der kanonische Dry-run `run-20260814T184824Z-391d72ebf4ce` für `000221_sprint2-closure-amend-002` brach mit `GIT_STAGED_PATH_PARITY_FAILED` ab. Bei sieben Manifestpfaden meldete die Toolkit-Runtime nur sechs staged paths; der gelöschte aktive Sprint-Brief fehlte, während sein Archivziel vorhanden war. Der Lauf bleibt unveränderte Failure-Evidence und wird durch diesen Patch weder wiederverwendet noch als erfolgreich bezeichnet.

## Nachgewiesene Ursache

Die unveränderte Toolkit-Runtime `1.1.4` wurde mit einem getrackten Delete und einer byte-identischen Addition reproduziert. Git stellte das Paar als `R100` dar. `GitRepository.staged_paths` verwendete `git diff --cached --name-only -z`; unter Rename Detection liefert diese Projektion nur den Zielpfad. `git diff --cached --no-renames --name-only -z` lieferte dagegen beide effektiven Indexpfade als Delete und Add. Das Staging war vollständig; ausschließlich die Paritätsinventarisierung war verlustbehaftet.

## Korrektur

- Toolkit `1.1.5` setzt für die staged-path inventory explizit `--no-renames`.
- Die Gleichheitsprüfung bleibt unverändert: Manifestpfade und effektive staged paths müssen exakt übereinstimmen.
- `PATCH_TOOLKIT_STAGED_PATH_RENAME_PARITY_REGRESSION_V1` reproduziert das ursprüngliche `R100`-Fehlverhalten, beweist den positiven Delete/Add-Fall und weist einen unerwarteten zusätzlichen staged path weiterhin mit `GIT_STAGED_PATH_PARITY_FAILED` zurück.
- Die kanonische PYZ wurde aus der digest-gebundenen `1.1.4`-Runtime zweimal deterministisch und byte-identisch erzeugt. Membermenge, Reihenfolge, Modi, Kompressionsarten und normalisierte Archivmetadaten bleiben erhalten.

## Version Closure

- Cocondo Patch Toolkit: `1.1.4` -> `1.1.5`
- `PLATFORM_TOOLING_VERSION`: `0.14.1` -> `0.14.2`
- `PLATFORM_STATE_PATCH`: `000222_patch-toolkit-staged-path-parity`
- Runtime SHA-256: `938706d0b3f47991c94aee797e3c7bedf25ddde25f9b8a317c64ae733107a058`
- Platform: unverändert `0.24.0-foundation`
- Maven: unverändert `0.24.0-foundation-SNAPSHOT`
- Core, Demo, Template und Platform Update: unverändert

Dieser Change autorisiert oder behauptet keine Integration, keine Acceptance und keine Reparatur von `000221`; diese Schritte bleiben getrennte Operatorentscheidungen.

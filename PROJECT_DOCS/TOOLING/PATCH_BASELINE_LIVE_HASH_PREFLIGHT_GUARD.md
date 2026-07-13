# Patch Baseline Live Hash Preflight Guard

## Zweck

Der Live-Baseline-Preflight stellt sicher, dass ein Patch nicht nur syntaktisch korrekt ist, sondern gegen den aktuell vorhandenen Working-Tree-Vorzustand gebaut wurde.

Der Guard adressiert die Fehlerklasse, bei der ein Patch aus einem rekonstruierten Export oder einer nicht exakt aktuellen Baseline erstellt wurde. In diesem Fall passen die im Manifest hinterlegten `expectedBeforeSha256`-Werte nicht zum Live-Dateistand im Repository.

## Kommando

```bash
./bin/patch.sh live-baseline <patch.zip>
```

Das Kommando ist nicht mutierend. Es prüft:

1. Manifest-Identität (`id`, `patchId`, Archivname, Scope, Name),
2. Patch-Scope und erlaubte ZIP-Wurzelpfade,
3. vollständige `baseline.expectedBeforeSha256`-Abdeckung für alle Patch-Operationen,
4. Live-SHA-256 des aktuellen Working Trees gegen den erwarteten Vorzustand,
5. `null`/`missing`-Erwartung für neu anzulegende Dateien.

## Harte Fehlerklassen

| Fehler | Bedeutung |
|---|---|
| `LIVE_BASELINE_HASH_MISSING` | Das Manifest enthält keine `baseline.expectedBeforeSha256`-Map. |
| `LIVE_BASELINE_HASH_INCOMPLETE` | Mindestens eine Patch-Operation hat keinen erwarteten Vorzustands-Hash. |
| `LIVE_BASELINE_HASH_UNSUPPORTED` | Das Manifest enthält Hash-Einträge für Pfade ohne Patch-Operation. |
| `LIVE_BASELINE_HASH_MISMATCH` | Der Live-Dateistand passt nicht zum erwarteten Vorzustand. |

Diese Fehler dürfen nicht durch Force-Apply, manuelles Überschreiben oder Entfernen der Baseline-Hashes umgangen werden. Der Patch muss gegen den tatsächlichen Live-Stand neu erstellt werden.

## Integration in `accept`

Seit `000104_springmaster_patch_baseline_live_hash_preflight_guard` führt `accept` vor dem normalen Dry-run automatisch aus:

```bash
./bin/patch.sh live-baseline <patch.zip>
```

Erst danach folgen:

```text
apply --dry-run
apply
show latest
validierungsprofil
export
```

Damit schlägt die Abnahme bereits in einem klar benannten Schritt `live-baseline` fehl, bevor der normale Dry-run erreicht wird.

## Grenze des Guards

Der Guard kann nicht beweisen, auf welchem System ein Patch erzeugt wurde. Er beweist aber, dass die im Patch deklarierte Vorzustandsannahme exakt zum aktuellen Live-Working-Tree passt. Für den Patchprozess ist diese Eigenschaft entscheidend.

## Konsequenz für Patch-Erstellung

Ein ausgelieferter Patch muss vor Übergabe an den Anwender mindestens gegen eine echte Live-Rekonstruktion des Zielstands geprüft sein:

```bash
./bin/patch.sh live-baseline <patch.zip>
./bin/patch.sh apply --dry-run <patch.zip>
```

Bei Dokumentationspatches ist zusätzlich `git diff --check` und ein Full-ZIP-Export ausreichend. Bei Code-, Test-, Build- oder Tooling-Patches gelten die jeweiligen Validierungsprofile.

# Platform-Update Review Gate

## Ziel

`000036_springmaster_platform_update_review_gate` trennt Review und reale Zielprojekt-Anwendung hart voneinander.

Der frühere Ablauf konnte dazu verleiten, ein von `apply-plan` erzeugtes Shell-Skript direkt auszuführen. Das war technisch möglich, aber prozessual zu nah am Zielprojekt-Apply.

## Neuer Ablauf

```text
generate
preflight
apply-plan
review
target-apply
```

## Nicht-invasive Befehle

Diese Befehle verändern Zielprojekte nicht:

```bash
./bin/platform-update.sh generate <target> --profile core
./bin/platform-update.sh preflight <target> --zip <generated-patch.zip>
./bin/platform-update.sh apply-plan <target> --zip <generated-patch.zip>
./bin/platform-update.sh compatibility-plan <target> --zip <generated-patch.zip>
```

`apply-plan` und `compatibility-plan` erzeugen Review-Artefakte unter:

```text
build/platform-update/manifests/**
```

Es werden keine ausführbaren Zieländerungs-Skripte mehr erzeugt.

## Einziger Ziel-Apply-Befehl

Die reale Zielprojektänderung ist ausschließlich dieser Befehl:

```bash
./bin/platform-update.sh target-apply <target> --zip <generated-patch.zip>
```

Der Befehl ist absichtlich deutlich benannt. Wer ihn ausführt, verändert das konfigurierte Zielprojekt nach erfolgreichem Preflight.

## Logverhalten

`target-apply` schreibt vollständige Ausgaben nach:

```text
build/platform-update/logs/*_target_apply.log
```

Die Terminalausgabe bleibt kompakt:

```text
Platform-Update-Target-Apply:
  Status:       OK|FAILED|PREFLIGHT_FAILED
  Target:       <target>
  Patch-ID:     <patch-id>
  Patch-Scope:  <scope>
  Source ZIP:   <zip>
  Target ZIP:   <target-zip>
  Preflight:    <preflight-log>
  Log:          <target-apply-log>
  Export-Pfad:  <target-export-zip>
```

Stacktraces, Maven-Ausgaben und Patchdetails bleiben im Log.

## Sicherheitsregel

`apply-plan` ist ein Review-Gate, kein Apply-Schritt. Zielprojektänderungen brauchen einen expliziten `target-apply`.


## Zusammenhang mit Payload-Profilen seit 000037

Der Review-Gate gilt für jedes Payload-Profil. Besonders wichtig ist die Trennung von `core`, `core-runtime`, `core-tests` und `core-docs`: Ein Reviewer sieht vor `target-apply`, ob ein Zielpatch nur technischen Core oder zusätzlich Masterdokumentation überträgt.

# Patch Archive and Rollback Policy

## Zweck

Diese Policy regelt, wie lokale Patcharchive, Baseline-Exporte und Rollback-Fähigkeit voneinander abgegrenzt werden.

## Grundsatz

Ein Full-Parts-Baseline-Export beschreibt den aktuellen Projektstand. Er ersetzt kein vollständiges Rollback-Archiv.

Rollback-Fähigkeit entsteht aus:

```text
patches/archives/**
```

Diese Archive enthalten die angewendeten Patch-ZIPs beziehungsweise die für Rollback erforderlichen Vorher-/Nachher-Informationen des lokalen Patchsystems.

## Export-Abgrenzung

`patches/archives/**` bleibt aus regulären Full- und Full-Parts-Baseline-Exporten ausgeschlossen.

Begründung:

* Archive können schnell groß werden.
* Baseline-Exporte sollen kompakt und reviewfähig bleiben.
* Rollback-Archive sind operative Artefakte, nicht automatisch Review-Artefakte.

Exportiert werden regulär:

```text
patches/logs/**
```

Damit bleibt nachvollziehbar, welche Patches angewendet wurden.

## Konsequenz

Aus einer Baseline allein kann der aktuelle Zustand rekonstruiert und geprüft werden. Ein vollständiger lokaler Rollback auf jeden früheren Patchstand ist daraus aber nicht garantiert.

Für echte Rollback-Sicherheit müssen Patcharchive separat gesichert werden.

## Mindestregel für kritische Änderungen

Vor riskanten Änderungen ist mindestens ein aktueller Full-Parts-Baseline-Export zu erzeugen.

Für Änderungen an folgenden Bereichen ist zusätzlich eine Sicherung von `patches/archives/**` empfohlen:

* Patchsystem
* Exporttool
* Platform-Update-Generator
* Buildtool
* DBTool
* Migrationen mit Zielprojektwirkung

## Künftige Erweiterung

Später soll ein dediziertes Exportprofil ergänzt werden, z. B.:

```text
rollback-archives
```

Dieses Profil darf nicht automatisch Teil von `baseline` sein. Es dient der bewussten operativen Sicherung.

## Zielprojekt-Regel

Wenn Springmaster später Update-Patches für Zielprojekte erzeugt, muss jeder Update-Patch einen Rollback-Hinweis enthalten:

* Ausgangsversion
* Zielversion
* betroffene Dateien
* lokaler Patcharchive-Pfad im Zielprojekt
* Hinweis, ob ein Rollback-Patch technisch möglich ist

## Nicht zulässig

Nicht zulässig ist:

* Baseline-Export als vollständige Rollback-Garantie zu bezeichnen.
* Patcharchive stillschweigend in reguläre Review-Baselines aufzunehmen.
* Zielprojekt-Updates ohne Rollback-Hinweis zu erzeugen.

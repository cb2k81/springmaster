# Export- und Artefakt-Hygiene

## Zweck

Der reguläre Springmaster-Export ist eine Quell-/Projektbaseline. Er ist kein forensischer Dump des kompletten Arbeitsverzeichnisses und darf keine lokalen Build-, Laufzeit-, Patcharchiv- oder Zielprojekt-Operationsartefakte enthalten.

## Verbindliche Abgrenzung

Reguläre Exporte schließen insbesondere aus:

```text
target/**
build/**
tmp/**
exports/**
.git/**
patches/archives/**
platform/update/generated/**
platform/update/manifests/**
```

Zusätzlich bleiben lokale Umgebungsdateien, IDE-Dateien, Python-Caches sowie Binär- und Archivdateien ausgeschlossen.

## `.env.example`-Regel

Nur die projektweite Root-Datei `.env.example` darf über die Export-Konfiguration wieder eingeschlossen werden. Verschachtelte `.env.example`-Dateien unter ausgeschlossenen Bereichen, insbesondere unter `patches/archives/**`, dürfen den globalen Ausschluss nicht mehr umgehen.

## Platform-Update-Artefakte

Die von `bin/platform-update.sh` erzeugten Zielpatch-ZIPs, Preflight-Logs, Apply-Pläne und Compatibility-Pläne sind Operations-/Review-Artefakte. Sie dürfen temporär im Arbeitsbaum liegen, gehören aber nicht in reguläre Full-ZIP-Baselines.

Seit `000035_springmaster_platform_update_build_workspace` werden diese Artefakte standardmäßig unter dem überschreibbaren Workspace abgelegt:

```text
build/platform-update/**
```

Die bisherigen Legacy-Pfade bleiben weiterhin aus normalen Exports ausgeschlossen:

```text
platform/update/generated/**
platform/update/manifests/**
```

## Forensik

Wenn ein vollständiger Arbeitsbaumzustand forensisch benötigt wird, soll dieser bewusst außerhalb des regulären Exporttools erzeugt werden, zum Beispiel als separat benanntes Archiv oder reine Dateiliste. Der reguläre Export bleibt die saubere Baseline für Folgepatches.



## Review-Gate-Artefakte seit 000036

`build/platform-update/manifests/**` und `build/platform-update/logs/**` bleiben Operationsartefakte. Review-Pläne, Review-Env-Dateien und Target-Apply-Logs sind nicht Teil regulärer Springmaster-Baselines.

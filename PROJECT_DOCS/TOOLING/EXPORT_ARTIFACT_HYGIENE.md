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

## Hash and closure hygiene since 000124

A clean export baseline contains an authoritative raw-byte manifest in each profile metadata file. Baseline hashes are taken from this manifest, not from the rendered text body. The metadata records export format version, completion status, file count, ordered included paths, raw sizes, SHA-256 values, canonical manifest digest and Git source state.

When a final runner supplies prior-gate evidence, the exporter embeds a separately digested `closure-evidence.json` and marks the export operation itself `COMPLETE`. This avoids a duplicate export while separating export completion from later runner status updates.

Operational `patches/logs/validation/**` trees are excluded from source profiles. They are mutable during and after export and therefore cannot be part of an immutable raw-byte snapshot. Stable gate facts belong in the embedded closure evidence; the external validation directory remains operational diagnostics.

`bin/export-integrity-check.py` and its positive/tampered fixtures are mandatory Tooling checks.

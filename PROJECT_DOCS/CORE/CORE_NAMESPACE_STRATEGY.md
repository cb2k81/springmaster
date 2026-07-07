# Core Namespace Strategy

## 1. Entscheidung

Der wiederverwendbare Core wird im Masterprojekt und in Zielprojekten unter demselben Java-Namespace geführt:

```text
de.cocondo.system
```

Springmaster-spezifische Bestandteile bleiben getrennt:

```text
de.cocondo.platform.app   # ausführbare Master-Anwendung
de.cocondo.platform.demo  # Demo-/Validierungsfachlichkeit
```

## 2. Begründung

Der Springmaster-Core wird kurzfristig nicht als separates Maven-Artefakt ausgeliefert, sondern über Patch-/Update-Mechanismen als Quellcode in Zielprojekte übertragen. Für diesen Modus ist ein identischer Package-Root vorteilhaft:

* keine Paket-Rewrites bei regulären Core-Updates,
* stabilere Diffs,
* geringeres Risiko bei Import-Anpassungen,
* Zielprojekte können Core-Updates einfacher prüfen,
* Migration bestehender Apps kann schrittweise auf den kanonischen Core-Pfad normalisiert werden.

Die Trennung zwischen Master und Zielprojekt erfolgt damit nicht über unterschiedliche Core-Packages, sondern über Rollen:

| Rolle | Namespace |
|---|---|
| Master-App | `de.cocondo.platform.app` |
| Master-Demo | `de.cocondo.platform.demo` |
| wiederverwendbarer Core | `de.cocondo.system` |

## 3. IDM-Migration

Der IDM-Referenzexport verwendet für den technischen System-Core:

```text
de.cocondo.app.system
```

Für die initiale Migration gilt deshalb:

```text
de.cocondo.app.system -> de.cocondo.system
```

Diese Transformation ist ein einmaliger Migrationsschritt aus der IDM-Referenzquelle. Nach der Migration werden Core-Updates nicht mehr zwischen unterschiedlichen Core-Packages übersetzt.

## 4. Zielpfade

Core-Code im Master:

```text
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
```

Core-Code in Zielprojekten:

```text
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
```

Abweichende Legacy-Pfade in bestehenden Zielprojekten müssen explizit über Migrations- oder Kompatibilitätsregeln behandelt werden. Sie sind nicht der Standard für neue Core-Updates.

## 5. Konsequenz für kommende Patches

Der nächste Code-Patch darf keinen Core-Code unter `de.cocondo.platform.core` anlegen. Der Basic-Core-Slice beginnt unter:

```text
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
```

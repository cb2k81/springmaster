# Core App Scan Alignment

## Zweck

Dieses Dokument definiert die Component-Scan-Ausrichtung für Springmaster und für neu erzeugte Projekte.

## Entscheidung

Der wiederverwendbare Core liegt im Master und in Zielprojekten unter:

```text
de.cocondo.system
```

Spring-Komponenten aus diesem Namespace müssen durch die Anwendung explizit mitgescannt werden, weil App- und Demo-Code nicht unter demselben Package-Root liegen.

## Springmaster

Springmaster verwendet:

```java
@SpringBootApplication(scanBasePackages = {
        "de.cocondo.platform",
        "de.cocondo.system"
})
```

Damit werden gescannt:

| Namespace | Zweck |
|---|---|
| `de.cocondo.platform` | Springmaster-App, Demo-Code und Master-spezifische Komponenten |
| `de.cocondo.system` | verteilbarer Core |

## Project Skeleton

Neu erzeugte Projekte verwenden analog:

```java
@SpringBootApplication(scanBasePackages = {
        "__BASE_PACKAGE__",
        "de.cocondo.system"
})
```

Nach Token-Ersetzung wird daraus beispielsweise:

```java
@SpringBootApplication(scanBasePackages = {
        "de.cocondo.sample",
        "de.cocondo.system"
})
```

## Migrationsnutzen

Die Regel verhindert eine spätere Divergenz zwischen Master und Zielprojekten:

* Core-Code wird unter identischem Package geführt.
* Zielprojekte benötigen keinen abweichenden Component-Scan.
* Spätere Core-Komponenten können deterministisch verteilt werden.
* Package-Rewrites für den Core bleiben auf die einmalige IDM-zu-Core-Migration beschränkt.

## Validierung

Code-Patches, die die Scan-Ausrichtung verändern, müssen mindestens prüfen:

```bash
mvn test
./bin/project-new.sh create --dry-run --name sample --path /tmp/springmaster-sample
./bin/project-new.sh create --name sample --path /tmp/springmaster-sample
cd /tmp/springmaster-sample
mvn test
```

Für Springmaster ist zusätzlich eine Testabdeckung der `@SpringBootApplication(scanBasePackages = ...)`-Konfiguration erforderlich.

# Project-New Instantiation Acceptance Review

Patch: `000076_springmaster_project_new_instantiation_acceptance_review`

## Zweck

Dieses Review belegt, dass Springmaster nach `000075` nicht nur Standards und Demo-Candidate-Code enthält, sondern ein neues Java-Backend-Skeleton mechanisch instanziieren kann.

Der Acceptance-Fokus liegt bewusst auf dem technischen Projektstart, nicht auf einem produktionsreifen Fachservice.

## Acceptance-Artefakt

Neu eingeführt wird:

```text
bin/project-new-acceptance.sh
src/test/java/de/cocondo/platform/tooling/ProjectNewInstantiationAcceptanceTest.java
```

Das Shell-Skript erzeugt ein temporäres Beispielprojekt unter:

```text
target/project-new-acceptance/sample-backend
```

Die JUnit-Prüfung führt die Acceptance ohne verschachtelten Maven-Lauf des generierten Projekts aus. Das Apply-/Verify-Skript kann zusätzlich den vollständigen generated-project Maven-Test ausführen.

## Geprüfte Instanziierungsfähigkeit

Die Acceptance prüft:

| Bereich | Erwartung |
|---|---|
| Dry-run | `project-new.sh create --dry-run` erzeugt nur einen Plan |
| Create | `project-new.sh create` schreibt ein neues Zielprojekt |
| Zielpfadschutz | Das Ziel wird neu erzeugt und nicht überschrieben |
| Maven-Basis | `pom.xml` enthält gerenderte `groupId` und `artifactId` |
| Package Rendering | Application und Controller liegen unter dem Ziel-Basispaket |
| Tooling | `patch.sh`, `export.sh`, `dbtool.sh`, `build.sh`, `tooling-selfcheck.sh` werden übernommen |
| Patch-Bootstrap | Bootstrap-Patch `000001_project_new_bootstrap` ist registriert |
| Export | Das generierte Projekt kann einen Full-ZIP-Export erzeugen |
| DBTool | `dbtool.sh status` validiert Konfiguration ohne DB-Verbindung |
| `.env` Hygiene | `.env.example` wird erzeugt, `.env` nicht |
| DB Defaults | Shell-Tooling nutzt sanitizierte DB-Namen, nicht den hyphenated Projektnamen |

## Geschlossene Schwäche

Das Review hat eine Instanziierungsschwäche sichtbar gemacht und innerhalb von `000076` geschlossen:

* `project-new.sh` tokenisiert kopierte Tooling-Dateien jetzt DB-spezifisch, bevor die generische `springmaster`-Ersetzung greift.
* Dadurch werden Defaults in `bin/lib/core/env.sh` für neue Projekte korrekt zu `sample_backend` und `sample_backend_build` gerendert.
* Ohne diese Korrektur konnte `dbtool.sh status` bei Projektnamen mit Bindestrich ohne `.env` inkonsistente Default-Datenbanknamen ausgeben.

## Aktuelle Bewertung

Springmaster ist nach diesem Review tauglich, ein neues technisches Java-Backend-Skeleton zu instanziieren.

Validierbar sind:

* Skeleton-Erzeugung,
* Patchsystem-Bootstrap,
* Tooling-Mitgabe,
* Exportfähigkeit,
* DBTool-Basiskonfiguration,
* Maven-Kontexttest des generierten Projekts,
* deterministische Acceptance über `bin/project-new-acceptance.sh`.

## Grenzen

Das erzeugte Projekt ist ein technisches Backend-Skeleton. Es enthält noch keinen fachlichen Aggregate-Slice.

Nicht Bestandteil der Project-New Acceptance sind:

* automatische CatalogItem- oder Fachdomänen-Generierung,
* Core-Verteilung als Maven-Artefakt,
* implementierte Security,
* produktive DB-Persistence,
* OpenAPI-Evidence,
* strict Gates,
* Zielprojekt-Update.

Diese Punkte bleiben Folgearbeiten nach erfolgreichem Instanziierungsnachweis.

## Freigabeentscheidung

`project-new.sh` darf nach `000076` als konservatives Instanziierungstool für neue technische Java-Backend-Baselines verwendet werden.

Die Freigabe gilt nicht für produktionsreife Fachservices ohne nachfolgenden fachlichen Implementierungspatch.


## Folgeentscheidung seit 000077

Die Acceptance aus `000076` beantwortet nur die Frage, ob Springmaster ein technisches Backend-Skeleton instanziieren kann. Diese Frage ist positiv beantwortet.

Patch `000077_springmaster_generated_service_slice_readiness_plan` definiert den nächsten Reifegrad: Ein fachlicher generated service slice muss getrennt vom Skeleton geplant und validiert werden.

Wichtig bleibt:

* Project-New erzeugt keine Demo-Domäne und keinen Fachslice.
* Core-Verteilung ist vor einer Slice-Erzeugung explizit zu entscheiden.
* Zielprojekt-Delivery bleibt blockiert, bis ein eigener Freigabe- und Vergleichsschritt erfolgt.
* Der CatalogItem-Slice ist eine Candidate-Referenz, keine Canonical-Quelle für unkritische Codekopie.

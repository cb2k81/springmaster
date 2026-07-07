# Project State Review after 000012

## Zweck

Dieses Review bewertet den erreichten Stand nach Patch `000012_springmaster_core_persistence_dependency_preparation` gegen das Masterkonzept, die gesetzten Arbeitsregeln und die Qualitätsmerkmale des Projekts.

## Bewerteter Stand

Maßgeblich ist die Baseline nach `000012` mit angewendeter Patch-Historie `000001` bis `000012`.

## Gesamturteil

Der aktuelle Stand ist als **Foundation-Stand mit grünem technischem Ergebnis und gelben Zielerreichungspunkten** zu bewerten.

Die technische Basis ist stabil:

* das Projekt ist Maven-buildbar
* das Patchsystem arbeitet manifestbasiert mit Dry-run, Apply, Patch-Log und lokaler Archivierung
* Full-ZIP- und Full-Parts-Baseline-Exporte sind etabliert
* das Project Skeleton kann ein lauffähiges Sample-Projekt erzeugen
* der Core-Namespace ist auf `de.cocondo.system` festgelegt
* der erste Core-Code-Slice ist vorhanden und getestet
* die minimale Persistence-Dependency ist vorbereitet

Nicht abgeschlossen sind:

* Demo-Domäne mit aktiver Core-Nutzung
* operativer Target-Update-Generator
* reale DBTool-/Liquibase-Operationen gegen MariaDB
* OpenAPI-/SBOM-/Runtime-ZIP-Endvalidierung
* vollständige Versionierungs- und Rollback-Operationalisierung über Zielprojekte hinweg

## Zielabgleich

| Ziel | Stand | Bewertung |
|---|---|---|
| Masterprojekt als kanonische Pflegebasis | erreicht als Foundation | Projektstruktur, Patchsystem, Export und Buildbasis existieren. |
| Tooling im Master pflegen | begonnen | Patch-, Export-, DBTool-, Build- und Project-New-Werkzeuge liegen im Master. |
| Core im Master pflegen | begonnen | Fachfreie Core-Basis liegt unter `de.cocondo.system`. |
| Neue Projekte aus Skeleton erzeugen | erreicht für Minimalprojekt | `project-new.sh` erzeugt ein Maven-testbares Sample-Projekt. |
| Core und Apps ohne Package-Rewrite ausrichten | erreicht | Master und Zielprojekte verwenden `de.cocondo.system` für Core. |
| Demo zur Core-Validierung | offen | Noch keine echte Demo-Domäne vorhanden. |
| Zielprojekt-Updates erzeugen | offen | `platform-update.sh` ist noch nicht operativ. |
| Rollback | lokal vorbereitet | Patcharchive sind lokal vorhanden; Baseline-Exporte enthalten aus Größen-/Hygienegründen nur Logs. |
| Versionierung | mit 000013 initialisiert | Versionspolicy und initiale Foundation-Versionen werden festgelegt. |

## Regelabgleich

### Erfüllt

* Jede Änderung wurde patchbasiert geliefert.
* Dry-run wurde vor Apply ausgeführt.
* Code- und Build-Konfigurationspatches wurden mit `mvn test` geprüft.
* Documentation-only-Patches sind von Maven-Test und Build ausgenommen.
* Full-ZIP- und Full-Parts-Baseline-Exporte werden am Ende der Kommando-Stacks erzeugt.
* Der Core-Namespace wurde vor der Code-Migration korrigiert.

### Zu beachten

* Dokumentations- und Planungsdokumente müssen bei jedem Statuswechsel aktualisiert werden, damit keine veralteten „nächster Schritt“-Aussagen stehen bleiben.
* Core-Code darf nicht dauerhaft nur durch isolierte Unit-Tests wachsen; Demo-Nutzung muss zeitnah folgen.
* Patcharchive sind Rollback-Artefakte und nicht automatisch Teil des Full-Parts-Baseline-Exports.

## Qualitätsrisiken

### Demo-Lücke

Der Core wurde begonnen, aber noch nicht in einer fachlichen Demo-Domäne verwendet. Für weitere Core-Slices ist deshalb ein konkreter Demo-Anschluss einzuplanen.

### Update-Lücke

Der Master kann noch keine Zielprojekt-Patches erzeugen. Das ist für die Gesamt-DoD zentral und darf nach den nächsten Core-/Demo-Grundlagen nicht weiter verschoben werden.

### Rollback-Archiv-Lücke

Lokale Rollbacks sind durch `patches/archives/**` möglich. Da diese Archive nicht in Full-Parts-Baselines enthalten sind, muss ihre Sicherung separat oder über ein eigenes Exportprofil geregelt werden.

## Entscheidung aus diesem Review

Patch `000013` hält den Foundation-Stand fest, initialisiert die Versionierung und dokumentiert die Rollback-/Patcharchive-Regel.

Der nächste Code-Schritt darf erst erfolgen, wenn er:

1. klein und fachfrei bleibt,
2. mit Tests validiert wird,
3. die Demo-Lücke nicht vergrößert oder eine konkrete Demo-Folge vorbereitet,
4. keine Zielprojekt-Update-Annahmen ohne Tooling-Grundlage trifft.

## Nächste empfohlene Schritte

1. `000014_springmaster_core_persistence_basic_types.zip`
   * erster JPA-naher, aber fachfreier Core-Code-Slice
   * nur wenn die Typen unmittelbar durch `jakarta.persistence-api` abgedeckt sind
   * Pflicht: `mvn test`
2. Danach zeitnah Demo-Fundament vorbereiten
   * minimale Demo-Domäne, die Core-Bausteine sichtbar nutzt
3. Danach Target-Update-Foundation operationalisieren
   * zunächst Dry-run für ein verifiziertes Zielprojekt

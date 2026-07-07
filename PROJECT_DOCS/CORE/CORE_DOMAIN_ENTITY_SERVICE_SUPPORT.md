# Core Domain Entity Service Support

## Zweck

Patch `000042_springmaster_core_domain_entity_service_support` übernimmt den ersten risikoarmen Service-Support aus dem zuvor klassifizierten Entity-/Service-/Sequence-Slice in den Springmaster-Core.

Der Patch ist bewusst klein gehalten: Er ergänzt Factory-/Helper-Services für bestehende Core-Entity-Verträge, ändert aber kein Persistenzmodell, keine Repositories und kein Zielprojekt.

## Enthaltene Klassen

```text
src/main/java/de/cocondo/system/entity/service/DomainEntityService.java
src/main/java/de/cocondo/system/entity/service/TagService.java
```

### DomainEntityService

`DomainEntityService` erzeugt neue `DomainEntity`-Instanzen über den parameterlosen Konstruktor und ersetzt die technische ID durch eine ID aus dem injizierten `IdGeneratorService`.

Damit wird die aus IDM bekannte Factory-Funktion in den gemeinsamen Core übernommen, aber ohne Lombok und ohne `de.cocondo.app.*`-Kopplung.

### TagService

`TagService` kapselt einfache Tag-Operationen auf der bestehenden `DomainEntity`-Tag-Collection:

```text
addTag
removeTag
getAllTags
hasTag
```

Der Service bleibt bewusst collection-basiert. Er führt kein Metadata-Persistenzmodell ein und nutzt keine `KeyValuePair`-Entity.

## Paketentscheidung

Die Services liegen unter:

```text
de.cocondo.system.entity.service
```

Damit wird bewusst zwischen dem Entity-Modell selbst und serviceförmigem Support getrennt. Der ursprüngliche IDM-Alt-Core lag teilweise direkt unter `entity/**` bzw. `entity/metadata/**`; Springmaster führt die Service-Unterstützung klarer unter `entity/service/**`.

## Tests

Der Patch ergänzt Tests für:

```text
DomainEntityService
TagService
Spring @Service Annotationen
Fehlerfall ohne parameterlosen Konstruktor
Tag hinzufügen, entfernen, abfragen
Null-Entity-Schutz
```

## Bewusst nicht enthalten

```text
Keine IDM-Zielprojektänderung
Keine IDM-Importmigration
Keine Löschung von de.cocondo.app.system/**
Keine Änderung des DomainEntity-Mappings
Keine KeyValuePair-JPA-Übernahme
Keine Metadata-Persistenz
Keine NumberSequence-Übernahme
Keine Repository- oder Liquibase-Änderung
Keine Security/JWT-Übernahme
Keine HTTP/Web-Konfiguration
Keine Event-Persistenz
```

## Ergebnis

Mit `000042` sind die risikoarmen Service-Bausteine aus dem Slice `core-entity-service-and-sequence` im Springmaster-Core verfügbar.

Die verbleibenden Klassen dieses Slice bleiben bewusst gesperrt, bis ihre Persistenz- und Runtime-Entscheidungen getroffen sind:

```text
entity/metadata/AbstractMetadataDomainService.java
entity/metadata/KeyValuePair.java
entity/metadata/KeyValueService.java
entity/sequence/NumberSequence.java
entity/sequence/NumberSequenceRepository.java
entity/sequence/NumberSequenceService.java
```

Der nächste sinnvolle Schritt ist keine IDM-Migration, sondern die nächste fachlich isolierte Core-Entscheidung:

```text
000043_springmaster_core_metadata_persistence_model_decision
```

# Core Entity/Service/Sequence Inventory

## Zweck

Patch `000041_springmaster_core_entity_service_sequence_inventory` ist eine reine Inventarisierungs- und Entscheidungsstufe für den persistenznahen IDM-Alt-Core-Slice `core-entity-service-and-sequence`.

Der Patch übernimmt **keinen Java-Code**, verändert keine Maven-Abhängigkeiten, erzeugt keine Zielprojekt-Patches und verändert kein Zielprojekt. Er trennt die noch offenen Klassen aus `de.cocondo.app.system.entity/**`, `de.cocondo.app.system.entity.metadata/**` und `de.cocondo.app.system.entity.sequence/**` in sichere Folgeschritte.

## Ausgangslage

| Bereich | Stand |
|---|---|
| Springmaster-Core | `de.cocondo.system` ist Zielnamespace. |
| IDM-Alt-Core | `de.cocondo.app.system` soll früh entfernt werden. |
| Voraussetzung für Entfernung | Alle relevanten Features müssen im Springmaster-Core enthalten oder bewusst als IDM-spezifisch klassifiziert sein. |
| Aktueller Core-Stand | DTO/List/Metadata-Contracts und UUID-ID-Generator sind umgesetzt. |
| Aktuelle Sperre | Keine IDM-Zielprojektänderung, keine Importmigration, keine Löschung. |

## Klassifizierter Slice

Der bisherige Gap-Slice `core-entity-service-and-sequence` umfasst acht Dateien:

```text
entity/DomainEntityService.java
entity/metadata/AbstractMetadataDomainService.java
entity/metadata/KeyValuePair.java
entity/metadata/KeyValueService.java
entity/metadata/TagService.java
entity/sequence/NumberSequence.java
entity/sequence/NumberSequenceRepository.java
entity/sequence/NumberSequenceService.java
```

## Detailklassifikation

| Datei | Kategorie | Risiko | Entscheidung |
|---|---|---|---|
| `entity/DomainEntityService.java` | Core-Service / Factory | mittel | Gemeinsamer Core-Kandidat, aber separat und ohne Lombok übernehmen. |
| `entity/metadata/TagService.java` | Tag-Service | niedrig-mittel | Gemeinsamer Core-Kandidat, kann vor Metadata-Persistenz übernommen werden. |
| `entity/metadata/KeyValueService.java` | Metadata-Service | hoch | Erst nach Metadata-Persistenzentscheidung übernehmen. |
| `entity/metadata/KeyValuePair.java` | JPA-Metadata-Entity | hoch | Nicht isoliert übernehmen; braucht DomainEntity-Metadata-Modell. |
| `entity/metadata/AbstractMetadataDomainService.java` | generischer Metadata-Domain-Service | hoch | Erst nach KeyValuePair/DomainEntity-Metadata-Modell übernehmen. |
| `entity/sequence/NumberSequence.java` | JPA-Sequence-Entity | hoch | Eigener Sequence-Slice mit Schema-/Repositoryentscheidung. |
| `entity/sequence/NumberSequenceRepository.java` | Spring-Data-Repository | hoch | Eigener Sequence-Slice; nicht mit Entity-Service-Support vermischen. |
| `entity/sequence/NumberSequenceService.java` | transaktionaler Sequence-Service | hoch | Eigener Sequence-Slice; concurrency/transaction semantics prüfen. |

## Wichtige Architekturbeobachtungen

### DomainEntity-Modell ist nicht identisch

IDM verwendet im Alt-Core:

```text
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
DomainEntity mit @OneToMany keyValuePairs
```

Springmaster verwendet aktuell:

```text
@MappedSuperclass
DomainEntity ohne persistente KeyValuePair-Assoziation
```

Das ist ein bewusst relevanter Unterschied. `KeyValuePair` kann nicht blind übernommen werden, weil die Beziehung auf `DomainEntity` im IDM auf eine Entity zeigt, während Springmaster `DomainEntity` derzeit als `@MappedSuperclass` führt.

### Metadata-DTOs sind umgesetzt, Metadata-Persistenz nicht

Seit `000039` existieren im Springmaster-Core die DTO-/Mapper-Vertragsbausteine:

```text
DomainEntityMetadataDTO
KeyValuePairDTO
KeyValuePairPayload
DomainMetadataSupportMapper
```

Diese bilden aber noch **kein persistentes Metadata-Modell**. `DomainMetadataSupportMapper` liefert Key-Value-Paare derzeit bewusst leer, solange kein Core-Metadata-Persistenzmodell entschieden ist.

### Sequence-Funktion ist potentiell Core, aber nicht dependency-arm

`NumberSequence*` ist fachfrei und damit grundsätzlich Core-fähig. Die Übernahme ist trotzdem nicht risikoarm, weil sie mindestens folgende Entscheidungen berührt:

```text
Spring Data Repository Runtime
JPA Entity Scanning
Tabellen-/Schema-Namen
Liquibase-/DDL-Verantwortung
Transaktionsgrenzen
Nebenläufigkeit und Sperrmodell
```

Deshalb wird Sequence nicht zusammen mit `DomainEntityService` oder `TagService` übernommen.

## Externe Nutzung im IDM

Die persistenznahen Support-Klassen dieses Slice werden außerhalb des Alt-Core nur indirekt genutzt:

| Bereich | Befund |
|---|---|
| `DomainEntity` | Direkt von IDM-Domain-Entities erweitert. |
| `DomainEntityService` | Keine direkte externe Nutzung gefunden. |
| `TagService` | Keine direkte externe Nutzung gefunden. |
| `KeyValueService` | Keine direkte externe Nutzung gefunden. |
| `KeyValuePair` | Nur über `DomainEntity`/Metadata-Vertragsbausteine relevant. |
| `NumberSequence*` | Keine direkte externe Nutzung gefunden. |

Daraus folgt: Die nächste Übernahme kann klein beginnen. Die spätere IDM-Importmigration muss jedoch zuerst die Domain-Entities von `de.cocondo.app.system.entity.DomainEntity` auf `de.cocondo.system.entity.DomainEntity` umstellen, bevor der alte Alt-Core entfernt werden kann.

## Empfohlene Folgeslices

### 000042: DomainEntityService und Tag-Service Support

Ziel: risikoarmen Service-Support übernehmen, ohne Persistenzmodell zu verändern.

Voraussichtlicher Inhalt:

```text
src/main/java/de/cocondo/system/entity/DomainEntityService.java
src/main/java/de/cocondo/system/entity/metadata/TagService.java
src/test/java/de/cocondo/system/entity/DomainEntityServiceTest.java
src/test/java/de/cocondo/system/entity/metadata/TagServiceTest.java
```

Voraussetzungen:

```text
Kein Lombok
Keine IDM-Imports
Keine Änderung am DomainEntity-Mapping
Keine KeyValuePair-Persistenz
Keine Sequence-Übernahme
mvn test grün
```

### Späterer Slice: Metadata Persistence Model

Ziel: entscheiden, ob und wie dynamische Key-Value-Metadata im Core persistiert wird.

Offene Entscheidungspunkte:

```text
DomainEntity bleibt @MappedSuperclass oder wird als Entity-Hierarchie geführt?
KeyValuePair ist Core-Entity oder Zielprojekt-spezifische Entity?
Tabellenname key_value_pair bleibt global stabil?
DomainMetadataSupportMapper bleibt contract-only oder mapped persistente KeyValuePairs?
```

### Späterer Slice: NumberSequence Foundation

Ziel: fachfreien Nummernkreis-Service übernehmen.

Vorbedingung:

```text
Spring Data/JPA Runtime Policy
Repository-Scan-Policy
Liquibase-/Schema-Policy
Nebenläufigkeits-/Locking-Entscheidung
```

## Nicht zulässig im nächsten Code-Slice

```text
Keine Änderung an IDM.
Keine Importmigration.
Keine Löschung von de.cocondo.app.system/**.
Keine Änderung des DomainEntity-Mappings.
Keine KeyValuePair-JPA-Übernahme.
Keine NumberSequence-Übernahme.
Keine Repository- oder Liquibase-Änderung.
```

## DoD vor Entfernung des IDM-Alt-Core

Der Alt-Core `de.cocondo.app.system/**` darf erst entfernt werden, wenn alle folgenden Bedingungen erfüllt sind:

```text
Alle relevanten Features sind im Springmaster-Core vorhanden oder bewusst als IDM-spezifisch klassifiziert.
Alle IDM-Imports auf de.cocondo.app.system.* sind migriert oder entfernt.
Maven-Testlauf im IDM ist grün.
Core-Zielpayload wurde über Review-Gate und target-apply angewendet.
IDM-Integrationsdokumentation ersetzt pauschale Master-Core-Dokumentation.
Keine Runtime-Abhängigkeit auf de.cocondo.app.system.entity.DomainEntity bleibt übrig.
```

## Ergebnis

`000041` bestätigt: Der persistenznahe Entity-/Metadata-/Sequence-Bereich ist nicht als ein gemeinsamer Code-Slice zu übernehmen. Der nächste sichere Schritt ist klein und dependency-arm:

```text
000042_springmaster_core_domain_entity_service_support
```


## Umsetzung seit 000042

Patch `000042_springmaster_core_domain_entity_service_support` setzt den risikoarmen Teil des Slices um:

```text
de.cocondo.system.entity.service.DomainEntityService
de.cocondo.system.entity.service.TagService
```

Die Umsetzung verändert kein `DomainEntity`-Mapping, führt keine `KeyValuePair`-Persistenz ein und übernimmt keine `NumberSequence`-Klassen.

Die verbleibenden Klassen dieses Slice bleiben gesperrt, bis ihre Persistenz-/Runtime-Entscheidungen getroffen sind. Der nächste empfohlene Schritt ist:

```text
000043_springmaster_core_metadata_persistence_model_decision
```

## Persistence standard follow-up since 000051

Patch `000051_springmaster_domain_entity_persistence_standard` does not implement the deferred metadata or sequence classes from this inventory. It documents the decision boundary instead:

* persistent KeyValuePair metadata remains deferred until a dedicated metadata persistence ADR exists;
* NumberSequence remains deferred until locking, table/schema, transaction and migration decisions exist;
* the current Core `DomainEntity` remains a `@MappedSuperclass` foundation;
* Catalog-demo must not introduce metadata persistence or business-number generation implicitly inside its first domain slice.

This keeps the inventory open for later implementation patches while giving Catalog-demo a deterministic persistence baseline.


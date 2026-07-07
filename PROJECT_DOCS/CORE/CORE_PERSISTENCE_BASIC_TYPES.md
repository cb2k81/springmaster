# Core Persistence Basic Types

## Zweck

Patch `000015_springmaster_core_persistence_basic_types` ergänzt den ersten JPA-nahen, aber weiterhin fachfreien Core-Code-Slice unter dem kanonischen Core-Namespace:

```text
src/main/java/de/cocondo/system/**
src/test/java/de/cocondo/system/**
```

## Enthaltene Typen

| Typ | Zweck |
|---|---|
| `Auditable` | technischer Audit-Vertrag für erstellende und ändernde Benutzer-/Zeitstempel |
| `AuditingEntityListener` | JPA-Listener für Audit-Felder bei `@PrePersist` und `@PreUpdate` |
| `DomainEntity` | abstrakte persistenznahe Basis mit ID, Optimistic-Locking-Version, Tags und Audit-Feldern |
| `DomainEntityListener` | technischer JPA-Sicherheitslistener für fehlende IDs vor Persistenz |
| `Range` | `@Embeddable` Gültigkeitszeitraum |

## Bewusste Abgrenzung

Nicht enthalten sind:

* Repository-Schicht
* Spring Data JPA Runtime-Aktivierung
* DataSource-Konfiguration
* Liquibase-Changesets
* Metadata-Key-Value-Struktur
* Demo-Domäne
* Security-/JWT-Bezug

## Abweichungen gegenüber IDM-Referenz

Die IDM-Referenz wurde nicht blind kopiert. Die Übernahme wurde für Springmaster bewusst minimalisiert:

* `DomainEntity` ist in diesem Slice `@MappedSuperclass` statt konkrete `@Entity` mit `TABLE_PER_CLASS`.
* `DomainEntity` enthält noch keine Key-Value-Metadata-Relation.
* Lombok wird nicht verwendet.
* Hibernate-spezifische Equals-Helfer werden nicht verwendet.

Diese Reduktion hält den Core-Slice runtime-arm, fachfrei und testbar. Eine spätere Metadata-/Repository-/JPA-Runtime-Erweiterung erfolgt in separaten Patches.

## Validierung

Dieser Patch ist ein Code-Patch. Pflichtvalidierung:

```bash
mvn test
./bin/export.sh full --zip
./bin/export.sh --full-parts baseline --zip
```

## Standard interpretation since 000051

Patch `000051_springmaster_domain_entity_persistence_standard` documents how this basic persistence slice is to be used by future reference implementations.

The existing `DomainEntity` remains a minimal `@MappedSuperclass` foundation with opaque string `id`, `persistenceVersion`, tags and audit fields. It is not a complete persistence framework and it does not imply KeyValuePair metadata persistence, NumberSequence support, soft-delete behavior, reusable repository base interfaces or a separate internal surrogate database ID.

Catalog-demo must make these decisions explicit before its first persistent `CatalogItem` slice becomes canonical.


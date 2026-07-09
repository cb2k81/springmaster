# Core DTO/List/Metadata Foundation

## Zweck

Patch `000039_springmaster_core_dto_list_metadata_foundation` ist der erste Java-Code-Slice nach der forensischen Trennung von Springmaster und IDM.

Der Slice übernimmt ausschließlich fachfreie, gemeinsam nutzbare DTO-, Paging- und Metadata-Vertragsbausteine aus dem IDM-Alt-Core in den Springmaster-Core unter `de.cocondo.system`.

## Architekturgrenze

Dieser Slice ist bewusst ein Contract-/Support-Slice. Er enthält keine persistenznahen Metadata-Entities, keine Repositories, keine Security, keine HTTP-Fehlerbehandlung und keine Zielprojektänderung.

## Enthaltene Runtime-Dateien

```text
src/main/java/de/cocondo/system/dto/DomainEntityDTO.java
src/main/java/de/cocondo/system/dto/DomainEntityInboundDTO.java
src/main/java/de/cocondo/system/dto/DomainEntityMetadataDTO.java
src/main/java/de/cocondo/system/dto/DomainEntityUpdateDTO.java
src/main/java/de/cocondo/system/dto/PagedResponseDTO.java
src/main/java/de/cocondo/system/entity/metadata/KeyValuePairDTO.java
src/main/java/de/cocondo/system/entity/metadata/KeyValuePairPayload.java
src/main/java/de/cocondo/system/list/PagedQuerySupport.java
src/main/java/de/cocondo/system/list/PagedResponseFactory.java
src/main/java/de/cocondo/system/mapper/DomainMetadataSupportMapper.java
```

## Enthaltene Tests

```text
src/test/java/de/cocondo/system/dto/CoreDtoMarkerTypesTest.java
src/test/java/de/cocondo/system/entity/metadata/CoreMetadataDtoTypesTest.java
src/test/java/de/cocondo/system/list/PagedQuerySupportTest.java
src/test/java/de/cocondo/system/list/PagedResponseFactoryTest.java
src/test/java/de/cocondo/system/mapper/DomainMetadataSupportMapperTest.java
```

## Dependency-Entscheidung

`PagedQuerySupport` und `PagedResponseFactory` verwenden bewusst Spring-Data-Commons-Typen:

```text
org.springframework.data.domain.Sort
org.springframework.data.domain.Page
```

Deshalb ergänzt der Patch `pom.xml` um:

```xml
<dependency>
    <groupId>org.springframework.data</groupId>
    <artifactId>spring-data-commons</artifactId>
</dependency>
```

Es wird bewusst **nicht** `spring-boot-starter-data-jpa` eingeführt. Repository-, Entity-Manager-, DataSource- und Liquibase-Themen bleiben späteren persistenznahen Slices vorbehalten.

## Lombok-Entscheidung

Die IDM-Vorlage nutzt in mehreren DTOs Lombok. Springmaster übernimmt die Konzepte, aber nicht die Lombok-Abhängigkeit.

Die neuen Core-DTOs verwenden explizite Getter/Setter. Damit bleibt der Springmaster-Core dependency-arm und Zielprojekte müssen wegen dieses Slices keine Lombok-Policy übernehmen.

## Metadata-Entscheidung

Der Slice enthält nur:

```text
KeyValuePairDTO
KeyValuePairPayload
DomainMetadataSupportMapper
```

Nicht enthalten sind:

```text
KeyValuePair
KeyValueService
TagService
AbstractMetadataDomainService
```

Grund: Diese Klassen sind persistenznah oder serviceorientiert und benötigen eine eigene JPA-/Repository-/Schemaentscheidung.

`DomainMetadataSupportMapper` bildet in diesem Slice die stabilen Basismetadata-Felder einer `DomainEntity` ab:

```text
id
createdBy
createdAt
lastModifiedBy
lastModifiedAt
tags
```

Key-Value-Mapping ist als Erweiterungspunkt über `toKeyValuePairDtos(DomainEntity entity)` vorbereitet, wird aber erst mit dem späteren persistenznahen Metadata-Slice vollständig angebunden.

## Zielprojekt-Relevanz für IDM

Dieser Slice deckt die höchste externe Nutzung aus dem IDM-Alt-Core ab:

```text
PagedResponseDTO
PagedQuerySupport
PagedResponseFactory
```

Diese Typen werden im IDM-Fachcode mehrfach direkt verwendet und sind Voraussetzung, bevor IDM-Imports später von `de.cocondo.app.system.*` auf `de.cocondo.system.*` migriert werden können.

## Nicht enthalten

```text
Security/JWT
HTTP/Web-Konfiguration
Event-Persistenz
Repositories
Liquibase-/Schemaänderungen
IDM-Zielprojektänderungen
Löschung von de.cocondo.app.system/**
```

## DoD

Der Patch ist erst abgeschlossen, wenn:

```text
mvn test
```

im Springmaster-Projekt erfolgreich ist und danach ein sauberer Full-ZIP-Export erzeugt wurde.


## Query support maturity addendum 000093

Patch `000093_springmaster_paged_query_support_sort_allowlist_tiebreaker` extends `PagedQuerySupport` from page-size and sort-direction validation to the reusable Core boundary for deterministic list sorting.

The support class now provides fachfreie helpers for:

```text
resolveSortBy(sortBy, allowedSortFields, defaultSortBy)
stableSort(sortBy, sortDir, allowedSortFields, defaultSortBy, tieBreakerSortBy)
stableComparator(sortBy, sortDir, allowedComparators, defaultSortBy, tieBreakerComparator)
```

The Core still does not know any fachliche field. Fachmodule or generated service slices must pass their own public sort allow-list, default sort and stable tie-breaker. Unsupported public sort fields remain request errors and must surface through the API error contract as `400 Bad Request` at the HTTP boundary.

The stable tie-breaker is intentionally explicit. Paged and `/all` result sets must not depend only on a non-unique business column such as `name` or `status`, because repeated page reads can otherwise drift when multiple rows have the same primary sort value.

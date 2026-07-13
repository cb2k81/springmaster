# Core Query Operations Interface Contract

## Zweck

Patch `000101_springmaster_query_operations_interface_contract_core` ergänzt den Springmaster-Core um eine fachfreie Java-Vertragsfläche für kanonische Query-Operationen.

Der Contract unterstützt generierte und manuell implementierte Service-Slices dabei, die drei Standard-Query-Operationen typisiert abzubilden:

```text
paged list
complete result set / all
count-only
```

## Architekturgrenze

Der Core definiert bewusst **keine generischen Spring-MVC-Controller-Interfaces**.

Nicht Teil dieses Core-Slices sind:

```text
@RequestMapping
@GetMapping
URL-Pfade
OpenAPI Operation IDs
Security-Annotationen
fachliche Filterfelder
Persistence-/Repository-Regeln
HTTP-Fehlerbehandlung
```

Diese Aspekte bleiben Aufgabe des jeweiligen Fachmoduls beziehungsweise der generierten Slice-Schicht.

Der Core stellt nur die typsichere Service-/Application-Vertragsfläche bereit.

## Runtime-Dateien

```text
src/main/java/de/cocondo/system/query/PagedResultSetQuery.java
src/main/java/de/cocondo/system/query/CompleteResultSetQuery.java
src/main/java/de/cocondo/system/query/CountResultSetQuery.java
src/main/java/de/cocondo/system/query/ResultSetQueryOperations.java
```

## Operationen

### PagedResultSetQuery

```java
PagedResponseDTO<T> listPaged(Q query);
```

Der konkrete Query-Typ `Q` gehört dem Fachslice. Er kapselt zum Beispiel `page`, `size`, Filter und Sortierung.

### CompleteResultSetQuery

```java
List<T> listAll(Q query);
```

Der konkrete Query-Typ `Q` gehört dem Fachslice. Er kapselt die für `/all` erlaubten Filter- und Sortierparameter.

### CountResultSetQuery

```java
CountResponseDTO count(Q query);
```

Der konkrete Query-Typ `Q` gehört dem Fachslice. Er kapselt ausschließlich die Count-relevanten Kriterien. HTTP-seitig bleiben Paging- und Sortierparameter auf Count-only-Endpunkten nicht semantisch relevant.

### ResultSetQueryOperations

```java
ResultSetQueryOperations<P, A, C, T>
```

Der Composite-Contract bündelt:

```text
PagedResultSetQuery<P, T>
CompleteResultSetQuery<A, T>
CountResultSetQuery<C>
```

Damit können Fachservices oder generierte Application Services den vollständigen Query-Operations-Contract implementieren, ohne Controller-Mapping oder fachliche Parameter in den Core zu verlagern.

## DoD

Der Patch ist erst abgeschlossen, wenn:

```text
mvn -Dtest=ResultSetQueryOperationsTest test
mvn test
./bin/export.sh full --zip
```

erfolgreich abgeschlossen sind.

## CatalogItem reference adoption

Patch `000102_springmaster_catalogitem_query_operations_interface_adoption` completes the first Demo-scope adoption. `CatalogItemService` implements `ResultSetQueryOperations<CatalogItemPagedQuery, CatalogItemAllQuery, CatalogItemCountQuery, CatalogItemListItemDTO>`.

The closure review in `000103_springmaster_query_operations_contract_closure_review` records the resulting target pattern:

```text
Controller = explicit Spring MVC adapter
Service    = typed query-operations contract
Query DTOs = fachlicher slice-owned model
Core       = fachfreie interfaces and DTOs
```

Further generated applications should use this contract shape, but strict enforcement remains deferred until gate implementation and canonicalization evidence are explicitly promoted.

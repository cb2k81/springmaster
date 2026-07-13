# CatalogItem Persistent JPA Count Reference Slice

Patch: `000113_springmaster_persistent_jpa_count_reference_slice`

## Ziel

Dieser Patch ergänzt den CatalogItem Candidate Slice um eine persistente JPA-Referenz für Query-Operationen. Die aktuelle Runtime bleibt bewusst weiterhin in-memory. Die neue Referenzklasse zeigt aber deterministisch, wie generierte oder spätere persistente Slices `list`, `/all` und `/count` gegen eine JPA-Persistenzschicht implementieren müssen.

## Referenzklasse

```text
src/main/java/de/cocondo/platform/demo/catalog/CatalogItemJpaQueryReference.java
```

Die Klasse ist nicht als Spring Bean registriert und ersetzt den bestehenden `CatalogItemService` nicht. Sie dient als kompakte, kompilierbare Referenz für die spätere Repository-/Persistence-Schicht.

## Abgedeckte Operationen

| Operation | Methode | Persistenzsemantik |
|---|---|---|
| paged list | `listPaged(EntityManager, CatalogItemPagedQuery)` | Datenquery mit Filter, Sortierung, stabilem Tie-Breaker, `setFirstResult`, `setMaxResults` und separater Count Query für `totalElements` |
| complete result set | `listAll(EntityManager, CatalogItemAllQuery)` | Datenquery mit Filter, Sortierung und stabilem Tie-Breaker ohne Paging |
| count-only | `count(EntityManager, CatalogItemCountQuery)` | dedizierte `CriteriaQuery<Long>` mit `cb.count(root)` und gleicher Filterfamilie |

## Verbindliche Count-Regeln

Die Count-Implementierung muss:

* eine eigene `CriteriaQuery<Long>` verwenden;
* `cb.count(root)` verwenden;
* dieselbe Predicate-Familie wie paged list und `/all` verwenden;
* keine DTOs mappen;
* keine Entity-Liste materialisieren;
* kein `listAll(...).size()` verwenden;
* kein `getResultList().size()` verwenden;
* keine Sortierung ausführen;
* kein `setFirstResult` und kein `setMaxResults` setzen.

## Predicate-Parität

Die JPA-Referenz nutzt eine gemeinsame Predicate-Familie:

```text
filterPredicates(root, cb, sku, name)
```

Diese Predicate-Familie wird von Datenqueries und Count Query verwendet. Damit wird die fachliche Parität zwischen paged list, `/all` und `/count` sichtbar.

## Sortierung und Tie-Breaker

Die Datenqueries verwenden dieselbe Sort-Allowlist wie der bestehende In-Memory-Service:

```text
sku
name
```

Die stabile Sortierung ergänzt immer `id` als technischen Tie-Breaker. Count Queries enthalten keine Sortierung.

## Tests

```text
src/test/java/de/cocondo/platform/demo/catalog/CatalogItemJpaQueryReferenceTest.java
```

Die Tests prüfen die Referenzstruktur source-basiert:

* dedizierte Criteria Count Query;
* gemeinsame Predicate-Familie;
* keine Materialisierung für Count;
* keine Paging-/Sort-Semantik in Count;
* Paging-/Sort-Semantik nur in Datenqueries.

## Abgrenzung

Dieser Patch macht den CatalogItem Slice noch nicht canonical. Es fehlt weiterhin Security-/Data-Scope-Parität und eine explizite Canonical-Promotion. Die bestehende Anwendung bleibt in-memory, damit keine implizite Datenbankpflicht für das Springmaster Demo-Runtime-Verhalten entsteht.

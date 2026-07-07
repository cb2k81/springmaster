# Demo Catalog Basic Domain

## Zweck

Patch `000017_springmaster_demo_catalog_basic_domain` führt die erste minimale Demo-Domäne im Masterprojekt ein.

Ziel ist nicht fachliche Vollständigkeit, sondern der überprüfbare Nachweis, dass Core-Bausteine unter `de.cocondo.system` in einer realen Master-Demo unter `de.cocondo.platform.demo` genutzt werden können.

## Paketstruktur

```text
src/main/java/de/cocondo/platform/demo/catalog/**
src/test/java/de/cocondo/platform/demo/catalog/**
```

## Enthaltene Bausteine

| Baustein | Zweck |
|---|---|
| `CatalogItem` | minimale Demo-Domain-Klasse auf Basis von `DomainEntity` |
| `CatalogItemCreateDTO` | einfacher Create-Payload mit `DataTransferObject` |
| `CatalogItemDTO` | einfacher Output-DTO mit `DTO` |
| `CatalogItemMapper` | deterministisches Mapping zwischen Payload, Domain und DTO |
| `CatalogItemValidator` | Nutzung des Core-Validation-Contracts |
| `CatalogItemService` | Spring-gescannter In-Memory-Service für Demo-Use-Cases |

## Genutzte Core-Bausteine

```text
de.cocondo.system.entity.DomainEntity
de.cocondo.system.entity.Range
de.cocondo.system.entity.validation.Validator
de.cocondo.system.entity.validation.ValidationException
de.cocondo.system.dto.DTO
de.cocondo.system.dto.DataTransferObject
de.cocondo.system.exception.EntityAlreadyExistsException
```

## Bewusste Abgrenzung

Nicht enthalten sind:

* Spring-Data-JPA-Repositories
* DataSource-Konfiguration
* Liquibase-Demo-Changesets
* REST-Controller
* OpenAPI-spezifische Demo-Kontrakte
* Zielprojekt-Update-Mechanik

Diese Punkte bleiben späteren, klein geschnittenen Patches vorbehalten.

## Validierung

Der Patch ist ein Code-Patch und muss mit `mvn test` validiert werden.

Die Tests prüfen:

* Domain-Verhalten von `CatalogItem`
* Validator-Regeln
* Mapping
* In-Memory-Service-Verhalten
* Spring-Component-Scan für den Demo-Service

## Validierungsfix 000019

Die erste Anwendung von `000017` hat gezeigt, dass der Dateistand vollständig angewendet war, die Maven-Pflichtvalidierung aber nicht grün war.

Korrigiert wurden:

* `CatalogItemServiceSpringContextTest` lädt `SpringmasterApplication` explizit, weil Demo-Tests nicht unterhalb des App-Pakets liegen.
* `CatalogItemService` verwendet in der Duplicate-Fehlermeldung den fachlichen Begriff `SKU`.

Die Patchnummer `000018` ist im lokalen Patch-Archiv bereits durch eine unveränderte Wiederanwendung des `000017`-Archivs belegt; der eigentliche Fix erfolgt deshalb deterministisch als `000019`.

Damit bleibt die Demo weiterhin ohne Spring-Data-JPA, DataSource-Konfiguration und Liquibase-Demo-Tabellen.

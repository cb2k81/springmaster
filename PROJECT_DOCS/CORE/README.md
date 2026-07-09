# Platform Core

Der Platform Core enthält künftig fachfreie, wiederverwendbare Java-Bausteine für Cocondo-Backend-Projekte.

## Aktueller Stand

* Bootstrap- und Tooling-Fundament sind vorhanden.
* Ein Project Skeleton kann über `bin/project-new.sh` erzeugt werden.
* IDM-System-Core-Dateien sind klassifiziert, aber noch nicht als Java-Code migriert.
* Die Core-Namespace-Strategie ist festgelegt: Core-Code wird im Master und in Zielprojekten unter `de.cocondo.system` geführt.

## Verbindliche Referenzen

* `PROJECT_DOCS/CORE/CORE_NAMESPACE_STRATEGY.md`
* `PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_CLASSIFICATION.md`
* `PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_CLASSIFICATION.json`
* `PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.md`
* `PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.json`
* `PROJECT_DOCS/CORE/CORE_MIGRATION_RULES.md`

## Grundregel

Kein IDM-Fachcode wird in den Platform Core übernommen. Jede Core-Übernahme muss paketkonform, dependency-bewusst und mit Tests erfolgen.

Springmaster-spezifischer App- und Demo-Code bleibt unter `de.cocondo.platform.*`. Wiederverwendbarer Core-Code liegt unter `de.cocondo.system`.

## Patch 000010: Core Basic Types Foundation

Der erste Core-Code-Slice übernimmt ausschließlich fachfreie, dependency-arme Basistypen unter dem kanonischen Package `de.cocondo.system`.

Enthalten sind:

- DTO-Marker (`DTO`, `DataTransferObject`)
- leeres Inbound-Metadata-DTO als späterer Erweiterungspunkt
- Entity-Marker (`Identifyable`, `Taggable`)
- Validierungsbasis (`Validator`, `ValidationException`)
- Basisausnahme (`EntityAlreadyExistsException`)
- ID-Generator-Contract (`IdGeneratorService`)

Bewusst nicht enthalten sind JPA-, Lombok-, Web-, Event-, Security- oder JWT-Bausteine. Diese bleiben separaten Core-Slices vorbehalten.

## Patch 000011: App Scan Alignment

Die Springmaster-Anwendung scannt ab Patch `000011` sowohl den Master-/Demo-Namespace `de.cocondo.platform` als auch den wiederverwendbaren Core-Namespace `de.cocondo.system`.

Diese Ausrichtung ist erforderlich, bevor spätere Core-Slices Spring-Komponenten, Konfigurationen oder Infrastruktur-Beans enthalten dürfen. Das Project Skeleton verwendet dieselbe Regel für neu erzeugte Anwendungen: App-spezifischer Code wird über das jeweilige Projekt-Basispaket gescannt, der verteilbare Core über `de.cocondo.system`.


## Patch 000012: Core Persistence Preparation

Patch `000012` ergänzt die minimale Jakarta-Persistence-API-Abhängigkeit und erlaubt dem Core-Scope bei begründeten Core-Dependency-Änderungen auch `pom.xml`.

Dieser Schritt migriert noch keine JPA-Entities. Er verhindert, dass der nächste persistenznahe Core-Code-Slice gleichzeitig Package-, Dependency- und Entity-Entscheidungen vermischt.

Bewusst nicht aktiviert werden `spring-boot-starter-data-jpa`, Repository-Infrastruktur, DataSource-Konfiguration oder Liquibase-Änderungen.

## Persistence Basic Types

Der erste persistenznahe Core-Slice liegt seit `000015_springmaster_core_persistence_basic_types` unter `de.cocondo.system`.

Siehe:

```text
PROJECT_DOCS/CORE/CORE_PERSISTENCE_BASIC_TYPES.md
```

Der Slice ergänzt JPA-nahe Basistypen ohne Repository-Schicht, ohne DataSource-Konfiguration und ohne Liquibase-Änderung.

## Patch 000038: IDM System Core Gap Inventory

Patch `000038_springmaster_core_idm_system_gap_inventory` ist eine reine Analyse-/Dokumentationsstufe nach der Platform-Update-Prozesshärtung.

Der Befund nach `000037`:

- IDM behält den Springmaster-Core unter `de.cocondo.system` als Zielbild.
- Core-Tests gehören zum übertragenen Core.
- Die pauschal nach IDM übertragene Master-Core-Dokumentation soll später durch eine kurze IDM-Integrationsdoku ersetzt werden.
- Der alte IDM-Core unter `de.cocondo.app.system` soll früh entfernt werden, aber erst nach vollständiger Feature-/Klassenabdeckung im Springmaster-Core und erfolgreicher Importmigration.

Die verbindliche Gap-Inventarisierung steht in:

```text
PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.md
PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.json
```

Der nächste zulässige Code-Slice ist `000039_springmaster_core_dto_list_metadata_foundation`.

## Patch 000039: Core DTO/List/Metadata Foundation

Patch `000039_springmaster_core_dto_list_metadata_foundation` übernimmt den ersten fehlenden gemeinsamen Core-Code-Slice aus der IDM-Gap-Inventarisierung.

Enthalten sind DTO-, Paging- und Metadata-Vertragsbausteine unter `de.cocondo.system`:

```text
src/main/java/de/cocondo/system/dto/**
src/main/java/de/cocondo/system/list/**
src/main/java/de/cocondo/system/entity/metadata/*DTO.java
src/main/java/de/cocondo/system/entity/metadata/*Payload.java
src/main/java/de/cocondo/system/mapper/**
```

Nicht enthalten sind persistenznahe Metadata-Entities/Services, Repositories, Security, HTTP/Web-Konfiguration, Event-Persistenz, Liquibase-Änderungen oder IDM-Zielprojektänderungen.

Siehe:

```text
PROJECT_DOCS/CORE/CORE_DTO_LIST_METADATA_FOUNDATION.md
```


## Patch 000040: Core ID Generator Implementation

Patch `000040_springmaster_core_id_generator_implementation` ergänzt den bestehenden Core-Vertrag `IdGeneratorService` um die konkrete UUID-basierte Standardimplementierung `UuidIdGeneratorService`.

Der Slice ist bewusst risikoarm: Er enthält keine IDM-Fachlogik, keine Persistenz, keine Repositories, keine Security und keine HTTP/Web-Konfiguration. Die Implementierung liegt unter `de.cocondo.system.core.id` und ist als Spring `@Service` registrierbar.

Siehe:

```text
PROJECT_DOCS/CORE/CORE_ID_GENERATOR_IMPLEMENTATION.md
```

## Patch 000041: Core Entity/Service/Sequence Inventory

Patch `000041_springmaster_core_entity_service_sequence_inventory` ist eine reine Analyse-/Dokumentationsstufe für den persistenznahen Slice `core-entity-service-and-sequence`.

Der Patch übernimmt keinen Java-Code. Er trennt den Slice in risikoarme Service-Unterstützung, später zu entscheidende Metadata-Persistenz und einen separaten NumberSequence-Slice.

Siehe:

```text
PROJECT_DOCS/CORE/CORE_ENTITY_SERVICE_SEQUENCE_INVENTORY.md
```

Der nächste zulässige Code-Slice ist `000042_springmaster_core_domain_entity_service_support`.


## Patch 000042: Core Domain Entity Service Support

Patch `000042_springmaster_core_domain_entity_service_support` ergänzt den Springmaster-Core um risikoarmen Service-Support für `DomainEntity` und Tags.

Enthalten sind `DomainEntityService` und `TagService` unter `de.cocondo.system.entity.service`. Der Slice ändert kein Persistenzmodell und übernimmt weder KeyValuePair-Persistenz noch NumberSequence.

Siehe:

```text
PROJECT_DOCS/CORE/CORE_DOMAIN_ENTITY_SERVICE_SUPPORT.md
```

## Domain Entity and Persistence Standard since 000051

Patch `000051_springmaster_domain_entity_persistence_standard` adds the master-level persistence standard under `PROJECT_DOCS/STANDARDS/DOMAIN_ENTITY_PERSISTENCE_STANDARD.md`.

The standard clarifies how the existing Core persistence foundation is to be interpreted before Catalog-demo becomes canonical:

* Core `DomainEntity` is the current `@MappedSuperclass` foundation.
* `id` is an opaque string identifier and must not carry business semantics.
* Business keys such as SKU, number or code are explicit domain fields.
* `persistenceVersion` is the current optimistic-locking field.
* repositories remain application/domain persistence adapters and are not exposed through controllers.
* persistent metadata, NumberSequence, soft delete, audit-current-user propagation and reusable repository base interfaces remain deferred until dedicated ADRs or code patches resolve them.


## Core Distribution Readiness seit 000077

Patch `000077_springmaster_generated_service_slice_readiness_plan` hält fest, dass neue Backend-Skeletons den Core-Namespace `de.cocondo.system` bereits scannen, den Core-Code aber noch nicht automatisch enthalten.

Vor einem generated service slice muss deshalb entschieden werden, wie der benötigte Core in ein neu erzeugtes Projekt gelangt:

* kurzfristig als deterministische Source-Core-Kopie per Patch,
* später eventuell als versioniertes Maven-Artefakt,
* nicht als implizite Vermischung mit Springmaster-App- oder Demo-Code.

Diese Entscheidung ist Voraussetzung, bevor ein generierter fachlicher Slice Core-Typen verbindlich voraussetzt.


## Patch 000093: Paged Query Support Sort Allowlist and Tie-Breaker

Patch `000093_springmaster_paged_query_support_sort_allowlist_tiebreaker` matures `PagedQuerySupport` as the fachfreie Core helper for deterministic management-list sorting.

It keeps fachliche field definitions outside Core. Callers provide the public sort allow-list, default sort and stable tie-breaker; Core validates and composes the query mechanics for Spring Data `Sort` or in-memory `Comparator` use.

See:

```text
PROJECT_DOCS/CORE/CORE_DTO_LIST_METADATA_FOUNDATION.md
```

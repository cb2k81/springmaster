# Core Persistence Preparation

## Zweck

Dieser Schritt bereitet die spätere Übernahme persistenznaher Core-Bausteine aus dem IDM-Referenzstand vor, ohne bereits JPA-Entities oder Repositories zu migrieren.

## Entscheidung

Der verteilbare Core soll JPA-Annotationen verwenden dürfen, ohne die Springmaster-Anwendung oder neu erzeugte Projekte sofort zur vollständigen Spring-Data-JPA-Anwendung zu machen.

Daher wird zunächst ausschließlich die API-Abhängigkeit ergänzt:

```xml
<dependency>
    <groupId>jakarta.persistence</groupId>
    <artifactId>jakarta.persistence-api</artifactId>
</dependency>
```

Bewusst nicht ergänzt wird in diesem Schritt:

* `spring-boot-starter-data-jpa`
* eine DataSource-Konfiguration
* eine Repository-Schicht
* ein Liquibase-Changeset
* eine Hibernate-spezifische Runtime-Anforderung

## Begründung

Persistenznahe Basistypen wie `@MappedSuperclass`, `@PrePersist`, `@PreUpdate`, `@Id`, `@Version` oder `@Embeddable` benötigen zur Kompilierung die Jakarta-Persistence-API. Für die bloße Definition solcher fachfreien Core-Typen ist jedoch noch keine vollständige JPA-Runtime erforderlich.

Damit bleibt der Master in dieser Phase weiterhin leichtgewichtig start- und testbar. Zielprojekte oder spätere Demo-Domänen können zusätzlich Spring Data JPA aktivieren, sobald echte Entities, Repositories und Datenbanktests eingeführt werden.

## Patch-Scope-Regel

Der Patch-Scope `core` darf ab diesem Schritt zusätzlich `pom.xml` enthalten, wenn eine Dependency-Änderung unmittelbar für Core-Code erforderlich ist.

Für solche Core-Patches gilt immer die strengere Kategorie `Build-Konfiguration` beziehungsweise `Java-Code + Build-Konfiguration`:

* `mvn test` ist Pflicht.
* Die Dependency-Änderung muss im Core-Kontext begründet sein.
* Es dürfen keine fachlichen App-Dependencies eingeschleppt werden.

## Nächster Schritt

Der nächste Core-Code-Slice kann nun JPA-nahe, aber weiterhin fachfreie Typen unter `de.cocondo.system` ergänzen.

Geplanter Folgeumfang:

* `Auditable`
* `AuditingEntityListener`
* `DomainEntityListener`
* eine schlanke `DomainEntity`-Basisklasse oder ein gleichwertiger abstrahierter Persistenz-Basistyp
* direkte Unit-Tests für Listener- und ID-Fallback-Verhalten

Nicht im Folgeumfang:

* Key-Value-Metadata-Komposition
* Repositories
* Spring Data JPA Runtime
* Demo-Domain
* Datenbank-Migration

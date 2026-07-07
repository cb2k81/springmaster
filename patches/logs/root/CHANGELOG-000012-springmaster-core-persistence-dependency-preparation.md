# Changelog – 000012 springmaster core persistence dependency preparation

## Typ

Build-/Tooling-/Core-Preparation-Patch.

## Änderungen

* ergänzt `jakarta.persistence-api` als minimale Compile-Abhängigkeit
* erweitert den Patch-Scope `core` um `pom.xml` für begründete Core-Dependency-Änderungen
* dokumentiert die Persistence-Preparation ohne Spring-Data-JPA-Runtime-Aktivierung
* aktualisiert Core-, Patchsystem-, Validierungs- und Planungsdokumentation

## Nicht enthalten

* keine Java-Code-Migration
* keine JPA-Entity-Übernahme
* keine Repository-Schicht
* keine Liquibase-Änderung
* keine DataSource-Konfiguration

## Validierung

Da `pom.xml` geändert wird, ist `mvn test` Pflicht.

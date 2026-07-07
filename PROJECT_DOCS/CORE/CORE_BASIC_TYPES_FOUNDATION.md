# Core Basic Types Foundation

## Zweck

Dieser Schritt etabliert den ersten ausführbaren Springmaster-Core-Slice unter dem kanonischen Namespace:

```text
de.cocondo.system
```

Der Slice ist bewusst klein und dependency-arm. Er dient als erste technische Verifikation, dass Core-Code im Master unter demselben Package liegt, das später auch in Zielprojekten verwendet wird.

## Enthaltene Klassen

```text
src/main/java/de/cocondo/system/dto/DTO.java
src/main/java/de/cocondo/system/dto/DataTransferObject.java
src/main/java/de/cocondo/system/dto/DomainEntityMetadataInboundDTO.java
src/main/java/de/cocondo/system/entity/Identifyable.java
src/main/java/de/cocondo/system/entity/Taggable.java
src/main/java/de/cocondo/system/entity/validation/ValidationException.java
src/main/java/de/cocondo/system/entity/validation/Validator.java
src/main/java/de/cocondo/system/exception/EntityAlreadyExistsException.java
src/main/java/de/cocondo/system/core/id/IdGeneratorService.java
```

## Herkunft

Die Klassen basieren auf den gleichnamigen IDM-System-Core-Klassen aus `de.cocondo.app.system`.

Die deterministische Transformation dieses Slices lautet:

```text
de.cocondo.app.system -> de.cocondo.system
```

Weitere fachliche oder technische Refactorings wurden in diesem Slice nicht vorgenommen.

## Bewusste Abgrenzung

Nicht enthalten sind:

- JPA-/Persistence-Typen
- Lombok-basierte DTOs
- Web-/Controller-Infrastruktur
- Event-Infrastruktur
- Security-/JWT-Infrastruktur
- Spring-Komponenten, die Component-Scan-Entscheidungen erzwingen würden

Diese Gruppen werden in späteren, separat validierten Slices behandelt.

## Verifikation

Dieser Patch ist ein Code-Patch. Daher sind verpflichtend:

```bash
mvn test
```

Zusätzlich validieren dedizierte Tests:

- DTO-Marker
- Entity-Marker
- Validierungscontract
- Basisausnahme
- ID-Generator-Contract

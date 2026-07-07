# Core ID Generator Implementation

## Zweck

Patch `000040_springmaster_core_id_generator_implementation` ergänzt den bestehenden Core-Vertrag `IdGeneratorService` um die konkrete UUID-basierte Standardimplementierung `UuidIdGeneratorService`.

Der Slice ist bewusst klein und risikoarm. Er übernimmt nur die fachfreie technische ID-Generator-Implementierung aus dem IDM-System-Core in den Springmaster-Core unter dem kanonischen Package `de.cocondo.system`.

## Enthaltene Dateien

```text
src/main/java/de/cocondo/system/core/id/UuidIdGeneratorService.java
src/test/java/de/cocondo/system/core/id/UuidIdGeneratorServiceTest.java
```

## Laufzeitverhalten

`UuidIdGeneratorService`:

- implementiert `IdGeneratorService`,
- erzeugt IDs über `UUID.randomUUID().toString()`,
- ist als Spring `@Service` registrierbar,
- enthält keine IDM-Fachlogik,
- enthält keine Repository-, Persistence-, Security-, HTTP- oder Event-Abhängigkeiten.

## Zielarchitektur

Die Implementierung ist Teil des gemeinsamen Springmaster-Core und darf in Zielprojekte übertragen werden.

Zielpfad in Master und Zielprojekten:

```text
de.cocondo.system.core.id
```

Der alte IDM-Pfad bleibt bis zur späteren IDM-Importmigration nur Übergang:

```text
de.cocondo.app.system.core.id
```

## Abgrenzung

Nicht Bestandteil dieses Slices:

- IDM-Zielprojektänderung,
- IDM-Importmigration,
- Entfernung von `de.cocondo.app.system/**`,
- Nummernkreise oder Sequenzgeneratoren,
- Datenbankpersistenz,
- Repositories,
- Liquibase-/Schemaänderungen,
- Security/JWT,
- HTTP/Web-Konfiguration.

## Validierung

Der Slice muss mit folgenden Gates validiert werden:

```bash
mvn test
python3 -m json.tool PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.json >/dev/null
./bin/export.sh full --zip
```

Zusätzlich darf der Springmaster-Core keine Imports auf `de.cocondo.app.*` oder Lombok enthalten.

## Folgearbeit

Nach diesem Patch ist der Gap-Slice `core-id-implementation` in Springmaster abgedeckt.

Der nächste größere Slice ist voraussichtlich:

```text
000041_springmaster_core_entity_service_sequence_inventory
```

Dieser muss gesondert geplant werden, weil er persistenznähere Services, Nummernkreise und Repository-/Schema-Fragen berührt.

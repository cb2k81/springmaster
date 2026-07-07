# IDM System Core Gap Inventory

## Zweck

Dieses Dokument ist die verbindliche Gap-Inventarisierung nach den Patches `000034` bis `000037`.
Es beschreibt, was zwischen dem IDM-Alt-Core unter `de.cocondo.app.system` und dem Springmaster-Core unter `de.cocondo.system` noch fehlt.

Dieser Patch ist **analyse- und dokumentations-only**. Er übernimmt keinen Java-Code, erzeugt keine Zielpatches und verändert kein Zielprojekt.

## Architekturentscheidungen für diese Analyse

| Entscheidung | Festlegung |
|---|---|
| Springmaster-Core in IDM | Der Springmaster-Core bleibt Zielbild und muss im IDM funktionsfähig gemacht werden. |
| Core-Tests | Core-Tests gehören zum Core und reisen mit dem Core in Zielprojekte. |
| IDM `PROJECT_DOCS/CORE/**` | Die pauschal übertragene Master-Core-Dokumentation wird später durch eine kurze IDM-Integrationsdoku ersetzt. |
| Alter IDM-Core `de.cocondo.app.system` | Wird so früh wie möglich entfernt, aber erst nach vollständiger Feature-/Klassenabdeckung und erfolgreicher Importmigration. |
| Generierte Zielartefakte | Bleiben temporär unter `build/platform-update/**` und sind aus regulären Exports ausgeschlossen. |

## Eingaben

| Quelle | Wert |
|---|---|
| Springmaster-Baseline | `000042_springmaster_core_domain_entity_service_support` |
| IDM-Gegenprobe | `idm.zip` nach angewendetem Compatibility-/Core-Zielpatch |
| IDM-Alt-Core | `src/main/java/de/cocondo/app/system/**` |
| Springmaster-Core | `src/main/java/de/cocondo/system/**` |
| Zielpackage | `de.cocondo.system` |

## Gesamtergebnis

| Kennzahl | Ergebnis |
|---|---:|
| IDM-Alt-Core-Dateien unter `de.cocondo.app.system` | 73 |
| Springmaster-Core-Dateien unter `de.cocondo.system` | 27 |
| In IDM bereits importierte Springmaster-Core-Dateien | 14 |
| Bereits im Springmaster-Core abgedeckte Alt-Core-Dateien | 27 |
| Noch fehlende Alt-Core-Dateien im Springmaster-Core | 46 |
| IDM-Alt-Core-Testdateien | 1 |
| Springmaster-Core-Testdateien | 16 |
| In IDM bereits importierte Springmaster-Core-Testdateien | 9 |
| Externe Imports auf `de.cocondo.app.system.*` | 6 Symbols |

## Paketübersicht des IDM-Alt-Core

| Paketgruppe | Dateien |
|---|---:|
| `config` | 3 |
| `core/http` | 7 |
| `core/id` | 2 |
| `core/locale` | 1 |
| `core/util` | 1 |
| `dto` | 8 |
| `entity` | 8 |
| `entity/metadata` | 6 |
| `entity/sequence` | 3 |
| `entity/validation` | 2 |
| `event` | 10 |
| `exception` | 1 |
| `info` | 5 |
| `list` | 2 |
| `mapper` | 1 |
| `security/authorization` | 3 |
| `security/config` | 5 |
| `security/http` | 2 |
| `security/jwt` | 2 |
| `swagger` | 1 |

## Gap-Slices

| Slice | Dateien | Risiko | Entscheidung |
|---|---:|---|---|
| `already-in-springmaster-core` | 27 | low | already_available |
| `core-dto-list-metadata-contracts` | 10 | medium | implemented_by_000039 |
| `core-id-implementation` | 1 | low | implemented_by_000040 |
| `core-domain-entity-service-support` | 2 | low | implemented_by_000042 |
| `core-entity-service-and-sequence` | 6 | high | remaining_split_required |
| `core-web-http-error-foundation` | 11 | high | common_core_candidate |
| `core-event-and-audit-foundation` | 11 | high | common_core_candidate |
| `core-application-info` | 5 | medium | common_core_candidate |
| `core-security-jwt-authorization` | 12 | high | common_core_candidate |
| `core-swagger-openapi` | 1 | medium | shared_infrastructure_candidate |

## Bereits im Springmaster-Core vorhanden

Diese Dateien sind bereits unter `de.cocondo.system` vorhanden und wurden in IDM als Springmaster-Core-Payload übernommen. Sie dürfen im Alt-Core erst entfernt werden, wenn die IDM-Imports vollständig umgestellt sind.

- `core/id/IdGeneratorService.java`
- `core/id/UuidIdGeneratorService.java`
- `entity/service/DomainEntityService.java`
- `entity/service/TagService.java`
- `dto/DTO.java`
- `dto/DataTransferObject.java`
- `dto/DomainEntityMetadataInboundDTO.java`
- `entity/Auditable.java`
- `entity/AuditingEntityListener.java`
- `entity/DomainEntity.java`
- `entity/DomainEntityListener.java`
- `entity/Identifyable.java`
- `entity/Range.java`
- `entity/Taggable.java`
- `entity/validation/ValidationException.java`
- `entity/validation/Validator.java`
- `exception/EntityAlreadyExistsException.java`

## Fehlende gemeinsame Core-Kandidaten nach Slice

### `core-dto-list-metadata-contracts`

Mit `000039_springmaster_core_dto_list_metadata_foundation` als Springmaster-Core-Contract-/Support-Slice umgesetzt. Er deckt die höchste externe Nutzung ab: `PagedResponseDTO`, `PagedQuerySupport` und `PagedResponseFactory` werden direkt von IDM-Domain-Handlern und Controllern verwendet. Die IDM-Importmigration erfolgt später separat.

- `dto/DomainEntityDTO.java`
- `dto/DomainEntityInboundDTO.java`
- `dto/DomainEntityMetadataDTO.java`
- `dto/DomainEntityUpdateDTO.java`
- `dto/PagedResponseDTO.java`
- `entity/metadata/KeyValuePairDTO.java`
- `entity/metadata/KeyValuePairPayload.java`
- `list/PagedQuerySupport.java`
- `list/PagedResponseFactory.java`
- `mapper/DomainMetadataSupportMapper.java`

### `core-id-implementation`

Mit `000040_springmaster_core_id_generator_implementation` umgesetzt. Der Slice ergänzt den bestehenden `IdGeneratorService`-Vertrag um die konkrete UUID-basierte Spring-Service-Implementierung. Die IDM-Importmigration erfolgt später separat.

- `core/id/UuidIdGeneratorService.java`
- `entity/service/DomainEntityService.java`
- `entity/service/TagService.java`

### `core-entity-service-and-sequence`

Mit `000041_springmaster_core_entity_service_sequence_inventory` forensisch vertieft. Der Slice wird nicht als Ganzes übernommen. Er wird in drei Folgeschritte getrennt:

1. risikoarme Service-Unterstützung: `DomainEntityService`, `TagService`
2. späteres Metadata-Persistenzmodell: `KeyValuePair`, `KeyValueService`, `AbstractMetadataDomainService`
3. separater NumberSequence-Slice: `NumberSequence`, `NumberSequenceRepository`, `NumberSequenceService`

Begründung: Springmaster führt `DomainEntity` aktuell als `@MappedSuperclass` ohne persistente Key-Value-Assoziation, während IDM `DomainEntity` als `@Entity` mit `@OneToMany keyValuePairs` nutzt. Diese Mapping-Differenz darf nicht implizit in einem Code-Slice aufgelöst werden.

Siehe:

```text
PROJECT_DOCS/CORE/CORE_ENTITY_SERVICE_SEQUENCE_INVENTORY.md
```

- `entity/DomainEntityService.java`
- `entity/metadata/AbstractMetadataDomainService.java`
- `entity/metadata/KeyValuePair.java`
- `entity/metadata/KeyValueService.java`
- `entity/metadata/TagService.java`
- `entity/sequence/NumberSequence.java`
- `entity/sequence/NumberSequenceRepository.java`
- `entity/sequence/NumberSequenceService.java`

### `core-web-http-error-foundation`

Web-/HTTP-/Fehlerbehandlungs-Slice. Nur mit Property-Kompatibilität, Fehlerkontrakt und Zielprojekt-Konfiguration übernehmen.

- `config/DefaultWebConfig.java`
- `config/DefaultWebConfigProperties.java`
- `config/RequestLoggingConfig.java`
- `core/http/DefaultController.java`
- `core/http/DefaultFallbackInterceptor.java`
- `core/http/EndpointPrinter.java`
- `core/http/ErrorResponse.java`
- `core/http/GlobalExceptionHandler.java`
- `core/http/InvalidHttpHeaderException.java`
- `core/http/RequestErrorEvent.java`
- `core/locale/LocalMessageProvider.java`

### `core-event-and-audit-foundation`

Event-/Audit-Slice. Teilweise mit Persistenz, Repositories oder Serialisierung gekoppelt.

- `core/util/serialize/PayloadSerializer.java`
- `event/DomainEvent.java`
- `event/DomainEventEntity.java`
- `event/DomainEventEntityRepository.java`
- `event/DomainEventLoggingListener.java`
- `event/DomainEventSpringShellListener.java`
- `event/ErrorEntity.java`
- `event/ErrorEntityRepository.java`
- `event/ErrorEvent.java`
- `event/ErrorIdService.java`
- `event/EventPublisher.java`

### `core-application-info`

- `info/ApplicationInfoContext.java`
- `info/ApplicationInfoContextDTO.java`
- `info/ApplicationInfoController.java`
- `info/PublicApplicationInfoController.java`
- `info/ServerInfoPrinter.java`

### `core-security-jwt-authorization`

Security/JWT ist ein eigener Architektur-Slice. Die IDM-Domain-Implementierung `IdmDatabasePermissionAuthoritySource` bleibt außerhalb des Core und implementiert nur die Core-Abstraktion `PermissionAuthoritySource`.

- `security/authorization/DatabasePermissionResolver.java`
- `security/authorization/PermissionAuthoritySource.java`
- `security/authorization/PermissionResolver.java`
- `security/config/HttpSecurityConfig.java`
- `security/config/HttpSecurityCorsProperties.java`
- `security/config/HttpSecurityPathsProperties.java`
- `security/config/JwtSecurityProperties.java`
- `security/config/MethodSecurityConfig.java`
- `security/http/RestAccessDeniedHandler.java`
- `security/http/RestAuthenticationEntryPoint.java`
- `security/jwt/JwtAuthenticationFilter.java`
- `security/jwt/JwtService.java`

### `core-swagger-openapi`

- `swagger/SwaggerConfig.java`

## Externe IDM-Imports auf den Alt-Core

Diese Imports verhindern das Entfernen von `de.cocondo.app.system/**`, solange sie nicht auf `de.cocondo.system/**` umgestellt oder bewusst anders klassifiziert wurden.

| Import | Nutzungen | Dateien |
|---|---:|---|
| `de.cocondo.app.system.dto.PagedResponseDTO` | 18 | `src/main/java/de/cocondo/app/domain/idm/assignment/ListApplicationScopesOfUserPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListPermissionsOfRolePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListRolesOfPermissionPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListRolesOfUserInScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListUsersOfApplicationScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListUsersOfRoleInScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/RolePermissionAssignmentController.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/UserApplicationScopeAssignmentController.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/UserRoleAssignmentController.java`<br>`src/main/java/de/cocondo/app/domain/idm/permission/PermissionManagementDomainService.java`<br>`src/main/java/de/cocondo/app/domain/idm/role/ListRolesPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/role/RoleController.java`<br>`src/main/java/de/cocondo/app/domain/idm/role/RoleManagementDomainService.java`<br>`src/main/java/de/cocondo/app/domain/idm/scope/ApplicationScopeController.java`<br>`src/main/java/de/cocondo/app/domain/idm/scope/ListApplicationScopesPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/user/ListUsersPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/user/UserAccountController.java`<br>`src/main/java/de/cocondo/app/domain/idm/user/UserAccountDomainService.java` |
| `de.cocondo.app.system.entity.DomainEntity` | 9 | `src/main/java/de/cocondo/app/domain/idm/assignment/RolePermissionAssignment.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/UserApplicationScopeAssignment.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/UserRoleAssignment.java`<br>`src/main/java/de/cocondo/app/domain/idm/auth/session/AuthSession.java`<br>`src/main/java/de/cocondo/app/domain/idm/permission/Permission.java`<br>`src/main/java/de/cocondo/app/domain/idm/permission/PermissionGroup.java`<br>`src/main/java/de/cocondo/app/domain/idm/role/Role.java`<br>`src/main/java/de/cocondo/app/domain/idm/scope/ApplicationScope.java`<br>`src/main/java/de/cocondo/app/domain/idm/user/UserAccount.java` |
| `de.cocondo.app.system.list.PagedQuerySupport` | 9 | `src/main/java/de/cocondo/app/domain/idm/assignment/ListApplicationScopesOfUserPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListPermissionsOfRolePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListRolesOfPermissionPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListRolesOfUserInScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListUsersOfApplicationScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListUsersOfRoleInScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/role/ListRolesPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/scope/ListApplicationScopesPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/user/ListUsersPagedHandler.java` |
| `de.cocondo.app.system.list.PagedResponseFactory` | 8 | `src/main/java/de/cocondo/app/domain/idm/assignment/ListApplicationScopesOfUserPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListPermissionsOfRolePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListRolesOfPermissionPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListUsersOfApplicationScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/assignment/ListUsersOfRoleInScopePagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/role/ListRolesPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/scope/ListApplicationScopesPagedHandler.java`<br>`src/main/java/de/cocondo/app/domain/idm/user/ListUsersPagedHandler.java` |
| `de.cocondo.app.system.security.authorization.PermissionAuthoritySource` | 1 | `src/main/java/de/cocondo/app/domain/idm/security/IdmDatabasePermissionAuthoritySource.java` |
| `de.cocondo.app.system.security.jwt.JwtService` | 2 | `src/main/java/de/cocondo/app/domain/idm/auth/IdmTokenService.java`<br>`src/test/java/de/cocondo/app/domain/idm/auth/PersonnelLoginBootstrapIntegrationTest.java` |

## Migrationsreihenfolge

Die Entfernung des Alt-Core darf nicht mit einem Löschpatch beginnen. Zuerst muss Springmaster die benötigten Core-Fähigkeiten vollständig bereitstellen.

1. `core-dto-list-metadata-contracts`: Paged-/DTO-/Metadata-Verträge und Factory/Support.
2. `core-id-implementation`: `UuidIdGeneratorService`, Bean-Verhalten und Tests.
3. `core-entity-service-and-sequence`: persistenznahe Services, Nummernkreise und Metadata-Services.
4. `core-web-http-error-foundation`: Web-/HTTP-/Exception-/Locale-Grundlagen.
5. `core-event-and-audit-foundation`: Events, Error-Events, Audit-/Logging-Listener.
6. `core-application-info`: Info-Kontext und Info-Endpoints.
7. `core-security-jwt-authorization`: JWT, Filter, Security-Konfiguration und Permission-Resolver-Abstraktionen.
8. `core-swagger-openapi`: optionaler OpenAPI-/Swagger-Slice.
9. IDM-Importmigration von `de.cocondo.app.system.*` nach `de.cocondo.system.*`.
10. Entfernung von `src/main/java/de/cocondo/app/system/**` und `src/test/java/de/cocondo/app/system/**`, sobald die Gates grün sind.
11. Ersetzen der übertragenen IDM-`PROJECT_DOCS/CORE/**`-Masterdokumente durch eine kurze Zielprojekt-Integrationsdoku.

## Deletion Gate für `de.cocondo.app.system/**`

Vor dem Löschen des Alt-Core müssen alle folgenden Bedingungen erfüllt sein:

- Alle für IDM relevanten gemeinsamen Core-Kandidaten liegen im Springmaster unter `src/main/java/de/cocondo/system/**`.
- IDM-Imports sind von `de.cocondo.app.system.*` auf `de.cocondo.system.*` migriert oder explizit als IDM-Domainadapter klassifiziert.
- `rg "de\.cocondo\.app\.system" src/main/java src/test/java` liefert keine nicht erlaubten Treffer mehr.
- `mvn test` im IDM-Projekt ist grün.
- IDM erzeugt danach einen sauberen Full-ZIP-Export.
- `PROJECT_DOCS/CORE/**` im IDM ist auf eine zielprojektspezifische Integrationsdokumentation reduziert.

## Nächster zulässiger Umsetzungsschritt

Die ersten fehlenden gemeinsamen Core-Slices wurden in Springmaster bereitgestellt:

```text
000039_springmaster_core_dto_list_metadata_foundation
000040_springmaster_core_id_generator_implementation
000042_springmaster_core_domain_entity_service_support
```

Der nächste Schritt darf weiterhin noch nicht im IDM löschen. Nach `000042` sind die risikoarmen Entity-Services umgesetzt; die persistenznahen Reste benötigen weiterhin eine eigene Entscheidung:

```text
000043_springmaster_core_metadata_persistence_model_decision
```

Nicht enthalten im nächsten Planungs-/Code-Slice:

```text
Security/JWT
HTTP/Web-Konfiguration
Event-Persistenz
IDM-Zielprojektänderungen
Löschung von de.cocondo.app.system/**
```

## Maschinenlesbare Inventarisierung

Die vollständige Inventarisierung liegt in:

```text
PROJECT_DOCS/CORE/IDM_SYSTEM_CORE_GAP_INVENTORY.json
```

## Umsetzung seit 000039

Der Slice `core-dto-list-metadata-contracts` wurde mit `000039_springmaster_core_dto_list_metadata_foundation` in Springmaster umgesetzt.

Die Umsetzung ist bewusst auf DTO-, Paging- und Metadata-Vertragsbausteine begrenzt. Persistenznahe Metadata-Entities/Services, Repositories, Sequenzen und Schema-Themen bleiben späteren Slices vorbehalten.

Die IDM-Importmigration ist noch nicht erfolgt und darf erst nach separater Zielprojektplanung mit Review-Gate durchgeführt werden.


## Umsetzung seit 000040

Der Slice `core-id-implementation` wurde mit `000040_springmaster_core_id_generator_implementation` in Springmaster umgesetzt.

Die Umsetzung enthält `UuidIdGeneratorService` als konkrete, fachfreie UUID-basierte Standardimplementierung des bestehenden `IdGeneratorService`-Vertrags.

Die IDM-Importmigration ist noch nicht erfolgt und darf erst nach separater Zielprojektplanung mit Review-Gate durchgeführt werden.

## Vertiefung seit 000041

Patch `000041_springmaster_core_entity_service_sequence_inventory` vertieft den persistenznahen Slice und legt fest, dass die nächste Codeübernahme nicht `KeyValuePair` oder `NumberSequence` enthält. Der nächste sichere Code-Slice ist:

```text
000042_springmaster_core_domain_entity_service_support
```


## Umsetzung seit 000042

Der risikoarme Service-Support aus `core-entity-service-and-sequence` wurde mit `000042_springmaster_core_domain_entity_service_support` in Springmaster umgesetzt.

Umgesetzt sind:

```text
src/main/java/de/cocondo/system/entity/service/DomainEntityService.java
src/main/java/de/cocondo/system/entity/service/TagService.java
```

Nicht umgesetzt sind weiterhin die persistenznahen Metadata- und Sequence-Bausteine. Für diese bleibt eine separate Entscheidung erforderlich, bevor Java-Code übernommen wird.

Nächster empfohlener Schritt:

```text
000043_springmaster_core_metadata_persistence_model_decision
```

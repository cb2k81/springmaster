# CHANGELOG 000015 - springmaster core persistence basic types

## Added

- Added `Auditable` as audit contract for persistent core entities.
- Added `AuditingEntityListener` with deterministic SYSTEM defaults.
- Added `DomainEntity` as abstract mapped superclass with ID, persistence version, tags and audit fields.
- Added `DomainEntityListener` as PrePersist ID safety net.
- Added `Range` as embeddable validity window.
- Added unit tests for mapping annotations, listener behavior, identifier safety and range accessors.
- Added documentation for persistence basic types.

## Changed

- Updated Core documentation.
- Updated Springmaster version policy with the `000015` Core version state.
- Increased `PLATFORM_VERSION` to `0.3.0-foundation`.
- Increased `PLATFORM_CORE_VERSION` to `0.2.0`.
- Updated `PLATFORM_STATE_PATCH` to `000015_springmaster_core_persistence_basic_types`.

## Not included

- No Spring Data JPA runtime activation.
- No repository layer.
- No DataSource configuration.
- No Liquibase changesets.
- No metadata Key-Value relation.
- No demo domain.

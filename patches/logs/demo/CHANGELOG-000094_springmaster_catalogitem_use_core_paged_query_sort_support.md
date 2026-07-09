# 000094 springmaster catalogitem use core paged query sort support

## Scope

Demo slice adoption of Core `PagedQuerySupport.stableComparator(...)`.

## Changes

- `CatalogItemService` now delegates sort allow-list validation, default-sort resolution, sort-direction parsing and stable tie-breaker composition to Core.
- Removed demo-local `resolveSortBy` and comparator switch helpers.
- Added service-level regression evidence for default sort behavior and descending `/all` query sorting.
- Updated CatalogItem candidate evidence documents and JSON metadata.

## Verification

- `git diff --check`
- `mvn -B -ntp test -Dtest=CatalogItemServiceTest,CatalogItemControllerTest`
- `mvn -B -ntp test`
- `./bin/export.sh full --zip`

# 000093_springmaster_paged_query_support_sort_allowlist_tiebreaker

## Scope

Core code patch for `de.cocondo.system.list.PagedQuerySupport`.

## Changes

- Extended `PagedQuerySupport` with public sort-field allow-list validation.
- Added default-sort resolution for canonical list/query endpoints.
- Added stable Spring Data `Sort` construction with optional ascending tie-breaker.
- Added stable in-memory `Comparator` construction for candidate/reference slices and generated service slices.
- Added targeted unit tests for sort-field validation, direction trimming, stable sort generation and comparator tie-breaker behavior.
- Updated Core documentation and platform version metadata.

## Verification

Required on target host:

```text
mvn -B -ntp test -Dtest=PagedQuerySupportTest
mvn -B -ntp test
./bin/export.sh full --zip
```

## Notes

Core remains fachfrei. Fachmodule and generated service slices pass their own public sort fields, comparator definitions and tie-breakers.

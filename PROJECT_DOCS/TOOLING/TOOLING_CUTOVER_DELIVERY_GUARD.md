# Tooling Cutover Delivery Guard

## Status

Patch `000130_springmaster_tooling_cutover_delivery_guard` closes the remaining
fail-closed prerequisites before the first ZBM Tooling Cutover.

The implementation is generic. ZBM is the first registered qualification target,
but no ZBM domain logic is embedded in Springmaster and this Springmaster patch
does not modify the live ZBM repository.

## Problems closed

### Explicit Tooling validation

The target patch system's implicit `auto` profile does not require a full Maven
regression for a Tooling-only path set. `platform-update target-apply` therefore
now derives an explicit acceptance contract from `manifest.requires.profile`.

| Generated profile | Target accept profile | Full test |
|---|---|---:|
| `tooling`, `tooling-cutover` | `tooling` | required |
| `core`, `core-runtime`, `core-tests` | `code` | required |
| `defaults`, `platform-update` | `tooling` | required |
| `core-docs`, `platform-update-doc` | `docs` | not required |

Unknown profiles stop before target mutation.

### Atomic bootstrap configuration

A legacy target cannot produce an integer Full-v2 closure export by receiving
shared Tooling files alone. Its existing `export.config.json` may still include
mutable validation logs.

The dedicated profile `tooling-cutover` therefore contains:

```text
shared dependency-complete Tooling payload
+ target-safe synthesized export.config.json
```

The synthesis starts from the target configuration, preserves its project key,
profiles and local settings, and only adds the mandatory exclusion:

```text
patches/logs/validation/**
```

Springmaster defaults are never copied wholesale into the target. The profile
uses target scope `tooling`, because the target patch contract explicitly owns
`bin/**`, `PROJECT_DOCS/TOOLING/**`, `.env.example` and `export.config.json`.

The target descriptor must authorize `tooling-cutover` explicitly. A plain
`tooling` delivery remains blocked for the initial ZBM bootstrap.

### Exactly one closure export

The target acceptance command is now explicit:

```text
./bin/patch.sh accept <patch.zip> \
  --profile tooling \
  --full-test \
  --no-export
```

The accept process applies and validates the patch but does not own the final
export. After a successful acceptance, `target-apply`:

1. validates `STATUS`, `PROFILE`, `FULL_TEST`, `EXPORT=False` and
   `LATEST_EXPORT=-` from the target summary;
2. writes canonical target-apply source evidence;
3. invokes the newly delivered target exporter exactly once with `--evidence`;
4. requires exactly one new Full-ZIP;
5. checks it with the newly delivered `export-integrity-check.py` against the
   real target bytes and with `--require-evidence`.

This ordering is bootstrap-safe: the old target patch process performs the
application, while the newly installed exporter and integrity checker perform
the final closure.

### Target environment isolation

The Springmaster process must not leak its own `APP_EXPORT_PROJECT_KEY` or
`APP_NAME` into the target export. `target-apply` binds those values explicitly
to the loaded target descriptor before invoking target commands. The ZBM closure
export must therefore be named `zbm_export_full_...zip` and report
`projectKey=zbm`.

### Evidence path integrity

Closure evidence is no longer accepted merely because its canonical digest is
valid. The integrity checker additionally requires:

- unique, safe repository-relative `changedPaths`;
- every non-deleted changed path exists in the final file manifest;
- `deletedPaths` is unique and a subset of `changedPaths`;
- misspelled, duplicated or unclassified paths fail closed.

## Qualification contract

`platform/update/tests/platform-update-delivery-contract-it.sh` performs the
full generic flow against an isolated clone of the registered target:

1. target-bound `tooling-cutover` generation;
2. producer Artifact Preflight;
3. target dry-run;
4. baseline-mutation and disallowed-profile negative tests;
5. isolated target acceptance with explicit Tooling/full-test policy;
6. proof that the full-test command was invoked;
7. proof that accept did not export;
8. one target-apply-owned Full-v2 closure export;
9. raw-byte and Closure-Evidence integrity check;
10. proof that the registered source target was not mutated.

The integration fixture records the full-test invocation without depending on
the target application's current Maven maturity. The real ZBM cutover runner
must separately execute the actual ZBM full Maven command in its isolated clone
before any live apply is authorized.

## Scope boundary

This patch does not:

- generate or apply the live ZBM Tooling patch;
- update the ZBM System Kernel;
- alter ZBM platform-version metadata;
- define ZBM local domain scopes;
- repair ZBM Maven, Persistence, Validation or Security maturity;
- select a pilot aggregate.

After this patch is committed, the next step is generation and host-side sandbox
qualification of target patch
`000013_springmaster_platform_update_tooling-cutover_for_zbm`.

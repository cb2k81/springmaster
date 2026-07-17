# ZBM Core Delivery Clone-State Repair

## Status

Qualified repair for the isolated ZBM Core delivery contract introduced with
`000131_springmaster_zbm_core_0_3_6_delivery_enablement`.

## Forensic finding

The delivery integration test derives the expected target patch number from the
live ZBM patch registry, then creates a Git clone and hydrates the ignored patch
runtime directories. The previous directory copy used:

```bash
cp -a "${SOURCE_TARGET_PATH}/patches/archives" "${TARGET_COPY}/patches/archives"
```

When the destination directory already exists in the clone, `cp` places the
source directory below it. The effective registry then becomes
`patches/archives/archives/...`. The cloned patch system cannot resolve the
latest patch, so Platform Update generates `000001_...` although the source
registry reports `000014_...`.

## Repair contract

The runtime directory contents are copied with `source/.` into an explicitly
created destination directory. Before generation, the test now requires the
source and clone to report the same latest patch. The generated patch ID is
read from the manifest and compared with an explicit diagnostic that includes
expected ID, actual ID, source latest patch and clone latest patch.

The live ZBM repository remains read-only. Delivery and Maven execution occur
only in the isolated clone. A failed contract run preserves its temporary work
root and reports the path so generated manifests, preflight reports and Maven
logs remain available for forensic diagnosis.

## Required closure

- source latest patch: `000014_zbm_tooling_cutover_version_truth_closure`;
- clone latest patch before generation: identical to source;
- generated patch: `000015_springmaster_platform_update_core_for_zbm`;
- Core delivery contract with real Maven: pass;
- source ZBM HEAD, working tree, latest patch and tracked fingerprint: unchanged.

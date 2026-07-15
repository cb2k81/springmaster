# Platform-Update Delivery Contract Closure

## Status

Patch `000129_springmaster_platform_update_delivery_contract_closure` closes the generic producer-side delivery contract required before the first ZBM Tooling Cutover in Sprint 1.

The change remains project-neutral. It does not contain ZBM fachlogik, ZBM configuration defaults or a generated ZBM live-apply decision.

## Closed gaps

The prior `platform-update generate` implementation produced timestamp-based patch identities and omitted the complete target baseline expected by the current patch artifact preflight. Its `tooling` payload was also not dependency-complete for the current selfcheck and export-integrity contracts.

The closed contract is now:

```text
clean registered target Git baseline
        ↓
allowed target/profile validation
        ↓
six-digit target-local patch identity
        ↓
dependency-complete profile payload
        ↓
remove byte- and mode-identical operations
        ↓
complete target raw-byte expectedBeforeSha256 map
        ↓
producer artifact preflight in isolated target worktree
        ↓
reviewed target-apply
        ↓
exactly one target accept/export execution
```

## Target-bound identity

Generated patches use the next six-digit patch number of the target repository:

```text
000013_springmaster_platform_update_tooling_for_zbm
```

The following values are identical:

```text
archive basename
manifest.id
manifest.patchId
<number>_<manifest.name>
```

Generation fails if the target is not a Git worktree, its working tree is dirty, the descriptor disables updates or the selected profile is not listed in `TARGET_ALLOWED_PROFILES`.

## Complete baseline contract

`platform/update/tools/finalize-target-patch.py` binds every effective operation to the clean target baseline.

For every target path it writes:

```json
{
  "baseline": {
    "expectedBeforeSha256": {
      "existing/file": "<raw-byte-sha256>",
      "new/file": null
    }
  }
}
```

Payload files whose bytes and executable mode already equal the target are removed before ZIP creation. This prevents unchanged operations from being presented as target changes.

## Dependency-complete tooling profile

The `tooling` profile includes the patch, export, database and integrity dependencies required by the delivered selfcheck:

```text
bin/patch.py
bin/patch.sh
bin/export.sh
bin/init.env.sh
bin/tooling-selfcheck.sh
bin/dbtool.sh
bin/patch-artifact-preflight.py
bin/patch-artifact-preflight-it.sh
bin/export-integrity-check.py
bin/export-integrity-it.sh
bin/lib/**
PROJECT_DOCS/TOOLING/**
```

Target-local defaults such as `.env.example` and `export.config.json` remain excluded from `tooling`. They require a separate reviewed target-local configuration patch.

## Bootstrap preflight

A target may still use an older patch engine that does not provide the current `live-baseline` command. The producer therefore runs the current Springmaster patch engine against the target root without copying or applying it to the target.

The generic Artifact Preflight supports:

```text
--engine <patch.py>
```

The supplied engine is used for live baseline validation, dry-run and isolated worktree apply. The target repository remains unchanged.

This is a producer qualification mechanism, not an implicit Tooling apply.

## Single target export

`platform-update target-apply` no longer invokes a second `export.sh full --zip` after `patch.sh accept`.

It assigns a deterministic target acceptance log directory, executes target `accept` once and reads `LATEST_EXPORT` from its `SUMMARY.txt`. Missing acceptance evidence or a missing export path fails the command without a reapply attempt.

## Integration qualification

`platform/update/tests/platform-update-delivery-contract-it.sh` creates a temporary Git clone of the registered target and proves:

- target-local six-digit patch identity;
- allowed-profile enforcement;
- clean-target enforcement;
- dependency-complete Tooling payload;
- complete target baseline hashes;
- elimination of unchanged operations;
- producer Artifact Preflight;
- target-local dry-run;
- fail-closed rejection after target baseline mutation.

The test accepts an optional target path for isolated qualification. Its default remains the path declared by the selected target descriptor.

## Scope boundary

This closure does not:

- apply a patch to ZBM;
- update ZBM defaults or local scopes;
- update the ZBM System Kernel;
- select a ZBM pilot aggregate;
- implement a target-bound Generated Service Slice renderer;
- introduce ZBM-specific rules into Springmaster.

Those steps remain governed by `PROJECT_DOCS/OPERATIONAL/SPRINT1_ZBM_SPRINGMASTER_CONFORMANT_IMPLEMENTATION_PLAN.md`.

## Tooling-cutover closure since 000130

Patch `000130_springmaster_tooling_cutover_delivery_guard` adds the atomic
`tooling-cutover` bootstrap profile and closes target validation, export
ownership, target-environment isolation and Closure-Evidence path integrity.

The isolated delivery integration test now requires:

```text
generated profile=tooling-cutover
producer preflight PASS
target dry-run PASS
STATUS=SUCCESS
PROFILE=tooling
FULL_TEST=True
EXPORT=False
exactly one target-apply-owned Full-v2 export
Closure-Evidence and raw-byte integrity PASS
registered source target mutation NONE
```

The generic fixture proves invocation of the full-test command. Actual ZBM Maven
success remains a mandatory host-side sandbox gate before live delivery. Details:
`PROJECT_DOCS/TOOLING/TOOLING_CUTOVER_DELIVERY_GUARD.md`.

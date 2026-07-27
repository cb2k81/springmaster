# Patch 000187 - Springmaster Operator Log History Compatibility

## Purpose

Correct the accepted patch-workflow workspace contract so canonical observer and diagnostic operations remain compatible with Springmaster's retained historical tracked validation evidence.

## Changes

- Permit historical tracked sibling evidence below the shared operator-log root.
- Enforce tracked-content and Git-ignore checks only for the exact current run directory `<operator-log-root>/<patch-id>/<run-id>/`.
- Keep current run directories fail-closed when tracked content collides with runtime evidence.
- Add integration coverage for historical tracked siblings and tracked current-run conflicts.
- Update process contracts, guidance, known-error recovery and activation evidence.
- Advance Springmaster to `0.21.1-foundation`, Tooling to `0.11.1` and state patch `000187`.

## Evidence

- Accepted baseline: `ef713cc73518da94419dfa342303df6847120420`.
- Canonical patch `000186` acceptance: `run-20260727T120640Z-800d2ab4656d`.
- All `000186` acceptance validators passed; only the post-accept observer log preparation exposed the compatibility defect.

## Boundaries

- No repeat acceptance of patch `000186`.
- No automatic push or managed-project rollout.
- No Codex execution or writable Codex promotion.
- The deferred D3 calibration patch must be rebuilt only after this correction is accepted and postqualified.

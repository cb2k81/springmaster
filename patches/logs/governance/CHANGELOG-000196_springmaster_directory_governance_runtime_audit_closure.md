# 000196 – Directory governance runtime audit closure

## Purpose

Close the validator inconsistency discovered by the failed `000195` dry-run while preserving the exact 995-path directory-governance cleanup.

## Changes

- remove the digest-bound historical runtime and validation inventory from Git;
- retain the strengthened project-directory contract and fixtures;
- make `patch-state-audit` ignore only empty archive directory skeletons left after exact file deletion;
- continue to reject every non-empty archive directory without a readable `patch-log.json`;
- add positive and negative regression fixtures for both states;
- advance the platform tooling patch version to `0.11.3` and update the canonical Activation Contract in the same candidate;
- close the completed Toolkit `1.1.2` post-accept export evidence and add an explicit activation-closure pre-profile check.

## Incident provenance

- enabling toolkit patch: `000194_springmaster_patch_toolkit_staging_version_closure`;
- failed cleanup dry-run: `000195_springmaster_directory_governance_live_adoption_cleanup`;
- failure class: the targeted profile audited empty archive directory skeletons as malformed runtime archives.

## Failed preparation correction

Delivery revision `g5w8n5` correctly failed before artifact creation because `platform.env` and the Activation Contract described different current tooling states. Revision `g5w8n5` keeps patch identity `000196`, closes the version contract, and makes that closure a dedicated preparation step before `targeted`, `full`, and `release`.

# CHANGELOG 000209 — Patch Toolkit accept qualification compatibility hotfix

## Anlass

The `000208` canonical accept run `run-20260808T185737Z-d6cd351a7ae9` passed all configured validators and failed only because Toolkit `1.1.2` combined `git show --check` with `--no-patch` during qualification-commit verification.

## Änderungen

- advance Cocondo Patch Toolkit `1.1.2` to `1.1.3` as a compatible patch correction;
- keep `git show --check --oneline <commit>` and remove only `--no-patch`;
- add regression coverage for the qualification-commit check;
- synchronize project env, lock, sidecar, activation contract and activation evidence;
- advance `PLATFORM_TOOLING_VERSION` from `0.13.0` to `0.13.1` and `PLATFORM_STATE_PATCH` to `000209_springmaster_patch_toolkit_accept_qualification_compatibility_hotfix`;
- keep aggregate Platform `0.23.0-foundation` and Maven `0.23.0-foundation-SNAPSHOT` unchanged;
- remove duplicated current Toolkit version constants from normative AGENTS/ADR wording.

## Qualification

`STEP_05V3` qualified the exact command correction against the installed Toolkit `1.1.2` runtime and the actual DEV-host Git without repository mutation. Canonical patch dry-run and separate self-update accept remain required; this changelog does not claim acceptance.

## Activation evidence isolation

Candidate qualification exposed a pre-existing validator coupling: `codexCutoverFoundationCandidate` was compared to the mutable current `versionClosure`, causing accepted 000203 evidence to be treated as if it must adopt 000209 patch identity and the new current Tooling version. The hotfix therefore adds `codexCutoverFoundationAcceptance` to the Activation Contract and validates immutable 000203 identity against that dedicated contract. Current `versionClosure` remains the source for the current Tooling state. The Toolkit runtime correction is patch-level (`1.1.3`), but the new `codexCutoverFoundationAcceptance` contract surface is a compatible contract extension and therefore a Springmaster Tooling/Platform `minor` impact. Version Closure is Platform `0.24.0-foundation`, Tooling `0.14.0`, Maven `0.24.0-foundation-SNAPSHOT`, State Patch `000209`.

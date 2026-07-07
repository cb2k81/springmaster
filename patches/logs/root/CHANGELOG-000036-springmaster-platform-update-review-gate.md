# 000036_springmaster_platform_update_review_gate

## Scope

Springmaster-only Platform-Update process hardening.

## Changes

* Makes `apply-plan` a strict review gate.
* Stops generating target-mutating `*_apply_plan.sh` scripts.
* Changes `compatibility-plan` to generate review artifacts instead of executable target-apply scripts.
* Adds explicit `platform-update target-apply` as the only Platform-Update command that may modify a target project.
* Adds compact, log-based target apply output under `build/platform-update/logs/**`.
* Updates Platform-Update documentation and version state.

## Safety

No target project is modified by this patch. IDM and all other target projects remain untouched.

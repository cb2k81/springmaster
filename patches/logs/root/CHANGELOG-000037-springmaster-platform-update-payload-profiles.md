# 000037_springmaster_platform_update_payload_profiles

Springmaster-only Platform-Update hardening.

## Changes

* Split generated Platform-Update payload profiles.
* Redefined `core` as runtime + tests without `PROJECT_DOCS/CORE/**`.
* Added explicit `core-runtime`, `core-tests`, `core-docs`, `platform-update-doc` and `tooling` profiles.
* Kept Review-Gate/Target-Apply safety model unchanged.
* Documented IDM standard payload: technical Core runtime + tests plus generated update documentation, not Master-Core documentation.

## Safety

No target project is changed by this patch.

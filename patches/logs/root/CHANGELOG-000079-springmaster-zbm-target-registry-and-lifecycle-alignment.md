# 000079_springmaster_zbm_target_registry_and_lifecycle_alignment

## Summary

Aligns Springmaster target-project delivery configuration with the first planned target `zbm` before generated service-slice work continues.

## Changes

* Adds `platform/update/targets/zbm.env` as the first planned Springmaster-delivered target.
* Reclassifies `idm` and `personnel` as deferred non-delivery targets to avoid risk in running projects.
* Keeps `contacts` and `orders` as non-delivery references until explicitly verified and reclassified.
* Documents and configures the distinction between initialization and update lifecycles.
* Adds `TARGET_DELIVERY_ENABLED` as a hard guard for real `platform-update target-apply`.
* Adds the `defaults` Platform-Update payload profile for baseline configuration defaults.
* Moves the generated-service-slice blueprint follow-up to `000080_springmaster_generated_service_slice_blueprint_spec`.

## Validation

* Shell syntax validation for `bin/platform-update.sh` is required.
* Maven test is not required because no Java code, Java tests, Maven configuration, Core, Demo or Template code is changed.
* Full-ZIP export remains required after application.

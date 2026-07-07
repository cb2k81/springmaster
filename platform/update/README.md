# Platform Update

This directory contains the persistent source configuration for Springmaster target-project planning.

Current foundation scope after `000079_springmaster_zbm_target_registry_and_lifecycle_alignment`:

* `targets/*.env` describes configured target projects.
* `zbm` is the first planned Springmaster-delivered Java backend target.
* Existing/running projects (`idm`, `personnel`) are intentionally deferred and are not delivery targets.
* `contacts` and `orders` remain non-delivery references until explicitly verified and reclassified.
* `rules/` and `templates/` remain reserved for later target patch generation rules.
* Generated target-local patch ZIPs, plans and logs are written to `build/platform-update/**`, not to this directory.

## Target lifecycle

Springmaster distinguishes initialization from update.

### Initialization

Initialization creates a new project from the master skeleton. For the first real target, this means:

```text
zbm -> project-new -> technical Backend-Skeleton -> generated-project acceptance -> export baseline
```

Initialization is not a Platform-Update `target-apply`. It is a controlled project creation workflow. Until that workflow is completed, the `zbm` descriptor keeps `TARGET_DELIVERY_ENABLED=false` and `TARGET_UPDATE_ALLOWED=false`.

### Update

Updates apply later master payloads to an already initialized target project. Payload profiles include:

```text
core-runtime
core-tests
core-docs
tooling
defaults
platform-update-doc
```

The compatibility profile `core` combines runtime and tests. It intentionally excludes `PROJECT_DOCS/CORE/**` so target projects do not receive a full copy of Springmaster master documentation unless `core-docs` is selected explicitly.

The `defaults` profile is reserved for baseline configuration defaults such as `.env.example`, `export.config.json` and the environment template documentation.

## Delivery guard

Real target mutation requires both:

1. the explicit command `platform-update target-apply`, and
2. `TARGET_DELIVERY_ENABLED=true` in the target descriptor.

This guard keeps active projects such as IDM and Personnel safe while Springmaster proves generation and delivery through the new `zbm` target.

## Apply-Plan

Since `000031_springmaster_platform_update_target_patch_apply_plan`, a generated target patch ZIP can be wrapped in an apply plan:

```bash
./bin/platform-update.sh apply-plan zbm --zip <generated-patch.zip>
```

The generated artefacts live under `build/platform-update/manifests/**`. Since `000036`, these are pure review artefacts (`*.md`, `*.env`) and no executable target-mutating scripts.

Since `000032_springmaster_platform_update_target_scope_preflight`, generated patches can be checked against the target-local patch system via `platform-update preflight`. `apply-plan` runs this preflight automatically before writing apply instructions.

## Compatibility-Plan

If a target preflight fails because the target patchsystem does not yet understand a generated scope, Springmaster can create a compatibility plan:

```bash
./bin/platform-update.sh compatibility-plan zbm --zip <generated-patch.zip>
```

The command writes only to `build/platform-update/generated/**` and `build/platform-update/manifests/**`. Target projects are not automatically changed.

## Export boundary

Generated transfer artefacts are operational review artefacts and live under `build/platform-update/**`. This workspace is excluded from regular Full-ZIP baselines.

Springmaster source configuration remains under `platform/update/**`; operational generation output does not become part of the canonical source baseline.

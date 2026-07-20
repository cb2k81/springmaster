# Target Registry

Target descriptors live under:

```text
platform/update/targets/*.env
```

## Current delivery decision

Springmaster uses an explicit target lifecycle and profile allow-list:

* `zbm` is the first established Springmaster-delivered Java backend target.
* Existing/running projects such as `idm` and `personnel` remain deferred and
  must not be updated until explicitly reclassified.
* `contacts` and `orders` remain non-delivery references until their project
  state and local patch systems are verified again.
* Real target mutation is blocked unless delivery, update lifecycle and the
  requested payload profile are all explicitly enabled.

## Current configured descriptors

| Target | Status | Lifecycle | Delivery | Allowed profiles | Path |
|---|---|---|---:|---|---|
| `zbm` | `DELIVERY_ENABLED` | `update-enabled` | `true` | `tooling-cutover,core` | `/opt/cocondo/zbm` |
| `contacts` | `TO_VERIFY_NO_DELIVERY` | `existing-deferred` | `false` | descriptor-specific | `/opt/cocondo/contacts` |
| `idm` | `DEFERRED_EXISTING_PROJECT_NO_DELIVERY` | `existing-deferred` | `false` | descriptor-specific | `/opt/cocondo/idm` |
| `orders` | `TO_VERIFY_NO_DELIVERY` | `existing-deferred` | `false` | descriptor-specific | `/opt/cocondo/orders` |
| `personnel` | `DEFERRED_EXISTING_PROJECT_NO_DELIVERY` | `existing-deferred` | `false` | descriptor-specific | `/opt/cocondo/personnel` |

The authoritative values are the descriptor files themselves. This document
must not be used to override a descriptor or a target-local baseline.

## Current ZBM descriptor

The Springmaster baseline after `000131` contains:

```env
TARGET_NAME=zbm
TARGET_STATUS=DELIVERY_ENABLED
TARGET_PATH=/opt/cocondo/zbm
TARGET_APP_NAME=zbm
TARGET_BASE_PACKAGE=de.cocondo.zbm
TARGET_LIFECYCLE=update-enabled
TARGET_INITIALIZATION_ALLOWED=false
TARGET_UPDATE_ALLOWED=true
TARGET_DELIVERY_ENABLED=true
TARGET_ALLOWED_PROFILES=tooling-cutover,core
```

This records that ZBM initialization, tooling cutover and the Core `0.3.6`
compatibility review have completed. It authorizes only the atomic tooling
cutover profile and the reviewed Core source-copy profile. It does **not**
authorize Generated-Slice delivery:
`generated-slice`, `domain` or an equivalent fachlicher profile is not present
in `TARGET_ALLOWED_PROFILES`.

Patch `000131_springmaster_zbm_core_0_3_6_delivery_enablement` adds only the
`core` profile after the committed ZBM `000014` baseline was checked for source,
dependency and runtime compatibility. The governing evidence is
`ZBM_CORE_0_3_6_COMPATIBILITY_REVIEW.md`. Generated-Slice and fachliche profiles
remain disabled and require their own later decision.

## Descriptor fields

Stable identity fields:

```env
TARGET_NAME=zbm
TARGET_PATH=/opt/cocondo/zbm
TARGET_APP_NAME=zbm
TARGET_BASE_PACKAGE=de.cocondo.zbm
```

Lifecycle and safety fields:

```env
TARGET_STATUS=DELIVERY_ENABLED
TARGET_LIFECYCLE=update-enabled
TARGET_INITIALIZATION_ALLOWED=false
TARGET_UPDATE_ALLOWED=true
TARGET_DELIVERY_ENABLED=true
TARGET_ALLOWED_PROFILES=tooling-cutover,core
```

| Field | Meaning |
|---|---|
| `TARGET_LIFECYCLE` | Distinguishes initialization, accepted update lifecycle and deferred existing projects. |
| `TARGET_INITIALIZATION_ALLOWED` | Permits project creation only when explicitly true. |
| `TARGET_UPDATE_ALLOWED` | Permits update planning only when explicitly true. |
| `TARGET_DELIVERY_ENABLED` | Enables delivery only together with an allowed profile and all further gates. |
| `TARGET_ALLOWED_PROFILES` | Exact allow-list for Platform-Update payload categories. |

`TARGET_DELIVERY_ENABLED=true` never bypasses the profile allow-list, target
compatibility, local patch preflight or explicit user authorization.

## Initialization vs. update

### Initialization

Initialization creates a new Java backend project from the master:

```text
project-new -> generated technical Backend-Skeleton -> acceptance -> export baseline
```

For ZBM this is historical, verified evidence documented in
`ZBM_INITIALIZATION_CONCEPT_TEST.md`. The current descriptor no longer permits
initialization.

### Update

Updates apply reviewed master changes to an accepted target project:

```text
payload plan -> generated target patch -> preflight -> target-local review/apply
```

Platform-Update commands may be used only for a profile present in the target
allow-list:

```bash
./bin/platform-update.sh show zbm
./bin/platform-update.sh validate zbm
./bin/platform-update.sh plan zbm --profile core
```

The current descriptor does not permit a generated fachlicher service-slice
profile.

## Generated-Slice pilot boundary

The first ZBM Generated-Slice pilot follows:

```text
current ZBM full baseline
-> forensic target qualification
-> resolved target bindings
-> generic renderer and patch assembler qualification
-> target-local artifact preflight and dry-run
-> isolated target tests
-> explicit user approval
-> optional live apply
```

The governing plan is:

```text
PROJECT_DOCS/TARGET_UPDATES/ZBM_GENERATED_SLICE_PILOT_PLAN.md
```

No ZBM patch generation or apply is authorized by planning documentation alone.

## Usage

The registry is read by `bin/platform-update.sh`:

```bash
./bin/platform-update.sh list
./bin/platform-update.sh show zbm
./bin/platform-update.sh validate all
./bin/platform-update.sh plan zbm --profile core
```

## Verification rule

Before any real target delivery:

1. the current target descriptor is reviewed;
2. target lifecycle and requested profile are compatible;
3. the target baseline is current, clean and integritätsgeprüft;
4. the local target patch system passes preflight;
5. exact target hashes and scope are verified;
6. tests and export duties are defined;
7. the user explicitly authorizes the concrete apply.

Generated plan patches and review artifacts do not themselves grant mutation
permission.

## Isolated second managed-target pilot

Patch `000149_springmaster_managed_project_lifecycle_pilot` adds a self-contained integration pilot. It creates a fresh target with Project-New in a disposable directory, proves N-1 tooling and Core upgrades, validates atomic version/provenance state, commits target-local patches and verifies closure exports.

The pilot is not a persistent descriptor and grants no delivery permission to a real Fachprojekt. A second real managed target requires a separate compatibility review and explicit descriptor reclassification.

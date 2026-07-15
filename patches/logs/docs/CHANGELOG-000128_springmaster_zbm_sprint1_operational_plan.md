# 000128_springmaster_zbm_sprint1_operational_plan

## Scope

`docs`

## Purpose

Persist the binding Sprint 1 implementation, quality-gate and delivery plan for the Springmaster-conformant ZBM implementation under `PROJECT_DOCS/OPERATIONAL`.

## Changes

- adds `PROJECT_DOCS/OPERATIONAL/SPRINT1_ZBM_SPRINGMASTER_CONFORMANT_IMPLEMENTATION_PLAN.md`;
- records the platform, tooling, kernel, domain, persistence, validation, security, generator and sandbox work packages;
- defines P0/P1/P2 priorities and gates G0 through G10;
- defines the patch, runner, evidence, test, commit and push contracts;
- defines the Sprint 1 Definition of Done and explicit non-goals.

## Validation class

Documentation-only:

- no Maven test;
- no build;
- artifact preflight;
- scope and payload validation;
- isolated dry-run and apply;
- changed-path and payload-byte parity;
- `git diff --check`;
- exactly one full export during host acceptance;
- export integrity with closure evidence.

## Version impact

None. This patch changes documentation only.

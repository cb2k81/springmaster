# Changelog 000126 – Generated Slice Patch Blueprint Dry-run

## Scope

`root`

## Purpose

Introduce the deterministic, non-mutating planning boundary from
`springmaster.generated-service-slice-ir.v1` to
`springmaster.generated-service-slice-patch-blueprint.v1`.

## Changes

* add IR-only patch-blueprint tooling and shell wrapper;
* add target-neutral package and path projection;
* plan root-scope archive entries and target raw-byte baseline bindings;
* list Controller, Service, Domain, DTO, Mapper, Validator, tests, evidence and
  changelog artifacts without rendering them;
* preserve all eight management API operations and all four report families;
* add explicit target delivery gates and unresolved target/persistence/security
  blockers;
* add byte-exact BusinessPartner golden blueprint;
* add Supplier neutrality and fail-closed IR contract tests;
* advance Foundation to `0.13.65-foundation` and Tooling to `0.3.25`.

## Non-goals

* no Java source rendering;
* no `manifest.json` generation;
* no patch-ZIP generation;
* no target repository inspection or mutation;
* no ZBM-specific package, persistence or security decision;
* no target patch apply.

## Verification duties

* deterministic golden blueprint comparison;
* repeated-run byte equality;
* Supplier neutrality fixture;
* unsupported schema, invalid package projection, optional report and direct
  target-apply negative cases;
* Git-status and patch-archive side-effect guards;
* targeted and full Maven tests;
* patch artifact preflight, exact scope, diff hygiene and one full export.

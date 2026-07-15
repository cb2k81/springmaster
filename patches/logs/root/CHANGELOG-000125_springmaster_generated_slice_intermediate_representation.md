# 000125 — Generated Slice Intermediate Representation

## Scope

`root`

## Purpose

Introduce the deterministic, domain-neutral generator IR between the validated
`GeneratedServiceSlice` YAML contract and the later patch-blueprint dry-run.

## Changes

* adds dependency-free `generated-slice-ir` Python/Shell tooling;
* reuses the strict YAML parser while validating contract version `1`
  generically instead of locking normalization to BusinessPartner values;
* adds canonical Query, Detail, Write, Model, Validation, Error, Reports and
  Delivery sections;
* adds byte-exact BusinessPartner golden IR and negative fail-closed tests;
* adds a synthetic Supplier projection proving domain/package neutrality;
* advances Foundation to `0.13.64-foundation` and Tooling to `0.3.24`;
* records `000126_springmaster_generated_slice_patch_blueprint_dry_run` as the
  next non-mutating generator phase.

## Non-goals

* no Java source rendering;
* no target-project file mutation;
* no generated target patch ZIP;
* no ZBM-specific package, DTO or route assumptions;
* no Core or Demo runtime modification.

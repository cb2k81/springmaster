# 000130_springmaster_tooling_cutover_delivery_guard

## Scope

`root`

## Changes

- introduces the explicitly authorized `tooling-cutover` delivery profile;
- combines dependency-complete shared Tooling with a target-safe synthesized
  `export.config.json` bootstrap update;
- requires an explicit target accept profile and full-test decision;
- runs target acceptance with `--no-export`;
- makes `target-apply` own exactly one Full-v2 closure export;
- writes target-apply Closure-Evidence and verifies the export against target
  raw bytes with `--require-evidence`;
- prevents Springmaster project-key environment leakage into target exports;
- validates Closure-Evidence changed and deleted path declarations against the
  final export manifest;
- extends isolated positive and negative target-delivery integration coverage;
- advances Springmaster Foundation, Tooling and Platform-Update versions.

## Non-goals

- no live target project is modified;
- no ZBM domain logic or Kernel payload is introduced;
- no ZBM platform-version metadata is advanced;
- no target full-Maven success is claimed by the generic fixture.

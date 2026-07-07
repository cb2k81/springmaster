# 000089 springmaster patch accept git commit opt in

## Scope

root

## Summary

This patch hardens the Patch Accept workflow by integrating Git as an explicit, validated finalization step.

## Changes

- Adds `./bin/patch.sh accept <patch.zip> --commit`.
- Adds `--push` as an explicit opt-in publication step; it implies `--commit`.
- Requires a clean Git working tree before a committing accept run.
- Keeps `git add .` forbidden and stages only patch-log candidate paths.
- Records commit status, commit hash and push status in `SUMMARY.txt`.
- Extends `bin/patch-system-it.sh` with a direct `accept --commit` fixture.
- Updates Patch Accept, Patch System and Patch Validation documentation.

## Validation

- `python3 -m py_compile bin/patch.py`
- `bash -n bin/patch-system-it.sh`
- `bash bin/patch-system-it.sh`

## Notes

Default behaviour stays unchanged: `accept` still applies and validates patches without committing unless `--commit` is explicitly set.

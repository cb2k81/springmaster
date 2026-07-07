# CHANGELOG 000069 - springmaster report-only gate regression and Maven profile

## Scope

`root`

## Type

`tooling-code`

## Summary

Hardens the first Springmaster report-only gate tooling seed with repeatable regression coverage, a stable report schema marker and a Maven profile for report-mode execution.

## Added

- `bin/springmaster-gates-regression.sh`
  - validates report file presence;
  - validates `summary.json`, `rule-sources.json`, `input-manifest.json` and `findings.jsonl`;
  - checks schema marker `springmaster.report-only-report.v1`;
  - checks duplicate run rejection without `--clean`;
  - checks target-project input rejection;
  - checks custom report output directory handling.
- `src/test/java/de/cocondo/platform/tooling/SpringmasterGatesReportProfileTest.java`
  - runs the regression script during Maven tests;
  - runs the report-only gate command when Maven profile `springmaster-gates-report` is active.
- Maven profile `springmaster-gates-report`.

## Changed

- Adds `reportSchemaVersion` to `summary.json`, `rule-sources.json` and `input-manifest.json`.
- Extends the gate selfcheck to validate report schema markers.
- Documents the regression command and Maven profile.
- Updates the platform/tooling version state.

## Safety

- Findings remain non-blocking in report-only mode.
- Tool setup/runtime errors remain blocking.
- Target-project input remains rejected.
- No target projects are scanned or modified.
- No strict gates are introduced.

## Validation expectation

- Patch ZIP integrity.
- Manifest JSON validation.
- Patch apply/accept with tooling profile.
- Shell syntax check.
- Python compilation.
- Gate selfcheck.
- Gate regression script.
- Deterministic report run through the Maven profile.
- `mvn -q test`.
- `mvn -q -Pspringmaster-gates-report test`.
- Full ZIP export and export hygiene check.

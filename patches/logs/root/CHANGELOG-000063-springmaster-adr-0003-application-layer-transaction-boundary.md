# CHANGELOG 000063 - springmaster ADR-0003 application layer transaction boundary

## Scope

Documentation-only root patch.

## Added

- `PROJECT_DOCS/ADR/ADR-0003-application-layer-and-transaction-boundary.md`
- accepted architecture decision for controller, service, use-case, repository, mapper and transaction boundaries

## Changed

- ADR index updated with accepted ADR-0003.
- ADR gap backlog marks ADR-0003 as accepted.
- ADR governance alignment records ADR-0003 gate impact.
- Controller/service/use-case/transaction standard references ADR-0003 acceptance.
- API contract gate concept marks ADR-0003 as G3 Java boundary rule source.
- Standards index, consistency review, implementation plan and version policy updated.
- `platform/versions/platform.env` updated to `0.13.24-foundation`.

## Validation

Documentation-only patch. No Maven test required.

Expected validation:

- patch ZIP SHA-256 check;
- manifest JSON check;
- `./bin/patch.sh accept <patch> --profile docs`;
- version entry checks;
- ADR marker checks;
- full ZIP export and export hygiene check.

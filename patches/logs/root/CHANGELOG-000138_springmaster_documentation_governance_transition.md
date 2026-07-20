# 000138 – Springmaster documentation governance transition

## Scope

- add a GWC-oriented documentation governance contract;
- add a complete active Markdown index;
- freeze the existing legacy inventory in a transition baseline;
- add a deterministic documentation gate and positive/negative integration fixture;
- run the gate from the tooling selfcheck;
- advance tooling and foundation state versions.

## Boundary

Legacy metadata findings remain report-only. New documents without mandatory metadata and index drift fail closed. Historical documents are not mass-rewritten by this patch.

## Validation

```bash
python3 -m py_compile bin/documentation-gate.py
bash -n bin/documentation-gate.sh bin/documentation-gate-it.sh
./bin/documentation-gate.sh --check
./bin/documentation-gate-it.sh
./bin/tooling-selfcheck.sh --no-export
```

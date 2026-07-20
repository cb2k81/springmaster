# 000136 – Springmaster AGENTS scope bootstrap

## Scope

- allow the root `AGENTS.md` path in the `root` and `docs` patch scopes;
- add an isolated integration fixture for the new path;
- include the fixture in the tooling selfcheck;
- advance the tooling and foundation state versions.

## Rationale

The existing fail-closed scope registry cannot accept a new root `AGENTS.md` in the same patch that first introduces the path. This bootstrap patch extends and verifies the scope before the repository working agreement is installed by the following patch.

## Validation

```bash
bash -n bin/patch-agents-scope-it.sh
python3 -m py_compile bin/patch.py
./bin/patch-agents-scope-it.sh
./bin/tooling-selfcheck.sh --no-export
```

# 000137 – Springmaster AGENTS and execution baseline

## Scope

- install the reviewed root `AGENTS.md` as repository-wide working agreement;
- require `/opt/cocondo/springmaster` as explicit working directory;
- require `/home/cb/Downloads` as the local handoff directory;
- keep patch, Git, export, target-update and verification boundaries in one discoverable baseline.

## Validation

```bash
cd /opt/cocondo/springmaster || exit 1
git diff --check
test -f AGENTS.md
grep -Fq '/opt/cocondo/springmaster' AGENTS.md
grep -Fq '/home/cb/Downloads' AGENTS.md
```

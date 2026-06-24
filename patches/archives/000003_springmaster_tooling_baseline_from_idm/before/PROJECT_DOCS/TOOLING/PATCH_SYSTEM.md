# Patch System Bootstrap

The bootstrap installs a manifest-based patch system:

```bash
./bin/patch.sh apply --dry-run <patch.zip>
./bin/patch.sh apply <patch.zip>
./bin/patch.sh list
./bin/patch.sh show latest
./bin/patch.sh rollback --dry-run latest
./bin/patch.sh rollback latest
```

Patch ZIPs must contain:

```text
manifest.json
files/**
logs/CHANGELOG-*.md
```

Optional deletions are represented through `delete/**`.

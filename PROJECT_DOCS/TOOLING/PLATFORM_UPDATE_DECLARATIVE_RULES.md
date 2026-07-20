---
documentType: guide
status: active
scope: platform-update
owner: springmaster-maintainers
validFrom: 2026-07-20
supersedes: none
---
# Platform Update Declarative Profile Rules

The canonical payload profile contract is `platform/update/rules/profiles.json`.

Each profile declares its scope, payload paths, payload mode, target accept profile, full-test policy, generated document family, optional Core POM synthesis, optional tooling-cutover configuration synthesis and the component versions updated in managed target state.

`platform/update/tools/profile-rules.py` validates the contract and is the only profile metadata reader used by `bin/platform-update.sh` and the managed-state synthesizer. Adding or changing a profile therefore requires a rule change and its positive and negative integration fixtures; profile semantics must not be added as an untested shell `case` branch.

Reserved profiles remain visible but carry no source payload until their own contract is accepted.

# 000134_springmaster_platform_update_core_delivery_clone_state_repair

Repairs the isolated ZBM Core delivery integration test after the fully green
Springmaster Maven closure of patches `000131`, `000132` and `000133`.

Changes:

- hydrate patch runtime directory contents without nesting an already existing
  destination directory;
- verify source and cloned target patch registries are identical before
  generation;
- derive the expected target patch number from the verified cloned registry;
- report expected and actual generated patch IDs explicitly;
- preserve failed temporary workspaces for complete forensic diagnostics;
- preserve the real-Maven, target-export and ZBM non-mutation contracts.

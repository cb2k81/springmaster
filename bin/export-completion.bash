#!/usr/bin/env bash
_springmaster_export_completion() {
  local cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "full root docs patches java resources tests db platform core demo tooling templates planning target-registry platform-update --full-parts --parts --zip --list help" -- "$cur") )
}
complete -F _springmaster_export_completion export.sh 2>/dev/null || true
